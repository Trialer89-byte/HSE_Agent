from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import openai
from datetime import datetime
import json

from app.config.settings import settings


class BaseHSEAgent(ABC):
    """
    Base class for HSE specialist agents
    """
    
    def __init__(self, user_context: Dict[str, Any]):
        self.user_context = user_context
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        
        # Agent configuration
        self.agent_name = self.__class__.__name__
        self.agent_version = "1.0"
        self.max_tokens = 4000
        self.temperature = 0.1  # Low temperature for consistent analysis
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent
        """
        pass
    
    @abstractmethod
    async def analyze(self, permit_data: Dict[str, Any], context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform analysis specific to this agent
        """
        pass
    
    async def _call_llm(
        self,
        messages: List[Dict[str, str]],
        response_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Call LLM with messages and return response
        """
        try:
            kwargs = {
                "model": self.model,
                "messages": messages,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature
            }
            
            # Add response format if specified (for structured output)
            if response_format:
                kwargs["response_format"] = response_format
            
            response = self.client.chat.completions.create(**kwargs)
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"LLM call failed in {self.agent_name}: {str(e)}")
    
    def _prepare_context_summary(self, context_documents: List[Dict[str, Any]]) -> str:
        """
        Prepare a summary of context documents for the agent
        """
        if not context_documents:
            return "Nessun documento di contesto disponibile."
        
        summary = "DOCUMENTI DI RIFERIMENTO DISPONIBILI:\n\n"
        
        for i, doc in enumerate(context_documents[:10], 1):  # Limit to top 10
            summary += f"{i}. {doc.get('title', 'Documento senza titolo')}\n"
            summary += f"   Codice: {doc.get('document_code', 'N/A')}\n"
            summary += f"   Tipo: {doc.get('document_type', 'N/A')}\n"
            summary += f"   Autorità: {doc.get('authority', 'N/A')}\n"
            summary += f"   Contenuto: {doc.get('content', '')[:200]}...\n"
            summary += f"   Score rilevanza: {doc.get('search_score', 0):.2f}\n\n"
        
        return summary
    
    def _format_permit_data(self, permit_data: Dict[str, Any]) -> str:
        """
        Format permit data for agent consumption
        """
        formatted = "DATI PERMESSO DI LAVORO:\n\n"
        formatted += f"ID: {permit_data.get('id', 'N/A')}\n"
        formatted += f"Titolo: {permit_data.get('title', 'N/A')}\n"
        formatted += f"Descrizione: {permit_data.get('description', 'N/A')}\n"
        formatted += f"Tipo di lavoro: {permit_data.get('work_type', 'N/A')}\n"
        formatted += f"Ubicazione: {permit_data.get('location', 'N/A')}\n"
        formatted += f"Durata prevista: {permit_data.get('duration_hours', 'N/A')} ore\n"
        formatted += f"Livello priorità: {permit_data.get('priority_level', 'N/A')}\n"
        
        if permit_data.get('dpi_required'):
            formatted += f"DPI richiesti: {', '.join(permit_data['dpi_required'])}\n"
        
        if permit_data.get('tags'):
            formatted += f"Tag: {', '.join(permit_data['tags'])}\n"
        
        if permit_data.get('custom_fields'):
            formatted += "\nCampi personalizzati:\n"
            for key, value in permit_data['custom_fields'].items():
                formatted += f"  {key}: {value}\n"
        
        return formatted
    
    def _get_tenant_context(self) -> str:
        """
        Get tenant-specific context information
        """
        return f"""
CONTESTO AZIENDALE:
- Tenant ID: {self.user_context.get('tenant_id', 'N/A')}
- Utente: {self.user_context.get('user_id', 'N/A')}
- Dipartimento: {self.user_context.get('department', 'N/A')}
- Timestamp analisi: {datetime.utcnow().isoformat()}
"""
    
    def _validate_output_format(self, output: Dict[str, Any]) -> bool:
        """
        Validate the output format from the agent
        """
        required_fields = ['analysis_complete', 'confidence_score', 'agent_name']
        
        for field in required_fields:
            if field not in output:
                return False
        
        # Validate confidence score
        confidence = output.get('confidence_score', 0)
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 1):
            return False
        
        return True
    
    def _create_error_response(self, error_message: str) -> Dict[str, Any]:
        """
        Create a standardized error response
        """
        return {
            "analysis_complete": False,
            "confidence_score": 0.0,
            "agent_name": self.agent_name,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime
import json

try:
    import openai
except ImportError:
    openai = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.config.settings import settings


class BaseHSEAgent(ABC):
    """
    Base class for HSE specialist agents
    """
    
    def __init__(self, user_context: Dict[str, Any], vector_service=None):
        self.user_context = user_context
        self.vector_service = vector_service  # Inject vector service for dynamic searches
        
        # Search budget control - prevent excessive token consumption
        self.max_additional_searches = 2  # Limit follow-up searches
        self.additional_searches_used = 0
        self.search_results_cache = {}  # Cache to avoid duplicate searches
        
        # Configurazione per AI provider
        self.ai_provider = getattr(settings, 'ai_provider', 'gemini').lower()
        
        if self.ai_provider == 'gemini' and genai:
            # Configura Gemini
            if settings.gemini_api_key:
                genai.configure(api_key=settings.gemini_api_key)
                self.model = genai.GenerativeModel(settings.gemini_model)
            else:
                raise ValueError("GEMINI_API_KEY is required when using Gemini provider")
        elif openai:
            # Fallback a OpenAI
            api_key = settings.openai_api_key or settings.gemini_api_key
            if not api_key:
                raise ValueError("Either OPENAI_API_KEY or GEMINI_API_KEY is required")
            self.client = openai.OpenAI(api_key=api_key)
            self.model_name = settings.openai_model
            self.ai_provider = 'openai'  # Force OpenAI if Gemini not available
        else:
            raise ValueError("Neither OpenAI nor Gemini libraries are available")
        
        # Agent configuration
        self.agent_name = self.__class__.__name__
        self.agent_version = "1.1"  # Updated for dynamic search capability
        self.max_tokens = 2048  # Reduced for faster processing
        self.temperature = 0.1  # Low temperature for consistent analysis
        self.request_timeout = 30  # 30 second timeout for Gemini requests
    
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
            if self.ai_provider == 'gemini':
                return await self._call_gemini(messages)
            else:
                return await self._call_openai(messages, response_format)
                
        except Exception as e:
            raise Exception(f"LLM call failed in {self.agent_name}: {str(e)}")
    
    async def _call_gemini(self, messages: List[Dict[str, str]]) -> str:
        """
        Call Gemini API
        """
        # Combina system prompt e user messages per Gemini
        system_prompt = ""
        user_content = ""
        
        for message in messages:
            if message["role"] == "system":
                system_prompt = message["content"]
            elif message["role"] == "user":
                user_content = message["content"]
        
        # Combina system prompt con user content
        full_prompt = f"""
{system_prompt}

ISTRUZIONI SPECIFICHE PER LA RISPOSTA:
- Rispondi SEMPRE e SOLO in formato JSON valido
- Non aggiungere testo prima o dopo il JSON
- Mantieni la struttura esatta richiesta nel prompt
- Usa terminologia tecnica HSE italiana
- Cita normative italiane quando applicabile
- Includi sempre i campi: "analysis_complete", "confidence_score", "agent_name"

RICHIESTA DA ELABORARE:
{user_content}

RICORDA: La risposta deve essere un JSON valido senza testo aggiuntivo.
"""
        
        # Genera response con Gemini con timeout
        generation_config = genai.types.GenerationConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
        )
        
        # Run in thread pool since Gemini is sync with timeout
        loop = asyncio.get_event_loop()
        try:
            response = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(full_prompt, generation_config=generation_config)
                ),
                timeout=self.request_timeout
            )
        except asyncio.TimeoutError:
            raise Exception(f"Gemini API request timed out after {self.request_timeout} seconds")
        
        # Clean the response to extract JSON
        cleaned_response = self._clean_json_response(response.text)
        return cleaned_response
    
    async def _call_openai(self, messages: List[Dict[str, str]], response_format: Optional[Dict[str, Any]] = None) -> str:
        """
        Call OpenAI API (fallback)
        """
        kwargs = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }
        
        if response_format:
            kwargs["response_format"] = response_format
        
        response = self.client.chat.completions.create(**kwargs)
        return response.choices[0].message.content
    
    def _clean_json_response(self, response_text: str) -> str:
        """
        Clean Gemini response to extract valid JSON
        """
        import re
        
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        response_text = response_text.strip()
        
        # Try to find JSON object bounds
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_text = response_text[start_idx:end_idx + 1]
            
            # Test if it's valid JSON
            try:
                import json
                json.loads(json_text)
                return json_text
            except:
                pass
        
        # If JSON extraction fails, return original
        return response_text
    
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
    
    async def request_additional_documents(
        self,
        search_terms: List[str],
        document_types: List[str] = None,
        categories: List[str] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Request additional documents based on identified knowledge gaps
        """
        if not self.vector_service:
            print(f"[{self.agent_name}] Vector service not available for additional searches")
            return []
        
        # Check if vector service client is available
        if hasattr(self.vector_service, 'client') and not self.vector_service.client:
            print(f"[{self.agent_name}] Vector service client not connected, skipping additional search")
            return []
        
        if self.additional_searches_used >= self.max_additional_searches:
            print(f"[{self.agent_name}] Search budget exhausted ({self.additional_searches_used}/{self.max_additional_searches})")
            return []
        
        # Create cache key to avoid duplicate searches
        cache_key = f"{'-'.join(search_terms)}_{'-'.join(document_types or [])}_{'-'.join(categories or [])}"
        if cache_key in self.search_results_cache:
            print(f"[{self.agent_name}] Returning cached search results")
            return self.search_results_cache[cache_key]
        
        try:
            self.additional_searches_used += 1
            print(f"[{self.agent_name}] Performing additional search {self.additional_searches_used}/{self.max_additional_searches}")
            print(f"[{self.agent_name}] Search terms: {search_terms}")
            
            # Build search query
            search_query = " ".join(search_terms)
            
            # Prepare filters
            filters = {
                "tenant_id": self.user_context.get("tenant_id")
            }
            
            if document_types:
                filters["document_type"] = document_types
            
            if categories:
                filters["category"] = categories
            
            # Perform hybrid search
            results = await self.vector_service.hybrid_search(
                query=search_query,
                filters=filters,
                limit=limit,
                threshold=0.6  # Lower threshold for follow-up searches
            )
            
            # Cache results
            self.search_results_cache[cache_key] = results
            
            print(f"[{self.agent_name}] Found {len(results)} additional documents")
            return results
            
        except Exception as e:
            print(f"[{self.agent_name}] Error in additional search: {str(e)}")
            return []
    
    async def search_specific_regulations(
        self,
        regulation_types: List[str],
        keywords: List[str],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for specific regulations or normative documents
        """
        search_terms = keywords + regulation_types
        return await self.request_additional_documents(
            search_terms=search_terms,
            document_types=["normativa"],
            limit=limit
        )
    
    async def search_operational_procedures(
        self,
        procedure_types: List[str],
        work_context: List[str],
        limit: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Search for specific operational procedures
        """
        search_terms = procedure_types + work_context
        return await self.request_additional_documents(
            search_terms=search_terms,
            document_types=["istruzione_operativa"],
            limit=limit
        )
    
    def detect_knowledge_gaps(
        self,
        permit_data: Dict[str, Any],
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """
        Detect potential knowledge gaps based on permit data and available documents
        """
        gaps = {
            "missing_regulations": [],
            "missing_procedures": [],
            "incomplete_coverage": []
        }
        
        work_type = permit_data.get("work_type", "").lower()
        description = permit_data.get("description", "").lower()
        location = permit_data.get("location", "").lower()
        
        # Check for work-type specific gaps
        work_type_mappings = {
            "chimico": ["d.lgs", "reach", "clp", "adr", "sostanze", "chimiche"],
            "scavo": ["scavi", "consolidamento", "servizi interrati", "dpr 177"],
            "elettrico": ["cei", "elettrotecnica", "impianti elettrici", "bassa tensione"],
            "meccanico": ["macchine", "attrezzature", "manutenzione", "lockout"],
            "edile": ["cantiere", "ponteggi", "dpi anticaduta", "edilizia"],
            "spazi_confinati": ["spazi confinati", "atmosfere", "gas", "ventilazione"]
        }
        
        # Look for keywords that might indicate need for specific documents
        risk_keywords = {
            "altezza": ["dpi anticaduta", "ponteggi", "lavori in quota"],
            "gas": ["rilevatori gas", "ventilazione", "atmosfere esplosive"],
            "sostanze": ["schede sicurezza", "dpi chimici", "stoccaggio"],
            "energia": ["lockout", "tagout", "isolamento energetico"],
            "macchine": ["manutenzione", "sicurezza macchine", "protezioni"]
        }
        
        # Analyze available document types
        available_doc_types = set()
        available_categories = set()
        
        for doc in context_documents:
            available_doc_types.add(doc.get("document_type", ""))
            available_categories.add(doc.get("category", ""))
        
        # Check for missing regulations based on work type
        if work_type in work_type_mappings:
            expected_keywords = work_type_mappings[work_type]
            for keyword in expected_keywords:
                if not any(keyword in doc.get("content", "").lower() for doc in context_documents):
                    gaps["missing_regulations"].append(keyword)
        
        # Check for missing procedures based on risk keywords
        for risk, procedures in risk_keywords.items():
            if risk in description or risk in location:
                for procedure in procedures:
                    if not any(procedure in doc.get("content", "").lower() for doc in context_documents):
                        gaps["missing_procedures"].append(procedure)
        
        # Check for incomplete coverage
        if "normativa" not in available_doc_types:
            gaps["incomplete_coverage"].append("normative documents")
        
        if "istruzione_operativa" not in available_doc_types:
            gaps["incomplete_coverage"].append("operational procedures")
        
        return gaps
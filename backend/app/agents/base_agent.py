"""
Base Agent Class for HSE Analysis System
"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import google.generativeai as genai
from app.config.settings import settings


class BaseHSEAgent(ABC):
    """Base class for all HSE specialist agents"""
    
    def __init__(self, name: str, specialization: str, activation_keywords: list = None):
        self.name = name
        self.specialization = specialization
        self.activation_keywords = activation_keywords or []
        self.system_message = self._get_system_message()
        self.vector_service = None  # Will be injected by orchestrator
        self.db_session = None     # Could be injected for PostgreSQL access
        
    @abstractmethod
    def _get_system_message(self) -> str:
        """Return the system message for this agent"""
        pass
    
    @abstractmethod
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform specialized analysis (now async for autonomous document search)"""
        pass
    
    def should_activate(self, risk_classification: Dict[str, Any]) -> bool:
        """Determine if this agent should be activated based on risk classification"""
        # Check if any activation keywords are present
        permit_text = str(risk_classification).lower()
        
        for keyword in self.activation_keywords:
            if keyword.lower() in permit_text:
                return True
                
        # Check specific risk domains if classified
        risk_domains = risk_classification.get("risk_domains", {})
        return self.specialization.lower() in [d.lower() for d in risk_domains.keys()]
    
    async def get_gemini_response(self, prompt: str, context_documents: list = None) -> str:
        """Get response from Gemini API with optional document context"""
        if not settings.gemini_api_key:
            return f"[{self.name}] Error: No Gemini API key configured"
            
        try:
            genai.configure(api_key=settings.gemini_api_key)
            model = genai.GenerativeModel(settings.gemini_model)
            
            # Add document context if available
            docs_context = ""
            if context_documents:
                docs_context = "\n\nDOCUMENTI AZIENDALI RILEVANTI:\n"
                for i, doc in enumerate(context_documents[:3], 1):  # Top 3 docs
                    docs_context += f"\n[DOCUMENTO {i}] {doc.get('title', 'N/A')}\n"
                    docs_context += f"Tipo: {doc.get('document_type', 'N/A')}\n"
                    content = doc.get('content', '')[:800]  # First 800 chars for specialists
                    docs_context += f"Contenuto rilevante:\n{content}...\n"
                    docs_context += "-" * 50 + "\n"
                
                docs_context += "\nIMPORTANTE: Quando citi informazioni dai documenti, usa '[FONTE: Documento Aziendale]' seguito dal titolo del documento.\n"
            
            full_prompt = f"""
Tu sei {self.name}, specialista in {self.specialization}.

{self.system_message}

{docs_context}

RICHIESTA SPECIFICA:
{prompt}

Rispondi utilizzando la tua expertise specifica in {self.specialization}.
Se utilizzi informazioni dai documenti aziendali, CITALE SEMPRE come '[FONTE: Documento Aziendale] Nome Documento'.
"""
            
            response = model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            return f"[{self.name}] Error generating response: {str(e)}"
    
    async def search_specialized_documents(self, query: str, tenant_id: int, limit: int = 5) -> list:
        """Search for documents specific to this specialist's domain"""
        if not self.vector_service:
            print(f"[{self.name}] No vector service available for autonomous search")
            return []
        
        try:
            # Create specialized query combining domain keywords with permit query
            specialized_query = f"{self.specialization} {' '.join(self.activation_keywords[:5])} {query}"
            
            # Search with filters relevant to this specialist
            specialized_docs = await self.vector_service.hybrid_search(
                query=specialized_query,
                filters={
                    "tenant_id": tenant_id,
                    "document_type": ["procedura_sicurezza", "istruzione_operativa", "manuale", "procedura"]
                },
                limit=limit,
                threshold=0.6  # Higher threshold for more relevant results
            )
            
            print(f"[{self.name}] Autonomous search found {len(specialized_docs)} specialized documents")
            return specialized_docs
            
        except Exception as e:
            print(f"[{self.name}] Error in autonomous document search: {e}")
            return []
    
    async def search_metadata_documents(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Search document metadata in PostgreSQL"""
        if not self.db_session:
            print(f"[{self.name}] No database session available for metadata search")
            return []
        
        try:
            from app.models.document import Document
            from sqlalchemy import and_, or_
            
            # Build query based on filters
            query = self.db_session.query(Document)
            
            conditions = []
            if filters.get("tenant_id"):
                conditions.append(Document.tenant_id == filters["tenant_id"])
            if filters.get("document_type"):
                conditions.append(Document.document_type.in_(filters["document_type"]))
            if filters.get("category"):
                conditions.append(Document.category == filters["category"])
            if filters.get("is_active", True):
                conditions.append(Document.is_active == True)
            
            if conditions:
                query = query.filter(and_(*conditions))
            
            # Execute query
            documents = query.limit(10).all()
            
            # Convert to dict format
            result = []
            for doc in documents:
                result.append({
                    "id": doc.id,
                    "document_code": doc.document_code,
                    "title": doc.title,
                    "document_type": doc.document_type,
                    "category": doc.category,
                    "file_path": doc.file_path,
                    "content_summary": doc.content_summary,
                    "industry_sectors": doc.industry_sectors,
                    "authority": doc.authority
                })
            
            print(f"[{self.name}] PostgreSQL search found {len(result)} metadata records")
            return result
            
        except Exception as e:
            print(f"[{self.name}] Error in PostgreSQL metadata search: {e}")
            return []
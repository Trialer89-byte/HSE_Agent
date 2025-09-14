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
        
        # Add limit instruction to the prompt for specialists and agents
        if "Specialist" in self.name or "Agent" in self.name:
            prompt += f"\n\nIMPORTANTE: Limita ogni categoria di raccomandazioni a MASSIMO 10 elementi. Sii conciso e prioritizza le azioni più critiche."
            
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
    
    def create_error_response(self, exception: Exception) -> Dict[str, Any]:
        """Create standardized error response for failed analysis"""
        error_type = type(exception).__name__
        error_msg = str(exception)
        
        # Categorize error for better user understanding
        if "weaviate" in error_msg.lower():
            error_category = "CONNESSIONE_DOCUMENTI"
            user_message = "Servizio documenti non disponibile - analisi limitata"
        elif "gemini" in error_msg.lower() or "api" in error_msg.lower():
            error_category = "SERVIZIO_AI" 
            user_message = "Servizio AI non disponibile - analisi non possibile"
        elif "timeout" in error_msg.lower():
            error_category = "TIMEOUT"
            user_message = "Analisi interrotta per timeout - riprovare"
        elif "connection" in error_msg.lower() or "network" in error_msg.lower():
            error_category = "CONNESSIONE_RETE"
            user_message = "Problemi di connessione - riprovare"
        else:
            error_category = "ERRORE_GENERALE"
            user_message = "Errore durante analisi"
        
        return {
            "specialist": self.name,
            "classification": f"ERRORE ANALISI - {error_category}",
            "ai_analysis_used": False,
            "error": f"{user_message}: {error_msg}",
            "error_type": error_type,
            "error_category": error_category,
            "risks_identified": [],
            "recommended_actions": [],
            "dpi_requirements": [],
            "existing_measures_evaluation": {
                "error": f"Analisi fallita: {error_category}"
            },
            "permits_required": [],
            "raw_ai_response": f"ERROR: {error_type}"
        }
    
    async def search_specialized_documents(self, query: str, tenant_id: int, limit: int = 5) -> list:
        """Search for documents specific to this specialist's domain"""
        if not self.vector_service:
            print(f"[{self.name}] WARNING: Weaviate vector service unavailable - proceeding without document context")
            return []  # Return empty list instead of crashing
        
        try:
            # Create specialized query combining domain keywords with permit query
            specialized_query = f"{self.specialization} {' '.join(self.activation_keywords[:5])} {query}"
            
            # Use semantic search for better relevance on technical HSE documents
            specialized_docs = await self.vector_service.semantic_search(
                query=specialized_query,
                tenant_id=tenant_id,
                document_types=["procedura_sicurezza", "istruzione_operativa", "manuale", "procedura"],
                limit=limit
            )
            
            print(f"[{self.name}] Autonomous search found {len(specialized_docs)} specialized documents")
            return specialized_docs
            
        except Exception as e:
            print(f"[{self.name}] WARNING: Weaviate search failed - {str(e)} - proceeding without documents")
            return []  # Return empty list instead of crashing
    
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

    def extract_citations_from_response(self, ai_response: str, context_documents: list = None) -> list:
        """Extract citations from AI response and create structured citation data"""
        import re

        citations = []
        context_documents = context_documents or []

        # Find citation patterns in AI response: [FONTE: Documento Aziendale] Nome Documento
        citation_pattern = r'\[FONTE:\s*Documento\s+Aziendale\]\s*([^\n\.,]+)'
        matches = re.findall(citation_pattern, ai_response, re.IGNORECASE)

        # Create structured citations for each match
        for i, cited_doc_name in enumerate(matches):
            cited_doc_name = cited_doc_name.strip()

            # Try to match with actual documents from context
            matched_doc = None
            for doc in context_documents:
                if (cited_doc_name.lower() in doc.get('title', '').lower() or
                    doc.get('title', '').lower() in cited_doc_name.lower() or
                    doc.get('document_code', '').lower() in cited_doc_name.lower()):
                    matched_doc = doc
                    break

            # Determine data source - documents from semantic_search have certainty, others don't
            data_source = "WEAVIATE" if matched_doc and matched_doc.get('certainty') is not None else "POSTGRESQL"

            citation = {
                "id": f"CIT_{i+1:03d}",
                "cited_document": cited_doc_name,
                "source": "AI_Analysis",
                "data_source": data_source,  # Track if from Weaviate or PostgreSQL
                "document_info": {
                    "title": matched_doc.get('title', cited_doc_name) if matched_doc else cited_doc_name,
                    "document_type": matched_doc.get('document_type', 'referenced') if matched_doc else 'referenced',
                    "document_code": matched_doc.get('document_code', '') if matched_doc else '',
                    "authority": matched_doc.get('authority', '') if matched_doc else ''
                },
                "relevance": {
                    "matched_from_context": bool(matched_doc),
                    "certainty": matched_doc.get('certainty', 0.0) if matched_doc else 0.0,
                    "search_score": matched_doc.get('search_score', 0.0) if matched_doc else 0.0
                },
                "weaviate_required": True  # Flag indicating Weaviate should be mandatory
            }
            citations.append(citation)

        # If AI didn't use proper citation format, create implicit citations from context documents
        if not citations and context_documents:
            print(f"[{self.name}] No formal citations found, using context documents as implicit citations")
            for i, doc in enumerate(context_documents[:3]):  # Max 3 implicit citations
                # Determine data source for implicit citations
                data_source = "WEAVIATE" if doc.get('certainty') is not None else "POSTGRESQL"

                citations.append({
                    "id": f"IMP_{i+1:03d}",
                    "cited_document": doc.get('title', 'Documento aziendale'),
                    "source": "Context_Document",
                    "data_source": data_source,  # Track data source for implicit citations
                    "document_info": {
                        "title": doc.get('title', 'N/A'),
                        "document_type": doc.get('document_type', 'unknown'),
                        "document_code": doc.get('document_code', ''),
                        "authority": doc.get('authority', '')
                    },
                    "relevance": {
                        "matched_from_context": True,
                        "certainty": doc.get('certainty', 0.0),
                        "search_score": doc.get('search_score', 0.0)
                    },
                    "weaviate_required": True  # Weaviate should be mandatory for all specialists
                })

        return citations

    def validate_weaviate_usage(self, citations: list) -> dict:
        """Validate that specialist used Weaviate documents before suggesting actions"""
        weaviate_citations = [c for c in citations if c.get('data_source') == 'WEAVIATE']
        postgresql_citations = [c for c in citations if c.get('data_source') == 'POSTGRESQL']

        validation_result = {
            "weaviate_used": len(weaviate_citations) > 0,
            "weaviate_count": len(weaviate_citations),
            "postgresql_count": len(postgresql_citations),
            "total_citations": len(citations),
            "compliance": "COMPLIANT" if len(weaviate_citations) > 0 else "NON_COMPLIANT",
            "warning": None
        }

        if len(weaviate_citations) == 0:
            validation_result["warning"] = "MANDATORY: Specialist must use Weaviate documents before suggesting actions"
            validation_result["recommendation"] = "Ensure semantic search is called and Weaviate documents are retrieved"

        return validation_result
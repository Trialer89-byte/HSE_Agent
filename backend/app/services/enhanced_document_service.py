from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.vector_service import VectorService
from app.models.document import Document


class EnhancedDocumentService:
    """
    Enhanced document service with intelligent search and retrieval capabilities
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_service = VectorService()
        
        # Search optimization settings
        self.default_search_limit = 20
        self.focused_search_limit = 5
        self.similarity_threshold = 0.7
        self.relaxed_threshold = 0.6
    
    async def intelligent_document_search(
        self,
        permit_data: Dict[str, Any],
        tenant_id: int,
        search_strategy: str = "comprehensive"
    ) -> List[Dict[str, Any]]:
        """
        Perform intelligent document search based on permit context
        
        Args:
            permit_data: Permit information for context
            tenant_id: Tenant isolation
            search_strategy: "comprehensive" | "focused" | "adaptive"
        """
        if search_strategy == "comprehensive":
            return await self._comprehensive_search(permit_data, tenant_id)
        elif search_strategy == "focused":
            return await self._focused_search(permit_data, tenant_id)
        elif search_strategy == "adaptive":
            return await self._adaptive_search(permit_data, tenant_id)
        else:
            raise ValueError(f"Unknown search strategy: {search_strategy}")
    
    async def _comprehensive_search(
        self,
        permit_data: Dict[str, Any],
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive search covering multiple aspects of the permit
        """
        all_results = []
        
        # 1. Primary search based on work type and description
        primary_query = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('work_type', '')}"
        primary_results = await self.vector_service.hybrid_search(
            query=primary_query,
            filters={
                "tenant_id": tenant_id,
                "document_type": ["normativa", "istruzione_operativa"]
            },
            limit=15,
            threshold=self.similarity_threshold
        )
        all_results.extend(primary_results)
        
        # 2. Work-type specific search
        if permit_data.get("work_type"):
            work_type_results = await self._search_by_work_type(
                permit_data["work_type"], tenant_id
            )
            all_results.extend(work_type_results)
        
        # 3. Risk-based search
        risk_keywords = self._extract_risk_keywords(permit_data)
        if risk_keywords:
            risk_results = await self._search_by_risk_keywords(
                risk_keywords, tenant_id
            )
            all_results.extend(risk_results)
        
        # 4. Location-specific search
        if permit_data.get("location"):
            location_results = await self._search_by_location(
                permit_data["location"], tenant_id
            )
            all_results.extend(location_results)
        
        # Remove duplicates and rank by relevance
        return self._deduplicate_and_rank(all_results)
    
    async def _focused_search(
        self,
        permit_data: Dict[str, Any],
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """
        Focused search for specific, high-relevance documents
        """
        # Build targeted search query
        search_terms = []
        
        if permit_data.get("work_type"):
            search_terms.append(permit_data["work_type"])
        
        # Extract key terms from description
        description = permit_data.get("description", "")
        key_terms = self._extract_key_terms(description)
        search_terms.extend(key_terms[:3])  # Top 3 key terms
        
        query = " ".join(search_terms)
        
        return await self.vector_service.hybrid_search(
            query=query,
            filters={
                "tenant_id": tenant_id,
                "document_type": ["normativa", "istruzione_operativa"]
            },
            limit=self.focused_search_limit,
            threshold=self.similarity_threshold
        )
    
    async def _adaptive_search(
        self,
        permit_data: Dict[str, Any],
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """
        Adaptive search that adjusts based on initial results quality
        """
        # Start with focused search
        initial_results = await self._focused_search(permit_data, tenant_id)
        
        # Analyze quality of initial results
        avg_score = sum(r.get("search_score", 0) for r in initial_results) / max(len(initial_results), 1)
        
        if avg_score >= self.similarity_threshold and len(initial_results) >= 3:
            # High quality results, return focused search
            return initial_results
        else:
            # Low quality or insufficient results, expand search
            print(f"[EnhancedDocumentService] Initial search quality low ({avg_score:.2f}), expanding search")
            return await self._comprehensive_search(permit_data, tenant_id)
    
    async def _search_by_work_type(
        self,
        work_type: str,
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """
        Search for documents specific to work type
        """
        work_type_keywords = {
            "chimico": ["sostanze chimiche", "DPI chimici", "REACH", "CLP", "SDS"],
            "scavo": ["scavi", "consolidamento", "servizi interrati", "DPR 177"],
            "elettrico": ["impianti elettrici", "CEI", "bassa tensione", "alta tensione"],
            "meccanico": ["macchine", "attrezzature", "manutenzione", "lockout tagout"],
            "edile": ["cantiere", "ponteggi", "DPI anticaduta", "lavori in quota"],
            "pulizia": ["detergenti", "disinfettanti", "spazi confinati", "ventilazione"]
        }
        
        keywords = work_type_keywords.get(work_type, [work_type])
        query = " ".join(keywords)
        
        return await self.vector_service.hybrid_search(
            query=query,
            filters={
                "tenant_id": tenant_id,
                "industry_sectors": [work_type]
            },
            limit=5,
            threshold=self.relaxed_threshold
        )
    
    async def _search_by_risk_keywords(
        self,
        risk_keywords: List[str],
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """
        Search for documents based on identified risk keywords
        """
        query = " ".join(risk_keywords)
        
        return await self.vector_service.hybrid_search(
            query=query,
            filters={
                "tenant_id": tenant_id,
                "document_type": ["normativa"]  # Focus on regulations for risks
            },
            limit=5,
            threshold=self.relaxed_threshold
        )
    
    async def _search_by_location(
        self,
        location: str,
        tenant_id: int
    ) -> List[Dict[str, Any]]:
        """
        Search for location-specific documents
        """
        location_keywords = self._extract_location_risks(location)
        if not location_keywords:
            return []
        
        query = f"{location} {' '.join(location_keywords)}"
        
        return await self.vector_service.hybrid_search(
            query=query,
            filters={
                "tenant_id": tenant_id,
                "document_type": ["istruzione_operativa"]  # Focus on procedures for locations
            },
            limit=3,
            threshold=self.relaxed_threshold
        )
    
    def _extract_risk_keywords(self, permit_data: Dict[str, Any]) -> List[str]:
        """
        Extract risk-related keywords from permit data
        """
        risk_keywords = []
        
        # HSE risk terms to look for
        hse_risk_terms = [
            "altezza", "caduta", "gas", "sostanze", "energia", "macchine",
            "esplosione", "incendio", "tossico", "corrosivo", "ustioni",
            "elettrico", "meccanico", "chimico", "biologico", "fisico"
        ]
        
        # Check in description and title
        text_content = f"{permit_data.get('description', '')} {permit_data.get('title', '')}".lower()
        
        for term in hse_risk_terms:
            if term in text_content:
                risk_keywords.append(term)
        
        return risk_keywords
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """
        Extract key terms from text using simple heuristics
        """
        if not text:
            return []
        
        # HSE-specific important terms
        important_terms = [
            "sicurezza", "protezione", "prevenzione", "controllo", "verifica",
            "ispezione", "manutenzione", "emergenza", "evacuazione", "soccorso",
            "formazione", "addestramento", "competenza", "autorizzazione"
        ]
        
        words = text.lower().split()
        key_terms = []
        
        for term in important_terms:
            if term in text.lower():
                key_terms.append(term)
        
        # Also include terms that appear multiple times
        word_freq = {}
        for word in words:
            if len(word) > 4:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Add frequently mentioned terms
        frequent_terms = [word for word, freq in word_freq.items() if freq > 1]
        key_terms.extend(frequent_terms[:3])  # Top 3 frequent terms
        
        return list(set(key_terms))  # Remove duplicates
    
    def _extract_location_risks(self, location: str) -> List[str]:
        """
        Extract location-specific risk keywords
        """
        location_risks = {
            "cantiere": ["ponteggi", "gru", "cadute", "traffico"],
            "laboratorio": ["sostanze", "vetreria", "ventilazione", "emergenza"],
            "magazzino": ["stoccaggio", "movimentazione", "scaffalature", "muletti"],
            "officina": ["macchine", "rumore", "oli", "saldatura"],
            "impianto": ["pressione", "temperatura", "energia", "lockout"],
            "esterno": ["condizioni meteorologiche", "visibilità", "traffico"],
            "sotterraneo": ["ventilazione", "gas", "emergenza", "illuminazione"],
            "quota": ["anticaduta", "imbracature", "ancoraggio", "salvataggio"]
        }
        
        location_lower = location.lower()
        risk_keywords = []
        
        for loc_type, risks in location_risks.items():
            if loc_type in location_lower:
                risk_keywords.extend(risks)
        
        return risk_keywords
    
    def _deduplicate_and_rank(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicates and rank results by relevance
        """
        seen_docs = set()
        unique_results = []
        
        for result in results:
            doc_id = result.get("document_code", "")
            if doc_id and doc_id not in seen_docs:
                seen_docs.add(doc_id)
                unique_results.append(result)
        
        # Sort by search score (descending)
        unique_results.sort(key=lambda x: x.get("search_score", 0), reverse=True)
        
        # Limit to reasonable number
        return unique_results[:self.default_search_limit]
    
    async def get_document_usage_stats(self, tenant_id: int) -> Dict[str, Any]:
        """
        Get statistics about document usage for optimization
        """
        total_docs = self.db.query(Document).filter(
            Document.tenant_id == tenant_id,
            Document.is_active == True
        ).count()
        
        doc_types = self.db.query(Document.document_type).filter(
            Document.tenant_id == tenant_id,
            Document.is_active == True
        ).distinct().all()
        
        categories = self.db.query(Document.category).filter(
            Document.tenant_id == tenant_id,
            Document.is_active == True
        ).distinct().all()
        
        return {
            "total_documents": total_docs,
            "document_types": [dt[0] for dt in doc_types if dt[0]],
            "categories": [cat[0] for cat in categories if cat[0]],
            "search_optimization": {
                "recommended_strategy": "adaptive" if total_docs > 50 else "comprehensive",
                "search_threshold": self.similarity_threshold,
                "last_updated": datetime.utcnow().isoformat()
            }
        }
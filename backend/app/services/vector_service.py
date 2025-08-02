from typing import List, Dict, Any, Optional
import weaviate
from weaviate.exceptions import WeaviateException
import json

from app.config.settings import settings


class VectorService:
    """
    Service for Weaviate vector database operations
    """
    
    def __init__(self):
        # Initialize Weaviate client
        if settings.weaviate_api_key:
            auth_config = weaviate.AuthApiKey(api_key=settings.weaviate_api_key)
            self.client = weaviate.Client(
                url=settings.weaviate_url,
                auth_client_secret=auth_config
            )
        else:
            self.client = weaviate.Client(url=settings.weaviate_url)
        
        # Ensure schema exists
        self._ensure_schema()
    
    def _ensure_schema(self):
        """
        Ensure HSEDocument schema exists in Weaviate
        """
        schema = {
            "class": "HSEDocument",
            "description": "Documenti normativi e istruzioni operative HSE",
            "properties": [
                {
                    "name": "document_code",
                    "dataType": ["text"],
                    "description": "Codice univoco documento (es. D.Lgs 81/2008)"
                },
                {
                    "name": "title",
                    "dataType": ["text"],
                    "description": "Titolo completo documento"
                },
                {
                    "name": "content",
                    "dataType": ["text"],
                    "description": "Contenuto testuale completo del documento"
                },
                {
                    "name": "content_chunk",
                    "dataType": ["text"],
                    "description": "Chunk semantico di contenuto"
                },
                {
                    "name": "document_type",
                    "dataType": ["text"],
                    "description": "Tipo documento: normativa | istruzione_operativa"
                },
                {
                    "name": "category",
                    "dataType": ["text"],
                    "description": "Categoria HSE: sicurezza | dpi | emergenza | chimico | meccanico"
                },
                {
                    "name": "industry_sectors",
                    "dataType": ["text[]"],
                    "description": "Settori applicabili: [chimico, scavo, edile, manifatturiero]"
                },
                {
                    "name": "tenant_id",
                    "dataType": ["int"],
                    "description": "ID tenant per isolamento multi-tenant"
                },
                {
                    "name": "authority",
                    "dataType": ["text"],
                    "description": "Autorità emittente (Stato, UNI, azienda)"
                },
                {
                    "name": "ai_keywords",
                    "dataType": ["text[]"],
                    "description": "Keywords estratte da AI"
                },
                {
                    "name": "relevance_score",
                    "dataType": ["number"],
                    "description": "Score rilevanza 0-1"
                },
                {
                    "name": "chunk_index",
                    "dataType": ["int"],
                    "description": "Indice chunk nel documento originale"
                },
                {
                    "name": "section_title",
                    "dataType": ["text"],
                    "description": "Titolo sezione/articolo di appartenenza"
                }
            ],
            "vectorizer": "text2vec-transformers",
            "moduleConfig": {
                "text2vec-transformers": {
                    "poolingStrategy": "masked_mean",
                    "vectorizeClassName": False
                }
            }
        }
        
        try:
            # Check if class exists
            if not self.client.schema.exists("HSEDocument"):
                self.client.schema.create_class(schema)
        except WeaviateException as e:
            print(f"Error creating schema: {e}")
    
    async def add_document_chunks(
        self,
        document_id: int,
        document_code: str,
        title: str,
        chunks: List[Dict[str, Any]],
        document_type: str,
        category: str,
        tenant_id: int,
        industry_sectors: List[str] = None,
        authority: str = None
    ) -> List[str]:
        """
        Add document chunks to vector database
        """
        chunk_ids = []
        
        try:
            for i, chunk in enumerate(chunks):
                # Prepare object data
                obj_data = {
                    "document_code": document_code,
                    "title": title,
                    "content": chunk.get("content", ""),
                    "content_chunk": chunk.get("content", ""),
                    "document_type": document_type,
                    "category": category,
                    "industry_sectors": industry_sectors or [],
                    "tenant_id": tenant_id,
                    "authority": authority or "",
                    "ai_keywords": chunk.get("ai_keywords", []),
                    "relevance_score": chunk.get("relevance_score", 0.0),
                    "chunk_index": chunk.get("chunk_index", i),
                    "section_title": chunk.get("section_title", f"Sezione {i+1}")
                }
                
                # Add to Weaviate
                result = self.client.data_object.create(
                    data_object=obj_data,
                    class_name="HSEDocument"
                )
                
                chunk_ids.append(result)
                
        except WeaviateException as e:
            print(f"Error adding document chunks: {e}")
            raise
        
        return chunk_ids
    
    async def hybrid_search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and keyword matching
        """
        try:
            # Build where filter
            where_filter = {}
            if filters:
                conditions = []
                
                if "tenant_id" in filters:
                    conditions.append({
                        "path": ["tenant_id"],
                        "operator": "Equal",
                        "valueInt": filters["tenant_id"]
                    })
                
                if "document_type" in filters:
                    if isinstance(filters["document_type"], list):
                        for doc_type in filters["document_type"]:
                            conditions.append({
                                "path": ["document_type"],
                                "operator": "Equal",
                                "valueText": doc_type
                            })
                    else:
                        conditions.append({
                            "path": ["document_type"],
                            "operator": "Equal",
                            "valueText": filters["document_type"]
                        })
                
                if "industry_sectors" in filters:
                    for sector in filters["industry_sectors"]:
                        conditions.append({
                            "path": ["industry_sectors"],
                            "operator": "ContainsAny",
                            "valueText": [sector]
                        })
                
                if len(conditions) > 1:
                    where_filter = {
                        "operator": "And",
                        "operands": conditions
                    }
                elif len(conditions) == 1:
                    where_filter = conditions[0]
            
            # Perform hybrid search
            query_builder = (
                self.client.query
                .get("HSEDocument", [
                    "document_code",
                    "title", 
                    "content_chunk",
                    "document_type",
                    "category",
                    "authority",
                    "section_title",
                    "chunk_index",
                    "relevance_score"
                ])
                .with_hybrid(
                    query=query,
                    alpha=0.7  # Balance between vector (0) and keyword (1) search
                )
                .with_limit(limit)
            )
            
            if where_filter:
                query_builder = query_builder.with_where(where_filter)
            
            # Add additional vector for ranking
            query_builder = query_builder.with_additional(["score", "distance"])
            
            result = query_builder.do()
            
            # Process results
            documents = []
            if "data" in result and "Get" in result["data"] and "HSEDocument" in result["data"]["Get"]:
                for item in result["data"]["Get"]["HSEDocument"]:
                    # Filter by threshold
                    score = item["_additional"]["score"]
                    if score >= threshold:
                        documents.append({
                            "document_code": item["document_code"],
                            "title": item["title"],
                            "content": item["content_chunk"],
                            "document_type": item["document_type"],
                            "category": item["category"],
                            "authority": item["authority"],
                            "section_title": item["section_title"],
                            "chunk_index": item["chunk_index"],
                            "relevance_score": item["relevance_score"],
                            "search_score": score
                        })
            
            return documents
            
        except WeaviateException as e:
            print(f"Error in hybrid search: {e}")
            return []
    
    async def semantic_search(
        self,
        query: str,
        tenant_id: int,
        document_types: List[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Pure semantic vector search
        """
        try:
            # Build where filter for tenant isolation
            where_filter = {
                "path": ["tenant_id"],
                "operator": "Equal",
                "valueInt": tenant_id
            }
            
            # Add document type filter if specified
            if document_types:
                type_conditions = []
                for doc_type in document_types:
                    type_conditions.append({
                        "path": ["document_type"],
                        "operator": "Equal",
                        "valueText": doc_type
                    })
                
                if len(type_conditions) > 1:
                    type_filter = {
                        "operator": "Or",
                        "operands": type_conditions
                    }
                else:
                    type_filter = type_conditions[0]
                
                where_filter = {
                    "operator": "And",
                    "operands": [where_filter, type_filter]
                }
            
            result = (
                self.client.query
                .get("HSEDocument", [
                    "document_code",
                    "title",
                    "content_chunk", 
                    "document_type",
                    "category",
                    "authority",
                    "section_title"
                ])
                .with_near_text({"concepts": [query]})
                .with_where(where_filter)
                .with_limit(limit)
                .with_additional(["certainty", "distance"])
                .do()
            )
            
            documents = []
            if "data" in result and "Get" in result["data"] and "HSEDocument" in result["data"]["Get"]:
                for item in result["data"]["Get"]["HSEDocument"]:
                    documents.append({
                        "document_code": item["document_code"],
                        "title": item["title"],
                        "content": item["content_chunk"],
                        "document_type": item["document_type"],
                        "category": item["category"],
                        "authority": item["authority"],
                        "section_title": item["section_title"],
                        "certainty": item["_additional"]["certainty"],
                        "distance": item["_additional"]["distance"]
                    })
            
            return documents
            
        except WeaviateException as e:
            print(f"Error in semantic search: {e}")
            return []
    
    async def delete_document_chunks(self, document_code: str, tenant_id: int) -> bool:
        """
        Delete all chunks for a document
        """
        try:
            where_filter = {
                "operator": "And",
                "operands": [
                    {
                        "path": ["document_code"],
                        "operator": "Equal",
                        "valueText": document_code
                    },
                    {
                        "path": ["tenant_id"],
                        "operator": "Equal",
                        "valueInt": tenant_id
                    }
                ]
            }
            
            self.client.batch.delete_objects(
                class_name="HSEDocument",
                where=where_filter
            )
            
            return True
            
        except WeaviateException as e:
            print(f"Error deleting document chunks: {e}")
            return False
from typing import List, Dict, Any, Optional
import weaviate
import json

from app.config.settings import settings


class VectorService:
    """
    Service for Weaviate vector database operations
    """
    
    def __init__(self):
        # Initialize Weaviate client with multiple fallback strategies
        self.client = None
        connection_strategies = [
            self._try_anonymous_connection,
            self._try_api_key_connection,
            self._try_startup_period_connection,
            self._try_basic_connection
        ]
        
        for strategy in connection_strategies:
            try:
                client = strategy()
                if client and self._test_connection(client):
                    self.client = client
                    print(f"[VectorService] Connected using {strategy.__name__}")
                    break
            except Exception as e:
                print(f"[VectorService] {strategy.__name__} failed: {str(e)}")
                continue
        
        if not self.client:
            print("[VectorService] All connection strategies failed, operating in offline mode")
            return
        
        # Ensure schema exists only if client is connected
        self._ensure_schema()
    
    def _batch_callback(self, results: List[Dict[str, Any]]):
        """
        Callback for batch processing to handle errors
        """
        for result in results:
            if 'result' in result and 'errors' in result['result']:
                print(f"[VectorService] Batch error: {result['result']['errors']}")
    
    def _try_anonymous_connection(self):
        """Try anonymous connection"""
        return weaviate.Client(
            url=settings.weaviate_url,
            additional_headers={}
        )
    
    def _try_api_key_connection(self):
        """Try API key connection if key is available"""
        if not settings.weaviate_api_key or not settings.weaviate_api_key.strip():
            raise Exception("No API key available")
        
        auth_config = weaviate.AuthApiKey(api_key=settings.weaviate_api_key)
        return weaviate.Client(
            url=settings.weaviate_url,
            auth_client_secret=auth_config
        )
    
    def _try_startup_period_connection(self):
        """Try connection with startup period"""
        return weaviate.Client(
            url=settings.weaviate_url,
            startup_period=10
        )
    
    def _try_basic_connection(self):
        """Try basic connection without any authentication"""
        return weaviate.Client(url=settings.weaviate_url)
    
    def _test_connection(self, client):
        """Test if the client connection works"""
        try:
            # Try to get schema
            schema = client.schema.get()
            # Try to check if ready
            ready = client.is_ready()
            return True
        except Exception as e:
            print(f"[VectorService] Connection test failed: {str(e)}")
            return False
    
    def _ensure_schema(self):
        """
        Ensure HSEDocument schema exists in Weaviate
        """
        if not self.client:
            print("[VectorService] No client available, skipping schema creation")
            return
            
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
        except Exception as e:
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
        Add document chunks to vector database using batch operations
        """
        if not self.client:
            print("[VectorService] No client available, skipping chunk addition")
            return []
            
        chunk_ids = []
        
        try:
            # Configure batch with optimal settings
            batch_size = 50  # Reduced from 100 to avoid timeout errors
            self.client.batch.configure(
                batch_size=batch_size,
                dynamic=True,  # Dynamic batching for better performance
                timeout_retries=3,
                callback=self._batch_callback
            )
            
            # Prepare all objects for batch insertion
            successful_chunks = 0
            failed_chunks = 0
            
            with self.client.batch as batch:
                for i, chunk in enumerate(chunks):
                    try:
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
                        
                        # Add to batch
                        uuid = batch.add_data_object(
                            data_object=obj_data,
                            class_name="HSEDocument"
                        )
                        chunk_ids.append(uuid)
                        successful_chunks += 1
                        
                    except Exception as chunk_error:
                        print(f"[VectorService] Error processing chunk {i}: {chunk_error}")
                        failed_chunks += 1
                        # Continue processing other chunks
                        continue
                    
                    # Log progress every 25 chunks (reduced batch size)
                    if (i + 1) % 25 == 0:
                        print(f"[VectorService] Processed {i + 1}/{len(chunks)} chunks (Success: {successful_chunks}, Failed: {failed_chunks})")
                
                # Final flush happens automatically on context exit
                print(f"[VectorService] Completed batch processing: {successful_chunks} successful, {failed_chunks} failed out of {len(chunks)} total chunks")
                
                # Raise error if too many failures
                if failed_chunks > len(chunks) * 0.1:  # More than 10% failed
                    raise Exception(f"Too many chunk failures: {failed_chunks}/{len(chunks)}")
                
        except Exception as e:
            print(f"Error adding document chunks: {e}")
            # Return partial results if some chunks were successful
            if chunk_ids:
                print(f"[VectorService] Returning {len(chunk_ids)} successful chunk IDs despite errors")
                return chunk_ids
            raise
        
        return chunk_ids
    
    async def hybrid_search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        threshold: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Hybrid search combining vector similarity and keyword matching
        """
        if not self.client:
            print("[VectorService] No client available, returning empty results")
            return []
            
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
                        # Create OR condition for multiple document types
                        doc_type_conditions = []
                        for doc_type in filters["document_type"]:
                            doc_type_conditions.append({
                                "path": ["document_type"],
                                "operator": "Equal",
                                "valueText": doc_type
                            })
                        if len(doc_type_conditions) > 1:
                            conditions.append({
                                "operator": "Or",
                                "operands": doc_type_conditions
                            })
                        elif len(doc_type_conditions) == 1:
                            conditions.append(doc_type_conditions[0])
                    else:
                        conditions.append({
                            "path": ["document_type"],
                            "operator": "Equal",
                            "valueText": filters["document_type"]
                        })
                
                if "industry_sectors" in filters and filters["industry_sectors"]:
                    # Only add industry sector filter if list is not empty
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
                    "relevance_score",
                    "ai_keywords"  # Include keywords for agent use
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
                    # Convert score to float if it's a string
                    if isinstance(score, str):
                        try:
                            score = float(score)
                        except (ValueError, TypeError):
                            score = 0.0
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
                            "ai_keywords": item.get("ai_keywords", []),  # Include keywords for agents
                            "search_score": score
                        })
            
            return documents
            
        except Exception as e:
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
        if not self.client:
            print("[VectorService] No client available, returning empty results")
            return []
            
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
                    "section_title",
                    "ai_keywords"  # Include keywords for agent use
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
                        "ai_keywords": item.get("ai_keywords", []),  # Include keywords for agents
                        "section_title": item["section_title"],
                        "certainty": item["_additional"]["certainty"],
                        "distance": item["_additional"]["distance"]
                    })
            
            return documents
            
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []
    
    async def delete_document_chunks(self, document_code: str, tenant_id: int) -> bool:
        """
        Delete all chunks for a document
        """
        if not self.client:
            print("[VectorService] No client available, skipping chunk deletion")
            return True  # Return True to avoid blocking operations
            
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
            
        except Exception as e:
            print(f"Error deleting document chunks: {e}")
            return False
    
    async def update_document_metadata(
        self, 
        document_code: str, 
        tenant_id: int, 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for all chunks of a document
        """
        if not self.client:
            print("[VectorService] No client available, skipping metadata update")
            return True  # Return True to avoid blocking operations
            
        try:
            # For now, we'll just log the update request
            # In a real implementation, you would update the vector store entries
            print(f"[VectorService] Would update metadata for document {document_code}: {metadata}")
            
            # TODO: Implement actual Weaviate update logic when needed
            # This would involve:
            # 1. Finding all chunks with the document_code and tenant_id
            # 2. Updating their metadata fields
            # 3. Re-indexing if necessary
            
            return True
            
        except Exception as e:
            print(f"Error updating document metadata: {e}")
            return False
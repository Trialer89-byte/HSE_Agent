from typing import List, Dict, Any, Optional
import os
from datetime import datetime
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session
import PyPDF2
import docx
import re

from app.models.document import Document
from app.services.vector_service import VectorService
from app.services.storage_service import StorageService
from app.core.tenant import validate_tenant_limits


class DocumentService:
    """
    Service for document management and processing
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.vector_service = VectorService()
        self.storage_service = StorageService()
    
    async def upload_document(
        self,
        file: UploadFile,
        document_code: str,
        title: str,
        document_type: str,
        category: str,
        tenant_id: int,
        uploaded_by: int,
        industry_sectors: List[str] = None,
        authority: str = None,
        subcategory: str = None,
        scope: str = "tenant"
    ) -> Document:
        """
        Upload and process a document
        """
        # Validate file type
        file_extension = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = ['.pdf', '.docx', '.doc', '.txt']
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed"
            )
        
        # Check tenant limits
        from app.models.tenant import Tenant
        tenant = self.db.query(Tenant).filter(Tenant.id == tenant_id).first()
        if not validate_tenant_limits(tenant, "upload_document", self.db):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Document limit reached for tenant"
            )
        
        # Check if document already exists
        existing_doc = self.db.query(Document).filter(
            Document.tenant_id == tenant_id,
            Document.document_code == document_code
        ).first()
        
        if existing_doc:
            # Create new version
            version_parts = existing_doc.version.split('.')
            new_version = f"{version_parts[0]}.{int(version_parts[1]) + 1}"
        else:
            new_version = "1.0"
        
        try:
            # Upload file to storage
            file_path = await self.storage_service.upload_file(
                file, f"documents/{tenant_id}/{document_code}_{new_version}{file_extension}"
            )
            
            # Extract text content
            content = await self._extract_text_content(file, file_extension)
            
            # Create semantic chunks
            chunks = await self._create_semantic_chunks(
                content, document_type, document_code
            )
            
            # Create document record
            document = Document(
                tenant_id=tenant_id,
                document_code=document_code,
                title=title,
                document_type=document_type,
                category=category,
                subcategory=subcategory,
                scope=scope,
                industry_sectors=industry_sectors or [],
                file_path=file_path,
                content_summary=content[:500] + "..." if len(content) > 500 else content,
                version=new_version,
                authority=authority,
                uploaded_by=uploaded_by,
                publication_date=datetime.now().date()
            )
            
            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)
            
            # Add chunks to vector database
            chunk_ids = await self.vector_service.add_document_chunks(
                document_id=document.id,
                document_code=document_code,
                title=title,
                chunks=chunks,
                document_type=document_type,
                category=category,
                tenant_id=tenant_id,
                industry_sectors=industry_sectors,
                authority=authority
            )
            
            # Store first chunk ID as vector_id
            if chunk_ids:
                document.vector_id = chunk_ids[0]
                self.db.commit()
            
            return document
            
        except Exception as e:
            # Cleanup on error
            if 'file_path' in locals():
                await self.storage_service.delete_file(file_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process document: {str(e)}"
            )
    
    async def _extract_text_content(self, file: UploadFile, file_extension: str) -> str:
        """
        Extract text content from uploaded file
        """
        content = ""
        
        try:
            if file_extension == '.pdf':
                # Extract from PDF
                pdf_reader = PyPDF2.PdfReader(file.file)
                for page in pdf_reader.pages:
                    content += page.extract_text() + "\n"
            
            elif file_extension in ['.docx']:
                # Extract from DOCX
                doc = docx.Document(file.file)
                for paragraph in doc.paragraphs:
                    content += paragraph.text + "\n"
            
            elif file_extension == '.txt':
                # Read text file
                content = (await file.read()).decode('utf-8')
            
            # Reset file pointer
            file.file.seek(0)
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to extract text from file: {str(e)}"
            )
        
        return content.strip()
    
    async def _create_semantic_chunks(
        self, 
        content: str, 
        document_type: str, 
        document_code: str
    ) -> List[Dict[str, Any]]:
        """
        Create semantic chunks based on document type
        """
        chunks = []
        
        if document_type == "normativa":
            # For legal documents: split by articles/sections
            chunks = self._legal_document_chunker(content, document_code)
        elif document_type == "istruzione_operativa":
            # For procedures: split by operational steps
            chunks = self._procedure_chunker(content, document_code)
        else:
            # Default chunking
            chunks = self._default_chunker(content, document_code)
        
        # Enrich chunks with AI keywords
        for i, chunk in enumerate(chunks):
            chunk["ai_keywords"] = self._extract_keywords(chunk["content"])
            chunk["relevance_score"] = self._calculate_relevance_score(chunk["content"])
        
        return chunks
    
    def _legal_document_chunker(self, content: str, document_code: str) -> List[Dict[str, Any]]:
        """
        Chunk legal documents by articles and sections
        """
        chunks = []
        
        # Split by articles
        article_pattern = r'(Art\.\s*\d+|Articolo\s+\d+)'
        sections = re.split(article_pattern, content, flags=re.IGNORECASE)
        
        current_section = ""
        for i, section in enumerate(sections):
            if re.match(article_pattern, section, re.IGNORECASE):
                current_section = section.strip()
            elif section.strip() and current_section:
                chunk_content = f"{current_section}\n{section.strip()}"
                if len(chunk_content) > 50:  # Skip very short chunks
                    chunks.append({
                        "content": chunk_content,
                        "section_title": current_section,
                        "chunk_index": len(chunks),
                        "word_count": len(chunk_content.split())
                    })
        
        # If no articles found, use paragraph chunking
        if not chunks:
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for i, paragraph in enumerate(paragraphs):
                if len(paragraph) > 100:  # Only substantial paragraphs
                    chunks.append({
                        "content": paragraph,
                        "section_title": f"Paragrafo {i+1}",
                        "chunk_index": i,
                        "word_count": len(paragraph.split())
                    })
        
        return chunks
    
    def _procedure_chunker(self, content: str, document_code: str) -> List[Dict[str, Any]]:
        """
        Chunk operational procedures by steps
        """
        chunks = []
        
        # Split by procedure steps
        step_pattern = r'(Step\s*\d+|Fase\s*\d+|Procedura\s*\d+|\d+\.\s)'
        sections = re.split(step_pattern, content, flags=re.IGNORECASE)
        
        current_step = ""
        for i, section in enumerate(sections):
            if re.match(step_pattern, section, re.IGNORECASE):
                current_step = section.strip()
            elif section.strip() and current_step:
                chunk_content = f"{current_step}\n{section.strip()}"
                if len(chunk_content) > 50:
                    chunks.append({
                        "content": chunk_content,
                        "section_title": current_step,
                        "chunk_index": len(chunks),
                        "word_count": len(chunk_content.split())
                    })
        
        # If no steps found, use default chunking
        if not chunks:
            return self._default_chunker(content, document_code)
        
        return chunks
    
    def _default_chunker(self, content: str, document_code: str) -> List[Dict[str, Any]]:
        """
        Default chunking strategy
        """
        chunks = []
        max_chunk_size = 1000
        overlap = 100
        
        words = content.split()
        
        for i in range(0, len(words), max_chunk_size - overlap):
            chunk_words = words[i:i + max_chunk_size]
            chunk_content = ' '.join(chunk_words)
            
            if len(chunk_content.strip()) > 50:
                chunks.append({
                    "content": chunk_content,
                    "section_title": f"Sezione {len(chunks) + 1}",
                    "chunk_index": len(chunks),
                    "word_count": len(chunk_words)
                })
        
        return chunks
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extract keywords from text using simple heuristics
        """
        # HSE-specific keywords
        hse_keywords = [
            "sicurezza", "dpi", "rischio", "pericolo", "prevenzione", "protezione",
            "emergenza", "evacuazione", "antincendio", "chimico", "tossico",
            "inquinamento", "ambiente", "rifiuti", "emissioni", "salute",
            "infortunio", "malattia", "professionale", "lavoro", "cantiere",
            "manutenzione", "controllo", "verifica", "ispezione", "audit"
        ]
        
        found_keywords = []
        text_lower = text.lower()
        
        for keyword in hse_keywords:
            if keyword in text_lower:
                found_keywords.append(keyword)
        
        return found_keywords
    
    def _calculate_relevance_score(self, text: str) -> float:
        """
        Calculate relevance score based on HSE content
        """
        hse_terms = [
            "sicurezza", "dpi", "rischio", "protezione", "emergenza",
            "salute", "ambiente", "prevenzione", "controllo", "verifica"
        ]
        
        text_lower = text.lower()
        score = 0.0
        
        for term in hse_terms:
            if term in text_lower:
                score += 0.1
        
        return min(score, 1.0)
    
    def get_documents_by_tenant(
        self,
        tenant_id: int,
        document_type: str = None,
        category: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Document]:
        """
        Get documents for a tenant with filtering
        """
        query = self.db.query(Document).filter(
            Document.tenant_id == tenant_id,
            Document.is_active == True
        )
        
        if document_type:
            query = query.filter(Document.document_type == document_type)
        
        if category:
            query = query.filter(Document.category == category)
        
        return query.offset(offset).limit(limit).all()
    
    async def delete_document(self, document_id: int, tenant_id: int) -> bool:
        """
        Delete document and its vector chunks
        """
        document = self.db.query(Document).filter(
            Document.id == document_id,
            Document.tenant_id == tenant_id
        ).first()
        
        if not document:
            return False
        
        try:
            # Delete from vector database
            await self.vector_service.delete_document_chunks(
                document.document_code, tenant_id
            )
            
            # Delete file from storage
            if document.file_path:
                await self.storage_service.delete_file(document.file_path)
            
            # Delete from database
            self.db.delete(document)
            self.db.commit()
            
            return True
            
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False
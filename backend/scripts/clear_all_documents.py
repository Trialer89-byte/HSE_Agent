import os
import sys
from pathlib import Path

# Add parent directory to path to import app modules
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from sqlalchemy.orm import Session
from app.config.database import SessionLocal, engine
from app.models.document import Document
from app.services.vector_service import VectorService
import weaviate
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_postgres_documents():
    """Remove all documents from PostgreSQL database"""
    db = SessionLocal()
    try:
        # Count documents before deletion
        count = db.query(Document).count()
        logger.info(f"Found {count} documents in PostgreSQL")
        
        # Delete all documents
        db.query(Document).delete()
        db.commit()
        
        logger.info("All documents deleted from PostgreSQL successfully")
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting documents from PostgreSQL: {e}")
        raise
    finally:
        db.close()

def clear_weaviate_documents():
    """Remove all documents from Weaviate vector database"""
    try:
        # Initialize Weaviate client
        client = weaviate.Client(
            url=os.getenv("WEAVIATE_URL", "http://weaviate:8080"),
            timeout_config=(5, 15)
        )
        
        # Check if Document collection exists
        schema = client.schema.get()
        collection_exists = any(cls['class'] == 'Document' for cls in schema.get('classes', []))
        
        if not collection_exists:
            logger.info("Document collection does not exist in Weaviate")
            return 0
        
        # Get count of documents before deletion
        result = client.query.aggregate("Document").with_meta_count().do()
        count = result.get('data', {}).get('Aggregate', {}).get('Document', [{}])[0].get('meta', {}).get('count', 0)
        logger.info(f"Found {count} documents in Weaviate")
        
        if count > 0:
            # Delete all documents from Document collection
            client.batch.delete_objects(
                class_name="Document",
                where={}  # Empty where clause deletes all
            )
            logger.info("All documents deleted from Weaviate successfully")
        
        return count
    except Exception as e:
        logger.error(f"Error deleting documents from Weaviate: {e}")
        raise

def main():
    """Main function to clear all documents from both databases"""
    logger.info("Starting document cleanup process...")
    
    try:
        # Clear PostgreSQL documents
        postgres_count = clear_postgres_documents()
        
        # Clear Weaviate documents
        weaviate_count = clear_weaviate_documents()
        
        logger.info(f"\n=== CLEANUP COMPLETE ===")
        logger.info(f"Deleted {postgres_count} documents from PostgreSQL")
        logger.info(f"Deleted {weaviate_count} documents from Weaviate")
        
    except Exception as e:
        logger.error(f"Document cleanup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.config.database import Base, get_db
from app.models import *  # Import all models
from app.core.security import get_password_hash


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing"""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test"""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def sample_tenant(db):
    """Create a sample tenant for testing"""
    from app.models.tenant import Tenant
    
    tenant = Tenant(
        name="Test Company",
        domain="test.hse-enterprise.local",
        settings={"max_users": 100, "max_documents": 1000},
        is_active=True
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    return tenant


@pytest.fixture
def sample_user(db, sample_tenant):
    """Create a sample user for testing"""
    from app.models.user import User
    
    user = User(
        tenant_id=sample_tenant.id,
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpassword123"),
        first_name="Test",
        last_name="User",
        role="admin",
        is_active=True,
        is_verified=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@pytest.fixture
def sample_work_permit(db, sample_tenant, sample_user):
    """Create a sample work permit for testing"""
    from app.models.work_permit import WorkPermit
    
    permit = WorkPermit(
        tenant_id=sample_tenant.id,
        title="Test Work Permit",
        description="This is a test work permit for unit testing",
        work_type="manutenzione",
        location="Test Area",
        duration_hours=4,
        dpi_required=["casco", "scarpe antinfortunistiche"],
        created_by=sample_user.id,
        status="draft"
    )
    
    db.add(permit)
    db.commit()
    db.refresh(permit)
    
    return permit


@pytest.fixture
def sample_document(db, sample_tenant, sample_user):
    """Create a sample document for testing"""
    from app.models.document import Document
    
    document = Document(
        tenant_id=sample_tenant.id,
        document_code="TEST_001",
        title="Test Safety Procedure",
        document_type="istruzione_operativa",
        category="sicurezza",
        content_summary="Test procedure for safety operations",
        uploaded_by=sample_user.id,
        is_active=True
    )
    
    db.add(document)
    db.commit()
    db.refresh(document)
    
    return document


@pytest.fixture
def auth_headers(sample_user):
    """Create authentication headers for testing"""
    from app.core.security import create_access_token
    
    token = create_access_token(
        subject=str(sample_user.id),
        tenant_id=sample_user.tenant_id
    )
    
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response for testing"""
    return {
        "choices": [
            {
                "message": {
                    "content": '''
                    {
                        "analysis_complete": true,
                        "confidence_score": 0.8,
                        "agent_name": "TestAgent",
                        "test_field": "test_value"
                    }
                    '''
                }
            }
        ]
    }


@pytest.fixture
def mock_vector_service():
    """Mock vector service for testing"""
    class MockVectorService:
        async def hybrid_search(self, query, filters=None, limit=20, threshold=0.7):
            return [
                {
                    "document_code": "TEST_001",
                    "title": "Test Document",
                    "content": "Test content for analysis",
                    "document_type": "normativa",
                    "category": "sicurezza",
                    "authority": "Test Authority",
                    "search_score": 0.9
                }
            ]
        
        async def add_document_chunks(self, *args, **kwargs):
            return ["test_chunk_id_1", "test_chunk_id_2"]
        
        async def delete_document_chunks(self, *args, **kwargs):
            return True
    
    return MockVectorService()


@pytest.fixture
def mock_storage_service():
    """Mock storage service for testing"""
    class MockStorageService:
        async def upload_file(self, file, object_name=None):
            return "test/file/path.pdf"
        
        async def download_file(self, object_name):
            return b"test file content"
        
        async def delete_file(self, object_name):
            return True
        
        def get_file_url(self, object_name, expires_in_hours=24):
            return f"http://test-storage.com/{object_name}"
    
    return MockStorageService()


# Test data factories
class TestDataFactory:
    """Factory for creating test data"""
    
    @staticmethod
    def create_permit_data(**overrides):
        """Create permit data for testing"""
        default_data = {
            "title": "Test Work Permit",
            "description": "Test description for work permit",
            "work_type": "manutenzione",
            "location": "Test Location",
            "duration_hours": 4,
            "dpi_required": ["casco", "guanti"],
            "priority_level": "medium",
            "custom_fields": {},
            "tags": ["test"]
        }
        default_data.update(overrides)
        return default_data
    
    @staticmethod
    def create_analysis_result(**overrides):
        """Create analysis result for testing"""
        default_result = {
            "analysis_id": "test_analysis_123",
            "permit_id": 1,
            "confidence_score": 0.8,
            "processing_time": 2.5,
            "analysis_complete": True,
            "executive_summary": {
                "overall_score": 0.8,
                "critical_issues": 2,
                "recommendations": 5,
                "compliance_level": "requires_action"
            },
            "action_items": [
                {
                    "id": "ACT_001",
                    "type": "dpi_requirement",
                    "priority": "alta",
                    "title": "Aggiungere DPI mancanti",
                    "description": "Sono necessari DPI aggiuntivi per questo lavoro",
                    "suggested_action": "Integrare guanti chimici"
                }
            ],
            "citations": {
                "normative_framework": [
                    {
                        "document_info": {
                            "code": "D.Lgs 81/2008",
                            "title": "Testo Unico Sicurezza"
                        }
                    }
                ]
            }
        }
        default_result.update(overrides)
        return default_result


# Pytest configuration
def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
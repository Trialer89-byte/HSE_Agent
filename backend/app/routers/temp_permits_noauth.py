"""
Temporary override for permits router to bypass authentication during testing
"""
from fastapi import APIRouter, HTTPException, Request, status, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.config.database import get_db
from app.models.work_permit import WorkPermit
from app.schemas.work_permit import (
    PermitAnalysisResponse, PermitAnalysisRequest,
    PermitPreviewAnalysisRequest, WorkPermitResponse, WorkPermitCreate
)
from app.services.vector_service import VectorService
from app.agents.advanced_orchestrator import AdvancedHSEOrchestrator
from app.services.autogen_orchestrator import AutoGenAIOrchestrator
from app.services.fast_ai_orchestrator import FastAIOrchestrator
from app.services.mock_orchestrator import MockOrchestrator


logger = logging.getLogger(__name__)

# Create a mock user for testing
class MockUser:
    def __init__(self):
        self.tenant_id = 1
        self.id = 1
        self.department = "test"

def get_mock_user():
    return MockUser()

def mock_permission_check(permission: str):
    """Mock permission decorator that always allows access"""
    def decorator(func):
        return func
    return decorator

# Override the imports for this module
import app.routers.permits as original_permits
original_permits.get_current_user = get_mock_user
original_permits.require_permission = mock_permission_check
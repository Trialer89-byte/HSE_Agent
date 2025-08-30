"""
Test router for permits without authentication - FOR DEVELOPMENT ONLY
"""
from fastapi import APIRouter, HTTPException, Request, status, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from app.config.database import get_db
from app.models.work_permit import WorkPermit
from app.models.user import User
from app.schemas.work_permit import (
    PermitAnalysisResponse, PermitAnalysisRequest,
    PermitPreviewAnalysisRequest, WorkPermitResponse
)
from app.services.vector_service import VectorService
from app.agents.simple_autogen_agents import SimpleAutoGenHSEAgents


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/test", tags=["Test Permits - NO AUTH"])


@router.get("/permits/{permit_id}", response_model=WorkPermitResponse)
async def get_test_permit(
    permit_id: int,
    db: Session = Depends(get_db)
):
    """Get permit by ID - TEST MODE (no auth)"""
    # Use tenant_id = 1 for testing
    permit = db.query(WorkPermit).filter(
        WorkPermit.id == permit_id,
        WorkPermit.tenant_id == 1
    ).first()
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work permit not found"
        )
    
    return permit


@router.post("/permits/{permit_id}/analyze", response_model=PermitAnalysisResponse)
async def test_analyze_permit(
    permit_id: int,
    analysis_request: PermitAnalysisRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    ENDPOINT TEST: Analisi completa permesso SENZA AUTENTICAZIONE
    """
    
    try:
        # Load permit with default tenant_id = 1 for testing
        permit = db.query(WorkPermit).filter(
            WorkPermit.id == permit_id,
            WorkPermit.tenant_id == 1
        ).first()
        
        if not permit:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Work permit not found"
            )
        
        # Check if Enhanced AutoGen analysis already exists and is recent
        if (permit.ai_analysis and permit.analyzed_at and 
            not analysis_request.force_reanalysis):
            # Return existing Enhanced AutoGen analysis if less than 24 hours old
            if datetime.utcnow() - permit.analyzed_at < timedelta(hours=24):
                print(f"[TestPermitRouter] Returning cached Enhanced AutoGen analysis for permit {permit_id}")
                return PermitAnalysisResponse(**permit.ai_analysis)
            else:
                print(f"[TestPermitRouter] Cached analysis is older than 24 hours - running new Enhanced AutoGen analysis")
        
        # Update permit status
        permit.status = "analyzing"
        db.commit()
        
        try:
            # Initialize vector service for searches
            vector_service = VectorService()
            
            # Search relevant documents with robust error handling
            search_query = f"{permit.title} {permit.description} {permit.work_type or ''}"
            relevant_docs = []  # Default to empty
            
            # Always try to search documents for comprehensive analysis
            try:
                relevant_docs = await vector_service.hybrid_search(
                    query=search_query,
                    filters={
                        "tenant_id": 1,  # Fixed for testing
                        "industry_sectors": [permit.work_type] if permit.work_type else [],
                        "document_type": ["normativa", "istruzione_operativa", "procedura_sicurezza", 
                                         "procedura", "standard", "guideline", "manuale"]
                    },
                    limit=20
                )
                
                # Enrich search results with keywords from PostgreSQL
                from app.services.document_service import DocumentService
                doc_service = DocumentService(db)
                relevant_docs = doc_service.enrich_search_results_with_keywords(
                    relevant_docs, 
                    1  # Fixed tenant_id for testing
                )
                
                print(f"[TestPermitRouter] Found {len(relevant_docs)} relevant documents for permit {permit_id}")
            except Exception as e:
                print(f"[TestPermitRouter] Warning: Document search failed: {e}")
                relevant_docs = []
            
            # Prepare permit metadata from PostgreSQL
            permit_metadata = {
                "id": permit.id,
                "status": permit.status,
                "created_at": permit.created_at.isoformat() if permit.created_at else None,
                "location_details": permit.location,
                "equipment_list": permit.custom_fields.get("equipment", "").split(",") if permit.custom_fields.get("equipment") else [],
                "custom_fields": permit.custom_fields or {},
                "identified_risks": permit.custom_fields.get("identified_risks", []),
                "control_measures": permit.custom_fields.get("control_measures", []),
                "required_ppe": permit.dpi_required or []
            }
            
            # Get historical data if available
            try:
                # Get similar permits
                similar_permits = db.query(WorkPermit).filter(
                    WorkPermit.tenant_id == 1,  # Fixed for testing
                    WorkPermit.work_type == permit.work_type,
                    WorkPermit.id != permit.id
                ).limit(5).all()
                
                permit_metadata["previous_permits"] = [
                    {"id": p.id, "title": p.title, "status": p.status}
                    for p in similar_permits
                ]
                
                # Get site-specific risks
                if permit.location:
                    permit_metadata["site_specific_risks"] = [
                        f"Rischio specifico per {permit.location}"
                    ]
            except Exception as e:
                print(f"[TestPermitRouter] Warning: Could not fetch historical data: {e}")
            
            # Use Enhanced AutoGen - ONLY orchestrator available
            user_context = {
                "tenant_id": 1,  # Fixed for testing
                "user_id": 1,   # Fixed for testing
                "department": "test"
            }
            
            print(f"[TestPermitRouter] Using Enhanced AutoGen 5-Phase Analysis - permit {permit_id}")
            print(f"[TestPermitRouter] Force reanalysis: {analysis_request.force_reanalysis}")
            print(f"[TestPermitRouter] Found {len(relevant_docs)} documents for context")
            
            # Initialize Enhanced AutoGen Orchestrator
            orchestrator = SimpleAutoGenHSEAgents(user_context)
            
            # Clean and validate documents before passing to Enhanced AutoGen
            safe_docs = []
            for doc in relevant_docs:
                try:
                    # Only include essential fields to avoid serialization issues
                    safe_doc = {
                        "title": str(doc.get("title", "N/A")),
                        "content": str(doc.get("content", ""))[:500],  # Limit content size
                        "document_type": str(doc.get("document_type", "unknown"))
                    }
                    safe_docs.append(safe_doc)
                except Exception as doc_error:
                    print(f"[TestPermitRouter] Skipping malformed document: {doc_error}")
                    continue
            
            print(f"[TestPermitRouter] Using {len(safe_docs)} validated documents")
            print(f"[TestPermitRouter] Enhanced AutoGen will analyze without documents for maximum reliability")
            
            # Create clean permit data for Enhanced AutoGen
            clean_permit_data = {
                "id": permit.id,
                "title": permit.title,
                "description": permit.description,
                "work_type": permit.work_type,
                "location": permit.location,
                "duration_hours": permit.duration_hours,
                "dpi_required": permit.dpi_required or [],
                "risk_mitigation_actions": permit.risk_mitigation_actions or []
            }
            
            # Execute Enhanced AutoGen 5-Phase Analysis
            analysis_result = await orchestrator.analyze_permit(
                permit_data=clean_permit_data,
                context_documents=[]
            )
            
            # Ensure analysis_result has required fields
            if not analysis_result.get("analysis_complete"):
                raise Exception("Analysis failed to complete")
            
            # Update permit with results
            permit.ai_analysis = analysis_result
            permit.ai_confidence = analysis_result.get("confidence_score", 0.0)
            permit.analyzed_at = datetime.utcnow()
            permit.status = "analyzed"
            
            # Store individual analysis components if available
            if "executive_summary" in analysis_result:
                permit.content_analysis = {"executive_summary": analysis_result["executive_summary"]}
            if "action_items" in analysis_result:
                permit.action_items = analysis_result["action_items"]
            
            db.commit()
            
            print(f"[TestPermitRouter] Analysis completed for permit {permit_id}")
            return PermitAnalysisResponse(**analysis_result)
            
        except Exception as analysis_error:
            # Rollback permit status on error
            permit.status = "draft"
            db.rollback()
            
            logger.error(f"Analysis failed for permit {permit_id}: {str(analysis_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {str(analysis_error)}"
            )
    
    except Exception as e:
        # Handle any other errors
        logger.error(f"Unexpected error in permit analysis: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@router.post("/permits/analyze-preview", response_model=PermitAnalysisResponse)
async def test_analyze_permit_preview(
    analysis_request: PermitPreviewAnalysisRequest,
    request: Request
):
    """
    TEST: Anteprima analisi permesso SENZA AUTENTICAZIONE
    """
    try:
        # Mock user context for testing
        user_context = {
            "tenant_id": 1,
            "user_id": 1,
            "department": "test"
        }
        
        # Convert preview request to permit data format
        permit_data = {
            "id": "preview",
            "title": analysis_request.title,
            "description": analysis_request.description,
            "work_type": analysis_request.work_type,
            "location": analysis_request.location,
            "risk_level": analysis_request.risk_level,
            "risk_mitigation_actions": analysis_request.risk_mitigation_actions or []
        }
        
        print(f"[TestPermitRouter] Running Enhanced AutoGen 5-Phase Analysis for preview")
        
        # Use Enhanced AutoGen - ONLY orchestrator available
        orchestrator = SimpleAutoGenHSEAgents(user_context)
        analysis_result = await orchestrator.analyze_permit(
            permit_data=permit_data,
            context_documents=[]
        )
        
        return PermitAnalysisResponse(**analysis_result)
        
    except Exception as e:
        logger.error(f"Preview analysis failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview analysis failed: {str(e)}"
        )


@router.get("/permits", response_model=List[WorkPermitResponse])
async def test_list_permits(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List permits - TEST MODE (no auth)"""
    permits = db.query(WorkPermit).filter(
        WorkPermit.tenant_id == 1  # Fixed for testing
    ).offset(skip).limit(limit).all()
    
    return permits
from typing import List, Optional
from datetime import datetime, timedelta
import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.work_permit import WorkPermit
from app.models.user import User
from app.schemas.work_permit import (
    WorkPermitCreate, WorkPermitUpdate, WorkPermitResponse, 
    PermitAnalysisResponse, PermitAnalysisRequest, PermitListResponse,
    PermitAnalysisStatusResponse, PermitPreviewAnalysisRequest
)
from app.services.auth_service import get_current_user
from app.services.autogen_orchestrator import AutoGenAIOrchestrator
from app.services.fast_ai_orchestrator import FastAIOrchestrator
from app.services.mock_orchestrator import MockOrchestrator
from app.services.vector_service import VectorService
from app.agents.advanced_orchestrator import AdvancedHSEOrchestrator
from app.core.permissions import require_permission
from app.core.tenant import enforce_tenant_isolation, tenant_context
from app.core.tenant_queries import get_tenant_query_manager, tenant_required
from app.core.audit import AuditService, get_client_ip, get_user_agent
from fastapi import Request


router = APIRouter(prefix="/api/v1/permits", tags=["Work Permits"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=WorkPermitResponse)
@require_permission("own.permits.create")
@tenant_required
async def create_work_permit(
    permit_data: WorkPermitCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo permesso di lavoro
    """
    # Get tenant-aware query manager
    query_manager = get_tenant_query_manager(db)
    
    # Create work permit with automatic tenant assignment
    permit_dict = permit_data.dict()
    
    # Remove status if it's an invalid placeholder value
    if 'status' in permit_dict and permit_dict['status'] in ['string', '', None]:
        permit_dict.pop('status', None)
    
    work_permit = query_manager.create(
        WorkPermit,
        **permit_dict,
        created_by=current_user.id,
        status="completed"  # Permesso definitivo quando salvato
    )
    
    db.commit()
    db.refresh(work_permit)
    
    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_action(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="permit.created",
        resource_type="work_permit",
        resource_id=work_permit.id,
        resource_name=work_permit.title,
        new_values=permit_data.dict(),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        api_endpoint=request.url.path
    )
    
    return work_permit


@router.get("/", response_model=PermitListResponse)
@require_permission("tenant.permits.read")
async def list_work_permits(
    page: int = Query(1, ge=1, description="Numero pagina"),
    page_size: int = Query(20, ge=1, le=100, description="Elementi per pagina"),
    status: Optional[str] = Query(None, description="Filtra per status"),
    work_type: Optional[str] = Query(None, description="Filtra per tipo lavoro"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista permessi di lavoro con paginazione e filtri
    """
    # Base query with tenant isolation
    query = db.query(WorkPermit).filter(WorkPermit.tenant_id == current_user.tenant_id)
    
    # Apply user-level filtering based on permissions
    if current_user.role not in ["super_admin", "admin"]:
        if current_user.role == "manager":
            # Manager sees department + own permits
            query = query.filter(
                (WorkPermit.created_by == current_user.id) |
                (WorkPermit.custom_fields.op('->>')('department') == current_user.department)
            )
        else:
            # Operator/viewer sees only own permits
            query = query.filter(WorkPermit.created_by == current_user.id)
    
    # Apply filters
    if status:
        query = query.filter(WorkPermit.status == status)
    if work_type:
        query = query.filter(WorkPermit.work_type == work_type)
    
    # Get total count
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    permits = query.order_by(WorkPermit.created_at.desc()).offset(offset).limit(page_size).all()
    
    return PermitListResponse(
        permits=permits,
        total_count=total_count,
        page=page,
        page_size=page_size,
        has_next=offset + page_size < total_count,
        has_previous=page > 1
    )


@router.get("/{permit_id}", response_model=WorkPermitResponse)
@require_permission("own.permits.read")
async def get_work_permit(
    permit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottieni dettagli permesso di lavoro specifico
    """
    permit = db.query(WorkPermit).filter(
        WorkPermit.id == permit_id,
        WorkPermit.tenant_id == current_user.tenant_id
    ).first()
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work permit not found"
        )
    
    # Check user access to this permit
    if current_user.role not in ["super_admin", "admin"]:
        if current_user.role == "manager":
            # Manager can access department permits
            if (permit.created_by != current_user.id and 
                permit.custom_fields.get('department') != current_user.department):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this permit"
                )
        else:
            # Operator/viewer can only access own permits
            if permit.created_by != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this permit"
                )
    
    return permit


@router.put("/{permit_id}", response_model=WorkPermitResponse)
@require_permission("own.permits.update")
async def update_work_permit(
    permit_id: int,
    permit_update: WorkPermitUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Aggiorna permesso di lavoro
    """
    permit = db.query(WorkPermit).filter(
        WorkPermit.id == permit_id,
        WorkPermit.tenant_id == current_user.tenant_id
    ).first()
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work permit not found"
        )
    
    # Check permission to update
    if current_user.role not in ["super_admin", "admin"]:
        if permit.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only update your own permits"
            )
    
    # Store old values for audit
    old_values = {
        "title": permit.title,
        "description": permit.description,
        "status": permit.status,
        "dpi_required": permit.dpi_required,
        "work_type": permit.work_type,
        "location": permit.location
    }
    
    # Update permit
    update_data = permit_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(permit, field, value)
    
    db.commit()
    db.refresh(permit)
    
    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_action(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="permit.updated",
        resource_type="work_permit",
        resource_id=permit.id,
        resource_name=permit.title,
        old_values=old_values,
        new_values=update_data,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        api_endpoint=request.url.path
    )
    
    return permit


@router.post("/analyze-preview", response_model=PermitAnalysisResponse)
@require_permission("permits.analyze")
async def analyze_permit_preview(
    analysis_request: PermitPreviewAnalysisRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analisi di anteprima per bozza di permesso (senza salvarlo)
    """
    try:
        # Create a temporary WorkPermit object from the request data
        temp_permit_data = analysis_request.model_dump()
        
        logger.info(f"Received analysis request data: {temp_permit_data}")
        logger.info(f"Title: '{temp_permit_data.get('title')}'")
        logger.info(f"Description: '{temp_permit_data.get('description')}'")
        logger.info(f"Work type: '{temp_permit_data.get('work_type')}'")
        
        # Validate required fields
        if not all([
            temp_permit_data.get('title'),
            temp_permit_data.get('description'), 
            temp_permit_data.get('work_type')
        ]):
            logger.error("Validation failed - missing required fields")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title, description, and work_type are required for analysis"
            )
        
        # Initialize orchestrator based on request
        orchestrator_type = temp_permit_data.get('orchestrator', 'mock').lower()
        
        if orchestrator_type == 'modular':
            # Use modular orchestrator with real agents
            orchestrator = AutoGenAIOrchestrator(use_modular=True)
            logger.info("Using Modular orchestrator with real specialist agents")
        elif orchestrator_type == 'autogen':
            # Use standard AutoGen orchestrator
            orchestrator = AutoGenAIOrchestrator(use_modular=False)
            logger.info("Using AutoGen orchestrator")
        else:
            # Default to Mock for quick preview
            orchestrator = MockOrchestrator()
            logger.info("Using Mock orchestrator for instant preview")
        
        logger.info(f"Starting analysis for permit data: {temp_permit_data}")
        
        # Perform analysis on the draft permit data
        if orchestrator_type in ['modular', 'autogen']:
            # For real orchestrators, we need to provide more context
            vector_service = VectorService()
            
            # Search for relevant documents
            search_query = f"{temp_permit_data.get('title', '')} {temp_permit_data.get('description', '')} {temp_permit_data.get('work_type', '')}"
            
            try:
                relevant_docs = await vector_service.hybrid_search(
                    query=search_query,
                    filters={
                        "tenant_id": current_user.tenant_id,
                        "document_type": ["normativa", "istruzione_operativa", "procedura_sicurezza"]
                    },
                    limit=10
                )
                logger.info(f"Found {len(relevant_docs)} relevant documents for preview analysis")
            except Exception as e:
                logger.warning(f"Document search failed: {e}")
                relevant_docs = []
            
            # User context for agents
            user_context = {
                "tenant_id": current_user.tenant_id,
                "user_role": current_user.role,
                "department": getattr(current_user, 'department', 'safety')
            }
            
            # Run analysis with real orchestrator
            analysis_result = await orchestrator.run_multi_agent_analysis(
                permit_data=temp_permit_data,
                context_documents=relevant_docs,
                user_context=user_context,
                vector_service=vector_service
            )
        else:
            # Mock orchestrator for quick preview
            analysis_result = await orchestrator.analyze_permit_draft(
                permit_data=temp_permit_data,
                analysis_type=temp_permit_data.get('analysis_type', "comprehensive"),
                focus_areas=temp_permit_data.get('focus_areas', [])
            )
        
        logger.info(f"Analysis completed, result type: {type(analysis_result)}")
        
        # Ensure permit_id is present for preview (use 0 for drafts)
        if 'permit_id' not in analysis_result or analysis_result['permit_id'] is None:
            analysis_result['permit_id'] = 0  # Use 0 for draft/preview permits
        
        # Log preview analysis
        audit_service = AuditService(db)
        await audit_service.log_action(
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            action="permits.preview_analyzed",
            resource_type="permit_draft",
            resource_name=temp_permit_data.get('title', 'Draft Permit'),
            new_values={
                "analysis_type": temp_permit_data.get('analysis_type'),
                "work_type": temp_permit_data.get('work_type'),
                "risk_level": temp_permit_data.get('risk_level')
            },
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            api_endpoint=request.url.path,
            category="analysis"
        )
        
        logger.info("Creating response object")
        
        # The MockOrchestrator already returns a properly formatted response
        # We just need to convert the datetime string to datetime object
        analysis_result["timestamp"] = datetime.fromisoformat(analysis_result["timestamp"])
        
        # Create response using the analysis result
        response = PermitAnalysisResponse(**analysis_result)
        
        logger.info("Response created successfully")
        return response
        
    except Exception as e:
        import traceback
        logger.error(f"Error in preview analysis: {e}")
        logger.error(f"Exception type: {type(e)}")
        logger.error(f"Exception args: {e.args}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview analysis failed: {str(e)} - Type: {type(e).__name__}"
        )


@router.post("/{permit_id}/analyze", response_model=PermitAnalysisResponse)
@require_permission("permits.analyze")
async def analyze_permit_comprehensive(
    permit_id: int,
    analysis_request: PermitAnalysisRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    ENDPOINT PRINCIPALE: Analisi completa permesso con tutti gli agenti AI
    """
    # Load permit with tenant validation
    permit = db.query(WorkPermit).filter(
        WorkPermit.id == permit_id,
        WorkPermit.tenant_id == current_user.tenant_id
    ).first()
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work permit not found"
        )
    
    # Check if analysis already exists and is recent
    if (permit.ai_analysis and permit.analyzed_at and 
        not analysis_request.force_reanalysis):
        # Return existing analysis if less than 24 hours old
        if datetime.utcnow() - permit.analyzed_at < timedelta(hours=24):
            return PermitAnalysisResponse(**permit.ai_analysis)
    
    # Update permit status
    permit.status = "analyzing"
    db.commit()
    
    try:
        # Initialize vector service for searches
        vector_service = VectorService()
        
        # Search relevant documents
        search_query = f"{permit.title} {permit.description} {permit.work_type or ''}"
        
        try:
            relevant_docs = await vector_service.hybrid_search(
                query=search_query,
                filters={
                    "tenant_id": current_user.tenant_id,
                    "industry_sectors": [permit.work_type] if permit.work_type else [],
                    "document_type": ["normativa", "istruzione_operativa", "procedura_sicurezza", 
                                     "procedura", "standard", "guideline", "manuale"]
                },
                limit=20
            )
            print(f"[PermitRouter] Found {len(relevant_docs)} relevant documents for permit {permit_id}")
        except Exception as e:
            print(f"[PermitRouter] Warning: Document search failed: {e}")
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
                WorkPermit.tenant_id == current_user.tenant_id,
                WorkPermit.work_type == permit.work_type,
                WorkPermit.id != permit.id
            ).limit(5).all()
            
            permit_metadata["previous_permits"] = [
                {"id": p.id, "title": p.title, "status": p.status}
                for p in similar_permits
            ]
            
            # Get site-specific risks (from custom fields or dedicated table)
            if permit.location:
                permit_metadata["site_specific_risks"] = [
                    f"Rischio specifico per {permit.location}"
                ]
        except Exception as e:
            print(f"[PermitRouter] Warning: Could not fetch historical data: {e}")
        
        # Choose orchestrator based on request parameter
        user_context = {
            "tenant_id": current_user.tenant_id,
            "user_id": current_user.id,
            "department": current_user.department
        }
        
        if analysis_request.orchestrator == "advanced":
            # Use Advanced Orchestrator with PostgreSQL integration
            print(f"[PermitRouter] Using Advanced Orchestrator for analysis - permit {permit_id}")
            orchestrator = AdvancedHSEOrchestrator(
                user_context=user_context,
                vector_service=vector_service,
                db_session=db
            )
            analysis_result = await orchestrator.analyze_permit_advanced(
                permit_data=permit.to_dict(),
                permit_metadata=permit_metadata,
                context_documents=relevant_docs
            )
        elif analysis_request.orchestrator == "autogen":
            # Use AutoGen Orchestrator
            print(f"[PermitRouter] Using AutoGen Orchestrator for analysis - permit {permit_id}")
            orchestrator = AutoGenAIOrchestrator()
            analysis_result = await orchestrator.run_multi_agent_analysis(
                permit_data=permit.to_dict(),
                context_documents=relevant_docs,
                user_context=user_context,
                vector_service=vector_service
            )
        elif analysis_request.orchestrator == "fast":
            # Use Fast AI Orchestrator for quick single-call analysis
            print(f"[PermitRouter] Using Fast AI Orchestrator for quick analysis - permit {permit_id}")
            orchestrator = FastAIOrchestrator()
            analysis_result = await orchestrator.run_fast_analysis(
                permit_data=permit.to_dict(),
                context_documents=relevant_docs,
                user_context=user_context,
                vector_service=vector_service
            )
        else:  # mock
            # Use Mock Orchestrator for instant results
            print(f"[PermitRouter] Using Mock Orchestrator for instant analysis - permit {permit_id}")
            orchestrator = MockOrchestrator()
            analysis_result = await orchestrator.run_mock_analysis(
                permit_data=permit.to_dict(),
                context_documents=relevant_docs,
                user_context=user_context,
                vector_service=vector_service
            )
        
        # Save analysis results
        permit.ai_analysis = analysis_result
        permit.ai_confidence = analysis_result.get("confidence_score", 0.0)
        permit.ai_version = analysis_result.get("ai_version", "1.0")
        permit.analyzed_at = datetime.utcnow()
        permit.status = "reviewed"
        
        # Save structured results in individual fields
        permit.content_analysis = analysis_result.get("content_improvements", {})
        permit.risk_assessment = analysis_result.get("risk_assessment", {})
        permit.compliance_check = analysis_result.get("compliance_check", {})
        permit.dpi_recommendations = analysis_result.get("dpi_recommendations", {})
        permit.action_items = analysis_result.get("action_items", [])
        
        db.commit()
        
        # Audit log for AI analysis
        audit_service = AuditService(db)
        await audit_service.log_ai_analysis(
            user=current_user,
            permit_id=permit_id,
            analysis_results=analysis_result,
            confidence_score=analysis_result.get("confidence_score", 0.0),
            processing_time=analysis_result.get("processing_time", 0.0)
        )
        
        # Log regular action
        await audit_service.log_action(
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            action="permit.analyzed",
            resource_type="work_permit",
            resource_id=permit_id,
            resource_name=permit.title,
            extra_data={
                "ai_confidence": analysis_result.get("confidence_score"),
                "processing_time": analysis_result.get("processing_time"),
                "agents_used": analysis_result.get("agents_involved", [])
            },
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            api_endpoint=request.url.path,
            category="ai_analysis"
        )
        
        return PermitAnalysisResponse(**analysis_result)
        
    except Exception as e:
        # Update permit status on error
        permit.status = "draft"
        db.commit()
        
        # Log error
        audit_service = AuditService(db)
        await audit_service.log_action(
            user_id=current_user.id,
            tenant_id=current_user.tenant_id,
            action="permit.analysis_failed",
            resource_type="work_permit",
            resource_id=permit_id,
            extra_data={"error": str(e)},
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            severity="error",
            category="ai_analysis"
        )
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/{permit_id}/analysis-status", response_model=PermitAnalysisStatusResponse)
@require_permission("own.permits.read")
async def get_permit_analysis_status(
    permit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Ottieni lo status dell'analisi di un permesso
    """
    permit = db.query(WorkPermit).filter(
        WorkPermit.id == permit_id,
        WorkPermit.tenant_id == current_user.tenant_id
    ).first()
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work permit not found"
        )
    
    # Determine analysis status
    if permit.status == "analyzing":
        analysis_status = "analyzing"
    elif permit.ai_analysis and permit.analyzed_at:
        analysis_status = "completed"
    elif permit.ai_analysis is None:
        analysis_status = "not_analyzed"
    else:
        analysis_status = "failed"
    
    return PermitAnalysisStatusResponse(
        permit_id=permit_id,
        status=analysis_status,
        last_analysis_at=permit.analyzed_at,
        confidence_score=permit.ai_confidence,
        analysis_id=permit.ai_analysis.get("analysis_id") if permit.ai_analysis else None,
        error_message=permit.ai_analysis.get("error") if permit.ai_analysis and "error" in permit.ai_analysis else None
    )


@router.delete("/{permit_id}")
@require_permission("own.permits.delete")
async def delete_work_permit(
    permit_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Elimina permesso di lavoro
    """
    permit = db.query(WorkPermit).filter(
        WorkPermit.id == permit_id,
        WorkPermit.tenant_id == current_user.tenant_id
    ).first()
    
    if not permit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Work permit not found"
        )
    
    # Check permission to delete
    if current_user.role not in ["super_admin", "admin"]:
        if permit.created_by != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only delete your own permits"
            )
    
    # Store permit data for audit
    permit_data = {
        "title": permit.title,
        "status": permit.status,
        "work_type": permit.work_type
    }
    
    # Delete permit
    db.delete(permit)
    db.commit()
    
    # Audit log
    audit_service = AuditService(db)
    await audit_service.log_action(
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
        action="permit.deleted",
        resource_type="work_permit",
        resource_id=permit_id,
        resource_name=permit_data["title"],
        old_values=permit_data,
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        api_endpoint=request.url.path
    )
    
    return {"message": "Work permit deleted successfully"}
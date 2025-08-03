from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.work_permit import WorkPermit
from app.models.user import User
from app.schemas.work_permit import (
    WorkPermitCreate, WorkPermitUpdate, WorkPermitResponse, 
    PermitAnalysisResponse, PermitAnalysisRequest, PermitListResponse,
    PermitAnalysisStatusResponse
)
from app.services.auth_service import get_current_user
from app.services.ai_orchestrator import AIOrchestrator
from app.services.autogen_orchestrator import AutoGenAIOrchestrator
from app.services.vector_service import VectorService
from app.core.permissions import require_permission
from app.core.tenant import enforce_tenant_isolation
from app.core.audit import AuditService, get_client_ip, get_user_agent
from fastapi import Request


router = APIRouter(prefix="/api/v1/permits", tags=["Work Permits"])


@router.post("/", response_model=WorkPermitResponse)
@require_permission("own.permits.create")
async def create_work_permit(
    permit_data: WorkPermitCreate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Crea un nuovo permesso di lavoro
    """
    # Create work permit
    work_permit = WorkPermit(
        **permit_data.dict(),
        tenant_id=current_user.tenant_id,
        created_by=current_user.id,
        status="draft"
    )
    
    db.add(work_permit)
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
@require_permission("own.permits.read")
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
        # Search relevant documents
        # TEMPORARY: Skip Weaviate search for testing
        relevant_docs = []
        
        # vector_service = VectorService()
        # search_query = f"{permit.title} {permit.description} {permit.work_type or ''}"
        # 
        # relevant_docs = await vector_service.hybrid_search(
        #     query=search_query,
        #     filters={
        #         "tenant_id": current_user.tenant_id,
        #         "industry_sectors": [permit.work_type] if permit.work_type else [],
        #         "document_type": ["normativa", "istruzione_operativa"]
        #     },
        #     limit=20
        # )
        
        # Initialize vector service for dynamic searches
        vector_service = VectorService()
        
        # Run AutoGen multi-agent analysis with dynamic search capability
        orchestrator = AutoGenAIOrchestrator()
        analysis_result = await orchestrator.run_multi_agent_analysis(
            permit_data=permit.to_dict(),
            context_documents=relevant_docs,
            user_context={
                "tenant_id": current_user.tenant_id,
                "user_id": current_user.id,
                "department": current_user.department
            },
            vector_service=vector_service  # Enable dynamic document searches
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
from typing import List, Optional, Dict
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
    PermitAnalysisStatusResponse, PermitPreviewAnalysisRequest,
    ExecutiveSummary, ActionItem, Citation
)
from app.services.auth_service import get_current_user
from app.models.user import User
from app.services.fast_ai_orchestrator import FastAIOrchestrator
from app.services.vector_service import VectorService
from app.agents.advanced_orchestrator import AdvancedHSEOrchestrator
from app.core.permissions import require_permission

from app.core.tenant import enforce_tenant_isolation, tenant_context
from app.core.tenant_queries import get_tenant_query_manager, tenant_required
from app.core.audit import AuditService, get_client_ip, get_user_agent
from fastapi import Request
import json
import uuid


def convert_enhanced_result_to_response_format(enhanced_result: Dict, permit_id: int) -> Dict:
    """Convert enhanced orchestrator result to PermitAnalysisResponse format"""
    
    # Extract data from enhanced result
    metadata = enhanced_result.get("analysis_metadata", {})
    performance = metadata.get("performance", {})
    risk_analysis = enhanced_result.get("risk_analysis", {})
    action_consolidation = enhanced_result.get("action_consolidation", {})
    ppe_analysis = enhanced_result.get("ppe_analysis", {})
    final_output = enhanced_result.get("final_output", {})
    
    # Skip ExecutiveSummary creation - using simplified format
    
    # Create ActionItem objects
    action_items = []
    
    # First try to get action_items directly from enhanced result (new format)
    enhanced_action_items = enhanced_result.get("action_items", [])
    print(f"[DEBUG] Enhanced result keys: {list(enhanced_result.keys())}")
    print(f"[DEBUG] Enhanced action_items found: {len(enhanced_action_items)} items")
    print(f"[DEBUG] Enhanced result analysis_metadata: {enhanced_result.get('analysis_metadata', {})}")
    print(f"[DEBUG] Enhanced result final_output: {enhanced_result.get('final_output', {})}")
    if enhanced_action_items:
        print(f"[DEBUG] First action item: {enhanced_action_items[0] if enhanced_action_items else 'None'}")
    if enhanced_action_items:
        for i, action in enumerate(enhanced_action_items):
            # Enhanced format already has proper structure
            action_item = ActionItem(
                id=str(action.get("id", f"action_{i+1}")),
                type=action.get("type", "safety_action"),
                priority=action.get("priority", "medium"),
                suggested_action=action.get("suggested_action", action.get("title", "Azione di sicurezza")),
                references=action.get("references", []),
                frontend_display=action.get("frontend_display", {
                    "icon": "⚠️" if action.get("priority") == "high" else "📋",
                    "color": "red" if action.get("priority") == "high" else "blue",
                    "category": action.get("category", "safety")
                })
            )
            action_items.append(action_item)
    else:
        # Fallback to legacy format for compatibility
        for i, action in enumerate(final_output.get("actions", [])):
            action_item = ActionItem(
                id=f"action_{i+1}",
                type="safety_action",
                priority=action.get("priority", "medium"),
                suggested_action=action.get("suggested_action", action.get("action", action.get("title", "Azione di sicurezza"))),
                references=action.get("references", []),
                frontend_display={
                    "icon": "⚠️" if action.get("priority") == "high" else "📋",
                    "color": "red" if action.get("priority") == "high" else "blue",
                    "category": action.get("category", "safety")
                }
            )
            action_items.append(action_item)
    
    # Create Citations (simplified for now)
    citations = {
        "safety_documents": [
            Citation(
                document_info={
                    "title": "D.Lgs 81/08 - Testo Unico Sicurezza",
                    "type": "regulation",
                    "source": "Normativa italiana"
                },
                relevance={
                    "score": 0.9,
                    "context": "Sicurezza sul lavoro"
                },
                key_requirements=[
                    {"requirement": "Valutazione dei rischi", "compliance": "required"},
                    {"requirement": "Formazione lavoratori", "compliance": "required"}
                ],
                frontend_display={
                    "icon": "📋",
                    "color": "blue",
                    "category": "regulation"
                }
            )
        ]
    }
    
    # Build response - convert Pydantic objects to dicts for JSON serialization
    return {
        "analysis_id": str(uuid.uuid4()),
        "permit_id": permit_id,
        "processing_time": float(performance.get("total_processing_time", "0").replace("s", "")),
        "action_items": [item.dict() for item in action_items],
        "specialist_results": enhanced_result.get("specialist_results", []),
        "citations": {k: [citation.dict() for citation in v] for k, v in citations.items()},
        "performance_metrics": {
            "workflow_steps": metadata.get("workflow_steps", []),
            "specialists_involved": len(enhanced_result.get("specialist_analysis", {}).get("results_by_specialist", {})),
            "processing_time": performance.get("total_processing_time", "0s"),
            "analysis_timestamp": performance.get("analysis_timestamp", datetime.now().isoformat())
        },
        "timestamp": datetime.now().isoformat(),
        "agents_involved": list(enhanced_result.get("specialist_analysis", {}).get("results_by_specialist", {}).keys()) + ["DPI_Agent"],
        "ai_version": enhanced_result.get("ai_version", "Enhanced_Workflow_v2.0")
    }


router = APIRouter(
    prefix="/api/v1/permits", 
    tags=["Work Permits"],
)
logger = logging.getLogger(__name__)


def serialize_for_audit(data: Dict) -> Dict:
    """
    Convert datetime objects to ISO strings for JSON serialization in audit logs
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        if isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, dict):
            result[key] = serialize_for_audit(value)
        elif isinstance(value, list):
            result[key] = [serialize_for_audit(item) if isinstance(item, dict) else 
                          item.isoformat() if isinstance(item, datetime) else item 
                          for item in value]
        else:
            result[key] = value
    return result


def _convert_implementation_roadmap_to_schema_format(roadmap: Dict) -> Dict[str, List[str]]:
    """Convert complex implementation roadmap to simple Dict[str, List[str]] format for Pydantic"""
    if not roadmap:
        return {}
    
    result = {}
    
    for phase_key, phase_data in roadmap.items():
        if isinstance(phase_data, dict):
            # Convert phase data to list of strings
            phase_items = []
            if "timeline" in phase_data:
                phase_items.append(f"Timeline: {phase_data['timeline']}")
            if "focus" in phase_data:
                phase_items.append(f"Focus: {phase_data['focus']}")
            if "deliverables" in phase_data and isinstance(phase_data["deliverables"], list):
                phase_items.extend([f"• {item}" for item in phase_data["deliverables"]])
            
            result[phase_key] = phase_items
        elif isinstance(phase_data, str):
            # Simple string value
            result[phase_key] = [phase_data]
        elif isinstance(phase_data, list):
            # Already a list
            result[phase_key] = [str(item) for item in phase_data]
    
    return result



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
        new_values=serialize_for_audit(permit_data.dict()),
        ip_address=get_client_ip(request),
        user_agent=get_user_agent(request),
        api_endpoint=request.url.path
    )
    
    return work_permit


@router.get("/", response_model=PermitListResponse)
@require_permission("tenant.permits.read")
@tenant_required
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
            # Manager sees own permits only (department filtering removed)
            query = query.filter(WorkPermit.created_by == current_user.id)
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
            # Manager can only access own permits (department access removed)
            if permit.created_by != current_user.id:
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
        new_values=serialize_for_audit(update_data),
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
        orchestrator_type = temp_permit_data.get('orchestrator', 'fast').lower()
        
        if orchestrator_type == 'advanced':
            # Use Advanced orchestrator with 3-step process
            orchestrator = AdvancedHSEOrchestrator(
                user_context={
                    "tenant_id": current_user.tenant_id,
                    "user_role": current_user.role,
                    "department": getattr(current_user, 'department', 'safety')
                },
                vector_service=VectorService(),
                db_session=db
            )
            logger.info("Using Advanced orchestrator with 3-step specialist process")
        else:
            # Default to Fast for quick preview
            orchestrator = FastAIOrchestrator()
            logger.info("Using Fast orchestrator for instant preview")
        
        logger.info(f"Starting analysis for permit data: {temp_permit_data}")
        
        # Perform analysis on the draft permit data
        if orchestrator_type == 'advanced':
            # Search for relevant documents
            search_query = f"{temp_permit_data.get('title', '')} {temp_permit_data.get('description', '')} {temp_permit_data.get('work_type', '')}"
            
            try:
                vector_service = VectorService()
                relevant_docs = await vector_service.hybrid_search(
                    query=search_query,
                    filters={
                        "tenant_id": current_user.tenant_id,
                        "document_type": ["normativa", "istruzione_operativa", "procedura_sicurezza"]
                    },
                    limit=10
                )
                
                # Enrich search results with keywords from PostgreSQL
                from app.services.document_service import DocumentService
                doc_service = DocumentService(db)
                relevant_docs = doc_service.enrich_search_results_with_keywords(
                    relevant_docs, 
                    current_user.tenant_id
                )
                
                logger.info(f"Found {len(relevant_docs)} relevant documents for preview analysis")
            except Exception as e:
                logger.warning(f"Document search failed: {e}")
                relevant_docs = []
            
            # Run analysis with advanced orchestrator
            analysis_result = await orchestrator.analyze_permit_advanced(
                permit_data=temp_permit_data,
                permit_metadata={
                    "identified_risks": temp_permit_data.get("identified_risks", []),
                    "control_measures": temp_permit_data.get("control_measures", []),
                    "required_ppe": temp_permit_data.get("dpi_required", [])
                },
                context_documents=relevant_docs
            )
        else:
            # Fast orchestrator for quick preview
            analysis_result = await orchestrator.run_fast_analysis(
                permit_data=temp_permit_data,
                context_documents=[],
                user_context={
                    "tenant_id": current_user.tenant_id,
                    "user_role": current_user.role,
                    "department": getattr(current_user, 'department', 'safety')
                },
                vector_service=None
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
@tenant_required
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
    
    # Update permit status with transaction handling
    try:
        permit.status = "analyzing"
        db.commit()
    except Exception as e:
        logger.error(f"Error updating permit status to analyzing: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update permit status for analysis"
        )
    
    try:
        # Initialize vector service for searches
        vector_service = VectorService()
        
        # Search relevant documents - try PostgreSQL first, fallback to vector search
        search_query = f"{permit.title} {permit.description} {permit.work_type or ''}"
        relevant_docs = []
        
        # HYBRID SEARCH STRATEGY: Use both PostgreSQL and Weaviate for comprehensive results
        print(f"[PermitRouter] *** CITATION DEBUG *** STARTING hybrid document search for permit {permit_id}, work_type='{permit.work_type}'")
        
        postgres_docs = []
        weaviate_docs = []
        
        # STEP 1: PostgreSQL structured search with separate session
        try:
            from app.models.document import Document
            from app.config.database import SessionLocal
            print(f"[PermitRouter] Searching PostgreSQL for documents...")
            
            # Use separate session for document search to avoid transaction conflicts
            search_db = SessionLocal()
            try:
                # DEBUG: Check total documents and tenant filtering
                total_docs = search_db.query(Document).count()
                tenant_docs = search_db.query(Document).filter(Document.tenant_id == current_user.tenant_id).count()
                print(f"[PermitRouter] DEBUG: Total docs={total_docs}, tenant_docs={tenant_docs}, user_tenant_id={current_user.tenant_id}")
                
                # SIMPLIFIED SEARCH: Get all tenant documents for now (to ensure we get documents)
                # This ensures we have documents to cite while avoiding complex query issues
                postgres_results = search_db.query(Document).filter(
                    Document.tenant_id == current_user.tenant_id
                ).limit(5).all()  # Get first 5 documents from tenant
                
                print(f"[PermitRouter] SIMPLIFIED: Found {len(postgres_results)} tenant documents")
            finally:
                search_db.close()
            
            # Convert to expected format
            for doc in postgres_results:
                postgres_docs.append({
                    "id": doc.id,
                    "title": doc.title,
                    "document_type": doc.document_type,
                    "document_code": doc.document_code,
                    "keywords": doc.keywords or [],
                    "content_summary": doc.content_summary or "",
                    "industry_sectors": doc.industry_sectors or [],
                    "search_score": 0.9,  # High score for direct matches
                    "source": "PostgreSQL"
                })
            
            print(f"[PermitRouter] PostgreSQL found {len(postgres_docs)} documents")
            # DEBUG: Show PostgreSQL documents found
            for i, doc in enumerate(postgres_docs):
                title = doc.get("title", "No title")
                doc_type = doc.get("document_type", "Unknown type")
                doc_code = doc.get("document_code", "No code")
                print(f"[PermitRouter] PG Doc {i+1}: {title} ({doc_type}) - Code: {doc_code}")
            
            
        except Exception as e:
            print(f"[PermitRouter] PostgreSQL document search failed: {e}")
        
        # STEP 2: Weaviate semantic search (ALWAYS executed)
        try:
            print(f"[PermitRouter] Searching Weaviate for semantic matches...")
            print(f"[PermitRouter] DEBUG: Weaviate search query='{search_query}', tenant_id={current_user.tenant_id}")
            weaviate_results = await vector_service.hybrid_search(
                query=search_query,
                filters={
                    "tenant_id": current_user.tenant_id,
                    # Remove industry_sectors filter to be less restrictive
                    "document_type": ["normativa", "istruzione_operativa", "procedura_sicurezza", 
                                     "procedura", "standard", "guideline", "manuale"]
                },
                limit=12,  # Get more from Weaviate for semantic richness
                threshold=0.0  # Lower threshold to get more results
            )
            
            # Enrich search results with keywords from PostgreSQL
            from app.services.document_service import DocumentService
            doc_service = DocumentService(db)
            weaviate_docs = doc_service.enrich_search_results_with_keywords(
                weaviate_results, 
                current_user.tenant_id
            )
            
            # Mark as Weaviate source
            for doc in weaviate_docs:
                doc["source"] = "Weaviate"
            
            print(f"[PermitRouter] Weaviate found {len(weaviate_docs)} documents")
            
        except Exception as e:
            print(f"[PermitRouter] Weaviate search failed: {e}")
            print(f"[PermitRouter] Continuing with PostgreSQL results only (tenant isolation maintained)")
        
        # STEP 3: Add historical permits (lowest priority) with separate session
        historical_permits = []
        try:
            # Use separate session for historical permit search
            historical_db = SessionLocal()
            try:
                # Get similar historical permits for context
                historical_results = historical_db.query(WorkPermit).filter(
                    WorkPermit.tenant_id == current_user.tenant_id,
                    WorkPermit.work_type == permit.work_type,
                    WorkPermit.id != permit_id,
                    WorkPermit.status.in_(['completed', 'approved'])  # Only successful permits
                ).limit(5).all()
            finally:
                historical_db.close()
            
            for hist_permit in historical_results:
                historical_permits.append({
                    "id": hist_permit.id,
                    "title": f"Permesso storico: {hist_permit.title}",
                    "document_type": "historical_permit", 
                    "document_code": f"PERMIT-{hist_permit.id}",
                    "content_summary": f"Permesso {hist_permit.work_type}: {hist_permit.description[:100]}",
                    "search_score": 0.3,  # Low priority
                    "source": "Historical",
                    "permit_status": hist_permit.status,
                    "analyzed_at": hist_permit.analyzed_at.isoformat() if hist_permit.analyzed_at else None
                })
                
            print(f"[PermitRouter] Found {len(historical_permits)} historical permits")
            
        except Exception as e:
            print(f"[PermitRouter] Error fetching historical permits: {e}")
        
        # STEP 4: Consolidate all results with priorities  
        print(f"[PermitRouter] BEFORE consolidation: PostgreSQL={len(postgres_docs)}, Weaviate={len(weaviate_docs)}, Historical={len(historical_permits)}")
        relevant_docs = consolidate_search_results(postgres_docs, weaviate_docs, historical_permits)
        print(f"[PermitRouter] AFTER consolidation: {len(relevant_docs)} unique documents from all sources")
        
        # DEBUG: Show what types of documents made it through consolidation
        for i, doc in enumerate(relevant_docs):
            doc_title = doc.get("title", "No title")
            doc_source = doc.get("source", "Unknown source")
            doc_type = doc.get("document_type", "Unknown type")
            print(f"[PermitRouter] Doc {i+1}: {doc_title} (source: {doc_source}, type: {doc_type})")
        
        
        # Prepare permit metadata from PostgreSQL
        permit_metadata = {
            "id": permit.id,
            "status": permit.status,
            "created_at": permit.created_at.isoformat() if permit.created_at else None,
            "location_details": permit.location,
            "equipment_list": [],
            "identified_risks": [],
            "control_measures": [],
            "required_ppe": permit.dpi_required or []
        }
        
        # Get historical data if available with separate session
        try:
            # Use separate session for similar permits search
            similar_db = SessionLocal()
            try:
                # Get similar permits
                similar_permits = similar_db.query(WorkPermit).filter(
                    WorkPermit.tenant_id == current_user.tenant_id,
                    WorkPermit.work_type == permit.work_type,
                    WorkPermit.id != permit.id
                ).limit(5).all()
            finally:
                similar_db.close()
            
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
            "department": getattr(current_user, 'department', 'safety')
        }
        
        # Debug: Log which orchestrator is being used
        logger.info(f"[PermitRouter] Orchestrator requested: {analysis_request.orchestrator}")
        print(f"[PermitRouter] DEBUG: Orchestrator type = '{analysis_request.orchestrator}'")
        
        if analysis_request.orchestrator == "advanced":
            # Use Advanced Orchestrator with 3-step process
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
        else:
            # Default to fast analysis if invalid orchestrator type
            print(f"[PermitRouter] Invalid orchestrator '{analysis_request.orchestrator}', defaulting to fast analysis")
            orchestrator = FastAIOrchestrator()
            analysis_result = await orchestrator.run_fast_analysis(
                permit_data=permit.to_dict(),
                context_documents=relevant_docs,
                user_context=user_context,
                vector_service=vector_service
            )
        
        # Debug: Log analysis result keys
        logger.info(f"[PermitRouter] Analysis result keys: {list(analysis_result.keys())}")
        print(f"[PermitRouter] DEBUG: Required fields check - citations: {'citations' in analysis_result}, ai_version: {'ai_version' in analysis_result}")
        
        # Convert enhanced result to PermitAnalysisResponse format
        if analysis_request.orchestrator == "advanced":
            analysis_result = convert_enhanced_result_to_response_format(analysis_result, permit_id)
        
        # Save analysis results with fresh database session to avoid transaction conflicts
        from app.config.database import SessionLocal
        fresh_db = SessionLocal()
        try:
            # Get fresh permit instance from new session
            fresh_permit = fresh_db.query(WorkPermit).filter(
                WorkPermit.id == permit_id,
                WorkPermit.tenant_id == current_user.tenant_id
            ).first()
            
            if not fresh_permit:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Work permit not found"
                )
            
            # Update with analysis results
            fresh_permit.ai_analysis = analysis_result
            fresh_permit.ai_version = analysis_result.get("ai_version", "1.0")
            fresh_permit.analyzed_at = datetime.utcnow()
            fresh_permit.status = "reviewed"
            
            # Save structured results in individual fields
            fresh_permit.action_items = analysis_result.get("action_items", [])
            
            fresh_db.commit()
            
            # Update the original permit object for consistency
            permit.ai_analysis = analysis_result
            permit.status = "reviewed"
            
        except Exception as e:
            logger.error(f"Error saving analysis results: {e}")
            fresh_db.rollback()
            raise e
        finally:
            fresh_db.close()
        
        # Audit log for AI analysis with fresh session
        fresh_audit_db = SessionLocal()
        try:
            audit_service = AuditService(fresh_audit_db)
            await audit_service.log_ai_analysis(
                user=current_user,
                permit_id=permit_id,
                analysis_results=analysis_result,
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
                    "processing_time": analysis_result.get("processing_time"),
                    "agents_used": analysis_result.get("agents_involved", [])
                },
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                api_endpoint=request.url.path,
                category="ai_analysis"
            )
            fresh_audit_db.commit()
        except Exception as audit_error:
            logger.error(f"Error logging audit information: {audit_error}")
            fresh_audit_db.rollback()
        finally:
            fresh_audit_db.close()
        
        # Convert dict data back to Pydantic objects for the response if it was processed by advanced orchestrator
        if analysis_request.orchestrator == "advanced":
            # Reconstruct Pydantic objects from dict data for action_items only
            analysis_result_copy = analysis_result.copy()
            analysis_result_copy["action_items"] = [ActionItem(**item) for item in analysis_result.get("action_items", [])]
            analysis_result_copy["citations"] = {
                k: [Citation(**citation) for citation in v] 
                for k, v in analysis_result.get("citations", {}).items()
            }
            # Convert timestamp string back to datetime object for Pydantic
            if isinstance(analysis_result_copy["timestamp"], str):
                analysis_result_copy["timestamp"] = datetime.fromisoformat(analysis_result_copy["timestamp"])
            return PermitAnalysisResponse(**analysis_result_copy)
        else:
            return PermitAnalysisResponse(**analysis_result)
        
    except Exception as e:
        # Update permit status on error with proper transaction handling
        try:
            permit.status = "draft"
            db.commit()
        except Exception as commit_error:
            logger.error(f"Error updating permit status after failure: {commit_error}")
            db.rollback()
        
        # Log error
        try:
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
        except Exception as audit_error:
            logger.error(f"Error logging audit action: {audit_error}")
        
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


def consolidate_search_results(postgres_docs: List[Dict], weaviate_docs: List[Dict], historical_permits: List[Dict] = None) -> List[Dict]:
    """
    Consolidate and deduplicate search results from PostgreSQL, Weaviate, and Historical permits
    Priority: 1) PostgreSQL (metadata accuracy), 2) Weaviate (semantic relevance), 3) Historical (context, lowest priority)
    """
    consolidated = []
    seen_documents = set()  # Track by document_code to avoid duplicates
    historical_permits = historical_permits or []
    
    # First add PostgreSQL results (structured metadata, high accuracy)
    for doc in postgres_docs:
        doc_key = doc.get("document_code", doc.get("title", ""))
        if doc_key and doc_key not in seen_documents:
            consolidated.append(doc)
            seen_documents.add(doc_key)
    
    # Then add Weaviate results that don't duplicate PostgreSQL
    for doc in weaviate_docs:
        doc_key = doc.get("document_code", doc.get("title", ""))
        if doc_key and doc_key not in seen_documents:
            # Weaviate has semantic relevance, preserve search_score
            consolidated.append(doc)
            seen_documents.add(doc_key)
    
    # Finally add historical permits (lowest priority, for context)
    for doc in historical_permits:
        doc_key = doc.get("document_code", doc.get("title", ""))
        if doc_key and doc_key not in seen_documents:
            consolidated.append(doc)
            seen_documents.add(doc_key)
    
    # Sort by relevance with priorities:
    # 1. PostgreSQL (score 0.9) - highest priority
    # 2. Weaviate (variable score) - semantic relevance
    # 3. Historical (score 0.3) - context only, lowest priority
    consolidated.sort(key=lambda x: (
        -x.get("search_score", 0),  # Higher scores first
        x.get("source", "") == "PostgreSQL",  # PostgreSQL gets priority
        x.get("source", "") == "Weaviate"     # Then Weaviate over Historical
    ), reverse=True)
    
    # Limit total results (more room for documents, fewer for historical)
    total_limit = 18
    historical_limit = 3  # Max 3 historical permits
    
    # Count historical permits in results
    historical_count = len([d for d in consolidated if d.get("source") == "Historical"])
    if historical_count > historical_limit:
        # Keep only first historical_limit historical permits
        non_historical = [d for d in consolidated if d.get("source") != "Historical"]
        historical_only = [d for d in consolidated if d.get("source") == "Historical"][:historical_limit]
        consolidated = non_historical + historical_only
    
    return consolidated[:total_limit]



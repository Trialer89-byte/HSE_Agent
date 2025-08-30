from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class WorkPermitBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255, description="Titolo del permesso di lavoro")
    description: str = Field(..., min_length=10, description="Descrizione dettagliata del lavoro")
    dpi_required: List[str] = Field(default=[], description="DPI richiesti")
    work_type: Optional[str] = Field(None, description="Tipo di lavoro")
    location: Optional[str] = Field(None, description="Ubicazione del lavoro")
    duration_hours: Optional[int] = Field(None, ge=1, le=168, description="Durata in ore")
    priority_level: str = Field(default="medium", description="Livello di priorità")
    risk_mitigation_actions: List[str] = Field(default=[], description="Azioni di mitigazione dei rischi")
    custom_fields: Dict[str, Any] = Field(default={}, description="Campi personalizzati")
    tags: List[str] = Field(default=[], description="Tag di categorizzazione")

    @validator('priority_level')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'medium', 'high', 'critical']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {allowed_priorities}')
        return v

    @validator('work_type')
    def validate_work_type(cls, v):
        if v is not None:
            allowed_types = ['chimico', 'scavo', 'manutenzione', 'elettrico', 'meccanico', 'edile', 'pulizia', 'altro']
            if v not in allowed_types:
                raise ValueError(f'Work type must be one of: {allowed_types}')
        return v


class WorkPermitCreate(WorkPermitBase):
    pass


class WorkPermitUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    dpi_required: Optional[List[str]] = None
    work_type: Optional[str] = None
    location: Optional[str] = None
    duration_hours: Optional[int] = Field(None, ge=1, le=168)
    priority_level: Optional[str] = None
    risk_mitigation_actions: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['draft', 'analyzing', 'reviewed', 'approved', 'rejected', 'completed']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {allowed_statuses}')
        return v


class WorkPermitResponse(WorkPermitBase):
    id: int
    tenant_id: int
    status: str
    ai_confidence: float
    ai_version: Optional[str]
    created_by: int
    approved_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    analyzed_at: Optional[datetime]
    
    # AI Analysis Results
    ai_analysis: Optional[Dict[str, Any]] = None
    content_analysis: Optional[Dict[str, Any]] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    compliance_check: Optional[Dict[str, Any]] = None
    dpi_recommendations: Optional[Dict[str, Any]] = None
    action_items: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class ActionItem(BaseModel):
    id: str
    type: str = Field(..., description="Tipo di action item")
    priority: str = Field(..., description="Priorità: alta, media, bassa")
    title: str = Field(..., description="Titolo dell'azione")
    description: str = Field(..., description="Descrizione dettagliata")
    suggested_action: str = Field(..., description="Azione suggerita")
    consequences_if_ignored: Optional[str] = Field(None, description="Conseguenze se ignorato")
    references: List[str] = Field(default=[], description="Riferimenti normativi")
    estimated_effort: Optional[str] = Field(None, description="Sforzo stimato")
    responsible_role: Optional[str] = Field(None, description="Ruolo responsabile")
    frontend_display: Dict[str, str] = Field(..., description="Configurazione display frontend")


class Citation(BaseModel):
    document_info: Dict[str, str] = Field(..., description="Informazioni documento")
    relevance: Dict[str, Any] = Field(..., description="Rilevanza del documento")
    key_requirements: List[Dict[str, Any]] = Field(default=[], description="Requisiti chiave")
    frontend_display: Dict[str, str] = Field(..., description="Configurazione display")


class ExecutiveSummary(BaseModel):
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Score complessivo")
    critical_issues: int = Field(..., ge=0, description="Numero di problemi critici")
    recommendations: int = Field(..., ge=0, description="Numero di raccomandazioni")
    compliance_level: str = Field(..., description="Livello di conformità")
    estimated_completion_time: str = Field(..., description="Tempo stimato di completamento")
    key_findings: List[str] = Field(default=[], description="Scoperte principali")
    next_steps: List[str] = Field(default=[], description="Prossimi passi")


class PermitAnalysisResponse(BaseModel):
    analysis_id: str
    permit_id: int
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    processing_time: float
    
    # Structured results
    executive_summary: ExecutiveSummary
    action_items: List[ActionItem]
    citations: Dict[str, List[Citation]]
    completion_roadmap: Dict[str, List[str]]
    
    # Performance metrics
    performance_metrics: Dict[str, Any]
    
    # Metadata
    timestamp: datetime
    agents_involved: List[str]
    ai_version: str

    class Config:
        from_attributes = True


class PermitAnalysisRequest(BaseModel):
    force_reanalysis: bool = Field(default=False, description="Forza ri-analisi anche se già esistente")
    # Enhanced AutoGen è l'unico orchestratore disponibile - parametro rimosso


class PermitPreviewAnalysisRequest(BaseModel):
    # Work permit data (required for preview)
    title: str = Field(..., description="Titolo del permesso di lavoro")
    description: str = Field(..., description="Descrizione dettagliata del lavoro")
    work_type: str = Field(..., description="Tipo di lavoro")
    location: Optional[str] = Field(None, description="Ubicazione del lavoro")
    risk_level: Optional[str] = Field(None, description="Livello di rischio")
    risk_mitigation_actions: Optional[List[str]] = Field(default=[], description="Azioni di mitigazione dei rischi")
    
    # Analysis options (optional for preview)
    analysis_type: Optional[str] = Field(default="comprehensive", description="Tipo di analisi")
    focus_areas: Optional[List[str]] = Field(default=[], description="Aree di focus specifiche")
    # Enhanced AutoGen è l'unico orchestratore disponibile - parametro rimosso
    
    @validator('work_type')
    def validate_work_type(cls, v):
        allowed_types = ['chimico', 'scavo', 'manutenzione', 'elettrico', 'meccanico', 'edile', 'pulizia', 'altro']
        if v not in allowed_types:
            raise ValueError(f'Work type must be one of: {allowed_types}')
        return v


class PermitListResponse(BaseModel):
    permits: List[WorkPermitResponse]
    total_count: int
    page: int
    page_size: int
    has_next: bool
    has_previous: bool


class PermitAnalysisStatusResponse(BaseModel):
    permit_id: int
    status: str  # "not_analyzed", "analyzing", "completed", "failed"
    last_analysis_at: Optional[datetime]
    confidence_score: Optional[float]
    analysis_id: Optional[str]
    error_message: Optional[str]
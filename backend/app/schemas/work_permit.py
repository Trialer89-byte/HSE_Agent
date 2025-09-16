from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, validator
from datetime import datetime


class WorkPermitBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255, description="Titolo del permesso di lavoro", example="Manutenzione quadro elettrico principale")
    description: str = Field(..., min_length=10, description="Descrizione dettagliata del lavoro", example="Sostituzione interruttore MT e verifica isolamento circuito principale cabina elettrica")
    dpi_required: List[str] = Field(default=[], description="DPI richiesti", example=["Guanti isolanti Classe 2", "Elmetto dielettrico", "Calzature isolanti"])
    work_type: Optional[str] = Field(None, description="Tipo di lavoro", example="elettrico")
    location: Optional[str] = Field(None, description="Ubicazione del lavoro", example="Cabina elettrica MT - Stabilimento A")
    equipment: List[str] = Field(default=[], description="Attrezzature utilizzate", example=["Multimetro", "Pinze amperometriche", "Tester isolamento"])
    risk_level: str = Field(default="medium", description="Livello di rischio", example="high")
    start_date: Optional[datetime] = Field(None, description="Data di inizio lavoro")
    end_date: Optional[datetime] = Field(None, description="Data di fine lavoro")
    risk_mitigation_actions: List[str] = Field(default=[], description="Azioni di mitigazione dei rischi", example=["Procedura LOTO", "Verifica assenza tensione", "Coordinamento con sala controllo"])
    custom_fields: Optional[Dict[str, Any]] = Field(default={}, description="Campi personalizzati")

    @validator('equipment', pre=True)
    def validate_equipment(cls, v):
        if isinstance(v, str):
            # Handle string input by splitting on commas
            if v.strip():
                return [item.strip() for item in v.split(',') if item.strip()]
            else:
                return []
        elif isinstance(v, list):
            return v
        else:
            return []

    @validator('risk_mitigation_actions', pre=True)
    def validate_risk_mitigation_actions(cls, v):
        if isinstance(v, str):
            # Handle string input by splitting on commas
            if v.strip():
                return [item.strip() for item in v.split(',') if item.strip()]
            else:
                return []
        elif isinstance(v, list):
            return v
        else:
            return []

    @validator('risk_level')
    def validate_risk_level(cls, v):
        allowed_risk_levels = ['low', 'medium', 'high', 'critical']
        if v not in allowed_risk_levels:
            raise ValueError(f'Risk level must be one of: {allowed_risk_levels}')
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
    equipment: Optional[List[str]] = None
    risk_level: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    risk_mitigation_actions: Optional[List[str]] = None
    custom_fields: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None

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
    is_active: bool
    ai_version: Optional[str]
    created_by: int
    approved_by: Optional[int]
    created_at: datetime
    updated_at: datetime
    analyzed_at: Optional[datetime]
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]

    # Computed fields
    duration_hours: int = Field(0, description="Durata calcolata in ore (end_date - start_date)")

    # AI Analysis Results
    ai_analysis: Optional[Dict[str, Any]] = None
    action_items: Optional[List[Dict[str, Any]]] = None

    class Config:
        from_attributes = True


class ActionItem(BaseModel):
    id: str
    type: str = Field(..., description="Tipo di action item")
    priority: str = Field(..., description="Priorità: alta, media, bassa")
    suggested_action: str = Field(..., description="Azione suggerita")
    frontend_display: Dict[str, str] = Field(..., description="Configurazione display frontend")


class Citation(BaseModel):
    document_info: Dict[str, str] = Field(..., description="Informazioni documento")
    relevance: Dict[str, Any] = Field(..., description="Rilevanza del documento")
    key_requirements: List[Dict[str, Any]] = Field(default=[], description="Requisiti chiave")
    frontend_display: Dict[str, str] = Field(..., description="Configurazione display")


class ExecutiveSummary(BaseModel):
    critical_issues: int = Field(..., ge=0, description="Numero di problemi critici")
    recommendations: int = Field(..., ge=0, description="Numero di raccomandazioni")
    compliance_level: str = Field(..., description="Livello di conformità")
    key_findings: List[str] = Field(default=[], description="Scoperte principali")


class PermitAnalysisResponse(BaseModel):
    analysis_id: str
    permit_id: int
    processing_time: float
    
    # Structured results
    action_items: List[ActionItem]
    specialist_results: Optional[List[Dict[str, Any]]] = Field(default=[], description="Results from specialist agents")
    citations: Dict[str, List[Citation]]
    
    # Performance metrics
    performance_metrics: Dict[str, Any]
    
    # Metadata
    timestamp: datetime
    agents_involved: List[str]
    ai_version: str

    class Config:
        from_attributes = True


class PermitAnalysisRequest(BaseModel):
    force_reanalysis: bool = Field(default=False, description="Forza ri-analisi anche se già esistente", example=True)
    orchestrator: str = Field(default="advanced", description="Tipo di agente/orchestratore da utilizzare per l'analisi", example="advanced")
    
    @validator('orchestrator')
    def validate_orchestrator(cls, v):
        allowed_orchestrators = ['fast', 'autogen', 'advanced']  # Removed 'mock'
        if v not in allowed_orchestrators:
            raise ValueError(f'Orchestrator must be one of: {allowed_orchestrators}')
        return v


class PermitPreviewAnalysisRequest(BaseModel):
    # Work permit data (required for preview)
    title: str = Field(..., description="Titolo del permesso di lavoro", example="Manutenzione pompa centrifuga")
    description: str = Field(..., description="Descrizione dettagliata del lavoro", example="Sostituzione girante pompa P-001 e verifica tenute meccaniche")
    work_type: str = Field(..., description="Tipo di lavoro", example="meccanico")
    location: Optional[str] = Field(None, description="Ubicazione del lavoro", example="Sala pompe - Area produzione")
    equipment: Optional[List[str]] = Field(default=[], description="Attrezzature utilizzate", example=["Chiavi inglesi", "Estrattore cuscinetti", "Torsiometro"])
    risk_level: Optional[str] = Field(None, description="Livello di rischio", example="medio")
    risk_mitigation_actions: Optional[List[str]] = Field(default=[], description="Azioni di mitigazione dei rischi", example=["Isolamento energia", "Drenaggio linea", "Uso DPI specifici"])
    
    @validator('risk_mitigation_actions', pre=True)
    def validate_risk_mitigation_actions(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            # Handle string input by splitting on commas
            if v.strip():
                return [item.strip() for item in v.split(',') if item.strip()]
            else:
                return []
        elif isinstance(v, list):
            return v
        else:
            return []
    
    # Analysis options (optional for preview)
    analysis_type: Optional[str] = Field(default="comprehensive", description="Tipo di analisi", example="comprehensive")
    focus_areas: Optional[List[str]] = Field(default=[], description="Aree di focus specifiche", example=["rischi_meccanici", "procedure_loto", "dpi_requirements"])
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
    analysis_id: Optional[str]
    error_message: Optional[str]
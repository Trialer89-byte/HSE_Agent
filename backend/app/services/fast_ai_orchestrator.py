from typing import Dict, Any, List
import asyncio
import time
from datetime import datetime

from app.agents.content_analysis_agent import ContentAnalysisAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent


class FastAIOrchestrator:
    """
    Fast AI Orchestrator - simplified version to avoid blocking
    """
    
    def __init__(self):
        self.analysis_timeout = 60  # 60 second total timeout
        self.agent_timeout = 30     # 30 seconds per agent max
    
    async def run_fast_analysis(
        self,
        permit_data: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        vector_service=None
    ) -> Dict[str, Any]:
        """
        Run fast, simplified analysis to avoid blocking
        """
        start_time = time.time()
        print(f"[FastAIOrchestrator] Starting fast analysis for permit {permit_data.get('id')}")
        
        try:
            # Simple, direct analysis without complex multi-agent coordination
            analysis_result = await self._run_simple_analysis(
                permit_data, context_documents, user_context, vector_service
            )
            
            processing_time = time.time() - start_time
            analysis_result["processing_time"] = round(processing_time, 2)
            
            print(f"[FastAIOrchestrator] Fast analysis completed in {processing_time:.2f}s")
            return analysis_result
            
        except Exception as e:
            processing_time = time.time() - start_time
            print(f"[FastAIOrchestrator] Fast analysis failed after {processing_time:.2f}s: {str(e)}")
            return self._create_emergency_response(permit_data, processing_time, str(e))
    
    async def _run_simple_analysis(
        self,
        permit_data: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        vector_service
    ) -> Dict[str, Any]:
        """
        Run simplified analysis with just one agent to avoid complexity
        """
        # Use only content analysis agent for speed
        content_agent = ContentAnalysisAgent(user_context, vector_service)
        
        try:
            # Run single agent with timeout
            content_result = await asyncio.wait_for(
                content_agent.analyze(permit_data, context_documents),
                timeout=self.agent_timeout
            )
            
            # Create structured response based on single agent result
            return self._structure_fast_response(permit_data, content_result, user_context)
            
        except asyncio.TimeoutError:
            print(f"[FastAIOrchestrator] Content agent timed out after {self.agent_timeout}s")
            return self._create_simple_fallback_response(permit_data, user_context)
        except Exception as e:
            print(f"[FastAIOrchestrator] Content agent failed: {str(e)}")
            return self._create_simple_fallback_response(permit_data, user_context)
    
    def _structure_fast_response(
        self,
        permit_data: Dict[str, Any],
        content_result: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Structure response from single agent analysis
        """
        work_type = permit_data.get("work_type", "generale")
        title = permit_data.get("title", "Permesso di lavoro")
        
        # Extract insights from content analysis
        content_quality = content_result.get("content_quality", {})
        missing_fields = content_result.get("missing_fields", [])
        improvements = content_result.get("improvement_suggestions", [])
        
        # Generate basic risk assessment based on work type
        basic_risks = self._get_basic_risks_by_work_type(work_type)
        basic_dpi = self._get_basic_dpi_by_work_type(work_type)
        
        # Create action items from analysis
        action_items = []
        for i, improvement in enumerate(improvements[:5]):  # Max 5 items
            action_items.append({
                "id": f"action_{i+1}",
                "type": "improvement",
                "priority": "media",
                "title": improvement.get("suggested_improvement", f"Miglioramento {i+1}"),
                "description": improvement.get("rationale", "Miglioramento suggerito dall'analisi"),
                "suggested_action": improvement.get("suggested_improvement", "Applicare miglioramento"),
                "consequences_if_ignored": "Potenziale riduzione della sicurezza",
                "references": [],
                "estimated_effort": "1-2 ore",
                "responsible_role": "Responsabile HSE",
                "frontend_display": {
                    "icon": "warning",
                    "color": "orange"
                }
            })
        
        return {
            "analysis_id": f"fast_analysis_{int(time.time())}_{user_context.get('user_id', 'unknown')}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": True,
            "confidence_score": content_result.get("confidence_score", 0.75),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": ["ContentAnalysisAgent"],
            "ai_version": "FastAI-1.0",
            
            # Required Pydantic fields
            "executive_summary": {
                "overall_score": content_quality.get("overall_score", 0.7),
                "critical_issues": len([mf for mf in missing_fields if mf.get("criticality") == "alta"]),
                "recommendations": len(improvements),
                "compliance_level": "da_verificare",
                "estimated_completion_time": "2-4 ore",
                "key_findings": [
                    f"Analisi completata per {title}",
                    f"Tipo lavoro: {work_type}",
                    f"Qualità contenuto: {content_quality.get('overall_score', 0.7):.1f}/1.0"
                ],
                "next_steps": [
                    "Implementare miglioramenti suggeriti",
                    "Verificare DPI richiesti",
                    "Completare campi mancanti"
                ]
            },
            
            "action_items": action_items,
            
            "citations": {
                "normative": [],
                "procedures": [],
                "guidelines": []
            },
            
            "completion_roadmap": {
                "immediate": [
                    "Verificare completezza informazioni",
                    "Controllare DPI richiesti"
                ],
                "short_term": [
                    "Implementare miglioramenti",
                    "Formazione specifica"
                ],
                "long_term": [
                    "Monitoraggio continuo",
                    "Aggiornamento procedure"
                ]
            },
            
            "performance_metrics": {
                "total_processing_time": 0.0,  # Will be set by caller
                "agents_successful": 1,
                "agents_total": 1,
                "analysis_method": "Fast Single Agent"
            },
            
            # Enhanced features data
            "content_improvements": content_result,
            "risk_assessment": {
                "identified_risks": basic_risks,
                "risk_level": "medio",
                "analysis_complete": True
            },
            "dpi_recommendations": {
                "required_dpi": basic_dpi,
                "analysis_complete": True
            },
            "compliance_check": {
                "compliance_level": "parziale",
                "missing_requirements": [mf.get("field_name", "Campo") for mf in missing_fields],
                "analysis_complete": True
            }
        }
    
    def _get_basic_risks_by_work_type(self, work_type: str) -> List[Dict[str, Any]]:
        """
        Get basic risks based on work type
        """
        risk_mappings = {
            "chimico": [
                {"risk": "Esposizione sostanze chimiche", "level": "alto"},
                {"risk": "Contaminazione", "level": "medio"},
                {"risk": "Reazioni pericolose", "level": "alto"}
            ],
            "meccanico": [
                {"risk": "Lesioni da attrezzature", "level": "medio"},
                {"risk": "Energia residua", "level": "alto"},
                {"risk": "Parti in movimento", "level": "medio"}
            ],
            "elettrico": [
                {"risk": "Elettrocuzione", "level": "alto"},
                {"risk": "Arco elettrico", "level": "alto"},
                {"risk": "Incendio", "level": "medio"}
            ],
            "scavo": [
                {"risk": "Cedimento scavo", "level": "alto"},
                {"risk": "Servizi interrati", "level": "alto"},
                {"risk": "Caduta materiali", "level": "medio"}
            ]
        }
        
        return risk_mappings.get(work_type, [
            {"risk": "Rischi generali sul lavoro", "level": "medio"},
            {"risk": "Lesioni personali", "level": "medio"}
        ])
    
    def _get_basic_dpi_by_work_type(self, work_type: str) -> List[str]:
        """
        Get basic DPI requirements based on work type
        """
        dpi_mappings = {
            "chimico": ["Tuta chimica", "Respiratore", "Guanti chimici", "Occhiali", "Calzature antiscivolo"],
            "meccanico": ["Casco", "Guanti anticorte", "Scarpe antinfortunistiche", "Occhiali"],
            "elettrico": ["Casco dielettrico", "Guanti dielettrici", "Scarpe isolanti", "Tester"],
            "scavo": ["Casco", "Imbracatura", "Scarpe antinfortunistiche", "Giubbotto alta visibilità"],
            "edile": ["Casco", "Imbracatura anticaduta", "Scarpe antinfortunistiche", "Guanti"],
        }
        
        return dpi_mappings.get(work_type, ["Casco", "Guanti", "Scarpe antinfortunistiche", "Occhiali"])
    
    def _create_simple_fallback_response(
        self,
        permit_data: Dict[str, Any],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create simple fallback response when analysis fails
        """
        work_type = permit_data.get("work_type", "generale")
        basic_risks = self._get_basic_risks_by_work_type(work_type)
        basic_dpi = self._get_basic_dpi_by_work_type(work_type)
        
        return {
            "analysis_id": f"fallback_{int(time.time())}_{user_context.get('user_id', 'unknown')}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": True,
            "confidence_score": 0.5,
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": ["FallbackAnalysis"],
            "ai_version": "FastAI-Fallback-1.0",
            
            "executive_summary": {
                "overall_score": 0.5,
                "critical_issues": 1,
                "recommendations": 3,
                "compliance_level": "da_verificare",
                "estimated_completion_time": "2-4 ore",
                "key_findings": [
                    f"Analisi di base per tipo lavoro: {work_type}",
                    "Analisi dettagliata non disponibile",
                    "Raccomandazioni standard applicate"
                ],
                "next_steps": [
                    "Verificare manualmente i requisiti",
                    "Consultare procedure specifiche",
                    "Riprovare analisi dettagliata"
                ]
            },
            
            "action_items": [
                {
                    "id": "fallback_1",
                    "type": "verification",
                    "priority": "alta",
                    "title": "Verifica manuale requisiti",
                    "description": "Verifica manuale dei requisiti di sicurezza per questo tipo di lavoro",
                    "suggested_action": "Consultare procedure standard",
                    "consequences_if_ignored": "Possibili rischi non identificati",
                    "references": [],
                    "estimated_effort": "30 minuti",
                    "responsible_role": "Responsabile HSE",
                    "frontend_display": {"icon": "check", "color": "blue"}
                }
            ],
            
            "citations": {"normative": [], "procedures": [], "guidelines": []},
            "completion_roadmap": {
                "immediate": ["Verifica manuale", "Consultare procedure"],
                "short_term": ["Analisi dettagliata", "Formazione"],
                "long_term": ["Miglioramento processo"]
            },
            
            "performance_metrics": {
                "total_processing_time": 0.0,
                "agents_successful": 0,
                "agents_total": 1,
                "analysis_method": "Fallback Analysis"
            },
            
            "content_improvements": {"analysis_complete": False, "confidence_score": 0.0},
            "risk_assessment": {"identified_risks": basic_risks, "analysis_complete": True},
            "dpi_recommendations": {"required_dpi": basic_dpi, "analysis_complete": True},
            "compliance_check": {"compliance_level": "da_verificare", "analysis_complete": False}
        }
    
    def _create_emergency_response(
        self,
        permit_data: Dict[str, Any],
        processing_time: float,
        error_message: str
    ) -> Dict[str, Any]:
        """
        Create emergency response when everything fails
        """
        return {
            "analysis_id": f"emergency_{int(time.time())}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": False,
            "confidence_score": 0.0,
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": [],
            "ai_version": "Emergency-1.0",
            "error": f"Emergency fallback: {error_message}",
            
            "executive_summary": {
                "overall_score": 0.0,
                "critical_issues": 1,
                "recommendations": 1,
                "compliance_level": "errore",
                "estimated_completion_time": "Unknown",
                "key_findings": ["Analisi fallita - utilizzare verifica manuale"],
                "next_steps": ["Contattare supporto tecnico", "Verifica manuale", "Riprovare più tardi"]
            },
            
            "action_items": [],
            "citations": {},
            "completion_roadmap": {
                "immediate": ["Verifica manuale"],
                "short_term": ["Riprovare analisi"],
                "long_term": ["Miglioramento sistema"]
            },
            
            "performance_metrics": {
                "total_processing_time": processing_time,
                "agents_successful": 0,
                "agents_total": 1,
                "analysis_method": "Emergency Fallback"
            }
        }
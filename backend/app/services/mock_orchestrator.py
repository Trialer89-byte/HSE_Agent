from typing import Dict, Any, List
import time
from datetime import datetime


class MockOrchestrator:
    """
    Mock orchestrator that returns instant results without AI calls
    For testing and emergency fallback
    """
    
    async def run_mock_analysis(
        self,
        permit_data: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        vector_service=None
    ) -> Dict[str, Any]:
        """
        Return immediate mock analysis results
        """
        start_time = time.time()
        print(f"[MockOrchestrator] Generating instant mock analysis for permit {permit_data.get('id')}")
        
        # Simulate minimal processing time
        processing_time = time.time() - start_time
        
        work_type = permit_data.get("work_type", "generale").lower()
        title = permit_data.get("title", "Permesso di lavoro")
        description = permit_data.get("description", "")
        
        # Generate realistic mock data based on work type
        mock_data = self._generate_mock_data(work_type, title, description)
        
        result = {
            "analysis_id": f"mock_{int(time.time())}_{user_context.get('user_id', 'test')}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": True,
            "confidence_score": mock_data["confidence"],
            "processing_time": round(processing_time, 3),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": ["MockAgent"],
            "ai_version": "Mock-1.0",
            
            # Required Pydantic fields
            "executive_summary": {
                "overall_score": mock_data["overall_score"],
                "critical_issues": mock_data["critical_issues"],
                "recommendations": len(mock_data["action_items"]),
                "compliance_level": mock_data["compliance_level"],
                "estimated_completion_time": mock_data["completion_time"],
                "key_findings": mock_data["key_findings"],
                "next_steps": mock_data["next_steps"]
            },
            
            "action_items": mock_data["action_items"],
            
            "citations": {
                "normative": self._convert_refs_to_citations(mock_data.get("normative_refs", [])),
                "procedures": self._convert_refs_to_citations(mock_data.get("procedure_refs", [])),
                "guidelines": []
            },
            
            "completion_roadmap": {
                "immediate": mock_data["immediate_actions"],
                "short_term": mock_data["short_term_actions"],
                "long_term": ["Monitoraggio continuo", "Aggiornamento procedure"]
            },
            
            "performance_metrics": {
                "total_processing_time": processing_time,
                "agents_successful": 1,
                "agents_total": 1,
                "analysis_method": "Mock Analysis (No AI calls)"
            },
            
            # Enhanced features mock data
            "content_improvements": {
                "analysis_complete": True,
                "confidence_score": 0.8,
                "content_quality": {"overall_score": mock_data["overall_score"]},
                "missing_fields": [],
                "improvement_suggestions": mock_data.get("improvements", [])
            },
            
            "risk_assessment": {
                "identified_risks": mock_data["risks"],
                "risk_level": mock_data["risk_level"],
                "analysis_complete": True,
                "confidence_score": 0.85
            },
            
            "dpi_recommendations": {
                "required_dpi": mock_data["dpi"],
                "dpi_adequacy": "adeguato",
                "analysis_complete": True
            },
            
            "compliance_check": {
                "compliance_level": mock_data["compliance_level"],
                "missing_requirements": [],
                "normative_references": self._convert_refs_to_citations(mock_data.get("normative_refs", [])),
                "analysis_complete": True
            }
        }
        
        print(f"[MockOrchestrator] Mock analysis completed in {processing_time:.3f}s")
        return result
    
    def _generate_mock_data(self, work_type: str, title: str, description: str) -> Dict[str, Any]:
        """
        Generate realistic mock data based on work type
        """
        base_data = {
            "confidence": 0.75,
            "overall_score": 0.7,
            "critical_issues": 1,
            "compliance_level": "parziale",
            "completion_time": "2-4 ore",
            "risk_level": "medio"
        }
        
        if work_type == "meccanico":
            return {
                **base_data,
                "key_findings": [
                    "Lavoro meccanico identificato",
                    "Rischi da attrezzature e energia residua",
                    "DPI specifici richiesti"
                ],
                "next_steps": [
                    "Verificare isolamento energetico",
                    "Controllare stato attrezzature",
                    "Briefing sicurezza pre-lavoro"
                ],
                "risks": [
                    {"risk": "Lesioni da attrezzature", "level": "medio", "probability": "media"},
                    {"risk": "Energia residua", "level": "alto", "probability": "bassa"},
                    {"risk": "Parti in movimento", "level": "medio", "probability": "media"}
                ],
                "dpi": ["Casco", "Guanti anticorte", "Scarpe antinfortunistiche", "Occhiali"],
                "action_items": [
                    {
                        "id": "mech_1",
                        "type": "safety_check", 
                        "priority": "alta",
                        "title": "Verifica isolamento energetico",
                        "description": "Verificare che tutte le fonti di energia siano isolate",
                        "suggested_action": "Applicare procedura LOTO (Lockout/Tagout)",
                        "consequences_if_ignored": "Rischio di avvio accidentale",
                        "references": ["D.Lgs 81/2008"],
                        "estimated_effort": "30 minuti",
                        "responsible_role": "Manutentore qualificato",
                        "frontend_display": {"icon": "lock", "color": "red"}
                    },
                    {
                        "id": "mech_2",
                        "type": "equipment",
                        "priority": "media", 
                        "title": "Controllo stato attrezzature",
                        "description": "Verificare che le attrezzature siano in buone condizioni",
                        "suggested_action": "Ispezione visiva e funzionale",
                        "consequences_if_ignored": "Possibili malfunzionamenti",
                        "references": [],
                        "estimated_effort": "15 minuti",
                        "responsible_role": "Operatore",
                        "frontend_display": {"icon": "tool", "color": "orange"}
                    }
                ],
                "immediate_actions": [
                    "Isolamento energetico",
                    "Verifica DPI"
                ],
                "short_term_actions": [
                    "Briefing sicurezza",
                    "Controllo attrezzature"
                ],
                "normative_refs": ["D.Lgs 81/2008 - Sicurezza macchine"],
                "improvements": [
                    {"area": "procedura", "suggestion": "Dettagliare sequenza isolamento"}
                ]
            }
        
        elif work_type == "chimico":
            return {
                **base_data,
                "confidence": 0.8,
                "critical_issues": 2,
                "key_findings": [
                    "Lavoro con sostanze chimiche",
                    "Rischi di esposizione e contaminazione", 
                    "DPI chimici specifici necessari"
                ],
                "next_steps": [
                    "Consultare schede di sicurezza",
                    "Verificare ventilazione",
                    "Preparare kit emergenza"
                ],
                "risks": [
                    {"risk": "Esposizione sostanze chimiche", "level": "alto", "probability": "media"},
                    {"risk": "Contaminazione", "level": "medio", "probability": "media"},
                    {"risk": "Reazioni pericolose", "level": "alto", "probability": "bassa"}
                ],
                "dpi": ["Tuta chimica", "Respiratore", "Guanti chimici", "Occhiali", "Calzature antiscivolo"],
                "action_items": [
                    {
                        "id": "chem_1",
                        "type": "documentation",
                        "priority": "alta",
                        "title": "Consultare SDS sostanze",
                        "description": "Verificare schede di sicurezza di tutte le sostanze coinvolte",
                        "suggested_action": "Leggere e comprendere le SDS",
                        "consequences_if_ignored": "Esposizione a rischi sconosciuti",
                        "references": ["Regolamento REACH", "CLP"],
                        "estimated_effort": "45 minuti",
                        "responsible_role": "Responsabile chimico",
                        "frontend_display": {"icon": "document", "color": "red"}
                    }
                ],
                "immediate_actions": ["Verifica SDS", "Controllo ventilazione"],
                "short_term_actions": ["Kit emergenza", "Briefing chimico"],
                "normative_refs": ["REACH", "CLP", "D.Lgs 81/2008"]
            }
        
        elif work_type == "elettrico":
            return {
                **base_data,
                "confidence": 0.85,
                "critical_issues": 2,
                "risk_level": "alto",
                "key_findings": [
                    "Lavoro elettrico ad alto rischio",
                    "Rischio elettrocuzione",
                    "DPI dielettrici obbligatori"
                ],
                "next_steps": [
                    "Verifica assenza tensione",
                    "Messa a terra",
                    "Autorizzazione elettrica"
                ],
                "risks": [
                    {"risk": "Elettrocuzione", "level": "alto", "probability": "media"},
                    {"risk": "Arco elettrico", "level": "alto", "probability": "bassa"},
                    {"risk": "Incendio", "level": "medio", "probability": "bassa"}
                ],
                "dpi": ["Casco dielettrico", "Guanti dielettrici", "Scarpe isolanti", "Tester"],
                "action_items": [
                    {
                        "id": "elec_1",
                        "type": "safety_procedure",
                        "priority": "alta",
                        "title": "Procedura 5 regole d'oro",
                        "description": "Applicare le 5 regole d'oro per lavori elettrici",
                        "suggested_action": "Sezionare, bloccare, verificare, mettere a terra, delimitare",
                        "consequences_if_ignored": "Rischio mortale da elettrocuzione",
                        "references": ["CEI 11-27", "D.Lgs 81/2008"],
                        "estimated_effort": "1 ora",
                        "responsible_role": "Elettricista qualificato",
                        "frontend_display": {"icon": "zap", "color": "red"}
                    }
                ],
                "immediate_actions": ["Sezionamento", "Verifica assenza tensione"],
                "short_term_actions": ["Messa a terra", "Delimitazione area"],
                "normative_refs": ["CEI 11-27", "D.Lgs 81/2008"]
            }
        
        else:  # Default/generale
            return {
                **base_data,
                "key_findings": [
                    f"Analisi per tipo lavoro: {work_type}",
                    "Applicazione misure standard",
                    "Verifica specifica necessaria"
                ],
                "next_steps": [
                    "Valutazione rischi specifica",
                    "Definizione DPI",
                    "Autorizzazioni necessarie"
                ],
                "risks": [
                    {"risk": "Rischi generali", "level": "medio", "probability": "media"},
                    {"risk": "Lesioni personali", "level": "medio", "probability": "media"}
                ],
                "dpi": ["Casco", "Guanti", "Scarpe antinfortunistiche"],
                "action_items": [
                    {
                        "id": "gen_1",
                        "type": "assessment",
                        "priority": "media",
                        "title": "Valutazione rischi specifica",
                        "description": "Effettuare valutazione dettagliata dei rischi",
                        "suggested_action": "Analisi sul posto",
                        "consequences_if_ignored": "Rischi non identificati",
                        "references": ["D.Lgs 81/2008"],
                        "estimated_effort": "1 ora",
                        "responsible_role": "RSPP",
                        "frontend_display": {"icon": "search", "color": "blue"}
                    }
                ],
                "immediate_actions": ["Valutazione preliminare"],
                "short_term_actions": ["Definizione procedure"],
                "normative_refs": ["D.Lgs 81/2008"]
            }
    
    def _convert_refs_to_citations(self, refs: List[str]) -> List[Dict[str, Any]]:
        """
        Convert simple reference strings to Citation objects
        """
        citations = []
        for ref in refs:
            citations.append({
                "document_info": {
                    "title": ref,
                    "type": "normativa" if "D.Lgs" in ref or "CEI" in ref else "regolamento",
                    "code": ref.split(" - ")[0] if " - " in ref else ref
                },
                "relevance": {
                    "score": 0.9,
                    "context": "Riferimento normativo applicabile"
                },
                "key_requirements": [],
                "frontend_display": {
                    "icon": "book",
                    "color": "blue"
                }
            })
        return citations
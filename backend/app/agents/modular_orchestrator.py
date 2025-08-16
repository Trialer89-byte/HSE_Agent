"""
Modular Orchestrator for HSE Agent System
Dynamically loads and coordinates specialist agents
"""

import asyncio
from typing import Dict, Any, List, Optional
import time
import json
from datetime import datetime

from .specialists import get_all_specialists, get_specialist
from .specialists.risk_classifier_agent import RiskClassifierAgent


class ModularHSEOrchestrator:
    """
    Modular orchestrator that coordinates specialist agents
    """
    
    def __init__(self, user_context: Dict[str, Any] = None, vector_service=None):
        self.user_context = user_context or {}
        self.vector_service = vector_service
        self.specialists = get_all_specialists()
        self.risk_classifier = self.specialists.get("risk_classifier")
        
        # Inject vector service into all specialists for autonomous search
        if vector_service:
            for specialist in self.specialists.values():
                specialist.vector_service = vector_service
            print(f"[ModularOrchestrator] Injected vector service into {len(self.specialists)} specialists")
        
        print(f"[ModularOrchestrator] Initialized with {len(self.specialists)} specialists:")
        for name in self.specialists.keys():
            print(f"  - {name}")
    
    async def analyze_permit(
        self, 
        permit_data: Dict[str, Any], 
        context_documents: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Orchestrate analysis using modular specialist agents
        """
        start_time = time.time()
        context_documents = context_documents or []
        
        try:
            print(f"\n[ModularOrchestrator] Starting analysis for permit {permit_data.get('id')}")
            
            # Phase 1: Primary Risk Classification
            print("[ModularOrchestrator] Phase 1: Risk Classification")
            classification_result = await self._run_risk_classification(permit_data, context_documents)
            
            if not classification_result.get("classification_complete"):
                return self._create_error_result("Risk classification failed", start_time)
            
            # Phase 2: Run Relevant Specialists
            print("[ModularOrchestrator] Phase 2: Running Specialist Analysis")
            specialists_to_run = classification_result.get("specialists_to_activate", [])
            print(f"  Specialists to activate: {specialists_to_run}")
            
            specialist_results = await self._run_specialists(
                permit_data, 
                classification_result,
                specialists_to_run
            )
            
            # Phase 3: Consolidate Results
            print("[ModularOrchestrator] Phase 3: Consolidating Results")
            final_result = self._consolidate_results(
                permit_data,
                classification_result,
                specialist_results,
                context_documents,
                time.time() - start_time
            )
            
            print(f"[ModularOrchestrator] Analysis completed in {time.time() - start_time:.2f}s")
            return final_result
            
        except Exception as e:
            print(f"[ModularOrchestrator] Error during analysis: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_result(str(e), start_time)
    
    async def _run_risk_classification(
        self, 
        permit_data: Dict[str, Any], 
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Run primary risk classification"""
        
        # Format documents for analysis
        documents_context = ""
        if context_documents:
            documents_context = "\n\nDOCUMENTI AZIENDALI DISPONIBILI:\n"
            for i, doc in enumerate(context_documents[:3], 1):  # Limit to top 3 docs
                documents_context += f"\n[DOC {i}] {doc.get('title', 'N/A')}\n"
                documents_context += f"Tipo: {doc.get('document_type', 'N/A')}\n"
                content_preview = doc.get('content', '')[:500]  # First 500 chars
                documents_context += f"Contenuto: {content_preview}...\n"
                documents_context += "-" * 40 + "\n"
        
        context = {
            "documents": context_documents,
            "user_context": self.user_context,
            "documents_context": documents_context
        }
        
        # Run risk classifier (now async)
        classification = await self.risk_classifier.analyze(permit_data, context)
        
        # Store documents in classification for passing to specialists
        classification["documents"] = context_documents
        classification["documents_context"] = documents_context
        
        # Always enhance with AI if we have documents
        if context_documents or classification.get("missing_critical_info"):
            print("  [Classifier] Enhancing analysis with AI and documents")
            enhance_prompt = f"""
Analizza questo permesso utilizzando i documenti aziendali forniti:

PERMESSO:
{json.dumps(permit_data, ensure_ascii=False)}

{documents_context}

Identifica tutti i rischi e specifica sempre la fonte (Documento Aziendale o Conoscenza Generale).
"""
            ai_analysis = await self.risk_classifier.get_gemini_response(
                enhance_prompt,
                context_documents=context_documents
            )
            classification["ai_enhanced_analysis"] = ai_analysis
            classification["documents_used"] = len(context_documents)
        
        return classification
    
    async def _run_specialists(
        self,
        permit_data: Dict[str, Any],
        classification: Dict[str, Any],
        specialists_to_run: List[str]
    ) -> Dict[str, Any]:
        """Run relevant specialist agents"""
        
        results = {}
        tasks = []
        
        for specialist_name in specialists_to_run:
            # Clean the specialist name
            clean_name = specialist_name.replace("_specialist", "")
            
            specialist = self.specialists.get(clean_name)
            if specialist and specialist.name != "Risk_Classifier":
                print(f"  Running specialist: {specialist.name}")
                
                # Check if specialist should activate
                if specialist.should_activate(classification):
                    task = self._run_single_specialist(
                        specialist,
                        permit_data,
                        classification
                    )
                    tasks.append((specialist.name, task))
        
        # Run all specialists in parallel
        if tasks:
            specialist_outputs = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            for i, (name, _) in enumerate(tasks):
                if not isinstance(specialist_outputs[i], Exception):
                    results[name] = specialist_outputs[i]
                else:
                    print(f"  [Error] Specialist {name} failed: {specialist_outputs[i]}")
                    results[name] = {"error": str(specialist_outputs[i])}
        
        return results
    
    async def _run_single_specialist(
        self,
        specialist,
        permit_data: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run a single specialist agent"""
        
        # Include documents from classification in context
        context = {
            "classification": classification,
            "user_context": self.user_context,
            "documents": classification.get("documents", []),
            "documents_context": classification.get("documents_context", "")
        }
        
        # Get specialist analysis (now async for autonomous search)
        result = await specialist.analyze(permit_data, context)
        
        # Enhance with AI if needed for complex cases
        if classification.get("overall_risk_level", "").startswith("CRITICO"):
            documents = context.get("documents", [])
            ai_enhancement = await specialist.get_gemini_response(
                f"Provide detailed safety analysis for: {json.dumps(permit_data, ensure_ascii=False)}",
                context_documents=documents
            )
            result["ai_enhanced"] = ai_enhancement
        
        return result
    
    def _consolidate_results(
        self,
        permit_data: Dict[str, Any],
        classification: Dict[str, Any],
        specialist_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        processing_time: float
    ) -> Dict[str, Any]:
        """Consolidate all results into final format"""
        
        # Collect all identified risks
        all_risks = []
        all_controls = []
        all_dpi = []
        all_permits = []
        
        # Add risks from classification
        for risk_type, risk_data in classification.get("detected_risks", {}).items():
            all_risks.append({
                "type": risk_type,
                "source": "Risk_Classifier",
                "indicators": risk_data
            })
        
        # Add risks from specialists
        for specialist_name, result in specialist_results.items():
            if "error" not in result:
                all_risks.extend(result.get("risks_identified", []))
                all_controls.extend(result.get("control_measures", []))
                all_dpi.extend(result.get("dpi_requirements", []))
                all_permits.extend(result.get("permits_required", []))
        
        # Remove duplicates
        all_controls = list(set(all_controls))
        all_dpi = list(set(all_dpi))
        all_permits = list(set(all_permits))
        
        # Convert to action items for frontend
        action_items = self._create_action_items(all_controls, all_dpi, all_permits)
        
        # Build executive summary
        critical_issues = len([r for r in all_risks if 
                              isinstance(r, dict) and 
                              r.get("severity") in ["critica", "alta"]])
        
        # Convert to 0-1 scale (0 = worst, 1 = best)
        overall_score = 0.2 if critical_issues > 2 else (0.5 if critical_issues > 0 else 0.8)
        
        executive_summary = {
            "overall_score": overall_score,
            "critical_issues": critical_issues,
            "recommendations": len(action_items),
            "compliance_level": classification.get("overall_risk_level", "da_verificare"),
            "estimated_completion_time": f"{len(action_items)*2}-{len(action_items)*4} ore",
            "key_findings": self._extract_key_findings(classification, all_risks),
            "next_steps": self._generate_next_steps(all_permits, critical_issues)
        }
        
        # Build citations (including company documents)
        citations = self._build_citations(specialist_results, context_documents)
        
        return {
            "analysis_id": f"modular_{int(time.time())}_{permit_data.get('id')}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": True,
            "confidence_score": 0.85 if not classification.get("missing_critical_info") else 0.65,
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": ["Risk_Classifier"] + list(specialist_results.keys()),
            "ai_version": "Modular-1.0",
            "executive_summary": executive_summary,
            "action_items": action_items,
            "citations": citations,
            "completion_roadmap": self._create_roadmap(action_items, all_permits),
            "performance_metrics": {
                "total_processing_time": round(processing_time, 2),
                "specialists_activated": len(specialist_results),
                "risks_identified": len(all_risks),
                "controls_recommended": len(all_controls),
                "analysis_method": "Modular Specialist System"
            }
        }
    
    def _create_action_items(
        self, 
        controls: List[str], 
        dpi: List[str], 
        permits: List[str]
    ) -> List[Dict[str, Any]]:
        """Convert controls and requirements to action items"""
        
        action_items = []
        item_id = 1
        
        # Add permit requirements first (highest priority)
        for permit in permits:
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "permit_requirement",
                "priority": "critica",
                "title": f"Ottenere {permit}",
                "description": f"Permesso obbligatorio: {permit}",
                "suggested_action": f"Compilare e approvare {permit} prima inizio lavori",
                "consequences_if_ignored": "Lavori non autorizzati - violazione procedure sicurezza",
                "references": ["D.Lgs 81/08", "Procedure aziendali"],
                "estimated_effort": "30-60 minuti",
                "responsible_role": "RSPP / Preposto",
                "frontend_display": {
                    "color": "red",
                    "icon": "file-check",
                    "category": "Permessi Obbligatori"
                }
            })
            item_id += 1
        
        # Add DPI requirements
        for dpi_item in dpi[:10]:  # Limit to 10 most important
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "dpi_requirement",
                "priority": "alta",
                "title": f"Fornire {dpi_item[:30]}",
                "description": dpi_item,
                "suggested_action": f"Verificare disponibilità e distribuzione {dpi_item}",
                "consequences_if_ignored": "Esposizione diretta ai rischi identificati",
                "references": [],
                "estimated_effort": "15-30 minuti",
                "responsible_role": "Magazzino DPI",
                "frontend_display": {
                    "color": "yellow",
                    "icon": "shield-check",
                    "category": "DPI Richiesti"
                }
            })
            item_id += 1
        
        # Add control measures
        for control in controls[:10]:  # Limit to 10 most important
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "control_measure",
                "priority": "media",
                "title": control[:50],
                "description": control,
                "suggested_action": control,
                "consequences_if_ignored": "Controllo rischi inadeguato",
                "references": [],
                "estimated_effort": "variabile",
                "responsible_role": "Preposto",
                "frontend_display": {
                    "color": "blue",
                    "icon": "check-circle",
                    "category": "Misure di Controllo"
                }
            })
            item_id += 1
        
        return action_items
    
    def _extract_key_findings(
        self, 
        classification: Dict[str, Any], 
        risks: List
    ) -> List[str]:
        """Extract key findings from analysis"""
        
        findings = []
        
        # Add overall risk level
        findings.append(classification.get("overall_risk_level", "Rischio non classificato"))
        
        # Add implicit risks if found
        for implicit in classification.get("implicit_risks", [])[:2]:
            findings.append(implicit)
        
        # Add critical risks from specialists
        for risk in risks:
            if isinstance(risk, dict) and risk.get("severity") == "critica":
                findings.append(risk.get("description", "Rischio critico identificato"))
                if len(findings) >= 5:
                    break
        
        return findings[:5]  # Max 5 findings
    
    def _generate_next_steps(self, permits: List[str], critical_issues: int) -> List[str]:
        """Generate next steps based on analysis"""
        
        steps = []
        
        if permits:
            steps.append(f"Ottenere permessi richiesti: {', '.join(permits)}")
        
        if critical_issues > 0:
            steps.append(f"Risolvere {critical_issues} problemi critici identificati")
        
        steps.extend([
            "Briefing sicurezza con tutti gli operatori",
            "Verifica disponibilità DPI e attrezzature",
            "Implementare misure di controllo"
        ])
        
        return steps[:4]  # Max 4 steps
    
    def _build_citations(self, specialist_results: Dict[str, Any], context_documents: List[Dict[str, Any]] = None) -> Dict[str, List]:
        """Build citations from specialist results and available documents"""
        
        citations = {
            "normative_framework": [],
            "company_procedures": []
        }
        
        # Add company procedures from available documents
        if context_documents:
            for doc in context_documents[:3]:  # Top 3 relevant docs
                citations["company_procedures"].append({
                    "document_info": {
                        "title": f"[FONTE: Documento Aziendale] {doc.get('title', 'N/A')}",
                        "type": doc.get('document_type', 'Procedura').title(),
                        "date": "Current"
                    },
                    "relevance": {
                        "score": 0.95,
                        "reason": "Documento aziendale specificamente applicabile"
                    },
                    "key_requirements": [
                        {"requirement": "Conformità procedura", "description": "Seguire indicazioni del documento aziendale"},
                        {"requirement": "Verifica applicabilità", "description": "Verificare che il documento sia applicabile al caso specifico"}
                    ],
                    "frontend_display": {
                        "color": "green",
                        "icon": "building",
                        "category": "Documento Aziendale"
                    }
                })
        
        # Add standard regulations based on specialists activated
        if "HotWork_Specialist" in specialist_results:
            citations["normative_framework"].append({
                "document_info": {
                    "title": "[FONTE: Specialist Knowledge] D.M. 10/03/1998 - Prevenzione incendi",
                    "type": "Normativa",
                    "date": "Current"
                },
                "relevance": {
                    "score": 0.95,
                    "reason": "Applicabile per lavori a caldo"
                },
                "key_requirements": [
                    {"requirement": "Hot work permit", "description": "Permesso obbligatorio per lavori a caldo"},
                    {"requirement": "Fire watch", "description": "Sorveglianza antincendio continua"}
                ],
                "frontend_display": {
                    "color": "red",
                    "icon": "fire",
                    "category": "Normativa Antincendio"
                }
            })
        
        if "ConfinedSpace_Specialist" in specialist_results:
            citations["normative_framework"].append({
                "document_info": {
                    "title": "[FONTE: Specialist Knowledge] DPR 177/2011 - Spazi confinati",
                    "type": "Normativa",
                    "date": "Current"
                },
                "relevance": {
                    "score": 0.95,
                    "reason": "Obbligatorio per spazi confinati"
                },
                "key_requirements": [
                    {"requirement": "Qualificazione impresa", "description": "30% personale con esperienza triennale"},
                    {"requirement": "Formazione specifica", "description": "Addestramento obbligatorio tutto il personale"}
                ],
                "frontend_display": {
                    "color": "red",
                    "icon": "alert-triangle",
                    "category": "Normativa Spazi Confinati"
                }
            })
        
        # Always add base safety regulation
        citations["normative_framework"].append({
            "document_info": {
                "title": "[FONTE: Sistema] D.Lgs 81/08 - Testo Unico Sicurezza",
                "type": "Normativa",
                "date": "Current"
            },
            "relevance": {
                "score": 0.90,
                "reason": "Normativa base sicurezza lavoro"
            },
            "key_requirements": [],
            "frontend_display": {
                "color": "green",
                "icon": "book",
                "category": "Normativa Base"
            }
        })
        
        return citations
    
    def _create_roadmap(self, action_items: List[Dict], permits: List[str]) -> Dict[str, List[str]]:
        """Create completion roadmap"""
        
        return {
            "immediate_actions": [
                f"Ottenere {len(permits)} permessi richiesti" if permits else "Verificare documentazione",
                "Briefing sicurezza pre-lavoro",
                "Verifica DPI disponibili"
            ][:3],
            "short_term_actions": [
                f"Implementare {len(action_items)} azioni richieste",
                "Setup area di lavoro sicura",
                "Posizionare attrezzature emergenza"
            ][:3],
            "medium_term_actions": [
                "Monitoraggio continuo condizioni",
                "Audit periodici conformità",
                "Aggiornamento valutazione rischi"
            ],
            "success_metrics": [
                "Zero incidenti",
                "100% conformità procedure",
                "Completamento nei tempi"
            ],
            "review_checkpoints": [
                "Pre-start safety meeting",
                "Controlli ogni 2 ore",
                "Review fine turno"
            ]
        }
    
    def _create_error_result(self, error_msg: str, start_time: float) -> Dict[str, Any]:
        """Create error result in expected format"""
        
        return {
            "analysis_id": f"error_{int(time.time())}",
            "analysis_complete": False,
            "error": error_msg,
            "confidence_score": 0.0,
            "processing_time": round(time.time() - start_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": [],
            "executive_summary": {
                "overall_score": 0.0,
                "critical_issues": 1,
                "recommendations": 0,
                "compliance_level": "errore_sistema",
                "estimated_completion_time": "N/A",
                "key_findings": [f"ERRORE: {error_msg}"],
                "next_steps": ["Risolvere errore", "Ripetere analisi"]
            },
            "action_items": [],
            "citations": {
                "normative_framework": [],
                "company_procedures": []
            },
            "completion_roadmap": {}
        }
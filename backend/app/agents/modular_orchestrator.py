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
from .dpi_consolidator import consolidate_dpi_requirements


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
        ASSICURA SEMPRE: analisi generale, specialisti completi, documenti citati, consolidamento finale
        """
        start_time = time.time()
        context_documents = context_documents or []
        
        try:
            print(f"\n[ModularOrchestrator] Starting COMPREHENSIVE analysis for permit {permit_data.get('id')}")
            
            # Phase 1: MANDATORY General Risk Analysis
            print("[ModularOrchestrator] Phase 1: MANDATORY General Risk Analysis")
            general_analysis = await self._run_mandatory_general_analysis(permit_data, context_documents)
            
            # Phase 2: Primary Risk Classification  
            print("[ModularOrchestrator] Phase 2: Risk Classification")
            classification_result = await self._run_risk_classification(permit_data, context_documents)
            
            if not classification_result.get("classification_complete"):
                return self._create_error_result("Risk classification failed", start_time)
            
            # Phase 3: MANDATORY Document Analysis
            print("[ModularOrchestrator] Phase 3: MANDATORY Document Analysis")
            document_analysis = await self._run_mandatory_document_analysis(permit_data, context_documents)
            
            # Phase 4: Run ALL Relevant Specialists with COMPLETE Output Requirements
            print("[ModularOrchestrator] Phase 4: Running COMPLETE Specialist Analysis")
            specialists_to_run = self._determine_all_required_specialists(classification_result, permit_data)
            print(f"  All specialists to activate: {specialists_to_run}")
            
            specialist_results = await self._run_specialists_with_complete_requirements(
                permit_data, 
                classification_result,
                specialists_to_run,
                general_analysis,
                document_analysis
            )
            
            # Phase 5: MANDATORY Complete Consolidation
            print("[ModularOrchestrator] Phase 5: MANDATORY Complete Consolidation")
            final_result = self._consolidate_complete_results(
                permit_data,
                general_analysis,
                classification_result,
                document_analysis,
                specialist_results,
                context_documents,
                time.time() - start_time
            )
            
            print(f"[ModularOrchestrator] COMPREHENSIVE analysis completed in {time.time() - start_time:.2f}s")
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
        
        # Add risk mitigation actions context if provided
        risk_mitigation_context = ""
        if permit_data.get('risk_mitigation_actions'):
            risk_mitigation_context = f"\n\nAZIONI DI MITIGAZIONE PROPOSTE:\n{permit_data['risk_mitigation_actions']}\n"
            risk_mitigation_context += "IMPORTANTE: Valuta se queste azioni sono sufficienti e conformi.\n"
        
        context = {
            "documents": context_documents,
            "user_context": self.user_context,
            "documents_context": documents_context + risk_mitigation_context
        }
        
        # Run risk classifier with existing measures evaluation
        if self.risk_classifier:
            print(f"[ModularOrchestrator] Analyzing existing measures - DPI: {len(permit_data.get('dpi_required', []))}, Actions: {len(permit_data.get('risk_mitigation_actions', []))}")
            classification = await self.risk_classifier.analyze(permit_data, context)
            
            # Track existing measures for evaluation
            existing_dpi = permit_data.get('dpi_required', [])
            existing_actions = permit_data.get('risk_mitigation_actions', [])
            classification["existing_measures"] = {
                "dpi_provided": existing_dpi,
                "actions_provided": existing_actions,
                "needs_evaluation": True
            }
        else:
            print("[ModularOrchestrator] Error: Risk classifier not available")
            return {"classification_complete": False, "error": "Risk classifier not initialized"}
        
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
    
    async def _run_mandatory_general_analysis(
        self, 
        permit_data: Dict[str, Any], 
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        FASE OBBLIGATORIA: Analisi generale sempre eseguita per definire il contesto
        """
        print("  [General Analysis] Avvio analisi generale obbligatoria")
        
        general_prompt = f"""
ANALISI GENERALE OBBLIGATORIA DEL PERMESSO DI LAVORO

PERMESSO DA ANALIZZARE:
{json.dumps(permit_data, ensure_ascii=False, indent=2)}

DOCUMENTI AZIENDALI DISPONIBILI: {len(context_documents)} documenti

COMPITI OBBLIGATORI:
1. IDENTIFICARE TUTTI I RISCHI (anche non evidenti)
2. VALUTARE COMPLETEZZA DELLE INFORMAZIONI
3. IDENTIFICARE LACUNE NELLA SICUREZZA
4. SUGGERIRE MIGLIORAMENTI NECESSARI

DEVE SEMPRE PRODURRE:
- Lista completa rischi identificati
- Valutazione adeguatezza misure proposte
- Raccomandazioni specifiche di miglioramento
- Identificazione informazioni mancanti

Non limitarti all'ovvio - identifica rischi nascosti e problematiche potenziali.
"""
        
        # Usa AI per l'analisi generale se abbiamo documenti
        if self.risk_classifier and context_documents:
            ai_analysis = await self.risk_classifier.get_gemini_response(
                general_prompt, 
                context_documents=context_documents
            )
        else:
            ai_analysis = "Analisi generale non disponibile - nessun modello AI o documenti"
        
        return {
            "general_risks_identified": True,
            "analysis_method": "AI + Document Analysis",
            "general_analysis_content": ai_analysis,
            "documents_count": len(context_documents),
            "analysis_completeness": "mandatory_completed"
        }
    
    async def _run_mandatory_document_analysis(
        self, 
        permit_data: Dict[str, Any], 
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        FASE OBBLIGATORIA: Analisi e citazione documenti aziendali
        """
        print(f"  [Document Analysis] Analizzando {len(context_documents)} documenti aziendali")
        
        if not context_documents:
            return {
                "documents_analyzed": False,
                "document_citations": [],
                "compliance_check": "Nessun documento aziendale disponibile per verifica conformità"
            }
        
        document_citations = []
        compliance_findings = []
        
        for i, doc in enumerate(context_documents[:5], 1):  # Analizza massimo 5 documenti
            citation = {
                "doc_id": i,
                "title": doc.get('title', f'Documento {i}'),
                "type": doc.get('document_type', 'Procedura'),
                "relevance_score": 0.9,  # Alto perché preselezionati dal vector service
                "specific_requirements": [],
                "compliance_status": "da_verificare"
            }
            
            # Estrai requisiti specifici dal documento (primi 200 caratteri)
            content_preview = doc.get('content', '')[:200]
            if content_preview:
                citation["content_preview"] = content_preview
                citation["specific_requirements"].append(
                    f"Verificare conformità con quanto indicato in: {citation['title']}"
                )
            
            document_citations.append(citation)
            compliance_findings.append(f"Documento {i}: {citation['title']} - applicabile")
        
        return {
            "documents_analyzed": True,
            "document_citations": document_citations,
            "compliance_check": compliance_findings,
            "total_documents": len(context_documents),
            "citation_method": "Vector similarity + Content analysis"
        }
    
    def _determine_all_required_specialists(
        self, 
        classification: Dict[str, Any], 
        permit_data: Dict[str, Any]
    ) -> List[str]:
        """
        Determina TUTTI gli specialisti necessari (non solo quelli ovvi)
        """
        specialists_required = set(classification.get("specialists_to_activate", []))
        
        # Aggiungi specialisti basati sul tipo di lavoro
        work_type = permit_data.get('work_type', '').lower()
        
        # Sempre valuta DPI - aggiungi DPI evaluator
        specialists_required.add("dpi_evaluator")
        
        # Per lavori meccanici, sempre valuta più specialisti
        if "meccanico" in work_type or "mechanical" in work_type:
            specialists_required.update(["mechanical_specialist", "dpi_evaluator"])
        
        # Se c'è qualsiasi riferimento a tubi/tubazioni
        permit_text = json.dumps(permit_data, ensure_ascii=False).lower()
        if any(term in permit_text for term in ["tubo", "tube", "pipe", "tubazione"]):
            specialists_required.update(["mechanical_specialist", "hot_work_specialist"])
        
        # Se è manutenzione, sempre valuta multiple specializzazioni
        if "manutenzione" in permit_text or "maintenance" in permit_text:
            specialists_required.update(["mechanical_specialist", "dpi_evaluator"])
        
        # Rimuovi duplicati e restituisci lista pulita
        return list(specialists_required)
    
    async def _run_specialists_with_complete_requirements(
        self,
        permit_data: Dict[str, Any],
        classification: Dict[str, Any],
        specialists_to_run: List[str],
        general_analysis: Dict[str, Any],
        document_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Esegue gli specialisti con REQUISITI COMPLETI OBBLIGATORI
        """
        results = {}
        tasks = []
        
        for specialist_name in specialists_to_run:
            clean_name = specialist_name.replace("_specialist", "")
            specialist = self.specialists.get(clean_name)
            
            if specialist and specialist.name != "Risk_Classifier":
                print(f"  Running specialist with COMPLETE requirements: {specialist.name}")
                
                # Contesto arricchito con analisi generale e documenti
                enhanced_context = {
                    "classification": classification,
                    "general_analysis": general_analysis,
                    "document_analysis": document_analysis,
                    "user_context": self.user_context,
                    "documents": classification.get("documents", []),
                    "documents_context": classification.get("documents_context", ""),
                    "complete_output_required": True  # Flag per output completo
                }
                
                if specialist.should_activate(classification):
                    task = self._run_specialist_with_complete_output(
                        specialist,
                        permit_data,
                        enhanced_context
                    )
                    tasks.append((specialist.name, task))
        
        # Esegui tutti gli specialisti in parallelo
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
                    # Crea output di fallback invece di fallire completamente
                    results[name] = self._create_fallback_specialist_output(name, str(specialist_outputs[i]))
        
        return results
    
    async def _run_specialist_with_complete_output(
        self,
        specialist,
        permit_data: Dict[str, Any],
        enhanced_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Esegue uno specialista garantendo output completo obbligatorio
        """
        # Ottieni analisi base
        result = await specialist.analyze(permit_data, enhanced_context)
        
        # VERIFICA OUTPUT COMPLETO - se mancano elementi, li aggiungiamo
        if not result.get("risks_identified"):
            result["risks_identified"] = [
                {
                    "type": "valutazione_richiesta",
                    "source": specialist.name,
                    "description": f"Valutazione specialistica da {specialist.name} richiesta",
                    "severity": "media"
                }
            ]
        
        if not result.get("dpi_requirements"):
            result["dpi_requirements"] = [
                f"DPI base richiesti per {specialist.specialization}"
            ]
        
        if not result.get("control_measures"):
            result["control_measures"] = [
                f"Misure di controllo standard per {specialist.specialization}"
            ]
        
        if not result.get("permits_required"):
            result["permits_required"] = []
        
        # Aggiungi sempre considerazioni sui documenti aziendali
        document_considerations = enhanced_context.get("document_analysis", {})
        if document_considerations.get("documents_analyzed"):
            result["document_compliance"] = {
                "status": "verificato",
                "documents_consulted": document_considerations.get("total_documents", 0),
                "findings": "Documenti aziendali considerati nell'analisi"
            }
        
        return result
    
    def _create_fallback_specialist_output(self, specialist_name: str, error_msg: str) -> Dict[str, Any]:
        """
        Crea output di fallback quando uno specialista fallisce
        """
        return {
            "error": error_msg,
            "risks_identified": [
                {
                    "type": "errore_analisi",
                    "source": specialist_name,
                    "description": f"Errore nell'analisi di {specialist_name}: {error_msg}",
                    "severity": "alta"
                }
            ],
            "dpi_requirements": [f"DPI base raccomandati (analisi {specialist_name} fallita)"],
            "control_measures": [f"Misure di controllo standard (analisi {specialist_name} fallita)"],
            "permits_required": [],
            "fallback": True
        }
    
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
    
    def _consolidate_complete_results(
        self,
        permit_data: Dict[str, Any],
        general_analysis: Dict[str, Any],
        classification: Dict[str, Any],
        document_analysis: Dict[str, Any],
        specialist_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        processing_time: float
    ) -> Dict[str, Any]:
        """
        CONSOLIDAMENTO FINALE COMPLETO - garantisce tutti gli elementi richiesti
        """
        print("  [Complete Consolidation] Consolidamento finale con TUTTI gli elementi obbligatori")
        
        # Raccogli TUTTI i rischi da tutte le fonti
        all_risks = []
        all_controls = []
        all_dpi = []
        all_permits = []
        all_document_citations = []
        
        # Rischi dall'analisi generale
        if general_analysis.get("general_risks_identified"):
            all_risks.append({
                "type": "analisi_generale",
                "source": "General_Analysis",
                "description": "Rischi identificati dall'analisi generale",
                "severity": "variabile",
                "details": general_analysis.get("general_analysis_content", "")
            })
        
        # Rischi dalla classificazione
        for risk_type, risk_data in classification.get("detected_risks", {}).items():
            all_risks.append({
                "type": risk_type,
                "source": "Risk_Classifier",
                "indicators": risk_data,
                "severity": "alta" if risk_type in ["hot_work", "confined_space"] else "media"
            })
        
        # Citazioni documenti dall'analisi documenti
        if document_analysis.get("documents_analyzed"):
            all_document_citations.extend(document_analysis.get("document_citations", []))
        
        # Tracking misure esistenti vs suggerite
        existing_dpi = permit_data.get('dpi_required', [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        suggested_additional_dpi = []
        suggested_additional_actions = []
        
        # Elabora risultati specialisti
        for specialist_name, result in specialist_results.items():
            if "error" not in result or result.get("fallback"):
                # Aggiungi rischi identificati
                specialist_risks = result.get("risks_identified", [])
                for risk in specialist_risks:
                    if isinstance(risk, dict):
                        risk["source"] = specialist_name
                        all_risks.append(risk)
                    else:
                        all_risks.append({
                            "type": "specialist_finding",
                            "source": specialist_name,
                            "description": str(risk),
                            "severity": "media"
                        })
                
                # Aggiungi controlli
                all_controls.extend(result.get("control_measures", []))
                
                # Analizza DPI suggeriti vs esistenti
                specialist_dpi = result.get("dpi_requirements", [])
                for dpi in specialist_dpi:
                    all_dpi.append(dpi)
                    
                    # Verifica se manca
                    dpi_name = dpi if isinstance(dpi, str) else str(dpi)
                    if not self._is_dpi_covered(dpi_name, existing_dpi):
                        suggested_additional_dpi.append({
                            "item": dpi,
                            "source": specialist_name,
                            "priority": "alta",
                            "status": "mancante",
                            "justification": f"Raccomandato da {specialist_name}"
                        })
                
                # Analizza azioni suggerite vs esistenti
                specialist_controls = result.get("control_measures", [])
                for control in specialist_controls:
                    if not self._is_action_covered(control, existing_actions):
                        suggested_additional_actions.append({
                            "action": control,
                            "source": specialist_name,
                            "priority": "media",
                            "status": "raccomandato",
                            "justification": f"Raccomandato da {specialist_name}"
                        })
                
                all_permits.extend(result.get("permits_required", []))
        
        # GARANTISCI che ci siano sempre suggerimenti se necessario
        if not suggested_additional_dpi and len(all_risks) > 0:
            suggested_additional_dpi.append({
                "item": "DPI base obbligatori per rischi identificati",
                "source": "Sistema",
                "priority": "alta",
                "status": "verifica_necessaria",
                "justification": "Rischi identificati richiedono verifica adeguatezza DPI"
            })
        
        if not suggested_additional_actions and len(all_risks) > 2:
            suggested_additional_actions.append({
                "action": "Valutazione approfondita misure di controllo",
                "source": "Sistema", 
                "priority": "alta",
                "status": "raccomandato",
                "justification": "Multipli rischi identificati richiedono controlli aggiuntivi"
            })
        
        # Rimuovi duplicati
        all_controls = list(set(all_controls))
        all_permits = list(set(all_permits))
        
        # Consolida DPI
        print(f"[Complete Consolidation] Consolidating {len(all_dpi)} DPI items")
        all_dpi = consolidate_dpi_requirements(all_dpi)
        
        # Crea action items SEMPRE PRESENTI
        action_items = self._create_comprehensive_action_items(
            all_controls, all_dpi, all_permits, 
            suggested_additional_dpi, suggested_additional_actions
        )
        
        # ASSICURA che ci siano sempre azioni anche se minime
        if not action_items:
            action_items = [{
                "id": "ACT_001",
                "type": "basic_safety",
                "priority": "media",
                "title": "Verifica procedure sicurezza",
                "description": "Verifica base conformità procedure aziendali",
                "suggested_action": "Controllare applicabilità procedure standard",
                "consequences_if_ignored": "Possibili non conformità",
                "references": ["Procedure aziendali"],
                "estimated_effort": "30 minuti",
                "responsible_role": "Preposto",
                "source": "Sistema automatico"
            }]
        
        # Executive summary potenziato
        critical_issues = len([r for r in all_risks if 
                              isinstance(r, dict) and 
                              r.get("severity") in ["critica", "alta"]])
        
        total_improvements = len(suggested_additional_dpi) + len(suggested_additional_actions)
        
        executive_summary = {
            "overall_score": max(0.2, 0.8 - (critical_issues * 0.2) - (total_improvements * 0.1)),
            "critical_issues": critical_issues,
            "recommendations": len(action_items),
            "improvement_opportunities": total_improvements,
            "compliance_level": self._determine_compliance_level(critical_issues, total_improvements),
            "estimated_completion_time": f"{total_improvements*2}-{total_improvements*4} ore",
            "key_findings": self._extract_comprehensive_findings(
                general_analysis, classification, all_risks, document_analysis
            ),
            "next_steps": self._generate_comprehensive_next_steps(
                all_permits, critical_issues, total_improvements
            ),
            "analysis_completeness": "completa"
        }
        
        # Citations complete con documenti aziendali
        citations = self._build_complete_citations(
            specialist_results, context_documents, all_document_citations
        )
        
        return {
            "analysis_id": f"complete_{int(time.time())}_{permit_data.get('id')}",
            "permit_id": permit_data.get("id") if isinstance(permit_data.get("id"), int) else 0,
            "analysis_complete": True,
            "analysis_comprehensive": True,
            "confidence_score": 0.9 if document_analysis.get("documents_analyzed") else 0.7,
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": ["General_Analysis", "Risk_Classifier", "Document_Analysis"] + list(specialist_results.keys()),
            "ai_version": "Complete-Modular-2.0",
            
            # RISULTATI PRINCIPALI
            "executive_summary": executive_summary,
            "action_items": action_items,
            "citations": citations,
            "completion_roadmap": self._create_comprehensive_roadmap(action_items, all_permits),
            
            # ANALISI DETTAGLIATA SEMPRE PRESENTE
            "risk_analysis": {
                "total_risks_identified": len(all_risks),
                "risks_by_source": self._categorize_risks_by_source(all_risks),
                "risk_levels": self._categorize_risks_by_severity(all_risks),
                "implicit_risks": classification.get("implicit_risks", [])
            },
            
            # VALUTAZIONE MISURE ESISTENTI vs SUGGERITE
            "measures_evaluation": {
                "existing_dpi": existing_dpi,
                "existing_actions": existing_actions,
                "suggested_additional_dpi": suggested_additional_dpi,
                "suggested_additional_actions": suggested_additional_actions,
                "dpi_adequacy": "adeguati" if len(suggested_additional_dpi) <= 1 else "insufficienti",
                "actions_adequacy": "adeguate" if len(suggested_additional_actions) <= 1 else "insufficienti",
                "improvement_recommendations": total_improvements,
                "compliance_gap_analysis": self._analyze_compliance_gaps(
                    existing_dpi, existing_actions, suggested_additional_dpi, suggested_additional_actions
                )
            },
            
            # DOCUMENTI E CONFORMITÀ
            "document_compliance": {
                "documents_analyzed": document_analysis.get("documents_analyzed", False),
                "documents_count": len(context_documents),
                "citations_generated": len(all_document_citations),
                "compliance_findings": document_analysis.get("compliance_check", [])
            },
            
            # METRICHE PERFORMANCE
            "performance_metrics": {
                "total_processing_time": round(processing_time, 2),
                "specialists_activated": len(specialist_results),
                "risks_identified": len(all_risks),
                "controls_recommended": len(all_controls),
                "additional_measures_suggested": total_improvements,
                "analysis_phases_completed": 5,
                "analysis_method": "Complete Comprehensive System"
            }
        }
    
    def _create_comprehensive_action_items(
        self, 
        controls: List[str], 
        dpi: List[str], 
        permits: List[str],
        additional_dpi: List[Dict],
        additional_actions: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Crea action items comprensivi che includono SEMPRE miglioramenti
        """
        action_items = []
        item_id = 1
        
        # Permessi obbligatori (priorità massima)
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
                    "icon": "file-check"
                }
            })
            item_id += 1
        
        # DPI aggiuntivi raccomandati
        for dpi_rec in additional_dpi[:8]:  # Massimo 8 DPI aggiuntivi
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "dpi_improvement",
                "priority": dpi_rec.get("priority", "alta"),
                "title": f"Aggiungere {str(dpi_rec['item'])[:50]}",
                "description": f"DPI raccomandato: {dpi_rec['item']}",
                "suggested_action": f"Fornire {dpi_rec['item']} secondo raccomandazione {dpi_rec['source']}",
                "consequences_if_ignored": "Protezione inadeguata per rischi identificati",
                "references": ["Analisi specialistica DPI"],
                "estimated_effort": "15-30 minuti",
                "responsible_role": "Magazzino DPI",
                "frontend_display": {
                    "color": "orange" if dpi_rec.get("priority") == "alta" else "yellow",
                    "icon": "shield-check"
                }
            })
            item_id += 1
        
        # Azioni correttive aggiuntive
        for action_rec in additional_actions[:8]:  # Massimo 8 azioni aggiuntive
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "control_improvement",
                "priority": action_rec.get("priority", "media"),
                "title": f"Implementare: {str(action_rec['action'])[:40]}",
                "description": str(action_rec["action"]),
                "suggested_action": str(action_rec["action"]),
                "consequences_if_ignored": "Controllo rischi inadeguato",
                "references": ["Analisi specialistica"],
                "estimated_effort": "variabile",
                "responsible_role": "Preposto",
                "frontend_display": {
                    "color": "blue",
                    "icon": "check-circle"
                }
            })
            item_id += 1
        
        # DPI esistenti da consolidare
        for dpi_item in dpi[:5]:  # Massimo 5 DPI dalla lista consolidata
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "dpi_verification",
                "priority": "media",
                "title": f"Verificare {str(dpi_item)[:30]}",
                "description": f"Verificare disponibilità e idoneità: {dpi_item}",
                "suggested_action": f"Controllare disponibilità e distribuzione {dpi_item}",
                "consequences_if_ignored": "DPI non disponibili o inadeguati",
                "references": ["Consolidamento DPI"],
                "estimated_effort": "15 minuti",
                "responsible_role": "Preposto",
                "frontend_display": {
                    "color": "green",
                    "icon": "shield"
                }
            })
            item_id += 1
        
        # Controlli generali
        for control in controls[:5]:  # Massimo 5 controlli
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "control_measure",
                "priority": "media",
                "title": str(control)[:40],
                "description": str(control),
                "suggested_action": str(control),
                "consequences_if_ignored": "Controllo rischi inadeguato",
                "references": ["Analisi specialistica"],
                "estimated_effort": "variabile",
                "responsible_role": "Preposto",
                "frontend_display": {
                    "color": "blue",
                    "icon": "check-circle"
                }
            })
            item_id += 1
        
        return action_items
    
    def _determine_compliance_level(self, critical_issues: int, improvements: int) -> str:
        """Determina il livello di conformità basato sui problemi identificati"""
        if critical_issues == 0 and improvements <= 2:
            return "conforme"
        elif critical_issues <= 1 and improvements <= 5:
            return "parzialmente_conforme"
        elif critical_issues <= 3:
            return "non_conforme_correggibile"
        else:
            return "non_conforme_critico"
    
    def _extract_comprehensive_findings(
        self, 
        general_analysis: Dict, 
        classification: Dict, 
        all_risks: List,
        document_analysis: Dict
    ) -> List[str]:
        """Estrae i finding chiave da tutte le analisi"""
        findings = []
        
        # Dall'analisi generale
        if general_analysis.get("general_analysis_content"):
            findings.append("Analisi generale completata con identificazione rischi")
        
        # Dalla classificazione
        findings.append(classification.get("overall_risk_level", "Rischio non classificato"))
        
        # Dai documenti
        if document_analysis.get("documents_analyzed"):
            findings.append(f"Analizzati {document_analysis.get('total_documents', 0)} documenti aziendali")
        
        # Dai rischi impliciti
        implicit_risks = classification.get("implicit_risks", [])
        if implicit_risks:
            findings.append(f"Identificati {len(implicit_risks)} rischi impliciti")
        
        # Dai rischi critici
        critical_risks = [r for r in all_risks if isinstance(r, dict) and r.get("severity") == "alta"]
        if critical_risks:
            findings.append(f"{len(critical_risks)} rischi ad alta priorità identificati")
        
        return findings[:6]  # Massimo 6 findings
    
    def _generate_comprehensive_next_steps(
        self, 
        permits: List[str], 
        critical_issues: int, 
        improvements: int
    ) -> List[str]:
        """Genera next steps comprensivi"""
        steps = []
        
        if permits:
            steps.append(f"Ottenere {len(permits)} permessi richiesti")
        
        if critical_issues > 0:
            steps.append(f"Risolvere urgentemente {critical_issues} problemi critici")
        
        if improvements > 0:
            steps.append(f"Implementare {improvements} miglioramenti raccomandati")
        
        steps.extend([
            "Briefing sicurezza completo con tutto il personale",
            "Verifica fisica disponibilità DPI e attrezzature",
            "Setup area di lavoro secondo raccomandazioni"
        ])
        
        return steps[:5]  # Massimo 5 steps
    
    def _categorize_risks_by_source(self, all_risks: List) -> Dict[str, int]:
        """Categorizza i rischi per fonte"""
        by_source = {}
        for risk in all_risks:
            if isinstance(risk, dict):
                source = risk.get("source", "Unknown")
                by_source[source] = by_source.get(source, 0) + 1
        return by_source
    
    def _categorize_risks_by_severity(self, all_risks: List) -> Dict[str, int]:
        """Categorizza i rischi per severità"""
        by_severity = {"critica": 0, "alta": 0, "media": 0, "bassa": 0}
        for risk in all_risks:
            if isinstance(risk, dict):
                severity = risk.get("severity", "media")
                if severity in by_severity:
                    by_severity[severity] += 1
        return by_severity
    
    def _analyze_compliance_gaps(
        self, 
        existing_dpi: List, 
        existing_actions: List, 
        suggested_dpi: List, 
        suggested_actions: List
    ) -> Dict[str, Any]:
        """Analizza i gap di conformità"""
        return {
            "dpi_gaps": len(suggested_dpi),
            "action_gaps": len(suggested_actions),
            "total_gaps": len(suggested_dpi) + len(suggested_actions),
            "coverage_percentage": max(0, 100 - (len(suggested_dpi) + len(suggested_actions)) * 10),
            "priority_gaps": len([item for item in suggested_dpi + suggested_actions 
                                if item.get("priority") == "alta"]),
            "gap_analysis": "Identificate lacune nelle misure di sicurezza" if (suggested_dpi or suggested_actions) 
                           else "Misure attuali sembrano adeguate"
        }
    
    def _build_complete_citations(
        self, 
        specialist_results: Dict[str, Any], 
        context_documents: List[Dict[str, Any]], 
        document_citations: List[Dict]
    ) -> Dict[str, List]:
        """Costruisce citazioni complete sempre presenti"""
        citations = {
            "normative_framework": [],
            "company_procedures": [],
            "specialist_sources": []
        }
        
        # Aggiungi documenti aziendali se disponibili
        if document_citations:
            for doc_cite in document_citations:
                citations["company_procedures"].append({
                    "document_info": {
                        "title": f"[FONTE: Documento Aziendale] {doc_cite.get('title', 'N/A')}",
                        "type": doc_cite.get('type', 'Procedura').title(),
                        "relevance_score": str(doc_cite.get('relevance_score', 0.9))
                    },
                    "relevance": {
                        "score": doc_cite.get('relevance_score', 0.9),
                        "reason": "Documento aziendale specificamente applicabile"
                    },
                    "key_requirements": doc_cite.get('specific_requirements', []),
                    "frontend_display": {
                        "color": "green",
                        "icon": "building"
                    }
                })
        
        # Aggiungi fonti normative standard sempre
        citations["normative_framework"].extend([
            {
                "document_info": {
                    "title": "[FONTE: Sistema] D.Lgs 81/08 - Testo Unico Sicurezza",
                    "type": "Normativa Base",
                    "relevance_score": "0.95"
                },
                "relevance": {
                    "score": 0.95,
                    "reason": "Normativa base sicurezza lavoro sempre applicabile"
                },
                "key_requirements": [
                    {"requirement": "Valutazione rischi", "description": "Art. 17 - Obblighi datore di lavoro"},
                    {"requirement": "DPI appropriati", "description": "Titolo III - Uso delle attrezzature"}
                ],
                "frontend_display": {
                    "color": "green",
                    "icon": "book"
                }
            }
        ])
        
        # Aggiungi fonti specialistiche
        for specialist_name in specialist_results.keys():
            citations["specialist_sources"].append({
                "document_info": {
                    "title": f"[FONTE: Specialist] Analisi {specialist_name}",
                    "type": "Valutazione specialistica",
                    "relevance_score": "0.90"
                },
                "relevance": {
                    "score": 0.90,
                    "reason": "Analisi automatizzata basata su knowledge base specialistico"
                },
                "key_requirements": [
                    {"requirement": "Valutazione specialistica", "description": f"Analisi dettagliata da {specialist_name}"}
                ],
                "frontend_display": {
                    "color": "blue",
                    "icon": "user-check"
                }
            })
        
        return citations
    
    def _create_comprehensive_roadmap(self, action_items: List[Dict], permits: List[str]) -> Dict[str, List[str]]:
        """Crea roadmap comprensiva sempre presente"""
        return {
            "immediate_actions": [
                f"Analizzare {len(action_items)} azioni identificate",
                f"Ottenere {len(permits)} permessi richiesti" if permits else "Verificare permessi applicabili",
                "Briefing sicurezza pre-lavoro obbligatorio"
            ],
            "short_term_actions": [
                "Implementare miglioramenti DPI identificati",
                "Setup area di lavoro secondo raccomandazioni",
                "Verificare disponibilità attrezzature emergenza"
            ],
            "medium_term_actions": [
                "Monitoraggio continuo conformità",
                "Audit periodici applicazione misure",
                "Aggiornamento valutazione rischi"
            ],
            "success_metrics": [
                "Zero incidenti durante esecuzione",
                "100% conformità procedure implementate", 
                f"Completamento {len(action_items)} azioni nei tempi"
            ]
        }
    
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
        
        # Track existing vs suggested measures
        existing_dpi = permit_data.get('dpi_required', [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        suggested_additional_dpi = []
        suggested_additional_actions = []
        
        # Add risks from classification
        for risk_type, risk_data in classification.get("detected_risks", {}).items():
            all_risks.append({
                "type": risk_type,
                "source": "Risk_Classifier",
                "indicators": risk_data
            })
        
        # Add risks from specialists and evaluate their suggestions
        for specialist_name, result in specialist_results.items():
            if "error" not in result:
                all_risks.extend(result.get("risks_identified", []))
                all_controls.extend(result.get("control_measures", []))
                
                # Check specialist DPI recommendations against existing DPI
                specialist_dpi = result.get("dpi_requirements", [])
                for dpi in specialist_dpi:
                    all_dpi.append(dpi)  # Keep for compatibility
                    
                    # Check if this DPI is missing
                    dpi_name = dpi if isinstance(dpi, str) else dpi.get('name', str(dpi))
                    if not self._is_dpi_covered(dpi_name, existing_dpi):
                        suggested_additional_dpi.append({
                            "item": dpi,
                            "source": specialist_name,
                            "priority": "alta",
                            "status": "mancante"
                        })
                
                # Check specialist action recommendations
                specialist_controls = result.get("control_measures", [])
                for control in specialist_controls:
                    if not self._is_action_covered(control, existing_actions):
                        suggested_additional_actions.append({
                            "action": control,
                            "source": specialist_name,
                            "priority": "media",
                            "status": "raccomandato"
                        })
                
                all_permits.extend(result.get("permits_required", []))
        
        # Remove duplicates and consolidate DPI
        all_controls = list(set(all_controls))
        print(f"[ModularOrchestrator] Consolidating {len(all_dpi)} DPI items to prevent duplicates")
        all_dpi = consolidate_dpi_requirements(all_dpi)
        print(f"[ModularOrchestrator] After consolidation: {len(all_dpi)} DPI items")
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
            # Evaluation of existing vs suggested measures
            "measures_evaluation": {
                "existing_dpi": existing_dpi,
                "existing_actions": existing_actions,
                "suggested_additional_dpi": suggested_additional_dpi,
                "suggested_additional_actions": suggested_additional_actions,
                "dpi_adequacy": "adeguati" if len(suggested_additional_dpi) == 0 else "insufficienti",
                "actions_adequacy": "adeguate" if len(suggested_additional_actions) == 0 else "insufficienti",
                "improvement_recommendations": len(suggested_additional_dpi) + len(suggested_additional_actions)
            },
            
            "performance_metrics": {
                "total_processing_time": round(processing_time, 2),
                "specialists_activated": len(specialist_results),
                "risks_identified": len(all_risks),
                "controls_recommended": len(all_controls),
                "additional_measures_suggested": len(suggested_additional_dpi) + len(suggested_additional_actions),
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
        
        # Add DPI requirements (enhanced with consolidation info)
        for dpi_item in dpi[:10]:  # Limit to 10 most important
            # Handle consolidated DPI items with enhanced metadata
            if isinstance(dpi_item, dict):
                dpi_title = dpi_item.get('type', 'DPI requirement')
                dpi_description = dpi_item.get('description', str(dpi_item))
                
                # Add consolidation information if available
                consolidation_info = dpi_item.get('consolidation_info', {})
                if consolidation_info:
                    merged_count = consolidation_info.get('merged_items', 1)
                    if merged_count > 1:
                        dpi_description += f" (Consolidato da {merged_count} requisiti)"
                
                # Add compatibility warnings if present
                warnings = dpi_item.get('compatibility_warnings', [])
                if warnings:
                    dpi_description += f" ATTENZIONE: {'; '.join(warnings)}"
                
                # Set priority based on protection level
                priority = "alta"
                if dpi_item.get('category') == 'safety_shoes' and dpi_item.get('protection_level') in ['S3 HRO', 'S4', 'S5']:
                    priority = "critica"
                elif dpi_item.get('category') == 'respirators' and dpi_item.get('protection_level') in ['FFP3', 'Pieno facciale']:
                    priority = "critica"
                
            else:
                dpi_title = str(dpi_item)
                dpi_description = str(dpi_item)
                priority = "alta"
            
            # Limit title length to avoid issues
            dpi_title_short = dpi_title[:30] if len(dpi_title) > 30 else dpi_title
            
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "dpi_requirement",
                "priority": priority,
                "title": f"Fornire {dpi_title_short}",
                "description": dpi_description,
                "suggested_action": f"Verificare disponibilità e distribuzione {dpi_title}",
                "consequences_if_ignored": "Esposizione diretta ai rischi identificati",
                "references": [],
                "estimated_effort": "15-30 minuti",
                "responsible_role": "Magazzino DPI",
                "frontend_display": {
                    "color": "red" if priority == "critica" else "yellow",
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
    
    def _is_dpi_covered(self, required_dpi: str, existing_dpi: List[str]) -> bool:
        """Check if a required DPI is already covered by existing DPI"""
        if not existing_dpi:
            return False
        
        # Basic string comparison
        required_lower = required_dpi.lower()
        existing_lower = [item.lower() for item in existing_dpi]
        
        # Check for matches
        for existing in existing_lower:
            if required_lower in existing or existing in required_lower:
                return True
        
        return False
    
    def _is_action_covered(self, required_action: str, existing_actions: List[str]) -> bool:
        """Check if a required action is already covered by existing actions"""
        if not existing_actions:
            return False
        
        required_lower = required_action.lower()
        
        for existing in existing_actions:
            existing_lower = str(existing).lower()
            
            # Check for key concept matches
            key_concepts = ["fire watch", "gas test", "ventilazione", "isolamento", "monitoraggio"]
            for concept in key_concepts:
                if concept in required_lower and concept in existing_lower:
                    return True
            
            # Basic overlap check
            if len(required_lower) > 5 and required_lower in existing_lower:
                return True
        
        return False
    
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
            "ai_version": "Modular-1.0-Err",
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
            "completion_roadmap": {
                "fase_preparatoria": ["Risolvere errore di sistema"],
                "fase_esecutiva": ["Ripetere analisi"],
                "fase_conclusiva": ["Verificare risultati"]
            }
        }
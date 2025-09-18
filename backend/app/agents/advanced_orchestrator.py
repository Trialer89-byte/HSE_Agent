"""
Advanced HSE Orchestrator - Simplified Architecture
Direct orchestrator with risk analysis and specialist coordination
"""

import asyncio
from typing import Dict, Any, List, Optional
import time
from datetime import datetime

from .specialists import get_all_specialists


class AdvancedHSEOrchestrator:
    """
    Simplified 2-step orchestrator:
    1. Risk Analysis & Classification with Unified Risk Classifier
    2. Specialist Agent Selection & Interaction with direct output
    """
    
    def __init__(
        self,
        user_context: Dict[str, Any] = None,
        vector_service=None
    ):
        self.user_context = user_context or {}
        self.vector_service = vector_service
        self.specialists = get_all_specialists()
        print(f"[AdvancedOrchestrator] Available specialists: {list(self.specialists.keys())}")
        
        self.unified_risk_classifier = self.specialists.get("unified_risk_classifier")
        print(f"[AdvancedOrchestrator] Unified Risk Classifier initialized: {self.unified_risk_classifier is not None}")
        if self.unified_risk_classifier:
            print(f"[AdvancedOrchestrator] Unified Risk Classifier type: {type(self.unified_risk_classifier)}")
        
        
        # Inject vector service into all specialists
        if vector_service:
            for specialist in self.specialists.values():
                specialist.vector_service = vector_service
            print(f"[AdvancedOrchestrator] Injected vector service into {len(self.specialists)} specialists")
        
        print(f"[AdvancedOrchestrator] Initialized with simplified 2-step process")
    
    async def analyze_permit_advanced(
        self, 
        permit_data: Dict[str, Any], 
        permit_metadata: Dict[str, Any] = None,
        context_documents: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simplified 2-step analysis process:
        1. Risk Analysis & Classification with Unified Risk Classifier
        2. Specialist Agent Selection & Interaction with direct output

        Args:
            permit_data: Basic permit data (title, description, etc.)
            permit_metadata: Extended metadata from PostgreSQL (risks, controls, history)
            context_documents: Pre-fetched documents from Weaviate
        """
        start_time = time.time()
        context_documents = context_documents or []
        permit_metadata = permit_metadata or {}
        
        # Initialize step timing tracking
        step_timings = {}
        
        try:
            print(f"\n[AdvancedOrchestrator] Starting simplified 2-step analysis for permit {permit_data.get('id')}")

            # STEP 1: Work permit risk analysis with unified risk classifier
            print("[AdvancedOrchestrator] STEP 1: Work permit risk analysis with unified risk classifier")
            step1_start = time.time()
            classification_result = await self._step1_risk_analysis(
                permit_data, 
                permit_metadata,
                context_documents
            )
            step_timings["step1_risk_analysis"] = round(time.time() - step1_start, 2)
            print(f"[AdvancedOrchestrator] STEP 1 completed in {step_timings['step1_risk_analysis']}s")
            
            if not classification_result.get("classification_complete"):
                return self._create_error_result("Step 1 - Risk analysis failed", start_time)
            
            # STEP 2: Specialist agent selection and interaction
            print("[AdvancedOrchestrator] STEP 2: Specialist agent selection and interaction")
            step2_start = time.time()
            specialists_to_run = classification_result.get("specialists_to_activate", [])
            print(f"  Selected specialists: {specialists_to_run}")
            
            specialist_results = await self._step2_specialist_interaction(
                permit_data,
                permit_metadata,
                classification_result,
                specialists_to_run,
                context_documents
            )
            step_timings["step2_specialist_analysis"] = round(time.time() - step2_start, 2)
            print(f"[AdvancedOrchestrator] STEP 2 completed in {step_timings['step2_specialist_analysis']}s")
            
            # STEP 2 COMPLETE: Build final result directly from specialist results
            print("[AdvancedOrchestrator] Building final result directly from specialist results")
            step4_start = time.time()
            final_result = self._build_final_result(
                permit_data,
                permit_metadata,
                classification_result,
                specialist_results,
                {},  # DPI functionality moved to specialists, so pass empty dict
                context_documents,
                time.time() - start_time,
                step_timings
            )
            step_timings["final_output_generation"] = round(time.time() - step4_start, 2)
            print(f"[AdvancedOrchestrator] Final output generation completed in {step_timings['final_output_generation']}s")

            total_time = round(time.time() - start_time, 2)
            print(f"[AdvancedOrchestrator] Simplified 2-step analysis completed in {total_time}s")
            print(f"[AdvancedOrchestrator] Step breakdown: {step_timings}")
            
            return final_result
            
        except Exception as e:
            print(f"[AdvancedOrchestrator] Error during simplified analysis: {e}")
            import traceback
            traceback.print_exc()

            # Enhanced error tracking to identify which step failed
            error_context = f"Error in permit {permit_data.get('id', 'unknown')}: {str(e)}"
            return self._create_error_result(error_context, start_time)
    
    async def _step1_risk_analysis(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        STEP 1: Comprehensive risk analysis and classification
        Read all permit fields, identify declared and undeclared risks using risk classifier
        """

        print(f"[AdvancedOrchestrator] Starting risk analysis for permit {permit_data.get('id')}")

        # Validate permit data before analysis
        try:
            self._validate_permit_data(permit_data)
        except Exception as e:
            print(f"[AdvancedOrchestrator] Permit data validation failed: {e}")
            raise ValueError(f"Invalid permit data for permit {permit_data.get('id', 'unknown')}: {e}")

        # Build enhanced context with full permit analysis
        enhanced_context = {
            "documents": context_documents,
            "user_context": self.user_context,
            "permit_metadata": permit_metadata,
            "historical_risks": permit_metadata.get("historical_risks", []),
            "previous_incidents": permit_metadata.get("previous_incidents", []),
            "site_specific_risks": permit_metadata.get("site_specific_risks", []),
            "equipment_risks": permit_metadata.get("equipment_risks", [])
        }
        
        # COMPREHENSIVE PERMIT ANALYSIS - Read all fields
        print(f"[AdvancedOrchestrator] Reading all permit fields for comprehensive analysis:")
        print(f"  - Title: {permit_data.get('title', 'N/A')}")
        print(f"  - Description: {permit_data.get('description', 'N/A')}")
        print(f"  - Work Type: {permit_data.get('work_type', 'N/A')}")
        print(f"  - Location: {permit_data.get('location', 'N/A')}")
        print(f"  - Existing DPI: {permit_data.get('dpi_required', [])}")
        print(f"  - Existing Actions: {permit_data.get('risk_mitigation_actions', [])}")
        print(f"  - Custom Fields: {permit_data.get('custom_fields', {})}")
        
        # Use Unified Risk Classifier for intelligent risk detection and specialist activation
        unified_analysis_result = None
        print(f"[AdvancedOrchestrator] DEBUG: unified_risk_classifier is {type(self.unified_risk_classifier) if self.unified_risk_classifier else 'None'}")
        if self.unified_risk_classifier:
            print(f"[AdvancedOrchestrator] Using Unified Risk Classifier for intelligent risk detection and specialist activation")
            unified_analysis_result = await self.unified_risk_classifier.analyze(permit_data, enhanced_context)
            
            # Extract risk information from unified analysis result
            detected_risks = unified_analysis_result.get("detected_risks", {})
            identified_risks = unified_analysis_result.get("identified_risks_for_specialists", [])
            
            print(f"  [UnifiedRiskClassifier] Detected {len(detected_risks)} risks: {list(detected_risks.keys())}")
            print(f"  [UnifiedRiskClassifier] {len(identified_risks)} risks for specialists")
            
            # Log risk combinations if any
            risk_combinations = unified_analysis_result.get("risk_combinations", [])
            if risk_combinations:
                print(f"  [UnifiedRiskClassifier] Found {len(risk_combinations)} critical risk combinations")
                for combo in risk_combinations:
                    print(f"    - {combo.get('severity', '').upper()}: {combo.get('description', '')}")
        else:
            print("[AdvancedOrchestrator] ERROR: Unified Risk Classifier not available")
            return {"classification_complete": False, "error": "Unified Risk Classifier not initialized"}
        
        # Build classification result using Unified Risk Classifier results
        print(f"[AdvancedOrchestrator] STEP 1: Building classification from Unified Risk Classifier")
        
        # Add evaluation of existing DPI and mitigation actions
        existing_dpi = permit_data.get('dpi_required', [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        
        # COMPLETENESS EVALUATION
        completeness_score = self._evaluate_permit_completeness(permit_data)
        print(f"[AdvancedOrchestrator] Permit completeness score: {completeness_score}/10")
        
        classification = {
            "permit_completeness": {
                "score": completeness_score,
                "missing_elements": self._identify_missing_elements(permit_data),
                "adequacy_assessment": self._assess_measures_adequacy(permit_data, unified_analysis_result)
            }
        }
        
        if existing_dpi or existing_actions:
            print(f"[AdvancedOrchestrator] Found existing DPI: {len(existing_dpi)} items, Actions: {len(existing_actions)} items")
            classification["existing_measures"] = {
                "dpi_provided": existing_dpi,
                "actions_provided": existing_actions,
                "evaluation_mode": "enhancement"  # Indicates we should enhance/correct existing measures
            }
        
        # Get specialists to activate from Unified Risk Classifier results
        if unified_analysis_result and unified_analysis_result.get("specialists_to_activate"):
            specialists_to_activate = unified_analysis_result["specialists_to_activate"]
            print(f"[AdvancedOrchestrator] Unified Risk Classifier recommends {len(specialists_to_activate)} specialists: {specialists_to_activate}")
        else:
            print("[AdvancedOrchestrator] Warning: No Unified Risk Classifier results, using mechanical and DPI evaluator")
            specialists_to_activate = ["mechanical", "dpi_evaluator"]
        
        total_risks = 0
        if unified_analysis_result:
            detected_risks = unified_analysis_result.get("detected_risks", {})
            total_risks = len(detected_risks)
        
        print(f"[AdvancedOrchestrator] STEP 1 Complete - Identified {total_risks} risk types, activating {len(specialists_to_activate)} specialists")
        
        classification["specialists_to_activate"] = specialists_to_activate
        classification["classification_complete"] = True
        
        # Add unified risk classification results
        if unified_analysis_result:
            classification["risk_mapping"] = unified_analysis_result.get("risk_mapping", {})
            classification["unified_analysis"] = {
                "classification_complete": unified_analysis_result.get("classification_complete", False),
                "detected_risks": unified_analysis_result.get("detected_risks", {}),
                "identified_risks_for_specialists": unified_analysis_result.get("identified_risks_for_specialists", []),
                "risk_combinations": unified_analysis_result.get("risk_combinations", []),
                "overall_risk_level": unified_analysis_result.get("overall_risk_level", "MEDIUM"),
                "analysis_confidence": unified_analysis_result.get("analysis_confidence", 0.8),
                "comprehensive_analysis": unified_analysis_result.get("comprehensive_analysis", {})
            }
        
        # Store context for next steps
        classification["documents"] = context_documents
        classification["permit_metadata"] = permit_metadata
        
        return classification
    
    async def _step2_specialist_interaction(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification: Dict[str, Any],
        specialists_to_run: List[str],
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        STEP 2: Specialist agent selection and interaction
        - Run selected specialists in parallel
        - Allow specialists to interact and use both PostgreSQL and Weaviate
        - Enforce mandatory document control on internal regulations and operational instructions
        """
        
        results = {}
        tasks = []
        
        # Map available specialist types according to requirements
        specialist_mapping = {
            "chemical": "🧪 **Chemical Safety Agent** - Esperto in sostanze chimiche e procedure REACH",
            "electrical": "⚡ **Electrical Safety Agent** - Specialista sicurezza elettrica e cablaggi",
            "height": "🏗️ **Height Work Agent** - Esperto lavori in altezza e DPI anticaduta", 
            "hot_work": "🔥 **Hot Work Agent** - Specialista saldatura e lavori a caldo",
            "confined_space": "🚪 **Confined Space Agent** - Esperto spazi confinati e atmosphere",
            "mechanical": "🔧 **Mechanical Specialist** - Sicurezza meccanica e macchinari",
            "dpi_evaluator": "🛡️ **DPI Evaluator** - Valutatore dispositivi di protezione individuale"
        }
        
        # Run all specialists in parallel - DPI specialist now works independently
        for specialist_name in specialists_to_run:
            clean_name = specialist_name.replace("_specialist", "")
            
            specialist = self.specialists.get(clean_name)
            if specialist and specialist.name != "Risk_Classifier":
                # All specialists use standard document control - DPI gets risk info from classification
                task = self._run_specialist_with_document_control(
                    specialist,
                    permit_data,
                    permit_metadata,
                    classification,
                    context_documents
                )
                tasks.append((specialist.name, task))
                print(f"  Activating: {specialist_mapping.get(clean_name, specialist.name)}")
        
        # Execute specialists with interaction capability
        if tasks:
            print(f"  Running {len(tasks)} specialists with document control and interaction...")
            specialist_outputs = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            for i, (name, _) in enumerate(tasks):
                if not isinstance(specialist_outputs[i], Exception):
                    results[name] = specialist_outputs[i]
                    print(f"    ✓ {name} completed with document verification")
                else:
                    print(f"    ✗ {name} failed: {specialist_outputs[i]}")
                    results[name] = {"error": str(specialist_outputs[i])}
            
        print(f"[AdvancedOrchestrator] STEP 2 Complete - {len(results)} specialists provided analysis")
        return results
    
    async def _run_specialist_with_document_control(
        self,
        specialist,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification: Dict[str, Any],
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Run specialist with mandatory document control and external API access
        - Specialists must check internal regulations and operational instructions
        - Can use both PostgreSQL and Weaviate for document retrieval
        - Must cite sources for all recommendations
        """
        
        # Enhanced context with document control requirements
        context = {
            "classification": classification,
            "user_context": self.user_context,
            "documents": context_documents,
            "permit_metadata": permit_metadata,
            "equipment_list": permit_metadata.get("equipment_list", []),
            "chemical_list": permit_metadata.get("chemical_list", []),
            "document_control_required": True,  # Mandatory document verification
            "available_document_sources": ["PostgreSQL", "Weaviate", "External_API"],
            "citation_required": True,  # Must cite all sources
            "historical_data": {
                "previous_permits": permit_metadata.get("previous_permits", []),
                "incidents": permit_metadata.get("incidents", []),
                "near_misses": permit_metadata.get("near_misses", [])
            },
            "interaction_enabled": True  # Specialists can interact with each other
        }
        
        # Run specialist analysis with enhanced context
        try:
            result = await specialist.analyze(permit_data, context)
        except Exception as e:
            error_msg = f"Specialist {specialist.name} analysis failed: {str(e)}"
            print(f"[AdvancedOrchestrator] {error_msg}")
            
            # Return structured error response with actual error details
            result = {
                "error": error_msg,
                "specialist": specialist.name,
                "error_type": type(e).__name__,
                "analysis_status": "failed",
                "risks_identified": [],
                "recommended_actions": [],
                "dpi_requirements": [],
                "ai_analysis_used": False
            }
        
        # Verify document citations are present - MANDATORY for all specialists
        if not result.get("citations") and not result.get("error"):
            result["warning"] = "Specialist did not provide required document citations"
            print(f"[{self.__class__.__name__}] WARNING: {specialist.name} did not provide citations for document traceability")

        # Validate Weaviate usage - MANDATORY for all specialists before suggesting actions
        elif result.get("citations") and not result.get("error"):
            if hasattr(specialist, 'validate_weaviate_usage'):
                weaviate_validation = specialist.validate_weaviate_usage(result["citations"])
                result["weaviate_validation"] = weaviate_validation

                if weaviate_validation["compliance"] == "NON_COMPLIANT":
                    result["warning"] = weaviate_validation["warning"]
                    print(f"[{self.__class__.__name__}] WEAVIATE WARNING: {specialist.name} - {weaviate_validation['warning']}")
                else:
                    print(f"[{self.__class__.__name__}] WEAVIATE ✅: {specialist.name} used {weaviate_validation['weaviate_count']} Weaviate documents")
        
        # Add metadata enhancements
        if permit_metadata.get("site_specific_controls"):
            result["site_specific_controls"] = permit_metadata["site_specific_controls"]
        
        if permit_metadata.get("mandatory_ppe"):
            existing_ppe = result.get("dpi_requirements", [])
            result["dpi_requirements"] = list(set(existing_ppe + permit_metadata["mandatory_ppe"]))
        
        return result
    
    
    
    
    
    

    def _convert_criticality_to_priority(self, criticality: str) -> str:
        """
        Convert AI-generated criticality to frontend priority
        Maps criticality levels from specialists to frontend display priorities
        """
        if not criticality:
            return "media"

        criticality_lower = str(criticality).lower()

        # Map criticality to priority - both English and Italian terms supported
        if criticality_lower in ["critica", "critical"]:
            return "alta"
        elif criticality_lower in ["alta", "high"]:
            return "alta"
        elif criticality_lower in ["media", "medium"]:
            return "media"
        elif criticality_lower in ["bassa", "low"]:
            return "bassa"
        else:
            # Default fallback
            return "media"

    
    def _find_dpi_citation(self, dpi_text: str, classification: Dict[str, Any]) -> Dict[str, str]:
        """Trova citazione documentale per il DPI"""
        if "guant" in dpi_text.lower():
            if "elettric" in dpi_text.lower():
                return {
                    "document": "EN 60903",
                    "requirement": "Guanti per lavori elettrici"
                }
            elif "taglio" in dpi_text.lower():
                return {
                    "document": "EN 388",
                    "requirement": "Protezione antitaglio"
                }
        elif "occhial" in dpi_text.lower():
            return {
                "document": "EN 166",
                "requirement": "Protezione occhi"
            }
        elif "respirator" in dpi_text.lower():
            return {
                "document": "EN 149",
                "requirement": "Protezione respiratoria"
            }
        return None
    
    
    def _get_dpi_justification(self, dpi_text: str, classification: Dict[str, Any]) -> str:
        """Fornisce giustificazione per il DPI usando risk mapping results"""
        detected_risks = {}
        if classification.get("risk_mapping"):
            detected_risks = classification["risk_mapping"].get("detected_risks", {})
        
        if "elettric" in dpi_text.lower() and "electrical" in detected_risks:
            return "Richiesto per lavori su impianti elettrici identificati"
        elif "taglio" in dpi_text.lower() and "mechanical" in detected_risks:
            return "Necessario per protezione da rischi meccanici/taglio"
        elif "chimico" in dpi_text.lower() and "chemical" in detected_risks:
            return "Protezione da esposizione a sostanze chimiche"
        elif detected_risks:
            risk_types = list(detected_risks.keys())
            return f"Raccomandato per mitigazione rischi identificati: {', '.join(risk_types)}"
        else:
            return "Raccomandato per mitigazione rischi identificati"
    
    def _categorize_dpi(self, dpi_text: str) -> str:
        """Categorizza il DPI"""
        dpi_lower = dpi_text.lower()
        if "guant" in dpi_lower:
            return "Protezione mani"
        elif "occhial" in dpi_lower:
            return "Protezione occhi"
        elif "casco" in dpi_lower:
            return "Protezione testa"
        elif "scarpe" in dpi_lower:
            return "Protezione piedi"
        elif "respirator" in dpi_lower or "ffp" in dpi_lower:
            return "Protezione respiratoria"
        elif "tuta" in dpi_lower:
            return "Protezione corpo"
        else:
            return "Altro DPI"
    
    def _create_dpi_summary(self, to_add: List[Dict], to_modify: List[Dict], existing: List[str]) -> str:
        """Crea sommario delle modifiche DPI"""
        summary_parts = []
        
        if existing:
            summary_parts.append(f"DPI attuali: {len(existing)}")
        if to_add:
            summary_parts.append(f"Da aggiungere: {len(to_add)}")
        if to_modify:
            summary_parts.append(f"Da modificare: {len(to_modify)}")
        
        return " | ".join(summary_parts) if summary_parts else "Nessuna modifica DPI necessaria"
    
    # Utility methods (simplified versions)
    def _evaluate_permit_completeness(self, permit_data: Dict[str, Any]) -> int:
        """Basic completeness evaluation"""
        score = 0
        if permit_data.get('title') and len(permit_data.get('title', '')) > 5:
            score += 2
        if permit_data.get('description') and len(permit_data.get('description', '')) > 20:
            score += 2
        if permit_data.get('work_type'):
            score += 2
        if permit_data.get('dpi_required') and len(permit_data.get('dpi_required', [])) > 0:
            score += 2
        if permit_data.get('risk_mitigation_actions') and len(permit_data.get('risk_mitigation_actions', [])) > 0:
            score += 2
        return min(10, score)
    
    def _identify_missing_elements(self, permit_data: Dict[str, Any]) -> List[str]:
        """Identify missing elements"""
        missing = []
        if not permit_data.get('title') or len(permit_data.get('title', '')) < 5:
            missing.append("Titolo dettagliato")
        if not permit_data.get('description') or len(permit_data.get('description', '')) < 20:
            missing.append("Descrizione dettagliata")
        
        # Check for DPI in both dpi_required field and custom_fields.safety_requirements
        dpi_in_field = permit_data.get('dpi_required') and len(permit_data.get('dpi_required', [])) > 0
        custom_fields = permit_data.get('custom_fields', {})
        dpi_in_safety_requirements = custom_fields.get('safety_requirements') and len(custom_fields.get('safety_requirements', '').strip()) > 0
        
        if not dpi_in_field and not dpi_in_safety_requirements:
            missing.append("DPI richiesti")
        
        return missing
    
    def _assess_measures_adequacy(self, permit_data: Dict[str, Any], unified_analysis_result: Dict[str, Any]) -> Dict[str, str]:
        """Basic adequacy assessment using unified analysis results"""
        assessment = {}
        
        # Get detected risks from unified analysis
        if unified_analysis_result:
            detected_risks = unified_analysis_result.get("detected_risks", {})
            for risk_type, risk_data in detected_risks.items():
                confidence = risk_data.get("confidence", 0)
                if confidence > 0.5:
                    assessment[risk_type] = "da_verificare"
                else:
                    assessment[risk_type] = "bassa_priorità"
            
            # Check risk combinations for higher priority
            risk_combinations = unified_analysis_result.get("risk_combinations", [])
            for combo in risk_combinations:
                if combo.get("severity") == "critical":
                    for risk in combo.get("combination", []):
                        assessment[risk] = "critico"
        
        return assessment
    
    
    
    def _create_citations(self, context_documents: List[Dict[str, Any]], permit_metadata: Dict[str, Any]) -> Dict[str, List]:
        """Create comprehensive citations from context documents"""
        print(f"[AdvancedOrchestrator] Creating citations from {len(context_documents)} documents")
        
        normative_citations = []
        internal_citations = []
        
        # Process each document to create proper citations
        for doc in context_documents:
            citation = {
                "document_info": {
                    "title": doc.get("title", "Documento non identificato"),
                    "document_type": doc.get("document_type", "unknown"),
                    "document_code": doc.get("document_code", ""),
                    "source": doc.get("source", "Unknown")
                },
                "relevance": {
                    "score": "High" if doc.get("search_score", 0) > 0.8 else "Medium",
                    "search_score": doc.get("search_score", 0),
                    "keywords_matched": doc.get("keywords", [])[:3]
                },
                "key_requirements": [
                    {
                        "requirement": "Conformità documentale",
                        "details": doc.get("content_summary", "")[:100] + "..." if doc.get("content_summary") else "Documento rilevante per l'analisi"
                    }
                ],
                "frontend_display": {
                    "display_title": doc.get("title", "Documento"),
                    "badge_color": "success" if doc.get("search_score", 0) > 0.8 else "warning",
                    "icon": "document"
                }
            }
            
            # Categorize by document type
            doc_type = doc.get("document_type", "").lower()
            if any(norm_type in doc_type for norm_type in ["norma", "standard", "legge", "decreto", "regolamento"]):
                normative_citations.append(citation)
            else:
                internal_citations.append(citation)
        
        # Add metadata sources if available (historical permits)
        metadata_citations = []
        if permit_metadata.get("previous_permits"):
            # Count historical permits to determine if work is recurrent
            historical_count = len(permit_metadata["previous_permits"])
            is_recurrent = historical_count >= 2
            
            print(f"[AdvancedOrchestrator] Found {historical_count} historical permits - Work is {'RECURRENT' if is_recurrent else 'NON-RECURRENT'}")
            
            # Add recurrence analysis to permit metadata
            permit_metadata["recurrence_analysis"] = {
                "is_recurrent": is_recurrent,
                "historical_count": historical_count,
                "recurrence_note": "Lavoro ricorrente con precedenti simili" if is_recurrent else "ATTENZIONE: Lavoro non ricorrente - maggiore attenzione richiesta"
            }
            for prev_permit in permit_metadata["previous_permits"][:3]:
                metadata_citations.append({
                    "document_info": {
                        "title": f"Permesso simile: {prev_permit.get('title', 'N/A')}",
                        "document_type": "historical_permit",
                        "document_code": prev_permit.get("permit_number", ""),
                        "source": "Database"
                    },
                    "relevance": {
                        "score": "Medium",
                        "search_score": 0.6,
                        "keywords_matched": []
                    },
                    "key_requirements": [
                        {
                            "requirement": "Riferimento storico",
                            "details": f"Permesso precedente con caratteristiche simili - Status: {prev_permit.get('status', 'unknown')}"
                        }
                    ],
                    "frontend_display": {
                        "display_title": prev_permit.get("title", "Permesso storico"),
                        "badge_color": "info",
                        "icon": "history"
                    }
                })
        
        result = {
            "normative": normative_citations[:5],  # Max 5 normative citations
            "internal": internal_citations[:10],   # Max 10 internal citations  
            "metadata": metadata_citations[:3]     # Max 3 metadata citations
        }
        
        # Count sources for logging
        weaviate_count = sum(1 for docs in [normative_citations, internal_citations] for doc in docs if doc["document_info"]["source"] == "Weaviate")

        print(f"[AdvancedOrchestrator] Generated citations: {len(result['normative'])} normative, {len(result['internal'])} internal, {len(result['metadata'])} metadata")
        print(f"[AdvancedOrchestrator] Source distribution: {weaviate_count} Weaviate documents")
        return result
    
    
    def _create_error_result(self, error_msg: str, start_time: float) -> Dict[str, Any]:
        """Create error result with proper structure for permits router compatibility"""
        return {
            "analysis_id": f"error_{int(time.time())}",
            "permit_id": 0,
            "analysis_complete": False,
            "error": error_msg,
            "processing_time": round(time.time() - start_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": ["Risk_Classifier"],  # At least this ran before error
            "ai_version": "Advanced-Final-1.0-Error",

            # Add specialist_analysis structure for permits router compatibility
            "specialist_analysis": {
                "results_by_specialist": {}
            },

            "executive_summary": {
                "overall_score": 0.0,
                "critical_issues": 1,
                "recommendations": 0,
                "compliance_level": "errore_sistema",
                "estimated_completion_time": "N/A",
                "key_findings": [f"ERRORE: {error_msg}"],
            },
            "action_items": [],
            "dpi_requirements": [],
            "citations": {"normative": [], "internal": [], "metadata": []},
            "performance_metrics": {
                "total_processing_time": round(time.time() - start_time, 2),
                "specialists_activated": 0,
                "analysis_depth": "error",
                "risks_identified": 0,
                "documents_analyzed": 0
            }
        }

    def _validate_permit_data(self, permit_data: Dict[str, Any]) -> None:
        """Validate permit data to prevent analysis errors"""
        if not permit_data:
            raise ValueError("Permit data is empty or None")

        # Check required fields
        required_fields = ['id', 'title', 'description']
        for field in required_fields:
            if field not in permit_data:
                raise ValueError(f"Missing required field: {field}")

            value = permit_data[field]
            if value is None:
                raise ValueError(f"Required field {field} is None")

            # Convert to string if not already (handle numbers, etc.)
            if not isinstance(value, str):
                permit_data[field] = str(value)

            # Check for empty strings
            if field in ['title', 'description'] and not permit_data[field].strip():
                raise ValueError(f"Required field {field} is empty")

        # Validate optional fields that should be strings if present
        string_fields = ['work_type', 'location', 'risks', 'controls']
        for field in string_fields:
            if field in permit_data and permit_data[field] is not None:
                if not isinstance(permit_data[field], str):
                    permit_data[field] = str(permit_data[field])

        # Validate workers_count is a positive number if present
        if 'workers_count' in permit_data and permit_data['workers_count'] is not None:
            try:
                workers_count = int(permit_data['workers_count'])
                if workers_count < 0:
                    raise ValueError("workers_count cannot be negative")
                permit_data['workers_count'] = workers_count
            except (ValueError, TypeError):
                raise ValueError(f"workers_count must be a valid number, got: {permit_data['workers_count']}")

        print(f"[AdvancedOrchestrator] Permit data validation passed for permit {permit_data['id']}")



    def _build_final_result(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification_result: Dict[str, Any],
        specialist_results: Dict[str, Any],
        dpi_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        processing_time: float,
        step_timings: Dict[str, str]
    ) -> Dict[str, Any]:
        """Build final result from specialist and DPI results"""

        print("[AdvancedOrchestrator] Building final result from specialists and DPI")

        # Extract actions directly from specialists
        all_actions = []
        action_id = 1

        # Get actions from specialist results
        for specialist_name, result in specialist_results.items():
            if "error" not in result:
                recommended_actions = result.get("recommended_actions", [])
                print(f"[AdvancedOrchestrator] {specialist_name}: {len(recommended_actions)} actions")

                for action in recommended_actions:
                    if isinstance(action, dict):
                        action_text = action.get("action", str(action))
                        criticality = action.get("criticality", "media")
                        priority = self._convert_criticality_to_priority(criticality)
                    else:
                        action_text = str(action)
                        priority = "media"  # Fallback for string actions

                    all_actions.append({
                        "id": action_id,
                        "type": "safety_action",
                        "priority": priority,
                        "suggested_action": action_text,
                        "category": specialist_name.lower(),
                        "source": specialist_name,
                        "frontend_display": {
                            "icon": "⚠️" if priority == "alta" else "📋",
                            "category_name": specialist_name.replace("_", " ").title()
                            # Removed urgency field as requested
                        }
                    })
                    action_id += 1

        # Extract DPI requirements ONLY from DPI Evaluator - other specialists focus on procedures/actions
        all_dpi_requirements = []

        # Only collect DPI from DPI Evaluator to avoid redundancy and conflicts
        if "DPI_Evaluator" in specialist_results and "error" not in specialist_results["DPI_Evaluator"]:
            dpi_requirements = specialist_results["DPI_Evaluator"].get("dpi_requirements", [])
            for dpi in dpi_requirements:
                all_dpi_requirements.append({
                    "requirement": str(dpi),
                    "source": "DPI_Evaluator",
                    "category": "comprehensive_dpi_assessment"
                })

        # DPI agent removed - DPIEvaluatorAgent handles DPI as specialist

        # Build executive summary
        total_actions = len(all_actions)
        total_dpi = len(all_dpi_requirements)

        # Calculate AI usage statistics
        ai_usage_stats = self._calculate_ai_usage_statistics(specialist_results)

        # Extract risks from classification
        detected_risks = classification_result.get("detected_risks", {})

        # Build citations from documents
        citations = []
        for doc in context_documents[:3]:
            citations.append({
                "source": doc.get("title", "Document"),
                "type": doc.get("document_type", "unknown"),
                "reference": f"[FONTE: Documento Aziendale] {doc.get('title', 'N/A')}"
            })

        final_result = {
            "analysis_id": permit_metadata.get("analysis_id"),
            "permit_id": permit_data.get("id", 1),
            "processing_time": round(processing_time, 2),
            "action_items": all_actions,
            "dpi_requirements": all_dpi_requirements,
            "citations": citations,
            "specialist_results": [specialist_results[name] for name in specialist_results.keys()],

            # Add specialist_analysis structure for permits router compatibility
            "specialist_analysis": {
                "results_by_specialist": specialist_results
            },

            "performance_metrics": {
                "total_specialists": len(specialist_results),
                "step_timings": step_timings,
                "analysis_depth": "simplified",
                "processing_time": round(processing_time, 2)
            },
            "ai_analysis_statistics": ai_usage_stats,
            "timestamp": time.time(),
            "agents_involved": ["Risk_Classifier"] + list(specialist_results.keys()),
            "ai_version": "Advanced-Final-1.0"
        }

        print(f"[AdvancedOrchestrator] Final result: {total_actions} actions, {total_dpi} DPI from {len(specialist_results)} specialists")
        return final_result
    
    def _calculate_ai_usage_statistics(self, specialist_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate AI usage statistics across all specialist agents
        """
        total_specialists = len(specialist_results)
        ai_successful = 0
        ai_failed = 0
        error_specialists = []
        successful_specialists = []
        
        for specialist_name, result in specialist_results.items():
            if "error" in result:
                ai_failed += 1
                error_specialists.append({
                    "name": specialist_name,
                    "error": result.get("error", "Unknown error"),
                    "error_type": result.get("error_type", "Unknown")
                })
            else:
                ai_used = result.get("ai_analysis_used", False)
                if ai_used:
                    ai_successful += 1
                    successful_specialists.append(specialist_name)
                else:
                    ai_failed += 1
                    error_specialists.append({
                        "name": specialist_name,
                        "error": "AI analysis not used",
                        "error_type": "no_ai_analysis"
                    })
        
        success_rate = (ai_successful / total_specialists * 100) if total_specialists > 0 else 0
        
        return {
            "total_specialists_run": total_specialists,
            "ai_analysis_successful": ai_successful,
            "ai_analysis_failed": ai_failed,
            "success_rate_percentage": round(success_rate, 1),
            "successful_specialists": successful_specialists,
            "failed_specialists": error_specialists,
            "overall_ai_status": "success" if ai_successful == total_specialists else "partial" if ai_successful > 0 else "failed"
        }
    

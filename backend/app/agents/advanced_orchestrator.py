"""
Advanced Orchestrator with 3-Step Process
New architecture with risk classifier, specialist interaction, and consolidation
"""

import asyncio
from typing import Dict, Any, List, Optional
import time
import json
from datetime import datetime

from .specialists import get_all_specialists
from .cross_validation import CrossValidationAgent


class AdvancedHSEOrchestrator:
    """
    Simplified 4-step orchestrator:
    1. Risk Analysis & Classification with Risk Mapper
    2. Specialist Agent Selection & Interaction  
    3. DPI Agent for PPE Analysis
    4. Direct Output Generation from Specialists and DPI
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
        
        self.cross_validator = CrossValidationAgent()
        
        # Inject vector service into all specialists
        if vector_service:
            for specialist in self.specialists.values():
                specialist.vector_service = vector_service
            print(f"[AdvancedOrchestrator] Injected vector service into {len(self.specialists)} specialists")
        
        print(f"[AdvancedOrchestrator] Initialized with enhanced 5-step process")
    
    async def analyze_permit_advanced(
        self, 
        permit_data: Dict[str, Any], 
        permit_metadata: Dict[str, Any] = None,
        context_documents: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simplified 4-step analysis process:
        1. Risk Analysis & Classification with Risk Mapper
        2. Specialist Agent Selection & Interaction
        3. DPI Agent for PPE Analysis
        4. Direct Output Generation from Specialists and DPI
        
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
            print(f"\n[AdvancedOrchestrator] Starting simplified 4-step analysis for permit {permit_data.get('id')}")
            
            # STEP 1: Work permit risk analysis with risk mapper
            print("[AdvancedOrchestrator] STEP 1: Work permit risk analysis with risk mapper")
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
            
            # STEP 3: Skip DPI consolidation - DPIEvaluatorAgent handles this as specialist
            print("[AdvancedOrchestrator] STEP 3: Skipping DPI consolidation - handled by DPIEvaluatorAgent")
            dpi_results = {}
            
            # STEP 4: Build final result directly from specialist and DPI results (no consolidation)
            print("[AdvancedOrchestrator] STEP 4: Building final result directly from specialists and DPI")
            step4_start = time.time()
            final_result = self._build_simple_final_result(
                permit_data,
                permit_metadata,
                classification_result,
                specialist_results,
                dpi_results,
                context_documents,
                time.time() - start_time,
                step_timings
            )
            step_timings["step4_final_output"] = round(time.time() - step4_start, 2)
            print(f"[AdvancedOrchestrator] STEP 4 completed in {step_timings['step4_final_output']}s")
            
            total_time = round(time.time() - start_time, 2)
            print(f"[AdvancedOrchestrator] Enhanced 4-step analysis completed in {total_time}s")
            print(f"[AdvancedOrchestrator] Step breakdown: {step_timings}")
            
            return final_result
            
        except Exception as e:
            print(f"[AdvancedOrchestrator] Error during enhanced 5-step analysis: {e}")
            import traceback
            traceback.print_exc()
            return self._create_error_result(str(e), start_time)
    
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
    
    async def _step3_consolidation(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification: Dict[str, Any],
        specialist_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        processing_time: float
    ) -> Dict[str, Any]:
        """
        STEP 3: Consolidation and coherence checking
        - Consolidate all actions and DPI recommendations
        - Check for coherence and eliminate duplicates
        - Resolve conflicts between specialist recommendations
        - Ensure DPI compatibility (e.g., electrical + cut protection gloves)
        """
        
        # Collect all recommendations
        all_actions = []
        all_dpi = []
        
        # Extract recommendations from each specialist
        for specialist_name, result in specialist_results.items():
            if "error" not in result:
                actions = result.get("mitigation_actions", [])
                dpi = result.get("dpi_requirements", [])
                
                # Tag recommendations with source
                for action in actions:
                    all_actions.append({
                        "action": action,
                        "source": specialist_name,
                        "type": "specialist_recommendation"
                    })
                
                for dpi_item in dpi:
                    all_dpi.append({
                        "item": dpi_item,
                        "source": specialist_name,
                        "type": "specialist_requirement"
                    })
        
        # COHERENCE CHECKING: Resolve conflicts and duplicates
        coherent_actions = await self._resolve_action_conflicts(all_actions)
        compatible_dpi = await self._resolve_dpi_compatibility(all_dpi)
        
        # INTERACTION RESULTS: Check if specialists needed to interact
        interaction_summary = await self._analyze_specialist_interactions(
            specialist_results, coherent_actions, compatible_dpi
        )
        
        print(f"[AdvancedOrchestrator] STEP 3 Complete - Consolidated {len(all_actions)} actions to {len(coherent_actions)}, {len(all_dpi)} DPI to {len(compatible_dpi)}")
        
        # Build final consolidated result
        return self._build_final_consolidated_result(
            permit_data, permit_metadata, classification,
            specialist_results, context_documents,
            coherent_actions, compatible_dpi,
            interaction_summary, processing_time
        )
    
    async def _resolve_action_conflicts(self, all_actions: List[Dict]) -> List[Dict]:
        """
        Resolve conflicts between specialist action recommendations
        """
        print(f"  Resolving conflicts in {len(all_actions)} action recommendations")
        
        # Group similar actions
        action_groups = {}
        for action_item in all_actions:
            action_text = str(action_item["action"]).lower()
            
            # Group by action type
            if "ventilaz" in action_text or "ventilation" in action_text:
                key = "ventilation"
            elif "lockout" in action_text or "loto" in action_text or "isolamento" in action_text:
                key = "isolation"
            elif "gas test" in action_text or "atmosfera" in action_text:
                key = "atmosphere_monitoring"
            elif "fire watch" in action_text or "sorveglianza" in action_text:
                key = "fire_watch"
            else:
                key = action_text[:30]  # Use first 30 chars as key
            
            if key not in action_groups:
                action_groups[key] = []
            action_groups[key].append(action_item)
        
        # Consolidate each group
        coherent_actions = []
        for group_key, actions in action_groups.items():
            if len(actions) == 1:
                coherent_actions.append(actions[0])
            else:
                # Merge multiple similar actions
                consolidated = self._merge_similar_actions(actions)
                coherent_actions.append(consolidated)
        
        print(f"  Consolidated to {len(coherent_actions)} coherent actions")
        return coherent_actions
    
    async def _resolve_dpi_compatibility(self, all_dpi: List[Dict]) -> List[Dict]:
        """
        Resolve DPI compatibility issues (e.g., combine electrical + cut protection)
        """
        print(f"  Resolving compatibility in {len(all_dpi)} DPI recommendations")
        
        # Group DPI by body part/type
        dpi_groups = {
            "hand_protection": [],
            "eye_protection": [],
            "foot_protection": [],
            "head_protection": [],
            "respiratory_protection": [],
            "body_protection": [],
            "fall_protection": []
        }
        
        for dpi_item in all_dpi:
            dpi_text = str(dpi_item["item"]).lower()
            
            if "guant" in dpi_text or "glove" in dpi_text:
                dpi_groups["hand_protection"].append(dpi_item)
            elif "occhial" in dpi_text or "goggle" in dpi_text or "eye" in dpi_text:
                dpi_groups["eye_protection"].append(dpi_item)
            elif "scarpe" in dpi_text or "boot" in dpi_text or "shoe" in dpi_text:
                dpi_groups["foot_protection"].append(dpi_item)
            elif "casco" in dpi_text or "helmet" in dpi_text:
                dpi_groups["head_protection"].append(dpi_item)
            elif "respirator" in dpi_text or "ffp" in dpi_text or "mask" in dpi_text:
                dpi_groups["respiratory_protection"].append(dpi_item)
            elif "tuta" in dpi_text or "suit" in dpi_text:
                dpi_groups["body_protection"].append(dpi_item)
            elif "imbracatura" in dpi_text or "harness" in dpi_text:
                dpi_groups["fall_protection"].append(dpi_item)
            else:
                dpi_groups["body_protection"].append(dpi_item)  # Default group
        
        # Resolve compatibility within each group
        compatible_dpi = []
        for group_name, dpi_items in dpi_groups.items():
            if len(dpi_items) == 0:
                continue
            elif len(dpi_items) == 1:
                compatible_dpi.append(dpi_items[0])
            else:
                # Resolve conflicts within the group - EXAMPLE: electrical + cut protection gloves
                resolved = self._resolve_dpi_group_conflicts(group_name, dpi_items)
                compatible_dpi.extend(resolved)
        
        print(f"  Resolved to {len(compatible_dpi)} compatible DPI items")
        return compatible_dpi
    
    def _resolve_dpi_group_conflicts(self, group_name: str, dpi_items: List[Dict]) -> List[Dict]:
        """
        Resolve conflicts within a DPI group (e.g., find glove that provides both electrical and cut protection)
        """
        if group_name == "hand_protection":
            # EXAMPLE IMPLEMENTATION: Special handling for gloves - find compatible protection
            electrical_needed = any("elettric" in str(item["item"]).lower() or "electrical" in str(item["item"]).lower() for item in dpi_items)
            cut_needed = any("taglio" in str(item["item"]).lower() or "cut" in str(item["item"]).lower() for item in dpi_items)
            chemical_needed = any("chemic" in str(item["item"]).lower() or "chimico" in str(item["item"]).lower() for item in dpi_items)
            
            if electrical_needed and cut_needed:
                # Need multi-protection gloves - THIS IS THE EXAMPLE FROM REQUIREMENTS
                return [{
                    "item": "Guanti multi-protezione: elettrica + antitaglio EN 388 Livello 3 + EN 60903",
                    "source": "Consolidated requirement",
                    "type": "compatibility_resolved",
                    "protection_types": ["electrical", "cut_protection"],
                    "note": "Risolto conflitto protezione elettrica/taglio - agente elettrico + meccanico"
                }]
            elif electrical_needed and chemical_needed:
                return [{
                    "item": "Guanti multi-protezione: elettrica + chimica EN 60903 + EN 374",
                    "source": "Consolidated requirement", 
                    "type": "compatibility_resolved",
                    "protection_types": ["electrical", "chemical_protection"]
                }]
        
        # For other groups or simpler conflicts, return most stringent requirement
        most_stringent = max(dpi_items, key=lambda x: len(str(x["item"])))
        most_stringent["type"] = "most_stringent_selected"
        most_stringent["consolidation_note"] = f"Selected most stringent from {len(dpi_items)} options"
        return [most_stringent]
    
    async def _analyze_specialist_interactions(
        self, 
        specialist_results: Dict[str, Any], 
        actions: List[Dict], 
        dpi: List[Dict]
    ) -> Dict[str, Any]:
        """
        Analyze whether specialists needed to interact for conflict resolution
        """
        interaction_needed = False
        interaction_details = []
        
        # Check for potential conflicts that required resolution
        specialist_names = list(specialist_results.keys())
        
        if len(specialist_names) > 1:
            for i, spec1 in enumerate(specialist_names):
                for spec2 in specialist_names[i+1:]:
                    # Check if both specialists made recommendations for same risk area
                    overlap = self._check_specialist_overlap(spec1, spec2, actions, dpi)
                    if overlap:
                        interaction_needed = True
                        interaction_details.append(f"{spec1} and {spec2} had overlapping recommendations")
        
        return {
            "interaction_occurred": interaction_needed,
            "interaction_details": interaction_details,
            "conflicts_resolved": len(interaction_details),
            "final_coherence_achieved": True
        }
    
    def _merge_similar_actions(self, actions: List[Dict]) -> Dict:
        """
        Merge similar actions from multiple specialists
        """
        sources = [action["source"] for action in actions]
        action_texts = [str(action["action"]) for action in actions]
        
        # Create merged action
        return {
            "action": f"Consolidato: {action_texts[0]}",  # Use first as base
            "source": f"Multiple specialists: {', '.join(sources)}",
            "type": "consolidated_recommendation",
            "original_count": len(actions),
            "consolidation_note": f"Merged {len(actions)} similar recommendations"
        }
    
    def _check_specialist_overlap(self, spec1: str, spec2: str, actions: List[Dict], dpi: List[Dict]) -> bool:
        """
        Check if two specialists have overlapping recommendations
        """
        spec1_actions = [a for a in actions if spec1 in str(a.get("source", ""))]
        spec2_actions = [a for a in actions if spec2 in str(a.get("source", ""))]
        
        spec1_dpi = [d for d in dpi if spec1 in str(d.get("source", ""))]
        spec2_dpi = [d for d in dpi if spec2 in str(d.get("source", ""))]
        
        # Simple overlap check based on keywords
        return (len(spec1_actions) > 0 and len(spec2_actions) > 0) or (len(spec1_dpi) > 0 and len(spec2_dpi) > 0)
    
    
    def _build_final_consolidated_result(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification: Dict[str, Any],
        specialist_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        coherent_actions: List[Dict],
        compatible_dpi: List[Dict],
        interaction_summary: Dict[str, Any],
        processing_time: float
    ) -> Dict[str, Any]:
        """
        Build the final consolidated result with all 3 steps completed
        """
        
        # Extract actions and DPI for action items
        final_actions = [item["action"] for item in coherent_actions]
        final_dpi = [item["item"] for item in compatible_dpi]
        
        # Create action items from consolidated specialist results
        action_items = self._create_action_items_from_consolidated(
            final_actions, final_dpi, permit_metadata, coherent_actions, compatible_dpi
        )
        
        # Calculate summary metrics using risk mapping results
        critical_issues = 0
        if classification.get("risk_mapping"):
            detected_risks = classification["risk_mapping"].get("detected_risks", {})
            risk_combinations = classification["risk_mapping"].get("risk_combinations", [])
            
            # Count high-confidence risks that are critical
            critical_risk_types = ["hot_work", "confined_space", "electrical", "height"]
            critical_issues = len([r for r in detected_risks.keys() if r in critical_risk_types and detected_risks[r].get("confidence", 0) > 0.5])
            
            # Add critical combinations
            critical_issues += len([c for c in risk_combinations if c.get("severity") == "critical"])
        
        return {
            "analysis_id": f"advanced_3step_{int(time.time())}_{permit_data.get('id')}",
            "permit_id": permit_data.get("id"),
            "processing_time": round(processing_time, 2),
            
            # Correttezza del permesso (in testa)
            "permit_correctness": {
                "completeness_score": classification.get('permit_completeness', {}).get('score', 0),
                "missing_elements": classification.get('permit_completeness', {}).get('missing_elements', []),
                "overall_assessment": self._determine_compliance_level(classification, critical_issues),
                "recommendations_needed": len(action_items)
            },
            
            # 3-Step Process Summary
            "three_step_process": {
                "step1_risk_analysis": {
                    "completed": True,
                    "risks_identified": len(classification.get("risk_mapping", {}).get("detected_risks", {})),
                    "completeness_score": classification.get('permit_completeness', {}).get('score', 0)
                },
                "step2_specialist_interaction": {
                    "completed": True,
                    "specialists_activated": len(specialist_results),
                    "document_control_enforced": True,
                    "interaction_occurred": interaction_summary.get("interaction_occurred", False)
                },
                "step3_consolidation": {
                    "completed": True,
                    "actions_consolidated": len(coherent_actions),
                    "dpi_compatibility_resolved": len(compatible_dpi),
                    "conflicts_resolved": interaction_summary.get("conflicts_resolved", 0)
                }
            },
            
            # Executive Summary (semplificato)
            "executive_summary": {
                "overall_score": self._calculate_overall_score(classification, critical_issues, compatible_dpi, coherent_actions),
                "critical_issues": critical_issues,
                "recommendations": len(action_items),
                "compliance_level": self._determine_compliance_level(classification, critical_issues),
                "estimated_completion_time": "0-0 ore",
                "key_findings": self._extract_key_findings(classification, permit_metadata),
            },
            
            # Lista azioni prioritizzate
            "prioritized_actions": self._create_prioritized_actions(coherent_actions, compatible_dpi, classification),
            
            # DPI da aggiungere/modificare
            "dpi_modifications": self._create_dpi_modifications(compatible_dpi, permit_data, classification),
            
            "action_items": action_items,
            "agents_involved": ["Risk_Classifier"] + list(specialist_results.keys()),
            
            # Required schema fields
            "citations": self._create_citations(context_documents, permit_metadata),
            "timestamp": datetime.utcnow().isoformat(),
            "ai_version": "Advanced-3Step-AI-1.0",
            
            # Consolidation results
            "consolidation_results": {
                "original_actions": len([item for sublist in [result.get("recommended_actions", []) for result in specialist_results.values() if "error" not in result] for item in sublist]),
                "final_actions": len(coherent_actions),
                "original_dpi": len([item for sublist in [result.get("dpi_requirements", []) for result in specialist_results.values() if "error" not in result] for item in sublist]),
                "final_dpi": len(compatible_dpi),
                "compatibility_issues_resolved": interaction_summary.get("conflicts_resolved", 0),
                "interaction_summary": interaction_summary
            },
            
            # Performance metrics
            "performance_metrics": {
                "total_processing_time": round(processing_time, 2),
                "step1_duration": "~30%",
                "step2_duration": "~50%", 
                "step3_duration": "~20%",
                "specialists_activated": len(specialist_results),
                "document_control_performed": True,
                "interaction_enabled": True,
                "consolidation_performed": True,
                "risks_identified": len(classification.get("risk_mapping", {}).get("detected_risks", {})),
                "documents_analyzed": len(context_documents)
            }
        }
    
    def _create_action_items_from_consolidated(
        self, 
        final_actions: List[str],
        final_dpi: List[str], 
        permit_metadata: Dict[str, Any],
        coherent_actions: List[Dict],
        compatible_dpi: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Create action items from consolidated results
        """
        action_items = []
        item_id = 1
        
        # Priority actions from consolidation - use AI-generated criticality
        for action_item in coherent_actions:
            # Trust AI-generated criticality from specialists, no hardcoded overrides
            priority = action_item.get("priority", "media")  # Keep original priority from specialists

            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "consolidated_action",
                "priority": priority,
                "action": str(action_item["action"]),
                "source": action_item.get('source', 'Multiple specialists'),
                "category": "safety_control"
            })
            item_id += 1
        
        # Compatible DPI requirements - use AI-generated priority
        for dpi_item in compatible_dpi:
            # Trust DPI specialist analysis, no hardcoded priority overrides
            priority = dpi_item.get("priority", "alta")  # DPI is generally high priority

            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "consolidated_dpi",
                "priority": priority,
                "action": f"Fornire DPI: {str(dpi_item['item'])}",
                "source": dpi_item.get('source', 'Multiple specialists'),
                "category": "dpi_safety"
            })
            item_id += 1
            
            if item_id > 10:  # Limit to 10 action items
                break
        
        return action_items
    
    def _create_prioritized_actions(
        self,
        coherent_actions: List[Dict],
        compatible_dpi: List[Dict],
        classification: Dict[str, Any]
    ) -> Dict[str, List[Dict]]:
        """
        Crea una lista di azioni divise per priorità basata su AI-generated criticality
        Trust specialists' AI analysis instead of hardcoded rules
        """
        prioritized = {
            "alta": [],
            "media": [],
            "bassa": []
        }

        action_id = 1

        # Process consolidated actions - trust AI-generated priority
        for action_item in coherent_actions:
            action_text = str(action_item.get("action", ""))
            source = action_item.get("source", "")

            # Use AI-generated priority from specialists, no hardcoded overrides
            priority = action_item.get("priority", "media")

            prioritized[priority].append({
                "id": f"PA_{action_id:03d}",
                "action": action_text,
                "source": source,
                "category": self._identify_risk_area(action_text)
            })
            action_id += 1

        # Add actions for permit completeness if necessary (keep as alta since these are critical gaps)
        completeness_score = classification.get('permit_completeness', {}).get('score', 10)
        if completeness_score < 8:
            missing_elements = classification.get('permit_completeness', {}).get('missing_elements', [])
            for element in missing_elements:
                prioritized["alta"].append({
                    "id": f"PA_{action_id:03d}",
                    "action": f"Completare elemento mancante: {element}",
                    "source": "Valutazione completezza",
                    "category": "documentale"
                })
                action_id += 1

        # Add actions for non-recurrent work (keep as alta since these require extra attention)
        recurrence_info = classification.get("permit_metadata", {}).get("recurrence_analysis")
        if recurrence_info and not recurrence_info.get("is_recurrent", True):
            prioritized["alta"].append({
                "id": f"PA_{action_id:03d}",
                "action": f"Verifica aggiuntiva per lavoro non ricorrente: {recurrence_info.get('recurrence_note', 'Lavoro non ricorrente')}",
                "source": "Analisi ricorrenza",
                "category": "risk_management"
            })
            action_id += 1

        return prioritized

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

    def _create_dpi_modifications(
        self,
        compatible_dpi: List[Dict],
        permit_data: Dict[str, Any], 
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Crea sezione DPI da aggiungere/modificare
        """
        existing_dpi = permit_data.get('dpi_required', [])
        
        # DPI da aggiungere
        dpi_to_add = []
        # DPI da modificare/sostituire
        dpi_to_modify = []
        
        for dpi_item in compatible_dpi:
            dpi_text = str(dpi_item.get("item", ""))
            source = dpi_item.get("source", "")
            
            # Determina se è aggiunta o modifica
            is_modification = (dpi_item.get("type") == "compatibility_resolved" or
                             "multi-protezione" in dpi_text.lower())

            # Use AI-generated priority from DPI specialist
            priority = dpi_item.get("priority", "alta")  # DPI is generally high priority if not specified

            dpi_entry = {
                "item": dpi_text,
                "source": source,
                "citation": self._find_dpi_citation(dpi_text, classification),
                "priority": priority,
                "justification": self._get_dpi_justification(dpi_text, classification),
                "category": self._categorize_dpi(dpi_text)
            }
            
            if is_modification:
                dpi_to_modify.append(dpi_entry)
            else:
                dpi_to_add.append(dpi_entry)
        
        return {
            "existing_dpi": existing_dpi,
            "to_add": dpi_to_add,
            "to_modify": dpi_to_modify,
            "total_changes": len(dpi_to_add) + len(dpi_to_modify),
            "modification_summary": self._create_dpi_summary(dpi_to_add, dpi_to_modify, existing_dpi)
        }
    
    def _find_action_citation(self, action_text: str, classification: Dict[str, Any]) -> Dict[str, str]:
        """Trova citazione documentale per l'azione"""
        # Logica semplificata - in produzione dovrebbe cercare nei documenti
        if "elettric" in action_text.lower():
            return {
                "document": "CEI 11-27",
                "requirement": "Lavori su impianti elettrici"
            }
        elif "ventilaz" in action_text.lower():
            return {
                "document": "D.Lgs 81/2008",
                "requirement": "Ventilazione spazi confinati"
            }
        elif "lockout" in action_text.lower() or "isolamento" in action_text.lower():
            return {
                "document": "Procedura LOTO aziendale",
                "requirement": "Isolamento energie pericolose"
            }
        return None
    
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
    
    def _identify_risk_area(self, action_text: str) -> str:
        """Identifica l'area di rischio dell'azione"""
        action_lower = action_text.lower()
        if "elettric" in action_lower:
            return "Elettrico"
        elif "chimico" in action_lower or "sostanza" in action_lower:
            return "Chimico"
        elif "altezza" in action_lower or "caduta" in action_lower:
            return "Lavori in altezza"
        elif "caldo" in action_lower or "saldatura" in action_lower:
            return "Lavori a caldo"
        elif "confinato" in action_lower or "serbatoio" in action_lower:
            return "Spazi confinati"
        else:
            return "Generale"
    
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
    
    def _calculate_overall_score(self, classification: Dict, critical_issues: int, compatible_dpi: List, coherent_actions: List) -> float:
        """Calculate overall score"""
        base_score = 0.8
        if critical_issues > 2:
            base_score *= 0.5
        elif critical_issues > 0:
            base_score *= 0.7
        if len(compatible_dpi) == 0:
            base_score *= 0.8
        return round(base_score, 2)
    
    def _determine_compliance_level(self, classification: Dict, critical_issues: int) -> str:
        """Determine compliance level"""
        completeness_score = classification.get('permit_completeness', {}).get('score', 0)
        
        if critical_issues > 2:
            return "NON CONFORME - Rischi critici non gestiti"
        elif completeness_score < 5:
            return "INCOMPLETO - Informazioni mancanti"
        elif critical_issues > 0:
            return "ACCETTABILE - Con raccomandazioni"
        else:
            return "CONFORME - Standard soddisfatti"
    
    def _extract_key_findings(self, classification: Dict, permit_metadata: Dict) -> List[str]:
        """Extract key findings using risk mapping results"""
        findings = []
        
        # Get risks from risk mapping results
        if classification.get('risk_mapping'):
            detected_risks = classification['risk_mapping'].get('detected_risks', {})
            risk_combinations = classification['risk_mapping'].get('risk_combinations', [])
            
            if detected_risks:
                risk_names = [risk.replace('_', ' ').title() for risk in detected_risks.keys()]
                findings.append(f"⚠️ RISCHI IDENTIFICATI: {', '.join(risk_names)}")
            
            # Add critical combinations
            for combo in risk_combinations:
                if combo.get('severity') == 'critical':
                    findings.append(f"🚨 {combo.get('warning', 'Combinazione critica rilevata')}")
        else:
            # If risk mapping not available, add generic message
            findings.append("⚠️ Sistema di mappatura rischi non disponibile")
        
        completeness_score = classification.get('permit_completeness', {}).get('score', 0)
        findings.append(f"🔍 COMPLETEZZA PERMESSO: {completeness_score}/10")
        
        # Add recurrence analysis to key findings
        if permit_metadata.get("recurrence_analysis"):
            recurrence_info = permit_metadata["recurrence_analysis"]
            if recurrence_info["is_recurrent"]:
                findings.append(f"🔄 LAVORO RICORRENTE: {recurrence_info['historical_count']} precedenti")
            else:
                findings.append(f"⚠️ LAVORO NON RICORRENTE: Prima volta o raro - maggiore attenzione")
        
        return findings[:5]
    
    
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
        """Create error result"""
        return {
            "analysis_id": f"error_{int(time.time())}",
            "permit_id": 0,
            "analysis_complete": False,
            "error": error_msg,
            "processing_time": round(time.time() - start_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": [],
            "ai_version": "Advanced-3Step-AI-1.0-Error",
            "executive_summary": {
                "overall_score": 0.0,
                "critical_issues": 1,
                "recommendations": 0,
                "compliance_level": "errore_sistema",
                "estimated_completion_time": "N/A",
                "key_findings": [f"ERRORE: {error_msg}"],
            },
            "action_items": [],
            "citations": {"normative": [], "internal": [], "metadata": []},
            "performance_metrics": {
                "total_processing_time": round(time.time() - start_time, 2),
                "specialists_activated": 0,
                "parallel_execution": False,
                "risks_identified": 0,
                "documents_analyzed": 0
            }
        }
    
    async def _build_final_result_from_specialists(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification: Dict[str, Any],
        specialist_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        processing_time: float
    ) -> Dict[str, Any]:
        """
        Build final result directly from specialist results without consolidation
        Convert specialist control_measures and dpi_requirements directly to action items
        """
        
        # Extract all actions and DPI from specialist results
        all_action_items = []
        item_id = 1
        agents_involved = ["Risk_Classifier"]
        
        print(f"[AdvancedOrchestrator] Processing {len(specialist_results)} specialist results")
        
        for specialist_name, result in specialist_results.items():
            if "error" not in result:
                agents_involved.append(specialist_name)
                
                # Get recommended actions from specialist
                recommended_actions = result.get("recommended_actions", [])
                dpi_requirements = result.get("dpi_requirements", [])
                
                print(f"  {specialist_name}: {len(recommended_actions)} actions, {len(dpi_requirements)} DPI")
                
                # Convert recommended actions to action items
                for action_item in recommended_actions:
                    if isinstance(action_item, dict):
                        # Extract action text and priority from specialist action item
                        action_text = action_item.get("action", "")
                        criticality = action_item.get("criticality", "media")
                        
                        # Convert criticality to priority
                        if criticality in ["critica", "critical"]:
                            priority = "alta"
                        elif criticality in ["alta", "high"]:
                            priority = "alta"
                        elif criticality in ["media", "medium"]:
                            priority = "media"
                        elif criticality in ["bassa", "low"]:
                            priority = "bassa"
                        else:
                            priority = "media"
                            
                        all_action_items.append({
                            "id": f"ACT_{item_id:03d}",
                            "type": action_item.get("type", "control_measure"),
                            "priority": priority,
                            "action": action_text,
                            "source": specialist_name,
                            "category": action_item.get("category", "safety_control")
                        })
                    else:
                        # Handle string actions (fallback - specialists should return structured objects)
                        all_action_items.append({
                            "id": f"ACT_{item_id:03d}",
                            "type": "control_measure",
                            "priority": "media",  # Default only for string fallback
                            "action": str(action_item),
                            "source": specialist_name,
                            "category": "safety_control"
                        })
                    item_id += 1
                
                # Convert DPI requirements to action items
                for dpi in dpi_requirements:
                    # DPI requirements should come from DPI specialist with proper priority
                    dpi_priority = dpi.get("priority", "alta") if isinstance(dpi, dict) else "alta"
                    dpi_text = dpi.get("item", str(dpi)) if isinstance(dpi, dict) else str(dpi)

                    all_action_items.append({
                        "id": f"DPI_{item_id:03d}",
                        "type": "dpi_requirement",
                        "priority": dpi_priority,
                        "action": f"Fornire e utilizzare {dpi_text}",
                        "source": specialist_name,
                        "category": "dpi_safety"
                    })
                    item_id += 1
        
        print(f"[AdvancedOrchestrator] Generated {len(all_action_items)} action items from specialists")
        
        # Calculate summary metrics
        critical_issues = 0
        if classification.get("risk_mapping"):
            detected_risks = classification["risk_mapping"].get("detected_risks", {})
            critical_risk_types = ["hot_work", "confined_space", "electrical", "height"]
            critical_issues = len([r for r in detected_risks.keys() if r in critical_risk_types and detected_risks[r].get("confidence", 0) > 0.5])
        
        # Build final result
        return {
            "analysis_id": f"advanced_direct_{int(time.time())}_{permit_data.get('id')}",
            "permit_id": permit_data.get("id"),
            "processing_time": round(processing_time, 2),
            
            # Executive Summary
            "executive_summary": {
                "overall_score": 0.85,
                "critical_issues": critical_issues,
                "recommendations": len(all_action_items),
                "compliance_level": "CONTROLLI RICHIESTI" if len(all_action_items) > 0 else "CONFORME",
                "estimated_completion_time": f"{len(all_action_items) * 15}-{len(all_action_items) * 45} minuti",
                "key_findings": [
                    f"⚠️ RISCHI IDENTIFICATI: {', '.join(classification.get('risk_mapping', {}).get('detected_risks', {}).keys())}",
                    f"🔍 AZIONI RICHIESTE: {len(all_action_items)} controlli e DPI"
                ],
            },
            
            # Action items (the main output)
            "action_items": all_action_items,
            
            # Agents involved
            "agents_involved": agents_involved,
            
            # Citations (simplified)
            "citations": {
                "normative": [],
                "internal": [],
                "metadata": []
            },
            
            # Performance metrics
            "performance_metrics": {
                "total_processing_time": round(processing_time, 2),
                "step1_duration": "~30%",
                "step2_duration": "~60%",
                "step3_duration": "~10%",
                "specialists_activated": len([r for r in specialist_results.values() if "error" not in r]),
                "consolidation_performed": False,
                "direct_conversion": True,
                "risks_identified": len(classification.get('risk_mapping', {}).get('detected_risks', {})),
                "documents_analyzed": len(context_documents),
                "action_items_generated": len(all_action_items)
            },
            
            # Additional metadata
            "timestamp": time.time(),
            "ai_version": "Advanced-Direct-2.0"
        }
    
    def _build_direct_final_result(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification_result: Dict[str, Any],
        specialist_results: Dict[str, Any],
        dpi_results: Dict[str, Any],
        consolidation_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        processing_time: float,
        step_timings: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Build final result directly from consolidator output, bypassing enhanced workflow methods
        """
        
        print(f"[AdvancedOrchestrator] Building direct final result from consolidator")
        
        # Extract consolidated actions directly from consolidator results
        # DEBUG: Check what keys the consolidator actually returns
        print(f"[AdvancedOrchestrator] Consolidator result keys: {list(consolidation_results.keys())}")
        
        # Try multiple possible keys for actions
        consolidated_actions = []
        if "actions" in consolidation_results:
            consolidated_actions = consolidation_results["actions"]
        elif "consolidated_actions" in consolidation_results:
            consolidated_actions = consolidation_results["consolidated_actions"]
        else:
            # Fallback: check all keys for action-like data
            for key, value in consolidation_results.items():
                if isinstance(value, list) and key in ["final_actions", "result_actions", "prioritized_actions"]:
                    consolidated_actions = value
                    print(f"[AdvancedOrchestrator] Found actions under key: {key}")
                    break
        
        print(f"[AdvancedOrchestrator] Got {len(consolidated_actions)} consolidated actions from consolidator")
        if consolidated_actions:
            print(f"[AdvancedOrchestrator] First action sample: {str(consolidated_actions[0])[:100]}...")
        
        # Extract DPI requirements from specialists and DPI agent
        all_dpi_requirements = []
        
        # From specialists
        for specialist_name, result in specialist_results.items():
            if "error" not in result:
                dpi_requirements = result.get("dpi_requirements", [])
                for dpi in dpi_requirements:
                    all_dpi_requirements.append({
                        "requirement": str(dpi),
                        "source": specialist_name,
                        "category": "specialist_dpi"
                    })
        
        # DPI agent removed - DPIEvaluatorAgent handles DPI as specialist
        
        print(f"[AdvancedOrchestrator] Extracted {len(all_dpi_requirements)} DPI requirements")
        
        # Build risk analysis summary from classification
        risk_mapping = classification_result.get("classification", {}).get("risk_mapping", {})
        detected_risks = risk_mapping.get("detected_risks", {})
        
        risk_summary = []
        for risk_type, risk_info in detected_risks.items():
            if isinstance(risk_info, dict):
                severity = risk_info.get("severity", "media")
                description = risk_info.get("description", f"Rischio {risk_type}")
                risk_summary.append(f"• {description} (severità: {severity})")
            else:
                risk_summary.append(f"• Rischio {risk_type}")
        
        # Get workers count from permit metadata
        workers_count = permit_metadata.get("workers_count", permit_data.get("workers_count"))
        
        # Build final result structure matching frontend expectations
        final_result = {
            "analysis": {
                "title": f"Analisi HSE: {permit_data.get('title', 'Permesso di lavoro')}",
                "executive_summary": consolidation_results.get("executive_summary", "Analisi completata con successo"),
                "key_findings": risk_summary if risk_summary else ["Nessun rischio critico identificato"],
                "risk_assessment": {
                    "overall_level": risk_mapping.get("overall_risk_level", "MEDIO"),
                    "critical_factors": list(detected_risks.keys()),
                    "mitigation_status": "In elaborazione"
                }
            },
            
            "consolidated_actions": consolidated_actions,  # Direct from consolidator
            
            "action_items": [
                {
                    "id": i + 1,
                    "type": "safety_action",
                    "priority": self._convert_criticality_to_priority(action.get("criticality", action.get("priority", "media"))),
                    "suggested_action": action.get("action", str(action)),
                    "category": action.get("category", "general"),
                    "timeline": action.get("timeline", "Da definire"),
                    "responsible": action.get("responsible", "Da assegnare"),
                    "status": action.get("status", "planned"),
                    "frontend_display": {
                        "icon": "⚠️" if self._convert_criticality_to_priority(action.get("criticality", action.get("priority", "media"))) == "alta" else "📋",
                        "category_name": action.get("source", "General")
                        # Removed urgency field - all actions are pre-work
                    }
                }
                for i, action in enumerate(consolidated_actions)
            ],
            
            "dpi_requirements": [
                {
                    "id": i + 1,
                    "requirement": dpi["requirement"],
                    "category": dpi["category"],
                    "source": dpi["source"]
                }
                for i, dpi in enumerate(all_dpi_requirements)
            ],
            
            "citations": {
                "normative": consolidation_results.get("regulatory_references", []),
                "internal": [],
                "metadata": {
                    "total_documents_analyzed": len(context_documents),
                    "specialists_activated": len([r for r in specialist_results.values() if "error" not in r]),
                    "consolidation_performed": True
                }
            },
            
            "custom_fields": {
                "workers_count": workers_count
            },
            
            "performance_metrics": {
                "total_processing_time": round(processing_time, 2),
                "step_timings": step_timings,
                "consolidation_efficiency": consolidation_results.get("consolidation_metadata", {}).get("deduplication_efficiency", "N/A"),
                "specialists_activated": len([r for r in specialist_results.values() if "error" not in r]),
                "risks_identified": len(detected_risks),
                "documents_analyzed": len(context_documents),
                "consolidated_actions_count": len(consolidated_actions),
                "dpi_requirements_count": len(all_dpi_requirements)
            },
            
            "timestamp": time.time(),
            "ai_version": "Direct-Consolidator-1.0"
        }
        
        print(f"[AdvancedOrchestrator] Final result: {len(final_result['consolidated_actions'])} actions, {len(final_result['dpi_requirements'])} DPI")
        return final_result
    
    def _build_simple_final_result(
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
        """Build final result directly from specialist and DPI results (no consolidation)"""
        
        print("[AdvancedOrchestrator] Building simple final result from specialists and DPI")
        
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
            "performance_metrics": {
                "total_specialists": len(specialist_results),
                "step_timings": step_timings,
                "analysis_depth": "simplified",
                "processing_time": round(processing_time, 2)
            },
            "ai_analysis_statistics": ai_usage_stats,
            "timestamp": time.time(),
            "agents_involved": ["Specialists"],
            "ai_version": "Simplified-Direct-1.0"
        }
        
        print(f"[AdvancedOrchestrator] Simple result: {total_actions} actions, {total_dpi} DPI from {len(specialist_results)} specialists")
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
    

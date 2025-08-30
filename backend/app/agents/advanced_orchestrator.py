"""
Advanced Orchestrator with PostgreSQL Integration
Uses permit metadata from PostgreSQL for intelligent agent routing
"""

import asyncio
from typing import Dict, Any, List, Optional
import time
import json
from datetime import datetime
from sqlalchemy.orm import Session

from .specialists import get_all_specialists
from .specialists.risk_classifier_agent import RiskClassifierAgent
from .cross_validation import CrossValidationAgent
from .dpi_consolidator import consolidate_dpi_requirements


class AdvancedHSEOrchestrator:
    """
    Advanced orchestrator that uses PostgreSQL metadata for routing
    and Weaviate for document search
    """
    
    def __init__(
        self, 
        user_context: Dict[str, Any] = None, 
        vector_service=None,
        db_session: Session = None
    ):
        self.user_context = user_context or {}
        self.vector_service = vector_service
        self.db_session = db_session
        self.specialists = get_all_specialists()
        self.risk_classifier = self.specialists.get("risk_classifier")
        self.cross_validator = CrossValidationAgent()
        
        # Inject services into all specialists
        if vector_service or db_session:
            for specialist in self.specialists.values():
                if vector_service:
                    specialist.vector_service = vector_service
                if db_session:
                    specialist.db_session = db_session
            print(f"[AdvancedOrchestrator] Injected services into {len(self.specialists)} specialists")
        
        print(f"[AdvancedOrchestrator] Initialized with PostgreSQL + Weaviate integration")
    
    async def analyze_permit_advanced(
        self, 
        permit_data: Dict[str, Any], 
        permit_metadata: Dict[str, Any] = None,
        context_documents: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Advanced analysis using PostgreSQL metadata and Weaviate documents
        
        Args:
            permit_data: Basic permit data (title, description, etc.)
            permit_metadata: Extended metadata from PostgreSQL (risks, controls, history)
            context_documents: Pre-fetched documents from Weaviate
        """
        start_time = time.time()
        context_documents = context_documents or []
        permit_metadata = permit_metadata or {}
        
        try:
            print(f"\n[AdvancedOrchestrator] Starting advanced analysis for permit {permit_data.get('id')}")
            print(f"[DEBUG] permit_data type: {type(permit_data)}")
            print(f"[DEBUG] risk_mitigation_actions value: {permit_data.get('risk_mitigation_actions')}")
            print(f"[DEBUG] risk_mitigation_actions type: {type(permit_data.get('risk_mitigation_actions'))}")
            
            # Phase 1: Risk Classification using PostgreSQL metadata
            print("[AdvancedOrchestrator] Phase 1: Risk Classification with PostgreSQL metadata")
            classification_result = await self._classify_with_metadata(
                permit_data, 
                permit_metadata,
                context_documents
            )
            
            if not classification_result.get("classification_complete"):
                return self._create_error_result("Risk classification failed", start_time)
            
            # Phase 2: Parallel Specialist Analysis
            print("[AdvancedOrchestrator] Phase 2: Parallel Specialist Analysis")
            specialists_to_run = classification_result.get("specialists_to_activate", [])
            print(f"  Activating {len(specialists_to_run)} specialists in parallel: {specialists_to_run}")
            
            specialist_results = await self._run_specialists_parallel(
                permit_data,
                permit_metadata,
                classification_result,
                specialists_to_run
            )
            
            # Phase 3: Document Enhancement
            print("[AdvancedOrchestrator] Phase 3: Document Enhancement from Weaviate")
            enhanced_results = await self._enhance_with_documents(
                specialist_results,
                context_documents
            )
            
            # Phase 4: Cross-Validation
            print("[AdvancedOrchestrator] Phase 4: Cross-Validation and Integration")
            cross_validation_results = await self.cross_validator.validate_and_integrate(
                permit_data,
                enhanced_results,
                context_documents
            )
            
            # Phase 5: Consolidate Results
            print("[AdvancedOrchestrator] Phase 5: Consolidating Results")
            final_result = self._consolidate_advanced_results(
                permit_data,
                permit_metadata,
                classification_result,
                enhanced_results,
                context_documents,
                cross_validation_results,
                time.time() - start_time
            )
            
            print(f"[AdvancedOrchestrator] Analysis completed in {time.time() - start_time:.2f}s")
            return final_result
            
        except Exception as e:
            print(f"[AdvancedOrchestrator] Error during analysis: {e}")
            print(f"[AdvancedOrchestrator] Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            return self._create_error_result(str(e), start_time)
    
    async def _classify_with_metadata(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Classify risks using PostgreSQL metadata and comprehensive permit analysis
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
        
        # Analyze permit text content for implicit risks
        permit_text = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('work_type', '')}".lower()
        
        # Enhanced risk identification from permit content
        content_based_risks = []
        risk_indicators = {
            "mechanical": ["rotore", "taglierina", "motore", "pompa", "turbina", "compressore", "riduttore", "macchinari", "meccanico", "mechanical", "engine", "gearbox", "rotor", "cutter", "machinery"],
            "hot_work": ["saldatura", "taglio", "fiamma", "welding", "cutting", "torch", "torcia", "caldo", "hot", "plasma", "ossigeno", "acetilene"],
            "confined_space": ["serbatoio", "tank", "vessel", "recipiente", "confined", "confinato", "cisterna", "silos", "bunker"],
            "height": ["altezza", "quota", "ponteggio", "scala", "roof", "tetto", "height", "fall", "caduta", "scaffold"],
            "electrical": ["elettrico", "tensione", "quadro", "voltage", "electric", "electrical", "cavi", "cables", "interruttore"],
            "chemical": ["chimico", "tossico", "atex", "chemical", "sostanza", "substance", "acido", "solvente", "gas"],
            "pressure": ["pressione", "pressure", "compressore", "pneumatico", "idraulico", "hydraulic", "compressed"],
            "rotating": ["rotante", "rotating", "rotore", "rotor", "turbina", "turbine", "centrifuga", "centrifugal"]
        }
        
        for risk_type, keywords in risk_indicators.items():
            if any(keyword in permit_text for keyword in keywords):
                content_based_risks.append(risk_type)
                print(f"  [Content Analysis] Identified {risk_type} risk from permit content")
        
        # Get risk domains from metadata
        metadata_risks = []
        if permit_metadata.get("identified_risks"):
            for risk in permit_metadata["identified_risks"]:
                risk_type = risk.get("type", "").lower()
                if "hot" in risk_type or "weld" in risk_type or "flame" in risk_type:
                    metadata_risks.append("hot_work")
                if "confined" in risk_type or "tank" in risk_type:
                    metadata_risks.append("confined_space")
                if "height" in risk_type or "fall" in risk_type:
                    metadata_risks.append("height")
                if "electric" in risk_type or "voltage" in risk_type:
                    metadata_risks.append("electrical")
                if "chemical" in risk_type or "toxic" in risk_type:
                    metadata_risks.append("chemical")
        
        # Run risk classifier with enhanced context and existing permit data
        if self.risk_classifier:
            print(f"[AdvancedOrchestrator] Analyzing existing permit with comprehensive evaluation")
            classification = await self.risk_classifier.analyze(permit_data, enhanced_context)
            
            # Add evaluation of existing DPI and mitigation actions
            existing_dpi = permit_data.get('dpi_required', [])
            existing_actions = permit_data.get('risk_mitigation_actions', [])
            
            # COMPLETENESS EVALUATION
            completeness_score = self._evaluate_permit_completeness(permit_data, content_based_risks)
            print(f"[AdvancedOrchestrator] Permit completeness score: {completeness_score}/10")
            
            classification["permit_completeness"] = {
                "score": completeness_score,
                "missing_elements": self._identify_missing_elements(permit_data, content_based_risks),
                "content_based_risks": content_based_risks,
                "adequacy_assessment": self._assess_measures_adequacy(permit_data, content_based_risks)
            }
            
            if existing_dpi or existing_actions:
                print(f"[AdvancedOrchestrator] Found existing DPI: {len(existing_dpi)} items, Actions: {len(existing_actions)} items")
                classification["existing_measures"] = {
                    "dpi_provided": existing_dpi,
                    "actions_provided": existing_actions,
                    "evaluation_mode": "enhancement"  # Indicates we should enhance/correct existing measures
                }
        else:
            print("[AdvancedOrchestrator] Error: Risk classifier not available")
            return {"classification_complete": False, "error": "Risk classifier not initialized"}
        
        # Merge all risk sources
        all_risk_types = list(set(content_based_risks + metadata_risks))
        if all_risk_types:
            print(f"  [Classifier] Total risk types identified: {len(set(all_risk_types))}")
            existing_specialists = classification.get("specialists_to_activate", [])
            all_specialists = list(set(existing_specialists + all_risk_types))
            classification["specialists_to_activate"] = all_specialists
            classification["content_risks_added"] = content_based_risks
            classification["metadata_risks_added"] = metadata_risks
        
        # Store full context for specialists
        classification["documents"] = context_documents
        classification["permit_metadata"] = permit_metadata
        
        return classification
    
    async def _run_specialists_parallel(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification: Dict[str, Any],
        specialists_to_run: List[str]
    ) -> Dict[str, Any]:
        """
        Run multiple specialists in parallel for faster analysis
        """
        
        results = {}
        tasks = []
        
        for specialist_name in specialists_to_run:
            clean_name = specialist_name.replace("_specialist", "")
            
            specialist = self.specialists.get(clean_name)
            if specialist and specialist.name != "Risk_Classifier":
                # Create task for parallel execution
                task = self._run_single_specialist_enhanced(
                    specialist,
                    permit_data,
                    permit_metadata,
                    classification
                )
                tasks.append((specialist.name, task))
        
        # Execute all specialists in parallel
        if tasks:
            print(f"  Running {len(tasks)} specialists in parallel...")
            specialist_outputs = await asyncio.gather(
                *[task for _, task in tasks],
                return_exceptions=True
            )
            
            for i, (name, _) in enumerate(tasks):
                if not isinstance(specialist_outputs[i], Exception):
                    results[name] = specialist_outputs[i]
                    print(f"    ✓ {name} completed")
                else:
                    print(f"    ✗ {name} failed: {specialist_outputs[i]}")
                    results[name] = {"error": str(specialist_outputs[i])}
        
        return results
    
    async def _run_single_specialist_enhanced(
        self,
        specialist,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a single specialist with enhanced context
        """
        
        # Build specialist context with metadata
        context = {
            "classification": classification,
            "user_context": self.user_context,
            "documents": classification.get("documents", []),
            "permit_metadata": permit_metadata,
            "equipment_list": permit_metadata.get("equipment_list", []),
            "chemical_list": permit_metadata.get("chemical_list", []),
            "historical_data": {
                "previous_permits": permit_metadata.get("previous_permits", []),
                "incidents": permit_metadata.get("incidents", []),
                "near_misses": permit_metadata.get("near_misses", [])
            }
        }
        
        # Get specialist analysis
        result = await specialist.analyze(permit_data, context)
        
        # Add metadata-based enhancements
        if permit_metadata.get("site_specific_controls"):
            result["site_specific_controls"] = permit_metadata["site_specific_controls"]
        
        if permit_metadata.get("mandatory_ppe"):
            existing_ppe = result.get("dpi_requirements", [])
            result["dpi_requirements"] = list(set(existing_ppe + permit_metadata["mandatory_ppe"]))
        
        return result
    
    async def _enhance_with_documents(
        self,
        specialist_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Enhance specialist results with relevant documents from Weaviate
        """
        
        enhanced_results = specialist_results.copy()
        
        # Map documents to relevant specialists
        doc_mapping = {
            "hot_work": ["saldatura", "taglio", "fiamma", "welding", "cutting", "caldo", "hot", "torcia", "torch"],
            "confined_space": ["spazio confinato", "serbatoio", "tank", "vessel", "confined", "confinato"],
            "height": ["altezza", "caduta", "ponteggio", "scaffold", "height", "fall", "quota"],
            "electrical": ["elettrico", "tensione", "quadro", "voltage", "electric", "electrical"],
            "chemical": ["chimico", "tossico", "atex", "chemical", "sostanza", "substance"],
            "mechanical": ["meccanico", "mechanical", "pressione", "pressure", "macchinari", "machinery", "motore", "engine", "riduttore", "gearbox", "rotore", "rotor", "turbina", "turbine", "pompa", "pump", "compressore", "compressor", "taglierina", "cutter"]
        }
        
        for specialist_name, result in enhanced_results.items():
            if isinstance(result, dict) and "error" not in result:
                # Find relevant documents for this specialist
                relevant_docs = []
                clean_name = specialist_name.lower().replace("_specialist", "")
                
                if clean_name in doc_mapping:
                    keywords = doc_mapping[clean_name]
                    for doc in context_documents:
                        doc_title = doc.get("title", "").lower()
                        doc_keywords = doc.get("keywords", [])
                        doc_content = doc.get("content_summary", "").lower()
                        
                        # Check title, keywords, and content summary
                        title_match = any(keyword in doc_title for keyword in keywords)
                        keyword_match = any(keyword.lower() in [k.lower() for k in doc_keywords] for keyword in keywords)
                        content_match = any(keyword in doc_content for keyword in keywords)
                        
                        if title_match or keyword_match or content_match:
                            relevant_docs.append(doc)
                            print(f"      Document '{doc.get('title')}' matched for {specialist_name} (title:{title_match}, keywords:{keyword_match}, content:{content_match})")
                
                if relevant_docs:
                    result["relevant_documents"] = relevant_docs[:3]  # Top 3
                    result["document_citations"] = [
                        f"[FONTE: Documento Aziendale] {doc.get('title')}"
                        for doc in relevant_docs[:3]
                    ]
                    print(f"    Enhanced {specialist_name} with {len(relevant_docs)} documents")
        
        return enhanced_results
    
    def _consolidate_advanced_results(
        self,
        permit_data: Dict[str, Any],
        permit_metadata: Dict[str, Any],
        classification: Dict[str, Any],
        specialist_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        cross_validation_results: Dict[str, Any],
        processing_time: float
    ) -> Dict[str, Any]:
        """
        Consolidate all results into final advanced format
        """
        
        # Collect all identified risks
        all_risks = []
        all_controls = []
        all_dpi = []
        all_permits = []
        
        # Initialize suggested measures EARLY (before they are used)
        suggested_dpi = []
        suggested_actions = []
        dpi_issues = []
        action_issues = []
        
        # Get existing measures for comparison
        existing_dpi = permit_data.get('dpi_required', [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        
        # Add risks from metadata
        if permit_metadata.get("identified_risks"):
            for risk in permit_metadata["identified_risks"]:
                all_risks.append({
                    "type": risk.get("type"),
                    "source": "PostgreSQL Metadata",
                    "severity": risk.get("severity", "media")
                })
        
        # Add risks from specialists and evaluate their recommendations vs existing measures
        for specialist_name, result in specialist_results.items():
            if "error" not in result:
                all_risks.extend(result.get("risks_identified", []))
                all_controls.extend(result.get("control_measures", []))
                
                # Evaluate specialist DPI recommendations against existing DPI
                specialist_dpi = result.get("dpi_requirements", [])
                for dpi in specialist_dpi:
                    dpi_name = dpi if isinstance(dpi, str) else dpi.get('type', str(dpi))
                    
                    # Check if this DPI is missing from existing ones
                    if not self._is_dpi_covered(dpi_name, existing_dpi):
                        suggested_dpi.append({
                            "item": dpi,
                            "reason": f"Richiesto da {specialist_name}",
                            "priority": "alta",
                            "status": "mancante"
                        })
                
                # Evaluate specialist action recommendations vs existing actions
                specialist_controls = result.get("control_measures", [])
                for control in specialist_controls:
                    if not self._is_action_covered(control, existing_actions):
                        suggested_actions.append({
                            "action": control,
                            "reason": f"Raccomandato da {specialist_name}",
                            "priority": "media",
                            "status": "mancante"
                        })
                
                all_permits.extend(result.get("permits_required", []))
        
        # Remove duplicates - handle both strings and dicts
        all_controls = list(set(all_controls))
        
        # Consolidate DPI using intelligent consolidation system
        print(f"[AdvancedOrchestrator] Consolidating {len(all_dpi)} DPI items to prevent duplicates")
        all_dpi = consolidate_dpi_requirements(all_dpi)
        print(f"[AdvancedOrchestrator] After consolidation: {len(all_dpi)} DPI items")
        
        all_permits = list(set(all_permits))
        
        # Add site-specific requirements from metadata
        if permit_metadata.get("site_requirements"):
            all_controls.extend(permit_metadata["site_requirements"])
        
        # Build executive summary
        critical_issues = len([r for r in all_risks if 
                              isinstance(r, dict) and 
                              r.get("severity") in ["critica", "alta"]])
        
        # Create action items (temporarily use old method to avoid error)
        action_items = self._create_advanced_action_items(
            all_controls, all_dpi, all_permits, permit_metadata
        )
        
        # TODO: Fix and re-enable specific action items
        # action_items = self._create_specific_action_items(
        #     permit_data, all_controls, all_dpi, all_permits, 
        #     permit_metadata, context_documents, specialist_results,
        #     suggested_dpi, suggested_actions
        # )
        
        # Add cross-validation enhanced action items
        if cross_validation_results.get("enhanced_action_items"):
            action_items.extend(cross_validation_results["enhanced_action_items"])
        
        return {
            "analysis_id": f"advanced_{int(time.time())}_{permit_data.get('id')}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": True,
            "confidence_score": 0.90,  # High confidence with metadata
            "processing_time": round(processing_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "orchestrator_version": "Advanced-2.0",
            
            # Data sources used
            "data_sources": {
                "postgresql_metadata": bool(permit_metadata),
                "weaviate_documents": len(context_documents),
                "historical_data": bool(permit_metadata.get("historical_data")),
                "site_specific_data": bool(permit_metadata.get("site_specific_risks"))
            },
            
            # Results
            "executive_summary": {
                "overall_score": self._calculate_overall_score(classification, critical_issues, suggested_dpi, suggested_actions),
                "critical_issues": critical_issues,
                "recommendations": len(suggested_dpi + suggested_actions),
                "compliance_level": self._determine_compliance_level(classification, critical_issues),
                "estimated_completion_time": f"{len(action_items)*2}-{len(action_items)*4} ore",
                "key_findings": self._extract_enhanced_key_findings(all_risks, permit_metadata, classification),
                "next_steps": self._generate_enhanced_next_steps(all_permits, critical_issues, classification),
                "permit_completeness": f"{classification.get('permit_completeness', {}).get('score', 0)}/10",
                "missing_elements": len(classification.get('permit_completeness', {}).get('missing_elements', [])),
                "adequacy_summary": self._create_adequacy_summary(classification.get('permit_completeness', {}))
            },
            
            "action_items": action_items,
            "agents_involved": ["Risk_Classifier"] + list(specialist_results.keys()),
            
            # Required schema fields
            "citations": self._create_citations(context_documents, permit_metadata),
            "completion_roadmap": self._create_completion_roadmap(action_items, all_permits),
            "ai_version": "Advanced-AI-2.0",
            
            # Enhanced metadata
            "metadata_insights": {
                "historical_incidents": len(permit_metadata.get("incidents", [])),
                "similar_permits": len(permit_metadata.get("previous_permits", [])),
                "site_specific_risks": len(permit_metadata.get("site_specific_risks", [])),
                "equipment_hazards": len(permit_metadata.get("equipment_risks", []))
            },
            
            # Evaluation of existing measures vs recommendations
            "measures_evaluation": {
                "existing_dpi": existing_dpi,
                "existing_actions": existing_actions,
                "suggested_additional_dpi": suggested_dpi,
                "suggested_additional_actions": suggested_actions,
                "dpi_adequacy": "adeguato" if len(suggested_dpi) == 0 else "insufficiente",
                "actions_adequacy": "adeguate" if len(suggested_actions) == 0 else "insufficienti",
                "improvement_needed": len(suggested_dpi) > 0 or len(suggested_actions) > 0
            },
            
            # Cross-validation results
            "cross_validation": {
                "validation_performed": cross_validation_results.get("validation_complete", False),
                "conflicts_identified": len(cross_validation_results.get("conflicts_identified", [])),
                "gaps_identified": len(cross_validation_results.get("gaps_identified", [])),
                "risk_interactions": len(cross_validation_results.get("risk_interactions", [])),
                "integration_recommendations": cross_validation_results.get("integration_recommendations", []),
                "enhanced_actions_added": len(cross_validation_results.get("enhanced_action_items", []))
            },
            
            # Performance metrics
            "performance_metrics": {
                "total_processing_time": round(processing_time, 2),
                "specialists_activated": len(specialist_results),
                "parallel_execution": True,
                "risks_identified": len(all_risks),
                "documents_analyzed": len(context_documents),
                "metadata_enhanced": True,
                "cross_validation_performed": True
            }
        }
    
    def _create_advanced_action_items(
        self,
        controls: List[str],
        dpi: List[str],
        permits: List[str],
        metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create action items with priority based on metadata
        """
        
        action_items = []
        item_id = 1
        
        # Priority 1: Historical incident-based controls
        if metadata.get("incident_based_controls"):
            for control in metadata["incident_based_controls"]:
                action_items.append({
                    "id": f"ACT_{item_id:03d}",
                    "type": "incident_prevention",
                    "priority": "critica",
                    "title": f"[STORICO INCIDENTI] {control[:50]}",
                    "description": control,
                    "suggested_action": f"Implementare controllo basato su incidente precedente: {control}",
                    "consequences_if_ignored": "Alto rischio ripetizione incidente",
                    "references": ["Analisi incidenti storici"],
                    "estimated_effort": "30-60 minuti",
                    "responsible_role": "RSPP",
                    "frontend_display": {
                        "color": "red",
                        "icon": "alert-triangle",
                        "category": "Prevenzione Incidenti"
                    }
                })
                item_id += 1
        
        # Priority 2: Permits
        for permit in permits:
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "permit_requirement",
                "priority": "critica",
                "title": f"Ottenere {permit}",
                "description": f"Permesso obbligatorio: {permit}",
                "suggested_action": f"Compilare e approvare {permit} prima inizio lavori",
                "consequences_if_ignored": "Lavori non autorizzati - violazione procedure",
                "references": ["D.Lgs 81/08", "Procedure aziendali"],
                "estimated_effort": "30-60 minuti",
                "responsible_role": "Preposto",
                "frontend_display": {
                    "color": "red",
                    "icon": "file-check",
                    "category": "Permessi Obbligatori"
                }
            })
            item_id += 1
        
        # Priority 3: Site-specific controls
        if metadata.get("site_specific_controls"):
            for control in metadata["site_specific_controls"][:5]:
                action_items.append({
                    "id": f"ACT_{item_id:03d}",
                    "type": "site_control",
                    "priority": "alta",
                    "title": f"[SITO] {control[:40]}",
                    "description": control,
                    "suggested_action": control,
                    "consequences_if_ignored": "Non conformità requisiti sito",
                    "references": ["Requisiti specifici del sito"],
                    "estimated_effort": "variabile",
                    "responsible_role": "Site Manager",
                    "frontend_display": {
                        "color": "orange",
                        "icon": "map-pin",
                        "category": "Controlli Sito"
                    }
                })
                item_id += 1
        
        # Priority 4: DPI (enhanced with consolidation info)
        for dpi_item in dpi[:10]:
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
            
            # Limit title length to avoid database errors
            dpi_title_short = dpi_title[:30] if len(dpi_title) > 30 else dpi_title
            
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "dpi_requirement",
                "priority": priority,
                "title": f"Fornire {dpi_title_short}",
                "description": dpi_description,
                "suggested_action": f"Verificare disponibilità e distribuzione {dpi_title}",
                "consequences_if_ignored": "Esposizione diretta ai rischi",
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
        
        return action_items
    
    def _extract_key_findings(
        self,
        risks: List,
        metadata: Dict[str, Any]
    ) -> List[str]:
        """
        Extract key findings including historical data
        """
        
        findings = []
        
        # Add historical insights
        if metadata.get("incidents"):
            findings.append(f"⚠️ STORICO: {len(metadata['incidents'])} incidenti simili registrati")
        
        # Add critical risks
        for risk in risks:
            if isinstance(risk, dict) and risk.get("severity") == "critica":
                findings.append(risk.get("description", "Rischio critico identificato"))
                if len(findings) >= 5:
                    break
        
        # Add site-specific warnings
        if metadata.get("site_specific_risks"):
            findings.append(f"📍 SITO: {len(metadata['site_specific_risks'])} rischi specifici del sito")
        
        return findings[:5]
    
    def _generate_next_steps(self, permits: List[str], critical_issues: int) -> List[str]:
        """
        Generate prioritized next steps
        """
        
        steps = []
        
        if permits:
            steps.append(f"1. Ottenere {len(permits)} permessi richiesti")
        
        if critical_issues > 0:
            steps.append(f"2. Risolvere {critical_issues} problemi critici")
        
        steps.extend([
            "3. Briefing sicurezza con riferimenti storici",
            "4. Verifica DPI e controlli sito-specifici"
        ])
        
        return steps[:4]
    
    def _is_dpi_covered(self, required_dpi: str, existing_dpi: List[str]) -> bool:
        """Check if a required DPI is already covered by existing DPI"""
        if not existing_dpi:
            return False
        
        # Normalize strings for comparison
        required_lower = required_dpi.lower()
        existing_lower = [item.lower() for item in existing_dpi]
        
        # Check for exact match
        if required_lower in existing_lower:
            return True
        
        # Check for semantic matches
        dpi_mappings = {
            "casco": ["helmet", "hard hat", "elmetto"],
            "guanti": ["gloves", "guanto"],
            "occhiali": ["goggles", "glasses", "eye protection"],
            "scarpe": ["shoes", "boots", "calzature"],
            "respiratore": ["respirator", "mask", "ffp"],
            "imbracatura": ["harness", "safety harness"]
        }
        
        for existing in existing_lower:
            if required_lower in existing or existing in required_lower:
                return True
            
            # Check semantic mappings
            for main_type, synonyms in dpi_mappings.items():
                if main_type in required_lower or any(syn in required_lower for syn in synonyms):
                    if main_type in existing or any(syn in existing for syn in synonyms):
                        return True
        
        return False
    
    def _is_action_covered(self, required_action: str, existing_actions: List[str]) -> bool:
        """Check if a required action is already covered by existing actions"""
        if not existing_actions:
            return False
        
        required_lower = required_action.lower()
        
        # Check each existing action
        for existing in existing_actions:
            existing_lower = str(existing).lower()
            
            # Check for partial matches in key concepts
            action_keywords = [
                "fire watch", "gas test", "ventilazione", "ventilation", 
                "isolamento", "lockout", "tagout", "loto", "monitoraggio",
                "supervisione", "formazione", "briefing", "emergency", "emergenza"
            ]
            
            for keyword in action_keywords:
                if keyword in required_lower and keyword in existing_lower:
                    return True
            
            # Check for semantic similarity (basic)
            if len(required_lower) > 10 and len(existing_lower) > 10:
                # Simple overlap check
                required_words = set(required_lower.split())
                existing_words = set(existing_lower.split())
                overlap = len(required_words.intersection(existing_words))
                if overlap >= 2:  # At least 2 words in common
                    return True
        
        return False
    
    def _evaluate_permit_completeness(self, permit_data: Dict[str, Any], identified_risks: List[str]) -> int:
        """Evaluate permit completeness on a scale of 1-10"""
        score = 0
        
        # Basic information completeness (0-3 points)
        if permit_data.get('title') and len(permit_data.get('title', '')) > 5:
            score += 1
        if permit_data.get('description') and len(permit_data.get('description', '')) > 20:
            score += 1
        if permit_data.get('work_type'):
            score += 1
        
        # Risk assessment completeness (0-3 points)  
        if permit_data.get('dpi_required') and len(permit_data.get('dpi_required', [])) > 0:
            score += 1
        if permit_data.get('risk_mitigation_actions') and len(permit_data.get('risk_mitigation_actions', [])) > 0:
            score += 1
        if permit_data.get('location'):
            score += 1
        
        # Risk coverage adequacy (0-4 points)
        if identified_risks:
            # Penalize for each major risk type that lacks specific measures
            high_risk_types = ['hot_work', 'confined_space', 'electrical', 'height']
            covered_high_risks = 0
            for risk_type in high_risk_types:
                if risk_type in identified_risks:
                    # Check if appropriate measures exist
                    if self._has_appropriate_measures_for_risk(permit_data, risk_type):
                        covered_high_risks += 1
            
            score += min(4, covered_high_risks)
        else:
            score += 2  # Baseline if no high risks identified
        
        return min(10, score)
    
    def _identify_missing_elements(self, permit_data: Dict[str, Any], identified_risks: List[str]) -> List[str]:
        """Identify missing elements in the permit"""
        missing = []
        
        if not permit_data.get('title') or len(permit_data.get('title', '')) < 5:
            missing.append("Titolo dettagliato")
        if not permit_data.get('description') or len(permit_data.get('description', '')) < 20:
            missing.append("Descrizione dettagliata del lavoro")
        if not permit_data.get('location'):
            missing.append("Localizzazione specifica")
        if not permit_data.get('dpi_required') or len(permit_data.get('dpi_required', [])) == 0:
            missing.append("DPI richiesti")
        if not permit_data.get('risk_mitigation_actions') or len(permit_data.get('risk_mitigation_actions', [])) == 0:
            missing.append("Azioni di mitigazione dei rischi")
        
        # Risk-specific missing elements
        for risk_type in identified_risks:
            if risk_type == 'hot_work' and not self._has_hot_work_measures(permit_data):
                missing.append("Misure specifiche per lavori a caldo")
            elif risk_type == 'confined_space' and not self._has_confined_space_measures(permit_data):
                missing.append("Misure specifiche per spazi confinati")
            elif risk_type == 'mechanical' and not self._has_mechanical_measures(permit_data):
                missing.append("Misure specifiche per rischi meccanici")
        
        return missing
    
    def _assess_measures_adequacy(self, permit_data: Dict[str, Any], identified_risks: List[str]) -> Dict[str, str]:
        """Assess adequacy of existing measures"""
        assessment = {}
        
        existing_dpi = permit_data.get('dpi_required', [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        
        for risk_type in identified_risks:
            adequacy = self._check_risk_measures_adequacy(risk_type, existing_dpi, existing_actions)
            assessment[risk_type] = adequacy
        
        return assessment
    
    def _has_appropriate_measures_for_risk(self, permit_data: Dict[str, Any], risk_type: str) -> bool:
        """Check if permit has appropriate measures for specific risk type"""
        existing_dpi = [str(item).lower() for item in permit_data.get('dpi_required', [])]
        existing_actions = [str(item).lower() for item in permit_data.get('risk_mitigation_actions', [])]
        
        if risk_type == 'hot_work':
            return any('ignifug' in item or 'fire' in item for item in existing_dpi) or \
                   any('fire watch' in action or 'estintore' in action for action in existing_actions)
        elif risk_type == 'confined_space':
            return any('respirator' in item or 'ffp' in item for item in existing_dpi) or \
                   any('ventilaz' in action or 'gas test' in action for action in existing_actions)
        elif risk_type == 'mechanical':
            return any('guant' in item or 'gloves' in item for item in existing_dpi) or \
                   any('lockout' in action or 'isolamento' in action for action in existing_actions)
        elif risk_type == 'electrical':
            return any('isolant' in item or 'electrical' in item for item in existing_dpi) or \
                   any('tagout' in action or 'tensione' in action for action in existing_actions)
        
        return len(existing_dpi) > 0 or len(existing_actions) > 0
    
    def _has_hot_work_measures(self, permit_data: Dict[str, Any]) -> bool:
        """Check for hot work specific measures"""
        text = f"{permit_data.get('dpi_required', [])} {permit_data.get('risk_mitigation_actions', [])}".lower()
        return 'ignifug' in text or 'fire watch' in text or 'estintore' in text
    
    def _has_confined_space_measures(self, permit_data: Dict[str, Any]) -> bool:
        """Check for confined space specific measures"""
        text = f"{permit_data.get('dpi_required', [])} {permit_data.get('risk_mitigation_actions', [])}".lower()
        return 'respirator' in text or 'ventilaz' in text or 'gas test' in text
    
    def _has_mechanical_measures(self, permit_data: Dict[str, Any]) -> bool:
        """Check for mechanical work specific measures"""
        text = f"{permit_data.get('dpi_required', [])} {permit_data.get('risk_mitigation_actions', [])}".lower()
        return 'lockout' in text or 'isolamento' in text or 'arresto' in text
    
    def _check_risk_measures_adequacy(self, risk_type: str, existing_dpi: List, existing_actions: List) -> str:
        """Check adequacy of measures for specific risk type"""
        if not existing_dpi and not existing_actions:
            return "insufficiente"
        
        text = f"{existing_dpi} {existing_actions}".lower()
        
        risk_requirements = {
            'mechanical': ['guant', 'lockout', 'isolamento', 'arresto'],
            'hot_work': ['ignifug', 'fire watch', 'estintore', 'fireproof'],
            'confined_space': ['respirator', 'ventilaz', 'gas test', 'ffp'],
            'electrical': ['isolant', 'tagout', 'tensione', 'electrical'],
            'chemical': ['respirator', 'guant', 'tuta', 'ventilaz'],
            'height': ['imbracatura', 'harness', 'casco', 'anticaduta']
        }
        
        if risk_type in risk_requirements:
            requirements = risk_requirements[risk_type]
            if any(req in text for req in requirements):
                return "adeguato"
            else:
                return "parziale"
        
        return "da_verificare"
    
    def _calculate_overall_score(self, classification: Dict, critical_issues: int, suggested_dpi: List, suggested_actions: List) -> float:
        """Calculate enhanced overall score"""
        base_score = 1.0
        
        # Penalize for completeness issues
        completeness = classification.get('permit_completeness', {})
        completeness_score = completeness.get('score', 0) / 10.0
        base_score *= completeness_score
        
        # Penalize for critical issues
        if critical_issues > 2:
            base_score *= 0.2
        elif critical_issues > 0:
            base_score *= 0.5
        
        # Penalize for missing measures
        if len(suggested_dpi) > 3:
            base_score *= 0.7
        elif len(suggested_dpi) > 0:
            base_score *= 0.8
            
        if len(suggested_actions) > 3:
            base_score *= 0.6
        elif len(suggested_actions) > 0:
            base_score *= 0.8
        
        return round(max(0.1, base_score), 2)
    
    def _determine_compliance_level(self, classification: Dict, critical_issues: int) -> str:
        """Determine compliance level based on analysis"""
        completeness_score = classification.get('permit_completeness', {}).get('score', 0)
        
        if critical_issues > 2:
            return "NON CONFORME - Rischi critici non gestiti"
        elif completeness_score < 5:
            return "INCOMPLETO - Informazioni mancanti"
        elif completeness_score < 7:
            return "PARZIALE - Miglioramenti necessari"
        elif critical_issues > 0:
            return "ACCETTABILE - Con raccomandazioni"
        else:
            return "CONFORME - Standard soddisfatti"
    
    def _extract_enhanced_key_findings(self, risks: List, metadata: Dict, classification: Dict) -> List[str]:
        """Extract enhanced key findings including completeness analysis"""
        findings = []
        
        # Completeness findings
        completeness = classification.get('permit_completeness', {})
        missing_elements = completeness.get('missing_elements', [])
        if missing_elements:
            findings.append(f"🔍 COMPLETEZZA: {len(missing_elements)} elementi mancanti")
        
        # Risk-based findings
        content_risks = classification.get('content_based_risks', [])
        if content_risks:
            findings.append(f"⚠️ RISCHI IDENTIFICATI: {', '.join(content_risks).replace('_', ' ').title()}")
        
        # Add historical insights
        if metadata.get("incidents"):
            findings.append(f"📊 STORICO: {len(metadata['incidents'])} incidenti simili registrati")
        
        # Add site-specific warnings
        if metadata.get("site_specific_risks"):
            findings.append(f"📍 SITO: {len(metadata['site_specific_risks'])} rischi specifici del sito")
        
        # Adequacy findings
        adequacy_assessment = completeness.get('adequacy_assessment', {})
        inadequate_risks = [risk for risk, adequacy in adequacy_assessment.items() if adequacy == 'insufficiente']
        if inadequate_risks:
            findings.append(f"❌ MISURE INADEGUATE: {', '.join(inadequate_risks).replace('_', ' ').title()}")
        
        return findings[:6]  # Limit to top 6 findings
    
    def _generate_enhanced_next_steps(self, permits: List, critical_issues: int, classification: Dict) -> List[str]:
        """Generate enhanced next steps based on complete analysis"""
        steps = []
        
        # Completeness-based steps
        missing_elements = classification.get('permit_completeness', {}).get('missing_elements', [])
        if missing_elements:
            steps.append(f"1. Completare {len(missing_elements)} elementi mancanti nel permesso")
        
        # Permit-based steps
        if permits:
            steps.append(f"2. Ottenere {len(permits)} permessi/autorizzazioni richiesti")
        
        # Risk-based steps
        if critical_issues > 0:
            steps.append(f"3. Risolvere {critical_issues} problemi critici identificati")
        
        # Standard steps
        content_risks = classification.get('content_based_risks', [])
        if 'mechanical' in content_risks:
            steps.append("4. Implementare procedura LOTO per isolamento energie")
        
        steps.extend([
            "5. Briefing sicurezza con focus su rischi identificati",
            "6. Verifica finale conformità prima inizio lavori"
        ])
        
        return steps[:6]  # Limit to top 6 steps
    
    def _create_specific_action_items(
        self,
        permit_data: Dict[str, Any],
        controls: List[str],
        dpi: List[str],
        permits: List[str],
        metadata: Dict[str, Any],
        documents: List[Dict[str, Any]],
        specialist_results: Dict[str, Any],
        suggested_dpi: List,
        suggested_actions: List
    ) -> List[Dict[str, Any]]:
        """Create specific, non-generic action items based on work type and documents"""
        
        print(f"[DEBUG] _create_specific_action_items called with documents type: {type(documents)}, suggested_dpi type: {type(suggested_dpi)}, suggested_actions type: {type(suggested_actions)}")
        
        action_items = []
        item_id = 1
        work_description = f"{permit_data.get('title', '')} {permit_data.get('description', '')}".lower()
        
        # SPECIFIC ACTIONS FOR ROTOR/CUTTER REPLACEMENT
        if "rotore" in work_description and "taglierina" in work_description:
            
            # Find relevant documents (check if documents is a list)
            if not isinstance(documents, list):
                documents = []
            
            loto_doc = next((d for d in documents if 'loto' in str(d).lower()), None)
            taglierina_doc = next((d for d in documents if 'taglierina' in str(d).lower()), None)
            dpi_doc = next((d for d in documents if 'dpi' in str(d).lower() and 'meccan' in str(d).lower()), None)
            
            # SPECIFIC MECHANICAL ACTIONS
            if "Mechanical_Specialist" in specialist_results:
                mech_result = specialist_results["Mechanical_Specialist"]
                
                # Check for LOTO implementation
                risk_mitigation_actions = permit_data.get('risk_mitigation_actions', [])
                if isinstance(risk_mitigation_actions, list) and not any("loto" in action.lower() for action in risk_mitigation_actions):
                    action_items.append({
                        "id": f"ACT_{item_id:03d}",
                        "type": "procedura_critica",
                        "priority": "critica",
                        "title": "Implementare Procedura LOTO completa",
                        "description": "Per sostituzione rotore taglierina: applicare procedura LOTO con doppio blocco meccanico",
                        "suggested_action": "1) Arrestare taglierina con pulsante normale\n2) Premere arresto emergenza\n3) Sezionare interruttore elettrico principale\n4) Applicare lucchetto personale su interruttore\n5) Applicare blocco meccanico su rotore (cunei o perni)\n6) Verificare zero energia con tentativo avvio\n7) Appendere cartellino LOTO",
                        "consequences_if_ignored": "Avvio accidentale durante sostituzione - rischio amputazione/morte",
                        "references": ["[DOC: PROC-LOTO-001] Procedura LOTO aziendale"] if loto_doc else ["Procedura LOTO standard industriale"],
                        "estimated_effort": "20 minuti",
                        "responsible_role": "Manutentore Meccanico Qualificato",
                        "frontend_display": {
                            "color": "red",
                            "icon": "lock",
                            "category": "Isolamento Energie"
                        }
                    })
                    item_id += 1
                
                # Specific rotor handling
                action_items.append({
                    "id": f"ACT_{item_id:03d}",
                    "type": "procedura_specifica",
                    "priority": "alta",
                    "title": "Procedura rimozione rotore taglierina",
                    "description": "Sequenza specifica per rimozione sicura rotore con lame",
                    "suggested_action": "1) Indossare guanti antitaglio livello 5\n2) Utilizzare estrattore rotore dedicato (non improvvisare)\n3) Supportare peso rotore con paranchi (peso stimato >50kg)\n4) Proteggere lame con carter temporanei durante movimentazione\n5) Depositare rotore su supporto stabile con lame protette",
                    "consequences_if_ignored": "Lesioni da taglio grave, ernia da sforzo, schiacciamento",
                    "references": ["[DOC: IO-TAGL-003] Istruzione Operativa Taglierine"] if taglierina_doc else ["Manuale costruttore taglierina"],
                    "estimated_effort": "45 minuti",
                    "responsible_role": "Manutentore + Assistente",
                    "frontend_display": {
                        "color": "orange",
                        "icon": "settings",
                        "category": "Procedure Operative"
                    }
                })
                item_id += 1
            
            # SPECIFIC DPI FOR ROTOR WORK
            missing_critical_dpi = []
            existing_dpi = [d.lower() for d in permit_data.get('dpi_required', [])]
            
            if not any("antitaglio" in d or "livello 5" in d or "en 388" in d for d in existing_dpi):
                missing_critical_dpi.append("Guanti antitaglio livello 5 EN 388:2016 (4X44F)")
                
            if not any("laterale" in d or "laterali" in d for d in existing_dpi):
                missing_critical_dpi.append("Occhiali protezione con schermi laterali EN 166")
                
            if not any("s3" in d or "antiperforazione" in d for d in existing_dpi):
                missing_critical_dpi.append("Scarpe S3 HRO con puntale rinforzato")
            
            if missing_critical_dpi:
                action_items.append({
                    "id": f"ACT_{item_id:03d}",
                    "type": "dpi_specifici",
                    "priority": "critica",
                    "title": "DPI specifici mancanti per rotore taglierina",
                    "description": f"DPI critici non presenti: {', '.join(missing_critical_dpi)}",
                    "suggested_action": f"Fornire IMMEDIATAMENTE:\n" + "\n".join([f"• {dpi}" for dpi in missing_critical_dpi]),
                    "consequences_if_ignored": "Lesioni gravi da taglio/perforazione durante manipolazione rotore",
                    "references": ["[DOC: STD-DPI-MECC] Standard DPI Manutenzione Meccanica"] if dpi_doc else ["EN 388:2016 - Guanti protezione meccanica"],
                    "estimated_effort": "10 minuti",
                    "responsible_role": "Magazzino DPI",
                    "frontend_display": {
                        "color": "red",
                        "icon": "shield",
                        "category": "DPI Critici"
                    }
                })
                item_id += 1
            
            # SPECIFIC RISK NOT EVALUATED
            if not any("inerzia" in str(permit_data).lower() or "inertia" in str(permit_data).lower()):
                action_items.append({
                    "id": f"ACT_{item_id:03d}",
                    "type": "rischio_non_valutato",
                    "priority": "alta",
                    "title": "Rischio inerzia rotore non valutato",
                    "description": "Rotore taglierina può continuare a ruotare per inerzia dopo arresto motore",
                    "suggested_action": "1) Attendere MINIMO 5 minuti dopo arresto per dissipazione inerzia\n2) Verificare arresto completo visivamente\n3) Applicare freno meccanico se disponibile\n4) Mai toccare rotore prima di verifica arresto totale",
                    "consequences_if_ignored": "Trascinamento/amputazione da rotore ancora in movimento",
                    "references": ["Fisica meccanica rotori - massa elevata = alta inerzia"],
                    "estimated_effort": "5 minuti attesa obbligatoria",
                    "responsible_role": "Operatore",
                    "frontend_display": {
                        "color": "yellow",
                        "icon": "alert-triangle",
                        "category": "Rischi Non Valutati"
                    }
                })
                item_id += 1
        
        # Add remaining generic items only if no specific ones
        if len(action_items) < 3:
            # Add the old generic method items
            generic_items = self._create_advanced_action_items(controls, dpi, permits, metadata)
            action_items.extend(generic_items[:5 - len(action_items)])
        
        return action_items
    
    def _create_adequacy_summary(self, completeness_data: Dict) -> str:
        """Create summary of measure adequacy"""
        adequacy_assessment = completeness_data.get('adequacy_assessment', {})
        
        if not adequacy_assessment:
            return "Non valutato"
        
        adequate_count = sum(1 for adequacy in adequacy_assessment.values() if adequacy == 'adeguato')
        total_count = len(adequacy_assessment)
        
        if adequate_count == total_count:
            return "Tutte le misure sono adeguate"
        elif adequate_count == 0:
            return "Misure inadeguate per tutti i rischi"
        else:
            return f"{adequate_count}/{total_count} misure adeguate"
    
    def _create_citations(self, context_documents: List[Dict[str, Any]], permit_metadata: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Create citations from context documents and metadata
        """
        citations = {
            "normative": [],
            "internal": [],
            "metadata": []
        }
        
        print(f"[AdvancedOrchestrator] Creating citations from {len(context_documents)} documents")
        
        # Citations from context documents (PostgreSQL or Weaviate)
        for doc in context_documents[:5]:  # Limit to top 5
            # Enhanced citation info for PostgreSQL documents
            doc_source = doc.get("source", "unknown")
            
            # Build requirements from document content
            requirements = []
            if doc.get("keywords"):
                keywords = doc.get("keywords", [])
                if "LOTO" in keywords or "lockout" in keywords:
                    requirements.append({
                        "requirement": "Procedura isolamento energie (LOTO)",
                        "section": "Sicurezza operativa"
                    })
                if "DPI" in keywords or any("protection" in k.lower() for k in keywords):
                    requirements.append({
                        "requirement": "Dispositivi di Protezione Individuale",
                        "section": "Protezione personale"
                    })
                if "taglierina" in keywords or "mechanical" in keywords:
                    requirements.append({
                        "requirement": "Sicurezza macchinari e attrezzature",
                        "section": "Rischi meccanici"
                    })
            
            # Default requirement if no specific ones
            if not requirements:
                requirements.append({
                    "requirement": "Conformità normativa generale",
                    "section": doc.get("document_type", "Generale")
                })
            
            citation = {
                "document_info": {
                    "title": doc.get("title", "Documento sconosciuto"),
                    "code": doc.get("document_code", "N/A"),
                    "type": doc.get("document_type", "unknown"),
                    "source": doc_source
                },
                "relevance": {
                    "score": doc.get("search_score", 0.8),
                    "reason": f"Trovato tramite {doc_source} - Keywords: {', '.join(doc.get('keywords', [])[:3])}"
                },
                "key_requirements": requirements,
                "content_summary": doc.get("content_summary", "")[:150],  # First 150 chars
                "frontend_display": {
                    "icon": "📋" if doc_source == "PostgreSQL" else "📄",
                    "color": "green" if doc_source == "PostgreSQL" else "blue"
                }
            }
            
            doc_type = doc.get("document_type", "")
            if "normativ" in doc_type.lower():
                citations["normative"].append(citation)
            else:
                citations["internal"].append(citation)
        
        # Citations from PostgreSQL metadata
        if permit_metadata.get("previous_permits"):
            for prev_permit in permit_metadata["previous_permits"][:3]:
                citation = {
                    "document_info": {
                        "title": f"Permesso precedente: {prev_permit.get('title', 'N/A')}",
                        "code": f"PERMIT-{prev_permit.get('id', 'N/A')}",
                        "type": "historical_permit"
                    },
                    "relevance": {
                        "score": 0.8,
                        "reason": "Permesso simile con storico aziendale"
                    },
                    "key_requirements": [
                        {
                            "requirement": "Esperienza precedente",
                            "section": "Storico aziendale"
                        }
                    ],
                    "frontend_display": {
                        "icon": "📋",
                        "color": "green"
                    }
                }
                citations["metadata"].append(citation)
        
        return citations
    
    def _create_completion_roadmap(self, action_items: List[Dict[str, Any]], permits_required: List[str]) -> Dict[str, List[str]]:
        """
        Create completion roadmap based on action items and required permits
        """
        roadmap = {
            "fase_preparatoria": [],
            "fase_esecutiva": [],
            "fase_conclusiva": []
        }
        
        # Preparatory phase
        roadmap["fase_preparatoria"].extend([
            "Ottenimento permessi richiesti",
            "Verifiche preliminari sicurezza",
            "Briefing team operativo"
        ])
        
        if permits_required:
            for permit in permits_required[:3]:
                roadmap["fase_preparatoria"].append(f"Acquisizione {permit}")
        
        # Executive phase
        critical_actions = [item for item in action_items if item.get("priority") == "alta"]
        if critical_actions:
            roadmap["fase_esecutiva"].append("Implementazione azioni critiche")
        
        roadmap["fase_esecutiva"].extend([
            "Monitoraggio continuo conformità",
            "Supervisione operazioni",
            "Controllo DPI e procedure"
        ])
        
        # Conclusive phase
        roadmap["fase_conclusiva"].extend([
            "Verifica completamento azioni",
            "Ripristino condizioni iniziali",
            "Documentazione lessons learned",
            "Aggiornamento database aziendale"
        ])
        
        return roadmap
    
    def _create_error_result(self, error_msg: str, start_time: float) -> Dict[str, Any]:
        """
        Create error result in expected format
        """
        
        return {
            "analysis_id": f"error_{int(time.time())}",
            "permit_id": 0,  # Add required field
            "analysis_complete": False,
            "error": error_msg,
            "confidence_score": 0.0,
            "processing_time": round(time.time() - start_time, 2),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": [],
            "ai_version": "Advanced-AI-2.0-Err",
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
                "normative": [],
                "internal": [],
                "metadata": []
            },
            "completion_roadmap": {
                "fase_preparatoria": ["Risolvere errore di sistema"],
                "fase_esecutiva": ["Ripetere analisi"],
                "fase_conclusiva": ["Verificare risultati"]
            },
            "performance_metrics": {  # Add required field
                "total_processing_time": round(time.time() - start_time, 2),
                "specialists_activated": 0,
                "parallel_execution": False,
                "risks_identified": 0,
                "documents_analyzed": 0,
                "metadata_enhanced": False,
                "cross_validation_performed": False
            }
        }
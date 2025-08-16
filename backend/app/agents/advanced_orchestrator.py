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
            
            # Phase 4: Consolidate Results
            print("[AdvancedOrchestrator] Phase 4: Consolidating Results")
            final_result = self._consolidate_advanced_results(
                permit_data,
                permit_metadata,
                classification_result,
                enhanced_results,
                context_documents,
                time.time() - start_time
            )
            
            print(f"[AdvancedOrchestrator] Analysis completed in {time.time() - start_time:.2f}s")
            return final_result
            
        except Exception as e:
            print(f"[AdvancedOrchestrator] Error during analysis: {e}")
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
        Classify risks using PostgreSQL metadata
        """
        
        # Build enhanced context with metadata
        enhanced_context = {
            "documents": context_documents,
            "user_context": self.user_context,
            "permit_metadata": permit_metadata,
            "historical_risks": permit_metadata.get("historical_risks", []),
            "previous_incidents": permit_metadata.get("previous_incidents", []),
            "site_specific_risks": permit_metadata.get("site_specific_risks", []),
            "equipment_risks": permit_metadata.get("equipment_risks", [])
        }
        
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
        
        # Run risk classifier with enhanced context
        classification = await self.risk_classifier.analyze(permit_data, enhanced_context)
        
        # Add metadata-identified risks
        if metadata_risks:
            print(f"  [Classifier] Added {len(set(metadata_risks))} risks from PostgreSQL metadata")
            existing_specialists = classification.get("specialists_to_activate", [])
            all_specialists = list(set(existing_specialists + metadata_risks))
            classification["specialists_to_activate"] = all_specialists
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
            "hot_work": ["saldatura", "taglio", "fiamma", "welding", "cutting"],
            "confined_space": ["spazio confinato", "serbatoio", "tank", "vessel"],
            "height": ["altezza", "caduta", "ponteggio", "scaffold"],
            "electrical": ["elettrico", "tensione", "quadro", "voltage"],
            "chemical": ["chimico", "tossico", "atex", "chemical"]
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
                        if any(keyword in doc_title for keyword in keywords):
                            relevant_docs.append(doc)
                
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
        
        # Add risks from metadata
        if permit_metadata.get("identified_risks"):
            for risk in permit_metadata["identified_risks"]:
                all_risks.append({
                    "type": risk.get("type"),
                    "source": "PostgreSQL Metadata",
                    "severity": risk.get("severity", "media")
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
        
        # Add site-specific requirements from metadata
        if permit_metadata.get("site_requirements"):
            all_controls.extend(permit_metadata["site_requirements"])
        
        # Build executive summary
        critical_issues = len([r for r in all_risks if 
                              isinstance(r, dict) and 
                              r.get("severity") in ["critica", "alta"]])
        
        # Convert to action items
        action_items = self._create_advanced_action_items(
            all_controls, all_dpi, all_permits, permit_metadata
        )
        
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
                "overall_score": 0.2 if critical_issues > 2 else (0.5 if critical_issues > 0 else 0.8),
                "critical_issues": critical_issues,
                "recommendations": len(action_items),
                "compliance_level": classification.get("overall_risk_level", "da_verificare"),
                "estimated_completion_time": f"{len(action_items)*2}-{len(action_items)*4} ore",
                "key_findings": self._extract_key_findings(all_risks, permit_metadata),
                "next_steps": self._generate_next_steps(all_permits, critical_issues)
            },
            
            "action_items": action_items,
            "agents_involved": ["Risk_Classifier"] + list(specialist_results.keys()),
            
            # Enhanced metadata
            "metadata_insights": {
                "historical_incidents": len(permit_metadata.get("incidents", [])),
                "similar_permits": len(permit_metadata.get("previous_permits", [])),
                "site_specific_risks": len(permit_metadata.get("site_specific_risks", [])),
                "equipment_hazards": len(permit_metadata.get("equipment_risks", []))
            },
            
            # Performance metrics
            "performance_metrics": {
                "total_processing_time": round(processing_time, 2),
                "specialists_activated": len(specialist_results),
                "parallel_execution": True,
                "risks_identified": len(all_risks),
                "documents_analyzed": len(context_documents),
                "metadata_enhanced": True
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
        
        # Priority 4: DPI
        for dpi_item in dpi[:10]:
            action_items.append({
                "id": f"ACT_{item_id:03d}",
                "type": "dpi_requirement",
                "priority": "alta",
                "title": f"Fornire {dpi_item[:30]}",
                "description": dpi_item,
                "suggested_action": f"Verificare disponibilità e distribuzione {dpi_item}",
                "consequences_if_ignored": "Esposizione diretta ai rischi",
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
    
    def _create_error_result(self, error_msg: str, start_time: float) -> Dict[str, Any]:
        """
        Create error result in expected format
        """
        
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
            "action_items": []
        }
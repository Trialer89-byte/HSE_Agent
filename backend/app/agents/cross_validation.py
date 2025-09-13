"""
Cross-Validation Agent - Validates and integrates results from multiple specialists
"""
from typing import Dict, Any, List
import asyncio


class CrossValidationAgent:
    """Agent for cross-validating and integrating specialist results"""
    
    def __init__(self):
        self.name = "Cross_Validation_Agent"
        self.specialization = "Validazione Incrociata e Integrazione Risultati"
    
    async def validate_and_integrate(
        self, 
        permit_data: Dict[str, Any],
        specialist_results: Dict[str, Any],
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform cross-validation of specialist results and identify gaps/conflicts
        """
        
        validation_results = {
            "validation_complete": True,
            "cross_checks_performed": [],
            "conflicts_identified": [],
            "gaps_identified": [],
            "integration_recommendations": [],
            "enhanced_action_items": [],
            "risk_interactions": []
        }
        
        # Collect all specialist data
        all_risks = self._collect_all_risks(specialist_results)
        all_controls = self._collect_all_controls(specialist_results)
        all_dpi = self._collect_all_dpi(specialist_results)
        
        # Cross-validation checks
        validation_results["cross_checks_performed"] = [
            "Hot Work + Chemical interaction analysis",
            "Mechanical + Chemical compatibility check", 
            "DPI compatibility across specialists",
            "Control measure effectiveness validation",
            "Risk escalation identification"
        ]
        
        # Check for specific dangerous combinations
        conflicts = self._identify_conflicts(specialist_results, permit_data)
        validation_results["conflicts_identified"] = conflicts
        
        # Check for missing risks based on specialist combinations
        gaps = self._identify_gaps(specialist_results, permit_data, all_risks)
        validation_results["gaps_identified"] = gaps
        
        # Risk interaction analysis
        interactions = self._analyze_risk_interactions(specialist_results, permit_data)
        validation_results["risk_interactions"] = interactions
        
        # Generate integration recommendations
        integration_recs = self._generate_integration_recommendations(
            specialist_results, conflicts, gaps, interactions
        )
        validation_results["integration_recommendations"] = integration_recs
        
        # Enhanced action items based on cross-validation
        enhanced_actions = self._create_enhanced_action_items(
            specialist_results, conflicts, gaps, interactions
        )
        validation_results["enhanced_action_items"] = enhanced_actions
        
        # CONSOLIDAMENTO FINALE - Verifica coerenza suggerimenti
        consolidation = self._perform_final_consolidation(
            permit_data, specialist_results, conflicts, gaps, interactions
        )
        validation_results["final_consolidation"] = consolidation
        
        return validation_results
    
    def _collect_all_risks(self, specialist_results: Dict[str, Any]) -> List[str]:
        """Collect all risks identified by specialists"""
        all_risks = []
        for specialist, result in specialist_results.items():
            if isinstance(result, dict) and "error" not in result:
                risks = result.get("risks_identified", [])
                all_risks.extend(risks)
        return all_risks
    
    def _collect_all_controls(self, specialist_results: Dict[str, Any]) -> List[str]:
        """Collect all mitigation actions from specialists"""
        all_controls = []
        for specialist, result in specialist_results.items():
            if isinstance(result, dict) and "error" not in result:
                controls = result.get("mitigation_actions", [])
                all_controls.extend(controls)
        return all_controls
    
    def _collect_all_dpi(self, specialist_results: Dict[str, Any]) -> List:
        """Collect all DPI requirements from specialists"""
        all_dpi = []
        for specialist, result in specialist_results.items():
            if isinstance(result, dict) and "error" not in result:
                dpi = result.get("dpi_requirements", [])
                all_dpi.extend(dpi)
        return all_dpi
    
    def _identify_conflicts(self, specialist_results: Dict[str, Any], permit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify conflicts between specialist recommendations"""
        conflicts = []
        
        # Critical conflict: Hot Work + Chemical in enclosed space
        has_hot_work = "HotWork_Specialist" in specialist_results
        has_chemical = "Chemical_Specialist" in specialist_results
        has_confined = "ConfinedSpace_Specialist" in specialist_results
        
        if has_hot_work and has_chemical:
            conflicts.append({
                "type": "critical_interaction",
                "description": "Hot Work + Chemical risks - High explosion potential",
                "severity": "CRITICA",
                "specialists_involved": ["HotWork_Specialist", "Chemical_Specialist"],
                "required_action": "Enhanced explosion prevention measures required",
                "additional_controls": [
                    "Continuous atmospheric monitoring",
                    "Enhanced ventilation systems",
                    "ATEX-certified equipment only",
                    "Specialized fire suppression systems"
                ]
            })
        
        if has_hot_work and has_confined:
            conflicts.append({
                "type": "critical_interaction", 
                "description": "Hot Work in Confined Space - Extreme hazard",
                "severity": "CRITICA",
                "specialists_involved": ["HotWork_Specialist", "ConfinedSpace_Specialist"],
                "required_action": "Special permit and emergency response required",
                "additional_controls": [
                    "Continuous attendant outside space",
                    "Emergency rescue team on standby",
                    "Direct communication with worker",
                    "Pre-arranged emergency evacuation"
                ]
            })
        
        # Check for DPI conflicts
        if has_chemical and "Mechanical_Specialist" in specialist_results:
            conflicts.append({
                "type": "dpi_compatibility",
                "description": "Chemical + Mechanical DPI compatibility check needed",
                "severity": "ALTA",
                "specialists_involved": ["Chemical_Specialist", "Mechanical_Specialist"],
                "required_action": "Verify DPI compatibility for dual protection",
                "additional_controls": [
                    "Multi-hazard certified DPI selection",
                    "Comfort and mobility assessment",
                    "Emergency doffing procedures"
                ]
            })
        
        return conflicts
    
    def _identify_gaps(self, specialist_results: Dict[str, Any], permit_data: Dict[str, Any], all_risks: List[str]) -> List[Dict[str, Any]]:
        """Identify missing risk assessments"""
        gaps = []
        
        work_description = f"{permit_data.get('title', '')} {permit_data.get('description', '')}".lower()
        
        # Check for missing specialists based on work description
        if "tubo" in work_description or "pipe" in work_description:
            if "Mechanical_Specialist" not in specialist_results:
                gaps.append({
                    "type": "missing_specialist",
                    "description": "Lavoro su tubazioni richiede valutazione rischi meccanici",
                    "missing_specialist": "Mechanical_Specialist", 
                    "rationale": "Pressurized systems require mechanical hazard assessment",
                    "impact": "Critical mechanical risks may be unassessed"
                })
        
        if ("olio" in work_description or "oil" in work_description) and "taglio" in work_description:
            if "Chemical_Specialist" not in specialist_results:
                gaps.append({
                    "type": "missing_specialist",
                    "description": "Taglio tubi con fluidi richiede valutazione chimica",
                    "missing_specialist": "Chemical_Specialist",
                    "rationale": "Cutting fluid-containing pipes creates vapor/explosion risks",
                    "impact": "Chemical exposure and explosion risks unassessed"
                })
        
        # Check for missing environmental assessments
        if len(specialist_results) > 2:  # Complex multi-risk scenario
            environmental_mentioned = any("environment" in str(result).lower() for result in specialist_results.values())
            if not environmental_mentioned:
                gaps.append({
                    "type": "missing_assessment",
                    "description": "Valutazione impatto ambientale mancante per scenario complesso",
                    "missing_assessment": "Environmental Impact",
                    "rationale": "Multi-risk scenarios often have environmental implications",
                    "impact": "Potential environmental contamination unassessed"
                })
        
        return gaps
    
    def _analyze_risk_interactions(self, specialist_results: Dict[str, Any], permit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze how risks from different specialists interact"""
        interactions = []
        
        specialists_active = list(specialist_results.keys())
        
        # Hot Work + Chemical = Explosion risk escalation
        if "HotWork_Specialist" in specialists_active and "Chemical_Specialist" in specialists_active:
            interactions.append({
                "interaction_type": "risk_escalation",
                "specialists": ["HotWork_Specialist", "Chemical_Specialist"],
                "description": "Hot work ignition sources + flammable vapors = Explosion risk",
                "escalated_risk": "Explosion/Fire",
                "mitigation_factor": "3x (risk tripled)",
                "combined_controls": [
                    "Inert atmosphere creation",
                    "Continuous gas monitoring",
                    "Enhanced fire suppression",
                    "Increased emergency response readiness"
                ]
            })
        
        # Mechanical + Chemical = Contamination spread risk
        if "Mechanical_Specialist" in specialists_active and "Chemical_Specialist" in specialists_active:
            interactions.append({
                "interaction_type": "contamination_spread",
                "specialists": ["Mechanical_Specialist", "Chemical_Specialist"],
                "description": "Mechanical cutting + pressurized chemical system = Wide contamination",
                "escalated_risk": "Chemical Contamination Spread",
                "mitigation_factor": "2x (area doubled)",
                "combined_controls": [
                    "Containment barriers extension",
                    "Enhanced decontamination procedures",
                    "Personal protective equipment upgrade",
                    "Environmental monitoring expansion"
                ]
            })
        
        # Multiple specialists = Complexity risk
        if len(specialists_active) >= 3:
            interactions.append({
                "interaction_type": "complexity_risk",
                "specialists": specialists_active,
                "description": "Multiple simultaneous risks increase coordination complexity",
                "escalated_risk": "Coordination/Communication Failure",
                "mitigation_factor": f"{len(specialists_active)}x coordination complexity",
                "combined_controls": [
                    "Enhanced communication protocols",
                    "Dedicated safety coordinator assignment",
                    "Detailed sequence planning",
                    "Multiple safety checkpoints"
                ]
            })
        
        return interactions
    
    def _generate_integration_recommendations(
        self, 
        specialist_results: Dict[str, Any], 
        conflicts: List[Dict], 
        gaps: List[Dict],
        interactions: List[Dict]
    ) -> List[str]:
        """Generate recommendations for integrating all specialist findings"""
        recommendations = []
        
        # Handle conflicts
        if conflicts:
            recommendations.append("PRIORITÀ MASSIMA: Risolvere conflitti critici tra specialist prima di procedere")
            
            for conflict in conflicts:
                if conflict.get("severity") == "CRITICA":
                    recommendations.append(f"Implementare controlli aggiuntivi per: {conflict['description']}")
        
        # Handle gaps
        if gaps:
            recommendations.append("Attivare specialist mancanti per valutazione completa")
            
            for gap in gaps:
                if gap.get("type") == "missing_specialist":
                    recommendations.append(f"Richiedere analisi {gap['missing_specialist']}")
        
        # Handle interactions
        if interactions:
            recommendations.append("Implementare controlli specifici per interazioni tra rischi")
            
            escalation_risks = [i for i in interactions if i.get("interaction_type") == "risk_escalation"]
            if escalation_risks:
                recommendations.append("Applicare fattori di sicurezza maggiorati per rischi escalati")
        
        # General integration recommendations
        if len(specialist_results) >= 2:
            recommendations.extend([
                "Nominare coordinatore sicurezza dedicato per scenario multi-rischio",
                "Implementare sistema comunicazione bidirezionale continua",
                "Predisporre piani di emergenza specifici per ogni combinazione di rischi",
                "Verificare compatibilità di tutti i DPI richiesti dai diversi specialist"
            ])
        
        return recommendations
    
    def _create_enhanced_action_items(
        self,
        specialist_results: Dict[str, Any],
        conflicts: List[Dict],
        gaps: List[Dict], 
        interactions: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Create enhanced action items based on cross-validation"""
        enhanced_actions = []
        item_id = 1
        
        # Critical conflict actions
        for conflict in conflicts:
            if conflict.get("severity") == "CRITICA":
                enhanced_actions.append({
                    "id": f"XV_{item_id:03d}",
                    "type": "critical_integration",
                    "priority": "critica",
                    "suggested_action": f"CRITICO: {conflict['description']} - {conflict['required_action']}",
                    "specialists_involved": conflict["specialists_involved"],
                    "additional_controls": conflict.get("additional_controls", []),
                    "frontend_display": {
                        "color": "red",
                        "icon": "alert-triangle",
                        "category": "Integrazione Critica"
                    }
                })
                item_id += 1
        
        # Gap filling actions
        for gap in gaps:
            if gap.get("type") == "missing_specialist":
                enhanced_actions.append({
                    "id": f"XV_{item_id:03d}",
                    "type": "specialist_activation",
                    "priority": "alta",
                    "title": f"Attivare {gap['missing_specialist']}",
                    "description": gap["description"],
                    "suggested_action": f"Richiedere analisi completa da {gap['missing_specialist']}",
                    "rationale": gap["rationale"],
                    "impact_if_ignored": gap["impact"],
                    "frontend_display": {
                        "color": "orange", 
                        "icon": "user-plus",
                        "category": "Specialist Mancanti"
                    }
                })
                item_id += 1
        
        # Risk interaction actions
        for interaction in interactions:
            if interaction.get("interaction_type") == "risk_escalation":
                enhanced_actions.append({
                    "id": f"XV_{item_id:03d}",
                    "type": "risk_interaction",
                    "priority": "alta",
                    "suggested_action": f"Gestire interazione: {interaction['description']} - Implementare controlli combinati per {interaction['escalated_risk']}",
                    "mitigation_factor": interaction["mitigation_factor"],
                    "combined_controls": interaction["combined_controls"],
                    "frontend_display": {
                        "color": "purple",
                        "icon": "layers",
                        "category": "Interazione Rischi"
                    }
                })
                item_id += 1
        
        return enhanced_actions
    
    def _perform_final_consolidation(
        self, 
        permit_data: Dict[str, Any], 
        specialist_results: Dict[str, Any], 
        conflicts: List[Dict], 
        gaps: List[Dict], 
        interactions: List[Dict]
    ) -> Dict[str, Any]:
        """Perform final consolidation to ensure coherence of all suggestions"""
        
        work_type = permit_data.get('work_type', '').lower()
        work_description = f"{permit_data.get('title', '')} {permit_data.get('description', '')}".lower()
        
        consolidation = {
            "coherence_analysis": [],
            "consistency_check": {},
            "work_type_alignment": {},
            "final_recommendations": [],
            "potential_contradictions": [],
            "prioritized_actions": []
        }
        
        # 1. COHERENCE ANALYSIS - Check if suggestions make sense together
        coherence_issues = []
        all_dpi = self._collect_all_dpi(specialist_results)
        all_controls = self._collect_all_controls(specialist_results)
        
        # Check DPI coherence
        dpi_text = " ".join([str(dpi) for dpi in all_dpi]).lower()
        
        # Identify potential DPI conflicts
        if "chemical" in dpi_text and "ignifug" in dpi_text:
            if not any("multi-hazard" in str(dpi).lower() for dpi in all_dpi):
                coherence_issues.append({
                    "type": "dpi_compatibility",
                    "issue": "Chemical + Fire resistant DPI required - check compatibility",
                    "solution": "Specify multi-hazard certified DPI"
                })
        
        # Check control measure coherence
        if "ventilation" in " ".join(all_controls).lower() and "confined" in work_description:
            if not any("atmospheric monitoring" in control.lower() for control in all_controls):
                coherence_issues.append({
                    "type": "control_completeness", 
                    "issue": "Ventilation specified but atmospheric monitoring missing",
                    "solution": "Add continuous atmospheric monitoring"
                })
        
        consolidation["coherence_analysis"] = coherence_issues
        
        # 2. CONSISTENCY CHECK - Verify suggestions align with work type
        consistency = {}
        
        # Mechanical work consistency
        if "mechanical" in work_type or any(term in work_description for term in ["rotore", "motore", "pompa", "taglierina"]):
            mechanical_specialists = [s for s in specialist_results.keys() if "mechanical" in s.lower()]
            if not mechanical_specialists:
                consistency["mechanical_missing"] = "Lavoro meccanico richiede Mechanical Specialist"
            else:
                # Check if LOTO is mentioned
                loto_mentioned = any("loto" in str(result).lower() or "lockout" in str(result).lower() 
                                   for result in specialist_results.values())
                if not loto_mentioned:
                    consistency["loto_missing"] = "Lavoro meccanico richiede procedura LOTO"
        
        # Pressure system consistency
        if any(term in work_description for term in ["tubo", "pipe", "pressione"]):
            pressure_controls = [c for c in all_controls if any(p in c.lower() for p in ["pressur", "spurgo", "depressur"])]
            if not pressure_controls:
                consistency["pressure_controls_missing"] = "Sistema in pressione richiede controlli specifici"
        
        consolidation["consistency_check"] = consistency
        
        # 3. WORK TYPE ALIGNMENT - Check all suggestions align with actual work
        alignment = {
            "work_type": work_type,
            "identified_work_aspects": [],
            "aligned_specialists": [],
            "misaligned_suggestions": []
        }
        
        # Identify work aspects from description
        work_aspects = []
        if any(term in work_description for term in ["rotore", "rotor", "rotating"]):
            work_aspects.append("rotating_equipment")
        if any(term in work_description for term in ["rimozione", "sostituzione", "removal"]):
            work_aspects.append("component_replacement")
        if any(term in work_description for term in ["taglierina", "cutter", "cutting"]):
            work_aspects.append("cutting_operation")
        
        alignment["identified_work_aspects"] = work_aspects
        
        # Check if specialists align with work aspects
        for specialist, result in specialist_results.items():
            if "mechanical" in specialist.lower() and "rotating_equipment" in work_aspects:
                alignment["aligned_specialists"].append(f"{specialist} - Correctly activated for rotating equipment")
            elif "hot_work" in specialist.lower() and not any(hot in work_description for hot in ["saldatura", "taglio", "welding", "cutting"]):
                alignment["misaligned_suggestions"].append(f"{specialist} - May not be needed for this work type")
        
        consolidation["work_type_alignment"] = alignment
        
        # 4. FINAL RECOMMENDATIONS - Consolidated coherent recommendations
        final_recs = []
        
        # Priority 1: Critical safety measures
        if conflicts:
            final_recs.append("PRIORITÀ CRITICA: Implementare controlli per conflitti identificati prima di procedere")
        
        # Priority 2: Work-type specific essentials
        if "rotating_equipment" in work_aspects:
            final_recs.append("ESSENZIALE: Implementare procedura LOTO per isolamento energia cinetica")
            final_recs.append("ESSENZIALE: Verificare arresto completo prima dell'intervento")
        
        if "component_replacement" in work_aspects:
            final_recs.append("RACCOMANDATO: Utilizzare attrezzature sollevamento certificate per componenti pesanti")
        
        # Priority 3: Risk-specific measures
        high_risk_controls = [c for c in all_controls if any(term in c.lower() for term in ["critical", "emergency", "mandatory"])]
        if high_risk_controls:
            final_recs.append("IMPLEMENTARE: Tutti i controlli critici identificati dagli specialist")
        
        consolidation["final_recommendations"] = final_recs
        
        # 5. IDENTIFY CONTRADICTIONS
        contradictions = []
        
        # Check for contradictory DPI requirements
        if any("no gloves" in str(dpi).lower() for dpi in all_dpi) and any("gloves" in str(dpi).lower() for dpi in all_dpi):
            contradictions.append({
                "type": "dpi_contradiction",
                "description": "Contrasting glove requirements identified",
                "resolution": "Review specific hazards and select appropriate glove type"
            })
        
        # Check for contradictory procedures
        ventilation_required = any("ventilation" in control.lower() for control in all_controls)
        sealed_space_required = any("seal" in control.lower() or "close" in control.lower() for control in all_controls)
        if ventilation_required and sealed_space_required:
            contradictions.append({
                "type": "procedure_contradiction",
                "description": "Ventilation required but space sealing also suggested",
                "resolution": "Clarify sequence: ventilation during work, sealing afterward"
            })
        
        consolidation["potential_contradictions"] = contradictions
        
        # 6. PRIORITIZED FINAL ACTIONS
        prioritized_actions = []
        
        # Critical first
        for conflict in conflicts:
            if conflict.get("severity") == "CRITICA":
                prioritized_actions.append({
                    "priority": 1,
                    "action": conflict["required_action"],
                    "rationale": f"Critical safety conflict: {conflict['description']}"
                })
        
        # Essential work-type specific
        if consistency:
            for key, issue in consistency.items():
                prioritized_actions.append({
                    "priority": 2,
                    "action": f"Address: {issue}",
                    "rationale": "Essential for work type safety"
                })
        
        # Coherence fixes
        for issue in coherence_issues:
            prioritized_actions.append({
                "priority": 3,
                "action": issue["solution"],
                "rationale": f"Coherence issue: {issue['issue']}"
            })
        
        consolidation["prioritized_actions"] = sorted(prioritized_actions, key=lambda x: x["priority"])
        
        return consolidation
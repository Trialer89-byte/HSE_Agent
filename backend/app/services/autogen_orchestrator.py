from typing import Dict, Any, List
import asyncio
import time
import json
from datetime import datetime

from app.agents.simple_autogen_agents import SimpleAutoGenHSEAgents
from app.agents.enhanced_autogen_agents import EnhancedAutoGenHSEAgents
from app.agents.modular_orchestrator import ModularHSEOrchestrator


class AutoGenAIOrchestrator:
    """
    AutoGen-based AI Orchestrator for HSE permit analysis
    """
    
    def __init__(self, use_modular: bool = True, use_enhanced_agents: bool = False):
        self.analysis_timeout = 60  # Reduced to 1 minute for faster response
        self.use_modular = use_modular
        self.use_enhanced_agents = use_enhanced_agents
    
    async def run_multi_agent_analysis(
        self,
        permit_data: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        vector_service=None
    ) -> Dict[str, Any]:
        """
        Run comprehensive HSE analysis using AutoGen agents
        """
        start_time = time.time()
        print(f"[AutoGenOrchestrator] Starting AutoGen multi-agent analysis for permit {permit_data.get('id')}")
        
        try:
            # Initialize AutoGen HSE agents with vector service for dynamic searches
            if self.use_modular:
                hse_agents = ModularHSEOrchestrator(user_context, vector_service)
                print(f"[AutoGenOrchestrator] Using MODULAR system with dynamic specialist loading")
                # For modular system, directly return its analysis
                return await hse_agents.analyze_permit(permit_data, context_documents)
            elif self.use_enhanced_agents:
                hse_agents = EnhancedAutoGenHSEAgents(user_context, vector_service)
                print(f"[AutoGenOrchestrator] Using ENHANCED agents with {len(hse_agents.agents)} specialists")
            else:
                hse_agents = SimpleAutoGenHSEAgents(user_context, vector_service)
                print(f"[AutoGenOrchestrator] Using SIMPLE agents with {len(hse_agents.agents)} AutoGen agents")
            if vector_service:
                print(f"[AutoGenOrchestrator] Vector service enabled for dynamic document searches")
            
            # Run analysis with timeout protection
            analysis_task = hse_agents.analyze_permit(permit_data, context_documents)
            
            try:
                analysis_result = await asyncio.wait_for(analysis_task, timeout=self.analysis_timeout)
            except asyncio.TimeoutError:
                print(f"[AutoGenOrchestrator] Analysis timed out after {self.analysis_timeout}s")
                return self._create_timeout_result(permit_data, start_time)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            analysis_result["processing_time"] = round(processing_time, 2)
            
            # Parse and structure the final output
            structured_output = self._structure_autogen_output(analysis_result, permit_data)
            
            print(f"[AutoGenOrchestrator] Analysis completed in {processing_time:.2f}s")
            
            return structured_output
            
        except Exception as e:
            print(f"[AutoGenOrchestrator] Error: {str(e)}")
            return self._create_error_result(permit_data, start_time, str(e))
    
    def _structure_autogen_output(self, analysis_result: Dict[str, Any], permit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Structure AutoGen conversation output into expected format
        """
        
        # Check if we have the structured analysis from the agents
        final_analysis = analysis_result.get("final_analysis", {})
        
        # If final_analysis is already a dict with the expected structure, use it directly
        if isinstance(final_analysis, dict) and final_analysis.get("executive_summary"):
            structured_data = final_analysis
            print(f"[AutoGenOrchestrator] Using AI-generated structured analysis")
        else:
            # Otherwise, try to extract from conversation history
            print(f"[AutoGenOrchestrator] WARNING: No structured analysis found, using fallback")
            structured_data = self._create_default_structure(analysis_result)
        
        # Build final result with metadata
        final_result = {
            # Metadata
            "analysis_id": f"autogen_{int(time.time())}_{permit_data.get('id')}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": analysis_result.get("analysis_complete", True),
            "confidence_score": analysis_result.get("confidence_score", 0.8),
            "processing_time": analysis_result.get("processing_time", 0.0),
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": analysis_result.get("agents_involved", []),
            "ai_version": "AutoGen-1.0",
            
            # Structured results from AutoGen conversation
            "executive_summary": structured_data.get("executive_summary", self._default_executive_summary()),
            "action_items": structured_data.get("action_items", []),
            "citations": structured_data.get("citations", {}),
            "completion_roadmap": structured_data.get("completion_roadmap", {}),
            
            # Performance metrics
            "performance_metrics": {
                "total_processing_time": analysis_result.get("processing_time", 0.0),
                "autogen_conversation_rounds": len(analysis_result.get("conversation_history", [])),
                "agents_successful": len(analysis_result.get("agents_involved", [])),
                "agents_total": 5,
                "analysis_method": "AutoGen GroupChat"
            },
            
            # Raw AutoGen data for debugging
            "autogen_conversation": analysis_result.get("conversation_history", [])
        }
        
        return final_result
    
    def _extract_json_from_conversation(self, conversation_text: str) -> Dict[str, Any]:
        """
        Try to extract structured JSON from AutoGen conversation
        """
        try:
            # Look for JSON blocks in the conversation
            import re
            
            # Find JSON blocks
            json_pattern = r'\{[\s\S]*\}'
            matches = re.findall(json_pattern, conversation_text)
            
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict) and any(key in parsed for key in ['executive_summary', 'action_items', 'citations']):
                        return parsed
                except:
                    continue
            
            return {}
            
        except Exception:
            return {}
    
    def _create_default_structure(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract actual analysis from AI conversation when structured output is not available
        """
        conversation = analysis_result.get("conversation_history", [])
        
        # Initialize containers for real analysis
        risks = []
        dpi_items = []
        recommendations = []
        action_items = []
        
        # Process each AI agent's response
        for idx, message in enumerate(conversation):
            if isinstance(message, dict):
                content = message.get("content", "")
                agent = message.get("agent", "")
            else:
                content = str(message)
                agent = f"Agent_{idx}"
            
            content_lower = content.lower()
            
            # Extract specific risks mentioned in the conversation
            risk_keywords = {
                "elettrico": "Rischio elettrico da quadro BT",
                "caduta": "Rischio caduta dall'alto",
                "meccanico": "Rischio meccanico da attrezzature",
                "chimico": "Rischio esposizione agenti chimici",
                "incendio": "Rischio incendio",
                "altezza": "Rischio lavoro in altezza",
                "spazi confinati": "Rischio spazi confinati",
                "esplosione": "Rischio esplosione ATEX"
            }
            
            for keyword, risk_desc in risk_keywords.items():
                if keyword in content_lower and risk_desc not in risks:
                    risks.append(risk_desc)
            
            # Extract DPI mentioned
            dpi_keywords = {
                "guanti": "Guanti di protezione EN 388",
                "elmetto": "Elmetto EN 397",
                "casco": "Casco di protezione EN 397",
                "occhiali": "Occhiali di sicurezza EN 166",
                "scarpe": "Scarpe antinfortunistiche EN ISO 20345",
                "imbracatura": "Imbracatura anticaduta EN 361",
                "respiratore": "Dispositivi protezione vie respiratorie"
            }
            
            for keyword, dpi_desc in dpi_keywords.items():
                if keyword in content_lower and dpi_desc not in dpi_items:
                    dpi_items.append(dpi_desc)
            
            # Extract recommendations
            if any(word in content_lower for word in ["raccomand", "suggeri", "necessario", "importante"]):
                # Try to extract specific recommendations
                lines = content.split('\n')
                for line in lines:
                    line_lower = line.lower()
                    if any(word in line_lower for word in ["raccomand", "necessario", "importante"]) and len(line) > 20:
                        rec = line.strip()[:150]  # Limit length
                        if rec and rec not in recommendations:
                            recommendations.append(rec)
        
        # Create action items based on identified risks
        for idx, risk in enumerate(risks[:5]):  # Limit to 5 main risks
            action_items.append({
                "id": f"ACT_{idx+1:03d}",
                "type": "risk_mitigation",
                "priority": "alta" if any(word in risk.lower() for word in ["elettrico", "caduta", "esplosione"]) else "media",
                "title": f"Mitigare {risk}",
                "description": f"Implementare misure di controllo per {risk}",
                "suggested_action": "Definire e implementare misure di controllo specifiche",
                "consequences_if_ignored": "Possibili incidenti o infortuni",
                "references": ["D.Lgs 81/08"],
                "estimated_effort": "2-4 ore",
                "responsible_role": "Responsabile Sicurezza",
                "frontend_display": {
                    "color": "red" if "elettrico" in risk.lower() else "orange",
                    "icon": "alert-triangle",
                    "category": "Controlli Sicurezza"
                }
            })
        
        # Add DPI action item if DPI are identified
        if dpi_items:
            action_items.append({
                "id": f"ACT_{len(action_items)+1:03d}",
                "type": "dpi_requirement",
                "priority": "alta",
                "title": "Fornire DPI necessari",
                "description": f"Fornire {len(dpi_items)} DPI identificati",
                "suggested_action": "Verificare disponibilità e distribuire DPI secondo standard specificati",
                "consequences_if_ignored": "Esposizione a rischi per i lavoratori",
                "references": [dpi.split("EN ")[1] if "EN " in dpi else "Standard applicabile" for dpi in dpi_items],
                "estimated_effort": "1-2 ore",
                "responsible_role": "Responsabile Magazzino",
                "dpi_details": dpi_items,  # Add detailed DPI list
                "frontend_display": {
                    "color": "orange",
                    "icon": "shield-check",
                    "category": "DPI Obbligatori"
                }
            })
        
        # Determine compliance level based on risks
        critical_risks = len([r for r in risks if any(word in r.lower() for word in ["elettrico", "caduta", "esplosione", "chimico"])])
        
        if critical_risks > 2:
            compliance_level = "non_conforme"
        elif critical_risks > 0:
            compliance_level = "requires_action" 
        else:
            compliance_level = "da_verificare"
        
        return {
            "executive_summary": {
                "overall_score": max(0.4, 1.0 - (critical_risks * 0.2)),
                "critical_issues": critical_risks,
                "recommendations": len(recommendations),
                "compliance_level": compliance_level,
                "estimated_completion_time": f"{2 + critical_risks}-{4 + critical_risks} ore",
                "key_findings": risks[:5] if risks else ["Analisi AI completata - verificare dettagli"],
                "next_steps": recommendations[:3] if recommendations else [
                    "Implementare misure di controllo identificate",
                    "Fornire DPI specificati", 
                    "Verificare formazione operatori"
                ]
            },
            "action_items": action_items,
            "dpi_requirements": self._format_dpi_requirements(dpi_items),
            "citations": self._create_citations_with_dpi_standards(dpi_items),
            "completion_roadmap": {
                "immediate": [
                    f"Fornire DPI: {', '.join(dpi_items[:3])}" if dpi_items else "Verificare DPI necessari",
                    "Briefing sicurezza pre-lavoro"
                ],
                "short_term": [
                    "Implementazione misure di controllo rischi",
                    "Formazione specifica operatori"
                ],
                "long_term": [
                    "Monitoraggio continuo conformità",
                    "Aggiornamento procedure operative"
                ]
            }
        }
    
    def _create_citations_with_dpi_standards(self, dpi_items: List[str]) -> Dict[str, List[Dict]]:
        """Create citations including DPI standards"""
        citations = {
            "normative_framework": [],
            "company_procedures": []
        }
        
        # Add DPI standards to citations
        seen_standards = set()
        for dpi in dpi_items:
            if "EN " in dpi:
                standard = dpi.split("EN ")[1].split()[0]
                standard_code = f"EN {standard}"
                if standard_code not in seen_standards:
                    seen_standards.add(standard_code)
                    dpi_type = dpi.split("EN ")[0].strip()
                    citations["normative_framework"].append({
                        "document_info": {
                            "title": standard_code,
                            "type": "Standard Tecnico",
                            "date": "Current"
                        },
                        "relevance": {
                            "score": 0.85,
                            "reason": f"Standard per {dpi_type}"
                        },
                        "key_requirements": [],
                        "frontend_display": {
                            "color": "green",
                            "icon": "shield-check",
                            "category": "Standard UNI EN"
                        }
                    })
        
        return citations
    
    def _format_dpi_requirements(self, dpi_items: List[str]) -> List[Dict[str, Any]]:
        """Format DPI requirements with detailed information"""
        dpi_requirements = []
        
        for idx, dpi in enumerate(dpi_items):
            if "EN " in dpi:
                dpi_type = dpi.split("EN ")[0].strip()
                standard = f"EN {dpi.split('EN ')[1].split()[0]}"
            else:
                dpi_type = dpi
                standard = "Standard applicabile"
            
            # Map DPI types to specific information
            dpi_info = {
                "Guanti": {"reason": "Protezione da rischi meccanici", "priority": "alta"},
                "Elmetto": {"reason": "Protezione del capo da caduta oggetti", "priority": "alta"},
                "Casco": {"reason": "Protezione del capo da caduta oggetti", "priority": "alta"},
                "Occhiali": {"reason": "Protezione degli occhi", "priority": "media"},
                "Scarpe": {"reason": "Protezione dei piedi", "priority": "alta"},
                "Imbracatura": {"reason": "Protezione anticaduta", "priority": "alta"},
                "Respiratore": {"reason": "Protezione vie respiratorie", "priority": "alta"}
            }
            
            # Find matching DPI info
            info = None
            for key, value in dpi_info.items():
                if key.lower() in dpi_type.lower():
                    info = value
                    break
            
            if not info:
                info = {"reason": "Protezione generale", "priority": "media"}
            
            dpi_requirements.append({
                "id": f"DPI_{idx+1:03d}",
                "dpi_type": dpi_type,
                "standard": standard,
                "reason": info["reason"],
                "priority": info["priority"],
                "status": "richiesto",
                "frontend_display": {
                    "color": "orange" if info["priority"] == "alta" else "yellow",
                    "icon": "shield-check",
                    "category": "DPI Obbligatori"
                }
            })
        
        return dpi_requirements
    
    def _default_executive_summary(self) -> Dict[str, Any]:
        """
        Default executive summary structure
        """
        return {
            "overall_score": 0.7,
            "critical_issues": 0,
            "recommendations": 1,
            "compliance_level": "da_verificare",
            "estimated_completion_time": "2-4 ore",
            "key_findings": ["Analisi AutoGen completata con successo"],
            "next_steps": ["Revisione dettagliata delle raccomandazioni"]
        }
    
    def _create_timeout_result(self, permit_data: Dict[str, Any], start_time: float) -> Dict[str, Any]:
        """
        Create result structure for timeout cases
        """
        processing_time = time.time() - start_time
        
        return {
            "analysis_id": f"autogen_timeout_{int(time.time())}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": False,
            "confidence_score": 0.0,
            "processing_time": round(processing_time, 2),
            "error": f"AutoGen analysis timed out after {self.analysis_timeout} seconds",
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": [],
            "ai_version": "AutoGen-1.0",
            
            # Required fields with defaults
            "executive_summary": {
                "overall_score": 0.0,
                "critical_issues": 1,
                "recommendations": 1,
                "compliance_level": "non_analizzato",
                "estimated_completion_time": "Unknown",
                "key_findings": ["Analisi interrotta per timeout"],
                "next_steps": ["Riprovare analisi con timeout maggiore"]
            },
            "action_items": [],
            "citations": {},
            "completion_roadmap": {},
            "performance_metrics": {
                "total_processing_time": processing_time,
                "autogen_conversation_rounds": 0,
                "agents_successful": 0,
                "agents_total": 5,
                "analysis_method": "AutoGen GroupChat (timeout)"
            }
        }
    
    def _create_error_result(self, permit_data: Dict[str, Any], start_time: float, error_message: str) -> Dict[str, Any]:
        """
        Create result structure for error cases
        """
        processing_time = time.time() - start_time
        
        return {
            "analysis_id": f"autogen_error_{int(time.time())}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": False,
            "confidence_score": 0.0,
            "processing_time": round(processing_time, 2),
            "error": f"AutoGen analysis failed: {error_message}",
            "timestamp": datetime.utcnow().isoformat(),
            "agents_involved": [],
            "ai_version": "AutoGen-1.0",
            
            # Required fields with defaults
            "executive_summary": {
                "overall_score": 0.0,
                "critical_issues": 1,
                "recommendations": 1,
                "compliance_level": "errore_analisi",
                "estimated_completion_time": "Unknown",
                "key_findings": ["Errore durante l'analisi"],
                "next_steps": ["Verificare configurazione e riprovare"]
            },
            "action_items": [],
            "citations": {},
            "completion_roadmap": {},
            "performance_metrics": {
                "total_processing_time": processing_time,
                "autogen_conversation_rounds": 0,
                "agents_successful": 0,
                "agents_total": 5,
                "analysis_method": "AutoGen GroupChat (error)"
            }
        }
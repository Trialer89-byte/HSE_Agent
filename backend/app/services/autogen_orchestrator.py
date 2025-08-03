from typing import Dict, Any, List
import asyncio
import time
import json
from datetime import datetime

from app.agents.simple_autogen_agents import SimpleAutoGenHSEAgents


class AutoGenAIOrchestrator:
    """
    AutoGen-based AI Orchestrator for HSE permit analysis
    """
    
    def __init__(self):
        self.analysis_timeout = 180  # 3 minutes for AutoGen conversations
    
    async def run_multi_agent_analysis(
        self,
        permit_data: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run comprehensive HSE analysis using AutoGen agents
        """
        start_time = time.time()
        print(f"[AutoGenOrchestrator] Starting AutoGen multi-agent analysis for permit {permit_data.get('id')}")
        
        try:
            # Initialize AutoGen HSE agents
            hse_agents = SimpleAutoGenHSEAgents(user_context)
            print(f"[AutoGenOrchestrator] Initialized {len(hse_agents.agents)} AutoGen agents")
            
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
        
        # Try to extract structured JSON from the final conversation
        final_analysis = analysis_result.get("final_analysis", "")
        structured_data = self._extract_json_from_conversation(final_analysis)
        
        # If no structured data found, create default structure
        if not structured_data:
            structured_data = self._create_default_structure(analysis_result)
        
        # Build final result with metadata
        final_result = {
            # Metadata
            "analysis_id": f"autogen_{int(time.time())}_{permit_data.get('id')}",
            "permit_id": permit_data.get("id"),
            "analysis_complete": analysis_result.get("analysis_complete", True),
            "confidence_score": analysis_result.get("confidence_score", 0.8),
            "processing_time": analysis_result.get("processing_time", 0.0),
            "timestamp": datetime.utcnow(),
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
        Create default structure when AutoGen doesn't provide structured output
        """
        conversation = analysis_result.get("conversation_history", [])
        
        # Extract insights from conversation
        risks = []
        recommendations = []
        
        for message in conversation:
            content = message.get("content", "").lower()
            if "rischio" in content or "pericolo" in content:
                risks.append("Rischio identificato nella conversazione")
            if "raccomand" in content or "suggeri" in content:
                recommendations.append("Raccomandazione dalla conversazione")
        
        return {
            "executive_summary": {
                "overall_score": 0.7,
                "critical_issues": len(risks),
                "recommendations": len(recommendations),
                "compliance_level": "da_verificare",
                "estimated_completion_time": "2-4 ore",
                "key_findings": risks[:3] if risks else ["Analisi AutoGen completata"],
                "next_steps": recommendations[:3] if recommendations else ["Revisione manuale necessaria"]
            },
            "action_items": [],
            "citations": {},
            "completion_roadmap": {
                "immediate": ["Revisione analisi AutoGen"],
                "short_term": ["Implementazione raccomandazioni"],
                "long_term": ["Monitoraggio conformità"]
            }
        }
    
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
            "timestamp": datetime.utcnow(),
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
            "timestamp": datetime.utcnow(),
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
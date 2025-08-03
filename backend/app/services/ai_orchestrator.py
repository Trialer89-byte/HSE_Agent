from typing import Dict, Any, List
import asyncio
import time
from datetime import datetime

from app.agents.content_analysis_agent import ContentAnalysisAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.compliance_checker_agent import ComplianceCheckerAgent
from app.agents.dpi_specialist_agent import DPISpecialistAgent
from app.agents.citation_agent import DocumentCitationAgent


class AIOrchestrator:
    """
    Orchestratore centrale per la coordinazione multi-agente
    """
    
    def __init__(self):
        self.agents = {}
        self.analysis_timeout = 120  # 2 minutes timeout (4 agents × 30s each)
        self.vector_service = None  # Will be injected for dynamic searches
    
    async def run_multi_agent_analysis(
        self,
        permit_data: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        vector_service = None
    ) -> Dict[str, Any]:
        """
        Orchestrazione completa multi-agente con output strutturato
        """
        start_time = time.time()
        print(f"[AIOrchestrator] Starting multi-agent analysis for permit {permit_data.get('id')}")
        
        try:
            # Store vector service for agent access
            self.vector_service = vector_service
            
            # Initialize agents with user context and vector service for dynamic searches
            agents = {
                "content_analyst": ContentAnalysisAgent(user_context, vector_service),
                "risk_analyst": RiskAnalysisAgent(user_context, vector_service),
                "compliance_checker": ComplianceCheckerAgent(user_context, vector_service),  
                "dpi_specialist": DPISpecialistAgent(user_context, vector_service),
                "citation_agent": DocumentCitationAgent(user_context, vector_service)
            }
            
            # Phase 1: Parallel analysis of independent agents
            parallel_tasks = []
            print(f"[AIOrchestrator] Starting parallel analysis with {len(agents)} agents")
            
            # Content analysis
            parallel_tasks.append(
                self._run_agent_with_timeout(
                    agents["content_analyst"].analyze(permit_data, context_documents),
                    "content_analysis"
                )
            )
            
            # Risk analysis
            parallel_tasks.append(
                self._run_agent_with_timeout(
                    agents["risk_analyst"].analyze(permit_data, context_documents),
                    "risk_analysis"
                )
            )
            
            # Compliance check
            parallel_tasks.append(
                self._run_agent_with_timeout(
                    agents["compliance_checker"].analyze(permit_data, context_documents),
                    "compliance_check"
                )
            )
            
            # Execute parallel tasks
            parallel_results = await asyncio.gather(*parallel_tasks, return_exceptions=True)
            
            # Process parallel results
            content_analysis = self._extract_result(parallel_results[0], "content_analysis")
            risk_analysis = self._extract_result(parallel_results[1], "risk_analysis")
            compliance_check = self._extract_result(parallel_results[2], "compliance_check")
            
            # Phase 2: DPI analysis (depends on risk analysis)
            identified_risks = risk_analysis.get("identified_risks", [])
            dpi_analysis = await self._run_agent_with_timeout(
                agents["dpi_specialist"].analyze(permit_data, identified_risks, context_documents),
                "dpi_analysis"
            )
            
            if isinstance(dpi_analysis, Exception):
                dpi_analysis = self._create_error_result("dpi_analysis", str(dpi_analysis))
            
            # Phase 3: Final synthesis and structured output
            combined_analysis = {
                "content_analysis": content_analysis,
                "risk_analysis": risk_analysis,
                "compliance_check": compliance_check,
                "dpi_analysis": dpi_analysis
            }
            
            structured_output = await self._run_agent_with_timeout(
                agents["citation_agent"].generate_structured_output(combined_analysis, context_documents),
                "structured_output"
            )
            
            if isinstance(structured_output, Exception):
                structured_output = self._create_error_result("structured_output", str(structured_output))
            
            # Calculate overall confidence and processing time
            processing_time = time.time() - start_time
            confidence_score = self._calculate_overall_confidence([
                content_analysis, risk_analysis, compliance_check, dpi_analysis, structured_output
            ])
            
            # Build final result
            final_result = {
                # Metadata
                "analysis_id": f"analysis_{int(time.time())}_{user_context.get('user_id', 'unknown')}",
                "permit_id": permit_data.get("id"),
                "analysis_complete": True,
                "confidence_score": confidence_score,
                "processing_time": round(processing_time, 2),
                "timestamp": datetime.utcnow(),
                "agents_involved": list(agents.keys()),
                "ai_version": "1.0",
                
                # Individual agent results
                "content_improvements": content_analysis,
                "risk_assessment": risk_analysis,
                "compliance_check": compliance_check,
                "dpi_recommendations": dpi_analysis,
                
                # Frontend-ready structured output
                "executive_summary": structured_output.get("executive_summary", {}),
                "action_items": structured_output.get("action_items", []),
                "citations": structured_output.get("citations", {}),
                "completion_roadmap": structured_output.get("completion_roadmap", {}),
                
                # System information
                "performance_metrics": {
                    "total_processing_time": processing_time,
                    "parallel_phase_time": sum(self._get_processing_time(r) for r in parallel_results if not isinstance(r, Exception)),
                    "agents_successful": sum(1 for r in [content_analysis, risk_analysis, compliance_check, dpi_analysis, structured_output] if r.get("analysis_complete", False)),
                    "agents_total": len(agents)
                }
            }
            
            return final_result
            
        except Exception as e:
            # Handle catastrophic failure
            processing_time = time.time() - start_time
            return {
                "analysis_id": f"failed_analysis_{int(time.time())}",
                "permit_id": permit_data.get("id"),
                "analysis_complete": False,
                "confidence_score": 0.0,
                "processing_time": round(processing_time, 2),
                "error": f"Multi-agent analysis failed: {str(e)}",
                "timestamp": datetime.utcnow(),
                "agents_involved": [],
                "ai_version": "1.0",
                # Required fields with empty defaults
                "executive_summary": {
                    "overall_score": 0.0,
                    "critical_issues": 0,
                    "recommendations": 0,
                    "compliance_level": "not_analyzed",
                    "estimated_completion_time": "Unknown",
                    "key_findings": ["Analysis failed"],
                    "next_steps": ["Retry analysis"]
                },
                "action_items": [],
                "citations": {},
                "completion_roadmap": {},
                "performance_metrics": {
                    "total_processing_time": processing_time,
                    "parallel_phase_time": 0.0,
                    "agents_successful": 0,
                    "agents_total": 5
                }
            }
    
    async def _run_agent_with_timeout(self, agent_coroutine, agent_name: str):
        """
        Run agent with timeout protection
        """
        try:
            return await asyncio.wait_for(agent_coroutine, timeout=self.analysis_timeout)
        except asyncio.TimeoutError:
            return Exception(f"Agent {agent_name} timed out after {self.analysis_timeout} seconds")
        except Exception as e:
            return Exception(f"Agent {agent_name} failed: {str(e)}")
    
    def _extract_result(self, result, agent_name: str) -> Dict[str, Any]:
        """
        Extract result from parallel execution, handling exceptions
        """
        if isinstance(result, Exception):
            return self._create_error_result(agent_name, str(result))
        return result
    
    def _create_error_result(self, agent_name: str, error_message: str) -> Dict[str, Any]:
        """
        Create standardized error result for failed agents
        """
        return {
            "analysis_complete": False,
            "confidence_score": 0.0,
            "agent_name": agent_name,
            "error": error_message,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_overall_confidence(self, agent_results: List[Dict[str, Any]]) -> float:
        """
        Calculate overall confidence score from all agent results
        """
        valid_scores = []
        
        for result in agent_results:
            if isinstance(result, dict) and result.get("analysis_complete", False):
                confidence = result.get("confidence_score", 0.0)
                if isinstance(confidence, (int, float)) and 0 <= confidence <= 1:
                    valid_scores.append(confidence)
        
        if not valid_scores:
            return 0.0
        
        # Calculate weighted average (can be customized based on agent importance)
        return sum(valid_scores) / len(valid_scores)
    
    def _get_processing_time(self, result) -> float:
        """
        Extract processing time from agent result
        """
        if isinstance(result, dict):
            return result.get("processing_time", 0.0)
        return 0.0
    
    async def validate_analysis_quality(self, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate the quality of the multi-agent analysis
        """
        validation_result = {
            "valid": True,
            "issues": [],
            "recommendations": []
        }
        
        # Check if analysis completed successfully
        if not analysis_result.get("analysis_complete", False):
            validation_result["valid"] = False
            validation_result["issues"].append("Analysis did not complete successfully")
        
        # Check confidence score
        confidence = analysis_result.get("confidence_score", 0.0)
        if confidence < 0.6:
            validation_result["issues"].append(f"Low confidence score: {confidence}")
            validation_result["recommendations"].append("Consider manual review of results")
        
        # Check if critical components are present
        required_components = ["action_items", "executive_summary", "citations"]
        for component in required_components:
            if component not in analysis_result or not analysis_result[component]:
                validation_result["issues"].append(f"Missing or empty component: {component}")
        
        # Check action items quality
        action_items = analysis_result.get("action_items", [])
        if len(action_items) == 0:
            validation_result["issues"].append("No action items generated")
        elif len(action_items) > 20:
            validation_result["recommendations"].append("Consider consolidating action items - too many may overwhelm users")
        
        # Check for high priority issues
        high_priority_items = [item for item in action_items if item.get("priority") == "alta"]
        if len(high_priority_items) > 10:
            validation_result["recommendations"].append("High number of critical issues - consider immediate review")
        
        return validation_result
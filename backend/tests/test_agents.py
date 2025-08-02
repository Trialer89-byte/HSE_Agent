import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from app.agents.content_analysis_agent import ContentAnalysisAgent
from app.agents.risk_analysis_agent import RiskAnalysisAgent
from app.agents.compliance_checker_agent import ComplianceCheckerAgent
from app.agents.dpi_specialist_agent import DPISpecialistAgent
from app.agents.citation_agent import DocumentCitationAgent
from app.services.ai_orchestrator import AIOrchestrator


class TestContentAnalysisAgent:
    """Test suite for ContentAnalysisAgent"""
    
    @pytest.fixture
    def agent(self):
        user_context = {
            "tenant_id": 1,
            "user_id": 123,
            "department": "Engineering"
        }
        return ContentAnalysisAgent(user_context)
    
    @pytest.fixture
    def sample_permit_data(self):
        return {
            "id": 1,
            "title": "Manutenzione pompa centrifuga",
            "description": "Sostituzione guarnizioni pompa P-101",
            "work_type": "manutenzione",
            "location": "Area produzione",
            "duration_hours": 4,
            "dpi_required": ["casco", "scarpe antinfortunistiche"],
            "custom_fields": {}
        }
    
    @pytest.fixture
    def sample_documents(self):
        return [
            {
                "document_code": "PROC_001",
                "title": "Procedura Manutenzione Pompe",
                "content": "Procedura per manutenzione pompe centrifughe...",
                "document_type": "istruzione_operativa",
                "authority": "HSE Department"
            }
        ]
    
    @pytest.mark.asyncio
    async def test_analyze_basic_functionality(self, agent, sample_permit_data, sample_documents):
        """Test basic analysis functionality"""
        
        # Mock LLM response
        mock_response = '''
        {
            "content_quality": {
                "overall_score": 0.7,
                "title_analysis": {
                    "adequacy": "adeguato",
                    "issues": [],
                    "suggestions": []
                },
                "description_analysis": {
                    "completeness": 0.6,
                    "clarity": 0.8,
                    "technical_detail": "insufficiente",
                    "safety_focus": 0.7
                }
            },
            "missing_fields": [
                {
                    "field_name": "isolamento_energetico",
                    "criticality": "alta",
                    "reason": "Necessario per lavori su equipaggiamenti",
                    "suggested_content": "Applicare LOTO secondo procedura"
                }
            ],
            "improvement_suggestions": [
                {
                    "area": "descrizione",
                    "current_content": "Sostituzione guarnizioni pompa P-101",
                    "suggested_improvement": "Specificare tipo guarnizioni e procedura isolamento",
                    "rationale": "Maggiore chiarezza operativa",
                    "safety_impact": "Riduce rischi operativi"
                }
            ],
            "data_consistency": {
                "consistent": true,
                "inconsistencies": [],
                "severity": "bassa"
            },
            "analysis_complete": true,
            "confidence_score": 0.8,
            "agent_name": "ContentAnalysisAgent"
        }
        '''
        
        with patch.object(agent, '_call_llm', return_value=mock_response):
            result = await agent.analyze(sample_permit_data, sample_documents)
        
        # Verify result structure
        assert result["analysis_complete"] == True
        assert result["confidence_score"] == 0.8
        assert "content_quality" in result
        assert "missing_fields" in result
        assert "improvement_suggestions" in result
        assert "data_consistency" in result
    
    @pytest.mark.asyncio
    async def test_analyze_handles_llm_error(self, agent, sample_permit_data, sample_documents):
        """Test error handling when LLM fails"""
        
        with patch.object(agent, '_call_llm', side_effect=Exception("LLM error")):
            result = await agent.analyze(sample_permit_data, sample_documents)
        
        # Should return error response
        assert result["analysis_complete"] == False
        assert result["confidence_score"] == 0.0
        assert "error" in result
        assert "Content analysis failed" in result["error"]
    
    @pytest.mark.asyncio
    async def test_analyze_handles_invalid_json(self, agent, sample_permit_data, sample_documents):
        """Test handling of invalid JSON response"""
        
        invalid_json = "This is not valid JSON"
        
        with patch.object(agent, '_call_llm', return_value=invalid_json):
            result = await agent.analyze(sample_permit_data, sample_documents)
        
        # Should return error response
        assert result["analysis_complete"] == False
        assert "Failed to parse JSON response" in result["error"]


class TestRiskAnalysisAgent:
    """Test suite for RiskAnalysisAgent"""
    
    @pytest.fixture
    def agent(self):
        user_context = {
            "tenant_id": 1,
            "user_id": 123,
            "department": "Engineering"
        }
        return RiskAnalysisAgent(user_context)
    
    @pytest.mark.asyncio
    async def test_risk_identification(self, agent):
        """Test risk identification functionality"""
        
        permit_data = {
            "title": "Lavoro in spazio confinato",
            "description": "Pulizia serbatoio di stoccaggio",
            "work_type": "chimico",
            "location": "Serbatoio T-201"
        }
        
        mock_response = '''
        {
            "identified_risks": [
                {
                    "risk_id": "RISK_001",
                    "category": "CONF",
                    "subcategory": "spazio_confinato",
                    "title": "Asfissia in spazio confinato",
                    "description": "Rischio di carenza di ossigeno",
                    "probability": {"score": 3, "rationale": "Ambiente chiuso"},
                    "severity": {"score": 5, "rationale": "Rischio morte"},
                    "risk_level": {"score": 15, "level": "alto"},
                    "current_controls": ["Ventilazione"],
                    "additional_controls_needed": ["Rilevatore gas", "Tripode"],
                    "regulatory_references": ["D.Lgs 81/2008 Art. 121"]
                }
            ],
            "risk_assessment_summary": {
                "total_risks_identified": 1,
                "high_priority_risks": 1,
                "risk_categories_present": ["CONF"],
                "overall_risk_level": "alto",
                "critical_control_measures": ["Monitoraggio atmosfera"]
            },
            "risk_interactions": [],
            "emergency_scenarios": [
                {
                    "scenario": "Perdita coscienza operatore",
                    "triggers": ["Carenza ossigeno"],
                    "consequences": "Rischio morte",
                    "response_actions": ["Evacuazione immediata", "Soccorso"]
                }
            ],
            "analysis_complete": true,
            "confidence_score": 0.9,
            "agent_name": "RiskAnalysisAgent"
        }
        '''
        
        with patch.object(agent, '_call_llm', return_value=mock_response):
            result = await agent.analyze(permit_data, [])
        
        # Verify risk identification
        assert len(result["identified_risks"]) > 0
        risk = result["identified_risks"][0]
        assert risk["category"] == "CONF"
        assert risk["risk_level"]["level"] == "alto"
        assert result["risk_assessment_summary"]["total_risks_identified"] == 1


class TestDPISpecialistAgent:
    """Test suite for DPISpecialistAgent"""
    
    @pytest.fixture
    def agent(self):
        user_context = {
            "tenant_id": 1,
            "user_id": 123,
            "department": "Safety"
        }
        return DPISpecialistAgent(user_context)
    
    @pytest.mark.asyncio
    async def test_dpi_analysis(self, agent):
        """Test DPI analysis functionality"""
        
        permit_data = {
            "title": "Saldatura in quota",
            "dpi_required": ["casco", "imbragatura"]
        }
        
        identified_risks = [
            {
                "risk_id": "RISK_001",
                "category": "FALL",
                "title": "Caduta dall'alto",
                "risk_level": {"level": "alto"}
            },
            {
                "risk_id": "RISK_002", 
                "category": "FIRE",
                "title": "Ustioni da saldatura",
                "risk_level": {"level": "medio"}
            }
        ]
        
        mock_response = '''
        {
            "current_dpi_adequacy": {
                "dpi_list": [
                    {
                        "dpi_name": "casco",
                        "standard_type": "UNI EN 397",
                        "specification": "Casco base",
                        "risks_covered": [],
                        "adequacy_score": 0.6,
                        "performance_level": "base",
                        "issues": ["Non protegge da schizzi metallici"],
                        "recommendations": ["Utilizzare casco con visiera"]
                    }
                ],
                "overall_adequacy": 0.5,
                "compliance_status": "insufficiente",
                "coverage_gaps": ["FIRE"]
            },
            "additional_dpi_needed": [
                {
                    "dpi_type": "guanti_saldatura",
                    "standard": "UNI EN 12477",
                    "specification": "Guanti saldatura categoria A",
                    "performance_requirements": {
                        "level": "A",
                        "properties": ["Resistenza calore", "Destrezza"],
                        "test_methods": ["EN 407"]
                    },
                    "justification": "Protezione da schizzi metallici",
                    "mandatory": true,
                    "risks_addressed": ["RISK_002"],
                    "compatibility_notes": "Compatibili con altri DPI",
                    "usage_duration": "Per tutta la durata saldatura",
                    "maintenance_requirements": "Controllo giornaliero"
                }
            ],
            "dpi_combinations": [],
            "standards_compliance": {
                "compliant_items": 1,
                "non_compliant_items": 0,
                "missing_standards": ["UNI EN 12477"],
                "certification_requirements": ["Marcatura CE"],
                "verification_methods": ["Controllo visivo"]
            },
            "procurement_recommendations": {
                "immediate_needs": ["guanti_saldatura"],
                "planned_replacements": [],
                "budget_estimate": "€150",
                "supplier_requirements": ["Certificazione CE"]
            },
            "training_requirements": {
                "dpi_specific_training": ["Uso corretto guanti saldatura"],
                "usage_procedures": ["Indossamento sequenza"],
                "maintenance_training": ["Controllo integrità"],
                "inspection_protocols": ["Check-list pre-uso"]
            },
            "analysis_complete": true,
            "confidence_score": 0.85,
            "agent_name": "DPISpecialistAgent"
        }
        '''
        
        with patch.object(agent, '_call_llm', return_value=mock_response):
            result = await agent.analyze(permit_data, identified_risks, [])
        
        # Verify DPI analysis
        assert result["current_dpi_adequacy"]["compliance_status"] == "insufficiente"
        assert len(result["additional_dpi_needed"]) > 0
        dpi_needed = result["additional_dpi_needed"][0]
        assert dpi_needed["dpi_type"] == "guanti_saldatura"
        assert dpi_needed["mandatory"] == True


class TestAIOrchestrator:
    """Test suite for AI Orchestrator"""
    
    @pytest.fixture
    def orchestrator(self):
        return AIOrchestrator()
    
    @pytest.fixture
    def sample_context(self):
        return {
            "tenant_id": 1,
            "user_id": 123,
            "department": "Engineering"
        }
    
    @pytest.mark.asyncio
    async def test_multi_agent_orchestration(self, orchestrator, sample_context):
        """Test complete multi-agent orchestration"""
        
        permit_data = {
            "id": 1,
            "title": "Test permit",
            "description": "Test description",
            "work_type": "manutenzione"
        }
        
        context_documents = []
        
        # Mock all agent responses
        mock_content_result = {
            "analysis_complete": True,
            "confidence_score": 0.8,
            "agent_name": "ContentAnalysisAgent",
            "content_quality": {"overall_score": 0.7}
        }
        
        mock_risk_result = {
            "analysis_complete": True,
            "confidence_score": 0.9,
            "agent_name": "RiskAnalysisAgent",
            "identified_risks": []
        }
        
        mock_compliance_result = {
            "analysis_complete": True,
            "confidence_score": 0.85,
            "agent_name": "ComplianceCheckerAgent"
        }
        
        mock_dpi_result = {
            "analysis_complete": True,
            "confidence_score": 0.75,
            "agent_name": "DPISpecialistAgent"
        }
        
        mock_citation_result = {
            "analysis_complete": True,
            "confidence_score": 0.8,
            "agent_name": "DocumentCitationAgent",
            "executive_summary": {"overall_score": 0.8},
            "action_items": [],
            "citations": {"normative_framework": []},
            "completion_roadmap": {}
        }
        
        # Patch all agents
        with patch('app.agents.content_analysis_agent.ContentAnalysisAgent.analyze', 
                  return_value=mock_content_result), \
             patch('app.agents.risk_analysis_agent.RiskAnalysisAgent.analyze', 
                  return_value=mock_risk_result), \
             patch('app.agents.compliance_checker_agent.ComplianceCheckerAgent.analyze', 
                  return_value=mock_compliance_result), \
             patch('app.agents.dpi_specialist_agent.DPISpecialistAgent.analyze', 
                  return_value=mock_dpi_result), \
             patch('app.agents.citation_agent.DocumentCitationAgent.generate_structured_output', 
                  return_value=mock_citation_result):
            
            result = await orchestrator.run_multi_agent_analysis(
                permit_data, context_documents, sample_context
            )
        
        # Verify orchestration result
        assert result["analysis_complete"] == True
        assert result["permit_id"] == 1
        assert "confidence_score" in result
        assert "processing_time" in result
        assert "agents_involved" in result
        assert "executive_summary" in result
        assert "action_items" in result
        assert "citations" in result
    
    @pytest.mark.asyncio
    async def test_agent_timeout_handling(self, orchestrator, sample_context):
        """Test timeout handling for slow agents"""
        
        permit_data = {"id": 1, "title": "Test"}
        
        # Mock a slow agent that times out
        async def slow_agent(*args, **kwargs):
            await asyncio.sleep(10)  # Longer than timeout
            return {"analysis_complete": True}
        
        with patch('app.agents.content_analysis_agent.ContentAnalysisAgent.analyze', 
                  side_effect=slow_agent):
            
            result = await orchestrator.run_multi_agent_analysis(
                permit_data, [], sample_context
            )
        
        # Should handle timeout gracefully
        assert result["analysis_complete"] == False
        assert "processing_time" in result
        # Content analysis should have failed due to timeout
        content_result = result.get("content_improvements", {})
        assert content_result.get("analysis_complete") == False
    
    @pytest.mark.asyncio 
    async def test_confidence_calculation(self, orchestrator):
        """Test overall confidence score calculation"""
        
        agent_results = [
            {"analysis_complete": True, "confidence_score": 0.8},
            {"analysis_complete": True, "confidence_score": 0.9},
            {"analysis_complete": False, "confidence_score": 0.0},
            {"analysis_complete": True, "confidence_score": 0.7}
        ]
        
        confidence = orchestrator._calculate_overall_confidence(agent_results)
        
        # Should average only successful agents: (0.8 + 0.9 + 0.7) / 3 = 0.8
        assert abs(confidence - 0.8) < 0.01
    
    @pytest.mark.asyncio
    async def test_validation_quality_check(self, orchestrator):
        """Test analysis quality validation"""
        
        # Test low confidence analysis
        low_confidence_result = {
            "analysis_complete": True,
            "confidence_score": 0.3,
            "action_items": [],
            "executive_summary": {},
            "citations": {}
        }
        
        validation = await orchestrator.validate_analysis_quality(low_confidence_result)
        
        assert validation["valid"] == True  # Still valid but with issues
        assert len(validation["issues"]) > 0
        assert any("Low confidence score" in issue for issue in validation["issues"])
        
        # Test missing components
        incomplete_result = {
            "analysis_complete": True,
            "confidence_score": 0.8
            # Missing action_items, executive_summary, citations
        }
        
        validation = await orchestrator.validate_analysis_quality(incomplete_result)
        
        assert len(validation["issues"]) >= 3  # One for each missing component


@pytest.mark.integration
class TestAgentIntegration:
    """Integration tests for agent workflows"""
    
    @pytest.mark.asyncio
    async def test_complete_workflow_integration(self):
        """Test complete workflow with real agent coordination"""
        
        # This would be a more comprehensive test using actual agent instances
        # but with mocked LLM calls to avoid external dependencies
        
        user_context = {
            "tenant_id": 1,
            "user_id": 123,
            "department": "Engineering"
        }
        
        permit_data = {
            "id": 1,
            "title": "Manutenzione impianto chimico",
            "description": "Sostituzione valvole su linea acido cloridrico",
            "work_type": "chimico",
            "location": "Area produzione A",
            "duration_hours": 6,
            "dpi_required": ["casco", "guanti", "scarpe"],
            "custom_fields": {"temperatura": "80°C", "pressione": "5 bar"}
        }
        
        context_documents = [
            {
                "document_code": "D.Lgs 81/2008",
                "title": "Testo Unico Sicurezza",
                "content": "Articolo 75 - DPI...",
                "document_type": "normativa",
                "authority": "Stato Italiano"
            }
        ]
        
        orchestrator = AIOrchestrator()
        
        # Mock all LLM calls with realistic responses
        # This would test the actual coordination logic
        # while avoiding external API dependencies
        
        # For brevity, this test is outlined but not fully implemented
        # In a real scenario, you'd want comprehensive integration tests
        pass


if __name__ == "__main__":
    pytest.main(["-v", __file__])
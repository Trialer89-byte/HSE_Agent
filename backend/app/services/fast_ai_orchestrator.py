from typing import Dict, Any, List
import time
import json
from datetime import datetime

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.config.settings import settings


class FastAIOrchestrator:
    """
    Fast AI Orchestrator - Single direct AI call without agents
    """
    
    def __init__(self):
        # Configure Gemini
        if genai and settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel(settings.gemini_model)
        else:
            raise ValueError("Gemini API key required for FastAIOrchestrator")
    
    async def run_fast_analysis(
        self,
        permit_data: Dict[str, Any],
        context_documents: List[Dict[str, Any]],
        user_context: Dict[str, Any],
        vector_service=None
    ) -> Dict[str, Any]:
        """
        Run fast single-call AI analysis without agents
        """
        start_time = time.time()
        print(f"[FastAIOrchestrator] Starting fast analysis for permit {permit_data.get('id')}")
        
        try:
            # Prepare context
            permit_summary = self._format_permit_data(permit_data)
            documents_summary = self._format_documents(context_documents)
            
            # Create comprehensive prompt
            prompt = f"""
Sei un esperto HSE che deve analizzare rapidamente un permesso di lavoro.

PERMESSO DI LAVORO:
{permit_summary}

DOCUMENTI DI RIFERIMENTO DISPONIBILI:
{documents_summary}

Analizza il permesso e fornisci una valutazione rapida ma completa che includa:
1. Identificazione dei principali rischi
2. DPI necessari (sii specifico)
3. Gap di conformità evidenti
4. Raccomandazioni prioritarie

Rispondi in formato JSON strutturato:
{{
    "executive_summary": {{
        "overall_score": 0.0-1.0,
        "critical_issues": numero,
        "recommendations": numero,
        "compliance_level": "compliant|requires_action|non_compliant",
        "estimated_completion_time": "tempo stimato (es. 2 giorni, 1 settimana)",
        "key_findings": ["lista scoperte principali"],
        "next_steps": ["prossimi passi da fare"]
    }},
    "action_items": [
        {{
            "id": "ACT_001",
            "type": "risk_mitigation|dpi_requirement|compliance_gap|content_improvement",
            "priority": "alta|media|bassa",
            "title": "titolo breve azione",
            "description": "descrizione dettagliata",
            "suggested_action": "azione specifica suggerita",
            "consequences_if_ignored": "conseguenze se ignorato",
            "references": ["riferimenti normativi"],
            "estimated_effort": "sforzo stimato",
            "responsible_role": "ruolo responsabile",
            "frontend_display": {{
                "color": "red|orange|blue",
                "icon": "alert-triangle|shield-check|file-text",
                "category": "categoria display"
            }}
        }}
    ],
    "citations": {{
        "normative_framework": [],
        "company_procedures": []
    }},
    "completion_roadmap": {{
        "immediate_actions": ["azioni immediate"],
        "short_term_actions": ["azioni breve termine"],
        "medium_term_actions": ["azioni medio termine"],
        "success_metrics": ["metriche di successo"],
        "review_checkpoints": ["checkpoint di verifica"]
    }},
    "performance_metrics": {{
        "analysis_depth": "fast",
        "agents_used": 0,
        "documents_analyzed": numero
    }},
    "analysis_complete": true,
    "confidence_score": 0.0-1.0
}}

IMPORTANTE: Sii specifico e pratico nelle raccomandazioni. Non fare riferimenti a normative non presenti nei documenti forniti.
"""
            
            # Call Gemini directly
            response = self.model.generate_content(prompt)
            
            # Parse response
            try:
                result = json.loads(self._clean_json_response(response.text))
            except json.JSONDecodeError:
                # Fallback structure if parsing fails
                result = {
                    "executive_summary": {
                        "overall_score": 0.5,
                        "critical_issues": 0,
                        "recommendations": 1,
                        "compliance_level": "requires_action",
                        "estimated_completion_time": "Da determinare",
                        "key_findings": ["Analisi rapida completata"],
                        "next_steps": ["Verificare i risultati dell'analisi"]
                    },
                    "action_items": [],
                    "citations": {
                        "normative_framework": [],
                        "company_procedures": []
                    },
                    "completion_roadmap": {
                        "immediate_actions": [],
                        "short_term_actions": [],
                        "medium_term_actions": [],
                        "success_metrics": [],
                        "review_checkpoints": []
                    },
                    "performance_metrics": {
                        "analysis_depth": "fast",
                        "agents_used": 0,
                        "documents_analyzed": len(context_documents)
                    },
                    "analysis_complete": True,
                    "confidence_score": 0.5,
                    "error": "Failed to parse AI response"
                }
            
            # Add metadata
            processing_time = time.time() - start_time
            result.update({
                "analysis_id": f"fast_{permit_data.get('id')}_{int(time.time())}",
                "permit_id": permit_data.get('id'),
                "processing_time": processing_time,
                "timestamp": datetime.utcnow().isoformat(),
                "ai_version": "fast_1.0",
                "agents_involved": ["FastAI"]
            })
            
            print(f"[FastAIOrchestrator] Analysis completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            print(f"[FastAIOrchestrator] Error: {str(e)}")
            return {
                "analysis_complete": False,
                "error": str(e),
                "confidence_score": 0.0,
                "processing_time": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _format_permit_data(self, permit_data: Dict[str, Any]) -> str:
        """Format permit data for prompt"""
        return f"""
- ID: {permit_data.get('id')}
- Titolo: {permit_data.get('title')}
- Descrizione: {permit_data.get('description')}
- Tipo lavoro: {permit_data.get('work_type')}
- Ubicazione: {permit_data.get('location')}
- Durata: {permit_data.get('duration_hours')} ore
- DPI già specificati: {', '.join(permit_data.get('dpi_required', []))}
"""
    
    def _format_documents(self, documents: List[Dict[str, Any]]) -> str:
        """Format documents for prompt"""
        if not documents:
            return "Nessun documento di riferimento disponibile"
        
        formatted = ""
        for i, doc in enumerate(documents[:5], 1):  # Limit to top 5
            formatted += f"""
{i}. {doc.get('title', 'Documento senza titolo')}
   Tipo: {doc.get('document_type', 'N/A')}
   Contenuto: {doc.get('content', '')[:200]}...
"""
        return formatted
    
    def _clean_json_response(self, response_text: str) -> str:
        """Clean response to extract JSON"""
        import re
        
        # Remove markdown code blocks
        response_text = re.sub(r'```json\s*', '', response_text)
        response_text = re.sub(r'```\s*$', '', response_text)
        response_text = response_text.strip()
        
        # Find JSON bounds
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            return response_text[start_idx:end_idx + 1]
        
        return response_text
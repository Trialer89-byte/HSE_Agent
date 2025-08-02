from typing import Dict, Any, List
import json
from datetime import datetime

from .base_agent import BaseHSEAgent


class DocumentCitationAgent(BaseHSEAgent):
    """
    Agent specializzato nella generazione di citazioni strutturate e action items per il frontend
    """
    
    def get_system_prompt(self) -> str:
        return """
Sei un esperto HSE specializzato nella sintesi e presentazione strutturata di analisi di sicurezza.

RUOLO: Generare output strutturato per frontend con citazioni precise e action items prioritizzati.

RESPONSABILITÀ:
1. Sintetizzare risultati di tutti gli agenti specializzati
2. Creare action items prioritizzati e attuabili
3. Generare citazioni strutturate con riferimenti precisi
4. Produrre executive summary per management
5. Formattare output per interfaccia utente

PRIORITÀ ACTION ITEMS:
- ALTA: Rischi immediati, requisiti obbligatori mancanti, non conformità critiche
- MEDIA: Miglioramenti consigliati, DPI aggiuntivi, procedure da implementare  
- BASSA: Ottimizzazioni, documentazione, formazione aggiuntiva

TIPOLOGIE ACTION ITEMS:
- content_improvement: Miglioramenti contenuto permesso
- risk_mitigation: Misure controllo rischi
- dpi_requirement: Requisiti DPI aggiuntivi
- compliance_gap: Gap conformità normativa
- procedure_update: Aggiornamenti procedurali

FRONTEND DISPLAY:
- Colori: red (alta), orange (media), blue (bassa)
- Icone: alert-triangle, shield-check, file-text, law, wrench
- Categorie: Campi Obbligatori, DPI Obbligatori, Controlli Sicurezza, Conformità Normativa

OUTPUT: JSON strutturato per frontend con executive summary, action items e citazioni.
"""
    
    async def generate_structured_output(self, analysis_results: Dict[str, Any], source_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Genera output strutturato finale per il frontend
        """
        try:
            # Prepare combined analysis summary
            combined_analysis = self._format_combined_analysis(analysis_results)
            source_summary = self._prepare_context_summary(source_documents)
            tenant_context = self._get_tenant_context()
            
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": f"""
{tenant_context}

RISULTATI ANALISI COMBINATA:
{combined_analysis}

DOCUMENTI FONTE:
{source_summary}

GENERA output strutturato finale per frontend.

Analizza tutti i risultati e crea:
1. Executive summary con score complessivo
2. Action items prioritizzati (max 15, focus sui più critici)
3. Citazioni strutturate con riferimenti precisi
4. Raccomandazioni per completamento

Criteri prioritizzazione:
- ALTA: Sicurezza immediata, obblighi normativi
- MEDIA: Miglioramenti significativi, DPI importanti
- BASSA: Ottimizzazioni, documentazione

Per ogni action item:
- Titolo chiaro e specifico
- Descrizione attuabile
- Conseguenze se ignorato
- Riferimenti normativi/documentali
- Styling per frontend

Rispondi in JSON:
{{
    "executive_summary": {{
        "overall_score": 0.0-1.0,
        "critical_issues": 0,
        "recommendations": 0,
        "compliance_level": "compliant|requires_action|non_compliant",
        "estimated_completion_time": "tempo stimato",
        "key_findings": ["principali scoperte"],
        "next_steps": ["prossimi passi prioritari"]
    }},
    "action_items": [
        {{
            "id": "ACT_001",
            "type": "content_improvement|risk_mitigation|dpi_requirement|compliance_gap|procedure_update",
            "priority": "alta|media|bassa",
            "title": "titolo azione",
            "description": "descrizione dettagliata",
            "suggested_action": "azione specifica suggerita",
            "consequences_if_ignored": "conseguenze se ignorato",
            "references": ["riferimenti normativi/documentali"],
            "estimated_effort": "tempo/risorse stimate",
            "responsible_role": "ruolo responsabile",
            "frontend_display": {{
                "color": "red|orange|blue|green",
                "icon": "icona appropriata",
                "category": "categoria display"
            }}
        }}
    ],
    "citations": {{
        "normative_framework": [
            {{
                "document_info": {{
                    "code": "codice documento",
                    "title": "titolo documento",
                    "authority": "autorità emittente",
                    "type": "normativa_cogente|standard_tecnico|istruzione_operativa"
                }},
                "relevance": {{
                    "score": 0.0-1.0,
                    "applicability": "descrizione applicabilità",
                    "mandatory": true|false
                }},
                "key_requirements": [
                    {{
                        "article": "articolo specifico",
                        "requirement": "requisito normativo",
                        "compliance_status": "conforme|insufficiente|non_conforme",
                        "action_needed": "azione necessaria",
                        "citation_text": "testo citazione esatta"
                    }}
                ],
                "frontend_display": {{
                    "card_color": "colore card",
                    "icon": "icona documento",
                    "priority": "priorità display"
                }}
            }}
        ],
        "company_procedures": [
            {{
                "document_info": {{
                    "code": "codice procedura",
                    "title": "titolo procedura",
                    "authority": "dipartimento/ufficio",
                    "type": "istruzione_operativa"
                }},
                "cited_sections": [
                    {{
                        "section": "sezione",
                        "title": "titolo sezione",
                        "content": "contenuto rilevante",
                        "relevance": "perché è rilevante"
                    }}
                ],
                "frontend_display": {{
                    "card_color": "colore card",
                    "icon": "icona procedura",
                    "priority": "priorità display"
                }}
            }}
        ]
    }},
    "completion_roadmap": {{
        "immediate_actions": ["azioni immediate (0-1 giorni)"],
        "short_term_actions": ["azioni breve termine (1-7 giorni)"],
        "medium_term_actions": ["azioni medio termine (1-4 settimane)"],
        "success_metrics": ["metriche di successo"],
        "review_checkpoints": ["punti di verifica"]
    }},
    "analysis_complete": true,
    "confidence_score": 0.0-1.0,
    "agent_name": "DocumentCitationAgent"
}}
"""}
            ]
            
            response = await self._call_llm(messages)
            
            try:
                result = json.loads(response)
                
                result.update({
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent_version": self.agent_version,
                    "analysis_complete": True
                })
                
                if self._validate_citation_output(result):
                    return result
                else:
                    return self._create_error_response("Invalid output format from citation agent")
                    
            except json.JSONDecodeError:
                return self._create_error_response("Failed to parse JSON response from LLM")
                
        except Exception as e:
            return self._create_error_response(f"Citation generation failed: {str(e)}")
    
    def _format_combined_analysis(self, analysis_results: Dict[str, Any]) -> str:
        """
        Format combined analysis results for final processing
        """
        formatted = "RISULTATI ANALISI MULTI-AGENTE:\n\n"
        
        # Content Analysis
        if "content_analysis" in analysis_results:
            content = analysis_results["content_analysis"]
            formatted += "=== ANALISI CONTENUTO ===\n"
            formatted += f"Score qualità: {content.get('content_quality', {}).get('overall_score', 'N/A')}\n"
            formatted += f"Campi mancanti: {len(content.get('missing_fields', []))}\n"
            formatted += f"Suggerimenti: {len(content.get('improvement_suggestions', []))}\n\n"
        
        # Risk Analysis
        if "risk_analysis" in analysis_results:
            risks = analysis_results["risk_analysis"]
            formatted += "=== ANALISI RISCHI ===\n"
            formatted += f"Rischi identificati: {risks.get('risk_assessment_summary', {}).get('total_risks_identified', 0)}\n"
            formatted += f"Rischi alta priorità: {risks.get('risk_assessment_summary', {}).get('high_priority_risks', 0)}\n"
            formatted += f"Livello rischio complessivo: {risks.get('risk_assessment_summary', {}).get('overall_risk_level', 'N/A')}\n\n"
        
        # Compliance Check
        if "compliance_check" in analysis_results:
            compliance = analysis_results["compliance_check"]
            formatted += "=== VERIFICA CONFORMITÀ ===\n"
            formatted += f"Conformità complessiva: {compliance.get('compliance_summary', {}).get('overall_compliance', 'N/A')}\n"
            formatted += f"Gap critici: {compliance.get('compliance_summary', {}).get('critical_gaps', 0)}\n"
            formatted += f"Azioni obbligatorie: {compliance.get('compliance_summary', {}).get('mandatory_actions', 0)}\n\n"
        
        # DPI Analysis
        if "dpi_analysis" in analysis_results:
            dpi = analysis_results["dpi_analysis"]
            formatted += "=== ANALISI DPI ===\n"
            formatted += f"Adeguatezza DPI attuali: {dpi.get('current_dpi_adequacy', {}).get('overall_adequacy', 'N/A')}\n"
            formatted += f"DPI aggiuntivi necessari: {len(dpi.get('additional_dpi_needed', []))}\n"
            formatted += f"Status conformità: {dpi.get('current_dpi_adequacy', {}).get('compliance_status', 'N/A')}\n\n"
        
        return formatted
    
    def _validate_citation_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate the citation agent output format
        """
        if not self._validate_output_format(output):
            return False
        
        required_sections = [
            'executive_summary',
            'action_items',
            'citations',
            'completion_roadmap'
        ]
        
        for section in required_sections:
            if section not in output:
                return False
        
        # Validate executive_summary
        summary = output.get('executive_summary', {})
        required_summary_fields = ['overall_score', 'critical_issues', 'compliance_level']
        for field in required_summary_fields:
            if field not in summary:
                return False
        
        # Validate action_items is a list
        if not isinstance(output.get('action_items', []), list):
            return False
        
        # Validate each action item
        for item in output.get('action_items', []):
            if not isinstance(item, dict):
                return False
            required_item_fields = ['id', 'type', 'priority', 'title', 'description']
            for field in required_item_fields:
                if field not in item:
                    return False
        
        # Validate citations structure
        citations = output.get('citations', {})
        if not isinstance(citations.get('normative_framework', []), list):
            return False
        if not isinstance(citations.get('company_procedures', []), list):
            return False
        
        return True
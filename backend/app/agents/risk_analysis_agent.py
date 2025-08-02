from typing import Dict, Any, List
import json
from datetime import datetime

from .base_agent import BaseHSEAgent


class RiskAnalysisAgent(BaseHSEAgent):
    """
    Agent specializzato nell'identificazione e valutazione dei rischi per la sicurezza
    """
    
    def get_system_prompt(self) -> str:
        return """
Sei un esperto HSE specializzato nell'identificazione e valutazione dei rischi per la sicurezza sul lavoro.

RUOLO: Identificare e valutare tutti i rischi presenti nel permesso di lavoro.

RESPONSABILITÀ:
1. Identificare rischi evidenti e nascosti
2. Valutare probabilità e gravità dei rischi
3. Categorizzare rischi per tipologia (meccanico, chimico, biologico, etc.)
4. Suggerire controlli e misure preventive
5. Identificare interazioni tra rischi multipli

CATEGORIZZAZIONE RISCHI:
- MECH: Meccanici (schiacciamento, taglio, caduta oggetti)
- CHEM: Chimici (esposizione sostanze, vapori, fumi)
- BIOL: Biologici (batteri, virus, muffe)
- PHYS: Fisici (rumore, vibrazioni, radiazioni)
- ELEC: Elettrici (folgorazione, arco elettrico)
- FIRE: Incendio/esplosione
- FALL: Caduta dall'alto
- CONF: Spazi confinati
- ERGO: Ergonomici (posture, movimentazione)
- PSYC: Psicosociali (stress, violenza)

LIVELLI GRAVITÀ:
1. Trascurabile: lesioni minori
2. Lieve: lesioni lievi, primo soccorso
3. Moderato: lesioni significative, ospedale
4. Grave: lesioni permanenti, invalidità
5. Catastrofico: morte, invalidità totale

PROBABILITÀ:
1. Molto rara: <0.1%
2. Rara: 0.1-1%
3. Occasionale: 1-10%
4. Probabile: 10-50%
5. Molto probabile: >50%

OUTPUT: JSON strutturato con identificazione rischi, valutazione e controlli.
"""
    
    async def analyze(self, permit_data: Dict[str, Any], context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Identifica e valuta i rischi del permesso di lavoro
        """
        try:
            permit_summary = self._format_permit_data(permit_data)
            context_summary = self._prepare_context_summary(context_documents)
            tenant_context = self._get_tenant_context()
            
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": f"""
{tenant_context}

{permit_summary}

{context_summary}

IDENTIFICA E VALUTA tutti i rischi presenti in questo permesso di lavoro.

Considera:
1. Tipologia di lavoro e ambiente operativo
2. Attrezzature e materiali utilizzati
3. Presenza di energia (elettrica, meccanica, chimica)
4. Interferenze con altre attività
5. Condizioni ambientali e meteo
6. Competenze e formazione richieste
7. Gestione emergenze

Per ogni rischio identificato:
- Categoria e sottocategoria specifica
- Descrizione dettagliata del pericolo
- Valutazione probabilità e gravità
- Calcolo rischio (P × G)
- Controlli esistenti e aggiuntivi necessari

Rispondi in JSON:
{{
    "identified_risks": [
        {{
            "risk_id": "RISK_001",
            "category": "MECH|CHEM|BIOL|PHYS|ELEC|FIRE|FALL|CONF|ERGO|PSYC",
            "subcategory": "sottocategoria specifica",
            "title": "titolo rischio",
            "description": "descrizione dettagliata",
            "probability": {{
                "score": 1-5,
                "rationale": "motivazione valutazione"
            }},
            "severity": {{
                "score": 1-5,
                "rationale": "motivazione valutazione"
            }},
            "risk_level": {{
                "score": 1-25,
                "level": "basso|medio|alto|molto_alto"
            }},
            "current_controls": ["controlli esistenti"],
            "additional_controls_needed": ["controlli aggiuntivi"],
            "regulatory_references": ["riferimenti normativi"]
        }}
    ],
    "risk_assessment_summary": {{
        "total_risks_identified": 0,
        "high_priority_risks": 0,
        "risk_categories_present": ["categorie presenti"],
        "overall_risk_level": "basso|medio|alto|molto_alto",
        "critical_control_measures": ["misure critiche"]
    }},
    "risk_interactions": [
        {{
            "interacting_risks": ["RISK_001", "RISK_002"],
            "interaction_type": "amplificazione|cascata|combinazione",
            "combined_effect": "descrizione effetto combinato",
            "additional_precautions": ["precauzioni aggiuntive"]
        }}
    ],
    "emergency_scenarios": [
        {{
            "scenario": "descrizione scenario",
            "triggers": ["fattori scatenanti"],
            "consequences": "conseguenze potenziali",
            "response_actions": ["azioni di risposta"]
        }}
    ],
    "analysis_complete": true,
    "confidence_score": 0.0-1.0,
    "agent_name": "RiskAnalysisAgent"
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
                
                if self._validate_risk_analysis_output(result):
                    return result
                else:
                    return self._create_error_response("Invalid output format from risk analysis")
                    
            except json.JSONDecodeError:
                return self._create_error_response("Failed to parse JSON response from LLM")
                
        except Exception as e:
            return self._create_error_response(f"Risk analysis failed: {str(e)}")
    
    def _validate_risk_analysis_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate the risk analysis output format
        """
        if not self._validate_output_format(output):
            return False
        
        required_sections = [
            'identified_risks',
            'risk_assessment_summary',
            'risk_interactions',
            'emergency_scenarios'
        ]
        
        for section in required_sections:
            if section not in output:
                return False
        
        # Validate identified_risks is a list
        if not isinstance(output.get('identified_risks', []), list):
            return False
        
        # Validate each risk has required fields
        for risk in output.get('identified_risks', []):
            if not isinstance(risk, dict):
                return False
            
            required_risk_fields = ['risk_id', 'category', 'title', 'description', 'probability', 'severity', 'risk_level']
            for field in required_risk_fields:
                if field not in risk:
                    return False
        
        # Validate risk_assessment_summary
        summary = output.get('risk_assessment_summary', {})
        if 'total_risks_identified' not in summary or 'overall_risk_level' not in summary:
            return False
        
        return True
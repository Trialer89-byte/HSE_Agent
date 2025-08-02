from typing import Dict, Any, List
import json
from datetime import datetime

from .base_agent import BaseHSEAgent


class DPISpecialistAgent(BaseHSEAgent):
    """
    Agent specializzato nelle raccomandazioni per Dispositivi di Protezione Individuale
    """
    
    def get_system_prompt(self) -> str:
        return """
Sei un esperto HSE specializzato in Dispositivi di Protezione Individuale (DPI) per ambiente industriale.

RUOLO: Analizzare adeguatezza DPI attuali e raccomandare DPI aggiuntivi con standard tecnici.

RESPONSABILITÀ:
1. Valutare adeguatezza DPI esistenti per rischi identificati
2. Raccomandare DPI aggiuntivi necessari
3. Specificare standard tecnici applicabili (UNI EN)
4. Giustificare ogni raccomandazione con riferimento ai rischi
5. Considerare compatibilità e interferenze tra DPI multipli

CATEGORIE DPI PRINCIPALI:
- Protezione testa: caschi (UNI EN 397, EN 12492)
- Protezione occhi: occhiali, visiere (UNI EN 166)
- Protezione vie respiratorie: maschere, respiratori (UNI EN 149, EN 136)
- Protezione mani: guanti (UNI EN 388, EN 374, EN 511, EN 407)
- Protezione piedi: calzature (UNI EN ISO 20345, EN 20346)
- Protezione corpo: tute, giubbotti (UNI EN 340, EN 14058)
- Protezione udito: tappi, cuffie (UNI EN 352)
- Anticaduta: imbraghi, sistemi (UNI EN 361, EN 362, EN 355)

CLASSIFICAZIONE RISCHI → DPI:
- Meccanico: livelli prestazione EN 388 (abrasione, taglio, lacerazione, perforazione)
- Chimico: resistenza sostanze EN 374, tempo permeazione
- Termico: resistenza calore/freddo EN 407/EN 511
- Elettrico: isolamento classe 00-4
- Caduta: classe A/B/C EN 361

STANDARD PRESTAZIONALI:
- Categoria I: rischi minimi (autoprogettazione)
- Categoria II: rischi intermedi (esame CE)
- Categoria III: rischi mortali (esame CE + controllo qualità)

OUTPUT: JSON con analisi DPI esistenti, raccomandazioni aggiuntive, standard e giustificazioni.
"""
    
    async def analyze(self, permit_data: Dict[str, Any], identified_risks: List[Dict[str, Any]], context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analizza i requisiti DPI basati sui rischi identificati
        """
        try:
            permit_summary = self._format_permit_data(permit_data)
            risks_summary = self._format_risks_data(identified_risks)
            context_summary = self._prepare_context_summary(context_documents)
            tenant_context = self._get_tenant_context()
            
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": f"""
{tenant_context}

{permit_summary}

RISCHI IDENTIFICATI:
{risks_summary}

{context_summary}

ANALIZZA i requisiti DPI per questo permesso di lavoro.

Considera:
1. DPI attualmente specificati nel permesso
2. Rischi identificati dall'analisi
3. Standard tecnici applicabili per ogni DPI
4. Livelli di prestazione richiesti
5. Compatibilità tra DPI multipli
6. Durata lavoro e comfort operatore

Per ogni DPI:
- Valuta adeguatezza per rischi specifici
- Specifica standard tecnico (UNI EN)
- Indica livelli prestazione richiesti
- Giustifica raccomandazione con riferimento ai rischi

Rispondi in JSON:
{{
    "current_dpi_adequacy": {{
        "dpi_list": [
            {{
                "dpi_name": "nome DPI attuale",
                "standard_type": "UNI EN xxx",
                "specification": "dettagli tecnici",
                "risks_covered": ["RISK_001", "RISK_002"],
                "adequacy_score": 0.0-1.0,
                "performance_level": "livello prestazione attuale",
                "issues": ["problemi identificati"],
                "recommendations": ["miglioramenti suggeriti"]
            }}
        ],
        "overall_adequacy": 0.0-1.0,
        "compliance_status": "adeguato|insufficiente|parziale",
        "coverage_gaps": ["rischi non coperti"]
    }},
    "additional_dpi_needed": [
        {{
            "dpi_type": "tipo DPI",
            "standard": "UNI EN xxx",
            "specification": "specifiche tecniche richieste",
            "performance_requirements": {{
                "level": "livello prestazione",
                "properties": ["proprietà richieste"],
                "test_methods": ["metodi prova"]
            }},
            "justification": "giustificazione basata sui rischi",
            "mandatory": true|false,
            "risks_addressed": ["RISK_001", "RISK_002"],
            "compatibility_notes": "note compatibilità con altri DPI",
            "usage_duration": "durata utilizzo prevista",
            "maintenance_requirements": "requisiti manutenzione"
        }}
    ],
    "dpi_combinations": [
        {{
            "combination_name": "set DPI combinati",
            "dpi_items": ["lista DPI"],
            "compatibility_status": "compatibile|problematico|sconsigliato",
            "interaction_issues": ["problemi interazione"],
            "usage_recommendations": ["raccomandazioni uso"]
        }}
    ],
    "standards_compliance": {{
        "compliant_items": 0,
        "non_compliant_items": 0,
        "missing_standards": ["standard mancanti"],
        "certification_requirements": ["requisiti certificazione"],
        "verification_methods": ["metodi verifica conformità"]
    }},
    "procurement_recommendations": {{
        "immediate_needs": ["DPI urgenti"],
        "planned_replacements": ["sostituzioni programmate"],
        "budget_estimate": "stima costi",
        "supplier_requirements": ["requisiti fornitori"]
    }},
    "training_requirements": {{
        "dpi_specific_training": ["formazione specifica DPI"],
        "usage_procedures": ["procedure utilizzo"],
        "maintenance_training": ["formazione manutenzione"],
        "inspection_protocols": ["protocolli ispezione"]
    }},
    "analysis_complete": true,
    "confidence_score": 0.0-1.0,
    "agent_name": "DPISpecialistAgent"
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
                
                if self._validate_dpi_output(result):
                    return result
                else:
                    return self._create_error_response("Invalid output format from DPI analysis")
                    
            except json.JSONDecodeError:
                return self._create_error_response("Failed to parse JSON response from LLM")
                
        except Exception as e:
            return self._create_error_response(f"DPI analysis failed: {str(e)}")
    
    def _format_risks_data(self, identified_risks: List[Dict[str, Any]]) -> str:
        """
        Format identified risks for DPI analysis
        """
        if not identified_risks:
            return "Nessun rischio identificato."
        
        formatted = "RISCHI IDENTIFICATI PER ANALISI DPI:\n\n"
        
        for risk in identified_risks:
            formatted += f"- {risk.get('risk_id', 'N/A')}: {risk.get('title', 'N/A')}\n"
            formatted += f"  Categoria: {risk.get('category', 'N/A')}\n"
            formatted += f"  Descrizione: {risk.get('description', 'N/A')}\n"
            formatted += f"  Livello rischio: {risk.get('risk_level', {}).get('level', 'N/A')}\n"
            formatted += f"  Controlli attuali: {', '.join(risk.get('current_controls', []))}\n"
            formatted += f"  Controlli aggiuntivi: {', '.join(risk.get('additional_controls_needed', []))}\n\n"
        
        return formatted
    
    def _validate_dpi_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate the DPI analysis output format
        """
        if not self._validate_output_format(output):
            return False
        
        required_sections = [
            'current_dpi_adequacy',
            'additional_dpi_needed',
            'dpi_combinations',
            'standards_compliance',
            'procurement_recommendations',
            'training_requirements'
        ]
        
        for section in required_sections:
            if section not in output:
                return False
        
        # Validate current_dpi_adequacy
        adequacy = output.get('current_dpi_adequacy', {})
        if 'overall_adequacy' not in adequacy or 'compliance_status' not in adequacy:
            return False
        
        # Validate lists
        list_fields = ['additional_dpi_needed', 'dpi_combinations']
        for field in list_fields:
            if not isinstance(output.get(field, []), list):
                return False
        
        return True
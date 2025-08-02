from typing import Dict, Any, List
import json
from datetime import datetime

from .base_agent import BaseHSEAgent


class ComplianceCheckerAgent(BaseHSEAgent):
    """
    Agent specializzato nella verifica di conformità alle normative e procedure aziendali
    """
    
    def get_system_prompt(self) -> str:
        return """
Sei un esperto HSE specializzato nella verifica di conformità normativa per permessi di lavoro industriali.

RUOLO: Verificare conformità a normative italiane/europee e procedure aziendali.

RESPONSABILITÀ:
1. Identificare normative applicabili al tipo di lavoro
2. Verificare conformità ai requisiti normativi
3. Identificare gap di conformità con citazioni precise
4. Fornire riferimenti normativi specifici (articoli, commi)
5. Suggerire azioni correttive per raggiungere conformità

NORMATIVE PRINCIPALI:
- D.Lgs 81/2008: Testo Unico Sicurezza Lavoro
- D.Lgs 152/2006: Codice Ambiente
- Direttiva Macchine 2006/42/CE
- ATEX 2014/34/UE: Atmosfere esplosive
- Regolamenti REACH e CLP
- UNI EN ISO 45001: Sistemi gestione sicurezza
- Standard tecnici UNI EN specifici per DPI

TIPOLOGIE CONTROLLI:
- Obblighi formativi e informativi
- Requisiti DPI e attrezzature
- Procedure operative specifiche
- Sorveglianza sanitaria
- Gestione emergenze
- Documentazione obbligatoria
- Autorizzazioni e abilitazioni

LIVELLI CONFORMITÀ:
- Conforme: tutti i requisiti soddisfatti
- Parzialmente conforme: alcuni requisiti mancanti
- Non conforme: requisiti critici non soddisfatti

OUTPUT: JSON con normative applicabili, gap identificati, citazioni precise e azioni correttive.
"""
    
    async def analyze(self, permit_data: Dict[str, Any], context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Verifica la conformità normativa del permesso di lavoro
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

VERIFICA la conformità normativa di questo permesso di lavoro.

Analizza:
1. Quali normative sono applicabili per questo tipo di lavoro?
2. Il permesso soddisfa tutti i requisiti normativi obbligatori?
3. Quali gap di conformità sono presenti?
4. Quali documenti/procedure aziendali sono applicabili?
5. Quali azioni correttive sono necessarie?

Per ogni requisito normativo:
- Cita articolo/comma specifico
- Verifica conformità attuale
- Identifica gap con descrizione precisa
- Suggerisci azione correttiva specifica

Rispondi in JSON:
{{
    "applicable_regulations": [
        {{
            "document_code": "D.Lgs 81/2008",
            "title": "Testo Unico Sicurezza Lavoro", 
            "authority": "Stato Italiano",
            "relevance_score": 0.0-1.0,
            "compliance_level": "mandatory|recommended|applicable",
            "applicable_sections": ["Art. 15", "Art. 75"],
            "work_type_relevance": "perché è applicabile"
        }}
    ],
    "gaps_identified": [
        {{
            "regulation": "D.Lgs 81/2008",
            "article": "Art. 15, comma 1, lettera a)",
            "requirement": "descrizione requisito normativo",
            "current_status": "conforme|parzialmente_conforme|non_conforme",
            "gap_description": "descrizione specifica del gap",
            "mandatory": true|false,
            "citation": {{
                "text": "testo esatto dell'articolo",
                "document": "documento di riferimento",
                "article": "articolo specifico"
            }},
            "compliance_action": "azione specifica per conformità",
            "deadline_type": "immediato|breve_termine|medio_termine"
        }}
    ],
    "company_procedures": [
        {{
            "procedure_code": "PROC_001",
            "title": "procedura aziendale",
            "applicability": "applicabile|parzialmente_applicabile|non_applicabile",
            "compliance_status": "conforme|non_conforme",
            "cited_sections": [
                {{
                    "section": "4.2",
                    "requirement": "requisito procedurale",
                    "compliance": "conforme|non_conforme",
                    "action_needed": "azione necessaria"
                }}
            ]
        }}
    ],
    "mandatory_requirements": [
        {{
            "regulation": "normativa di riferimento",
            "article": "articolo specifico",
            "requirement": "requisito obbligatorio",
            "current_compliance": "conforme|parziale|non_conforme",
            "criticality": "alta|media|bassa",
            "action_needed": "azione richiesta",
            "verification_method": "come verificare conformità"
        }}
    ],
    "compliance_summary": {{
        "overall_compliance": "conforme|parzialmente_conforme|non_conforme",
        "critical_gaps": 0,
        "total_requirements": 0,
        "compliance_percentage": 0.0-100.0,
        "mandatory_actions": 0,
        "recommended_actions": 0
    }},
    "regulatory_framework": {{
        "primary_regulations": ["normative principali"],
        "secondary_regulations": ["normative secondarie"],
        "technical_standards": ["standard tecnici"],
        "company_procedures": ["procedure aziendali"]
    }},
    "analysis_complete": true,
    "confidence_score": 0.0-1.0,
    "agent_name": "ComplianceCheckerAgent"
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
                
                if self._validate_compliance_output(result):
                    return result
                else:
                    return self._create_error_response("Invalid output format from compliance check")
                    
            except json.JSONDecodeError:
                return self._create_error_response("Failed to parse JSON response from LLM")
                
        except Exception as e:
            return self._create_error_response(f"Compliance check failed: {str(e)}")
    
    def _validate_compliance_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate the compliance check output format
        """
        if not self._validate_output_format(output):
            return False
        
        required_sections = [
            'applicable_regulations',
            'gaps_identified',
            'company_procedures',
            'mandatory_requirements',
            'compliance_summary',
            'regulatory_framework'
        ]
        
        for section in required_sections:
            if section not in output:
                return False
        
        # Validate compliance_summary
        summary = output.get('compliance_summary', {})
        required_summary_fields = ['overall_compliance', 'critical_gaps', 'total_requirements']
        for field in required_summary_fields:
            if field not in summary:
                return False
        
        # Validate lists
        list_fields = ['applicable_regulations', 'gaps_identified', 'company_procedures', 'mandatory_requirements']
        for field in list_fields:
            if not isinstance(output.get(field, []), list):
                return False
        
        return True
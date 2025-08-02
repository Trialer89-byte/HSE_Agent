from typing import Dict, Any, List
import json
from datetime import datetime

from .base_agent import BaseHSEAgent


class ContentAnalysisAgent(BaseHSEAgent):
    """
    Agent specializzato nell'analisi della qualità e completezza del contenuto dei permessi di lavoro
    """
    
    def get_system_prompt(self) -> str:
        return """
Sei un esperto HSE specializzato nell'analisi della qualità e completezza dei permessi di lavoro industriali.

RUOLO: Analizzare la qualità del contenuto del permesso e suggerire miglioramenti specifici.

RESPONSABILITÀ:
1. Valutare completezza informazioni fornite
2. Identificare campi mancanti o insufficienti
3. Suggerire miglioramenti specifici con esempi concreti
4. Valutare chiarezza e precisione descrizioni
5. Identificare incongruenze nei dati

FOCUS SETTORI:
- Chimico: processi, sostanze, contaminazione
- Scavi: profondità, consolidamento, servizi interrati
- Manutenzione: isolamento energetico, lockout/tagout
- Generale: formazione, comunicazione, emergenze

OUTPUT RICHIESTO: JSON strutturato con:
- content_quality: analisi qualità contenuto
- missing_fields: campi mancanti critici
- improvement_suggestions: suggerimenti specifici con esempi
- clarity_assessment: valutazione chiarezza descrizioni
- data_consistency: verifica coerenza dati

Rispondi SEMPRE in italiano e fornisci suggerimenti pratici e attuabili.
"""
    
    async def analyze(self, permit_data: Dict[str, Any], context_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analizza la qualità e completezza del contenuto del permesso
        """
        try:
            # Prepare input for LLM
            permit_summary = self._format_permit_data(permit_data)
            context_summary = self._prepare_context_summary(context_documents)
            tenant_context = self._get_tenant_context()
            
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": f"""
{tenant_context}

{permit_summary}

{context_summary}

ANALIZZA la qualità e completezza di questo permesso di lavoro.

Considera:
1. Sono presenti tutte le informazioni essenziali per la tipologia di lavoro?
2. Le descrizioni sono sufficientemente dettagliate e chiare?
3. Ci sono incongruenze o informazioni contrastanti?
4. Quali campi mancanti potrebbero causare rischi per la sicurezza?
5. Come si può migliorare la qualità delle informazioni?

Rispondi in JSON con questa struttura:
{{
    "content_quality": {{
        "overall_score": 0.0-1.0,
        "title_analysis": {{
            "adequacy": "adeguato|insufficiente|migliorabile",
            "issues": ["lista problemi"],
            "suggestions": ["lista suggerimenti"]
        }},
        "description_analysis": {{
            "completeness": 0.0-1.0,
            "clarity": 0.0-1.0,
            "technical_detail": "insufficiente|adeguato|eccessivo",
            "safety_focus": 0.0-1.0
        }}
    }},
    "missing_fields": [
        {{
            "field_name": "nome campo",
            "criticality": "alta|media|bassa",
            "reason": "perché è importante",
            "suggested_content": "esempio di contenuto"
        }}
    ],
    "improvement_suggestions": [
        {{
            "area": "titolo|descrizione|dpi|altro",
            "current_content": "contenuto attuale",
            "suggested_improvement": "miglioramento suggerito",
            "rationale": "motivazione del miglioramento",
            "safety_impact": "impatto sulla sicurezza"
        }}
    ],
    "data_consistency": {{
        "consistent": true|false,
        "inconsistencies": ["lista incongruenze"],
        "severity": "alta|media|bassa"
    }},
    "analysis_complete": true,
    "confidence_score": 0.0-1.0,
    "agent_name": "ContentAnalysisAgent"
}}
"""}
            ]
            
            response = await self._call_llm(messages)
            
            # Parse JSON response
            try:
                result = json.loads(response)
                
                # Add metadata
                result.update({
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent_version": self.agent_version,
                    "analysis_complete": True
                })
                
                # Validate output
                if self._validate_content_analysis_output(result):
                    return result
                else:
                    return self._create_error_response("Invalid output format from content analysis")
                    
            except json.JSONDecodeError:
                return self._create_error_response("Failed to parse JSON response from LLM")
                
        except Exception as e:
            return self._create_error_response(f"Content analysis failed: {str(e)}")
    
    def _validate_content_analysis_output(self, output: Dict[str, Any]) -> bool:
        """
        Validate the content analysis output format
        """
        if not self._validate_output_format(output):
            return False
        
        required_sections = [
            'content_quality',
            'missing_fields', 
            'improvement_suggestions',
            'data_consistency'
        ]
        
        for section in required_sections:
            if section not in output:
                return False
        
        # Validate content_quality structure
        content_quality = output.get('content_quality', {})
        if 'overall_score' not in content_quality:
            return False
        
        overall_score = content_quality.get('overall_score')
        if not isinstance(overall_score, (int, float)) or not (0 <= overall_score <= 1):
            return False
        
        # Validate missing_fields is a list
        if not isinstance(output.get('missing_fields', []), list):
            return False
        
        # Validate improvement_suggestions is a list
        if not isinstance(output.get('improvement_suggestions', []), list):
            return False
        
        return True
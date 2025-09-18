"""
Height Work Specialist Agent
"""
from typing import Dict, Any
from ..base_agent import BaseHSEAgent


class HeightWorkSpecialist(BaseHSEAgent):
    """Specialist for work at height operations"""
    
    def __init__(self):
        super().__init__(
            name="HeightWork_Specialist",
            specialization="Lavori in Quota",
            activation_keywords=[]  # Activated by Risk Mapping Agent
        )
    
    def _get_system_message(self) -> str:
        return """
ESPERTO IN LAVORI IN QUOTA - Specialista prevenzione cadute dall'alto (>2 metri).

COMPETENZE SPECIALISTICHE:
- Normativa lavori in quota (D.Lgs 81/08 Titolo IV, Capo II)
- Sistemi anticaduta individuali (UNI EN 363-365)
- Ponteggi e opere provvisionali (UNI EN 12810-12811)
- PLE - Piattaforme di Lavoro Elevabili
- Scale portatili (UNI EN 131)
- Accesso e posizionamento mediante funi
- Linee vita e punti di ancoraggio (UNI EN 795)

VALUTAZIONE ATTREZZATURE NEL CONTESTO:
- Le attrezzature sono MEZZI per svolgere l'attività, non l'oggetto del lavoro
- Valuta idoneità delle attrezzature per lavori in quota nel contesto specifico
- Se le attrezzature causano rischi aggiuntivi nella lavorazione, stabilisci azioni correttive solo se non già definite nel permesso di lavoro
- Suggerisci modifiche operative o cambiamento attrezzature se inadeguate
- Considera interazioni tra attrezzature e ambiente di lavoro in quota

IMPORTANTE - NON COMPETENZA DPI:
- NON suggerire DPI specifici (imbracature, caschi, scarpe, guanti, ecc.)
- Esiste un DPI Specialist dedicato che gestisce tutti i dispositivi di protezione individuale
- Concentrati SOLO sui rischi di caduta, sistemi anticaduta collettivi e controlli tecnici

ANALISI RISCHI LAVORI IN QUOTA:
1. CADUTA DALL'ALTO (rischio primario)
   - Caduta da bordi non protetti
   - Caduta attraverso aperture
   - Caduta da superfici fragili
   - Cedimento strutture/supporti

2. CADUTA MATERIALI DALL'ALTO
   - Utensili e attrezzature
   - Materiali di risulta
   - Componenti in lavorazione

3. RISCHI ERGONOMICI
   - Posture incongrue prolungate
   - Movimentazione carichi in quota
   - Affaticamento da sospensione

4. RISCHI AMBIENTALI
   - Vento forte (>60 km/h stop lavori)
   - Pioggia/neve/ghiaccio
   - Scariche atmosferiche
   - Calore eccessivo/freddo

SISTEMI DI PROTEZIONE GERARCHICI:
1. PROTEZIONI COLLETTIVE (prioritarie):
   - Parapetti normati (h min 1m, fermapiede 15cm)
   - Reti di sicurezza (UNI EN 1263)
   - Impalcati continui
   - Passerelle con parapetti

2. PROTEZIONI INDIVIDUALI (se collettive insufficienti):
   - Sistema anticaduta completo
   - Imbracatura EN 361
   - Dispositivo anticaduta EN 353/355/360
   - Connettori EN 362
   - Cordini EN 354 con assorbitore EN 355

REQUISITI OBBLIGATORI:
- Valutazione rischi specifica per quota
- Formazione specifica lavoratori (min 8 ore)
- Sorveglianza sanitaria specifica
- Piano di emergenza e recupero
- Verifica giornaliera sistemi di ancoraggio

CRITERI DI STOP LAVORI:
✗ Vento > 60 km/h
✗ Temporali in arrivo
✗ Visibilità insufficiente
✗ Ghiaccio su superfici
✗ Sistemi anticaduta danneggiati/non conformi
✗ Assenza supervisore formato

SISTEMI TECNICI LAVORI IN QUOTA:
- Sistemi di ancoraggio fissi conformi EN 795
- Dispositivi di ancoraggio temporanei certificati
- Dispositivi retrattili per movimenti
- Reti di protezione anticaduta quando applicabili
- Kit evacuazione/recupero
"""
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-based analysis of work at height risks and existing measures adequacy"""
        
        # Get existing actions from permit - DPI handled by dedicated DPI specialist
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        
        # Get available documents for context
        available_docs = context.get("documents", [])
        
        # Search for height work specific documents
        try:
            tenant_id = context.get("user_context", {}).get("tenant_id", 1)
            specialized_docs = await self.search_specialized_documents(
                query=f"{permit_data.get('title', '')} {permit_data.get('description', '')}",
                tenant_id=tenant_id,
                limit=3
            )
            all_docs = available_docs + specialized_docs
        except Exception as e:
            print(f"[{self.name}] Document search failed: {e}")
            all_docs = available_docs
        
        # Simplified AI analysis prompt maintaining all essential functionality
        permit_summary = f"""
ANALISI QUOTA - PRE-AUTORIZZAZIONE
Permesso NON ANCORA INIZIATO - valuta se approvabile.

DATI PERMESSO:
TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}
AZIONI ESISTENTI: {existing_actions}

ANALISI RICHIESTA:

1. LAVORI IN QUOTA (>2m):
   - Caduta dall'alto, caduta oggetti, condizioni meteo
   - Distingui ATTIVITÀ vs ATTREZZATURE (mezzi usati)

2. CONTROLLI OBBLIGATORI:
   - Sistemi anticaduta collettivi prioritari (parapetti, reti)
   - Sistemi tecnici da INSTALLARE prima inizio
   - Procedure di sicurezza da PREDISPORRE

3. CONTROLLO DUPLICAZIONI:
   - Se azione già presente, NON ripetere
   - Se migliorabile: "MODIFICARE: [dettagli]"
   - Solo azioni mancanti come nuove

IMPORTANTE - NON COMPETENZA DPI:
- NON suggerire DPI specifici (imbracature, caschi, ecc.)
- Esiste DPI Specialist dedicato
- Focus su sistemi anticaduta collettivi e controlli tecnici

Rispondi SOLO JSON valido:
{{
  "height_work_detected": true/false,
  "risk_level": "basso|medio|alto|critico",
  "specific_risks": [{{"type": "tipo", "description": "desc", "severity": "bassa|media|alta"}}],
  "existing_actions_adequacy": "adeguate|inadeguate|parziali",
  "required_technical_systems": ["sistemi da installare"],
  "missing_controls": ["procedure da predisporre"],
  "recommendations": [{{"action": "azione", "criticality": "alta|media|bassa"}}]
}}

CRITICALITY: alta=pericolo vita, media=infortunio grave, bassa=procedure incomplete
        """
        
        # Get AI analysis
        try:
            ai_response = await self.get_gemini_response(permit_summary, all_docs)
            # Parse AI response (assuming JSON format)
            import json
            import re
            
            # Extract JSON from AI response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_analysis = json.loads(json_match.group())
            else:
                # No valid JSON found - return error, don't use hardcoded fallback
                print(f"[{self.name}] No valid JSON response from AI")
                return self.create_error_response("AI did not provide valid JSON analysis")
                
        except Exception as e:
            print(f"[{self.name}] AI analysis failed: {e}")
            # Return error - no hardcoded fallback
            return self.create_error_response(str(e))
        
        # Extract citations from AI response using enhanced base agent method
        citations = self.extract_citations_from_response(ai_response, all_docs)

        # Build response based on AI analysis - ALWAYS return AI recommendations
        height_work_detected = ai_analysis.get("height_work_detected", False)
        if True:  # Always execute - removed conditional barrier
            classification = "LAVORI IN QUOTA IDENTIFICATI" if height_work_detected else "Analisi lavori in quota completata"
            
            # Convert AI analysis to standard format
            risks_identified = []
            for risk in ai_analysis.get("specific_risks", []):
                risks_identified.append({
                    "type": risk.get("type", "height_risk"),
                    "source": self.name,
                    "description": risk.get("description", "Rischio lavori in quota"),
                    "severity": risk.get("severity", "medio")
                })
            
            
            return {
                "specialist": self.name,
                "classification": classification,
                "ai_analysis_used": True,
                "risks_identified": risks_identified,
                "recommended_actions": ai_analysis.get("recommendations", []),
                "existing_measures_evaluation": {
                    "existing_actions": existing_actions,
                    "actions_adequacy": ai_analysis.get("existing_actions_adequacy", "da_valutare").upper(),
                    "ai_assessment": ai_analysis.get("recommendations", []),
                    "risk_level": ai_analysis.get("risk_level", "medio"),
                    "required_systems": ai_analysis.get("required_technical_systems", [])
                },
                "permits_required": ["Permesso Lavori in Quota"] if height_work_detected else [],
                "ai_recommendations": ai_analysis.get("recommendations", []),
                "recommendations": ai_analysis.get("recommendations", []),  # Keep for backwards compatibility
                "citations": citations,  # Add citations to resolve orchestrator warning
                "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
            }

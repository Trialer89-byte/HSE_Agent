"""
Hot Work Specialist Agent - AI-powered hot work risk analysis
"""
from typing import Dict, Any, List
from ..base_agent import BaseHSEAgent


class HotWorkSpecialist(BaseHSEAgent):
    """AI-powered specialist for hot work operations (welding, cutting, brazing, etc.)"""

    def __init__(self):
        super().__init__(
            name="HotWork_Specialist",
            specialization="Lavori a Caldo",
            activation_keywords=[]  # Activated by Risk Mapping Agent
        )

    def _get_system_message(self) -> str:
        return """
ESPERTO LAVORI A CALDO - Specialista operazioni con fiamme libere, scintille, calore.

COMPETENZE SPECIALISTICHE:
- Hot Work Permits e autorizzazioni
- Prevenzione incendi e esplosioni in lavori a caldo
- Saldatura, taglio termico, brasatura
- Atmosfere esplosive e zone ATEX
- Fire Watch e sistemi rilevazione
- Sistemi spegnimento fissi/portatili
- Procedure emergenza incendio

TIPOLOGIE LAVORI A CALDO:
1. SALDATURA (arc welding, TIG, MIG, elettrodo)
2. TAGLIO TERMICO (ossitaglio, plasma, laser)
3. BRASATURA e saldatura dolce
4. OPERAZIONI CON FIAMMA LIBERA
5. ABRASIONE metalli (generazione scintille)
6. RISCALDAMENTO industriale

RISCHI PRIMARI LAVORI A CALDO:
1. INCENDIO/ESPLOSIONE:
   - Ignizione materiali combustibili
   - Atmosfere esplosive (vapori, gas, polveri)
   - Scintille proiettate fino 11 metri
   - Surriscaldamento superfici

2. INTOSSICAZIONE/ASFISSIA:
   - Fumi metallici (Zn, Pb, Cr, Ni)
   - Gas tossici (CO, NO2, ozono)
   - Consumo ossigeno
   - Vapori solventi/rivestimenti

3. USTIONI E RADIAZIONI:
   - Schizzi metallo fuso
   - Radiazioni UV/IR intense
   - Superfici surriscaldate
   - Contatto accidentale

4. ELETTRICI (saldatura):
   - Elettrocuzione
   - Campi magnetici
   - Interferenze elettroniche

CONTROLLI CRITICI HOT WORK:
✓ Hot Work Permit obbligatorio
✓ Fire Watch presente durante e 30min dopo
✓ Rimozione materiali combustibili 11m raggio
✓ Sistema antincendio funzionante
✓ Controllo atmosfera esplosiva
✓ Ventilazione adeguata/LEV
✓ Delimitazione area sicurezza

ATTREZZATURE TECNICHE LAVORI A CALDO:
- Sistemi di ventilazione localizzata (LEV)
- Rilevatori gas/vapori esplosivi
- Estintori specifici per tipo di combustibile
- Schermi protettivi per contenimento scintille

FIRE WATCH REQUIREMENTS:
- Formazione antincendio specifica
- Estintore portatile sempre disponibile
- Comunicazione diretta operatore
- Sorveglianza continua + 30min post lavori
- Autorità stop lavori immediato

CRITERI STOP LAVORI CALDI:
✗ Atmosfera esplosiva rilevata
✗ Materiali combustibili non rimossi
✗ Fire Watch assente
✗ Sistema antincendio non funzionante
✗ Ventilazione insufficiente
✗ Condizioni meteo avverse (vento forte)
"""

    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered hot work risk analysis"""

        # Get existing DPI and actions from permit
        existing_dpi = permit_data.get('dpi_required', [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])

        # Get available documents for context
        available_docs = context.get("documents", [])

        # Search for hot work specific documents
        try:
            tenant_id = context.get("user_context", {}).get("tenant_id", 1)
            hot_work_docs = await self.search_specialized_documents(
                query=f"lavori caldo saldatura taglio fire hot work {permit_data.get('title', '')} {permit_data.get('description', '')}",
                tenant_id=tenant_id,
                limit=3
            )
            all_docs = available_docs + hot_work_docs
        except Exception as e:
            print(f"[{self.name}] Document search failed: {e}")
            all_docs = available_docs

        # Create AI analysis prompt
        permit_summary = f"""
ANALISI PERMESSO DI LAVORO - FASE PRE-AUTORIZZAZIONE
IMPORTANTE: Stai analizzando un PERMESSO DI LAVORO che deve ancora essere approvato. Il lavoro NON È ANCORA INIZIATO.

PERMESSO DA ANALIZZARE - LAVORI A CALDO:
TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}

DISPOSITIVI DI PROTEZIONE PREVISTI NEL PERMESSO:
{existing_dpi if existing_dpi else 'Nessun dispositivo specificato'}

AZIONI MITIGAZIONE RISCHI PREVISTE:
{existing_actions if existing_actions else 'Nessuna azione specificata'}

CONTESTO: Il tuo ruolo è valutare SE questo permesso può essere APPROVATO e quali PREREQUISITI di sicurezza devono essere soddisfatti PRIMA dell'inizio del lavoro.

ANALIZZA I SEGUENTI ASPETTI:
1. Questo lavoro comporta operazioni a caldo (saldatura, taglio, fiamme)?
2. Quali sono i rischi specifici (incendio, esplosione, fumi, radiazioni)?
3. Le attuali azioni di mitigazione sono sufficienti?
4. Quali controlli critici devono essere PREDISPOSTI (Fire Watch, Hot Work Permit, ecc.)?
5. Quali procedure di emergenza devono essere PREDISPOSTE?

IMPORTANTE: Le tue raccomandazioni devono essere PREREQUISITI che devono essere soddisfatti PRIMA dell'approvazione del permesso.
NON suggerire di "sospendere" o "interrompere" il lavoro - piuttosto specifica cosa deve essere PREPARATO/PREDISPOSTO prima dell'inizio.

Fornisci risposta strutturata in JSON con:
- hot_work_detected: boolean
- work_type: tipo specifico operazione (saldatura/taglio/brasatura/altro)
- risk_level: "basso|medio|alto|critico"
- specific_risks: array di oggetti con type, description, severity
- missing_controls: array controlli di sicurezza mancanti
- fire_prevention_measures: array misure prevenzione incendi
- recommendations: array di oggetti con formato {{"action": "descrizione azione", "criticality": "alta|media|bassa"}} per prerequisiti da soddisfare prima dell'approvazione (max 8)

IMPORTANTE: Tutte le azioni devono essere implementate PRIMA dell'inizio lavori. La criticality indica il livello di rischio:
- "alta": Rischi con alta probabilità E alta gravità (incendio/esplosione imminente, atmosfere esplosive)
- "media": Rischi con media probabilità O media gravità (Hot Work senza adeguati controlli, Fire Watch)
- "bassa": Rischi con bassa probabilità E bassa gravità (ventilazione insufficiente, procedure incomplete)
        """

        # Get AI analysis
        try:
            ai_response = await self.get_gemini_response(permit_summary, all_docs)
            # Parse AI response
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

            # Extract citations from AI response for document traceability
            citations = self.extract_citations_from_response(ai_response, all_docs)

        except Exception as e:
            print(f"[{self.name}] AI analysis failed: {e}")
            # Return error - no hardcoded fallback
            return self.create_error_response(str(e))

        # Build response based on AI analysis - ALWAYS return AI recommendations
        hot_work_detected = ai_analysis.get("hot_work_detected", False)
        if True:  # Always execute - removed conditional barrier
            classification = "LAVORI A CALDO IDENTIFICATI" if hot_work_detected else "Analisi lavori a caldo completata"

            # Convert AI analysis to standard format
            risks_identified = []
            for risk in ai_analysis.get("specific_risks", []):
                risks_identified.append({
                    "type": risk.get("type", "hot_work_risk"),
                    "source": self.name,
                    "description": risk.get("description", "Rischio lavori a caldo"),
                    "severity": risk.get("severity", "alto")
                })

            # Use AI-generated recommendations directly - no hardcoded actions
            recommended_actions = ai_analysis.get("recommendations", [])


            return {
                "specialist": self.name,
                "classification": classification,
                "ai_analysis_used": True,
                "work_type": ai_analysis.get("work_type", "altro"),
                "risks_identified": risks_identified,
                "recommended_actions": recommended_actions,
                "existing_measures_evaluation": {
                    "existing_actions": existing_actions,
                    "actions_adequacy": ai_analysis.get("existing_actions_adequacy", "da_valutare").upper(),
                    "ai_assessment": ai_analysis.get("recommendations", []),
                    "risk_level": ai_analysis.get("risk_level", "alto"),
                    "work_type_detected": ai_analysis.get("work_type", "altro"),
                    "location_hazards": ai_analysis.get("location_hazards", []),
                    "missing_controls": ai_analysis.get("missing_controls", [])
                },
                "fire_prevention_measures": ai_analysis.get("fire_prevention_measures", []),
                "permits_required": ["Hot Work Permit"] if hot_work_detected else [],
                "citations": citations,  # Add proper citations for document traceability
                "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
            }
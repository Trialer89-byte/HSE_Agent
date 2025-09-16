"""
Confined Space Specialist Agent - AI-powered confined space analysis
"""
from typing import Dict, Any, List
from ..base_agent import BaseHSEAgent


class ConfinedSpaceSpecialist(BaseHSEAgent):
    """AI-powered specialist for confined space entry operations"""

    def __init__(self):
        super().__init__(
            name="ConfinedSpace_Specialist",
            specialization="Spazi Confinati",
            activation_keywords=[]  # Activated by Risk Mapping Agent
        )

    def _get_system_message(self) -> str:
        return """
ESPERTO IN SPAZI CONFINATI - Specialista DPR 177/2011 e procedure di accesso sicuro.

COMPETENZE SPECIALISTICHE:
- Classificazione spazi confinati (NIOSH/OSHA)
- Valutazione atmosfere pericolose (O2, LEL, H2S, CO)
- Procedure Entry Permit e LOTO
- Sistemi di ventilazione forzata
- Rescue plan e recupero emergenza
- Monitoraggio continuo parametri

IDENTIFICAZIONE SPAZIO CONFINATO:
1. Spazio NON progettato per presenza continua
2. Accessi limitati (entrata/uscita ristrette)
3. Ventilazione naturale insufficiente
4. Potenziale accumulo sostanze pericolose

PERICOLI TIPICI SPAZI CONFINATI:
- ASFISSIA: Carenza O2 (<19.5%) o eccesso CO2
- INTOSSICAZIONE: Gas tossici (H2S, CO, NH3, vapori)
- ESPLOSIONE: Accumulo gas/vapori infiammabili
- ANNEGAMENTO: Ingresso liquidi o materiali fluidi
- INTRAPPOLAMENTO: Configurazione interna complessa
- TEMPERATURE ESTREME: Stress termico

REQUISITI OBBLIGATORI (DPR 177/2011):
✓ Qualificazione specifica impresa (30% esperti)
✓ Formazione/addestramento tutto il personale
✓ Sistemi di monitoraggio e dispositivi emergenza
✓ Presenza continua supervisore esterno
✓ Piano di emergenza e recupero
✓ Confined Space Entry Permit

PROTOCOLLO ACCESSO SICURO:
1. PRE-ENTRY:
   - Isolamento energetico (LOTO)
   - Bonifica e ventilazione (min 30 min)
   - Test atmosfera (O2, LEL, tossici)
   - Permesso di lavoro specifico

2. DURANTE:
   - Monitoraggio continuo atmosfera
   - Ventilazione forzata continua
   - Sorvegliante esterno sempre presente
   - Comunicazione continua interno/esterno

3. EMERGENZA:
   - Team rescue addestrato disponibile
   - Equipaggiamento recupero pronto
   - Non-entry rescue preferito
   - Simulazioni periodiche obbligatorie

SISTEMI E ATTREZZATURE CRITICHE:
- Rilevatore multigas calibrato (O2, LEL, H2S, CO)
- Sistemi di ventilazione forzata ATEX
- Tripode/argano per recupero verticale
- Sistemi di comunicazione ATEX
- Illuminazione ATEX
- Sistemi di isolamento energetico (LOTO)
"""

    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered confined space risk analysis"""

        # Get available documents for context
        available_docs = context.get("documents", [])
        user_context = context.get('user_context', {})

        # Get existing actions from permit
        existing_actions = permit_data.get('risk_mitigation_actions', [])

        # Search for confined space-specific documents
        try:
            tenant_id = user_context.get("tenant_id", 1)
            confined_docs = await self.search_specialized_documents(
                query=f"spazi confinati DPR 177 confined space {permit_data.get('title', '')} {permit_data.get('description', '')}",
                tenant_id=tenant_id,
                limit=5
            )
            all_docs = available_docs + confined_docs
        except Exception as e:
            print(f"[{self.name}] Document search failed: {e}")
            all_docs = available_docs

        # Create comprehensive AI analysis prompt
        permit_summary = f"""
ANALISI PERMESSO DI LAVORO - FASE PRE-AUTORIZZAZIONE
IMPORTANTE: Stai analizzando un PERMESSO DI LAVORO che deve ancora essere approvato. Il lavoro NON È ANCORA INIZIATO.

PERMESSO DA ANALIZZARE - SPAZI CONFINATI:
TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}

CONTESTO: Il tuo ruolo è valutare SE questo permesso può essere APPROVATO e quali PREREQUISITI di sicurezza devono essere soddisfatti PRIMA dell'inizio del lavoro.

ANALIZZA COMPLETAMENTE I RISCHI SPAZI CONFINATI secondo:
- DPR 177/2011 (Qualificazione imprese spazi confinati)
- D.Lgs 81/08 art. 121 (Spazi confinati)
- Norma UNI 11448 (Sistemi gestione sicurezza)

1. IDENTIFICAZIONE SPAZIO CONFINATO:
   - Spazio non progettato per presenza continua umana
   - Accessi/uscite limitati o ristretti
   - Ventilazione naturale insufficiente
   - Potenziale accumulo sostanze pericolose
   - Esempi: serbatoi, cisterne, silos, fosse, pozzi, tunnel, condotti

2. VALUTAZIONE ATMOSFERA:
   - Carenza ossigeno (<19.5% O2)
   - Accumulo gas/vapori tossici (H2S, CO, NH3)
   - Atmosfere infiammabili/esplosive (LEL)
   - Eccesso CO2 (>0.5%)
   - Temperature estreme

3. ALTRI PERICOLI SPAZI CONFINATI:
   - Intrappolamento/annegamento
   - Configurazione interna complessa
   - Rischio seppellimento
   - Energie pericolose non controllate
   - Sostanze chimiche residue

4. PROCEDURE OBBLIGATORIE DPR 177/2011:
   - Confined Space Entry Permit
   - Isolamento energetico (LOTO)
   - Test atmosfera pre-ingresso
   - Ventilazione forzata continua
   - Supervisore esterno sempre presente
   - Piano di emergenza e recupero

5. SISTEMI TECNICI SPAZI CONFINATI:
   - Rilevatore multigas continuo
   - Sistemi di ventilazione forzata ATEX
   - Tripode/argano per recupero
   - Sistemi di comunicazione ATEX
   - Sistemi di isolamento energetico

IMPORTANTE: Le tue raccomandazioni devono essere PREREQUISITI che devono essere soddisfatti PRIMA dell'approvazione del permesso.
NON suggerire di "sospendere" o "interrompere" il lavoro - piuttosto specifica cosa deve essere PREPARATO/PREDISPOSTO prima dell'inizio.

Fornisci analisi strutturata in JSON con:
- confined_space_classification: classificazione spazio (confinato/non_confinato/dubbio)
- atmospheric_hazards: pericoli atmosferici identificati
- physical_hazards: pericoli fisici del sito
- required_procedures: procedure che devono essere PREDISPOSTE prima dell'inizio
- safety_equipment: attrezzature di sicurezza che devono essere FORNITE prima dell'inizio
- required_technical_systems: sistemi tecnici che devono essere INSTALLATI prima dell'inizio
- recommendations: array di oggetti con formato {{"action": "descrizione azione", "criticality": "alta|media|bassa"}} per prerequisiti da soddisfare prima dell'approvazione (max 8)

IMPORTANTE: Tutte le azioni devono essere implementate PRIMA dell'inizio lavori. La criticality indica il livello di rischio:
- "alta": Rischi con alta probabilità E alta gravità (asfissia immediata, atmosfere IDLH, intrappolamento)
- "media": Rischi con media probabilità O media gravità (atmosfere impoverite O2, gas tossici, procedure LOTO)
- "bassa": Rischi con bassa probabilità E bassa gravità (ventilazione insufficiente, comunicazioni limitate)
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
            print(f"[{self.name}] Analysis failed: {e}")
            # Use standardized error response with confined space specific fields
            error_response = self.create_error_response(e)
            error_response.update({
                "equipment_requirements": [],
                "training_requirements": [],
                "emergency_measures": [],
                "regulatory_compliance": "N/A - Analysis failed"
            })
            return error_response

        # Convert AI analysis to standard orchestrator format
        risks_identified = []

        # Process confined space classification
        classification = ai_analysis.get("confined_space_classification", "non_confinato")
        atmospheric_hazards = ai_analysis.get("atmospheric_hazards", [])
        physical_hazards = ai_analysis.get("physical_hazards", [])

        # Add atmospheric risks
        for hazard in atmospheric_hazards:
            if hazard and "Nessun" not in hazard and "nessun" not in hazard:
                severity = "critica" if any(term in hazard.lower() for term in ["critico", "asfissia", "intossicazione", "esplosion"]) else "alta"
                risks_identified.append({
                    "type": "confined_space_atmospheric",
                    "source": self.name,
                    "description": hazard,
                    "severity": severity
                })

        # Add physical risks
        for hazard in physical_hazards:
            if hazard and hazard != "Standard" and "Nessun" not in hazard:
                risks_identified.append({
                    "type": "confined_space_physical",
                    "source": self.name,
                    "description": f"Rischio fisico spazio confinato: {hazard}",
                    "severity": "alta"
                })

        # If no significant risks detected
        if not risks_identified:
            risks_identified.append({
                "type": "no_confined_space_risk",
                "source": self.name,
                "description": "Non classificato come spazio confinato secondo DPR 177/2011",
                "severity": "bassa"
            })

        # Determine if DPR 177/2011 applies
        is_confined_space = classification == "confinato" or any("confinato" in str(risk).lower() for risk in risks_identified)

        # Use AI-generated recommendations directly - no hardcoded actions
        recommended_actions = ai_analysis.get("recommendations", [])

        safety_equipment = ai_analysis.get("safety_equipment", [])

        return {
            "specialist": self.name,
            "classification": f"SPAZIO CONFINATO - DPR 177/2011 APPLICABILE" if is_confined_space else "NON SPAZIO CONFINATO",
            "ai_analysis_used": True,
            "risks_identified": risks_identified,
            "recommended_actions": recommended_actions,
            "existing_measures_evaluation": {
                "confined_space_classification": classification,
                "atmospheric_hazards_assessment": atmospheric_hazards,
                "physical_hazards_assessment": physical_hazards,
                "risk_coverage": "comprehensive" if len(risks_identified) > 1 else "basic",
                "ai_assessment": ai_analysis
            },
            "equipment_requirements": safety_equipment if is_confined_space else [],
            "permits_required": ["Confined Space Entry Permit", "LOTO Permit"] if is_confined_space else [],
            "training_requirements": [
                "Formazione specifica spazi confinati (16 ore minimo)",
                "Addestramento uso sistemi di protezione III categoria",
                "Training procedure emergenza e recupero"
            ] if is_confined_space else [],
            "emergency_measures": [
                "Rescue team addestrato on-site",
                "Piano evacuazione non-entry rescue",
                "Comunicazione diretta emergenza medica"
            ] if is_confined_space else [],
            "regulatory_compliance": "DPR 177/2011 - Qualificazione imprese OBBLIGATORIA" if is_confined_space else "Non applicabile",
            "citations": citations,  # Add citations for document traceability
            "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
        }
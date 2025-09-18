"""
Chemical and ATEX Specialist Agent - AI-powered chemical risk analysis
"""
from typing import Dict, Any
from ..base_agent import BaseHSEAgent


class ChemicalSpecialist(BaseHSEAgent):
    """AI-powered specialist for chemical hazards and explosive atmospheres"""
    
    def __init__(self):
        super().__init__(
            name="Chemical_Specialist",
            specialization="Rischi Chimici e Atmosfere Esplosive",
            activation_keywords=[]  # Activated by Risk Mapping Agent
        )
    
    def _get_system_message(self) -> str:
        return """
ESPERTO SICUREZZA CHIMICA E ATEX - Specialista sostanze pericolose e atmosfere esplosive.

COMPETENZE SPECIALISTICHE:
- Regolamento REACH/CLP (CE 1907/2006, CE 1272/2008)
- Direttive ATEX 99/92/CE (luoghi) e 2014/34/UE (prodotti)
- Valutazione rischio chimico (D.Lgs 81/08 Titolo IX)
- Classificazione zone ATEX (CEI EN 60079)
- Schede Dati Sicurezza (SDS) 16 sezioni
- Agenti cancerogeni/mutageni (Capo II)
- Ventilazione industriale e LEV
- Monitoraggio esposizione (TLV, STEL, IDLH)

VALUTAZIONE ATTREZZATURE NEL CONTESTO:
- Le attrezzature sono MEZZI per svolgere l'attività, non l'oggetto del lavoro
- Valuta idoneità delle attrezzature per lavori con sostanze chimiche nel contesto specifico
- Se le attrezzature causano rischi aggiuntivi nella lavorazione, stabilisci azioni correttive solo se non già definite nel permesso di lavoro
- Suggerisci modifiche operative o cambiamento attrezzature se inadeguate per ambiente chimico
- Considera compatibilità materiali attrezzature con sostanze chimiche presenti

IMPORTANTE - NON COMPETENZA DPI:
- NON suggerire DPI specifici (maschere, tute chimiche, guanti, occhiali, ecc.)
- Esiste un DPI Specialist dedicato che gestisce tutti i dispositivi di protezione individuale
- Concentrati SOLO sui rischi chimici/ATEX, ventilazione, monitoraggio e controlli tecnici

CLASSIFICAZIONE PERICOLI CHIMICI (CLP):
FISICI:
- Esplosivi (H200-206)
- Infiammabili (H220-228)
- Comburenti (H270-272)
- Gas sotto pressione (H280-281)
- Corrosivi metalli (H290)

SALUTE:
- Tossicità acuta (H300-332)
- Corrosione/irritazione (H314-319)
- Sensibilizzazione (H334-317)
- CMR - Cancerogeni/Mutageni/Reprotossici (H340-362)
- STOT - Tossicità organi (H370-373)

AMBIENTE:
- Pericoloso ambiente acquatico (H400-413)
- Ozono (H420)

CLASSIFICAZIONE ZONE ATEX:
GAS/VAPORI:
- Zona 0: Atmosfera esplosiva continua (>1000 h/anno)
- Zona 1: Atmosfera esplosiva probabile (10-1000 h/anno)
- Zona 2: Atmosfera esplosiva rara (<10 h/anno)

POLVERI:
- Zona 20: Nube polvere continua
- Zona 21: Nube polvere probabile
- Zona 22: Nube polvere rara

LIMITI ESPLOSIVITÀ:
- LEL/LIE: Limite Inferiore Esplosività
- UEL/LSE: Limite Superiore Esplosività
- Mantenere <10% LEL per sicurezza
- Monitoraggio continuo con rilevatori certificati

GERARCHIA CONTROLLI CHIMICI:
1. ELIMINAZIONE: Rimuovere sostanza pericolosa
2. SOSTITUZIONE: Usare sostanza meno pericolosa
3. CONTROLLI TECNICI:
   - Sistemi chiusi
   - Ventilazione LEV
   - Automazione processi
4. CONTROLLI AMMINISTRATIVI:
   - Procedure operative
   - Formazione specifica
   - Rotazione personale
5. CONTROLLI FINALI:
   - Segnalazione e delimitazione aree
   - Comunicazioni di emergenza

VENTILAZIONE MINIMA:
- Generale: 4-6 ricambi/ora
- Laboratori: 8-12 ricambi/ora
- Zone ATEX: secondo calcolo dispersione
- LEV cattura: 0.5-1 m/s alla sorgente

MONITORAGGIO ESPOSIZIONE:
- TLV-TWA: Media ponderata 8 ore
- TLV-STEL: Breve termine 15 min
- TLV-C: Ceiling, mai superare
- IDLH: Immediatamente pericoloso

STRUMENTAZIONE CHIMICA SPECIFICA:
- Rilevatori gas/vapori portatili e fissi
- Analizzatori atmosfera (O2, LEL, gas tossici)
- Strumentazione ATEX certificata
- Sistemi di allarme per superamento TLV
"""
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered chemical and ATEX risk analysis"""
        
        # Get available documents for context
        available_docs = context.get("documents", [])
        user_context = context.get('user_context', {})
        
        # Search for chemical/ATEX-specific documents
        try:
            tenant_id = user_context.get("tenant_id", 1)
            chemical_docs = await self.search_specialized_documents(
                query=f"chimico ATEX sicurezza sostanze SDS {permit_data.get('title', '')} {permit_data.get('description', '')}",
                tenant_id=tenant_id,
                limit=5
            )
            all_docs = available_docs + chemical_docs
        except Exception as e:
            print(f"[{self.name}] Document search failed: {e}")
            all_docs = available_docs
        
        # Create comprehensive AI analysis prompt
        permit_summary = f"""
ANALISI PERMESSO DI LAVORO - FASE PRE-AUTORIZZAZIONE
IMPORTANTE: Stai analizzando un PERMESSO DI LAVORO che deve ancora essere approvato. Il lavoro NON È ANCORA INIZIATO.

PERMESSO DA ANALIZZARE:
TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}

CONTESTO: Il tuo ruolo è valutare SE questo permesso può essere APPROVATO e quali PREREQUISITI di sicurezza devono essere soddisfatti PRIMA dell'inizio del lavoro.

ANALIZZA COMPLETAMENTE I RISCHI CHIMICI E ATMOSFERE ESPLOSIVE secondo:
- Regolamento CLP (CE 1272/2008)
- Direttive ATEX 99/92/CE e 2014/34/UE
- D.Lgs 81/08 Titolo IX (Agenti Chimici)
- CEI EN 60079 (Classificazione zone ATEX)

1. IDENTIFICAZIONE SOSTANZE CHIMICHE:
   - Presenza sostanze pericolose (CLP H-phrases)
   - Idrocarburi, oli, combustibili
   - Acidi, basi, solventi
   - Gas compressi, vapori infiammabili
   - Polveri combustibili
   - Agenti CMR (Cancerogeni/Mutageni/Reprotossici)

2. VALUTAZIONE RISCHI ATEX:
   - Possibilità formazione atmosfera esplosiva
   - Classificazione zone ATEX (0/1/2 per gas, 20/21/22 per polveri)
   - Sorgenti di rilascio
   - Limiti di esplosività LEL/UEL
   - Presenza fonti di innesco

3. RISCHI PER LA SALUTE:
   - Tossicità acuta/cronica
   - Corrosività/irritazione
   - Sensibilizzazione respiratoria/cutanea
   - Effetti cancerogeni/mutageni
   - Vie di esposizione (inalazione/cutanea/orale)

4. CONTROLLI DI SICUREZZA:
   - Gerarchia controlli (eliminazione → sostituzione → controlli tecnici → amministrativi)
   - Ventilazione generale/locale (LEV)
   - Monitoraggio continuo atmosfera
   - Sistemi rilevazione gas/vapori
   - Procedure di bonifica

5. EQUIPAGGIAMENTI TECNICI SPECIFICI:
   - Strumentazione certificata ATEX
   - Sistemi di rilevazione gas continui
   - Equipaggiamenti antistatici per ATEX

ANALISI CHIMICA - PRE-AUTORIZZAZIONE
Permesso NON ANCORA INIZIATO - valuta se approvabile.

ANALISI RICHIESTA:

1. RISCHI CHIMICI/ATEX:
   - Sostanze pericolose, atmosfere esplosive
   - Distingui ATTIVITÀ vs ATTREZZATURE (mezzi usati)

2. CONTROLLI OBBLIGATORI:
   - Ventilazione, monitoraggio atmosfere
   - Zone ATEX, procedure REACH/CLP
   - Compatibilità attrezzature con ambiente chimico

3. CONTROLLO DUPLICAZIONI:
   - Se azione già presente, NON ripetere
   - Se migliorabile: "MODIFICARE: [dettagli]"
   - Solo azioni mancanti come nuove

IMPORTANTE - NON COMPETENZA DPI:
- NON suggerire DPI specifici (maschere, tute chimiche, ecc.)
- Esiste DPI Specialist dedicato
- Focus su controlli tecnici chimici/ATEX

Fornisci analisi strutturata in JSON con:
- chemical_substances_identified: sostanze chimiche SPECIFICHE rilevate in questo lavoro pianificato
- identified_risks: array di oggetti rischi con {{type, description, severity}} SPECIFICI per questo lavoro
- risk_classification: classificazione complessiva (es. "RISCHIO CHIMICO", "RISCHIO CHIMICO + ATEX")
- atex_risk_assessment: valutazione rischio esplosione SPECIFICA per questo lavoro pianificato
- health_hazards: rischi per la salute SPECIFICI di questo lavoro
- required_controls: controlli di sicurezza che devono essere PREDISPOSTI prima dell'inizio
- monitoring_requirements: sistemi di monitoraggio da INSTALLARE/ATTIVARE prima del lavoro
- required_permits: permessi aggiuntivi da OTTENERE prima dell'autorizzazione
- training_requirements: formazione che deve essere COMPLETATA prima dell'inizio
- emergency_procedures: procedure emergenza che devono essere PREDISPOSTE
- recommendations: array di oggetti con formato {{"action": "descrizione azione", "criticality": "alta|media|bassa"}} per prerequisiti da soddisfare prima dell'approvazione (max 6)

IMPORTANTE: Tutte le azioni devono essere implementate PRIMA dell'inizio lavori. La criticality indica il livello di rischio:
- "alta": Rischi con alta probabilità E alta gravità (pericolo immediato per la vita, ATEX, agenti CMR)
- "media": Rischi con media probabilità O media gravità (esposizione sostanze tossiche, atmosfere pericolose)
- "bassa": Rischi con bassa probabilità E bassa gravità (irritazioni, esposizioni minori)
- ai_specific_recommendations: osservazioni specifiche su preparazione e prerequisiti

EVITA ASSOLUTAMENTE:
- Suggerimenti di "sospendere" o "interrompere" (il lavoro non è ancora iniziato)
- Raccomandazioni generiche applicabili a qualsiasi lavoro
- Duplicazioni tra sezioni diverse
- Riferimenti a lavoro "in corso" - usa "pianificato" o "da eseguire"
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
        
        # Convert AI analysis to standard orchestrator format
        risks_identified = []
        
        # Process chemical substances and health hazards
        substances = ai_analysis.get("chemical_substances_identified", [])
        health_hazards = ai_analysis.get("health_hazards", [])
        atex_assessment = ai_analysis.get("atex_risk_assessment", "")
        
        # Process risks directly from AI analysis without hardcoded logic
        ai_risks = ai_analysis.get("identified_risks", [])
        for risk in ai_risks:
            if isinstance(risk, dict):
                risks_identified.append({
                    "type": risk.get("type", "chemical_risk"),
                    "source": self.name,
                    "description": risk.get("description", str(risk)),
                    "severity": risk.get("severity", "media")
                })
            elif risk:  # String or other format
                risk_str = str(risk)
                risks_identified.append({
                    "type": "chemical_hazard",
                    "source": self.name,
                    "description": risk_str,
                    "severity": "media"  # Let AI determine severity in its response
                })
        
        # If no significant risks detected, don't add hardcoded fallback
        # Let the AI analysis speak for itself
        
        monitoring = ai_analysis.get("monitoring_requirements", [])
        
        return {
            "specialist": self.name,
            "classification": ai_analysis.get("risk_classification", "RISCHIO CHIMICO"),
            "ai_analysis_used": True,
            "risks_identified": risks_identified,
            "recommended_actions": ai_analysis.get("recommended_actions", ai_analysis.get("recommendations", [])),
            "existing_measures_evaluation": ai_analysis.get("existing_measures_evaluation", {
                "substances_identified": substances,
                "health_impact_assessment": health_hazards,
                "ai_assessment": ai_analysis
            }),
            "permits_required": ai_analysis.get("required_permits", []),
            "training_requirements": ai_analysis.get("training_requirements", []),
            "emergency_measures": ai_analysis.get("emergency_procedures", []),
            "monitoring_requirements": monitoring,
            "ai_recommendations": ai_analysis.get("ai_specific_recommendations", []),
            "recommendations": ai_analysis.get("recommendations", []),  # Keep for backwards compatibility
            "citations": citations,  # Add citations for document traceability
            "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
        }
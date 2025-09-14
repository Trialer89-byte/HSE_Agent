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
5. DPI (ultima risorsa):
   - Protezione vie respiratorie
   - Indumenti chimici
   - Protezione occhi/viso

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

DPI CHIMICI SPECIFICI:
- Respiratori: Filtri A (organici), B (inorganici), E (acidi), K (ammoniaca), P (polveri)
- SCBA per IDLH o O2<19.5%
- Tute chimiche: Tipo 1 (gas), 3 (liquidi), 4 (spray), 5 (polveri), 6 (schizzi)
- Guanti: Materiale secondo permeazione chimica
- Occhiali/visiera: Tenuta stagna per vapori
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
PERMESSO DI LAVORO - ANALISI RISCHI CHIMICI E ATEX:

TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}

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
   - Gerarchia controlli (eliminazione → sostituzione → controlli tecnici → DPI)
   - Ventilazione generale/locale (LEV)
   - Monitoraggio continuo atmosfera
   - Sistemi rilevazione gas/vapori
   - Procedure di bonifica

5. DPI CHIMICI/ATEX:
   - Protezione respiratoria (filtri A/B/E/K/P, SCBA)
   - Indumenti chimici (Tipo 1-6)
   - Guanti resistenti permeazione chimica
   - Equipaggiamenti antistatici per ATEX
   - Strumentazione certificata ATEX

Fornisci analisi strutturata in JSON con:
- chemical_substances_identified: sostanze chimiche rilevate
- atex_risk_assessment: valutazione rischio esplosione
- health_hazards: rischi per la salute
- required_controls: controlli di sicurezza necessari
- monitoring_requirements: monitoraggi richiesti
- required_dpi: DPI chimici/ATEX specifici
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
        
        # Add chemical risks
        for hazard in health_hazards:
            if hazard and "Nessun" not in hazard and "nessun" not in hazard:
                severity = "critica" if any(term in hazard.lower() for term in ["critico", "atex", "esplosiv", "cancerogen"]) else "alta"
                risks_identified.append({
                    "type": "chemical_hazard",
                    "source": self.name,
                    "description": hazard,
                    "severity": severity
                })
        
        # Add ATEX risk if detected
        if "alto" in atex_assessment.lower() or "critico" in atex_assessment.lower():
            risks_identified.append({
                "type": "atex_explosion",
                "source": self.name,
                "description": f"ATEX - Rischio esplosione: {atex_assessment}",
                "severity": "critica"
            })
        
        # If no significant risks detected
        if not risks_identified:
            risks_identified.append({
                "type": "no_chemical_risk",
                "source": self.name,
                "description": "Nessun rischio chimico significativo identificato",
                "severity": "bassa"
            })
        
        monitoring = ai_analysis.get("monitoring_requirements", [])
        
        # Determine if ATEX controls are needed
        is_atex_risk = any("atex" in str(risk).lower() or "esplosion" in str(risk).lower() for risk in risks_identified)
        
        return {
            "specialist": self.name,
            "classification": f"RISCHIO CHIMICO" + (" + ATMOSFERA ESPLOSIVA ATEX" if is_atex_risk else ""),
            "ai_analysis_used": True,
            "risks_identified": risks_identified,
            "recommended_actions": ai_analysis.get("recommended_actions", ai_analysis.get("recommendations", [])),
            "existing_measures_evaluation": {
                "substances_identified": substances,
                "atex_risk_level": atex_assessment,
                "health_impact_assessment": health_hazards,
                "risk_coverage": "comprehensive" if len(risks_identified) > 1 else "basic",
                "ai_assessment": ai_analysis
            },
            "permits_required": ["Permesso Esposizione Chimica"] + (["ATEX Work Permit"] if is_atex_risk else []),
            "training_requirements": [
                "Formazione rischio chimico specifico",
                "Lettura e comprensione SDS",
                "Uso corretto DPI chimici"
            ] + (["Formazione ATEX", "Procedure emergenza esplosione"] if is_atex_risk else []),
            "emergency_measures": [
                "Piano evacuazione immediata",
                "Procedure decontaminazione",
                "Comunicazione centro antiveleni"
            ] + (["Procedura emergenza esplosione", "Isolamento area 100m"] if is_atex_risk else []),
            "monitoring_requirements": monitoring,
            "ai_recommendations": [
                f"Sostanze identificate: {', '.join(substances[:3])}",
                f"Valutazione ATEX: {atex_assessment}",
                "Conformità Regolamento CLP e Direttive ATEX"
            ],
            "recommendations": ai_analysis.get("recommendations", []),  # Keep for backwards compatibility
            "citations": citations,  # Add citations for document traceability
            "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
        }
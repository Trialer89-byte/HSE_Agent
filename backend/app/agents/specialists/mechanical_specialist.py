"""
Mechanical Specialist Agent - Handles mechanical hazards
"""
from typing import Dict, Any, List
from ..base_agent import BaseHSEAgent


class MechanicalSpecialist(BaseHSEAgent):
    """Specialist agent for mechanical hazards and risks"""
    
    def __init__(self):
        super().__init__(
            name="Mechanical_Specialist",
            specialization="Rischi Meccanici e Energia Immagazzinata",
            activation_keywords=[]  # Activated by Risk Mapping Agent
        )
    
    def _get_system_message(self) -> str:
        return """
SPECIALIST MECCANICO - Esperto in rischi meccanici, energia immagazzinata e sicurezza macchinari.

COMPETENZE PRIMARIE:
1. SISTEMI IN PRESSIONE
   - Tubazioni, serbatoi, circuiti idraulici/pneumatici
   - Rischi da decompressione improvvisa
   - Energia potenziale accumulata
   - Procedure di depressurizzazione sicura

2. MACCHINE E ATTREZZATURE
   - Parti in movimento (rotanti, alternative, traslanti)
   - Punti di intrappolamento (nip points)
   - Rischi da avviamento imprevisto
   - LOTO (Lock Out Tag Out) procedures

3. ENERGIA MECCANICA RESIDUA
   - Molle caricate, contrappesi
   - Volani, sistemi inerziali
   - Fluidi in pressione residua
   - Sistemi gravitazionali

4. RISCHI DA SCHIACCIAMENTO/TAGLIO
   - Utensili manuali e pneumatici
   - Lamiere, strutture pesanti
   - Rischi da caduta oggetti
   - Manipolazione carichi pesanti

METODOLOGIA VALUTAZIONE:
1. Identificare tutte le fonti di energia meccanica
2. Valutare energia potenziale/cinetica coinvolta
3. Determinare percorsi di rilascio energia
4. Identificare punti di esposizione operatori
5. Verificare sistemi di protezione esistenti
6. Proporre misure di controllo gerarchiche

FOCUS SPECIFICO SU:
- Isolamento energie pericolose
- Procedure di messa in sicurezza
- DPI appropriati per rischi meccanici
- Permessi di lavoro su sistemi energizzati
- Verifica sistemi di protezione collettiva

OUTPUT RICHIESTO:
Analisi dettagliata dei rischi meccanici con:
- Inventario fonti energia meccanica
- Valutazione magnitudo rischi
- Procedure isolamento/LOTO necessarie
- DPI specifici per protezione meccanica
- Controlli ingegneristici necessari
- Formazione/addestramento richiesto
"""
    
    def should_activate(self, risk_classification: Dict[str, Any]) -> bool:
        """Determine if mechanical specialist should be activated"""
        
        # Check for mechanical work indicators
        detected_risks = risk_classification.get("detected_risks", {})
        
        # Direct mechanical risk detection
        if "mechanical" in detected_risks:
            return True
            
        # Mechanical work type
        work_type = risk_classification.get("work_type", "").lower()
        if "meccanico" in work_type or "mechanical" in work_type:
            return True
            
        # Pressurized systems indicators
        high_risk_terms = ["pressure", "pressione", "tubo", "pipe", "serbatoio", "tank", "compressor"]
        activity_text = str(risk_classification).lower()
        
        if any(term in activity_text for term in high_risk_terms):
            return True
            
        return False
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered mechanical hazards analysis"""
        
        # Get existing DPI and actions from permit
        existing_dpi = permit_data.get('dpi_required', [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        
        # Get available documents for context
        available_docs = context.get("documents", [])
        
        # Search for mechanical safety documents
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
        
        # Create comprehensive AI analysis prompt
        permit_summary = f"""
PERMESSO DI LAVORO - ANALISI SICUREZZA MECCANICA:

TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}

DPI ATTUALMENTE PREVISTI:
{existing_dpi if existing_dpi else 'Nessun DPI specificato'}

AZIONI MITIGAZIONE RISCHI ATTUALI:
{existing_actions if existing_actions else 'Nessuna azione specificata'}

ANALIZZA COMPLETAMENTE I RISCHI MECCANICI:

1. IDENTIFICAZIONE RISCHI MECCANICI:
   - Schiacciamento/intrappolamento
   - Taglio/perforazione/abrasione  
   - Proiezione materiali/schegge
   - Caduta oggetti dall'alto
   - Urti/colpi/impatti
   - Vibrazioni hand-arm e corpo intero
   - Rumore >85 dB(A)

2. FONTI DI ENERGIA:
   - Energia cinetica (rotazione, movimento)
   - Energia potenziale (molle, contrappesi)
   - Pressione fluidi (idraulica, pneumatica, vapore)
   - Energia elettrica su sistemi meccanici
   - Energia termica (attrito, compressione)

3. ATTREZZATURE E MACCHINARI:
   - PLE/piattaforme elevabili
   - Gru/sollevatori/paranchi
   - Utensili elettrici/pneumatici
   - Sistemi in pressione
   - Parti rotanti/nastri trasportatori
   - Presse/cesoie/macchine utensili

4. VALUTAZIONE MISURE ESISTENTI:
   - Adeguatezza DPI attuali per rischi meccanici identificati
   - Completezza procedure di isolamento energia meccanica (non elettrica)
   - Necessità procedure LOTO specifiche per sistemi meccanici/idraulici/pneumatici
   - Conformità alle normative D.Lgs 81/08

   IMPORTANTE: Concentrati SOLO su sistemi meccanici. Per lavori elettrici, lascia le procedure LOTO elettriche allo specialist elettrico.

5. RACCOMANDAZIONI SPECIFICHE:
   - DPI mancanti con normative EN specifiche
   - Controlli tecnici di sicurezza per sistemi meccanici
   - Procedure operative sicure per macchinari/attrezzature
   - Formazione/addestramento per uso attrezzature meccaniche
   - Attrezzature ausiliarie per sicurezza meccanica

   REGOLA ANTI-DUPLICAZIONE: Se il work_type è "elettrico" o la descrizione contiene "elettrico/elettrica",
   NON raccomandare procedure LOTO generiche. Concentrati solo su aspetti meccanici complementari.

Fornisci risposta strutturata in JSON con:
- mechanical_risks: array di rischi identificati con severity (bassa/media/alta/critica)
- energy_sources: fonti energetiche presenti e metodi isolamento
- existing_measures_adequacy: valutazione misure attuali (adeguate/inadeguate/parziali)
- missing_dpi: array DPI mancanti con standard EN
- control_measures: controlli tecnici/procedurali necessari
- intelligent_recommendations: array di oggetti con formato {{"action": "descrizione azione", "criticality": "alta|media|bassa"}} per mitigare i rischi identificati (max 10)
- loto_required: boolean se necessaria procedura LOTO
- training_needs: formazione specifica richiesta
- risk_level: livello rischio complessivo (basso/medio/alto/critico)

IMPORTANTE: Evita raccomandazioni duplicate. Non ripetere la stessa azione in campi diversi.

IMPORTANTE: Il campo 'intelligent_recommendations' deve contenere azioni specifiche e contestuali basate sui documenti aziendali e sui rischi identificati. Non fornire raccomandazioni generiche ma azioni concrete per questo specifico lavoro.

IMPORTANTE: Tutte le azioni devono essere implementate PRIMA dell'inizio lavori. La criticality indica il livello di rischio:
- "alta": Rischi con alta probabilità E alta gravità (schiacciamento fatale, energia immagazzinata critica, LOTO mancante)
- "media": Rischi con media probabilità O media gravità (sistemi in pressione, parti rotanti, energia meccanica)
- "bassa": Rischi con bassa probabilità E bassa gravità (superfici taglienti, vibrazioni, procedure incomplete)
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
                # Fallback parsing if no JSON found
                ai_analysis = {
                    "mechanical_risks": [{"type": "generic_mechanical", "description": "Rischi meccanici da valutare", "severity": "media"}],
                    "energy_sources": [],
                    "existing_measures_adequacy": "inadeguate",
                    "missing_dpi": ["Guanti meccanici EN 388", "Scarpe antinfortunistiche S3"],
                    "loto_required": False,
                    "training_needs": ["Formazione uso attrezzature"],
                    "risk_level": "medio"
                }

            # Extract citations from AI response for document traceability
            citations = self.extract_citations_from_response(ai_response, all_docs)

        except Exception as e:
            print(f"[{self.name}] Analysis failed: {e}")
            # Use standardized error response
            return self.create_error_response(e)
        
        # Convert AI analysis to standard orchestrator format
        risks_identified = []
        for risk in ai_analysis.get("mechanical_risks", []):
            risks_identified.append({
                "type": risk.get("type", "mechanical_risk"),
                "source": self.name,
                "description": risk.get("description", "Rischio meccanico"),
                "severity": risk.get("severity", "media")
            })
        
        # Use AI-generated recommendations with criticality
        recommended_actions = ai_analysis.get("intelligent_recommendations", [])
        
        
        return {
            "specialist": self.name,
            "classification": f"RISCHI MECCANICI - Livello: {str(ai_analysis.get('risk_level', 'medio')).upper()}",
            "ai_analysis_used": True,
            "risks_identified": risks_identified,
            "recommended_actions": recommended_actions,
            "existing_measures_evaluation": {
                "existing_dpi": existing_dpi,
                "existing_actions": existing_actions,
                "dpi_adequacy": str(ai_analysis.get("existing_measures_adequacy", "da_valutare")).upper(),
                "actions_adequacy": str(ai_analysis.get("existing_measures_adequacy", "da_valutare")).upper(),
                "risk_level": ai_analysis.get("risk_level", "medio"),
                "loto_required": ai_analysis.get("loto_required", False)
            },
            "permits_required": ["Permesso Lavori Meccanici"] if ai_analysis.get("risk_level") in ["alto", "critico"] else [],
            "citations": citations,  # Add citations for document traceability
            "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
        }
    

    
    
    
    
    
    
    
    
    
    
    

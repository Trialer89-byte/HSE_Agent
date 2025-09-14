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
   - Completezza procedure di isolamento energia
   - Necessità procedura LOTO (Lock-Out Tag-Out)
   - Conformità alle normative D.Lgs 81/08

5. RACCOMANDAZIONI SPECIFICHE:
   - DPI mancanti con normative EN specifiche
   - Controlli tecnici di sicurezza
   - Procedure operative sicure
   - Formazione/addestramento necessari
   - Attrezzature ausiliarie richieste

Fornisci risposta strutturata in JSON con:
- mechanical_risks: array di rischi identificati con severity (bassa/media/alta/critica)
- energy_sources: fonti energetiche presenti e metodi isolamento
- existing_measures_adequacy: valutazione misure attuali (adeguate/inadeguate/parziali)
- missing_dpi: array DPI mancanti con standard EN
- control_measures: controlli tecnici/procedurali necessari
- intelligent_recommendations: array di azioni specifiche per mitigare i rischi identificati (max 10)
- loto_required: boolean se necessaria procedura LOTO
- training_needs: formazione specifica richiesta
- risk_level: livello rischio complessivo (basso/medio/alto/critico)

IMPORTANTE: Il campo 'intelligent_recommendations' deve contenere azioni specifiche e contestuali basate sui documenti aziendali e sui rischi identificati. Non fornire raccomandazioni generiche ma azioni concrete per questo specifico lavoro.
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
        
        # Use ONLY AI-generated recommendations - NO hardcoding allowed
        recommended_actions = []

        # Extract AI recommendations from different possible fields
        if "intelligent_recommendations" in ai_analysis:
            recommended_actions = ai_analysis["intelligent_recommendations"]
        elif "safety_procedures" in ai_analysis:
            recommended_actions = ai_analysis["safety_procedures"]
        elif "recommended_actions" in ai_analysis:
            recommended_actions = ai_analysis["recommended_actions"]

        # Ensure we have a list of strings/dicts, limit to 10 max
        if not isinstance(recommended_actions, list):
            recommended_actions = []
        recommended_actions = recommended_actions[:10]
        
        
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
    
    def _analyze_and_recommend_actions(
        self, 
        existing_actions: List[str], 
        ai_suggested_measures: List[str],
        loto_required: bool,
        risk_level: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze existing actions and provide consolidated recommendations by criticality
        Limited to max 10 actions prioritized by risk mitigation importance
        """
        recommendations = []
        
        # Critical actions (must be implemented)
        critical_actions = []
        if loto_required:
            critical_actions.extend([
                "Implementare procedura LOTO (Lock Out Tag Out) obbligatoria",
                "Verificare isolamento completo di tutte le fonti energia",
                "Utilizzare lucchetti e cartellini di segnalazione personali"
            ])
        
        if risk_level in ["alto", "critico"]:
            critical_actions.append("Presenza obbligatoria di personale qualificato")
            critical_actions.append("Delimitazione area di lavoro con segnaletica")
        
        # High priority actions
        high_priority_actions = []
        for measure in ai_suggested_measures[:3]:  # Top 3 AI suggestions
            if measure not in critical_actions:
                high_priority_actions.append(measure)
        
        # Medium priority actions (improvements to existing measures)
        medium_priority_actions = []
        if existing_actions:
            medium_priority_actions.append("Verifica adeguatezza delle misure esistenti")
            medium_priority_actions.append("Aggiornamento procedure operative specifiche")
        else:
            medium_priority_actions.extend([
                "Sviluppo di procedure operative standard",
                "Formazione specifica per operatori"
            ])
        
        # Build prioritized recommendations
        action_id = 1
        
        # Add critical actions
        for action in critical_actions[:4]:  # Max 4 critical
            recommendations.append({
                "id": action_id,
                "action": action,
                "criticality": "critica",
                "type": "safety_control"
            })
            action_id += 1
        
        # Add high priority actions  
        for action in high_priority_actions[:3]:  # Max 3 high
            recommendations.append({
                "id": action_id,
                "action": action,
                "criticality": "alta",
                "type": "risk_mitigation"
            })
            action_id += 1
            
        # Add medium priority actions
        for action in medium_priority_actions[:3]:  # Max 3 medium
            recommendations.append({
                "id": action_id,
                "action": action,
                "criticality": "media",
                "type": "improvement"
            })
            action_id += 1
            
        # Limit to maximum 10 total actions
        return recommendations[:10]

    def _identify_mechanical_hazards(self, text: str, permit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify specific mechanical hazards"""
        hazards = []
        text_lower = text.lower()
        
        # Pressurized systems
        if any(term in text_lower for term in ["tubo", "pipe", "pressione", "pressure", "pneumatic", "hydraulic"]):
            hazards.append({
                "type": "pressurized_system",
                "description": "Sistema in pressione - rischio decompressione/schizzi",
                "severity": "alta",
                "likelihood": "media",
                "energy_type": "pressure"
            })
        
        # Cutting/welding on pressurized lines
        if any(cut in text_lower for cut in ["taglio", "cut", "sald", "weld"]) and any(pipe in text_lower for pipe in ["tubo", "pipe"]):
            hazards.append({
                "type": "pressurized_cutting",
                "description": "Taglio su tubazioni - rischio esplosione/schizzi fluidi",
                "severity": "critica",
                "likelihood": "alta", 
                "energy_type": "pressure + thermal"
            })
        
        # Heavy lifting/manipulation
        if any(term in text_lower for term in ["rimozione", "removal", "installazione", "installation", "pesante", "heavy"]):
            hazards.append({
                "type": "heavy_lifting",
                "description": "Movimentazione carichi pesanti - rischio schiacciamento",
                "severity": "alta",
                "likelihood": "media",
                "energy_type": "gravitational"
            })
        
        # Rotating equipment
        if any(term in text_lower for term in ["rotante", "rotating", "pompa", "pump", "ventilatore", "fan", "motor"]):
            hazards.append({
                "type": "rotating_equipment",
                "description": "Apparecchiature rotanti - rischio intrappolamento",
                "severity": "critica",
                "likelihood": "bassa",
                "energy_type": "kinetic"
            })
        
        return hazards
    
    def _assess_energy_sources(self, text: str, permit_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Assess mechanical energy sources present"""
        energy_sources = []
        text_lower = text.lower()
        
        # Pressure energy
        if any(term in text_lower for term in ["pressione", "pressure", "bar", "psi", "compressed"]):
            energy_sources.append({
                "type": "pressure",
                "source": "Sistema pressurizzato",
                "magnitude": "alta" if any(x in text_lower for x in ["alta", "high", "elevata"]) else "media",
                "isolation_method": "Depressurizzazione e bloccaggio valvole",
                "verification": "Manometro a zero, spurgo completo"
            })
        
        # Stored mechanical energy
        if any(term in text_lower for term in ["molla", "spring", "contrappeso", "counterweight"]):
            energy_sources.append({
                "type": "stored_mechanical",
                "source": "Energia meccanica immagazzinata",
                "magnitude": "media",
                "isolation_method": "Rilascio controllato energia",
                "verification": "Ispezione visiva posizione riposo"
            })
        
        # Kinetic energy
        if any(term in text_lower for term in ["rotante", "rotating", "belt", "cinghia", "volano", "flywheel"]):
            energy_sources.append({
                "type": "kinetic", 
                "source": "Energia cinetica parti in movimento",
                "magnitude": "alta",
                "isolation_method": "Arresto completo + blocco meccanico",
                "verification": "Conferma arresto visivo + tentativo avvio"
            })
        
        return energy_sources
    
    def _generate_control_measures(self, hazards: List[Dict], energy_sources: List[Dict]) -> List[str]:
        """Generate mechanical risk control measures"""
        measures = []
        
        # Standard mechanical controls
        measures.extend([
            "Implementare procedura LOTO (Lock Out Tag Out)",
            "Verificare isolamento completo fonti energia",
            "Utilizzare protezioni fisiche (barriere, schermi)",
            "Mantenere vie di fuga libere e segnalate"
        ])
        
        # Pressure-specific controls
        if any(h.get("type") == "pressurized_system" for h in hazards):
            measures.extend([
                "Depressurizzare completamente il sistema prima dell'intervento",
                "Installare bloccaggi fisici su valvole di isolamento",
                "Utilizzare schermature contro schizzi di fluidi",
                "Predisporre kit assorbimento perdite"
            ])
        
        # Cutting on pressurized lines
        if any(h.get("type") == "pressurized_cutting" for h in hazards):
            measures.extend([
                "OBBLIGATORIO: Verifica pressione zero con manometro",
                "Eseguire spurgo completo linea prima del taglio",
                "Utilizzare schermature anti-schizzi rinforzate",
                "Predisporre equipaggiamenti emergenza (doccia, lavaocchi)"
            ])
        
        return measures
    
    def _determine_mechanical_dpi(self, hazards: List[Dict]) -> List[Dict[str, Any]]:
        """Determine mechanical-specific DPI requirements"""
        dpi_requirements = []
        
        # Standard mechanical DPI
        dpi_requirements.extend([
            {
                "type": "Guanti meccanici",
                "standard": "EN 388 (4X43X)",
                "description": "Protezione da abrasioni, tagli, perforazioni",
                "mandatory": True
            },
            {
                "type": "Scarpe antinfortunistiche",
                "standard": "EN ISO 20345 S3",
                "description": "Protezione da schiacciamento, perforazione",
                "mandatory": True
            }
        ])
        
        # Pressure-specific DPI
        if any(h.get("energy_type") and "pressure" in h.get("energy_type") for h in hazards):
            dpi_requirements.extend([
                {
                    "type": "Occhiali protezione",
                    "standard": "EN 166 (schizzi liquidi)",
                    "description": "Protezione da schizzi fluidi in pressione",
                    "mandatory": True
                },
                {
                    "type": "Indumenti chimico-resistenti",
                    "standard": "EN 14605 Type 4",
                    "description": "Protezione da schizzi fluidi pericolosi",
                    "mandatory": True
                }
            ])
        
        return dpi_requirements
    
    def _generate_loto_requirements(self, energy_sources: List[Dict]) -> Dict[str, Any]:
        """Generate Lock Out Tag Out requirements"""
        if not energy_sources:
            return {"required": False}
        
        return {
            "required": True,
            "procedure": "Procedura LOTO obbligatoria",
            "steps": [
                "1. Identificare tutte le fonti di energia",
                "2. Notificare personale interessato",
                "3. Arrestare apparecchiature in sicurezza",
                "4. Isolare fonti energia (valvole, interruttori)",
                "5. Applicare lucchetti e cartellini personali",
                "6. Rilasciare energia residua immagazzinata",
                "7. Verificare isolamento efficace",
                "8. Mantenere controllo esclusivo chiavi"
            ],
            "equipment_needed": [
                "Lucchetti di sicurezza personali",
                "Cartellini di avvertimento",
                "Dispositivi di bloccaggio valvole",
                "Strumenti verifica isolamento"
            ],
            "authorization_required": "Supervisore qualificato LOTO"
        }
    
    def _generate_isolation_procedures(self, energy_sources: List[Dict]) -> List[str]:
        """Generate specific isolation procedures"""
        procedures = []
        
        for source in energy_sources:
            if source["type"] == "pressure":
                procedures.append(f"Pressione: {source['isolation_method']} - Verifica: {source['verification']}")
            elif source["type"] == "kinetic":
                procedures.append(f"Cinetica: {source['isolation_method']} - Verifica: {source['verification']}")
            elif source["type"] == "stored_mechanical":
                procedures.append(f"Meccanica: {source['isolation_method']} - Verifica: {source['verification']}")
        
        return procedures
    
    def _identify_specialized_equipment(self, hazards: List[Dict]) -> List[str]:
        """Identify specialized equipment needed"""
        equipment = []
        
        if any(h.get("type") == "pressurized_system" for h in hazards):
            equipment.extend([
                "Manometri di verifica pressione",
                "Kit spurgo e drenaggio",
                "Schermature mobili anti-schizzi"
            ])
        
        if any(h.get("type") == "heavy_lifting" for h in hazards):
            equipment.extend([
                "Apparecchi di sollevamento certificati",
                "Imbracature di sicurezza",
                "Cunei e bloccaggi"
            ])
        
        return equipment
    
    def _generate_training_requirements(self, hazards: List[Dict]) -> List[str]:
        """Generate training requirements"""
        training = ["Formazione base rischi meccanici"]
        
        if any(h.get("energy_type") and "pressure" in h.get("energy_type") for h in hazards):
            training.append("Addestramento sistemi in pressione")
        
        training.extend([
            "Procedura LOTO (Lock Out Tag Out)",
            "Uso DPI specifici per rischi meccanici",
            "Procedure di emergenza per rilascio energia"
        ])
        
        return training
    
    def _identify_required_permits(self, hazards: List[Dict], energy_sources: List[Dict]) -> List[str]:
        """Identify additional permits required"""
        permits = []
        
        if energy_sources:
            permits.append("Permit per lavori su sistemi energizzati")
        
        if any(h.get("severity") == "critica" for h in hazards):
            permits.append("Autorizzazione supervisore per rischi critici")
        
        return permits
    
    def _define_inspection_points(self, hazards: List[Dict]) -> List[str]:
        """Define critical inspection points"""
        return [
            "Verifica efficacia isolamento energie",
            "Controllo integrità dispositivi protezione",
            "Ispezione attrezzature sollevamento",
            "Verifica competenza operatori",
            "Controllo procedure di emergenza"
        ]
    
    def _generate_emergency_procedures(self, hazards: List[Dict]) -> List[str]:
        """Generate emergency procedures"""
        procedures = [
            "Procedure arresto di emergenza",
            "Protocolli primo soccorso per traumi meccanici"
        ]
        
        if any("pressure" in h.get("energy_type", "") for h in hazards):
            procedures.extend([
                "Procedure emergenza per rilascio fluidi",
                "Protocolli decontaminazione",
                "Attivazione docce di emergenza"
            ])
        
        return procedures
    
    def _calculate_mechanical_risk(self, hazards: List[Dict], energy_sources: List[Dict]) -> str:
        """Calculate overall mechanical risk level"""
        
        if any(h.get("severity") == "critica" for h in hazards):
            return "CRITICO"
        elif len(energy_sources) > 2:
            return "ALTO - Multiple energy sources"
        elif any(h.get("severity") == "alta" for h in hazards):
            return "ALTO"
        else:
            return "MEDIO"
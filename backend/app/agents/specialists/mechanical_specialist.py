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
            activation_keywords=["mechanical", "meccanico", "pressure", "pressione", "rotating", "rotante", "pinch", "crush"]
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
        """Analyze mechanical hazards and risks"""
        
        # Combine text for analysis
        full_text = f"""
        {permit_data.get('title', '')} {permit_data.get('description', '')} 
        {permit_data.get('work_type', '')} {permit_data.get('location', '')}
        """
        
        # Identify mechanical hazards
        mechanical_hazards = self._identify_mechanical_hazards(full_text, permit_data)
        
        # Assess energy sources
        energy_sources = self._assess_energy_sources(full_text, permit_data)
        
        # Generate control measures
        control_measures = self._generate_control_measures(mechanical_hazards, energy_sources)
        
        # Determine required DPI
        required_dpi = self._determine_mechanical_dpi(mechanical_hazards)
        
        # Generate LOTO requirements
        loto_requirements = self._generate_loto_requirements(energy_sources)
        
        # Calculate risk level
        risk_level = self._calculate_mechanical_risk(mechanical_hazards, energy_sources)
        
        # CONVERT TO STANDARD OUTPUT FORMAT per l'orchestratore
        return {
            # FORMATO STANDARD RICHIESTO DALL'ORCHESTRATORE
            "risks_identified": [
                {
                    "type": hazard["type"],
                    "source": "Mechanical_Specialist",
                    "description": hazard["description"],
                    "severity": hazard["severity"],
                    "likelihood": hazard.get("likelihood", "media"),
                    "energy_type": hazard.get("energy_type", "mechanical")
                } for hazard in mechanical_hazards
            ] if mechanical_hazards else [
                {
                    "type": "mechanical_standard",
                    "source": "Mechanical_Specialist",
                    "description": "Rischi meccanici standard da valutare",
                    "severity": "media"
                }
            ],
            
            "dpi_requirements": [
                f"{dpi['type']} ({dpi['standard']})" for dpi in required_dpi
            ] + [
                f"DPI specifici per energia {source['type']}" for source in energy_sources
            ],
            
            "control_measures": control_measures + self._generate_isolation_procedures(energy_sources) + [
                f"Attrezzature specializzate: {', '.join(self._identify_specialized_equipment(mechanical_hazards))}"
            ] if self._identify_specialized_equipment(mechanical_hazards) else control_measures,
            
            "permits_required": self._identify_required_permits(mechanical_hazards, energy_sources),
            
            "document_citations": [
                {
                    "type": "normativa_meccanica",
                    "source": "D.Lgs 81/08 - Allegato VI",
                    "description": "Requisiti minimi attrezzature di lavoro",
                    "mandatory": True
                },
                {
                    "type": "standard_loto",
                    "source": "UNI 11670:2017", 
                    "description": "Procedure Lock Out Tag Out",
                    "mandatory": True if energy_sources else False
                }
            ] + [
                {
                    "type": "norma_dpi_meccanico",
                    "source": dpi["standard"],
                    "description": f"Standard per {dpi['type']}",
                    "mandatory": dpi["mandatory"]
                } for dpi in required_dpi
            ],
            
            # DETTAGLI TECNICI ORIGINALI (mantenuti per compatibilità)
            "specialist": "Mechanical_Specialist",
            "risk_domain": "mechanical_hazards", 
            "analysis_complete": True,
            "confidence": 0.85,
            "mechanical_hazards_identified": mechanical_hazards,
            "energy_sources": energy_sources,
            "risk_level": risk_level,
            "loto_requirements": loto_requirements,
            "isolation_procedures": self._generate_isolation_procedures(energy_sources),
            "specialized_equipment": self._identify_specialized_equipment(mechanical_hazards),
            "training_requirements": self._generate_training_requirements(mechanical_hazards),
            "inspection_points": self._define_inspection_points(mechanical_hazards),
            "emergency_procedures": self._generate_emergency_procedures(mechanical_hazards)
        }
    
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
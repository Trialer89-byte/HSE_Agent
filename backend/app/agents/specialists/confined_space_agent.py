"""
Confined Space Specialist Agent
"""
from typing import Dict, Any
from ..base_agent import BaseHSEAgent


class ConfinedSpaceSpecialist(BaseHSEAgent):
    """Specialist for confined space entry operations"""
    
    def __init__(self):
        super().__init__(
            name="ConfinedSpace_Specialist",
            specialization="Spazi Confinati",
            activation_keywords=[
                # Standard terms
                "confined space", "spazio confinato",
                "tank", "serbatoio", "cisterna",
                "vessel", "recipiente", "contenitore",
                "silo", "hopper", "tramoggia",
                "pit", "fossa", "vasca",
                "manhole", "pozzetto", "tombino",
                "tunnel", "galleria", "cunicolo",
                "duct", "condotto", "canalizzazione",
                "chamber", "camera", "vano",
                
                # Activities indicating confined space
                "internal inspection", "ispezione interna",
                "tank cleaning", "pulizia serbatoio",
                "vessel entry", "ingresso recipiente"
            ]
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
✓ DPI specifici e dispositivi emergenza
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

DPI E ATTREZZATURE CRITICHE:
- Rilevatore multigas calibrato (O2, LEL, H2S, CO)
- SCBA o aria respirabile con linea
- Imbracatura con punto aggancio dorsale
- Tripode/argano per recupero verticale
- Ventilatore ATEX con manichette
- Radio ATEX per comunicazione
- Illuminazione ATEX
"""
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze permit for confined space risks"""
        
        risks = []
        controls = []
        dpi_required = []
        
        permit_text = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('location', '')}".lower()
        
        # Identify if it's a confined space entry
        is_confined_space = any(keyword in permit_text for keyword in [
            "tank", "serbatoio", "vessel", "silo", "pit", "fossa",
            "internal", "interno", "inside", "entry", "ingresso"
        ])
        
        if is_confined_space:
            # Critical risks for confined spaces
            risks.append({
                "type": "confined_space_atmosphere",
                "description": "CRITICO: Rischio asfissia/intossicazione da atmosfera pericolosa",
                "severity": "critica",
                "controls_required": ["atmospheric_testing", "continuous_monitoring", "forced_ventilation"]
            })
            
            risks.append({
                "type": "confined_space_entrapment",
                "description": "Rischio intrappolamento e difficoltà evacuazione",
                "severity": "alta",
                "controls_required": ["rescue_plan", "attendant", "retrieval_system"]
            })
            
            # Check for additional hazards
            if any(term in permit_text for term in ["chemical", "chimico", "product", "prodotto"]):
                risks.append({
                    "type": "toxic_atmosphere",
                    "description": "Rischio intossicazione da vapori chimici residui",
                    "severity": "critica",
                    "controls_required": ["gas_free_certificate", "SCBA", "decontamination"]
                })
            
            # Mandatory controls for confined space
            controls.extend([
                "Confined Space Entry Permit OBBLIGATORIO",
                "Test atmosfera pre-ingresso (O2, LEL, H2S, CO)",
                "Ventilazione forzata minimo 30 minuti prima accesso",
                "Monitoraggio continuo atmosfera durante lavori",
                "Supervisore esterno SEMPRE presente",
                "Sistema comunicazione continua interno/esterno",
                "Piano di emergenza e rescue team disponibile",
                "Isolamento energetico completo (LOTO)",
                "Bonifica e lavaggio se conteneva sostanze pericolose"
            ])
            
            # Specific PPE for confined space
            dpi_required.extend([
                "Rilevatore multigas personale con allarmi",
                "Imbracatura con recupero dorsale EN 361",
                "SCBA o sistema aria respirabile con linea",
                "Radio ATEX per comunicazione",
                "Elmetto con lampada frontale ATEX",
                "Tuta Tyvek se contaminazione chimica"
            ])
            
            # Additional equipment required
            equipment_required = [
                "Tripode con argano per recupero",
                "Ventilatore ATEX con manichette",
                "Kit pronto soccorso specifico",
                "Barella spinale per evacuazione",
                "Monitor atmosfera fisso all'ingresso"
            ]
            
            return {
                "specialist": self.name,
                "classification": "SPAZIO CONFINATO - DPR 177/2011 APPLICABILE",
                "risks_identified": risks,
                "control_measures": controls,
                "dpi_requirements": dpi_required,
                "equipment_requirements": equipment_required,
                "permits_required": ["Confined Space Entry Permit", "LOTO Permit"],
                "training_requirements": [
                    "Formazione specifica spazi confinati (16 ore min)",
                    "Addestramento uso DPI III categoria",
                    "Training procedure emergenza e recupero"
                ],
                "emergency_measures": [
                    "Rescue team addestrato on-site",
                    "Piano evacuazione non-entry rescue",
                    "Comunicazione diretta con emergenza medica",
                    "SCBA di riserva per soccorritori"
                ],
                "regulatory_compliance": "DPR 177/2011 - Qualificazione imprese OBBLIGATORIA"
            }
        
        return {
            "specialist": self.name,
            "classification": "Non classificato come spazio confinato",
            "risks_identified": [],
            "control_measures": [],
            "dpi_requirements": []
        }
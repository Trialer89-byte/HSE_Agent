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
            activation_keywords=[
                # Standard terms
                "height", "altezza", "quota",
                "ladder", "scala", "scale",
                "scaffold", "ponteggio", "impalcatura",
                "roof", "tetto", "copertura",
                "platform", "piattaforma",
                "elevated", "sopraelevato",
                "fall", "caduta",
                "crane", "gru",
                "lift", "sollevamento", "cestello",
                
                # Height indicators
                "metri", "meter", "m di altezza",
                "piano", "floor", "livello",
                
                # Equipment
                "harness", "imbracatura",
                "lanyard", "cordino",
                "anchor", "ancoraggio"
            ]
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
- Addestramento pratico uso DPI anticaduta
- Sorveglianza sanitaria specifica
- Piano di emergenza e recupero
- Verifica giornaliera DPI e ancoraggi

CRITERI DI STOP LAVORI:
✗ Vento > 60 km/h
✗ Temporali in arrivo
✗ Visibilità insufficiente
✗ Ghiaccio su superfici
✗ DPI danneggiati/non conformi
✗ Assenza supervisore formato

DPI SPECIFICI LAVORI IN QUOTA:
- Imbracatura anticaduta EN 361 (punto attacco dorsale/sternale)
- Doppio cordino con assorbitore energia EN 355
- Dispositivo retrattile EN 360 per movimenti
- Elmetto con sottogola EN 397/EN 12492
- Scarpe antiscivolo con suola antiperforazione
- Guanti grip per presa sicura
- Kit evacuazione/recupero
"""
    
    def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze permit for work at height risks"""
        
        risks = []
        controls = []
        dpi_required = []
        
        permit_text = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('location', '')} {permit_data.get('equipment', '')}".lower()
        
        # Check for height indicators
        height_detected = False
        height_level = "unknown"
        
        # Check for explicit height mentions
        import re
        height_pattern = r'(\d+)\s*(m|metri|meter)'
        height_match = re.search(height_pattern, permit_text)
        if height_match:
            height_value = int(height_match.group(1))
            if height_value >= 2:
                height_detected = True
                height_level = "alta" if height_value > 6 else "media"
        
        # Check for height-related keywords
        if any(keyword in permit_text for keyword in [
            "tetto", "roof", "scala", "ladder", "ponteggio", "scaffold",
            "piano", "floor", "sopraelevat", "elevated", "quota", "height"
        ]):
            height_detected = True
            if height_level == "unknown":
                height_level = "media"  # Conservative assumption
        
        if height_detected:
            # Primary fall risk
            risks.append({
                "type": "fall_from_height",
                "description": f"Rischio caduta dall'alto - Lavori in quota",
                "severity": height_level,
                "controls_required": ["fall_protection", "anchor_points", "safety_harness"]
            })
            
            # Falling objects risk
            risks.append({
                "type": "falling_objects",
                "description": "Rischio caduta materiali dall'alto",
                "severity": "media",
                "controls_required": ["tool_lanyards", "exclusion_zone", "toe_boards"]
            })
            
            # Environmental risks
            if "outdoor" in permit_text or "esterno" in permit_text or "roof" in permit_text:
                risks.append({
                    "type": "weather_hazards",
                    "description": "Rischi meteo (vento, pioggia) per lavori in quota esterni",
                    "severity": "media",
                    "controls_required": ["weather_monitoring", "stop_work_criteria"]
                })
            
            # Mandatory controls for work at height
            controls.extend([
                "Valutazione rischi specifica per lavori in quota",
                "Verifica portata e stabilità strutture/supporti",
                "Installazione protezioni collettive (parapetti, reti)",
                "Delimitazione area sottostante (rischio caduta oggetti)",
                "Sistema anticaduta con doppio cordino",
                "Punti di ancoraggio certificati EN 795",
                "Supervisore formato presente durante lavori",
                "Piano di emergenza e recupero specifico",
                "Controllo meteo (stop se vento >60km/h)",
                "Ispezione pre-uso DPI anticaduta"
            ])
            
            # Specific PPE for height work
            dpi_required.extend([
                "Imbracatura anticaduta EN 361",
                "Doppio cordino con assorbitore EN 355",
                "Elmetto con sottogola EN 397",
                "Scarpe antiscivolo S3 con suola antiperforazione",
                "Guanti con grip migliorato",
                "Giubbotto alta visibilità"
            ])
            
            # Check for specific equipment
            if "scala" in permit_text or "ladder" in permit_text:
                controls.append("Verifica conformità scale EN 131")
                controls.append("Posizionamento scala 1:4 (75°)")
                controls.append("Assistente a terra per stabilizzazione")
            
            if "ponteggio" in permit_text or "scaffold" in permit_text:
                controls.append("Verifica PiMUS (Piano Montaggio Uso Smontaggio)")
                controls.append("Controllo ancoraggi ponteggio")
                controls.append("Parapetti completi su tutti i lati")
            
            return {
                "specialist": self.name,
                "classification": "LAVORI IN QUOTA IDENTIFICATI",
                "risks_identified": risks,
                "control_measures": controls,
                "dpi_requirements": dpi_required,
                "permits_required": ["Permesso Lavori in Quota"],
                "training_requirements": [
                    "Formazione lavori in quota (8 ore min)",
                    "Addestramento uso DPI anticaduta",
                    "Corso montaggio ponteggi (se applicabile)"
                ],
                "emergency_measures": [
                    "Piano di recupero/evacuazione",
                    "Kit primo soccorso trauma",
                    "Comunicazione con emergenza medica",
                    "Barella e sistema recupero disponibili"
                ],
                "stop_work_conditions": [
                    "Vento superiore a 60 km/h",
                    "Temporali/fulmini in arrivo",
                    "Ghiaccio o neve su superfici",
                    "Visibilità insufficiente",
                    "DPI danneggiati o non conformi"
                ]
            }
        
        return {
            "specialist": self.name,
            "classification": "Nessun lavoro in quota identificato",
            "risks_identified": [],
            "control_measures": [],
            "dpi_requirements": []
        }
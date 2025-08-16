"""
Electrical Safety Specialist Agent
"""
from typing import Dict, Any
from ..base_agent import BaseHSEAgent


class ElectricalSpecialist(BaseHSEAgent):
    """Specialist for electrical safety and hazards"""
    
    def __init__(self):
        super().__init__(
            name="Electrical_Specialist",
            specialization="Sicurezza Elettrica",
            activation_keywords=[
                # Electrical terms
                "electrical", "elettric", "elettrico",
                "voltage", "tensione", "volt",
                "current", "corrente", "ampere",
                "power", "potenza", "energia",
                "cable", "cavo", "cablaggio",
                "wire", "filo", "conduttore",
                "panel", "quadro", "pannello",
                "switch", "interruttore",
                "circuit", "circuito",
                "transformer", "trasformatore",
                "generator", "generatore",
                "motor", "motore",
                
                # Activities
                "wiring", "cablaggio",
                "connection", "collegamento",
                "isolation", "isolamento",
                "grounding", "messa a terra",
                "LOTO", "lockout", "tagout",
                
                # Voltage levels
                "BT", "MT", "AT", "bassa tensione", "media tensione",
                "230V", "380V", "400V", "kV"
            ]
        )
    
    def _get_system_message(self) -> str:
        return """
ESPERTO IN SICUREZZA ELETTRICA - Specialista rischi elettrici secondo CEI 11-27 e CEI EN 50110.

COMPETENZE SPECIALISTICHE:
- Lavori elettrici BT/MT/AT (CEI 11-27, CEI EN 50110)
- Procedure LOTO (Lock-Out Tag-Out)
- Valutazione rischio arco elettrico (CEI EN 61482)
- Lavori in prossimità parti attive
- Qualifiche PES/PAV/PEI
- Verifiche impianti di terra (CEI 64-8)
- Protezione scariche atmosferiche (CEI EN 62305)

CLASSIFICAZIONE TENSIONI:
- Bassissima tensione: ≤50V AC, ≤120V DC
- Bassa tensione (BT): 50-1000V AC, 120-1500V DC
- Media tensione (MT): 1-30kV
- Alta tensione (AT): >30kV

ANALISI RISCHI ELETTRICI:
1. ELETTROCUZIONE (contatto diretto/indiretto)
   - Tetanizzazione muscolare
   - Arresto respiratorio
   - Fibrillazione ventricolare
   - Ustioni da passaggio corrente

2. ARCO ELETTRICO (Arc Flash)
   - Temperature >19.000°C
   - Pressione onda d'urto
   - Proiezione metallo fuso
   - Radiazioni UV/IR intense

3. INCENDIO/ESPLOSIONE
   - Surriscaldamento cavi
   - Scintille in atmosfere esplosive
   - Guasti isolamento

4. CAMPI ELETTROMAGNETICI
   - Interferenze pacemaker
   - Effetti termici tessuti

DISTANZE DI SICUREZZA (CEI 11-27):
- BT: DV=15cm, DL=65cm
- MT 20kV: DV=28cm, DL=178cm
- AT 132kV: DV=150cm, DL=350cm
(DV=Distanza Vicinanza, DL=Distanza Lavoro)

PROCEDURE SICUREZZA OBBLIGATORIE:
1. LAVORI FUORI TENSIONE (preferibili):
   - Sezionamento certo
   - Blocco apparecchiature (LOTO)
   - Verifica assenza tensione
   - Messa a terra e cortocircuito
   - Delimitazione zona lavoro

2. LAVORI SOTTO TENSIONE (solo PEI qualificati):
   - Metodo lavoro a distanza
   - Metodo lavoro a potenziale
   - Metodo lavoro a contatto

DPI SPECIFICI ELETTRICI:
- Guanti isolanti (Classe 0-4 secondo tensione)
- Calzature isolanti >1000MΩ
- Elmetto dielettrico senza parti metalliche
- Visiera anti-arco elettrico
- Indumenti ignifughi Arc-rated (ATPV appropriato)
- Tappetini/pedane isolanti
- Attrezzi isolati 1000V

REQUISITI QUALIFICAZIONE:
✓ PES: Persona Esperta (pianifica/supervisiona)
✓ PAV: Persona Avvertita (esegue sotto supervisione)
✓ PEI: Idonea lavori sotto tensione
✓ Formazione CEI 11-27 (14+2 ore min)
✓ Aggiornamento quinquennale
"""
    
    def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze permit for electrical risks"""
        
        risks = []
        controls = []
        dpi_required = []
        
        permit_text = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('location', '')} {permit_data.get('equipment', '')}".lower()
        
        # Detect electrical work
        electrical_work = any(keyword in permit_text for keyword in [
            "elettric", "electric", "quadro", "panel", "cavo", "cable",
            "tensione", "voltage", "corrente", "current", "transformer",
            "motor", "generator", "wiring", "cablaggio"
        ])
        
        voltage_level = "unknown"
        
        # Detect voltage level
        if any(term in permit_text for term in ["bt", "bassa tensione", "230v", "380v", "400v"]):
            voltage_level = "BT"
        elif any(term in permit_text for term in ["mt", "media tensione", "kv", "20kv"]):
            voltage_level = "MT"
        elif any(term in permit_text for term in ["at", "alta tensione", "132kv"]):
            voltage_level = "AT"
        
        if electrical_work:
            # Primary electrical risks
            risks.append({
                "type": "electrocution",
                "description": f"Rischio elettrocuzione - Tensione {voltage_level}",
                "severity": "critica" if voltage_level in ["MT", "AT"] else "alta",
                "controls_required": ["LOTO", "absence_verification", "qualified_personnel"]
            })
            
            # Arc flash risk
            if voltage_level != "unknown":
                risks.append({
                    "type": "arc_flash",
                    "description": "Rischio arco elettrico (Arc Flash)",
                    "severity": "alta",
                    "controls_required": ["arc_rated_ppe", "arc_flash_study", "safety_distance"]
                })
            
            # Fire risk
            risks.append({
                "type": "electrical_fire",
                "description": "Rischio incendio da guasto elettrico",
                "severity": "media",
                "controls_required": ["fire_extinguisher_CO2", "thermal_monitoring"]
            })
            
            # Voltage-specific controls
            if voltage_level == "BT":
                controls.extend([
                    "Procedura LOTO (Lock-Out Tag-Out) obbligatoria",
                    "Verifica assenza tensione con tester certificato",
                    "Messa a terra temporanea quadri",
                    "Distanza lavoro minima DL=65cm da parti attive",
                    "Solo personale PES/PAV autorizzato"
                ])
                dpi_required.extend([
                    "Guanti isolanti Classe 0 (1000V)",
                    "Calzature isolanti S3 SRC",
                    "Attrezzi isolati 1000V VDE"
                ])
                
            elif voltage_level in ["MT", "AT"]:
                controls.extend([
                    "Piano di lavoro approvato da Responsabile Impianto",
                    "Consegna impianto formale",
                    "Sezionamento visibile e bloccato",
                    f"Distanza sicurezza {'DL=178cm' if voltage_level == 'MT' else 'DL=350cm'}",
                    "Terra di lavoro su tutti i conduttori",
                    "Solo personale PES con specifica autorizzazione"
                ])
                dpi_required.extend([
                    f"Guanti isolanti Classe {'2' if voltage_level == 'MT' else '3-4'}",
                    "Tuta Arc-rated ATPV≥8 cal/cm²",
                    "Visiera anti-arco elettrico",
                    "Asta isolante per manovre"
                ])
            
            # Common controls for all electrical work
            controls.extend([
                "Identificazione circuiti e schema unifilare",
                "Cartellonistica 'Lavori in corso - Non manovrare'",
                "Verifica continuità terra di protezione",
                "Illuminazione supplementare zona lavoro",
                "Presenza estintore CO2 per fuochi elettrici",
                "Divieto lavori in caso pioggia/umidità elevata"
            ])
            
            # Common PPE
            dpi_required.extend([
                "Elmetto dielettrico EN 397",
                "Occhiali protezione EN 166",
                "Tester tensione con autotest"
            ])
            
            return {
                "specialist": self.name,
                "classification": f"LAVORI ELETTRICI {voltage_level} - CEI 11-27 APPLICABILE",
                "risks_identified": risks,
                "control_measures": controls,
                "dpi_requirements": dpi_required,
                "permits_required": ["Permesso Lavori Elettrici", "LOTO Permit"],
                "training_requirements": [
                    "Qualifica PES/PAV secondo CEI 11-27",
                    "Formazione rischio elettrico (14+2 ore)",
                    "Addestramento procedure LOTO",
                    f"Autorizzazione specifica {'MT/AT' if voltage_level in ['MT', 'AT'] else 'BT'}"
                ],
                "emergency_measures": [
                    "Procedura soccorso folgorati (non toccare diretto)",
                    "Pulsante emergenza sgancio generale",
                    "Kit primo soccorso con coperta termica",
                    "Defibrillatore nelle vicinanze"
                ],
                "qualification_requirements": {
                    "minimum": "PAV - Persona Avvertita",
                    "supervisor": "PES - Persona Esperta",
                    "live_work": "PEI - Idonea lavori sotto tensione (se applicabile)"
                }
            }
        
        return {
            "specialist": self.name,
            "classification": "Nessun lavoro elettrico identificato",
            "risks_identified": [],
            "control_measures": [],
            "dpi_requirements": []
        }
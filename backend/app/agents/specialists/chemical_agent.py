"""
Chemical and ATEX Specialist Agent  
"""
from typing import Dict, Any
from ..base_agent import BaseHSEAgent


class ChemicalSpecialist(BaseHSEAgent):
    """Specialist for chemical hazards and explosive atmospheres"""
    
    def __init__(self):
        super().__init__(
            name="Chemical_Specialist",
            specialization="Rischi Chimici e Atmosfere Esplosive",
            activation_keywords=[
                # Chemical terms
                "chemical", "chimico", "sostanza",
                "toxic", "tossico", "nocivo",
                "corrosive", "corrosivo",
                "flammable", "infiammabile",
                "explosive", "esplosivo",
                "gas", "vapore", "vapor",
                "fume", "fumo", "polvere",
                "solvent", "solvente",
                "acid", "acido",
                "base", "alcalino",
                
                # ATEX indicators
                "ATEX", "explosion", "esplosione",
                "LEL", "LIE", "limite esplosivo",
                "zone 0", "zone 1", "zone 2",
                "zone 20", "zone 21", "zone 22",
                
                # Common chemicals
                "oil", "olio", "petrolio",
                "fuel", "carburante", "benzina",
                "diesel", "gasolio",
                "hydrogen", "idrogeno",
                "methane", "metano",
                "ammonia", "ammoniaca",
                "H2S", "solfuro",
                
                # Activities
                "tank", "serbatoio", "cisterna",
                "storage", "stoccaggio",
                "transfer", "travaso",
                "mixing", "miscelazione",
                "cleaning", "pulizia", "bonifica"
            ]
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
    
    def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze permit for chemical and ATEX risks"""
        
        risks = []
        controls = []
        dpi_required = []
        
        permit_text = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('location', '')} {permit_data.get('equipment', '')}".lower()
        
        # Detect chemical/ATEX indicators
        chemical_work = False
        atex_risk = False
        substances = []
        
        # Check for fuel/oil (common in maintenance)
        if any(term in permit_text for term in ["oil", "olio", "fuel", "benzina", "diesel", "gasolio", "petrolio"]):
            chemical_work = True
            atex_risk = True
            substances.append("idrocarburi")
            
        # Check for tank/vessel work
        if any(term in permit_text for term in ["tank", "serbatoio", "cisterna", "vessel"]):
            chemical_work = True
            if any(term in permit_text for term in ["oil", "fuel", "chemical", "gas"]):
                atex_risk = True
                
        # Check for specific chemicals
        if any(term in permit_text for term in ["chemical", "chimico", "toxic", "tossico", "corrosive", "solvent"]):
            chemical_work = True
            
        # Check for gas/vapors
        if any(term in permit_text for term in ["gas", "vapor", "vapore", "fume", "h2s", "ammonia"]):
            chemical_work = True
            atex_risk = True
            
        if chemical_work:
            # Chemical exposure risk
            risks.append({
                "type": "chemical_exposure",
                "description": f"Rischio esposizione chimica - {', '.join(substances) if substances else 'sostanze non specificate'}",
                "severity": "alta" if atex_risk else "media",
                "controls_required": ["sds_review", "ventilation", "monitoring"]
            })
            
            if atex_risk:
                # ATEX risk - Critical!
                risks.append({
                    "type": "explosion_atex",
                    "description": "CRITICO: Rischio esplosione - Atmosfera potenzialmente esplosiva (ATEX)",
                    "severity": "critica",
                    "controls_required": ["gas_free_certificate", "continuous_monitoring", "atex_equipment", "hot_work_prohibition"]
                })
                
                risks.append({
                    "type": "fire_chemical",
                    "description": "Rischio incendio da vapori infiammabili",
                    "severity": "alta",
                    "controls_required": ["elimination_ignition_sources", "grounding", "fire_suppression"]
                })
                
                # ATEX specific controls
                controls.extend([
                    "Classificazione zona ATEX obbligatoria",
                    "Certificato Gas-Free prima di qualsiasi lavoro",
                    "Monitoraggio continuo LEL con allarme <10%",
                    "Monitoraggio O2 (19.5-23.5%)",
                    "Ventilazione forzata continua min 10 ricambi/ora",
                    "Attrezzature certificate ATEX (II 2G o II 2D)",
                    "Eliminazione TUTTE fonti innesco",
                    "Messa a terra e equipotenzialità",
                    "Permesso di lavoro speciale per zona ATEX",
                    "Divieto assoluto lavori a caldo senza bonifica"
                ])
                
                # ATEX PPE
                dpi_required.extend([
                    "Rilevatore multigas personale (LEL, O2, H2S, CO)",
                    "Indumenti antistatici EN 1149",
                    "Calzature antistatiche/conduttive",
                    "Attrezzi antiscintilla (bronzo, ottone)",
                    "Torce certificate ATEX"
                ])
            
            # General chemical controls
            controls.extend([
                "Consultazione SDS (Schede Dati Sicurezza) PRIMA dei lavori",
                "Valutazione rischio chimico specifica",
                "Ventilazione adeguata area di lavoro",
                "Kit assorbimento/neutralizzazione sversamenti",
                "Doccia/lavaocchi di emergenza disponibile",
                "Divieto mangiare/bere/fumare in area",
                "Decontaminazione al termine lavori"
            ])
            
            # Check for specific protection needs
            if "acid" in permit_text or "acido" in permit_text:
                dpi_required.extend([
                    "Tuta antiacido Tipo 3",
                    "Guanti PVC/Neoprene antiacido",
                    "Visiera antiacido panoramica"
                ])
                controls.append("Neutralizzante specifico disponibile")
                
            elif "solvent" in permit_text or "solvente" in permit_text:
                dpi_required.extend([
                    "Respiratore con filtri A (vapori organici)",
                    "Guanti nitrile resistenti solventi",
                    "Tuta Tyvek Tipo 5/6"
                ])
                
            # Standard chemical PPE
            dpi_required.extend([
                "Occhiali chimici a tenuta EN 166",
                "Respiratore con filtri appropriati (ABEK-P3)",
                "Guanti chimici secondo EN 374",
                "Tuta chimica (minimo Tipo 6)",
                "Stivali chimici resistenti"
            ])
            
            # Additional measures for tank/confined space + chemicals
            if "tank" in permit_text or "serbatoio" in permit_text:
                controls.extend([
                    "Bonifica completa e certificata del serbatoio",
                    "Test atmosfera stratificato (alto/medio/basso)",
                    "Piano evacuazione rapida",
                    "SCBA di emergenza all'ingresso"
                ])
                
            emergency_equipment = [
                "Doccia di emergenza/lavaocchi",
                "Kit neutralizzazione sversamenti",
                "Coperte ignifughe",
                "Estintori appropriati (polvere/CO2/schiuma)",
                "SCBA per soccorritori"
            ]
            
            return {
                "specialist": self.name,
                "classification": "RISCHIO CHIMICO" + (" + ATMOSFERA ESPLOSIVA ATEX" if atex_risk else ""),
                "risks_identified": risks,
                "control_measures": controls,
                "dpi_requirements": dpi_required,
                "equipment_requirements": emergency_equipment,
                "permits_required": ["Permesso Esposizione Chimica"] + (["ATEX Work Permit"] if atex_risk else []),
                "training_requirements": [
                    "Formazione rischio chimico",
                    "Lettura e comprensione SDS",
                    "Uso corretto DPI chimici"
                ] + (["Formazione ATEX", "Procedure emergenza esplosione"] if atex_risk else []),
                "emergency_measures": [
                    "Piano evacuazione immediata",
                    "Procedure decontaminazione",
                    "Antidoti specifici se applicabili",
                    "Comunicazione con centro antiveleni"
                ] + (["Procedura emergenza esplosione", "Isolamento area minimo 100m"] if atex_risk else []),
                "monitoring_requirements": {
                    "continuous": ["LEL (<10%)", "O2 (19.5-23.5%)"] if atex_risk else [],
                    "periodic": ["Concentrazione vapori", "Qualità aria"]
                }
            }
        
        return {
            "specialist": self.name,
            "classification": "Nessun rischio chimico significativo identificato",
            "risks_identified": [],
            "control_measures": [],
            "dpi_requirements": []
        }
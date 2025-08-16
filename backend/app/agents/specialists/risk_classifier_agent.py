"""
Risk Classifier Agent - Primary analyzer
"""
from typing import Dict, Any, List
from ..base_agent import BaseHSEAgent
import re


class RiskClassifierAgent(BaseHSEAgent):
    """Primary risk classification agent that analyzes and routes to specialists"""
    
    def __init__(self):
        super().__init__(
            name="Risk_Classifier",
            specialization="Classificazione e Analisi Rischi Primaria",
            activation_keywords=[]  # Always active
        )
        
        # Define risk patterns for intelligent classification
        self.risk_patterns = {
            "hot_work": {
                "keywords": ["weld", "sald", "cut", "tagl", "grind", "mol", "torch", "flame", "spark", "heat"],
                "equipment": ["welder", "torch", "grinder", "plasma", "cutting"],
                "misspellings": ["welsing", "weling", "salding", "cuting", "griding"]
            },
            "confined_space": {
                "keywords": ["tank", "serbatoio", "vessel", "silo", "pit", "fossa", "confined", "confinato"],
                "locations": ["inside", "internal", "dentro", "interno"],
                "activities": ["entry", "cleaning", "inspection", "ingresso", "pulizia", "ispezione"]
            },
            "electrical": {
                "keywords": ["electrical", "elettric", "voltage", "tensione", "panel", "quadro", "cable"],
                "equipment": ["transformer", "switchgear", "motor", "generator"],
                "activities": ["wiring", "cablaggio", "connection", "collegamento"]
            },
            "height": {
                "keywords": ["height", "altezza", "ladder", "scala", "scaffold", "ponteggio", "roof", "tetto"],
                "indicators": ["fall", "caduta", "elevated", "sopraelevat"],
                "measurements": [r"\d+\s*m", r"\d+\s*meter", r"\d+\s*metri"]
            },
            "chemical": {
                "keywords": ["chemical", "chimico", "substance", "sostanza", "hazmat", "toxic", "tossico"],
                "indicators": ["fume", "vapor", "gas", "liquid", "spill", "leak"],
                "hazards": ["corrosive", "flammable", "reactive", "asphyxiant"]
            }
        }
    
    def _get_system_message(self) -> str:
        return """
RISK CLASSIFIER PRINCIPALE - Analizzatore primario e classificatore di rischi HSE.

RUOLO CRITICO: Sei il PRIMO punto di analisi. Devi identificare TUTTI i rischi potenziali e attivare gli specialisti giusti.

METODOLOGIA SISTEMATICA:
1. ANALISI SEMANTICA INTELLIGENTE
   - Interpreta il significato, non solo le parole chiave
   - Riconosci errori ortografici comuni (welsing = welding)
   - Identifica attività implicite non dichiarate
   - Considera il contesto industriale

2. CLASSIFICAZIONE MULTILIVELLO
   - Rischi ESPLICITI (chiaramente menzionati)
   - Rischi IMPLICITI (tipici dell'attività)
   - Rischi NASCOSTI (non ovvi ma probabili)
   - Rischi da INTERFERENZA (combinazioni pericolose)

3. ATTIVAZIONE SPECIALISTI
   Determina quali esperti coinvolgere:
   - Hot Work: saldatura, taglio, molatura
   - Confined Space: spazi ristretti, serbatoi
   - Electrical: impianti elettrici, quadri
   - Height: lavori in quota > 2m
   - Chemical: sostanze pericolose, ATEX
   - Mechanical: macchinari, energia residua

4. PRIORITIZZAZIONE RISCHI
   - CRITICO: potenziale fatalità/infortunio grave
   - ALTO: infortunio serio probabile
   - MEDIO: infortunio moderato possibile
   - BASSO: rischio minore controllabile

APPROCCIO DETECTIVE:
- Leggi tra le righe
- Cosa NON dice il permesso?
- Quali preparazioni sono necessarie?
- Quali rischi emergono durante l'esecuzione?
- Meglio sovrastimare che sottostimare

OUTPUT RICHIESTO:
Classificazione strutturata con:
- Attività identificate (anche quelle non dichiarate)
- Ambiente di lavoro e interferenze
- Rischi per categoria e priorità
- Specialisti da attivare
- Informazioni mancanti critiche
"""
    
    def should_activate(self, risk_classification: Dict[str, Any]) -> bool:
        """Risk Classifier is always active as primary analyzer"""
        return True
    
    def _detect_risks(self, text: str) -> Dict[str, List[str]]:
        """Detect risk categories from text using patterns"""
        detected_risks = {}
        text_lower = text.lower()
        
        for risk_type, patterns in self.risk_patterns.items():
            matches = []
            
            # Check keywords
            for keyword in patterns.get("keywords", []):
                if keyword in text_lower:
                    matches.append(f"keyword: {keyword}")
            
            # Check equipment
            for equipment in patterns.get("equipment", []):
                if equipment in text_lower:
                    matches.append(f"equipment: {equipment}")
            
            # Check misspellings
            for misspelling in patterns.get("misspellings", []):
                if misspelling in text_lower:
                    matches.append(f"misspelling detected: {misspelling}")
            
            # Check locations/activities
            for location in patterns.get("locations", []):
                if location in text_lower:
                    matches.append(f"location: {location}")
                    
            for activity in patterns.get("activities", []):
                if activity in text_lower:
                    matches.append(f"activity: {activity}")
            
            # Check regex patterns (for height measurements)
            for pattern in patterns.get("measurements", []):
                if re.search(pattern, text_lower):
                    matches.append(f"measurement found")
            
            if matches:
                detected_risks[risk_type] = matches
        
        return detected_risks
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Perform primary risk classification and routing"""
        
        # Combine all text for analysis
        full_text = f"""
        Title: {permit_data.get('title', '')}
        Description: {permit_data.get('description', '')}
        Work Type: {permit_data.get('work_type', '')}
        Location: {permit_data.get('location', '')}
        Equipment: {permit_data.get('equipment', '')}
        Duration: {permit_data.get('duration_hours', '')} hours
        Workers: {permit_data.get('workers_count', '')}
        """
        
        # Detect risks using patterns
        detected_risks = self._detect_risks(full_text)
        
        # Classify overall risk level
        risk_level = self._classify_risk_level(detected_risks)
        
        # Determine which specialists to activate
        specialists_to_activate = []
        risk_domains = {}
        
        for risk_type, matches in detected_risks.items():
            specialists_to_activate.append(f"{risk_type}_specialist")
            risk_domains[risk_type] = {
                "detected": True,
                "confidence": "high" if len(matches) > 2 else "medium",
                "indicators": matches,
                "priority": "alta" if risk_type in ["hot_work", "confined_space"] else "media"
            }
        
        # Check for missing critical information
        missing_info = []
        if not permit_data.get('location'):
            missing_info.append("Ubicazione specifica del lavoro")
        if not permit_data.get('equipment'):
            missing_info.append("Attrezzature da utilizzare")
        if "chemical" in str(permit_data).lower() and "msds" not in str(context).lower():
            missing_info.append("Schede di sicurezza (MSDS) sostanze chimiche")
        
        # Identify implicit risks
        implicit_risks = []
        
        # Tank + repair often means confined space + hot work
        if "tank" in full_text.lower() and "repair" in full_text.lower():
            implicit_risks.append("Probabile spazio confinato con lavori a caldo")
            if "confined_space" not in detected_risks:
                detected_risks["confined_space"] = ["implicit: tank repair"]
                specialists_to_activate.append("confined_space")
            if "hot_work" not in detected_risks:
                detected_risks["hot_work"] = ["implicit: tank repair likely needs welding"]
                specialists_to_activate.append("hot_work")
        
        # Oil/fuel + any work = explosion risk
        if any(term in full_text.lower() for term in ["oil", "fuel", "gasoline", "benzina", "gasolio"]):
            implicit_risks.append("Atmosfera potenzialmente esplosiva (presenza idrocarburi)")
            if "chemical" not in detected_risks:
                detected_risks["chemical"] = ["implicit: flammable atmosphere"]
                specialists_to_activate.append("chemical")
        
        # Electrical work detection
        if any(term in full_text.lower() for term in ["elettric", "electric", "quadro", "panel", "tensione", "voltage"]):
            if "electrical" not in detected_risks:
                detected_risks["electrical"] = ["implicit: electrical work"]
                specialists_to_activate.append("electrical")
        
        # Height work detection  
        if any(term in full_text.lower() for term in ["altezza", "height", "scala", "ladder", "tetto", "roof", "ponteggio"]):
            implicit_risks.append("Possibili lavori in quota (>2m)")
            if "height" not in detected_risks:
                detected_risks["height"] = ["implicit: height indicators"]
                specialists_to_activate.append("height")
        
        return {
            "classification_complete": True,
            "activity_identified": self._extract_main_activity(permit_data),
            "work_environment": permit_data.get('location', 'Non specificato'),
            "risk_domains": risk_domains,
            "detected_risks": detected_risks,
            "implicit_risks": implicit_risks,
            "overall_risk_level": risk_level,
            "specialists_to_activate": list(set(specialists_to_activate)),
            "missing_critical_info": missing_info,
            "classification_confidence": "high" if not missing_info else "medium",
            "recommendations": self._generate_recommendations(detected_risks, implicit_risks)
        }
    
    def _extract_main_activity(self, permit_data: Dict[str, Any]) -> str:
        """Extract and interpret the main activity"""
        title = permit_data.get('title', '')
        work_type = permit_data.get('work_type', '')
        
        # Interpret common patterns
        if "repair" in title.lower():
            if "pipe" in title.lower() or "tub" in title.lower():
                return "Riparazione tubazioni (probabili lavori a caldo)"
            elif "tank" in title.lower():
                return "Riparazione serbatoio (spazio confinato + lavori a caldo)"
        elif "maintenance" in work_type.lower():
            return "Manutenzione impianti"
        elif "inspection" in title.lower():
            return "Ispezione (verificare se interna = spazio confinato)"
        
        return title if title else "Attività non chiaramente specificata"
    
    def _classify_risk_level(self, detected_risks: Dict[str, List[str]]) -> str:
        """Classify overall risk level based on detected risks"""
        
        # Critical combinations
        if "hot_work" in detected_risks and "chemical" in detected_risks:
            return "CRITICO - Lavori a caldo in presenza sostanze infiammabili"
        if "confined_space" in detected_risks and "hot_work" in detected_risks:
            return "CRITICO - Lavori a caldo in spazio confinato"
        if "confined_space" in detected_risks:
            return "ALTO - Spazio confinato"
        if "hot_work" in detected_risks:
            return "ALTO - Lavori a caldo"
        if "electrical" in detected_risks:
            return "ALTO - Rischio elettrico"
        if "height" in detected_risks:
            return "MEDIO-ALTO - Lavori in quota"
        
        return "MEDIO - Rischi standard industriali"
    
    def _generate_recommendations(self, detected_risks: Dict, implicit_risks: List) -> List[str]:
        """Generate recommendations based on risk analysis"""
        recommendations = []
        
        if "hot_work" in detected_risks:
            recommendations.append("Emettere Hot Work Permit obbligatorio")
            recommendations.append("Predisporre fire watch qualificato")
        
        if "confined_space" in detected_risks:
            recommendations.append("Emettere Confined Space Entry Permit")
            recommendations.append("Verificare qualificazione impresa DPR 177/2011")
        
        if implicit_risks:
            recommendations.append("Verificare e documentare rischi impliciti identificati")
        
        if not recommendations:
            recommendations.append("Procedere con valutazione rischi standard")
        
        return recommendations
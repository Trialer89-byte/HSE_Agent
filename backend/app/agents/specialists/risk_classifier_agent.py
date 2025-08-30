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
                "keywords": ["weld", "sald", "torch", "flame", "spark", "heat", "fiamma", "scintill"],
                "equipment": ["welder", "torch", "grinder", "plasma", "saldatrice", "cannello"],
                "actions": ["cutting", "taglio", "grinding", "molatura"],
                "context_required": ["cut", "tagl", "grind", "mol"],  # These need validation
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
        """Detect risk categories from text using patterns with context validation"""
        detected_risks = {}
        text_lower = text.lower()
        
        for risk_type, patterns in self.risk_patterns.items():
            matches = []
            context_matches = []
            
            # Check keywords (high confidence)
            for keyword in patterns.get("keywords", []):
                if keyword in text_lower:
                    matches.append(f"keyword: {keyword}")
            
            # Check equipment (high confidence)
            for equipment in patterns.get("equipment", []):
                if equipment in text_lower:
                    matches.append(f"equipment: {equipment}")
            
            # Check actions (medium confidence)
            for action in patterns.get("actions", []):
                # Use word boundaries to avoid partial matches
                import re
                if re.search(r'\b' + re.escape(action) + r'\b', text_lower):
                    matches.append(f"action: {action}")
            
            # Check context_required terms (need validation)
            for term in patterns.get("context_required", []):
                if term in text_lower:
                    # These terms need context validation
                    context_matches.append(f"context_term: {term}")
            
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
            
            # Only add risk if we have strong evidence or validated context
            if matches:
                detected_risks[risk_type] = matches
            elif context_matches and self._validate_context(risk_type, text_lower, context_matches):
                detected_risks[risk_type] = context_matches
        
        return detected_risks
    
    def _validate_context(self, risk_type: str, text: str, context_matches: List[str]) -> bool:
        """Validate if context matches actually indicate the risk"""
        
        # For hot work, validate that cutting/grinding terms are actually about hot work
        if risk_type == "hot_work":
            # Check for false positives
            false_positive_indicators = [
                "taglierina",  # cutting machine name, not cutting action
                "tagliaerba",   # lawnmower
                "tagliando",    # maintenance service
                "molleggio",    # suspension
                "molletta",     # clip
            ]
            
            for indicator in false_positive_indicators:
                if indicator in text:
                    return False
            
            # Check for positive context that confirms hot work
            hot_work_context = [
                "ossiacetilen",
                "plasma",
                "arco elettrico",
                "elettrodo",
                "fiamma",
                "torch",
                "metallo",
                "acciaio",
                "ferro",
                "saldatura",
                "brasatura"
            ]
            
            for context in hot_work_context:
                if context in text:
                    return True
            
            # If cutting/grinding is mentioned with pipes/metal, likely hot work
            if any(term in text for term in ["tubo", "pipe", "tubazione", "metall", "acciaio"]):
                if any(term in text for term in ["riparazione", "repair", "modifica", "modify"]):
                    return True
            
            return False
        
        # Default validation for other risk types
        return len(context_matches) > 0
    
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
        Risk Mitigation Actions: {permit_data.get('risk_mitigation_actions', '')}
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
        
        # Identify implicit risks with better context analysis
        implicit_risks = []
        
        # Tank + repair often means confined space (but validate hot work separately)
        if "tank" in full_text.lower() and "repair" in full_text.lower():
            if "confined_space" not in detected_risks:
                implicit_risks.append("Probabile spazio confinato per riparazione serbatoio")
                detected_risks["confined_space"] = ["implicit: tank repair"]
                specialists_to_activate.append("confined_space")
            # Only add hot work if welding/cutting context is present
            if self._validate_context("hot_work", full_text.lower(), ["repair"]):
                if "hot_work" not in detected_risks:
                    implicit_risks.append("Possibili lavori a caldo per riparazione")
                    detected_risks["hot_work"] = ["implicit: tank repair with welding context"]
                    specialists_to_activate.append("hot_work")
        
        # Oil/fuel + work = explosion risk
        if any(term in full_text.lower() for term in ["oil", "fuel", "gasoline", "benzina", "gasolio", "olio"]):
            implicit_risks.append("Atmosfera potenzialmente esplosiva (presenza idrocarburi)")
            if "chemical" not in detected_risks:
                detected_risks["chemical"] = ["implicit: flammable atmosphere"]
                specialists_to_activate.append("chemical_specialist")
            # Only add hot work if actual hot work indicators are present
            if self._validate_context("hot_work", full_text.lower(), ["cut", "tagl"]):
                implicit_risks.append("Lavori a caldo in presenza di sostanze infiammabili")
                if "hot_work" not in detected_risks:
                    detected_risks["hot_work"] = ["implicit: hot work near flammables"]
                    specialists_to_activate.append("hot_work_specialist")
        
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
                specialists_to_activate.append("height_specialist")
        
        # Mechanical risks detection (pressurized systems, rotating equipment)
        if any(term in full_text.lower() for term in ["tubo", "tube", "pipe", "tubazione", "pressione", "pressure", "vapor", "steam"]):
            implicit_risks.append("Rischi meccanici da sistemi in pressione")
            # For mechanical work, always check multiple risks
            if permit_data.get('work_type') == 'meccanico' or "meccanico" in full_text.lower():
                if "mechanical" not in detected_risks:
                    detected_risks["mechanical"] = ["implicit: mechanical work on pressurized systems"]
                    specialists_to_activate.append("mechanical_specialist")
                # Mechanical + cutting/welding = multiple specialists needed
                if any(cut_term in full_text.lower() for cut_term in ["taglio", "cut", "sald", "weld"]):
                    implicit_risks.append("Lavoro meccanico con operazioni di taglio - necessaria valutazione multipla")
        
        # Tube/pipe work specific logic - validate context carefully
        if any(tube_term in full_text.lower() for tube_term in ["tubo", "tube", "pipe", "tubazione"]):
            # Check if it's actually tube work that needs special attention
            tube_work_indicators = ["riparazione", "repair", "sostituzione", "replace", "modifica", "modify", "installazione", "install"]
            if any(indicator in full_text.lower() for indicator in tube_work_indicators):
                implicit_risks.append("Intervento su tubazioni - verificare rischi specifici")
                
                # Only add hot work if context validates it
                if self._validate_context("hot_work", full_text.lower(), ["taglio", "cut", "sald", "weld"]):
                    if "hot_work" not in detected_risks:
                        detected_risks["hot_work"] = ["implicit: tube work with hot work context"]
                        specialists_to_activate.append("hot_work_specialist")
                
                # Check for mechanical risks with pressurized systems
                if any(pressure_term in full_text.lower() for pressure_term in ["pressione", "pressure", "vapor", "steam", "compressed"]):
                    if "mechanical" not in detected_risks:
                        detected_risks["mechanical"] = ["implicit: pressurized system work"]
                        specialists_to_activate.append("mechanical_specialist")
                
                # If location suggests confined space
                if any(conf_term in full_text.lower() for conf_term in ["inside", "interno", "within", "all'interno"]):
                    if "confined_space" not in detected_risks:
                        detected_risks["confined_space"] = ["implicit: internal tube work"]
                        specialists_to_activate.append("confined_space_specialist")
        
        # Evaluate risk mitigation actions  
        mitigation_evaluation = self._evaluate_mitigation_actions(
            permit_data.get('risk_mitigation_actions', []),
            detected_risks,
            implicit_risks
        )
        
        # GARANTISCI sempre che ci siano raccomandazioni se necessario
        if not self._generate_recommendations(detected_risks, implicit_risks):
            recommendations = ["Verificare procedure standard sicurezza applicabili"]
        else:
            recommendations = self._generate_recommendations(detected_risks, implicit_risks)
        
        # ASSICURA sempre identificazione problemi se ci sono rischi
        problems_identified = []
        if detected_risks:
            problems_identified.append(f"Identificati {len(detected_risks)} tipi di rischio")
        if implicit_risks:
            problems_identified.append(f"Rilevati {len(implicit_risks)} rischi impliciti")
        if mitigation_evaluation.get('gaps'):
            problems_identified.extend(mitigation_evaluation['gaps'])
        
        if not problems_identified:
            problems_identified = ["Analisi completata - verificare applicabilità misure standard"]
        
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
            "recommendations": recommendations,
            "problems_identified": problems_identified,
            "mitigation_evaluation": mitigation_evaluation,
            "analysis_always_complete": True
        }
    
    def _extract_main_activity(self, permit_data: Dict[str, Any]) -> str:
        """Extract and interpret the main activity with better context awareness"""
        title = permit_data.get('title', '')
        work_type = permit_data.get('work_type', '')
        description = permit_data.get('description', '')
        
        # Combine all text for better understanding
        full_context = f"{title} {description} {work_type}".lower()
        
        # Check for mechanical maintenance first (most common)
        if any(term in full_context for term in ["sostituzione", "replacement", "cambio", "change"]):
            if any(part in full_context for part in ["rotore", "rotor", "motore", "engine", "riduttore", "gearbox"]):
                return "Manutenzione meccanica - sostituzione componenti"
        
        # Check for specific equipment names that are NOT actions
        if "taglierina" in full_context:
            return "Manutenzione taglierina (equipaggiamento meccanico)"
        
        # Then check for actual repair work
        if "repair" in full_context or "riparazione" in full_context:
            # Only suggest hot work if there's actual evidence
            if self._validate_context("hot_work", full_context, ["repair"]):
                if "pipe" in full_context or "tub" in full_context:
                    return "Riparazione tubazioni (verificare necessità lavori a caldo)"
                elif "tank" in full_context:
                    return "Riparazione serbatoio (verificare spazio confinato e lavori a caldo)"
            else:
                return "Riparazione/manutenzione generale"
        
        # Standard maintenance
        if "maintenance" in work_type.lower() or "manutenzione" in work_type.lower():
            return "Manutenzione impianti"
        
        # Inspection work
        if "inspection" in full_context or "ispezione" in full_context:
            return "Ispezione (verificare accessi e spazi)"
        
        return title if title else "Attività da specificare meglio"
    
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
    
    def _evaluate_mitigation_actions(self, mitigation_actions, detected_risks: Dict, implicit_risks: List) -> Dict[str, Any]:
        """Evaluate if risk mitigation actions are adequate and compliant"""
        
        evaluation = {
            "adequacy": "insufficiente",
            "compliance": "non_conforme",
            "gaps": [],
            "strengths": [],
            "score": 0.0
        }
        
        # Convert to list if string
        if isinstance(mitigation_actions, str):
            mitigation_actions = [mitigation_actions] if mitigation_actions else []
        
        if not mitigation_actions or mitigation_actions == ['Non specificate']:
            evaluation["gaps"].append("Nessuna azione di mitigazione specificata")
            evaluation["adequacy"] = "assente"
            return evaluation
        
        # Combine all mitigation actions text
        mitigation_text = ' '.join(mitigation_actions).lower()
        
        # Check for specific mitigations for each detected risk
        covered_risks = []
        
        # Hot work specific mitigations
        if "hot_work" in detected_risks:
            if any(term in mitigation_text for term in ["fire watch", "estintore", "permesso fuoco", "hot work permit"]):
                covered_risks.append("hot_work")
                evaluation["strengths"].append("Fire watch/estintori previsti per lavori a caldo")
            else:
                evaluation["gaps"].append("Mancano misure specifiche per lavori a caldo (fire watch, estintori)")
        
        # Confined space specific mitigations
        if "confined_space" in detected_risks:
            if any(term in mitigation_text for term in ["gas test", "ventilazione", "rescue", "salvataggio", "monitoraggio atmosfera"]):
                covered_risks.append("confined_space")
                evaluation["strengths"].append("Monitoraggio atmosfera/ventilazione previsti per spazi confinati")
            else:
                evaluation["gaps"].append("Mancano misure per spazi confinati (gas test, ventilazione, rescue plan)")
        
        # Height work specific mitigations
        if "height" in detected_risks:
            if any(term in mitigation_text for term in ["imbracatura", "harness", "parapetto", "ponteggio", "anticaduta"]):
                covered_risks.append("height")
                evaluation["strengths"].append("Protezioni anticaduta previste per lavori in quota")
            else:
                evaluation["gaps"].append("Mancano protezioni anticaduta per lavori in quota")
        
        # Electrical specific mitigations
        if "electrical" in detected_risks:
            if any(term in mitigation_text for term in ["lockout", "tagout", "loto", "isolamento", "messa a terra"]):
                covered_risks.append("electrical")
                evaluation["strengths"].append("LOTO/isolamento previsti per lavori elettrici")
            else:
                evaluation["gaps"].append("Mancano procedure LOTO per lavori elettrici")
        
        # Chemical specific mitigations
        if "chemical" in detected_risks:
            if any(term in mitigation_text for term in ["sds", "scheda sicurezza", "neutralizzante", "assorbente", "kit sversamento"]):
                covered_risks.append("chemical")
                evaluation["strengths"].append("Gestione sostanze chimiche prevista")
            else:
                evaluation["gaps"].append("Mancano misure per gestione sostanze chimiche")
        
        # Calculate coverage score
        total_risks = len(detected_risks) + len(implicit_risks)
        if total_risks > 0:
            coverage = len(covered_risks) / len(detected_risks) if detected_risks else 0
            evaluation["score"] = coverage
            
            if coverage >= 0.8:
                evaluation["adequacy"] = "adeguata"
                evaluation["compliance"] = "conforme"
            elif coverage >= 0.5:
                evaluation["adequacy"] = "parziale"
                evaluation["compliance"] = "parzialmente_conforme"
            else:
                evaluation["adequacy"] = "insufficiente"
                evaluation["compliance"] = "non_conforme"
        
        # Check for general good practices
        if any(term in mitigation_text for term in ["formazione", "training", "supervisione", "briefing"]):
            evaluation["strengths"].append("Formazione/supervisione prevista")
        
        if any(term in mitigation_text for term in ["emergenza", "emergency", "evacuazione"]):
            evaluation["strengths"].append("Procedure di emergenza previste")
        
        return evaluation
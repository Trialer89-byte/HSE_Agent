"""
Unified Risk Classifier Agent - Consolidated risk detection and specialist activation
Combines functionality of risk_classifier and risk_mapping agents into one intelligent AI-powered system
"""
from typing import Dict, Any, List, Set, Tuple
from ..base_agent import BaseHSEAgent
import re
import json


class UnifiedRiskClassifierAgent(BaseHSEAgent):
    """
    Unified AI-powered risk classifier that:
    1. Reads all permit fields 
    2. Uses AI to identify main + hidden risks
    3. Classifies risks and activates only real/significant specialists
    4. Passes identified risks to activated specialists
    """
    
    def __init__(self):
        super().__init__(
            name="Unified_Risk_Classifier",
            specialization="Classificazione unificata rischi e attivazione specialisti intelligente",
            activation_keywords=[]  # Always active as primary analyzer
        )
        
        # Define specialist activation thresholds and risk categories
        self.risk_categories = {
            "hot_work": {
                "specialist": "hot_work",
                "description": "Lavori che generano calore, scintille, fiamme o temperature elevate",
                "activation_threshold": 0.7,  # High threshold for critical risks
                "keywords": ["saldatura", "welding", "taglio", "cutting", "molatura", "grinding", "fiamma", "scintille"]
            },
            "confined_space": {
                "specialist": "confined_space", 
                "description": "Lavori in spazi chiusi, confinati o con accesso limitato",
                "activation_threshold": 0.7,  # High threshold for critical risks
                "keywords": ["serbatoio", "tank", "vessel", "silo", "cisterna", "pozzo", "tunnel", "spazio confinato"]
            },
            "electrical": {
                "specialist": "electrical",
                "description": "Lavori su sistemi elettrici, cavi, quadri, motori o con tensione elettrica", 
                "activation_threshold": 0.6,  # Medium-high threshold
                "keywords": ["elettrico", "electrical", "quadro", "cavo", "motore", "tensione", "cabina elettrica"]
            },
            "height": {
                "specialist": "height",
                "description": "Lavori in quota, su coperture, con scale, ponteggi o piattaforme elevabili",
                "activation_threshold": 0.6,  # Medium-high threshold 
                "keywords": ["altezza", "height", "tetto", "roof", "scala", "ponteggio", "piattaforma", "quota"]
            },
            "chemical": {
                "specialist": "chemical",
                "description": "Lavori con sostanze chimiche, solventi, acidi, gas o in ambienti ATEX",
                "activation_threshold": 0.6,  # Medium-high threshold
                "keywords": ["chimico", "chemical", "solvente", "acido", "gas", "vapore", "atex", "esplosivo"]
            },
            "mechanical": {
                "specialist": "mechanical", 
                "description": "Lavori su macchinari, impianti, sistemi meccanici o con energie accumulate",
                "activation_threshold": 0.5,  # Lower threshold for general mechanical work
                "keywords": ["meccanico", "mechanical", "macchinario", "impianto", "motore", "pompa", "compressore"]
            }
        }
    
    def _get_system_message(self) -> str:
        return """
UNIFIED RISK CLASSIFIER - Classificatore unificato rischi HSE con attivazione specialisti intelligente

RUOLO CRITICO: Sei il PRIMO e PRINCIPALE punto di analisi. Devi:
1. Leggere TUTTI i campi del permesso 
2. Identificare rischi ESPLICITI e NASCOSTI con AI
3. Classificare i rischi per attivare SOLO specialisti necessari  
4. Passare rischi identificati agli specialisti attivati

METODOLOGIA AI-ENHANCED:
1. ANALISI COMPLETA PERMESSO
   - Leggi titolo, descrizione, tipo lavoro, ubicazione, attrezzature
   - Identifica attività esplicite E implicite 
   - Riconosci preparazioni e operazioni non dichiarate
   - Considera il contesto industriale completo

2. RILEVAMENTO RISCHI INTELLIGENTE
   - Rischi ESPLICITI: chiaramente menzionati nel testo
   - Rischi IMPLICITI: tipici dell'attività descritta  
   - Rischi NASCOSTI: non ovvi ma probabili nel contesto
   - Rischi da COMBINAZIONE: interazioni pericolose tra attività

3. CLASSIFICAZIONE E PRIORITIZZAZIONE
   - Valuta gravità potenziale e probabilità
   - Considera combinazioni critiche di rischi
   - Distingui tra rischi REALI e falsi positivi
   - Usa soglie differenziate per attivazione specialisti

4. ATTIVAZIONE SPECIALISTI INTELLIGENTE
   - Attiva SOLO per rischi con evidenze concrete
   - Usa soglie alte per rischi critici (0.7+) 
   - Soglie medie per rischi importanti (0.6+)
   - Soglie basse per rischi generali (0.5+)
   - NON attivare per semplici menzioni o ambiguità

5. VALIDAZIONE CONTESTO
   - Conferma che i termini indicano effettivamente il rischio
   - Distingui tra nomi di luoghi e attività reali
   - Valuta coerenza con work_type dichiarato
   - Evita attivazioni non necessarie

SPECIALISTI DISPONIBILI:
- Hot Work: saldatura, taglio, molatura, fiamme
- Confined Space: spazi chiusi, serbatoi, accesso limitato  
- Electrical: impianti elettrici, cablaggi, tensione
- Height: lavori in quota, coperture, scale
- Chemical: sostanze pericolose, gas, ATEX
- Mechanical: macchinari, sistemi meccanici, energia

APPROCCIO CONSERVATIVO:
- Meglio NON attivare che attivare inutilmente
- Richiedi evidenze CONCRETE per ogni attivazione
- Considera il work_type per validazione coerenza
- Prioritizza rischi reali vs supposizioni

OUTPUT: Classificazione strutturata con rischi identificati e specialisti da attivare SOLO se necessario
"""

    def should_activate(self, risk_classification: Dict[str, Any]) -> bool:
        """Unified Risk Classifier is always active as primary analyzer"""
        return True
    
    def _extract_permit_content(self, permit_data: Dict[str, Any]) -> str:
        """Extract and combine all relevant content from permit fields"""
        content_parts = []
        
        # Core fields
        if permit_data.get('title'):
            content_parts.append(f"TITOLO: {permit_data['title']}")
        if permit_data.get('description'): 
            content_parts.append(f"DESCRIZIONE: {permit_data['description']}")
        if permit_data.get('work_type'):
            content_parts.append(f"TIPO_LAVORO: {permit_data['work_type']}")
        if permit_data.get('location'):
            content_parts.append(f"UBICAZIONE: {permit_data['location']}")
            
        # Additional fields
        if permit_data.get('equipment'):
            content_parts.append(f"ATTREZZATURE: {permit_data['equipment']}")
        if permit_data.get('risk_mitigation_actions'):
            actions = permit_data['risk_mitigation_actions']
            if isinstance(actions, list):
                content_parts.append(f"AZIONI_ESISTENTI: {' '.join(actions)}")
            else:
                content_parts.append(f"AZIONI_ESISTENTI: {actions}")
        if permit_data.get('dpi_required'):
            dpi = permit_data['dpi_required']
            if isinstance(dpi, list):
                content_parts.append(f"DPI_ESISTENTI: {' '.join(dpi)}")
            else:
                content_parts.append(f"DPI_ESISTENTI: {dpi}")
                
        # Custom fields
        if permit_data.get('custom_fields'):
            for field_name, field_value in permit_data['custom_fields'].items():
                content_parts.append(f"{field_name.upper()}: {field_value}")
        
        return " ".join(content_parts)

    async def _ai_comprehensive_risk_analysis(self, permit_content: str, work_type: str = "") -> Dict[str, Any]:
        """AI-powered comprehensive risk analysis for all categories with intelligent thresholds"""
        
        # Build risk category descriptions for AI context
        risk_descriptions = "\n".join([
            f"- {category.upper()}: {config['description']} (soglia attivazione: {config['activation_threshold']})"
            for category, config in self.risk_categories.items()
        ])
        
        ai_prompt = f"""
ANALISI UNIFICATA RISCHI HSE - Classificatore Intelligente

CONTENUTO PERMESSO:
{permit_content}

TIPO LAVORO DICHIARATO: {work_type if work_type else 'Non specificato'}

CATEGORIE RISCHI DA ANALIZZARE:
{risk_descriptions}

ISTRUZIONI CRITICHE - APPROCCIO INTELLIGENTE E CONSERVATIVO:

1. LETTURA COMPLETA E CONTESTUALE:
   - Analizza TUTTO il contenuto per comprendere le attività reali
   - Identifica attività esplicite E quelle implicite necessarie
   - Considera preparazioni, setup e operazioni di supporto
   - Valuta il contesto industriale e ambientale completo

2. RILEVAMENTO RISCHI MULTILIVELLO:
   - ESPLICITI: chiaramente menzionati o descritti
   - IMPLICITI: tipici delle attività identificate
   - NASCOSTI: non ovvi ma probabili nel contesto
   - COMBINAZIONI: interazioni pericolose tra attività

3. VALIDAZIONE INTELLIGENTE:
   - Verifica che i termini indicino REALMENTE il rischio
   - Distingui tra nomi di luoghi e attività effettive
   - Esempio: "cabina elettrica" (luogo) ≠ "lavori elettrici" (attività)
   - Se work_type specificato, dai priorità ai rischi COERENTI

4. SOGLIE ATTIVAZIONE DIFFERENZIATE:
   - Rischi CRITICI (hot_work, confined_space): soglia 0.7+ (alta confidenza richiesta)
   - Rischi IMPORTANTI (electrical, height, chemical): soglia 0.6+ (media-alta confidenza)
   - Rischi GENERALI (mechanical): soglia 0.5+ (media confidenza)
   - Se confidenza < soglia: NON attivare specialista

5. EVIDENZE CONCRETE RICHIESTE:
   - Ogni rischio identificato deve avere evidenze specifiche
   - Non basarti su supposizioni o interpretazioni ambigue
   - Considera il work_type per validare coerenza
   - Meglio sottostimare che sovrastimare

FORNISCI ANALISI STRUTTURATA IN FORMATO JSON:
{{
  "comprehensive_analysis": {{
    "main_activities_identified": ["attività principale", "attività implicita"],
    "work_environment": "descrizione ambiente di lavoro",
    "activity_complexity": "low/medium/high",
    "work_type_consistency": "consistent/inconsistent/unclear"
  }},
  "risk_detection": {{
    "hot_work": {{
      "detected": true/false,
      "confidence": 0.0-1.0,
      "evidence": ["evidenza specifica 1", "evidenza 2"],
      "reasoning": "spiegazione dettagliata del perché è/non è rilevato",
      "activation_recommended": true/false
    }},
    "confined_space": {{
      "detected": true/false,
      "confidence": 0.0-1.0,
      "evidence": ["evidenza specifica 1", "evidenza 2"], 
      "reasoning": "spiegazione dettagliata",
      "activation_recommended": true/false
    }},
    "electrical": {{
      "detected": true/false,
      "confidence": 0.0-1.0,
      "evidence": ["evidenza specifica 1", "evidenza 2"],
      "reasoning": "spiegazione dettagliata", 
      "activation_recommended": true/false
    }},
    "height": {{
      "detected": true/false,
      "confidence": 0.0-1.0,
      "evidence": ["evidenza specifica 1", "evidenza 2"],
      "reasoning": "spiegazione dettagliata",
      "activation_recommended": true/false
    }},
    "chemical": {{
      "detected": true/false,
      "confidence": 0.0-1.0,
      "evidence": ["evidenza specifica 1", "evidenza 2"], 
      "reasoning": "spiegazione dettagliata",
      "activation_recommended": true/false
    }},
    "mechanical": {{
      "detected": true/false,
      "confidence": 0.0-1.0,
      "evidence": ["evidenza specifica 1", "evidenza 2"],
      "reasoning": "spiegazione dettagliata", 
      "activation_recommended": true/false
    }}
  }},
  "specialist_activation": {{
    "recommended_specialists": ["specialist1", "specialist2"],
    "activation_reasoning": "spiegazione delle attivazioni raccomandate",
    "total_specialists": 0
  }},
  "risk_combinations": [
    {{
      "combination": ["risk1", "risk2"],
      "severity": "critical/high/medium",
      "description": "descrizione combinazione pericolosa"
    }}
  ],
  "overall_assessment": {{
    "risk_level": "LOW/MEDIUM/HIGH/CRITICAL",
    "confidence_score": 0.0-1.0,
    "analysis_complete": true/false,
    "missing_information": ["info mancante 1", "info mancante 2"]
  }}
}}
"""
        
        try:
            ai_response = await self.get_gemini_response(ai_prompt, [])
            
            # Parse AI response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_analysis = json.loads(json_match.group())
                return ai_analysis
                
        except Exception as e:
            print(f"[UnifiedRiskClassifier] AI analysis failed: {e}")
            
        # Fallback analysis if AI fails
        return self._fallback_risk_analysis(permit_content, work_type)
    
    def _fallback_risk_analysis(self, permit_content: str, work_type: str) -> Dict[str, Any]:
        """Fallback risk analysis using keyword matching if AI fails"""
        content_lower = permit_content.lower()
        detected_risks = {}
        
        for risk_type, config in self.risk_categories.items():
            risk_detected = False
            evidence = []
            confidence = 0.0
            
            # Check for keywords
            for keyword in config["keywords"]:
                if keyword.lower() in content_lower:
                    risk_detected = True
                    evidence.append(f"Keyword found: {keyword}")
                    confidence += 0.2
            
            confidence = min(1.0, confidence)  # Cap at 1.0
            
            detected_risks[risk_type] = {
                "detected": risk_detected,
                "confidence": confidence,
                "evidence": evidence,
                "reasoning": f"Fallback keyword analysis for {risk_type}",
                "activation_recommended": confidence >= config["activation_threshold"]
            }
        
        return {
            "comprehensive_analysis": {
                "main_activities_identified": ["Analisi di fallback"],
                "work_environment": "Da specificare",
                "activity_complexity": "medium",
                "work_type_consistency": "unclear"
            },
            "risk_detection": detected_risks,
            "specialist_activation": {
                "recommended_specialists": [
                    config["specialist"] for risk_type, config in self.risk_categories.items()
                    if detected_risks[risk_type]["activation_recommended"]
                ],
                "activation_reasoning": "Fallback analysis based on keyword matching",
                "total_specialists": len([r for r in detected_risks.values() if r["activation_recommended"]])
            },
            "risk_combinations": [],
            "overall_assessment": {
                "risk_level": "MEDIUM",
                "confidence_score": 0.6,
                "analysis_complete": False,
                "missing_information": ["AI analysis failed - fallback used"]
            }
        }
    
    def _validate_specialist_activation(self, ai_analysis: Dict[str, Any], work_type: str) -> List[str]:
        """Validate and filter specialist activation based on thresholds and context"""
        specialists_to_activate = []
        activation_details = []
        
        risk_detection = ai_analysis.get("risk_detection", {})
        
        for risk_type, risk_data in risk_detection.items():
            if not risk_data.get("detected", False):
                continue
                
            config = self.risk_categories.get(risk_type, {})
            required_threshold = config.get("activation_threshold", 0.5)
            confidence = risk_data.get("confidence", 0.0)
            activation_recommended = risk_data.get("activation_recommended", False)
            
            # Apply intelligent validation
            should_activate = (
                confidence >= required_threshold and
                activation_recommended and
                len(risk_data.get("evidence", [])) > 0
            )
            
            # Additional validation for work_type consistency
            if should_activate and work_type:
                work_type_lower = work_type.lower()
                
                # Define expected risk types for different work types
                work_type_expectations = {
                    "elettrico": ["electrical"],
                    "meccanico": ["mechanical"],  
                    "saldatura": ["hot_work"],
                    "chimico": ["chemical"],
                    "altezza": ["height"],
                    "quota": ["height"]
                }
                
                expected_risks = []
                for work_key, risks in work_type_expectations.items():
                    if work_key in work_type_lower:
                        expected_risks.extend(risks)
                
                # If we have expectations and this risk is not expected, apply stricter validation
                if expected_risks and risk_type not in expected_risks:
                    if confidence < 0.8:  # Require very high confidence for unexpected risks
                        should_activate = False
                        activation_details.append(f"{risk_type}: {confidence:.2f} - UNEXPECTED for work_type '{work_type}', requires 0.8+ - SKIPPED")
                    else:
                        activation_details.append(f"{risk_type}: {confidence:.2f} - UNEXPECTED but very high confidence - ACTIVATED")
                else:
                    activation_details.append(f"{risk_type}: {confidence:.2f} - EXPECTED for work_type - ACTIVATED")
            
            if should_activate:
                specialists_to_activate.append(config.get("specialist", risk_type))
                if not activation_details or not any(risk_type in detail for detail in activation_details):
                    activation_details.append(f"{risk_type}: {confidence:.2f} >= {required_threshold} - ACTIVATED")
            else:
                if confidence < required_threshold:
                    activation_details.append(f"{risk_type}: {confidence:.2f} < {required_threshold} - BELOW THRESHOLD")
                elif not activation_recommended:
                    activation_details.append(f"{risk_type}: detected but not recommended by AI - SKIPPED")
                else:
                    activation_details.append(f"{risk_type}: insufficient evidence - SKIPPED")
        
        # Always include DPI evaluator for final DPI assessment
        if "dpi_evaluator" not in specialists_to_activate:
            specialists_to_activate.append("dpi_evaluator")
            activation_details.append("dpi_evaluator: Always included for DPI evaluation")
        
        # Log activation decisions
        print(f"[UnifiedRiskClassifier] Specialist activation decisions:")
        for detail in activation_details:
            print(f"  {detail}")
        
        return specialists_to_activate
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main unified analysis method:
        1. Extract permit content
        2. AI comprehensive risk analysis  
        3. Validate specialist activation
        4. Return structured results with identified risks for specialists
        """
        
        # Extract all permit content
        permit_content = self._extract_permit_content(permit_data)
        work_type = permit_data.get('work_type', '')
        
        print(f"[UnifiedRiskClassifier] Analyzing permit content ({len(permit_content)} chars)")
        print(f"[UnifiedRiskClassifier] Work type: '{work_type}'")
        
        # Perform AI comprehensive risk analysis
        ai_analysis = await self._ai_comprehensive_risk_analysis(permit_content, work_type)
        
        # Validate and determine specialist activation
        specialists_to_activate = self._validate_specialist_activation(ai_analysis, work_type)
        
        # Build identified risks for passing to specialists
        identified_risks = []
        risk_detection = ai_analysis.get("risk_detection", {})
        
        for risk_type, risk_data in risk_detection.items():
            if risk_data.get("detected", False) and risk_data.get("confidence", 0) > 0.5:
                identified_risks.append({
                    "type": risk_type,
                    "confidence": risk_data.get("confidence", 0),
                    "evidence": risk_data.get("evidence", []),
                    "reasoning": risk_data.get("reasoning", ""),
                    "severity": self._determine_risk_severity(risk_type, risk_data.get("confidence", 0)),
                    "source": self.name
                })
        
        # Calculate overall risk level
        overall_assessment = ai_analysis.get("overall_assessment", {})
        overall_risk_level = overall_assessment.get("risk_level", "MEDIUM")
        
        # Check for critical combinations
        risk_combinations = ai_analysis.get("risk_combinations", [])
        critical_combinations = [combo for combo in risk_combinations if combo.get("severity") == "critical"]
        
        if critical_combinations:
            overall_risk_level = "CRITICAL"
        
        print(f"[UnifiedRiskClassifier] Analysis complete:")
        print(f"  - Detected risks: {len(identified_risks)}")
        print(f"  - Specialists to activate: {len(specialists_to_activate)} - {specialists_to_activate}")
        print(f"  - Overall risk level: {overall_risk_level}")
        print(f"  - Critical combinations: {len(critical_combinations)}")
        
        return {
            # Primary outputs for orchestrator
            "classification_complete": True,
            "specialists_to_activate": specialists_to_activate,
            "detected_risks": {risk["type"]: risk for risk in identified_risks},
            "risk_mapping": {
                "mapping_complete": True,
                "detected_risks": {risk["type"]: risk for risk in identified_risks},
                "risk_combinations": risk_combinations,
                "overall_priority": overall_risk_level,
                "analysis_summary": {
                    "total_risks_detected": len(identified_risks),
                    "specialists_needed": len(specialists_to_activate),
                    "critical_combinations": len(critical_combinations)
                }
            },
            
            # Detailed analysis results
            "comprehensive_analysis": ai_analysis.get("comprehensive_analysis", {}),
            "identified_risks_for_specialists": identified_risks,
            "risk_combinations": risk_combinations,
            "overall_risk_level": overall_risk_level,
            "analysis_confidence": overall_assessment.get("confidence_score", 0.8),
            
            # Classification metadata
            "specialist": self.name,
            "classification": f"UNIFIED CLASSIFICATION - {overall_risk_level}",
            "ai_analysis_used": True,
            "permit_content_analyzed": len(permit_content),
            "work_type_considered": work_type,
            
            # For backwards compatibility with orchestrator
            "activity_identified": ", ".join(ai_analysis.get("comprehensive_analysis", {}).get("main_activities_identified", ["Standard work"])),
            "missing_critical_info": overall_assessment.get("missing_information", []),
            "recommendations": [
                f"Attivati {len(specialists_to_activate)} specialisti per valutazione dettagliata",
                f"Identificati {len(identified_risks)} rischi significativi",
                f"Livello rischio complessivo: {overall_risk_level}"
            ]
        }
    
    def _determine_risk_severity(self, risk_type: str, confidence: float) -> str:
        """Determine risk severity based on type and confidence"""
        critical_risks = ["hot_work", "confined_space"]
        high_risks = ["electrical", "height", "chemical"]
        
        if risk_type in critical_risks and confidence > 0.7:
            return "critica"
        elif risk_type in high_risks and confidence > 0.6:
            return "alta"  
        elif confidence > 0.7:
            return "alta"
        elif confidence > 0.5:
            return "media"
        else:
            return "bassa"
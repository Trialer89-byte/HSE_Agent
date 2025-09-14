"""
DPI Evaluator Agent - Specialista nella valutazione e raccomandazione DPI
"""
from typing import Dict, Any, List
from ..base_agent import BaseHSEAgent


class DPIEvaluatorAgent(BaseHSEAgent):
    """AI-powered specialist agent for PPE evaluation and recommendations based on identified risks"""
    
    def __init__(self):
        super().__init__(
            name="DPI_Evaluator",
            specialization="Valutazione e Raccomandazione DPI secondo normative",
            activation_keywords=[]  # Always activated by orchestrator
        )
    
    def _get_system_message(self) -> str:
        return """
ESPERTO DPI - Valutatore e consulente per Dispositivi di Protezione Individuale secondo normative.

COMPETENZE PRINCIPALI:
1. VALUTAZIONE RISCHI-DPI
   - Analisi rischi identificati nel permesso
   - Mappatura rischio → DPI richiesto
   - Verifica completezza protezioni
   - Identificazione lacune nella protezione

2. CONFORMITÀ NORMATIVA
   - D.Lgs 81/08 Titolo III Capo II
   - Norme EN/ISO specifiche per categoria
   - Marcatura CE e categorie DPI (I, II, III)
   - Obblighi formazione per DPI categoria III

3. SELEZIONE TECNICA DPI
   Per ogni rischio identificato:
   - Tipo specifico di DPI
   - Norma tecnica di riferimento (EN/ISO)
   - Livello di protezione richiesto
   - Caratteristiche tecniche minime

4. VERIFICA COMPATIBILITÀ
   - Interferenze tra DPI diversi
   - Comfort e ergonomia
   - Durata e manutenzione
   - Costi-benefici

5. PRIORITIZZAZIONE
   - DPI OBBLIGATORI (per legge)
   - DPI CRITICI (rischio grave)
   - DPI RACCOMANDATI (comfort/efficienza)
   - DPI OPZIONALI (miglioramento)

ANALISI RICHIESTA:
1. Confronta DPI forniti nel permesso vs rischi identificati
2. Identifica DPI mancanti o inadeguati
3. Specifica normativa per ogni DPI
4. Fornisci livello protezione richiesto
5. Segnala incompatibilità tra DPI

OUTPUT STRUTTURATO:
- Gap analysis (cosa manca)
- DPI obbligatori con normative
- DPI raccomandati con giustificazione
- Formazione richiesta (DPI cat. III)
- Verifiche periodiche necessarie
"""
    
    def should_activate(self, risk_classification: Dict[str, Any]) -> bool:
        """DPI Evaluator should always activate after risk identification"""
        return True  # Always evaluate DPI after risks are identified
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered PPE evaluation based on comprehensive risk analysis"""
        
        # Get existing DPI from permit and detected risks from context
        existing_dpi = permit_data.get("dpi_required", [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        
        # Get detected risks from Risk Mapping Agent
        classification = context.get("classification", {})
        risk_mapping = classification.get("risk_mapping", {})
        detected_risks = risk_mapping.get("detected_risks", {})
        
        # Extract electrical risk information directly from risk mapping
        electrical_risk_info = self._extract_electrical_risk_from_mapping(detected_risks, permit_data)
        
        # Get specialist results for additional context (but don't depend on them)
        specialist_results = context.get("specialist_results", {})
        additional_electrical_context = {}
        if "electrical_specialist" in specialist_results:
            additional_electrical_context = specialist_results["electrical_specialist"].get("electrical_context_for_dpi", {})
        
        # Get available documents for context
        available_docs = context.get("documents", [])
        
        # Search for DPI-specific documents
        try:
            tenant_id = context.get("user_context", {}).get("tenant_id", 1)
            dpi_docs = await self.search_specialized_documents(
                query=f"DPI dispositivi protezione {permit_data.get('title', '')} {permit_data.get('description', '')}",
                tenant_id=tenant_id,
                limit=3
            )
            all_docs = available_docs + dpi_docs
        except Exception as e:
            print(f"[{self.name}] Document search failed: {e}")
            all_docs = available_docs
        
        # Create comprehensive AI analysis prompt with risk-based electrical analysis
        detected_risks_summary = ", ".join(detected_risks.keys()) if detected_risks else "Nessun rischio specifico identificato"
        
        # Build electrical context from risk mapping (primary) and specialist (secondary)
        electrical_info = ""
        if electrical_risk_info["has_electrical_risk"]:
            voltage_info = electrical_risk_info.get("voltage_level", "sconosciuto")
            confidence = electrical_risk_info.get("confidence", 0.0)
            electrical_details = electrical_risk_info.get("risk_details", [])
            
            # Combine with specialist info if available
            if additional_electrical_context and additional_electrical_context.get("voltage_level"):
                voltage_info = additional_electrical_context.get("voltage_level", voltage_info)
            
            electrical_info = f"""
RISCHIO ELETTRICO IDENTIFICATO DAL RISK MAPPING:
- Presenza lavori elettrici: SÌ (confidenza: {confidence:.1f})
- Livello tensione stimato: {voltage_info}
- Dettagli rischio elettrico: {', '.join(electrical_details) if electrical_details else 'Rischio elettrico generico'}
- Fonte primaria: Risk Mapping Agent
{f"- Contesto aggiuntivo specialista: {additional_electrical_context}" if additional_electrical_context else ""}
"""
        elif additional_electrical_context:
            # Fallback to specialist context if risk mapping didn't detect electrical risk
            voltage_level = additional_electrical_context.get("voltage_level", "unknown")
            electrical_risks = additional_electrical_context.get("electrical_risks", [])
            electrical_info = f"""
CONTESTO ELETTRICO DA SPECIALISTA:
- Livello tensione identificato: {voltage_level}
- Rischi elettrici specifici: {', '.join(electrical_risks) if electrical_risks else 'Nessun rischio specifico'}
- Tipo lavoro elettrico: {additional_electrical_context.get('work_type', 'non specificato')}
"""
        
        permit_summary = f"""
PERMESSO DI LAVORO - VALUTAZIONE DPI (Dispositivi di Protezione Individuale):

TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}

RISCHI IDENTIFICATI DAL SISTEMA: {detected_risks_summary}
{electrical_info}
DPI ATTUALMENTE PREVISTI: {existing_dpi if existing_dpi else 'Nessun DPI specificato'}

AZIONI MITIGAZIONE ATTUALI: {existing_actions if existing_actions else 'Nessuna azione specificata'}

VALUTA COMPLETAMENTE I REQUISITI DPI secondo D.Lgs 81/08 e Regolamento UE 2016/425:

1. ANALISI RISCHI SPECIFICI per DPI:
   - Protezione della testa (elmetti EN 397, caschi dielettrici EN 50365)
   - Protezione degli occhi/viso (occhiali EN 166, visiere anti-arco EN 166)
   - Protezione dell'udito (cuffie EN 352, inserti EN 352)
   - Protezione delle vie respiratorie (maschere EN 149, respiratori EN 140)
   - Protezione delle mani/braccia (guanti meccanici EN 388, guanti isolanti EN 60903)
   - Protezione del corpo (indumenti EN ISO 13688, indumenti Arc-rated per arco elettrico)
   - Protezione dei piedi/gambe (calzature EN ISO 20345, calzature isolanti >1000MΩ)
   - Protezione anticaduta (imbracature EN 361, cordini EN 354)

2. ANALISI COMPLETA RISCHI PER DPI SPECIFICI:

   a) RISCHI ELETTRICI (se rilevati dal Risk Mapping o testo):
      IMPORTANTE: Analizzare sempre i rischi elettrici indipendentemente dalla presenza di specialisti:
      
      - BASSISSIMA/BASSA TENSIONE (BT ≤1000V):
        * Guanti isolanti Classe 00 (500V) EN 60903
        * Calzature isolanti con resistenza >1000MΩ
        * Elmetto dielettrico senza parti metalliche EN 50365
        
      - MEDIA TENSIONE (MT 1-30kV):
        * Guanti isolanti Classe 1 (7.5kV) o Classe 2 (17kV) EN 60903
        * Calzature isolanti certificate per MT
        * Elmetto dielettrico classe E EN 50365
        * Visiera anti-arco elettrico
        
      - ALTA TENSIONE (AT >30kV):
        * Guanti isolanti Classe 3 (26.5kV) o Classe 4 (36kV) EN 60903
        * Calzature isolanti certificate per AT
        * Indumenti Arc-rated con ATPV appropriato
        * Visiera e scudi anti-arco completi
        
      - TENSIONE SCONOSCIUTA MA RISCHIO PRESENTE:
        * Guanti isolanti EN 60903 (classe da determinare)
        * Calzature isolanti
        * Elmetto dielettrico EN 50365

   b) RISCHI DA LAVORI IN ALTEZZA:
      - Imbracatura anticaduta EN 361
      - Cordini con assorbitore di energia EN 355
      - Elmetto con sottogola EN 397
      
   c) RISCHI MECCANICI:
      - Guanti anti-taglio EN 388 (livello appropriato)
      - Occhiali di protezione EN 166
      - Scarpe antinfortunistiche S3 EN ISO 20345
      
   d) RISCHI CHIMICI:
      - Guanti resistenti a sostanze chimiche EN 374
      - Respiratori o maschere filtranti EN 149/140
      - Indumenti di protezione chimica EN 14605
      
   e) RISCHI DA CALORE/SALDATURA:
      - Guanti per saldatura EN 12477
      - Visiera per saldatura EN 175
      - Indumenti ignifughi EN ISO 11612

3. CATEGORIE DPI secondo Regolamento UE 2016/425:
   - Categoria I (rischi minimi): DPI semplici
   - Categoria II (rischi significativi): DPI intermedi  
   - Categoria III (rischi mortali/irreversibili): DPI complessi (include DPI elettrici)

4. VALUTAZIONE ADEGUATEZZA DPI ESISTENTI:
   - Corrispondenza ai rischi identificati
   - Conformità normative (marcatura CE, standards EN)
   - Compatibilità tra diversi DPI
   - Stato di manutenzione e integrità

Fornisci risposta ESCLUSIVAMENTE in formato JSON con:
- existing_dpi_adequacy: "adeguati" | "inadeguati" | "parziali"
- missing_dpi: array di stringhe con DPI mancanti (es. "Guanti isolanti EN 60903 classe 1")
- required_training: array di stringhe con formazione richiesta
- normative_compliance: stringa con conformità normative

ESEMPIO FORMATO RISPOSTA:
{{
  "existing_dpi_adequacy": "inadeguati",
  "missing_dpi": ["Guanti isolanti EN 60903", "Elmetto dielettrico EN 50365"],
  "required_training": ["Formazione DPI categoria III", "Addestramento lavori elettrici"],
  "normative_compliance": "D.Lgs 81/08 art. 75-79, UE 2016/425"
}}

NON AGGIUNGERE TESTO PRIMA O DOPO IL JSON.
"""
        
        # Get AI analysis
        try:
            ai_response = await self.get_gemini_response(permit_summary, all_docs)
            
            # Parse AI response
            import json
            import re
            
            # Parse JSON response with robust error handling
            ai_analysis = self._parse_ai_json_response(ai_response)
            if ai_analysis is None:
                print(f"[{self.name}] Failed to parse AI JSON response")
                return self.create_error_response("AI did not provide valid JSON analysis")

            # Extract citations from AI response for document traceability
            citations = self.extract_citations_from_response(ai_response, all_docs)
            
            # Validate response schema
            validation_result = self._validate_dpi_response_schema(ai_analysis)
            if not validation_result["valid"]:
                print(f"[{self.name}] AI response failed schema validation: {validation_result['errors']}")
                # Try to use auto-fixed version if available
                if validation_result.get("auto_fixed"):
                    ai_analysis = validation_result["auto_fixed"]
                    print(f"[{self.name}] Using auto-fixed AI response")
                else:
                    return self.create_error_response(f"AI response schema validation failed: {validation_result['errors']}")
                
        except Exception as e:
            print(f"[{self.name}] AI analysis failed: {e}")
            # Return error - no hardcoded fallback
            return self.create_error_response(str(e))
        
        # Convert AI analysis to standard orchestrator format
        risks_identified = []
        
        if ai_analysis.get("existing_dpi_adequacy") == "inadeguati":
            risks_identified.append({
                "type": "dpi_inadequacy",
                "source": self.name,
                "description": f"DPI inadeguati: mancano {len(ai_analysis.get('missing_dpi', []))} elementi essenziali",
                "severity": "alta"
            })
        elif ai_analysis.get("existing_dpi_adequacy") == "parziali":
            risks_identified.append({
                "type": "dpi_partial",
                "source": self.name,
                "description": "DPI parzialmente adeguati: necessari integrazioni",
                "severity": "media"
            })
        else:
            risks_identified.append({
                "type": "dpi_adequate",
                "source": self.name,
                "description": "DPI attualmente adeguati ai rischi identificati",
                "severity": "bassa"
            })
        
        dpi_requirements = ai_analysis.get("missing_dpi", [])
        
        return {
            "specialist": self.name,
            "classification": f"VALUTAZIONE DPI - Adeguatezza: {str(ai_analysis.get('existing_dpi_adequacy', 'da_valutare')).upper()}",
            "ai_analysis_used": True,
            "risks_identified": risks_identified,
            "dpi_requirements": dpi_requirements,
            "existing_measures_evaluation": {
                "existing_dpi": existing_dpi,
                "existing_actions": existing_actions,
                "dpi_adequacy": str(ai_analysis.get("existing_dpi_adequacy", "da_valutare")).upper(),
                "actions_adequacy": "VALUTAZIONE_DPI_FOCUS",
                "ai_assessment": ai_analysis.get("required_training", []),
                "risk_coverage": ai_analysis.get("existing_dpi_adequacy", "da_valutare")
            },
            "permits_required": ["Certificazione DPI Categoria III"] if ai_analysis.get("required_training") else [],
            "ai_recommendations": ai_analysis.get("normative_compliance", []),
            "citations": citations,  # Add citations for document traceability
            "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
        }
    
    def _extract_electrical_risk_from_mapping(self, detected_risks: Dict[str, Any], permit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract electrical risk information directly from risk mapping results
        """
        electrical_risk_info = {
            "has_electrical_risk": False,
            "voltage_level": "unknown",
            "confidence": 0.0,
            "risk_details": []
        }
        
        # Check if electrical risk is detected by risk mapping
        if "electrical" in detected_risks:
            electrical_risk = detected_risks["electrical"]
            electrical_risk_info["has_electrical_risk"] = True
            electrical_risk_info["confidence"] = electrical_risk.get("confidence", 0.0)
            
            # Extract voltage level information
            description = electrical_risk.get("description", "").lower()
            details = electrical_risk.get("details", [])
            
            # Analyze description and details for voltage clues
            voltage_indicators = {
                "BT": ["bassa tensione", "bt", "230v", "400v", "500v", "1000v", "bassissima"],
                "MT": ["media tensione", "mt", "15kv", "20kv", "30kv", "media"],
                "AT": ["alta tensione", "at", "50kv", "132kv", "alta", "high voltage"]
            }
            
            for voltage, indicators in voltage_indicators.items():
                if any(indicator in description for indicator in indicators):
                    electrical_risk_info["voltage_level"] = voltage
                    break
            
            # Add risk details
            electrical_risk_info["risk_details"] = [description] if description else []
            if details:
                electrical_risk_info["risk_details"].extend([str(d) for d in details[:3]])  # Limit to 3 details
        
        # Secondary check: analyze permit text for electrical keywords
        elif not electrical_risk_info["has_electrical_risk"]:
            permit_text = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('work_type', '')}".lower()
            
            electrical_keywords = [
                "elettric", "tensione", "impianto elettrico", "cabina", "trasformatore",
                "quadro elettrico", "cavo", "conduttore", "interruttore", "presa",
                "collegamento elettrico", "alimentazione", "energia elettrica"
            ]
            
            if any(keyword in permit_text for keyword in electrical_keywords):
                electrical_risk_info["has_electrical_risk"] = True
                electrical_risk_info["confidence"] = 0.6  # Medium confidence from text analysis
                electrical_risk_info["risk_details"] = ["Rischio elettrico identificato dal testo del permesso"]
                
                # Try to infer voltage level from text
                if any(term in permit_text for term in ["cabina", "trasformatore", "mt", "media tensione"]):
                    electrical_risk_info["voltage_level"] = "MT"
                elif any(term in permit_text for term in ["at", "alta tensione", "trasmissione"]):
                    electrical_risk_info["voltage_level"] = "AT"
                elif any(term in permit_text for term in ["presa", "230v", "400v", "domestico", "ufficio"]):
                    electrical_risk_info["voltage_level"] = "BT"
        
        return electrical_risk_info
    
    def _deduplicate_and_optimize_dpi(self, dpi_list: List[str]) -> List[str]:
        """
        Remove duplicates and optimize DPI recommendations for compatibility and coverage
        """
        if not dpi_list:
            return dpi_list
        
        # Group DPI by protection type
        protection_groups = {
            "hand": [],
            "head": [],
            "foot": [],
            "eye_face": [],
            "body": [],
            "respiratory": [],
            "fall": []
        }
        
        # Categorize each DPI item
        for dpi in dpi_list:
            dpi_lower = dpi.lower()
            
            if any(term in dpi_lower for term in ["guant", "glove", "mani"]):
                protection_groups["hand"].append(dpi)
            elif any(term in dpi_lower for term in ["elmetto", "casco", "helmet", "head"]):
                protection_groups["head"].append(dpi)
            elif any(term in dpi_lower for term in ["scarpe", "calzature", "boot", "shoe", "piedi"]):
                protection_groups["foot"].append(dpi)
            elif any(term in dpi_lower for term in ["occhial", "visiera", "goggle", "eye", "face", "viso"]):
                protection_groups["eye_face"].append(dpi)
            elif any(term in dpi_lower for term in ["indument", "tuta", "suit", "body", "corpo"]):
                protection_groups["body"].append(dpi)
            elif any(term in dpi_lower for term in ["respirator", "mask", "ffp", "aria", "respir"]):
                protection_groups["respiratory"].append(dpi)
            elif any(term in dpi_lower for term in ["imbracatura", "harness", "cordini", "anticaduta", "fall"]):
                protection_groups["fall"].append(dpi)
        
        # Select best DPI for each protection group
        optimized_dpi = []
        
        for group_name, group_items in protection_groups.items():
            if not group_items:
                continue
                
            if len(group_items) == 1:
                optimized_dpi.append(group_items[0])
            else:
                # Resolve conflicts by selecting most comprehensive protection
                best_dpi = self._select_best_dpi_for_group(group_name, group_items)
                optimized_dpi.append(best_dpi)
        
        return optimized_dpi
    
    def _select_best_dpi_for_group(self, group_name: str, group_items: List[str]) -> str:
        """
        Select the best DPI from a group when multiple options exist
        """
        # Priority rules for each group
        if group_name == "hand":
            # Electrical protection takes priority over mechanical
            electrical_gloves = [g for g in group_items if "isolanti" in g.lower() or "60903" in g]
            if electrical_gloves:
                # Select highest voltage class if multiple electrical gloves
                highest_class = max(electrical_gloves, key=lambda x: len(x))
                return highest_class
            # Otherwise, select most comprehensive mechanical protection
            return max(group_items, key=lambda x: len(x))
        
        elif group_name == "head":
            # Electrical helmets take priority
            electrical_helmets = [h for h in group_items if "dielettrico" in h.lower() or "50365" in h]
            if electrical_helmets:
                return electrical_helmets[0]
            # Fall protection helmets with chin straps take priority
            fall_helmets = [h for h in group_items if "sottogola" in h.lower()]
            if fall_helmets:
                return fall_helmets[0]
            # Standard safety helmet
            return group_items[0]
        
        elif group_name == "foot":
            # Electrical shoes take priority
            electrical_shoes = [s for s in group_items if "isolanti" in s.lower()]
            if electrical_shoes:
                return electrical_shoes[0]
            # S3 safety shoes for general protection
            s3_shoes = [s for s in group_items if "s3" in s.lower()]
            if s3_shoes:
                return s3_shoes[0]
            # Most comprehensive option
            return max(group_items, key=lambda x: len(x))
        
        else:
            # For other groups, select the most comprehensive option
            return max(group_items, key=lambda x: len(x))
    
    def _parse_ai_json_response(self, ai_response: str):
        """Parse AI JSON response with multiple fallback strategies"""
        import json
        import re
        
        try:
            # Strategy 1: Extract first complete JSON object
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            
            # Strategy 2: Look for JSON between code blocks
            code_block_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response, re.DOTALL | re.IGNORECASE)
            if code_block_match:
                return json.loads(code_block_match.group(1))
            
            # Strategy 3: Extract any JSON-like content
            json_lines = []
            in_json = False
            for line in ai_response.split('\n'):
                line = line.strip()
                if line.startswith('{'):
                    in_json = True
                    json_lines.append(line)
                elif in_json:
                    json_lines.append(line)
                    if line.endswith('}') and '{' not in line:
                        break
            
            if json_lines:
                json_content = '\n'.join(json_lines)
                return json.loads(json_content)
                
        except json.JSONDecodeError as e:
            print(f"[{self.name}] JSON parsing failed: {e}")
        except Exception as e:
            print(f"[{self.name}] Unexpected parsing error: {e}")
        
        return None
    
    def _validate_dpi_response_schema(self, ai_analysis: dict) -> dict:
        """Validate DPI AI response schema with auto-fixing"""
        errors = []
        auto_fixed = ai_analysis.copy()
        
        # Validate existing_dpi_adequacy
        adequacy_options = ["adeguati", "inadeguati", "parziali"]
        if "existing_dpi_adequacy" not in ai_analysis:
            errors.append("Missing required field: existing_dpi_adequacy")
            auto_fixed["existing_dpi_adequacy"] = "da_valutare"
        elif ai_analysis["existing_dpi_adequacy"] not in adequacy_options:
            errors.append(f"Invalid existing_dpi_adequacy value: {ai_analysis['existing_dpi_adequacy']}")
            auto_fixed["existing_dpi_adequacy"] = "da_valutare"
        
        # Validate missing_dpi (must be array)
        if "missing_dpi" not in ai_analysis:
            auto_fixed["missing_dpi"] = []
        elif not isinstance(ai_analysis["missing_dpi"], list):
            if isinstance(ai_analysis["missing_dpi"], str):
                auto_fixed["missing_dpi"] = [ai_analysis["missing_dpi"]]
            else:
                auto_fixed["missing_dpi"] = []
        
        # Validate required_training (must be array)
        if "required_training" not in ai_analysis:
            auto_fixed["required_training"] = []
        elif not isinstance(ai_analysis["required_training"], list):
            if isinstance(ai_analysis["required_training"], str):
                auto_fixed["required_training"] = [ai_analysis["required_training"]]
            else:
                auto_fixed["required_training"] = []
        
        # Validate normative_compliance (must be string)
        if "normative_compliance" not in ai_analysis:
            auto_fixed["normative_compliance"] = "Da valutare"
        elif not isinstance(ai_analysis["normative_compliance"], str):
            auto_fixed["normative_compliance"] = str(ai_analysis["normative_compliance"])
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "auto_fixed": auto_fixed if errors else None
        }
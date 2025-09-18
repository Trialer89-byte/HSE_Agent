"""
Electrical Safety Specialist Agent - AI-powered electrical risk analysis
"""
from typing import Dict, Any, List
from ..base_agent import BaseHSEAgent


class ElectricalSpecialist(BaseHSEAgent):
    """AI-powered specialist for electrical safety and hazards"""
    
    def __init__(self):
        super().__init__(
            name="Electrical_Specialist",
            specialization="Sicurezza Elettrica",
            activation_keywords=[]  # Activated by Risk Mapping Agent
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

COORDINAMENTO DPI:
- NON specificare DPI direttamente (competenza DPI Specialist)
- Fornire solo informazioni tecniche su livello tensione e rischi
- Il DPI Specialist determinerà i dispositivi appropriati

REQUISITI QUALIFICAZIONE:
✓ PES: Persona Esperta (pianifica/supervisiona)
✓ PAV: Persona Avvertita (esegue sotto supervisione)
✓ PEI: Idonea lavori sotto tensione
✓ Formazione CEI 11-27 (14+2 ore min)
✓ Aggiornamento quinquennale
"""
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """AI-powered electrical risk analysis"""
        
        # Get available documents for context
        available_docs = context.get("documents", [])
        user_context = context.get('user_context', {})
        
        # Get existing actions from permit
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        
        # Search for electrical-specific documents
        try:
            tenant_id = user_context.get("tenant_id", 1)
            electrical_docs = await self.search_specialized_documents(
                query=f"elettrico sicurezza CEI tensione {permit_data.get('title', '')} {permit_data.get('description', '')}",
                tenant_id=tenant_id,
                limit=5
            )
            # Deduplicate documents before feeding to AI
            all_docs = self._deduplicate_documents(available_docs + electrical_docs)
        except Exception as e:
            print(f"[{self.name}] Document search failed: {e}")
            all_docs = available_docs
        
        # Get existing actions to check for gaps
        existing_actions_text = str(existing_actions).lower() if existing_actions else ""
        
        # Simplified AI analysis prompt maintaining all essential functionality
        permit_summary = f"""
ANALISI PERMESSO ELETTRICO - PRE-AUTORIZZAZIONE
Permesso NON ANCORA INIZIATO - valuta se approvabile.

DATI PERMESSO:
TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}
AZIONI ESISTENTI: {existing_actions}

ANALISI RICHIESTA (CEI 11-27, CEI EN 50110):

1. RISCHI ELETTRICI:
   - Identifica tensioni (BT/MT/AT), elettrocuzione, arco elettrico, incendio
   - Distingui ATTIVITÀ PRIMARIA (lavoro su impianti) vs ATTREZZATURE (mezzi usati, non sono lo scopo primario del lavoro)
   - Per le ATTREZZATURE considera i rischi associati al loro utilizzo

2. CONTROLLI OBBLIGATORI:
   - LOTO solo per attività su impianti fissi (non attrezzature portatili)
   - Qualifiche PES/PAV/PEI se richieste per attività
   - Verifiche tensione, messe a terra
   - Compatibilità attrezzature con ambiente di lavoro

3. CONTROLLO DUPLICAZIONI:
   - Se azione già presente, NON ripetere
   - Se migliorabile: "MODIFICARE: [dettagli]"
   - Solo azioni mancanti come nuove

IMPORTANTE - NON COMPETENZA DPI:
- NON suggerire DPI specifici
- Esiste DPI Specialist dedicato
- Fornisci solo electrical_context_for_dpi

Rispondi SOLO JSON valido:
{{
  "electrical_risks_detected": ["rischi identificati"],
  "voltage_level": "BT|MT|AT|unknown|none",
  "required_qualifications": ["PES/PAV/PEI se necessarie"],
  "safety_procedures": ["procedure mancanti"],
  "gap_analysis": ["lacune nelle azioni esistenti"],
  "intelligent_recommendations": [{{"action": "azione", "criticality": "alta|media|bassa"}}],
  "electrical_context_for_dpi": {{
    "voltage_level": "stesso di sopra",
    "electrical_risks": ["rischi per DPI"],
    "work_type": "tipo lavoro"
  }}
}}

CRITICALITY: alta=pericolo vita, media=infortunio grave, bassa=procedure incomplete
"""
        
        # Get AI analysis
        try:
            ai_response = await self.get_gemini_response(permit_summary, all_docs)
            
            # Parse AI response
            import json
            import re
            
            # Extract and parse JSON from AI response with robust error handling
            ai_analysis = self._parse_ai_json_response(ai_response)
            if ai_analysis is None:
                print(f"[{self.name}] Failed to parse AI JSON response")
                return self.create_error_response("AI did not provide valid JSON analysis")
            
            # Validate AI response against expected schema (with auto-fixes)
            validation_result = self._validate_ai_response_schema(ai_analysis)
            if not validation_result["valid"]:
                print(f"[{self.name}] AI response failed schema validation after auto-fixes: {validation_result['errors']}")
                return self.create_error_response(f"AI response schema validation failed: {validation_result['errors']}")

            # Extract citations from AI response for document traceability
            citations = self.extract_citations_from_response(ai_response, all_docs)

        except Exception as e:
            print(f"[{self.name}] Analysis failed: {e}")
            # Use standardized error response
            return self.create_error_response(e)
        
        # Convert AI analysis to standard orchestrator format
        risks_identified = []
        
        # Process detected electrical risks
        for risk in ai_analysis.get("electrical_risks_detected", []):
            risks_identified.append({
                "type": "electrical_risk",
                "source": self.name,
                "description": risk,
                "severity": "alta" if "arco" in risk.lower() or "elettrocuzione" in risk.lower() else "media"
            })
        
        # If no electrical risks detected, still provide basic assessment
        if not risks_identified:
            risks_identified.append({
                "type": "no_electrical_risk",
                "source": self.name,
                "description": "Nessun rischio elettrico significativo identificato",
                "severity": "bassa"
            })
        
        safety_procedures = ai_analysis.get("safety_procedures", [])
        qualifications = ai_analysis.get("required_qualifications", [])
        
        # Build classification based on voltage level
        voltage_level = ai_analysis.get("voltage_level", "unknown")
        classification = f"LAVORI ELETTRICI {voltage_level.upper()}" if voltage_level != "unknown" else "VALUTAZIONE ELETTRICA"
        if voltage_level in ["BT", "MT", "AT"]:
            classification += " - CEI 11-27 APPLICABILE"
        
        # Use AI-driven recommendations instead of hardcoded actions
        recommended_actions = self._extract_ai_recommendations(
            ai_analysis,
            existing_actions,
            voltage_level
        )
        
        # Prepare electrical context for DPI Specialist
        electrical_context_for_dpi = ai_analysis.get("electrical_context_for_dpi", {})
        if not electrical_context_for_dpi and voltage_level != "unknown":
            electrical_context_for_dpi = {
                "voltage_level": voltage_level,
                "electrical_risks": [risk["description"] for risk in risks_identified if risk["type"] != "no_electrical_risk"],
                "work_type": "electrical_maintenance" if len(risks_identified) > 0 else "electrical_assessment"
            }

        return {
            "specialist": self.name,
            "classification": classification,
            "ai_analysis_used": True,
            "risks_identified": risks_identified,
            "recommended_actions": recommended_actions,
            "existing_measures_evaluation": {
                "voltage_level_detected": voltage_level,
                "electrical_work_identified": len(ai_analysis.get("electrical_risks_detected", [])) > 0,
                "risk_coverage": "comprehensive" if len(risks_identified) > 1 else "basic"
            },
            "permits_required": ["Permesso Lavori Elettrici"] if voltage_level != "unknown" else [],
            "training_requirements": qualifications,
            "emergency_measures": [
                "Procedura soccorso folgorati (non toccare diretto)",
                "Pulsante emergenza sgancio generale",
                "Kit primo soccorso con coperta termica"
            ] if len(risks_identified) > 0 and risks_identified[0]["type"] != "no_electrical_risk" else [],
            "electrical_context_for_dpi": electrical_context_for_dpi,
            "ai_recommendations": [
                f"Tensione identificata: {voltage_level}",
                f"Qualifiche richieste: {', '.join(qualifications)}",
                "Conformità CEI 11-27 e CEI EN 50110"
            ],
            "citations": citations,  # Add citations for document traceability
            "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
        }

    def _extract_ai_recommendations(
        self,
        ai_analysis: Dict[str, Any],
        existing_actions: List[str],
        voltage_level: str
    ) -> List[Dict[str, Any]]:
        """
        Extract intelligent recommendations from AI analysis based on gap detection
        """
        recommendations = []
        action_id = 1
        
        # Extract AI-driven intelligent recommendations
        intelligent_recs = ai_analysis.get("intelligent_recommendations", [])
        gap_analysis = ai_analysis.get("gap_analysis", [])
        safety_procedures = ai_analysis.get("safety_procedures", [])
        
        # Convert AI recommendations to structured format
        for rec in intelligent_recs:
            if isinstance(rec, dict) and rec.get("action"):
                recommendations.append({
                    "id": action_id,
                    "action": rec.get("action"),
                    "criticality": rec.get("criticality", "media"),
                    "type": "electrical_gap_filling"
                })
                action_id += 1
            elif isinstance(rec, str) and rec.strip():
                recommendations.append({
                    "id": action_id,
                    "action": rec,
                    "criticality": "media",
                    "type": "electrical_gap_filling"
                })
                action_id += 1
        
        # Add safety procedures that are missing
        for proc in safety_procedures:
            if isinstance(proc, dict) and proc.get("action"):
                recommendations.append({
                    "id": action_id,
                    "action": proc.get("action"),
                    "criticality": proc.get("criticality", "alta"),
                    "type": "electrical_procedure"
                })
                action_id += 1
            elif isinstance(proc, str) and proc.strip():
                recommendations.append({
                    "id": action_id,
                    "action": proc,
                    "criticality": "alta",
                    "type": "electrical_procedure"
                })
                action_id += 1
        
        # Add gap analysis findings (only if not already covered by other recommendations)
        existing_actions_text = " ".join([rec.get("action", "").lower() for rec in recommendations])
        for gap in gap_analysis:
            if isinstance(gap, dict) and gap.get("action"):
                gap_text = gap.get("action", "")
                gap_lower = gap_text.lower()
                if not any(keyword in existing_actions_text for keyword in ["loto", "lockout", "isolamento", "sezionamento"] if keyword in gap_lower):
                    recommendations.append({
                        "id": action_id,
                        "action": f"Colmare lacuna identificata: {gap_text}",
                        "criticality": gap.get("criticality", "media"),
                        "type": "electrical_gap_analysis"
                    })
                    action_id += 1
            elif isinstance(gap, str) and gap.strip():
                gap_lower = gap.lower()
                if not any(keyword in existing_actions_text for keyword in ["loto", "lockout", "isolamento", "sezionamento"] if keyword in gap_lower):
                    recommendations.append({
                        "id": action_id,
                        "action": f"Colmare lacuna identificata: {gap}",
                        "criticality": "media",
                        "type": "electrical_gap_analysis"
                    })
                    action_id += 1
        
        # No hardcoded fallback - if AI provides no recommendations, return empty list
        # This ensures all recommendations come from AI analysis
        
        # Limit to maximum 10 actions
        return recommendations[:10]
    
    def _deduplicate_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate documents before feeding to AI to avoid duplicate responses
        """
        if not documents:
            return documents
            
        seen_content = set()
        unique_docs = []
        
        for doc in documents:
            # Use content hash for deduplication
            content = str(doc.get('content', ''))
            title = str(doc.get('title', ''))
            
            # Create a normalized identifier
            doc_key = f"{title}:{content[:200]}"  # Use title + first 200 chars of content
            content_hash = hash(doc_key)
            
            if content_hash not in seen_content:
                seen_content.add(content_hash)
                unique_docs.append(doc)
            else:
                print(f"[{self.name}] Skipped duplicate document: {title[:50]}...")
        
        print(f"[{self.name}] Document deduplication: {len(documents)} -> {len(unique_docs)}")
        return unique_docs
    
    def _validate_ai_response_schema(self, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and auto-fix AI response schema for electrical analysis
        
        This method validates the AI response and attempts to fix common format issues
        like strings instead of lists, missing fields, etc.
        """
        errors = []
        fixed_response = ai_response.copy()
        
        # Define expected schema with optional fields
        required_fields = ["electrical_risks_detected", "voltage_level"]
        optional_fields = [
            "required_qualifications", "safety_procedures", "gap_analysis", 
            "intelligent_recommendations", "electrical_context_for_dpi"
        ]
        
        # Auto-fix common AI response issues
        fixed_response = self._auto_fix_ai_response_format(fixed_response)
        
        # Check required fields exist
        for field in required_fields:
            if field not in fixed_response:
                errors.append(f"Missing required field: {field}")
        
        # Validate and fix data types
        list_fields = ["electrical_risks_detected", "required_qualifications", "safety_procedures", 
                      "gap_analysis", "intelligent_recommendations"]
        
        for field in list_fields:
            if field in fixed_response:
                if not isinstance(fixed_response[field], list):
                    # Try to convert to list
                    if isinstance(fixed_response[field], str):
                        if fixed_response[field].strip():
                            fixed_response[field] = [fixed_response[field]]
                        else:
                            fixed_response[field] = []
                    else:
                        fixed_response[field] = []
        
        # Validate voltage_level with auto-correction
        if "voltage_level" in fixed_response:
            voltage = str(fixed_response["voltage_level"]).upper()
            valid_voltages = ["BT", "MT", "AT", "UNKNOWN", "NONE"]
            
            # Auto-correct common variations
            voltage_mapping = {
                "LOW": "BT", "MEDIUM": "MT", "HIGH": "AT", 
                "BASSA": "BT", "MEDIA": "MT", "ALTA": "AT",
                "UNKNOW": "UNKNOWN", "N/A": "UNKNOWN", "NULL": "UNKNOWN"
            }
            
            if voltage in voltage_mapping:
                fixed_response["voltage_level"] = voltage_mapping[voltage]
            elif voltage not in valid_voltages:
                fixed_response["voltage_level"] = "unknown"
        
        # Ensure electrical_context_for_dpi is a dict
        if "electrical_context_for_dpi" in fixed_response:
            if not isinstance(fixed_response["electrical_context_for_dpi"], dict):
                fixed_response["electrical_context_for_dpi"] = {}
        
        # Update original response with fixed version
        ai_response.update(fixed_response)
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "validated_fields": len(required_fields + optional_fields),
            "auto_fixes_applied": True,
            "schema_version": "electrical_v2.0_flexible"
        }
    
    def _auto_fix_ai_response_format(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-fix common AI response format issues
        """
        # Provide defaults for missing optional fields
        if "safety_procedures" not in response:
            response["safety_procedures"] = []
        if "intelligent_recommendations" not in response:
            response["intelligent_recommendations"] = []
        if "gap_analysis" not in response:
            response["gap_analysis"] = []
        if "required_qualifications" not in response:
            response["required_qualifications"] = []
        if "electrical_context_for_dpi" not in response:
            response["electrical_context_for_dpi"] = {}
        
        return response
    
    def _parse_ai_json_response(self, ai_response: str) -> Dict[str, Any]:
        """
        Robust parsing of AI JSON response with multiple fallback strategies
        """
        import json
        import re
        
        if not ai_response or not ai_response.strip():
            return None
        
        # Strategy 1: Try to find JSON block
        json_patterns = [
            r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}',  # Simple nested JSON
            r'\{.*\}',  # Any content between braces
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
            r'```\s*(\{.*?\})\s*```'  # JSON in generic code blocks
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, ai_response, re.DOTALL)
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if isinstance(parsed, dict):
                        return parsed
                except json.JSONDecodeError:
                    continue
        
        # Strategy 2: Try to clean and parse the entire response
        cleaned_response = ai_response.strip()
        if not cleaned_response.startswith('{'):
            # Find first { and last }
            start_idx = cleaned_response.find('{')
            end_idx = cleaned_response.rfind('}')
            if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                cleaned_response = cleaned_response[start_idx:end_idx+1]
        
        try:
            return json.loads(cleaned_response)
        except json.JSONDecodeError as e:
            print(f"[{self.name}] JSON parse error: {e}")
            print(f"[{self.name}] Problematic response: {ai_response[:200]}...")
            
        # Strategy 3: Try to fix common JSON issues
        try:
            # Fix common issues: unescaped quotes, trailing commas, etc.
            fixed_response = cleaned_response
            fixed_response = re.sub(r',\s*}', '}', fixed_response)  # Remove trailing commas
            fixed_response = re.sub(r',\s*]', ']', fixed_response)  # Remove trailing commas in arrays
            fixed_response = re.sub(r'([^\\])"([^"]*)":', r'\1"\2":', fixed_response)  # Fix potential quote issues
            
            return json.loads(fixed_response)
        except json.JSONDecodeError:
            pass
        
        return None
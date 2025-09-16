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

3. SELEZIONE TECNICA DPI PER CATEGORIA RISCHIO

   RISCHI ELETTRICI:
   - Guanti isolanti (EN 60903): Classe 00 (BT), Classe 0-4 (MT/AT)
   - Scarpe isolanti (EN 50321): Classe 00-3 secondo tensione
   - Elmetti dielettrici (EN 397): Proprietà elettriche opzionali
   - Indumenti antistatici per ATEX (EN 1149)

   RISCHI CHIMICI/ATEX:
   - Protezione respiratoria: Filtri A/B/E/K/P secondo sostanza
   - SCBA per IDLH o O2<19.5%
   - Indumenti chimici: Tipo 1-6 secondo permeazione
   - Guanti resistenti permeazione chimica (EN 374)
   - Calzature antistatiche per ATEX (EN 345 S1/S2/S3)

   LAVORI IN QUOTA (>2m):
   - Imbracatura anticaduta (EN 361): Punto attacco dorsale/sternale
   - Cordini con assorbitore energia (EN 355)
   - Dispositivi retrattili (EN 360)
   - Elmetti con sottogola (EN 397/EN 12492)
   - Scarpe antiscivolo con suola antiperforazione

   LAVORI A CALDO:
   - Maschera saldatura DIN 9-14 secondo processo
   - Indumenti ignifughi (EN 11611/11612)
   - Guanti saldatore (EN 12477)
   - Scarpe resistenti calore
   - Protezione respiratoria per fumi metallici
   - Grembiuli/ghette in cuoio

   SPAZI CONFINATI:
   - SCBA o sistema aria respirabile con linea
   - Imbracatura con punto aggancio dorsale per recupero
   - Rilevatore multigas portatile calibrato
   - Radio/comunicazione ATEX
   - Illuminazione portatile ATEX

   RISCHI MECCANICI GENERALI:
   - Guanti resistenti taglio/abrasione (EN 388)
   - Scarpe antinfortunistiche S1/S2/S3 (EN 345)
   - Elmetti di protezione (EN 397)
   - Occhiali/visiere protezione (EN 166)
   - Indumenti alta visibilità (EN 471)

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
        
        # Extract comprehensive risk information directly from risk mapping
        all_risk_info = self._extract_all_risks_from_mapping(detected_risks, permit_data)
        electrical_risk_info = all_risk_info.get("electrical", {})
        
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
        
        # Build comprehensive risk context from risk mapping
        risks_context = self._build_risk_context_for_dpi(all_risk_info, additional_electrical_context)
        
        permit_summary = f"""
ANALISI PERMESSO DI LAVORO - FASE PRE-AUTORIZZAZIONE
IMPORTANTE: Stai analizzando un PERMESSO DI LAVORO che deve ancora essere approvato. Il lavoro NON È ANCORA INIZIATO.

PERMESSO DA ANALIZZARE - VALUTAZIONE DPI (Dispositivi di Protezione Individuale):
TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}

CONTESTO: Il tuo ruolo è valutare SE questo permesso può essere APPROVATO e quali DPI devono essere FORNITI PRIMA dell'inizio del lavoro.

RISCHI IDENTIFICATI DAL SISTEMA: {detected_risks_summary}

{risks_context}

DPI PREVISTI NEL PERMESSO: {existing_dpi if existing_dpi else 'Nessun DPI specificato'}

AZIONI MITIGAZIONE PREVISTE: {existing_actions if existing_actions else 'Nessuna azione specificata'}

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

   b) RISCHI DA LAVORI IN QUOTA (>2 metri):
      IMPORTANTE: Analizzare sempre se il lavoro comporta rischi di caduta dall'alto:

      - PROTEZIONE ANTICADUTA OBBLIGATORIA:
        * Imbracatura anticaduta EN 361 (punto attacco dorsale/sternale)
        * Cordini con assorbitore energia EN 355 (lunghezza ≤2m)
        * Dispositivi retrattili EN 360 per movimenti
        * Elmetto con sottogola EN 397/EN 12492
        * Scarpe antiscivolo con suola antiperforazione
        * Guanti grip per presa sicura

      - FORMAZIONE OBBLIGATORIA: DPI Categoria III

   c) RISCHI CHIMICI E ATEX:
      IMPORTANTE: Analizzare sempre presenza sostanze chimiche o atmosfere esplosive:

      - PROTEZIONE RESPIRATORIA:
        * Filtri A (organici), B (inorganici), E (acidi), K (ammoniaca), P (polveri)
        * SCBA per IDLH o O2<19.5%
        * Maschere filtranti EN 149 (FFP1/2/3)

      - PROTEZIONE CORPO:
        * Indumenti chimici Tipo 1-6 secondo permeazione EN 14605
        * Indumenti antistatici ATEX EN 1149
        * Guanti resistenti permeazione chimica EN 374
        * Calzature antistatiche EN 345 S1/S2/S3

      - FORMAZIONE OBBLIGATORIA: DPI Categoria III per respiratori

   d) RISCHI DA LAVORI A CALDO:
      IMPORTANTE: Analizzare sempre operazioni con fiamme, scintille, calore:

      - PROTEZIONE SPECIFICA:
        * Maschera saldatura DIN 9-14 secondo processo
        * Indumenti ignifughi EN 11611 (saldatura) / EN 11612 (calore)
        * Guanti saldatore EN 12477 (tipo A/B secondo lavoro)
        * Scarpe resistenti calore e scintille
        * Protezione respiratoria fumi metallici
        * Grembiuli/ghette in cuoio per schizzi

      - FORMAZIONE OBBLIGATORIA: Saldatura e DPI categoria II/III

   e) RISCHI DA SPAZI CONFINATI:
      IMPORTANTE: Analizzare sempre accesso a spazi con ventilazione limitata:

      - PROTEZIONE VITALE:
        * SCBA o sistema aria respirabile con linea
        * Imbracatura con punto aggancio dorsale per recupero
        * Rilevatore multigas portatile calibrato (O2, LEL, H2S, CO)
        * Radio/comunicazione ATEX per spazio confinato
        * Illuminazione portatile ATEX

      - FORMAZIONE OBBLIGATORIA: DPI Categoria III e procedure spazi confinati

   f) RISCHI MECCANICI GENERALI:
      IMPORTANTE: Analizzare sempre presenza macchinari, utensili, materiali:

      - PROTEZIONE BASE:
        * Elmetto di protezione EN 397 (impatti, penetrazione)
        * Occhiali/visiere protezione EN 166 (schizzi, proiezioni)
        * Guanti resistenti taglio/abrasione EN 388 (livello appropriato)
        * Scarpe antinfortunistiche S1/S2/S3 EN 345
        * Indumenti alta visibilità EN 471 se necessario

3. CATEGORIE DPI secondo Regolamento UE 2016/425:
   - Categoria I (rischi minimi): DPI semplici
   - Categoria II (rischi significativi): DPI intermedi  
   - Categoria III (rischi mortali/irreversibili): DPI complessi (include DPI elettrici)

4. VALUTAZIONE ADEGUATEZZA DPI ESISTENTI:
   - Corrispondenza ai rischi identificati
   - Conformità normative (marcatura CE, standards EN)
   - Compatibilità tra diversi DPI
   - Stato di manutenzione e integrità

IMPORTANTE: ELIMINAZIONE INTELLIGENTE DUPLICATI DPI

Prima di fornire la risposta, ANALIZZA ATTENTAMENTE i DPI raccomandati e ELIMINA tutti i duplicati seguendo questa logica:

**STEP 1 - IDENTIFICAZIONE DUPLICATI:**
Cerca DPI che proteggono la stessa zona corporea con funzioni sovrapposte:
- Guanti isolanti vs guanti meccanici (se isolanti coprono anche meccanici)
- Elmetto standard vs elmetto elettrico (se elettrico copre anche impatti)
- Scarpe S1 vs scarpe isolanti (se isolanti coprono anche requisiti S1)

**STEP 2 - CONSOLIDAMENTO INTELLIGENTE:**
Per ogni zona corporea (mani, testa, piedi, occhi, corpo, respirazione):

a) **SE hai DPI compatibili** → Scegli quello più completo che copre tutti i rischi:
   - Esempio: "Guanti isolanti EN 60903 classe 1" invece di separare isolanti + meccanici
   - Esempio: "Elmetto dielettrico EN 50365" invece di elmetto standard + elettrico

b) **SE hai DPI incompatibili** → Mantieni entrambi con specifica dell'uso:
   - Esempio: "Guanti isolanti EN 60903 (per lavori elettrici)" + "Guanti saldatore EN 12477 (per saldatura)"
   - Questo SOLO se ci sono davvero operazioni elettriche E di saldatura nel permesso

**STEP 3 - VERIFICA FINALE:**
Prima di completare la risposta, rileggi l'array "missing_dpi" e verifica:
- ❌ Non ci sono DPI identici o estremamente simili
- ❌ Non ci sono DPI che si sovrappongono inutilmente
- ✅ Ogni DPI multiplo per stessa zona ha giustificazione specifica tra parentesi
- ✅ La lista è la più CONCISA possibile mantenendo la sicurezza

**ESEMPI PRATICI DI DEDUPLICAZIONE:**

❌ SBAGLIATO (duplicati):
```json
"missing_dpi": [
  "Guanti resistenti EN 388",
  "Guanti isolanti EN 60903",
  "Guanti da lavoro meccanici",
  "Elmetto EN 397",
  "Elmetto elettrico EN 50365"
]
```

✅ CORRETTO (deduplicato):
```json
"missing_dpi": [
  "Guanti isolanti EN 60903 classe 1 (protezione elettrica e meccanica)",
  "Elmetto dielettrico EN 50365 (protezione elettrica e impatti)"
]
```

❌ SBAGLIATO (sovrapposizione inutile):
```json
"missing_dpi": [
  "Occhiali protezione EN 166",
  "Visiera trasparente",
  "Protezione occhi"
]
```

✅ CORRETTO (consolidato):
```json
"missing_dpi": [
  "Occhiali protezione EN 166 con protezione laterale"
]
```

SOLO SE ci sono operazioni davvero incompatibili (es. saldatura + elettrica):
✅ ACCETTABILE:
```json
"missing_dpi": [
  "Guanti isolanti EN 60903 classe 1 (per interventi elettrici)",
  "Guanti saldatore EN 12477 tipo A (per saldatura TIG)",
  "Maschera saldatura DIN 11 (per saldatura)"
]
```

Fornisci risposta ESCLUSIVAMENTE in formato JSON con:
- existing_dpi_adequacy: "adeguati" | "inadeguati" | "parziali"
- missing_dpi: array SENZA DUPLICATI con DPI consolidati e attività specifica se multipli (es. "Guanti isolanti EN 60903 classe 1 (lavori elettrici)")
- required_training: array di stringhe con formazione richiesta
- normative_compliance: stringa con conformità normative

ESEMPIO FORMATO RISPOSTA:
{{
  "existing_dpi_adequacy": "inadeguati",
  "missing_dpi": [
    "Guanti isolanti EN 60903 classe 1 (per lavori elettrici MT)",
    "Maschera saldatura DIN 11 (per operazioni saldatura)",
    "Imbracatura anticaduta EN 361 (per lavori in quota)"
  ],
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
        
        # DPI requirements are already deduplicated by AI based on prompt instructions
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

    def _extract_all_risks_from_mapping(self, detected_risks: Dict[str, Any], permit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract comprehensive risk information for all risk types from risk mapping results
        """
        all_risks = {
            "electrical": {"has_risk": False, "details": []},
            "height_work": {"has_risk": False, "details": []},
            "chemical": {"has_risk": False, "details": []},
            "hot_work": {"has_risk": False, "details": []},
            "confined_space": {"has_risk": False, "details": []},
            "mechanical": {"has_risk": False, "details": []}
        }

        # Process detected risks from risk mapping
        for risk_type, risk_info in detected_risks.items():
            if risk_type == "electrical":
                # Use existing electrical extraction logic
                all_risks["electrical"] = self._extract_electrical_risk_from_mapping(detected_risks, permit_data)
                all_risks["electrical"]["has_risk"] = all_risks["electrical"]["has_electrical_risk"]

            elif risk_type in ["height", "height_work", "lavori_quota"]:
                all_risks["height_work"]["has_risk"] = True
                all_risks["height_work"]["details"] = [risk_info.get("description", "Lavori in quota identificati")]

            elif risk_type in ["chemical", "chimico", "atex"]:
                all_risks["chemical"]["has_risk"] = True
                all_risks["chemical"]["details"] = [risk_info.get("description", "Rischi chimici/ATEX identificati")]

            elif risk_type in ["hot_work", "lavori_caldo", "saldatura"]:
                all_risks["hot_work"]["has_risk"] = True
                all_risks["hot_work"]["details"] = [risk_info.get("description", "Lavori a caldo identificati")]

            elif risk_type in ["confined_space", "spazi_confinati"]:
                all_risks["confined_space"]["has_risk"] = True
                all_risks["confined_space"]["details"] = [risk_info.get("description", "Spazi confinati identificati")]

            elif risk_type in ["mechanical", "meccanico"]:
                all_risks["mechanical"]["has_risk"] = True
                all_risks["mechanical"]["details"] = [risk_info.get("description", "Rischi meccanici identificati")]

        # Secondary analysis from permit text for missing risks
        permit_text = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('work_type', '')}".lower()

        # Height work keywords
        if not all_risks["height_work"]["has_risk"]:
            height_keywords = ["quota", "altezza", "tetto", "ponteggio", "scala", "piattaforma", "sopra", "metri"]
            if any(keyword in permit_text for keyword in height_keywords):
                all_risks["height_work"]["has_risk"] = True
                all_risks["height_work"]["details"] = ["Lavori in quota identificati dal testo"]

        # Chemical/ATEX keywords
        if not all_risks["chemical"]["has_risk"]:
            chemical_keywords = ["chimico", "solvente", "acido", "base", "gas", "vapore", "atex", "esplosivo"]
            if any(keyword in permit_text for keyword in chemical_keywords):
                all_risks["chemical"]["has_risk"] = True
                all_risks["chemical"]["details"] = ["Rischi chimici identificati dal testo"]

        # Hot work keywords
        if not all_risks["hot_work"]["has_risk"]:
            hot_work_keywords = ["saldatura", "taglio", "fiamma", "caldo", "scintille", "brasatura", "ossitaglio"]
            if any(keyword in permit_text for keyword in hot_work_keywords):
                all_risks["hot_work"]["has_risk"] = True
                all_risks["hot_work"]["details"] = ["Lavori a caldo identificati dal testo"]

        # Confined space keywords
        if not all_risks["confined_space"]["has_risk"]:
            confined_keywords = ["confinato", "serbatoio", "cisterna", "tunnel", "fossa", "pozzo", "cunicolo"]
            if any(keyword in permit_text for keyword in confined_keywords):
                all_risks["confined_space"]["has_risk"] = True
                all_risks["confined_space"]["details"] = ["Spazi confinati identificati dal testo"]

        # Mechanical keywords (always present as baseline)
        if not all_risks["mechanical"]["has_risk"]:
            mechanical_keywords = ["utensile", "macchinario", "meccanico", "taglio", "assemblaggio", "montaggio"]
            if any(keyword in permit_text for keyword in mechanical_keywords) or permit_data.get('work_type') in ['meccanico', 'manutenzione']:
                all_risks["mechanical"]["has_risk"] = True
                all_risks["mechanical"]["details"] = ["Rischi meccanici identificati"]

        return all_risks

    def _build_risk_context_for_dpi(self, all_risk_info: Dict[str, Any], additional_electrical_context: Dict[str, Any]) -> str:
        """
        Build comprehensive risk context for DPI analysis
        """
        context_parts = []

        # Electrical risks
        electrical_risk = all_risk_info.get("electrical", {})
        if electrical_risk.get("has_risk") or electrical_risk.get("has_electrical_risk"):
            voltage_info = electrical_risk.get("voltage_level", "sconosciuto")
            confidence = electrical_risk.get("confidence", 0.0)
            details = electrical_risk.get("risk_details", electrical_risk.get("details", []))

            # Combine with specialist info if available
            if additional_electrical_context and additional_electrical_context.get("voltage_level"):
                voltage_info = additional_electrical_context.get("voltage_level", voltage_info)

            context_parts.append(f"""RISCHIO ELETTRICO IDENTIFICATO:
- Presenza lavori elettrici: SÌ (confidenza: {confidence:.1f})
- Livello tensione stimato: {voltage_info}
- Dettagli: {', '.join(details) if details else 'Rischio elettrico generico'}""")

        # Height work risks
        if all_risk_info.get("height_work", {}).get("has_risk"):
            details = all_risk_info["height_work"].get("details", [])
            context_parts.append(f"""RISCHIO LAVORI IN QUOTA IDENTIFICATO:
- Presenza lavori >2m: SÌ
- Dettagli: {', '.join(details) if details else 'Rischio caduta dall alto'}""")

        # Chemical/ATEX risks
        if all_risk_info.get("chemical", {}).get("has_risk"):
            details = all_risk_info["chemical"].get("details", [])
            context_parts.append(f"""RISCHIO CHIMICO/ATEX IDENTIFICATO:
- Presenza sostanze pericolose: SÌ
- Dettagli: {', '.join(details) if details else 'Esposizione sostanze chimiche/atmosfere esplosive'}""")

        # Hot work risks
        if all_risk_info.get("hot_work", {}).get("has_risk"):
            details = all_risk_info["hot_work"].get("details", [])
            context_parts.append(f"""RISCHIO LAVORI A CALDO IDENTIFICATO:
- Presenza fiamme/scintille: SÌ
- Dettagli: {', '.join(details) if details else 'Operazioni con sorgenti di ignizione'}""")

        # Confined space risks
        if all_risk_info.get("confined_space", {}).get("has_risk"):
            details = all_risk_info["confined_space"].get("details", [])
            context_parts.append(f"""RISCHIO SPAZI CONFINATI IDENTIFICATO:
- Accesso spazi confinati: SÌ
- Dettagli: {', '.join(details) if details else 'Ingresso spazi con ventilazione limitata'}""")

        # Mechanical risks
        if all_risk_info.get("mechanical", {}).get("has_risk"):
            details = all_risk_info["mechanical"].get("details", [])
            context_parts.append(f"""RISCHI MECCANICI IDENTIFICATI:
- Presenza rischi meccanici: SÌ
- Dettagli: {', '.join(details) if details else 'Uso utensili/macchinari'}""")

        return "\n\n".join(context_parts) if context_parts else "NESSUN RISCHIO SPECIFICO IDENTIFICATO dal Risk Mapping"

    
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
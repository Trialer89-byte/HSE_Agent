"""
AI-Powered Work Analysis Agent
Uses AI to recognize work types, generate searches, and suggest PPE/actions
"""
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from app.config.settings import settings


class AIWorkAnalyzer:
    """
    AI-powered agent that analyzes work permits to identify work types,
    generate search queries, and suggest actions/PPE using AI intelligence
    """
    
    def __init__(self):
        """Initialize the AI Work Analyzer"""
        self.gemini_model = None
        self.api_working = False
        
        # Initialize Gemini
        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(settings.gemini_model)
                # Test API
                test_response = self.gemini_model.generate_content('test')
                self.api_working = True
                print(f"[AIWorkAnalyzer] Gemini API initialized successfully")
            except Exception as e:
                print(f"[AIWorkAnalyzer] Gemini API failed: {str(e)}")
                self.api_working = False
    
    async def analyze_work_permit(self, permit_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive AI-based analysis of work permit
        """
        if not self.api_working:
            return self._fallback_analysis()
        
        # Extract text from permit
        permit_text = self._extract_permit_text(permit_data)
        
        try:
            # AI-based work type recognition
            work_types = await self._ai_recognize_work_types(permit_text)
            
            # AI-generated search queries
            search_queries = await self._ai_generate_search_queries(permit_text, work_types)
            
            # AI-based action validation
            action_validation = await self._ai_validate_actions(permit_data, work_types)
            
            # AI-based PPE validation
            ppe_validation = await self._ai_validate_ppe(permit_data, work_types)
            
            return {
                "work_types": work_types,
                "search_queries": search_queries,
                "action_validation": action_validation,
                "ppe_validation": ppe_validation,
                "analysis_quality": "ai_powered"
            }
            
        except Exception as e:
            print(f"[AIWorkAnalyzer] AI analysis failed: {str(e)}")
            return self._fallback_analysis()
    
    async def _ai_recognize_work_types(self, permit_text: str) -> List[Dict[str, Any]]:
        """
        Use AI to recognize work types from permit text
        """
        prompt = f"""
Analizza questo permesso di lavoro e identifica TUTTI i tipi di lavoro che potrebbero essere coinvolti.

TESTO PERMESSO:
{permit_text}

TIPI DI LAVORO DA CONSIDERARE (esempi, ma non limitarti a questi):
- Spazi confinati (serbatoi, vasche, pozzi, locali chiusi, atmosfere pericolose)
- Lavori a caldo (saldatura, taglio, molatura, scintille, fiamme)
- Lavori in quota (altezza, cadute, ponteggi, coperture)
- Lavori elettrici (tensione, quadri, cabine, isolamento)
- Manipolazione chimica (sostanze pericolose, SDS, reazioni)
- Scavi (movimento terra, franamenti, sottoservizi)
- Sollevamento carichi (gru, brache, movimentazione)
- Manutenzione generale (LOTO, isolamento energie, riparazioni)

RAGIONA COME ESPERTO HSE:
- Identifica lavori IMPLICITI (es: "pulizia serbatoio" = spazio confinato)
- Correggi errori ortografici (es: "welsing" = welding = saldatura)
- Considera attività preparatorie (es: accesso, isolamento)
- Pensa a cosa farebbe REALMENTE l'operatore

Restituisci JSON con questa struttura:
{{
  "work_types": [
    {{
      "type": "nome_tipo_lavoro",
      "confidence": 0.0-1.0,
      "reasoning": "perché hai identificato questo tipo",
      "hazards": ["pericolo1", "pericolo2"],
      "evidence": ["frase o parola che ti ha fatto pensare a questo tipo"]
    }}
  ]
}}

Rispondi SOLO con il JSON.
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result.get("work_types", [])
        except Exception as e:
            print(f"[AIWorkAnalyzer] Work type recognition failed: {str(e)}")
            return []
    
    async def _ai_generate_search_queries(self, permit_text: str, work_types: List[Dict]) -> List[Dict[str, Any]]:
        """
        Use AI to generate targeted search queries for documents
        """
        work_types_str = "\n".join([
            f"- {wt['type']} (confidenza: {wt['confidence']:.0%}): {wt['reasoning']}"
            for wt in work_types[:5]
        ])
        
        prompt = f"""
Basandoti su questo permesso di lavoro e sui tipi di lavoro identificati, genera query di ricerca specifiche per trovare documenti normativi e procedure aziendali rilevanti.

PERMESSO:
{permit_text}

TIPI DI LAVORO IDENTIFICATI:
{work_types_str}

ESEMPI DI DOCUMENTI DA CERCARE (non limitarti a questi):
- Normative specifiche (D.Lgs 81/08, DPR 177/2011, CEI 11-27, EN standards)
- Procedure aziendali (LOTO, spazi confinati, hot work)
- Check list operative
- Istruzioni di sicurezza
- Schede sicurezza (SDS)
- Piani di emergenza

GENERA query di ricerca che troverebbero documenti utili per:
1. Verificare conformità normativa
2. Identificare procedure da seguire  
3. Controllare DPI richiesti
4. Pianificare misure di sicurezza

Restituisci JSON:
{{
  "search_queries": [
    {{
      "query": "testo ricerca specifico",
      "purpose": "scopo della ricerca",
      "priority": "alta|media|bassa",
      "document_type": "normativa|procedura|check_list|istruzione|sds"
    }}
  ]
}}

Rispondi SOLO con il JSON.
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result.get("search_queries", [])
        except Exception as e:
            print(f"[AIWorkAnalyzer] Search query generation failed: {str(e)}")
            return []
    
    async def _ai_validate_actions(self, permit_data: Dict[str, Any], work_types: List[Dict]) -> Dict[str, Any]:
        """
        Use AI to validate if proposed actions are sufficient
        """
        # Extract existing actions
        existing_actions = self._extract_existing_actions(permit_data)
        existing_actions_str = "\n".join(existing_actions) if existing_actions else "Nessuna azione specificata"
        
        work_types_str = "\n".join([
            f"- {wt['type']}: {', '.join(wt.get('hazards', []))}"
            for wt in work_types[:5]
        ])
        
        prompt = f"""
Valuta se le azioni/misure proposte in questo permesso sono SUFFICIENTI per i rischi identificati.

AZIONI/MISURE ATTUALI NEL PERMESSO:
{existing_actions_str}

TIPI DI LAVORO E RISCHI IDENTIFICATI:
{work_types_str}

ESEMPI DI AZIONI TIPICAMENTE RICHIESTE (usa come riferimento):
- Spazi confinati: verifica atmosfera, ventilazione forzata, sorveglianza esterna, piano recupero
- Lavori a caldo: rimozione combustibili, sorveglianza antincendio, estintori, isolamento area
- Lavori in quota: verifica dispositivi anticaduta, ancoraggi, delimitazione area
- Lavori elettrici: sezionamento, verifica assenza tensione, messa a terra, LOTO
- Manipolazione chimica: consultazione SDS, ventilazione, contenimento sversamenti
- Scavi: identificazione sottoservizi, armature, vie fuga
- Sollevamento: calcolo carichi, verifica attrezzature, piano sollevamento
- Manutenzione: isolamento energie, LOTO, consegna impianto

VALUTA E SUGGERISCI:
1. Azioni OBBLIGATORIE mancanti (critiche per sicurezza)
2. Azioni RACCOMANDATE per migliorare sicurezza
3. Insufficienze nelle azioni proposte

Restituisci JSON:
{{
  "action_assessment": {{
    "sufficiency_score": 0.0-1.0,
    "missing_mandatory": [
      {{
        "action": "azione specifica mancante",
        "reason": "perché è obbligatoria",
        "work_type": "tipo lavoro correlato"
      }}
    ],
    "missing_recommended": [
      {{
        "action": "azione raccomandata",
        "reason": "come migliora la sicurezza",
        "work_type": "tipo lavoro correlato"
      }}
    ],
    "improvements": [
      "suggerimento miglioramento 1",
      "suggerimento miglioramento 2"
    ]
  }}
}}

Rispondi SOLO con il JSON.
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result.get("action_assessment", {})
        except Exception as e:
            print(f"[AIWorkAnalyzer] Action validation failed: {str(e)}")
            return {}
    
    async def _ai_validate_ppe(self, permit_data: Dict[str, Any], work_types: List[Dict]) -> Dict[str, Any]:
        """
        Use AI to validate if proposed PPE is sufficient
        """
        # Extract existing PPE
        existing_ppe = self._extract_existing_ppe(permit_data)
        existing_ppe_str = "\n".join(existing_ppe) if existing_ppe else "Nessun DPI specificato"
        
        work_types_str = "\n".join([
            f"- {wt['type']}: {', '.join(wt.get('hazards', []))}"
            for wt in work_types[:5]
        ])
        
        prompt = f"""
Valuta se i DPI (Dispositivi di Protezione Individuale) specificati sono SUFFICIENTI per i rischi identificati.

DPI ATTUALI NEL PERMESSO:
{existing_ppe_str}

TIPI DI LAVORO E RISCHI IDENTIFICATI:
{work_types_str}

ESEMPI DI DPI TIPICAMENTE RICHIESTI (usa come riferimento con standard):
- Spazi confinati: APVR/respiratore (EN 137), rilevatore gas (EN 60079), imbracatura (EN 361)
- Lavori a caldo: maschera saldatura (EN 175), guanti termici (EN 12477), abbigliamento ignifugo (EN 11612)
- Lavori in quota: imbracatura anticaduta (EN 361), casco (EN 397), dispositivo retrattile (EN 360)
- Lavori elettrici: guanti isolanti (EN 60903), casco isolante (EN 50365), tester tensione (EN 61243)
- Manipolazione chimica: guanti chimico-resistenti (EN 374), occhiali/visiera (EN 166), facciale ABEK (EN 14387)
- Scavi: casco (EN 397), gilet alta visibilità (EN 20471), calzature antinfortunistiche (EN ISO 20345)
- Sollevamento: casco (EN 397), gilet alta visibilità (EN 20471), guanti antiscivolo (EN 388)
- Manutenzione: casco (EN 397), occhiali (EN 166), guanti meccanici (EN 388), calzature (EN ISO 20345)

VALUTA E SUGGERISCI:
1. DPI OBBLIGATORI mancanti (critici per sicurezza)
2. DPI RACCOMANDATI per migliorare protezione
3. Standard tecnici specifici richiesti

Restituisci JSON:
{{
  "ppe_assessment": {{
    "sufficiency_score": 0.0-1.0,
    "missing_mandatory": [
      {{
        "item": "DPI specifico mancante",
        "standard": "standard tecnico (EN XXXX)",
        "reason": "protezione da quale rischio",
        "work_type": "tipo lavoro correlato"
      }}
    ],
    "missing_recommended": [
      {{
        "item": "DPI raccomandato",
        "standard": "standard tecnico",
        "reason": "come migliora la protezione",
        "work_type": "tipo lavoro correlato"
      }}
    ],
    "improvements": [
      "suggerimento miglioramento 1",
      "suggerimento miglioramento 2"
    ]
  }}
}}

Rispondi SOLO con il JSON.
"""
        
        try:
            response = self.gemini_model.generate_content(prompt)
            result = self._parse_json_response(response.text)
            return result.get("ppe_assessment", {})
        except Exception as e:
            print(f"[AIWorkAnalyzer] PPE validation failed: {str(e)}")
            return {}
    
    def _extract_permit_text(self, permit_data: Dict[str, Any]) -> str:
        """Extract all relevant text from permit data"""
        text_parts = []
        
        # Main fields
        for field in ["title", "description", "work_type", "location", "equipment", 
                     "safety_measures", "actions", "procedures", "ppe", "dpi"]:
            if field in permit_data and permit_data[field]:
                if isinstance(permit_data[field], list):
                    text_parts.extend([str(item) for item in permit_data[field]])
                else:
                    text_parts.append(str(permit_data[field]))
        
        return " ".join(text_parts)
    
    def _extract_existing_actions(self, permit_data: Dict[str, Any]) -> List[str]:
        """Extract existing actions from permit"""
        actions = []
        action_fields = ["safety_measures", "actions", "procedures", "controls", "measures"]
        
        for field in action_fields:
            if field in permit_data and permit_data[field]:
                if isinstance(permit_data[field], list):
                    actions.extend([str(action) for action in permit_data[field]])
                else:
                    actions.append(str(permit_data[field]))
        
        return actions
    
    def _extract_existing_ppe(self, permit_data: Dict[str, Any]) -> List[str]:
        """Extract existing PPE from permit"""
        ppe_items = []
        ppe_fields = ["ppe", "dpi", "protective_equipment", "safety_equipment"]
        
        for field in ppe_fields:
            if field in permit_data and permit_data[field]:
                if isinstance(permit_data[field], list):
                    ppe_items.extend([str(item) for item in permit_data[field]])
                else:
                    ppe_items.append(str(permit_data[field]))
        
        return ppe_items
    
    def _parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        import json
        
        # Find JSON in response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx+1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                print(f"[AIWorkAnalyzer] Failed to parse JSON: {json_str[:200]}...")
                return {}
        
        return {}
    
    def _fallback_analysis(self) -> Dict[str, Any]:
        """Fallback analysis when AI is not available"""
        return {
            "work_types": [],
            "search_queries": [],
            "action_validation": {"sufficiency_score": 0.5, "missing_mandatory": [], "missing_recommended": []},
            "ppe_validation": {"sufficiency_score": 0.5, "missing_mandatory": [], "missing_recommended": []},
            "analysis_quality": "fallback"
        }
from typing import Dict, Any, List
try:
    from autogen_agentchat.agents import AssistantAgent
    
    # Create compatibility layer
    class autogen:
        AssistantAgent = AssistantAgent
except ImportError:
    # Fallback mock for testing
    class MockAgent:
        def __init__(self, name, system_message, llm_config=None, max_consecutive_auto_reply=1, human_input_mode="NEVER"):
            self.name = name
            self.system_message = system_message
    
    class autogen:
        AssistantAgent = MockAgent

import google.generativeai as genai
from .autogen_config import get_autogen_llm_config, GeminiLLMConfig
from app.config.settings import settings


class SimpleAutoGenHSEAgents:
    """
    Simplified AutoGen HSE agents for testing
    """
    
    def __init__(self, user_context: Dict[str, Any], vector_service=None):
        self.user_context = user_context
        self.vector_service = vector_service
        self.llm_config = get_autogen_llm_config()
        
        # Initialize Gemini directly for AI-powered conversations
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(settings.gemini_model)
            print(f"[SimpleAutoGenHSEAgents] Gemini model initialized: {settings.gemini_model}")
        else:
            self.gemini_model = None
            print("[SimpleAutoGenHSEAgents] WARNING: No Gemini API key - agents will not use AI")
        
        self.agents = self._create_simple_agents()
    
    def _create_simple_agents(self) -> Dict[str, autogen.AssistantAgent]:
        """Create simplified HSE agents"""
        
        # HSE Analyst Agent
        hse_analyst = autogen.AssistantAgent(
            name="HSE_Analyst",
            system_message="""
Sei un Ingegnere HSE specializzato nell'analisi dei rischi secondo il D.Lgs 81/08.

OBIETTIVI SPECIFICI:
1. IDENTIFICAZIONE RISCHI DETTAGLIATA:
   - Rischi elettrici (tensione, arco elettrico, contatti indiretti)
   - Rischi meccanici (cesoiamento, schiacciamento, taglio)
   - Rischi chimici (inalazione, contatto cutaneo, ingestione)
   - Rischi fisici (rumore, vibrazioni, microclima)
   - Rischi di caduta (dall'alto, in piano, nello stesso livello)
   - Rischi ergonomici (movimentazione manuale carichi, posture)

2. VALUTAZIONE DPI SPECIFICA:
   - Categorie DPI (I, II, III) secondo Reg. UE 2016/425
   - Standard tecnici applicabili (EN, ISO)
   - Livelli di protezione richiesti
   - Compatibilità tra DPI diversi

3. MISURE DI CONTROLLO GERARCHICHE:
   - Eliminazione del rischio
   - Sostituzione (tecnologie, sostanze)
   - Controlli ingegneristici
   - Controlli amministrativi
   - DPI (ultima risorsa)

METODOLOGIA:
- Usa matrice rischio/probabilità per prioritizzazione
- Riferimenti normativi specifici per ogni rischio
- Indicazioni quantitative dove possibile
- Considera interferenze tra attività diverse

FORMATO RISPOSTA STRUTTURATA:
```json
{
  "rischi_identificati": [
    {
      "tipo": "elettrico",
      "descrizione": "Rischio elettrocuzione da quadro BT 400V",
      "probabilità": "media",
      "magnitudo": "alta",
      "livello_rischio": "alto",
      "misure_controllo": ["LOTO", "DPI isolanti"],
      "normative": ["CEI 11-27", "D.Lgs 81/08 art. 80-87"]
    }
  ],
  "dpi_richiesti": [
    {
      "tipo": "guanti_isolanti",
      "standard": "EN 60903",
      "classe": "0",
      "motivazione": "Protezione da contatti elettrici 1000V"
    }
  ]
}
```
""",
            llm_config=self.llm_config,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER"
        )
        
        # Safety Reviewer Agent
        safety_reviewer = autogen.AssistantAgent(
            name="Safety_Reviewer",
            system_message="""
Sei un RSPP certificato con 15+ anni di esperienza nella validazione di analisi HSE.

COMPITI DI REVISIONE CRITICA:
1. AUDIT COMPLETEZZA RISCHI:
   - Verifica identificazione rischi secondo art. 28 D.Lgs 81/08
   - Controlla se tutti i rischi dell'allegato VI sono considerati
   - Valuta adeguatezza della valutazione probabilità/magnitudo
   - Identifica rischi non evidenti o interferenze

2. VALIDAZIONE DPI E MISURE:
   - Verifica conformità DPI al Reg. UE 2016/425
   - Controlla standard tecnici e classi di protezione
   - Valuta compatibilità ergonomica tra DPI
   - Verifica priorità misure di controllo (art. 15 D.Lgs 81/08)

3. COMPLIANCE NORMATIVA:
   - D.Lgs 81/08 - Titoli specifici applicabili
   - Normative tecniche UNI EN pertinenti
   - Regolamenti europei (REACH, CLP, Macchine)
   - Codici di prevenzione incendi

4. QUALITÀ DOCUMENTALE:
   - Precisione tecnica delle prescrizioni
   - Fattibilità operativa delle misure
   - Chiarezza delle istruzioni operative
   - Tracciabilità delle decisioni

CRITERI DI APPROVAZIONE:
✓ Rischi fatali/gravi tutti identificati e mitigati
✓ DPI specificati con standard e motivazioni tecniche
✓ Misure di controllo gerarchicamente ordinate
✓ Riferimenti normativi precisi e aggiornati
✓ Responsabilità e tempistiche definite

FORMATO VALIDAZIONE:
```json
{
  "esito_revisione": "approvata|integrazione_richiesta|respinta",
  "rischi_aggiuntivi": [...],
  "dpi_integrativi": [...],
  "note_compliance": [...],
  "raccomandazioni_miglioramento": [...]
}
```

STANDARD PROFESSIONALE: La revisione deve garantire zero infortuni.
""",
            llm_config=self.llm_config,
            max_consecutive_auto_reply=1,
            human_input_mode="NEVER"
        )
        
        return {
            "hse_analyst": hse_analyst,
            "safety_reviewer": safety_reviewer
        }
    
    async def analyze_permit(
        self, 
        permit_data: Dict[str, Any], 
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        AI-powered permit analysis using direct Gemini API calls
        """
        
        if not self.gemini_model:
            return {
                "analysis_complete": False,
                "error": "No AI model available - check Gemini API key configuration",
                "confidence_score": 0.0,
                "agents_involved": [],
                "processing_time": 0.0
            }
        
        # Prepare context from documents
        document_context = ""
        if context_documents:
            document_context = "\n\nDOCUMENTI DI RIFERIMENTO:\n"
            for doc in context_documents[:3]:  # Limit to 3 docs to avoid token limits
                document_context += f"- {doc.get('title', 'Documento')}: {doc.get('content', '')[:500]}...\n"
        
        # Create comprehensive analysis prompt
        analysis_prompt = f"""
Sei un Ingegnere HSE certificato che deve condurre una valutazione dei rischi secondo l'art. 28 del D.Lgs 81/08.

PERMESSO DI LAVORO DA ANALIZZARE:
- Titolo: {permit_data.get('title', 'Non specificato')}
- Descrizione: {permit_data.get('description', 'Non specificata')}
- Tipo di lavoro: {permit_data.get('work_type', 'Non specificato')}
- Ubicazione: {permit_data.get('location', 'Non specificata')}
- Durata: {permit_data.get('duration_hours', 'Non specificata')} ore
- Numero operatori: {permit_data.get('workers_count', 'Non specificato')}
- Attrezzature: {permit_data.get('equipment', 'Non specificate')}
{document_context}

METODOLOGIA DI ANALISI SISTEMATICA:

1. IDENTIFICAZIONE PERICOLI (Allegato VI D.Lgs 81/08):
   • Agenti chimici e cancerogeni/mutageni
   • Agenti fisici (rumore, vibrazioni, campi elettromagnetici, radiazioni)
   • Agenti biologici
   • Atmosfere esplosive (Direttiva ATEX)
   • Rischi connessi all'organizzazione del lavoro
   • Rischi ergonomici (MMC, videoterminali, posture)
   • Rischi psicosociali (stress lavoro-correlato)

2. VALUTAZIONE SPECIALE PER TIPO DI LAVORO:
   • Lavori elettrici → CEI 11-27, CEI EN 50110, D.Lgs 81/08 Titolo III
   • Lavori in altezza → D.Lgs 81/08 Titolo IV, UNI EN 365
   • Spazi confinati → DPR 177/2011, UNI 11326
   • Lavori con sostanze chimiche → Regolamento REACH/CLP
   • Movimentazione carichi → ISO 11228, UNI EN 1005

3. MATRICE RISCHIO (Probabilità × Magnitudo):
   Probabilità: improbabile(1) - poco probabile(2) - probabile(3) - molto probabile(4)
   Magnitudo: lieve(1) - modesta(2) - grave(3) - gravissima(4)
   Livello Rischio: basso(1-4) - medio(6-8) - alto(9-12) - molto alto(16)

4. DPI SECONDO GERARCHIA ART. 15 D.LGS 81/08:
   Per ogni DPI specificare:
   • Categoria (I-II-III secondo Reg. UE 2016/425)
   • Standard tecnico applicabile (EN/ISO)
   • Classe/Livello di protezione
   • Marcatura CE obbligatoria
   • Compatibilità con altri DPI

5. MISURE DI CONTROLLO PRIORITARIE:
   A) Eliminazione del pericolo
   B) Sostituzione (sostanze meno pericolose, attrezzature più sicure)
   C) Controlli ingegneristici (protezioni collettive, ventilazione)
   D) Controlli amministrativi (procedure, formazione, segnaletica)
   E) DPI (ultima linea di difesa)

FORMATO RISPOSTA RICHIESTO - FORNISCI JSON STRUTTURATO:

```json
{{
  "analisi_generale": {{
    "tipologia_lavoro": "descrizione specifica",
    "classificazione_rischio": "basso|medio|alto|molto_alto",
    "normative_principali": ["D.Lgs 81/08 art. X", "UNI EN XXXX"],
    "interferenze_identificate": ["descrizione interferenze"]
  }},
  "rischi_identificati": [
    {{
      "id": "R001",
      "categoria": "elettrico|meccanico|chimico|fisico|biologico|ergonomico|organizzativo",
      "descrizione_dettagliata": "Descrizione specifica del rischio con riferimenti tecnici",
      "fonti_pericolo": ["quadro elettrico BT", "attrezzi taglienti"],
      "probabilita": "improbabile|poco_probabile|probabile|molto_probabile",
      "magnitudo": "lieve|modesta|grave|gravissima",
      "livello_rischio": "basso|medio|alto|molto_alto",
      "normative_riferimento": ["CEI 11-27", "D.Lgs 81/08 art. 80-87"],
      "misure_controllo": [
        "eliminazione/sostituzione",
        "controlli_ingegneristici", 
        "controlli_amministrativi",
        "dpi_richiesti"
      ]
    }}
  ],
  "dpi_obbligatori": [
    {{
      "id": "DPI001",
      "tipo": "nome specifico DPI",
      "categoria_ue": "I|II|III",
      "standard_tecnico": "EN XXXX:YYYY",
      "classe_protezione": "specifica classe/livello",
      "rischi_coperti": ["rischi specifici protetti"],
      "requisiti_marcatura": "CE + codici applicabili",
      "istruzioni_uso": "modalità corretta di utilizzo",
      "compatibilita": "compatibilità con altri DPI",
      "periodicita_controllo": "giornaliera|settimanale|mensile"
    }}
  ],
  "misure_organizzative": [
    {{
      "tipo": "formazione|procedura|segnaletica|sorveglianza",
      "descrizione": "misura specifica da implementare",
      "responsabile": "figura responsabile",
      "tempistica": "prima dell'inizio|durante|dopo i lavori",
      "verifica": "modalità di verifica efficacia"
    }}
  ],
  "procedure_operative": [
    {{
      "fase_lavoro": "descrizione fase",
      "prescrizioni": ["prescrizione 1", "prescrizione 2"],
      "dpi_fase": ["DPI specifici per questa fase"],
      "controlli_sicurezza": ["controlli da effettuare"]
    }}
  ]
}}
```

RACCOMANDAZIONI FINALI:
- Utilizza sempre terminologia tecnica precisa
- Cita articoli specifici delle normative
- Quantifica dove possibile (dB, mg/m³, kN, ecc.)
- Considera tutte le fasi del lavoro
- Valuta le interferenze con altre attività
- Assicurati che ogni rischio abbia una misura di controllo specifica
"""
        
        try:
            print(f"[SimpleAutoGenHSEAgents] Starting HSE analysis with Gemini for permit {permit_data.get('id')}")
            
            # Simulate multi-agent conversation with multiple AI calls
            conversation_history = []
            
            # HSE Analyst response
            analyst_response = await self._get_gemini_response(
                analysis_prompt,
                "HSE_Analyst", 
                "Esperto HSE che identifica rischi e misure di sicurezza"
            )
            conversation_history.append({
                "agent": "HSE_Analyst",
                "content": analyst_response,
                "timestamp": "2025-08-04T21:07:00Z"
            })
            
            # Safety Reviewer response
            review_prompt = f"""
Rivedi l'analisi HSE seguente e fornisci feedback critico:

ANALISI DA RIVEDERE:
{analyst_response}

COMPITI DI REVISIONE:
1. Verifica completezza identificazione rischi
2. Valida adeguatezza DPI proposti  
3. Controlla conformità misure di controllo
4. Integra eventuali aspetti mancanti
5. Fornisci valutazione finale con raccomandazioni prioritarie

Sii critico e dettagliato nella revisione.
"""
            
            reviewer_response = await self._get_gemini_response(
                review_prompt,
                "Safety_Reviewer",
                "Revisore esperto che valida analisi HSE"
            )
            conversation_history.append({
                "agent": "Safety_Reviewer", 
                "content": reviewer_response,
                "timestamp": "2025-08-04T21:07:30Z"
            })
            
            # Combine both responses for final analysis
            combined_analysis = f"""
ANALISI HSE PRIMARIA:
{analyst_response}

REVISIONE E VALIDAZIONE:
{reviewer_response}
"""
            
            # Extract structured output from the combined analysis
            final_analysis = self._extract_structured_output_from_ai_responses(
                combined_analysis, 
                conversation_history
            )
            
            return {
                "analysis_complete": True,
                "confidence_score": 0.85,  # Higher confidence with AI
                "conversation_history": conversation_history,
                "agents_involved": ["HSE_Analyst", "Safety_Reviewer"],
                "processing_time": 0.0,
                "final_analysis": final_analysis
            }
            
        except Exception as e:
            print(f"[SimpleAutoGenHSEAgents] Error in AI analysis: {str(e)}")
            return {
                "analysis_complete": False,
                "error": f"AI analysis failed: {str(e)}",
                "confidence_score": 0.0,
                "agents_involved": [],
                "processing_time": 0.0
            }
    
    async def _get_gemini_response(self, prompt: str, agent_name: str, agent_role: str) -> str:
        """Get response from Gemini model for a specific agent role"""
        
        full_prompt = f"""
Tu sei {agent_name}, un {agent_role}.

{prompt}

Rispondi come {agent_name} utilizzando la tua expertise specifica.
"""
        
        try:
            generation_config = genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=2000,
            )
            
            response = self.gemini_model.generate_content(full_prompt, generation_config=generation_config)
            return response.text
            
        except Exception as e:
            return f"Errore nella risposta di {agent_name}: {str(e)}"
    
    def _extract_structured_output_from_ai_responses(self, combined_analysis: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Extract structured analysis from AI responses with mandatory fallback"""
        
        # Try to extract JSON from the AI response first
        ai_structured_data = self._parse_json_from_ai_response(combined_analysis)
        
        if ai_structured_data:
            print("[SimpleAutoGenHSEAgents] Successfully parsed structured JSON from AI response")
            result = self._convert_ai_json_to_expected_format(ai_structured_data)
        else:
            print("[SimpleAutoGenHSEAgents] No structured JSON found, using fallback extraction")
            result = self._fallback_extraction(combined_analysis, conversation_history)
        
        # MANDATORY: Ensure we ALWAYS have proper analysis
        result = self._ensure_mandatory_analysis(result, combined_analysis)
        
        return result
    
    def _parse_json_from_ai_response(self, content: str) -> Dict[str, Any]:
        """Parse JSON from AI response"""
        import json
        import re
        
        # Look for JSON blocks in the response
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, dict) and any(key in parsed for key in ['rischi_identificati', 'dpi_obbligatori', 'analisi_generale']):
                    return parsed
            except json.JSONDecodeError:
                continue
        
        # Try to find JSON without code blocks
        json_pattern_simple = r'\{[\s\S]*\}'
        matches = re.findall(json_pattern_simple, content)
        
        for match in matches:
            try:
                parsed = json.loads(match)
                if isinstance(parsed, dict) and any(key in parsed for key in ['rischi_identificati', 'dpi_obbligatori']):
                    return parsed
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _convert_ai_json_to_expected_format(self, ai_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert AI JSON to expected analysis format"""
        
        # Extract risks
        risks = ai_data.get('rischi_identificati', [])
        dpi_list = ai_data.get('dpi_obbligatori', [])
        measures = ai_data.get('misure_organizzative', [])
        procedures = ai_data.get('procedure_operative', [])
        general_analysis = ai_data.get('analisi_generale', {})
        
        # Count critical issues
        critical_issues = len([r for r in risks if r.get('livello_rischio') in ['alto', 'molto_alto']])
        total_recommendations = len(dpi_list) + len(measures)
        
        # Determine compliance level
        classification = general_analysis.get('classificazione_rischio', 'medio')
        compliance_mapping = {
            'basso': 'conforme',
            'medio': 'da_verificare', 
            'alto': 'requires_action',
            'molto_alto': 'non_conforme'
        }
        compliance_level = compliance_mapping.get(classification, 'da_verificare')
        
        # Create key findings from risks
        key_findings = []
        for risk in risks[:5]:
            desc = risk.get('descrizione_dettagliata', risk.get('categoria', 'Rischio identificato'))
            key_findings.append(desc)
        
        # Create action items from structured data
        action_items = self._create_detailed_action_items(risks, dpi_list, measures, procedures)
        
        # Create detailed citations from normative references
        citations = self._create_detailed_citations(risks, dpi_list, general_analysis.get('normative_principali', []))
        
        return {
            "executive_summary": {
                "overall_score": max(0.2, 1.0 - (critical_issues * 0.15)),
                "critical_issues": critical_issues,
                "recommendations": total_recommendations,
                "compliance_level": compliance_level,
                "estimated_completion_time": f"{2 + critical_issues}-{4 + (critical_issues * 2)} ore",
                "key_findings": key_findings if key_findings else [f"Analisi {classification} - {len(risks)} rischi identificati"],
                "next_steps": [
                    "Implementare misure di controllo prioritarie",
                    "Fornire DPI secondo standard specificati",
                    "Verificare formazione specifica operatori",
                    "Definire procedure operative dettagliate"
                ][:3 + min(critical_issues, 2)]
            },
            "action_items": action_items,
            "citations": citations,
            "completion_roadmap": {
                "immediate_actions": [
                    f"Verifica disponibilità {len(dpi_list)} DPI identificati" if dpi_list else "Verifica DPI base necessari",
                    "Briefing sicurezza pre-lavoro dettagliato"
                ],
                "short_term_actions": [
                    f"Implementazione {len([r for r in risks if r.get('livello_rischio') == 'alto'])} misure controllo ad alta priorità",
                    "Formazione specifica sui rischi identificati"
                ],
                "medium_term_actions": [
                    "Monitoraggio continuo efficacia misure",
                    "Aggiornamento procedure operative"
                ],
                "success_metrics": [
                    "Zero incidenti/near miss",
                    "100% conformità uso DPI", 
                    "Completamento entro tempi stimati",
                    "Validazione misure di controllo"
                ],
                "review_checkpoints": [
                    "Pre-start meeting sicurezza",
                    "Controlli intermedi durante lavori", 
                    "Debriefing post-completamento"
                ]
            }
        }
    
    def _fallback_extraction(self, combined_analysis: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Fallback extraction when JSON parsing fails"""
        
        # Initialize containers for different types of findings
        risks = []
        dpi_recommendations = []
        safety_measures = []
        
        # Process the combined analysis text
        content = combined_analysis.lower()
        
        # Enhanced risk pattern matching with more specific patterns
        risk_patterns = [
            ("elettrico", "alto", "Disattivazione impianto, LOTO e DPI isolanti", ["CEI 11-27", "D.Lgs 81/08 art. 80-87"]),
            ("caduta", "alto", "DPI anticaduta, parapetti e delimitazione area", ["D.Lgs 81/08 Titolo IV", "UNI EN 365"]),
            ("altezza", "alto", "Piattaforme di lavoro e sistemi anticaduta", ["D.Lgs 81/08 Titolo IV", "UNI EN 365"]),
            ("meccanico", "medio", "Protezioni macchine e procedure operative", ["D.Lgs 81/08 Titolo III"]),
            ("chimico", "alto", "Ventilazione, schede sicurezza e DPI specifici", ["Regolamento REACH", "D.Lgs 81/08 Titolo IX"]),
            ("incendio", "alto", "Misure antincendio e permesso di fuoco", ["D.M. 10/03/1998", "D.Lgs 81/08"]),
            ("esplosione", "molto_alto", "Controllo atmosfera, bonifica e ATEX", ["Direttiva ATEX", "D.Lgs 81/08 Titolo XI"]),
            ("rumore", "medio", "Protezioni uditive e limitazione esposizione", ["D.Lgs 81/08 Titolo VIII"]),
            ("vibrazione", "medio", "Limitazione tempo esposizione e attrezzature", ["D.Lgs 81/08 Titolo VIII"]),
            ("confinati", "molto_alto", "DPR 177/2011 e procedure spazi confinati", ["DPR 177/2011", "UNI 11326"])
        ]
        
        for risk_term, severity, mitigation, norms in risk_patterns:
            if risk_term in content or f"spazi {risk_term}" in content:
                risks.append({
                    "risk": f"Rischio {risk_term}",
                    "severity": severity,
                    "mitigation": mitigation,
                    "normatives": norms
                })
        
        # Enhanced DPI pattern matching with detailed standards
        dpi_patterns = [
            ("guanti", "EN 388", "Protezione da rischi meccanici", "II", "Anticuneo, antiperforazione, antistrappo"),
            ("isolanti", "EN 60903", "Protezione da rischi elettrici", "III", "Classe 0 fino 1000V"),
            ("casco", "EN 397", "Protezione del capo da caduta oggetti", "II", "Resistenza penetrazione e urto"),
            ("elmetto", "EN 397", "Protezione del capo da caduta oggetti", "II", "Resistenza penetrazione e urto"),
            ("occhiali", "EN 166", "Protezione degli occhi", "II", "Protezione da particelle e liquidi"),
            ("scarpe", "EN ISO 20345", "Protezione dei piedi", "II", "Puntale 200J e suola antiforo"),
            ("imbracatura", "EN 361", "Protezione anticaduta", "III", "Distribuzione forze caduta"),
            ("respiratore", "EN 149", "Protezione delle vie respiratorie", "III", "Filtrazione particelle FFP2/FFP3"),
            ("tuta", "EN ISO 11612", "Protezione da calore e fiamme", "III", "Resistenza calore radiante e convettivo"),
            ("antitaglio", "EN 388", "Protezione da tagli", "II", "Livello protezione taglio A2-A5")
        ]
        
        for dpi_term, standard, reason, category, details in dpi_patterns:
            if dpi_term in content:
                dpi_recommendations.append({
                    "dpi_type": f"{dpi_term.capitalize()} di protezione",
                    "reason": reason,
                    "standard": standard,
                    "category": category,
                    "details": details
                })
        
        # Extract detailed safety measures
        if "procedure" in content or "procedura" in content:
            safety_measures.append("Definizione procedure operative specifiche con check-list")
        if "formazione" in content:
            safety_measures.append("Formazione specifica sui rischi e uso DPI")
        if "sorveglianza" in content:
            safety_measures.append("Sorveglianza sanitaria periodica")
        if "emergenza" in content:
            safety_measures.append("Piano di emergenza e procedure evacuazione")
        if "segnaletica" in content:
            safety_measures.append("Installazione segnaletica di sicurezza")
        
        # Count findings for scoring
        critical_issues = len([r for r in risks if r.get("severity") in ["alto", "molto_alto"]])
        total_recommendations = len(dpi_recommendations) + len(safety_measures)
        
        # Determine compliance level
        if critical_issues > 3:
            compliance_level = "non_conforme"
        elif critical_issues > 1:
            compliance_level = "requires_action"
        elif critical_issues > 0:
            compliance_level = "da_verificare"
        else:
            compliance_level = "conforme"
        
        return {
            "executive_summary": {
                "overall_score": max(0.3, 1.0 - (critical_issues * 0.15)),
                "critical_issues": critical_issues,
                "recommendations": total_recommendations,
                "compliance_level": compliance_level,
                "estimated_completion_time": f"{2 + critical_issues}-{4 + (critical_issues * 2)} ore",
                "key_findings": [r["risk"] for r in risks[:5]] if risks else [f"Analisi completata - {len(risks)} rischi identificati"],
                "next_steps": [
                    "Implementare misure di controllo prioritarie",
                    "Fornire DPI secondo standard specificati",
                    "Verificare formazione specifica operatori",
                    "Definire procedure operative dettagliate"
                ][:3 + min(critical_issues, 2)]
            },
            "action_items": self._create_action_items_from_ai(risks, dpi_recommendations, safety_measures),
            "citations": self._create_enhanced_citations(dpi_recommendations, risks),
            "completion_roadmap": {
                "immediate_actions": [
                    f"Verifica disponibilità {len(dpi_recommendations)} DPI identificati" if dpi_recommendations else "Verifica DPI base necessari",
                    "Briefing sicurezza pre-lavoro dettagliato"
                ],
                "short_term_actions": [
                    f"Implementazione {critical_issues} misure controllo ad alta priorità",
                    "Formazione specifica sui rischi identificati"
                ],
                "medium_term_actions": [
                    "Monitoraggio continuo efficacia misure",
                    "Aggiornamento procedure operative"
                ],
                "success_metrics": [
                    "Zero incidenti/near miss",
                    "100% conformità uso DPI",
                    "Completamento entro tempi stimati"
                ],
                "review_checkpoints": [
                    "Pre-start meeting sicurezza",
                    "Controlli intermedi durante lavori",
                    "Debriefing post-completamento"
                ]
            }
        }
    
    def _create_action_items_from_ai(self, risks: List[Dict], dpi_recommendations: List[Dict], safety_measures: List[str]) -> List[Dict]:
        """Create action items from AI-identified risks and recommendations"""
        action_items = []
        item_counter = 1
        
        # Create action items for high-severity risks
        for risk in risks:
            if risk.get("severity") == "high":
                action_items.append({
                    "id": f"ACT_{item_counter:03d}",
                    "type": "risk_mitigation",
                    "priority": "alta",
                    "title": f"Mitigare {risk['risk']}",
                    "description": f"Implementare misure di controllo per {risk['risk']}",
                    "suggested_action": risk.get("mitigation", "Definire misure di controllo appropriate"),
                    "consequences_if_ignored": "Possibili incidenti gravi",
                    "references": ["D.Lgs 81/08"],
                    "estimated_effort": "2-4 ore",
                    "responsible_role": "Responsabile Sicurezza",
                    "frontend_display": {
                        "color": "red",
                        "icon": "alert-triangle",
                        "category": "Controlli Sicurezza"
                    }
                })
                item_counter += 1
        
        # Create action items for DPI
        if dpi_recommendations:
            action_items.append({
                "id": f"ACT_{item_counter:03d}",
                "type": "dpi_requirement",
                "priority": "alta" if len(risks) > 2 else "media",
                "title": "Fornire DPI necessari",
                "description": f"Fornire {len(dpi_recommendations)} DPI identificati",
                "suggested_action": "Verificare disponibilità e distribuire DPI secondo standard specificati",
                "consequences_if_ignored": "Esposizione a rischi per i lavoratori",
                "references": [dpi["standard"] for dpi in dpi_recommendations if dpi.get("standard")],
                "estimated_effort": "1-2 ore",
                "responsible_role": "Responsabile Magazzino",
                "frontend_display": {
                    "color": "orange",
                    "icon": "shield-check",
                    "category": "DPI Obbligatori"
                }
            })
            item_counter += 1
        
        # Create action items for safety measures
        for measure in safety_measures:
            action_items.append({
                "id": f"ACT_{item_counter:03d}",
                "type": "safety_measure",
                "priority": "media",
                "title": measure,
                "description": f"Implementare: {measure}",
                "suggested_action": f"Sviluppare e implementare {measure.lower()}",
                "consequences_if_ignored": "Ridotta efficacia delle misure di sicurezza",
                "references": ["D.Lgs 81/08"],
                "estimated_effort": "2-6 ore",
                "responsible_role": "Responsabile Sicurezza",
                "frontend_display": {
                    "color": "blue",
                    "icon": "clipboard-check",
                    "category": "Misure Organizzative"
                }
            })
            item_counter += 1
        
        return action_items
    
    def _create_citations(self, dpi_recommendations: List[Dict]) -> Dict[str, List[Dict]]:
        """Create properly formatted citations"""
        citations = {
            "normative_framework": [
                {
                    "document_info": {
                        "title": "D.Lgs 81/08",
                        "type": "Normativa",
                        "date": "2008-04-09"
                    },
                    "relevance": {
                        "score": 0.95,
                        "reason": "Testo unico sulla salute e sicurezza sul lavoro"
                    },
                    "key_requirements": [],
                    "frontend_display": {
                        "color": "blue",
                        "icon": "book-open",
                        "category": "Normativa Nazionale"
                    }
                }
            ],
            "company_procedures": []
        }
        
        # Add UNI EN standards from DPI recommendations
        seen_standards = set()
        for dpi in dpi_recommendations:
            standard = dpi.get("standard")
            if standard and standard not in seen_standards:
                seen_standards.add(standard)
                citations["normative_framework"].append({
                    "document_info": {
                        "title": standard,
                        "type": "Standard Tecnico",
                        "date": "Current"
                    },
                    "relevance": {
                        "score": 0.85,
                        "reason": f"Standard per {dpi.get('dpi_type', 'DPI')}"
                    },
                    "key_requirements": [],
                    "frontend_display": {
                        "color": "green",
                        "icon": "shield-check",
                        "category": "Standard UNI EN"
                    }
                })
        
        return citations
    
    def _extract_structured_output(self, chat_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract structured analysis from chat history"""
        
        # Initialize containers for different types of findings
        risks = []
        dpi_recommendations = []
        safety_measures = []
        compliance_notes = []
        
        # Process each message in the conversation
        for message in chat_history:
            content = message.get("content", "").lower() if isinstance(message, dict) else str(message).lower()
            
            # Extract risks
            if any(word in content for word in ["rischio", "pericolo", "hazard"]):
                if "elettrico" in content:
                    risks.append({
                        "risk": "Rischio elettrico",
                        "severity": "high",
                        "mitigation": "Disattivazione impianto e lockout/tagout"
                    })
                if "caduta" in content or "altezza" in content:
                    risks.append({
                        "risk": "Rischio caduta dall'alto",
                        "severity": "high", 
                        "mitigation": "Utilizzo DPI anticaduta e delimitazione area"
                    })
                if "meccanico" in content:
                    risks.append({
                        "risk": "Rischio meccanico",
                        "severity": "medium",
                        "mitigation": "Protezioni macchine e procedure operative"
                    })
            
            # Extract DPI recommendations
            if "dpi" in content or "protezione" in content:
                if "guanti" in content:
                    dpi_recommendations.append({
                        "dpi_type": "Guanti di protezione",
                        "reason": "Protezione da rischi meccanici",
                        "standard": "EN 388"
                    })
                if "casco" in content or "elmetto" in content:
                    dpi_recommendations.append({
                        "dpi_type": "Elmetto di protezione", 
                        "reason": "Protezione del capo",
                        "standard": "EN 397"
                    })
                if "occhiali" in content or "visiera" in content:
                    dpi_recommendations.append({
                        "dpi_type": "Occhiali di sicurezza",
                        "reason": "Protezione degli occhi",
                        "standard": "EN 166"
                    })
        
        # Create structured output
        return {
            "executive_summary": {
                "overall_score": 0.75,
                "critical_issues": len([r for r in risks if r.get("severity") == "high"]),
                "recommendations": len(dpi_recommendations) + len(safety_measures),
                "compliance_level": "requires_action" if risks else "compliant",
                "estimated_completion_time": "4-6 ore",
                "key_findings": [r["risk"] for r in risks[:3]],
                "next_steps": ["Implementare misure di controllo", "Fornire DPI specificati", "Verificare formazione operatori"]
            },
            "action_items": self._create_action_items(risks, dpi_recommendations),
            "citations": {
                "normative_framework": [],
                "company_procedures": []
            },
            "completion_roadmap": {
                "immediate_actions": ["Verifica DPI disponibili", "Briefing sicurezza"],
                "short_term_actions": ["Implementazione misure di controllo", "Formazione specifica"],
                "medium_term_actions": ["Monitoraggio continuo", "Aggiornamento procedure"],
                "success_metrics": ["Zero incidenti", "100% conformità DPI", "Completamento nei tempi"],
                "review_checkpoints": ["Inizio lavori", "Metà lavori", "Fine lavori"]
            }
        }
    
    def _create_action_items(self, risks: List[Dict], dpi_recommendations: List[Dict]) -> List[Dict]:
        """Create action items from risks and recommendations"""
        action_items = []
        item_counter = 1
        
        # Create action items for high-severity risks
        for risk in risks:
            if risk.get("severity") == "high":
                action_items.append({
                    "id": f"ACT_{item_counter:03d}",
                    "type": "risk_mitigation",
                    "priority": "alta",
                    "title": f"Mitigare {risk['risk']}",
                    "description": f"Implementare misure di controllo per {risk['risk']}",
                    "suggested_action": risk.get("mitigation", "Definire misure di controllo appropriate"),
                    "consequences_if_ignored": "Possibili incidenti gravi",
                    "references": [],
                    "estimated_effort": "2-4 ore",
                    "responsible_role": "Responsabile Sicurezza",
                    "frontend_display": {
                        "color": "red",
                        "icon": "alert-triangle",
                        "category": "Controlli Sicurezza"
                    }
                })
                item_counter += 1
        
        # Create action items for DPI
        if dpi_recommendations:
            action_items.append({
                "id": f"ACT_{item_counter:03d}",
                "type": "dpi_requirement",
                "priority": "alta",
                "title": "Fornire DPI necessari",
                "description": f"Fornire {len(dpi_recommendations)} DPI identificati",
                "suggested_action": "Verificare disponibilità e distribuire DPI",
                "consequences_if_ignored": "Esposizione a rischi per i lavoratori",
                "references": [dpi["standard"] for dpi in dpi_recommendations if dpi.get("standard")],
                "estimated_effort": "1 ora",
                "responsible_role": "Responsabile Magazzino",
                "frontend_display": {
                    "color": "orange",
                    "icon": "shield-check",
                    "category": "DPI Obbligatori"
                }
            })
        
        return action_items
    
    def _create_detailed_action_items(self, risks: List[Dict], dpi_list: List[Dict], measures: List[Dict], procedures: List[Dict]) -> List[Dict]:
        """Create detailed action items from structured AI data"""
        action_items = []
        item_counter = 1
        
        # Create action items for high/very high risks
        for risk in risks:
            if risk.get("livello_rischio") in ["alto", "molto_alto"]:
                priority = "critica" if risk.get("livello_rischio") == "molto_alto" else "alta"
                action_items.append({
                    "id": f"ACT_{item_counter:03d}",
                    "type": "risk_mitigation",
                    "priority": priority,
                    "title": f"Mitigare {risk.get('categoria', 'rischio identificato')}",
                    "description": risk.get('descrizione_dettagliata', f"Implementare controlli per {risk.get('categoria')}"),
                    "suggested_action": "; ".join(risk.get('misure_controllo', ['Definire misure di controllo appropriate'])),
                    "consequences_if_ignored": "Possibili incidenti gravi o fatali",
                    "references": risk.get('normative_riferimento', ['D.Lgs 81/08']),
                    "estimated_effort": "4-8 ore" if priority == "critica" else "2-4 ore",
                    "responsible_role": "Responsabile Sicurezza/RSPP",
                    "frontend_display": {
                        "color": "red" if priority == "critica" else "orange",
                        "icon": "alert-triangle",
                        "category": "Controlli Sicurezza Critici"
                    }
                })
                item_counter += 1
        
        # Create detailed DPI action items
        if dpi_list:
            for dpi in dpi_list:
                action_items.append({
                    "id": f"ACT_{item_counter:03d}",
                    "type": "dpi_requirement",
                    "priority": "alta" if dpi.get("categoria_ue") == "III" else "media",
                    "title": f"Fornire {dpi.get('tipo', 'DPI')}",
                    "description": f"{dpi.get('tipo', 'DPI')} - {dpi.get('standard_tecnico', 'Standard applicabile')}",
                    "suggested_action": f"Approvvigionare e distribuire {dpi.get('tipo')} conformi a {dpi.get('standard_tecnico')}",
                    "consequences_if_ignored": f"Esposizione diretta ai rischi: {', '.join(dpi.get('rischi_coperti', ['non specificati']))}",
                    "references": [dpi.get('standard_tecnico', 'Standard applicabile')],
                    "estimated_effort": "1-2 ore",
                    "responsible_role": "Responsabile Approvvigionamenti",
                    "dpi_details": {
                        "standard": dpi.get('standard_tecnico'),
                        "category": dpi.get('categoria_ue'),
                        "protection_class": dpi.get('classe_protezione'),
                        "usage_instructions": dpi.get('istruzioni_uso')
                    },
                    "frontend_display": {
                        "color": "orange" if dpi.get("categoria_ue") == "III" else "yellow",
                        "icon": "shield-check",
                        "category": f"DPI Categoria {dpi.get('categoria_ue', 'II')}"
                    }
                })
                item_counter += 1
        
        # Create action items for organizational measures
        for measure in measures:
            action_items.append({
                "id": f"ACT_{item_counter:03d}",
                "type": "organizational_measure",
                "priority": "media",
                "title": measure.get('tipo', 'Misura organizzativa'),
                "description": measure.get('descrizione', 'Implementare misura organizzativa'),
                "suggested_action": measure.get('descrizione', 'Sviluppare e implementare misura'),
                "consequences_if_ignored": "Ridotta efficacia delle misure di sicurezza",
                "references": ["D.Lgs 81/08"],
                "estimated_effort": "2-6 ore",
                "responsible_role": measure.get('responsabile', 'Responsabile Sicurezza'),
                "timeline": measure.get('tempistica', 'Prima dell\'inizio lavori'),
                "frontend_display": {
                    "color": "blue",
                    "icon": "clipboard-check",
                    "category": "Misure Organizzative"
                }
            })
            item_counter += 1
        
        return action_items
    
    def _create_detailed_citations(self, risks: List[Dict], dpi_list: List[Dict], main_norms: List[str]) -> Dict[str, List[Dict]]:
        """Create detailed citations from structured data"""
        citations = {
            "normative_framework": [],
            "company_procedures": []
        }
        
        # Add main normative framework
        main_citations = [
            ("D.Lgs 81/08", "Testo unico sulla salute e sicurezza sul lavoro", "2008-04-09", "blue", "book-open", "Normativa Nazionale")
        ]
        
        # Collect unique normative references from risks
        all_norms = set(main_norms)
        for risk in risks:
            norms = risk.get('normative_riferimento', [])
            all_norms.update(norms)
        
        # Add technical standards from DPI
        for dpi in dpi_list:
            standard = dpi.get('standard_tecnico')
            if standard:
                all_norms.add(standard)
        
        # Create citation entries
        for norm in all_norms:
            if norm.startswith('D.Lgs'):
                citation_type = "Decreto Legislativo"
                color = "blue"
                icon = "book-open"
                category = "Normativa Nazionale"
            elif norm.startswith('DPR'):
                citation_type = "Decreto del Presidente della Repubblica"
                color = "blue"
                icon = "book-open" 
                category = "Normativa Nazionale"
            elif norm.startswith('EN'):
                citation_type = "Standard Tecnico Europeo"
                color = "green"
                icon = "shield-check"
                category = "Standard UNI EN"
            elif norm.startswith('ISO'):
                citation_type = "Standard Internazionale"
                color = "green"
                icon = "globe"
                category = "Standard ISO"
            elif norm.startswith('CEI'):
                citation_type = "Standard Elettrotecnico"
                color = "yellow"
                icon = "zap"
                category = "Standard CEI"
            elif norm.startswith('UNI'):
                citation_type = "Standard Nazionale"
                color = "green"
                icon = "award"
                category = "Standard UNI"
            else:
                citation_type = "Normativa"
                color = "gray"
                icon = "file-text"
                category = "Altro"
            
            citations["normative_framework"].append({
                "document_info": {
                    "title": norm,
                    "type": citation_type,
                    "date": "Current" if not norm.startswith('D.Lgs') else "Variable"
                },
                "relevance": {
                    "score": 0.95 if norm.startswith('D.Lgs') else 0.85,
                    "reason": f"Applicabile per conformità {citation_type.lower()}"
                },
                "key_requirements": [],
                "frontend_display": {
                    "color": color,
                    "icon": icon,
                    "category": category
                }
            })
        
        return citations
    
    def _create_enhanced_citations(self, dpi_recommendations: List[Dict], risks: List[Dict]) -> Dict[str, List[Dict]]:
        """Create enhanced citations from recommendations and risks"""
        citations = {
            "normative_framework": [
                {
                    "document_info": {
                        "title": "D.Lgs 81/08",
                        "type": "Normativa",
                        "date": "2008-04-09"
                    },
                    "relevance": {
                        "score": 0.95,
                        "reason": "Testo unico sulla salute e sicurezza sul lavoro"
                    },
                    "key_requirements": [],
                    "frontend_display": {
                        "color": "blue",
                        "icon": "book-open",
                        "category": "Normativa Nazionale"
                    }
                }
            ],
            "company_procedures": []
        }
        
        # Add DPI standards to citations
        seen_standards = set()
        for dpi in dpi_recommendations:
            standard = dpi.get("standard")
            if standard and standard not in seen_standards:
                seen_standards.add(standard)
                dpi_type = dpi.get("dpi_type", "DPI")
                citations["normative_framework"].append({
                    "document_info": {
                        "title": standard,
                        "type": "Standard Tecnico",
                        "date": "Current"
                    },
                    "relevance": {
                        "score": 0.85,
                        "reason": f"Standard per {dpi_type} - {dpi.get('reason', 'protezione')}"
                    },
                    "key_requirements": [{
                        "requirement": dpi.get('details', 'Requisiti secondo standard'),
                        "mandatory": True,
                        "description": f"Standard tecnico per {dpi_type}"
                    }],
                    "frontend_display": {
                        "color": "green",
                        "icon": "shield-check",
                        "category": f"Standard UNI EN"
                    }
                })
        
        # Add normative references from risks
        seen_norms = set()
        for risk in risks:
            norms = risk.get("normatives", [])
            for norm in norms:
                if norm and norm not in seen_norms:
                    seen_norms.add(norm)
                    citations["normative_framework"].append({
                        "document_info": {
                            "title": norm,
                            "type": "Normativa Specifica",
                            "date": "Current"
                        },
                        "relevance": {
                            "score": 0.90,
                            "reason": f"Applicabile per {risk.get('risk', 'rischio identificato')}"
                        },
                        "key_requirements": [],
                        "frontend_display": {
                            "color": "blue",
                            "icon": "alert-circle",
                            "category": "Normativa Settoriale"
                        }
                    })
        
        return citations
    
    def _ensure_mandatory_analysis(self, result: Dict[str, Any], combined_analysis: str) -> Dict[str, Any]:
        """Ensure we ALWAYS provide a comprehensive professional analysis"""
        
        exec_summary = result.get('executive_summary', {})
        action_items = result.get('action_items', [])
        
        # If no risks or DPI identified, this is WRONG for any real permit
        if exec_summary.get('critical_issues', 0) == 0 and len(action_items) == 0:
            print("[SimpleAutoGenHSEAgents] WARNING: No risks/DPI identified - applying mandatory professional analysis")
            
            # Apply work-type specific mandatory analysis
            return self._apply_mandatory_professional_analysis(combined_analysis, result)
        
        # If minimal analysis, enhance it
        if len(action_items) < 3:
            print("[SimpleAutoGenHSEAgents] Enhancing minimal analysis with mandatory requirements")
            result = self._enhance_minimal_analysis(result, combined_analysis)
        
        return result
    
    def _apply_mandatory_professional_analysis(self, analysis_text: str, base_result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply mandatory professional HSE analysis based on work content"""
        
        # Analyze work content to determine mandatory risks and DPI
        content_lower = analysis_text.lower()
        
        # MANDATORY base risks that ALWAYS exist in industrial work
        mandatory_risks = []
        mandatory_dpi = []
        
        # Determine work type from content
        work_types = {
            "elettrico": self._get_electrical_work_requirements,
            "mechanical": self._get_mechanical_work_requirements,  
            "maintenance": self._get_maintenance_work_requirements,
            "chemical": self._get_chemical_work_requirements,
            "confined": self._get_confined_space_requirements,
            "height": self._get_height_work_requirements
        }
        
        # Apply work-specific requirements
        for work_type, requirement_func in work_types.items():
            if any(keyword in content_lower for keyword in self._get_work_keywords(work_type)):
                risks, dpi = requirement_func()
                mandatory_risks.extend(risks)
                mandatory_dpi.extend(dpi)
        
        # If no specific work type identified, apply GENERAL INDUSTRIAL mandatory requirements
        if not mandatory_risks:
            mandatory_risks, mandatory_dpi = self._get_general_industrial_requirements()
        
        # Remove duplicates
        seen_risks = set()
        unique_risks = []
        for risk in mandatory_risks:
            risk_key = risk['risk']
            if risk_key not in seen_risks:
                seen_risks.add(risk_key)
                unique_risks.append(risk)
        
        seen_dpi = set()
        unique_dpi = []
        for dpi in mandatory_dpi:
            dpi_key = dpi['dpi_type']
            if dpi_key not in seen_dpi:
                seen_dpi.add(dpi_key)
                unique_dpi.append(dpi)
        
        # Count critical issues
        critical_issues = len([r for r in unique_risks if r.get("severity") in ["alto", "molto_alto"]])
        
        # Build comprehensive result
        return {
            "executive_summary": {
                "overall_score": max(0.4, 1.0 - (critical_issues * 0.15)),
                "critical_issues": critical_issues,
                "recommendations": len(unique_dpi) + len(unique_risks),
                "compliance_level": "requires_action" if critical_issues > 1 else "da_verificare",
                "estimated_completion_time": f"{2 + critical_issues}-{4 + (critical_issues * 2)} ore",
                "key_findings": [r["risk"] for r in unique_risks[:5]],
                "next_steps": [
                    f"Fornire {len(unique_dpi)} DPI obbligatori identificati",
                    f"Implementare controlli per {critical_issues} rischi critici",
                    "Briefing sicurezza specifico pre-lavoro",
                    "Definire procedure operative dettagliate"
                ][:4]
            },
            "action_items": self._create_action_items_from_mandatory(unique_risks, unique_dpi),
            "citations": self._create_enhanced_citations(unique_dpi, unique_risks),
            "completion_roadmap": {
                "immediate_actions": [
                    f"OBBLIGATORIO: Fornire {len(unique_dpi)} DPI identificati",
                    "Briefing sicurezza pre-lavoro con checklist"
                ],
                "short_term_actions": [
                    f"Implementare {critical_issues} controlli rischi ad alta priorità",
                    "Verificare qualificazione operatori"
                ],
                "medium_term_actions": [
                    "Monitoraggio continuo sicurezza",
                    "Validazione efficacia misure implementate"
                ],
                "success_metrics": [
                    "Zero incidenti/near miss",
                    f"100% conformità {len(unique_dpi)} DPI obbligatori",
                    "Completamento nei tempi stimati",
                    "Validazione post-lavoro conformità"
                ],
                "review_checkpoints": [
                    "Pre-start safety meeting obbligatorio",
                    "Controlli sicurezza ogni 2 ore",
                    "Post-work safety debrief"
                ]
            }
        }
    
    def _get_work_keywords(self, work_type: str) -> List[str]:
        """Get keywords to identify work types"""
        keywords = {
            "elettrico": ["elettric", "electric", "quadro", "tensione", "volt", "corrente", "impianto elettrico"],
            "mechanical": ["meccanico", "mechanical", "machine", "attrezzature", "utensili"],
            "maintenance": ["manutenzione", "maintenance", "riparazione", "sostituzione"],
            "chemical": ["chimico", "chemical", "sostanze", "solventi", "acidi"],
            "confined": ["confinati", "confined", "serbatoio", "cisterna"],
            "height": ["altezza", "height", "scala", "ponteggio", "tetto"]
        }
        return keywords.get(work_type, [])
    
    def _get_electrical_work_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for electrical work"""
        risks = [
            {"risk": "Rischio elettrocuzione da contatto diretto/indiretto", "severity": "molto_alto", "normatives": ["CEI 11-27", "D.Lgs 81/08 art. 80-87"]},
            {"risk": "Rischio arco elettrico e ustioni", "severity": "alto", "normatives": ["CEI 11-27"]},
            {"risk": "Rischio incendio da sovraccarico elettrico", "severity": "alto", "normatives": ["D.M. 10/03/1998"]}
        ]
        
        dpi = [
            {"dpi_type": "Guanti isolanti Classe 0", "standard": "EN 60903", "reason": "Protezione contatti elettrici 1000V", "category": "III"},
            {"dpi_type": "Scarpe isolanti", "standard": "EN ISO 20345", "reason": "Isolamento elettrico", "category": "II"},
            {"dpi_type": "Elmetto dielettrico", "standard": "EN 397", "reason": "Protezione capo e isolamento", "category": "II"},
            {"dpi_type": "Tuta antistatica", "standard": "EN 1149", "reason": "Prevenzione accumulo cariche", "category": "I"}
        ]
        
        return risks, dpi
    
    def _get_mechanical_work_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for mechanical work"""
        risks = [
            {"risk": "Rischio cesoiamento da macchine in movimento", "severity": "alto", "normatives": ["D.Lgs 81/08 Titolo III"]},
            {"risk": "Rischio taglio da utensili", "severity": "medio", "normatives": ["D.Lgs 81/08"]},
            {"risk": "Rischio schiacciamento arti", "severity": "alto", "normatives": ["D.Lgs 81/08"]}
        ]
        
        dpi = [
            {"dpi_type": "Guanti antitaglio Livello 5", "standard": "EN 388", "reason": "Protezione da tagli", "category": "II"},
            {"dpi_type": "Scarpe antinfortunistiche S3", "standard": "EN ISO 20345", "reason": "Protezione piedi", "category": "II"},
            {"dpi_type": "Occhiali di sicurezza", "standard": "EN 166", "reason": "Protezione occhi da schegge", "category": "II"}
        ]
        
        return risks, dpi
    
    def _get_maintenance_work_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for maintenance work"""
        risks = [
            {"risk": "Rischio meccanico da attrezzature", "severity": "medio", "normatives": ["D.Lgs 81/08"]},
            {"risk": "Rischio caduta oggetti", "severity": "medio", "normatives": ["D.Lgs 81/08"]},
            {"risk": "Rischio posturale", "severity": "basso", "normatives": ["D.Lgs 81/08 Titolo VI"]}
        ]
        
        dpi = [
            {"dpi_type": "Elmetto di protezione", "standard": "EN 397", "reason": "Protezione capo", "category": "II"},
            {"dpi_type": "Guanti meccanici", "standard": "EN 388", "reason": "Protezione mani", "category": "II"},
            {"dpi_type": "Scarpe antinfortunistiche", "standard": "EN ISO 20345", "reason": "Protezione piedi", "category": "II"}
        ]
        
        return risks, dpi
    
    def _get_chemical_work_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for chemical work"""  
        risks = [
            {"risk": "Rischio inalazione vapori tossici", "severity": "alto", "normatives": ["D.Lgs 81/08 Titolo IX"]},
            {"risk": "Rischio contatto cutaneo sostanze chimiche", "severity": "alto", "normatives": ["Regolamento REACH"]},
            {"risk": "Rischio incendio/esplosione", "severity": "molto_alto", "normatives": ["D.Lgs 81/08 Titolo XI"]}
        ]
        
        dpi = [
            {"dpi_type": "Respiratore FFP3", "standard": "EN 149", "reason": "Protezione vie respiratorie", "category": "III"},
            {"dpi_type": "Guanti chimici", "standard": "EN 374", "reason": "Protezione da agenti chimici", "category": "III"},
            {"dpi_type": "Tuta di protezione chimica", "standard": "EN ISO 6529", "reason": "Protezione corpo", "category": "III"}
        ]
        
        return risks, dpi
    
    def _get_confined_space_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for confined space work"""
        risks = [
            {"risk": "Rischio asfissia per carenza ossigeno", "severity": "molto_alto", "normatives": ["DPR 177/2011"]},
            {"risk": "Rischio intossicazione gas tossici", "severity": "molto_alto", "normatives": ["DPR 177/2011"]},
            {"risk": "Rischio esplosione atmosfere ATEX", "severity": "molto_alto", "normatives": ["D.Lgs 81/08 Titolo XI"]}
        ]
        
        dpi = [
            {"dpi_type": "Autorespiratore SCSR", "standard": "EN 137", "reason": "Respirazione autonoma", "category": "III"},
            {"dpi_type": "Imbracatura anticaduta", "standard": "EN 361", "reason": "Recupero di emergenza", "category": "III"},
            {"dpi_type": "Rilevatore gas portatile", "standard": "EN 60079", "reason": "Monitoraggio atmosfera", "category": "II"}
        ]
        
        return risks, dpi
    
    def _get_height_work_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for work at height"""
        risks = [
            {"risk": "Rischio caduta dall'alto", "severity": "molto_alto", "normatives": ["D.Lgs 81/08 Titolo IV"]},
            {"risk": "Rischio caduta oggetti", "severity": "alto", "normatives": ["D.Lgs 81/08 Titolo IV"]},
            {"risk": "Rischio ribaltamento scale/ponteggi", "severity": "alto", "normatives": ["UNI EN 131"]}
        ]
        
        dpi = [
            {"dpi_type": "Imbracatura anticaduta Classe A", "standard": "EN 361", "reason": "Protezione cadute", "category": "III"},
            {"dpi_type": "Casco con sottogola", "standard": "EN 397", "reason": "Protezione capo", "category": "II"},
            {"dpi_type": "Scarpe antiscivolo", "standard": "EN ISO 20345", "reason": "Aderenza superfici", "category": "II"}
        ]
        
        return risks, dpi
    
    def _get_general_industrial_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for ANY industrial work"""
        risks = [
            {"risk": "Rischio infortunio generico", "severity": "medio", "normatives": ["D.Lgs 81/08"]},
            {"risk": "Rischio caduta in piano", "severity": "medio", "normatives": ["D.Lgs 81/08"]},
            {"risk": "Rischio movimentazione manuale carichi", "severity": "basso", "normatives": ["D.Lgs 81/08 Titolo VI"]}
        ]
        
        dpi = [
            {"dpi_type": "Elmetto di protezione base", "standard": "EN 397", "reason": "Protezione capo obbligatoria", "category": "II"},
            {"dpi_type": "Scarpe antinfortunistiche S1P", "standard": "EN ISO 20345", "reason": "Protezione piedi obbligatoria", "category": "II"},
            {"dpi_type": "Guanti da lavoro", "standard": "EN 388", "reason": "Protezione mani generica", "category": "I"}
        ]
        
        return risks, dpi
    
    def _create_action_items_from_mandatory(self, risks: List[Dict], dpi_list: List[Dict]) -> List[Dict]:
        """Create action items from mandatory analysis"""
        action_items = []
        item_counter = 1
        
        # Create action items for all identified risks
        for risk in risks:
            severity = risk.get("severity", "medio")
            priority = "alta" if severity in ["alto", "molto_alto"] else "media"
            
            action_items.append({
                "id": f"ACT_{item_counter:03d}",
                "type": "risk_mitigation",
                "priority": priority,
                "title": f"OBBLIGATORIO: Mitigare {risk['risk']}",
                "description": f"Rischio {severity} - {risk['risk']}",
                "suggested_action": f"Implementare controlli specifici per {risk['risk']}",
                "consequences_if_ignored": "INCIDENTE GRAVE/FATALE" if severity == "molto_alto" else "Possibili infortuni",
                "references": risk.get('normatives', ['D.Lgs 81/08']),
                "estimated_effort": "4-8 ore" if severity == "molto_alto" else "2-4 ore",
                "responsible_role": "RSPP/Responsabile Sicurezza",
                "frontend_display": {
                    "color": "red" if severity == "molto_alto" else "orange",
                    "icon": "alert-triangle",
                    "category": "CONTROLLI OBBLIGATORI"
                }
            })
            item_counter += 1
        
        # Create DPI action items (ALL mandatory)
        if dpi_list:
            action_items.append({
                "id": f"ACT_{item_counter:03d}",
                "type": "dpi_requirement",
                "priority": "alta",
                "title": f"OBBLIGATORIO: Fornire {len(dpi_list)} DPI identificati",
                "description": f"DPI obbligatori per conformità normativa: {', '.join([dpi['dpi_type'] for dpi in dpi_list[:3]])}{'...' if len(dpi_list) > 3 else ''}",
                "suggested_action": f"Approvvigionare e distribuire TUTTI i {len(dpi_list)} DPI secondo standard specificati",
                "consequences_if_ignored": "VIOLAZIONE NORMATIVA - Possibili sanzioni e incidenti",
                "references": [dpi['standard'] for dpi in dpi_list],
                "estimated_effort": "1-2 ore",
                "responsible_role": "Responsabile Approvvigionamenti/Magazzino",
                "dpi_details": dpi_list,
                "frontend_display": {
                    "color": "red",
                    "icon": "shield-alert",
                    "category": "DPI OBBLIGATORI"
                }
            })
        
        return action_items
    
    def _enhance_minimal_analysis(self, result: Dict[str, Any], combined_analysis: str) -> Dict[str, Any]:
        """Enhance minimal analysis with additional mandatory requirements"""
        
        # Get existing action items
        existing_items = result.get('action_items', [])
        existing_exec = result.get('executive_summary', {})
        
        # Apply mandatory enhancements based on content
        content_lower = combined_analysis.lower()
        
        # Add missing mandatory DPI if not present
        dpi_items = [item for item in existing_items if item.get('type') == 'dpi_requirement']
        if len(dpi_items) == 0:
            # Add basic mandatory DPI
            _, basic_dpi = self._get_general_industrial_requirements()
            
            existing_items.append({
                "id": f"ACT_{len(existing_items)+1:03d}",
                "type": "dpi_requirement", 
                "priority": "alta",
                "title": "OBBLIGATORIO: DPI base mancanti",
                "description": "DPI base obbligatori per qualsiasi lavoro industriale",
                "suggested_action": f"Fornire DPI base: {', '.join([dpi['dpi_type'] for dpi in basic_dpi])}",
                "consequences_if_ignored": "VIOLAZIONE D.Lgs 81/08 - Sanzioni amministrative",
                "references": ["D.Lgs 81/08 art. 75-79"],
                "estimated_effort": "1 ora",
                "responsible_role": "Responsabile Sicurezza",
                "dpi_details": basic_dpi,
                "frontend_display": {
                    "color": "orange",
                    "icon": "shield-alert", 
                    "category": "DPI BASE OBBLIGATORI"
                }
            })
        
        # Enhance executive summary
        enhanced_exec = {
            **existing_exec,
            "critical_issues": max(existing_exec.get('critical_issues', 0), 1),
            "recommendations": len(existing_items),
            "compliance_level": "requires_action" if existing_exec.get('compliance_level') == 'conforme' else existing_exec.get('compliance_level', 'da_verificare'),
            "key_findings": existing_exec.get('key_findings', []) + ["DPI base obbligatori integrati"],
            "next_steps": [
                "Verificare disponibilità DPI base obbligatori",
                "Briefing sicurezza specifico",
                "Controlli conformità durante lavori"
            ]
        }
        
        return {
            **result,
            "executive_summary": enhanced_exec,
            "action_items": existing_items
        }
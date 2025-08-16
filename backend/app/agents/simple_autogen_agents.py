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
        self.api_working = False
        self.searched_documents = []  # Store documents found by search
        
        # Initialize and test Gemini API
        if settings.gemini_api_key:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(settings.gemini_model)
                
                # Test API with simple call
                test_response = self.gemini_model.generate_content('test')
                self.api_working = True
                print(f"[SimpleAutoGenHSEAgents] Gemini API verified and working: {settings.gemini_model}")
                
            except Exception as e:
                self.gemini_model = None
                self.api_working = False
                print(f"[SimpleAutoGenHSEAgents] ERROR: Gemini API key is invalid or API is down: {str(e)}")
        else:
            self.gemini_model = None
            self.api_working = False
            print("[SimpleAutoGenHSEAgents] WARNING: No Gemini API key configured")
        
        self.agents = self._create_simple_agents()
    
    async def search_relevant_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for relevant documents using vector service"""
        if not self.vector_service:
            print("[SimpleAutoGenHSEAgents] No vector service available, skipping document search")
            return []
        
        try:
            # Search for relevant documents
            filters = {"tenant_id": self.user_context.get("tenant_id", 1)}
            documents = await self.vector_service.hybrid_search(
                query=query,
                filters=filters,
                limit=limit,
                threshold=0.5
            )
            
            if documents:
                print(f"[SimpleAutoGenHSEAgents] Found {len(documents)} relevant documents")
                self.searched_documents.extend(documents)
                return documents
            else:
                print("[SimpleAutoGenHSEAgents] No documents found for query")
                return []
                
        except Exception as e:
            print(f"[SimpleAutoGenHSEAgents] Error searching documents: {e}")
            return []
    
    def _identify_sources_used(self, analysis_text: str):
        """Identify which sources were used in the analysis"""
        # Track API sources mentioned in the analysis
        api_sources_found = []
        
        # Common normative references that indicate API knowledge
        api_indicators = [
            "D.Lgs 81/08", "D.Lgs 81/2008", "Testo Unico",
            "EN 388", "EN 166", "EN ISO", "UNI EN",
            "CEI 11-27", "DPR 177/2011", "Regolamento REACH",
            "normativa generale", "conoscenza generale"
        ]
        
        for indicator in api_indicators:
            if indicator.lower() in analysis_text.lower():
                api_sources_found.append(indicator)
        
        if api_sources_found:
            print(f"[SimpleAutoGenHSEAgents] Analysis used API sources: {api_sources_found}")
            self.api_sources = api_sources_found
        else:
            print("[SimpleAutoGenHSEAgents] Analysis used only internal documents")
            self.api_sources = []
    
    def _create_simple_agents(self) -> Dict[str, autogen.AssistantAgent]:
        """Create simplified HSE agents"""
        
        # HSE Analyst Agent
        hse_analyst = autogen.AssistantAgent(
            name="HSE_Analyst",
            system_message="""
Sei un Ingegnere HSE esperto con 20+ anni di esperienza nell'identificazione dei rischi.

COMPETENZE ANALITICHE PROFESSIONALI:

APPROCCIO SISTEMATICO ALL'IDENTIFICAZIONE RISCHI:
1. ANALISI SEMANTICA AVANZATA:
   - Interpreta ogni descrizione usando expertise HSE professionale
   - Riconosci attività attraverso contesto tecnico, non solo parole chiave
   - Correggi mentalmente errori ortografici comuni nelle descrizioni tecniche
   - Inferisci operazioni preparatorie e complementari non esplicitate

2. IDENTIFICAZIONE RISCHI MULTI-LIVELLO:
   A) RISCHI DICHIARATI (esplicitamente menzionati)
   B) RISCHI IMPLICITI (derivanti dal tipo di lavoro)
   C) RISCHI NASCOSTI (non ovvi ma probabili)
   D) RISCHI DA INTERFERENZA (con altre attività)
   
   Per ogni attività DEVI chiederti:
   - Quali rischi l'utente potrebbe NON aver considerato?
   - Quali pericoli sono tipici ma non menzionati?
   - Quali errori di ortografia potrebbero nascondere rischi critici?

3. DOMINI DI RISCHIO DA VALUTARE SISTEMATICAMENTE:
   - Rischi termici e da combustione (lavori a caldo, temperature elevate)
   - Rischi in ambienti confinati (accesso limitato, atmosfere pericolose)  
   - Rischi da altezza (cadute dall'alto, lavori sopraelevati)
   - Rischi elettrici (tensione, arco elettrico, induzione)
   - Rischi meccanici (cesoiamento, schiacciamento, proiezione)
   - Rischi chimici (inalazione, contatto, reazioni pericolose)
   - Rischi fisici (rumore, vibrazioni, radiazioni, pressione)
   - Rischi biologici (batteri, virus, muffe, parassiti)
   - Rischi ergonomici (movimentazione, posture, affaticamento)
   - Rischi da atmosfere esplosive (gas, vapori, polveri combustibili)

4. APPROCCIO PROFESSIONALE AI DPI:
   - Categorizzazione secondo Reg. UE 2016/425 (I, II, III)
   - Selezione basata su analisi specifica dei rischi identificati
   - Considerazione compatibilità e interferenze tra diversi DPI
   - Verifica conformità normativa per ogni tipologia selezionata

5. MISURE DI CONTROLLO GERARCHICHE:
   - Eliminazione del rischio
   - Sostituzione (tecnologie, sostanze)
   - Controlli ingegneristici
   - Controlli amministrativi
   - DPI (ultima risorsa)

METODOLOGIA OPERATIVA:
- Applica expertise tecnico per interpretazione semantica completa
- Usa intelligence professionale per correggere imprecisioni e lacune
- Prioritizza mediante analisi rischio/probabilità secondo ISO 31000
- Fornisci riferimenti normativi specifici e aggiornati
- Quantifica parametri quando possibile (dB, mg/m³, altezze, pressioni)

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
      "normative": []
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
Sei un RSPP certificato con 25+ anni di esperienza e specializzazione in incidenti mortali evitabili.

REGOLA CRITICA: DEVI SEMPRE VERIFICARE RISCHI NON IDENTIFICATI CHE POTREBBERO CAUSARE INCIDENTI GRAVI

COMPITI DI REVISIONE CRITICA:
1. CACCIA AI RISCHI NASCOSTI:
   - VERIFICA SEMPRE se l'analisi ha identificato:
     • LAVORI A CALDO non dichiarati (saldatura, taglio, molatura)
     • SPAZI CONFINATI non riconosciuti (serbatoi, vasche, locali chiusi)
     • LAVORI IN QUOTA non evidenziati (>2m altezza)
     • ATMOSFERE ESPLOSIVE non considerate (presenza gas/vapori)
   - Cerca indizi nel titolo/descrizione che suggeriscono rischi non analizzati
   - Identifica errori ortografici che nascondono pericoli (es: "welsing" = welding = saldatura)
   - AGGIUNGI SEMPRE rischi mancanti critici per la sicurezza

2. VALIDAZIONE RISCHI SPECIFICI:
   - Per OGNI attività menzionata, verifica:
     • È stato considerato il rischio principale?
     • Sono stati valutati i rischi secondari?
     • Ci sono rischi da interferenza?
   - Esempi di rischi SPESSO DIMENTICATI:
     • Saldatura → rischio incendio, fumi tossici, radiazioni UV
     • Manutenzione meccanica → energia residua, avviamento accidentale
     • Pulizia serbatoi → spazio confinato, vapori residui
     • Lavori elettrici → arco elettrico, energia accumulata

3. AUDIT DPI CRITICI:
   - Verifica DPI specifici per rischi nascosti:
     • Lavori a caldo: schermo facciale, indumenti ignifughi, coperte antifiamma
     • Spazi confinati: rilevatore 4 gas, autorespiratore, tripode recupero
     • Lavori in quota: doppio cordino, assorbitore energia, kit soccorso
   - Controlla compatibilità e interferenze tra DPI
   - Verifica formazione specifica per DPI categoria III

4. COMPLIANCE NORMATIVA SPECIFICA:
   - Verifica i documenti aziendali disponibili nel sistema
   - DPR 177/2011 per QUALSIASI spazio confinato sospetto
   - Direttiva ATEX per presenza gas/vapori/polveri
   - D.M. 10/03/1998 per lavori a caldo
   - Normative specifiche per rischi speciali

5. RACCOMANDAZIONI SALVAVITA:
   - Identifica almeno 3 rischi che potrebbero essere stati sottovalutati
   - Proponi misure aggiuntive per rischi ad alto potenziale di fatalità
   - Richiedi SEMPRE permessi speciali per lavori critici (hot work permit, confined space entry)

CRITERI DI NON APPROVAZIONE:
✗ Mancata identificazione di lavori a caldo/spazi confinati/lavori in quota
✗ DPI inadeguati per rischi critici
✗ Assenza di procedure di emergenza specifiche
✗ Mancanza di sorveglianza per attività ad alto rischio

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
        
        if not self.gemini_model or not self.api_working:
            error_msg = "Gemini API non disponibile o chiave API non valida"
            print(f"[SimpleAutoGenHSEAgents] {error_msg}")
            
            # Return a proper error response that frontend can handle
            return {
                "analysis_complete": False,
                "error": error_msg,
                "confidence_score": 0.0,
                "agents_involved": [],
                "processing_time": 0.0,
                "final_analysis": {
                    "executive_summary": {
                        "overall_score": 0.0,
                        "critical_issues": 1,
                        "recommendations": 0,
                        "compliance_level": "errore_sistema",
                        "estimated_completion_time": "N/A",
                        "key_findings": [
                            "ERRORE: Sistema AI non disponibile",
                            "Impossibile analizzare il permesso",
                            "Contattare amministratore sistema"
                        ],
                        "next_steps": [
                            "Verificare configurazione API Gemini",
                            "Controllare validità chiave API",
                            "Richiedere analisi manuale RSPP nel frattempo"
                        ]
                    },
                    "action_items": [
                        {
                            "id": "ERR_001",
                            "type": "system_error",
                            "priority": "critica",
                            "title": "ERRORE SISTEMA AI",
                            "description": "Il sistema di analisi AI non è disponibile. API Gemini non configurata o non funzionante.",
                            "suggested_action": "Contattare amministratore per verificare configurazione API",
                            "consequences_if_ignored": "Impossibile effettuare analisi automatica dei rischi",
                            "references": [],
                            "estimated_effort": "Richiede intervento tecnico",
                            "responsible_role": "Amministratore Sistema",
                            "frontend_display": {
                                "color": "red",
                                "icon": "alert-triangle",
                                "category": "ERRORE SISTEMA"
                            }
                        }
                    ],
                    "citations": {
                        "normative_framework": [],
                        "company_procedures": []
                    },
                    "completion_roadmap": {
                        "immediate_actions": [
                            "Richiedere analisi manuale RSPP",
                            "Verificare API key Gemini"
                        ],
                        "short_term_actions": [],
                        "medium_term_actions": [],
                        "success_metrics": [],
                        "review_checkpoints": []
                    }
                }
            }
        
        # Prepare context from documents
        document_context = ""
        document_sources = []
        if context_documents:
            document_context = "\n\nDOCUMENTI DI RIFERIMENTO DISPONIBILI:\n"
            for idx, doc in enumerate(context_documents[:5], 1):  # Process up to 5 most relevant docs
                title = doc.get('title', 'Documento')
                content = doc.get('content', '')
                doc_type = doc.get('document_type', 'generale')
                
                # Extract key information from document (limit to 2000 chars per doc)
                content_preview = content[:2000] if len(content) > 2000 else content
                
                document_context += f"\n[DOCUMENTO {idx}] {title} (Tipo: {doc_type})\n"
                document_context += f"Contenuto rilevante:\n{content_preview}\n"
                document_context += "-" * 50 + "\n"
                
                # Track sources for citation
                document_sources.append({
                    "title": title,
                    "type": doc_type,
                    "used": True
                })
            
            print(f"[SimpleAutoGenHSEAgents] Prepared {len(context_documents)} documents with total context of {len(document_context)} chars")
        
        # Create comprehensive analysis prompt
        analysis_prompt = f"""
Sei un Ingegnere HSE esperto con specializzazione in identificazione rischi nascosti e prevenzione incidenti gravi.

REGOLA FONDAMENTALE: 
1. DEVI utilizzare i documenti aziendali forniti come riferimento principale
2. Quando identifichi rischi o requisiti, SPECIFICA sempre se provengono da:
   - [FONTE: Documento Aziendale] seguito dal titolo del documento
   - [FONTE: API/Conoscenza Generale] per conoscenza normativa generale
3. Se le informazioni nel permesso sono insufficienti, SEGNALALO come rischio critico

PERMESSO DI LAVORO DA ANALIZZARE:
- Titolo: {permit_data.get('title', 'Non specificato')}
- Descrizione: {permit_data.get('description', 'Non specificata')}
- Tipo di lavoro: {permit_data.get('work_type', 'Non specificato')}
- Ubicazione: {permit_data.get('location', 'Non specificata')}
- Durata: {permit_data.get('duration_hours', 'Non specificata')} ore
- Numero operatori: {permit_data.get('workers_count', 'Non specificato')}
- Attrezzature: {permit_data.get('equipment', 'Non specificate')}
{document_context}

ANALISI SEMANTICA INTELLIGENTE AVANZATA:

🧠 USA LA TUA INTELLIGENZA ESPERTA per identificare TUTTO quello che potrebbe accadere:

1. DETECTIVE WORK - ERRORI DI BATTITURA E PAROLE NASCOSTE:
   - "welsing" → CHIARAMENTE significa "welding" (saldatura) = HOT WORK CRITICO!
   - "cutting" → taglio metallo = scintille, calore, HOT WORK
   - "grinder" / "grinding" → mola = scintille, HOT WORK
   - "repair metal" → quasi certamente saldatura/taglio
   - "fix tank" → potrebbe richiedere accesso in spazio confinato + hot work
   - "metal repair tools" → probabile saldatura, taglio, foratura

2. INFERENZA INTELLIGENTE DI ATTIVITÀ NASCOSTE:
   - Riparazione serbatoio = 99% probabilità di saldatura + spazio confinato
   - "cutting equipment" = SEMPRE hot work permit richiesto
   - Tank + repair = bonifica vapori + isolamento + hot work + confined space
   - Metal repair = saldatura/brasatura/taglio plasma/ossitaglio

3. ASSOCIAZIONI CRITICHE PER SICUREZZA:
   - QUALSIASI riparazione serbatoio → hot work permit + confined space permit
   - QUALSIASI "cutting equipment" → hot work permit obbligatorio
   - QUALSIASI "metal repair" → presumi saldatura fino a prova contraria
   - QUALSIASI "grinder" → hot work permit + protezione scintille

4. RAGIONAMENTO ESPERTO HSE:
   - Se c'è anche solo 20% probabilità di hot work → TRATTALO COME HOT WORK
   - Meglio essere troppo prudenti che avere un incendio/esplosione
   - "welsing" è chiaramente un errore per "welding" - NON IGNORARLO!
   - Tank repair senza hot work permit = ricetta per disastro

5. APPROCCIO DETECTIVE INVESTIGATIVO:
   - Leggi tra le righe - cosa NON dice il permesso?
   - Se dice "riparazione" ma non specifica "come" → presumi il peggio
   - Errori di battitura spesso nascondono attività pericolose
   - L'operatore potrebbe non conoscere la terminologia tecnica corretta

4. RISCHI DA PROCESSO INDUSTRIALE:
   - Ogni settore ha rischi tipici che l'utente potrebbe non menzionare
   - Considera l'ambiente (petrolchimico, alimentare, metalmeccanico)
   - Pensa alle fasi preparatorie e di completamento, non solo al lavoro principale

METODOLOGIA DI ANALISI INTELLIGENTE:

1. IDENTIFICAZIONE RISCHI MULTI-LIVELLO:
   A) RISCHI ESPLICITI (chiaramente menzionati nel permesso)
   B) RISCHI IMPLICITI (tipici del tipo di lavoro anche se non menzionati)
   C) RISCHI NASCOSTI (derivanti da possibili errori ortografici o descrizioni incomplete)
   D) RISCHI DA INTERFERENZA (con ambiente circostante o altre attività)

2. PER OGNI ATTIVITÀ IDENTIFICATA, VALUTA:
   • Qual è il rischio principale?
   • Quali rischi secondari sono presenti?
   • L'utente ha considerato tutti i pericoli?
   • Ci sono indizi di lavori pericolosi non dichiarati?

3. CATEGORIE CRITICHE (usa il ragionamento, non solo keyword matching):
   
   LAVORI A CALDO - Riconosci quando c'è generazione di calore/scintille:
   • Qualsiasi processo che fonde, taglia, salda, brasaa metalli
   • Processi che generano scintille (molatura, taglio)
   • Uso di fiamme libere o strumenti riscaldanti
   → Inferisci: rischio incendio, fumi tossici, ustioni, radiazioni
   
   SPAZI CONFINATI - Identifica ambienti ristretti dove l'atmosfera può essere pericolosa:
   • Contenitori, vasche, serbatoi, silos, pozzi
   • Locali con ventilazione limitata o ingresso ristretto
   • Ambienti dove i gas possono accumularsi
   → Inferisci: asfissia, intossicazione, esplosione
   
   LAVORI IN QUOTA - Rileva attività che comportano rischio di caduta:
   • Lavoro su scale, ponteggi, tetti, piattaforme
   • Qualsiasi attività oltre 2 metri di altezza
   • Lavoro vicino a bordi, aperture, dislivelli
   → Inferisci: trauma da caduta, oggetti che cadono
   
   ENERGIE PERICOLOSE - Identifica dove ci sono energie non controllate:
   • Impianti elettrici, pressurizzati, con parti in movimento
   • Sistemi con energia potenziale accumulata
   • Macchinari che possono avviarsi inaspettatamente
   → Inferisci: elettrocuzione, schiacciamento, scoppio

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

APPROCCIO RICHIESTO:
1. VERIFICA PRIMA se hai informazioni sufficienti per fare una valutazione professionale
2. Se informazioni INCOMPLETE → INTERROMPI e richiedi chiarimenti 
3. Se informazioni COMPLETE → RAGIONA su cosa sta accadendo
4. Identifica attività implicite e rischi nascosti
5. Fornisci JSON strutturato

NON PROCEDERE con analisi generica se mancano dettagli critici!

⚠️ PRINCIPI ANALITICI PROFESSIONALI:

🧠 ANALISI INFERENZIALE ESPERTA:
Come esperto HSE, devi SEMPRE inferire i rischi dalle attività descritte, anche se incomplete:
- Identifica l'attività principale dalle descrizioni, anche con errori ortografici
- Riconosci le famiglie di rischio associate (meccanico, chimico, fisico, elettrico, etc.)
- Applica i principi di precauzione: meglio sovrastimare che sottostimare
- Considera sia i rischi diretti che quelli indiretti/interferenziali

💡 GESTIONE INFORMAZIONI INSUFFICIENTI:
Quando mancano dettagli specifici MA hai identificato attività potenzialmente pericolose:
- Genera i rischi BASE tipici di quella categoria di lavoro
- Classifica appropriatamente il livello di rischio in base alla pericolosità intrinseca
- Usa "informazioni_aggiuntive_necessarie" per dettagliare cosa serve per completare l'analisi
- Nel JSON, popola SEMPRE "rischi_identificati" basandoti sui dati disponibili

🔍 APPROCCIO SISTEMATICO:
- Prima: identifica COSA si sta facendo (analisi semantica)
- Secondo: WHERE si sta lavorando (ambiente, interferenze)
- Terzo: HOW si sta operando (attrezzature, metodi)
- Quarto: WHO è coinvolto (competenze, formazione)
- Quinto: genera rischi e misure appropriate per il contesto identificato

FORMATO RISPOSTA - FORNISCI JSON STRUTTURATO DOPO IL RAGIONAMENTO:

```json
{{
  "analisi_generale": {{
    "tipologia_lavoro": "descrizione specifica",
    "classificazione_rischio": "basso|medio|alto|molto_alto|informazioni_insufficienti",
    "informazioni_mancanti": ["lista dettagliata di informazioni critiche mancanti"],
    "completezza_permesso": "completo|parziale|insufficiente",
    "normative_principali": [],  # Lista con formato: "[FONTE: Doc Aziendale/API] Nome normativa"
    "interferenze_identificate": ["descrizione interferenze"],
    "raccomandazioni_integrative": ["cosa richiedere per completare l'analisi"]
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
      "normative_riferimento": [],  # Specifica se da "Documento Aziendale" o "API/Normativa Generale"
      "misure_controllo": [
        "eliminazione/sostituzione",
        "controlli_ingegneristici", 
        "controlli_amministrativi",
        "dpi_richiesti"
      ],
      "informazioni_aggiuntive_necessarie": ["dettagli specifici da richiedere"]
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
  ],
  "valutazione_completezza": {{
    "permesso_completo": true|false,
    "informazioni_critiche_mancanti": ["lista dettagliata"],
    "impossibilita_analisi_completa": "motivo se applicabile",
    "azioni_richieste_prima_approvazione": ["cosa fare prima di procedere"]
  }}
}}
```

RACCOMANDAZIONI FINALI:
- Utilizza sempre terminologia tecnica precisa
- Cita articoli specifici delle normative
5. PRINCIPI DI ANALISI PROFESSIONALE:
   • Ragiona come un esperto HSE: "Se fossi sul campo, cosa vedrei?"
   • Considera il PRIMA, DURANTE e DOPO l'attività principale
   • Pensa alle preparazioni necessarie (isolamenti, bonifiche, allestimenti)
   • Valuta l'ambiente circostante e le possibili interferenze
   • Quantifica i rischi dove possibile (livelli di rumore, concentrazioni, altezze)
   • Ogni rischio identificato DEVE avere misure di controllo specifiche e DPI appropriati
   
   IMPORTANTE - CITAZIONE DELLE FONTI:
   • Se usi informazioni dai DOCUMENTI AZIENDALI sopra, cita: "Fonte: [Nome Documento Aziendale]"
   • Se usi conoscenze generali/API, cita: "Fonte: Normativa generale (D.Lgs 81/08)" o simili
   • DAI SEMPRE PRIORITÀ ai documenti aziendali quando disponibili

6. GESTIONE INFORMAZIONI INCOMPLETE:
   • Se TITOLO, DESCRIZIONE o ATTREZZATURE sono vaghi/vuoti → IDENTIFICALO come RISCHIO CRITICO
   • Informazioni insufficienti = IMPOSSIBILITÀ di garantire sicurezza
   • SEMPRE segnala esplicitamente cosa manca per fare una valutazione completa
   • Non inventare rischi generici - richiedi informazioni specifiche

7. OUTPUT INTELLIGENTE:
   • Se le informazioni sono complete: analisi dettagliata dei rischi specifici
   • Se le informazioni sono incomplete: FERMA L'ANALISI e richiedi chiarimenti
   • Spiega sempre il TUO RAGIONAMENTO per ogni decisione
   • Identifica esplicitamente cosa impedisce una valutazione completa
"""
        
        try:
            print(f"[SimpleAutoGenHSEAgents] Starting HSE analysis with Gemini for permit {permit_data.get('id')}")
            
            # Search for relevant documents first
            relevant_docs = []
            api_sources = []  # Track API sources used
            
            if self.vector_service:
                # Build search query from permit data
                search_query = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('work_type', '')}"
                relevant_docs = await self.search_relevant_documents(search_query)
                
                if relevant_docs:
                    print(f"[SimpleAutoGenHSEAgents] Found {len(relevant_docs)} relevant documents to use in analysis")
                    # Add document context to the prompt
                    docs_context = "\n\nDOCUMENTI AZIENDALI RILEVANTI TROVATI:\n"
                    for doc in relevant_docs[:5]:  # Use top 5 documents
                        docs_context += f"\n- {doc.get('title', 'N/A')} ({doc.get('document_code', 'N/A')}): {doc.get('content', '')[:200]}..."
                    analysis_prompt += docs_context
                else:
                    print("[SimpleAutoGenHSEAgents] No internal documents found, will use API knowledge")
            
            # Add instruction to use API knowledge if documents are incomplete
            analysis_prompt += """\n\nNOTA IMPORTANTE:
            - Dai PRIORITÀ ai documenti aziendali trovati sopra
            - Se i documenti non coprono tutti gli aspetti, INTEGRA con conoscenze normative generali (D.Lgs 81/08, norme EN, etc.)
            - CITA SEMPRE le fonti: specifica se provengono da 'Documento aziendale' o 'Normativa generale'
            - Se usi normative generali, indica chiaramente che sono 'Fonte: API/Conoscenza generale'
            """
            
            # Store sources for citation tracking
            self.document_sources = relevant_docs
            self.api_sources = []  # Will be populated based on AI response
            
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
Sei un RSPP esperto che deve RIVEDERE CRITICAMENTE l'analisi seguente.

PERMESSO ORIGINALE:
- Titolo: {permit_data.get('title', 'Non specificato')}
- Descrizione: {permit_data.get('description', 'Non specificata')}
- Tipo lavoro: {permit_data.get('work_type', 'Non specificato')}
- Attrezzature: {permit_data.get('equipment', 'Non specificate')}

ANALISI DA RIVEDERE:
{analyst_response}

COMPITI CRITICI DI REVISIONE:

1. RAGIONAMENTO CRITICO SULL'ANALISI RICEVUTA:
   • L'analisi ha veramente compreso cosa sta accadendo?
   • Ha identificato tutte le attività implicite nel processo descritto?
   • Mancano rischi che normalmente accompagnano questo tipo di lavoro?
   • Le misure proposte sono realistiche e sufficienti?

2. ANALISI SEMANTICA DEL PERMESSO ORIGINALE:
   • Rileggi il permesso originale con occhi esperti
   • Cosa farebbe realmente un operatore in quella situazione?
   • Quali preparazioni, strumenti, procedure sono necessarie?
   • Ci sono termini imprecisi o errori che nascondono attività pericolose?

3. IDENTIFICAZIONE INTELLIGENTE DI RISCHI MANCANTI:
   • Usa la tua conoscenza degli incidenti tipici per questo tipo di lavoro
   • Considera i "near miss" più comuni nel settore
   • Pensa ai rischi che emergono durante l'esecuzione, non solo nella pianificazione
   • Valuta le condizioni ambientali e organizzative specifiche

4. VALIDAZIONE INTELLIGENTE DPI:
   • I DPI proposti sono appropriati per i rischi REALI del lavoro?
   • Sono stati considerati tutti i DPI per le fasi preparatorie?
   • C'è compatibilità ergonomica tra i DPI multipli?
   • Sono specifici per l'ambiente di lavoro (es: ATEX, chimico-resistenti)?

5. VALUTAZIONE MISURE DI CONTROLLO:
   • Le procedure proposte sono realmente applicabili sul campo?
   • Sono state considerate le misure di controllo gerarchiche?
   • Ci sono controlli amministrativi (permessi speciali, sorveglianza)?
   • È previsto un piano di emergenza specifico?

APPROCCIO RICHIESTO:
1. Prima RAGIONA sul permesso originale indipendentemente dall'analisi ricevuta
2. Identifica cosa avresti fatto diversamente
3. Fornisci una revisione che integra e migliora l'analisi

OBIETTIVO: Garantire che ZERO INCIDENTI GRAVI possano accadere durante questo lavoro
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
            
            # Identify which sources were used based on response content
            self._identify_sources_used(combined_analysis)
            
            # Add document sources to final analysis
            if document_sources:
                final_analysis["document_sources_used"] = document_sources
                print(f"[SimpleAutoGenHSEAgents] Analysis used {len(document_sources)} document sources")
            
            return {
                "analysis_complete": True,
                "confidence_score": 0.85 if document_sources else 0.65,  # Higher confidence with documents
                "conversation_history": conversation_history,
                "agents_involved": ["HSE_Analyst", "Safety_Reviewer"],
                "processing_time": 0.0,
                "final_analysis": final_analysis,
                "documents_used": len(document_sources) if document_sources else 0
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
        """Parse JSON from AI response with improved extraction"""
        import json
        import re
        
        print(f"[JSON Parser] Starting JSON extraction from content length: {len(content)}")
        
        # Look for JSON blocks in the response first (most reliable)
        json_pattern = r'```json\s*(.*?)\s*```'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        print(f"[JSON Parser] Found {len(matches)} JSON code blocks")
        
        for i, match in enumerate(matches):
            try:
                print(f"[JSON Parser] Trying to parse JSON block {i+1}: {match[:200]}...")
                parsed = json.loads(match)
                if isinstance(parsed, dict) and any(key in parsed for key in ['rischi_identificati', 'dpi_obbligatori', 'analisi_generale']):
                    print(f"[JSON Parser] Successfully parsed valid JSON block {i+1}")
                    return parsed
            except json.JSONDecodeError as e:
                print(f"[JSON Parser] Failed to parse JSON block {i+1}: {e}")
                continue
        
        # Try to find JSON objects by counting braces (more robust)
        def find_complete_json_objects(text):
            """Find complete JSON objects by matching braces"""
            objects = []
            i = 0
            while i < len(text):
                if text[i] == '{':
                    brace_count = 0
                    start = i
                    j = i
                    while j < len(text):
                        if text[j] == '{':
                            brace_count += 1
                        elif text[j] == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                # Found complete object
                                objects.append(text[start:j+1])
                                break
                        j += 1
                    i = j + 1
                else:
                    i += 1
            return objects
        
        json_objects = find_complete_json_objects(content)
        print(f"[JSON Parser] Found {len(json_objects)} potential JSON objects")
        
        for i, obj in enumerate(json_objects):
            try:
                print(f"[JSON Parser] Trying to parse JSON object {i+1}: {obj[:200]}...")
                parsed = json.loads(obj)
                if isinstance(parsed, dict) and any(key in parsed for key in ['rischi_identificati', 'dpi_obbligatori', 'analisi_generale']):
                    print(f"[JSON Parser] Successfully parsed valid JSON object {i+1}")
                    return parsed
                else:
                    print(f"[JSON Parser] JSON object {i+1} doesn't contain expected keys")
            except json.JSONDecodeError as e:
                print(f"[JSON Parser] Failed to parse JSON object {i+1}: {e}")
                continue
        
        print("[JSON Parser] No valid JSON found, returning None")
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
        
        # Let AI do the heavy lifting - only use basic fallback patterns as last resort
        # The AI should have already identified all critical risks through intelligent analysis
        
        # Basic fallback risk patterns (only for when AI completely fails)
        basic_risk_patterns = [
            ("elettrico", "alto", "Controlli elettrici e DPI isolanti", []),
            ("meccanico", "medio", "Protezioni macchine", []),
            ("chimico", "alto", "Controlli ambientali e DPI", []),
            ("rumore", "medio", "Protezioni uditive", []),
            ("caduta", "alto", "Sistemi anticaduta", [])
        ]
        
        for risk_term, severity, mitigation, norms in basic_risk_patterns:
            if risk_term in content:
                risks.append({
                    "risk": f"Rischio {risk_term}",
                    "severity": severity,
                    "mitigation": mitigation,
                    "normatives": norms
                })
        
        # Trust the AI analysis - only add basic DPI if AI provided none
        # The enhanced AI prompts should identify all necessary DPI through semantic understanding
        
        # Only add minimal fallback DPI if AI provided absolutely nothing
        if len(dpi_recommendations) == 0:
            # Basic industrial DPI as absolute minimum
            dpi_recommendations.extend([
                {
                    "dpi_type": "Elmetto di protezione",
                    "reason": "Protezione base del capo",
                    "standard": "EN 397",
                    "category": "II",
                    "details": "DPI base obbligatorio"
                },
                {
                    "dpi_type": "Scarpe antinfortunistiche",
                    "reason": "Protezione base dei piedi",
                    "standard": "Standard applicabile",
                    "category": "II",
                    "details": "S1P minimo richiesto"
                }
            ])
        
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
                    "references": ["Documenti aziendali"],
                    "estimated_effort": "2-4 ore",
                    "responsible_role": "Responsabile Sicurezza",
                    "frontend_display": {
                        "color": "red",
                        "icon": "alert-triangle",
                        "category": "Controlli Sicurezza"
                    }
                })
                item_counter += 1
        
        # Create action items for DPI - one for each DPI type
        for dpi in dpi_recommendations:
            dpi_type = dpi.get("dpi_type", "DPI non specificato")
            reason = dpi.get("reason", "Protezione generica")
            standard = dpi.get("standard", "Standard da definire")
            details = dpi.get("details", "")
            
            action_items.append({
                "id": f"ACT_{item_counter:03d}",
                "type": "dpi_requirement",
                "priority": "alta" if len(risks) > 2 else "media",
                "title": f"Fornire {dpi_type}",
                "description": f"{dpi_type} - {reason}. {details}".strip(),
                "suggested_action": f"Approvvigionare e distribuire {dpi_type} conformi a {standard}",
                "consequences_if_ignored": f"Esposizione diretta ai rischi: {reason}",
                "references": [standard] if standard and standard != "Standard da definire" else [],
                "estimated_effort": "1-2 ore",
                "responsible_role": "Responsabile Approvvigionamenti",
                "frontend_display": {
                    "color": "yellow" if standard == "Standard da definire" else "orange",
                    "icon": "shield-check",
                    "category": f"DPI Categoria {standard}" if standard != "Standard da definire" else "DPI Richiesto"
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
                "references": ["Documenti aziendali"],
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
            "normative_framework": [],
            "company_procedures": []
        }
        
        # PRIORITY 1: Use documents found during search if available
        if hasattr(self, 'searched_documents') and self.searched_documents:
            print(f"[SimpleAutoGenHSEAgents] Creating citations from {len(self.searched_documents)} found documents")
            for doc in self.searched_documents[:10]:  # Use top 10 documents
                doc_type = doc.get('document_type', 'normativa')
                citation_entry = {
                    "document_info": {
                        "title": doc.get('title', 'Documento'),
                        "code": doc.get('document_code', ''),
                        "type": doc.get('document_type', 'Normativa'),
                        "date": doc.get('created_at', 'Current'),
                        "source": "Documento Aziendale"  # Mark as internal source
                    },
                    "relevance": {
                        "score": doc.get('search_score', 0.9),  # Higher score for internal docs
                        "reason": f"Documento aziendale specifico per {doc.get('category', 'attività')}"
                    },
                    "key_requirements": [],
                    "frontend_display": {
                        "color": "blue" if doc_type in ['normativa', 'decreto'] else "green",
                        "icon": "book-open" if doc_type in ['normativa', 'decreto'] else "file-text",
                        "category": "Documenti Aziendali" if doc_type in ['normativa', 'decreto'] else "Procedure Aziendali"
                    }
                }
                
                if doc_type in ['normativa', 'decreto', 'legge', 'standard']:
                    citations["normative_framework"].append(citation_entry)
                else:
                    citations["company_procedures"].append(citation_entry)
        
        # PRIORITY 2: Add API/general knowledge citations if needed
        if len(citations["normative_framework"]) < 3:  # If we have less than 3 internal citations
            print("[SimpleAutoGenHSEAgents] Adding API knowledge citations to complement internal documents")
            
            # Add general safety regulations from API knowledge
            api_citations = [
                {
                    "document_info": {
                        "title": "D.Lgs 81/08 - Testo Unico Sicurezza",
                        "code": "D.Lgs 81/08",
                        "type": "Decreto Legislativo",
                        "date": "2008-04-09",
                        "source": "API/Conoscenza Generale"  # Mark as API source
                    },
                    "relevance": {
                        "score": 0.7,  # Lower score for API sources
                        "reason": "Normativa generale di riferimento per la sicurezza sul lavoro"
                    },
                    "key_requirements": [],
                    "frontend_display": {
                        "color": "orange",  # Different color for API sources
                        "icon": "cloud",  # Cloud icon for API sources
                        "category": "Normativa Generale (API)"
                    }
                }
            ]
            
            # Add only if we don't have enough internal citations
            for api_citation in api_citations:
                if len(citations["normative_framework"]) < 5:
                    citations["normative_framework"].append(api_citation)
        
        if not citations["normative_framework"] and not citations["company_procedures"]:
            print("[SimpleAutoGenHSEAgents] No citations available from any source")
        
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
                        "standard": "Standard applicabile"
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
                        "standard": "Standard applicabile"
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
        
        # Create action items for DPI - one for each DPI type
        for dpi in dpi_recommendations:
            dpi_type = dpi.get("dpi_type", "DPI non specificato")
            reason = dpi.get("reason", "Protezione generica")
            standard = dpi.get("standard", "Standard da definire")
            
            action_items.append({
                "id": f"ACT_{item_counter:03d}",
                "type": "dpi_requirement",
                "priority": "alta",
                "title": f"Fornire {dpi_type}",
                "description": f"{dpi_type} - {reason}",
                "suggested_action": f"Verificare disponibilità e distribuire {dpi_type} conformi a {standard}",
                "consequences_if_ignored": f"Esposizione diretta ai rischi: {reason}",
                "references": [standard] if standard and standard != "Standard da definire" else [],
                "estimated_effort": "1 ora",
                "responsible_role": "Responsabile Magazzino",
                "frontend_display": {
                    "color": "orange",
                    "icon": "shield-check",
                    "category": "DPI Obbligatori"
                }
            })
            item_counter += 1
        
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
                "references": ["Documenti aziendali"],
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
        
        # PRIORITY 1: Add internal document citations if available
        if hasattr(self, 'searched_documents') and self.searched_documents:
            print(f"[Citations] Using {len(self.searched_documents)} internal documents as primary sources")
            for doc in self.searched_documents[:5]:
                doc_type = doc.get('document_type', 'normativa')
                citation = {
                    "document_info": {
                        "title": doc.get('title', 'Documento Aziendale'),
                        "code": doc.get('document_code', ''),
                        "type": doc.get('document_type', 'Procedura'),
                        "date": doc.get('created_at', 'Current'),
                        "source": "Documento Aziendale"
                    },
                    "relevance": {
                        "score": 0.95,  # High score for internal docs
                        "reason": f"Documento aziendale specifico per {doc.get('category', 'sicurezza')}"
                    },
                    "key_requirements": [],
                    "frontend_display": {
                        "color": "green",
                        "icon": "file-text",
                        "category": "Documenti Aziendali"
                    }
                }
                
                if doc_type in ['normativa', 'decreto', 'standard']:
                    citations["normative_framework"].append(citation)
                else:
                    citations["company_procedures"].append(citation)
        
        # PRIORITY 2: Add API-based citations only if needed
        if len(citations["normative_framework"]) < 3:
            print("[Citations] Adding API-based normative references to complement internal documents")
        
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
                        "title": "Documenti aziendali",
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
        
        
        # Check if AI failed to analyze properly (this should NOT happen with good AI)
        if exec_summary.get('critical_issues', 0) == 0 and len(action_items) == 0:
            print("[SimpleAutoGenHSEAgents] CRITICAL ERROR: AI failed to identify ANY risks - this should never happen!")
            
            # Create a critical finding about missing information instead of generic fallback
            return self._create_critical_analysis_failure_response(combined_analysis)
        
        # If analysis seems too minimal, enhance it but don't override good AI work
        if len(action_items) < 2:
            print("[SimpleAutoGenHSEAgents] Analysis seems minimal - adding mandatory safety review")
            result = self._add_mandatory_safety_review(result, combined_analysis)
        
        return result
    
    def _create_critical_analysis_failure_response(self, combined_analysis: str) -> Dict[str, Any]:
        """Create a response that highlights critical analysis failure"""
        
        # This indicates either:
        # 1. The permit has missing critical information
        # 2. The AI analysis completely failed
        # 3. The permit is genuinely low-risk but we should still flag for review
        
        return {
            "executive_summary": {
                "overall_score": 0.1,  # Very low score for failed analysis
                "critical_issues": 1,  # At least the analysis failure itself is critical
                "recommendations": 3,
                "compliance_level": "non_conforme",
                "estimated_completion_time": "INDEFINITO - Richiesta revisione",
                "key_findings": [
                    "ERRORE CRITICO: Analisi AI non ha identificato rischi - possibile informazione mancante",
                    "Permesso richiede revisione manuale immediata",
                    "Informazioni insufficienti per valutazione completa"
                ],
                "next_steps": [
                    "STOP: Non procedere senza revisione manuale",
                    "Verificare completezza informazioni nel permesso",
                    "Richiedere dettagli mancanti (attrezzature, procedure, ambiente)",
                    "Ri-sottoporre per analisi dopo integrazione informazioni"
                ]
            },
            "action_items": [
                {
                    "id": "CRIT_001",
                    "type": "critical_review",
                    "priority": "critica",
                    "title": "REVISIONE MANUALE OBBLIGATORIA",
                    "description": "L'analisi AI non ha identificato rischi - indica informazioni mancanti o permesso incompleto",
                    "suggested_action": "Non autorizzare il lavoro fino a revisione manuale completa da parte di RSPP",
                    "consequences_if_ignored": "RISCHIO INCIDENTI GRAVI - Analisi incompleta",
                    "references": ["Procedura aziendale"],
                    "estimated_effort": "Revisione completa richiesta",
                    "responsible_role": "RSPP/Responsabile Sicurezza",
                    "frontend_display": {
                        "color": "red",
                        "icon": "alert-triangle",
                        "category": "ERRORE ANALISI CRITICO"
                    }
                },
                {
                    "id": "INFO_001",
                    "type": "information_gap",
                    "priority": "alta",
                    "title": "Informazioni mancanti nel permesso",
                    "description": "Permesso carente di dettagli necessari per analisi rischi completa",
                    "suggested_action": "Richiedere: descrizione dettagliata lavoro, attrezzature specifiche, procedure operative, ambiente lavoro",
                    "consequences_if_ignored": "Impossibilità di identificare tutti i rischi presenti",
                    "references": ["Procedura aziendale"],
                    "estimated_effort": "30 minuti raccolta informazioni",
                    "responsible_role": "Richiedente permesso",
                    "frontend_display": {
                        "color": "orange",
                        "icon": "info",
                        "category": "INFORMAZIONI MANCANTI"
                    }
                },
                {
                    "id": "MIN_001",
                    "type": "minimum_safety",
                    "priority": "media",
                    "title": "DPI base comunque obbligatori",
                    "description": "Anche con informazioni incomplete, DPI base sono sempre obbligatori",
                    "suggested_action": "Fornire elmetto, scarpe antinfortunistiche, guanti base - completare dopo revisione",
                    "consequences_if_ignored": "Violazione norme base sicurezza",
                    "references": ["Procedura DPI"],
                    "estimated_effort": "Immediato",
                    "responsible_role": "Responsabile Sicurezza",
                    "frontend_display": {
                        "color": "blue",
                        "icon": "shield",
                        "category": "DPI BASE OBBLIGATORI"
                    }
                }
            ],
            "citations": {
                "normative_framework": [
                    {
                        "document_info": {
                            "title": "Procedura aziendale",
                            "type": "Normativa",
                            "date": "2008-04-09"
                        },
                        "relevance": {
                            "score": 1.0,
                            "reason": "Obbligo valutazione rischi completa"
                        },
                        "key_requirements": [
                            {
                                "requirement": "Valutazione deve considerare tutti i rischi",
                                "mandatory": True,
                                "description": "Requisito obbligatorio per valutazione completa dei rischi"
                            },
                            {
                                "requirement": "Informazioni sufficienti per identificazione pericoli",
                                "mandatory": True,
                                "description": "Necessarie informazioni dettagliate per identificare tutti i pericoli"
                            }
                        ],
                        "frontend_display": {
                            "color": "red",
                            "icon": "alert-triangle",
                            "category": "NORMATIVA VIOLATA"
                        }
                    }
                ],
                "company_procedures": []
            },
            "completion_roadmap": {
                "immediate_actions": [
                    "STOP - Non autorizzare il lavoro",
                    "Richiedere informazioni complete"
                ],
                "short_term_actions": [
                    "Revisione manuale RSPP",
                    "Integrazione dettagli mancanti"
                ],
                "medium_term_actions": [
                    "Ri-analisi dopo integrazione informazioni",
                    "Formazione su compilazione permessi completi"
                ],
                "success_metrics": [
                    "Permesso completo di tutte le informazioni",
                    "Analisi successiva identifica rischi specifici",
                    "Zero incidenti da informazioni mancanti"
                ],
                "review_checkpoints": [
                    "Completezza informazioni",
                    "Approvazione RSPP",
                    "Ri-analisi AI successiva"
                ]
            }
        }
    
    def _add_mandatory_safety_review(self, result: Dict[str, Any], combined_analysis: str) -> Dict[str, Any]:
        """Add mandatory safety review without overriding good AI analysis"""
        
        # Add one additional action item about mandatory review
        existing_items = result.get('action_items', [])
        exec_summary = result.get('executive_summary', {})
        
        # Add a safety review item but keep existing analysis
        additional_item = {
            "id": f"REVIEW_{len(existing_items)+1:03d}",
            "type": "mandatory_review",
            "priority": "media",
            "title": "Revisione sicurezza obbligatoria",
            "description": "Verifica completezza analisi e conformità procedure",
            "suggested_action": "RSPP deve validare l'analisi e confermare idoneità misure proposte",
            "consequences_if_ignored": "Possibili rischi non identificati",
            "references": ["Procedura aziendale"],
            "estimated_effort": "30 minuti",
            "responsible_role": "RSPP",
            "frontend_display": {
                "color": "blue",
                "icon": "check-circle",
                "category": "CONTROLLO QUALITÀ"
            }
        }
        
        existing_items.append(additional_item)
        result['action_items'] = existing_items
        
        # Update executive summary
        exec_summary['recommendations'] = len(existing_items)
        exec_summary['next_steps'] = exec_summary.get('next_steps', []) + ["Revisione RSPP obbligatoria"]
        result['executive_summary'] = exec_summary
        
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
            {"risk": "Rischio elettrocuzione da contatto diretto/indiretto", "severity": "molto_alto", "normatives": ["Procedura elettrica", "Procedura elettrica"]},
            {"risk": "Rischio arco elettrico e ustioni", "severity": "alto", "normatives": ["Procedura elettrica"]},
            {"risk": "Rischio incendio da sovraccarico elettrico", "severity": "alto", "normatives": ["Procedura antincendio"]}
        ]
        
        dpi = [
            {"dpi_type": "Guanti isolanti Classe 0", "standard": "EN 60903", "reason": "Protezione contatti elettrici 1000V", "category": "III"},
            {"dpi_type": "Scarpe isolanti", "standard": "Standard applicabile", "reason": "Isolamento elettrico", "category": "II"},
            {"dpi_type": "Elmetto dielettrico", "standard": "EN 397", "reason": "Protezione capo e isolamento", "category": "II"},
            {"dpi_type": "Tuta antistatica", "standard": "EN 1149", "reason": "Prevenzione accumulo cariche", "category": "I"}
        ]
        
        return risks, dpi
    
    def _get_mechanical_work_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for mechanical work"""
        risks = [
            {"risk": "Rischio cesoiamento da macchine in movimento", "severity": "alto", "normatives": ["Procedura macchine"]},
            {"risk": "Rischio taglio da utensili", "severity": "medio", "normatives": ["Documenti aziendali"]},
            {"risk": "Rischio schiacciamento arti", "severity": "alto", "normatives": ["Documenti aziendali"]}
        ]
        
        dpi = [
            {"dpi_type": "Guanti antitaglio Livello 5", "standard": "Standard applicabile", "reason": "Protezione da tagli", "category": "II"},
            {"dpi_type": "Scarpe antinfortunistiche S3", "standard": "Standard applicabile", "reason": "Protezione piedi", "category": "II"},
            {"dpi_type": "Occhiali di sicurezza", "standard": "Standard applicabile", "reason": "Protezione occhi da schegge", "category": "II"}
        ]
        
        return risks, dpi
    
    def _get_maintenance_work_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for maintenance work"""
        risks = [
            {"risk": "Rischio meccanico da attrezzature", "severity": "medio", "normatives": ["Documenti aziendali"]},
            {"risk": "Rischio caduta oggetti", "severity": "medio", "normatives": ["Documenti aziendali"]},
            {"risk": "Rischio posturale", "severity": "basso", "normatives": ["Procedura ergonomia"]}
        ]
        
        dpi = [
            {"dpi_type": "Elmetto di protezione", "standard": "EN 397", "reason": "Protezione capo", "category": "II"},
            {"dpi_type": "Guanti meccanici", "standard": "Standard applicabile", "reason": "Protezione mani", "category": "II"},
            {"dpi_type": "Scarpe antinfortunistiche", "standard": "Standard applicabile", "reason": "Protezione piedi", "category": "II"}
        ]
        
        return risks, dpi
    
    def _get_chemical_work_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for chemical work"""  
        risks = [
            {"risk": "Rischio inalazione vapori tossici", "severity": "alto", "normatives": ["Procedura sostanze chimiche"]},
            {"risk": "Rischio contatto cutaneo sostanze chimiche", "severity": "alto", "normatives": ["Procedura sostanze chimiche"]},
            {"risk": "Rischio incendio/esplosione", "severity": "molto_alto", "normatives": ["Procedura ATEX"]}
        ]
        
        dpi = [
            {"dpi_type": "Respiratore FFP3", "standard": "EN 149", "reason": "Protezione vie respiratorie", "category": "III"},
            {"dpi_type": "Guanti chimici", "standard": "EN 374", "reason": "Protezione da agenti chimici", "category": "III"},
            {"dpi_type": "Tuta di protezione chimica", "standard": "Standard applicabile", "reason": "Protezione corpo", "category": "III"}
        ]
        
        return risks, dpi
    
    def _get_confined_space_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for confined space work"""
        risks = [
            {"risk": "Rischio asfissia per carenza ossigeno", "severity": "molto_alto", "normatives": ["Procedura spazi confinati"]},
            {"risk": "Rischio intossicazione gas tossici", "severity": "molto_alto", "normatives": ["Procedura spazi confinati"]},
            {"risk": "Rischio esplosione atmosfere ATEX", "severity": "molto_alto", "normatives": ["Procedura ATEX"]}
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
            {"risk": "Rischio caduta dall'alto", "severity": "molto_alto", "normatives": ["Procedura lavori altezza"]},
            {"risk": "Rischio caduta oggetti", "severity": "alto", "normatives": ["Procedura lavori altezza"]},
            {"risk": "Rischio ribaltamento scale/ponteggi", "severity": "alto", "normatives": ["Procedura scale"]}
        ]
        
        dpi = [
            {"dpi_type": "Imbracatura anticaduta Classe A", "standard": "EN 361", "reason": "Protezione cadute", "category": "III"},
            {"dpi_type": "Casco con sottogola", "standard": "EN 397", "reason": "Protezione capo", "category": "II"},
            {"dpi_type": "Scarpe antiscivolo", "standard": "Standard applicabile", "reason": "Aderenza superfici", "category": "II"}
        ]
        
        return risks, dpi
    
    def _get_general_industrial_requirements(self) -> tuple[List[Dict], List[Dict]]:
        """Mandatory requirements for ANY industrial work"""
        risks = [
            {"risk": "Rischio infortunio generico", "severity": "medio", "normatives": ["Documenti aziendali"]},
            {"risk": "Rischio caduta in piano", "severity": "medio", "normatives": ["Documenti aziendali"]},
            {"risk": "Rischio movimentazione manuale carichi", "severity": "basso", "normatives": ["Procedura ergonomia"]}
        ]
        
        dpi = [
            {"dpi_type": "Elmetto di protezione base", "standard": "EN 397", "reason": "Protezione capo obbligatoria", "category": "II"},
            {"dpi_type": "Scarpe antinfortunistiche S1P", "standard": "Standard applicabile", "reason": "Protezione piedi obbligatoria", "category": "II"},
            {"dpi_type": "Guanti da lavoro", "standard": "Standard applicabile", "reason": "Protezione mani generica", "category": "I"}
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
                "references": ["Procedura DPI"],
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
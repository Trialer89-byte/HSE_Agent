from typing import Dict, Any, List
import autogen
from .autogen_config import get_autogen_llm_config, GeminiLLMConfig


class AutoGenHSEAgents:
    """
    AutoGen-based HSE agents for comprehensive work permit analysis
    """
    
    def __init__(self, user_context: Dict[str, Any]):
        self.user_context = user_context
        self.llm_config = GeminiLLMConfig()
        self.agents = self._create_agents()
        self.group_chat = self._create_group_chat()
        self.manager = self._create_group_chat_manager()
    
    def _create_agents(self) -> Dict[str, autogen.AssistantAgent]:
        """Create all HSE specialist agents"""
        
        # 1. Content Analysis Agent
        content_analyst = autogen.AssistantAgent(
            name="HSE_Content_Analyst",
            system_message="""
Sei un esperto HSE specializzato nell'analisi qualitativa dei contenuti dei permessi di lavoro.

RUOLO: Analizzare la completezza e qualità del contenuto del permesso di lavoro.

RESPONSABILITÀ:
1. Valutare completezza delle informazioni fornite
2. Identificare informazioni mancanti o insufficienti
3. Suggerire miglioramenti per chiarezza e precisione
4. Verificare coerenza tra titolo, descrizione e tipo di lavoro
5. Valutare adeguatezza della durata stimata

CRITERI DI VALUTAZIONE:
- Chiarezza della descrizione del lavoro
- Specificità delle attività da svolgere
- Identificazione corretta dell'ubicazione
- Adeguatezza della durata stimata
- Presenza di informazioni sui materiali/attrezzature

FORMATO RISPOSTA: Fornisci sempre una valutazione strutturata con:
- Qualità contenuto (0.0-1.0)
- Problemi identificati (lista)
- Raccomandazioni di miglioramento (lista)
- Informazioni mancanti (lista)
""",
            llm_config=get_autogen_llm_config(),
            max_consecutive_auto_reply=3,
            human_input_mode="NEVER"
        )
        
        # 2. Risk Analysis Agent
        risk_analyst = autogen.AssistantAgent(
            name="HSE_Risk_Analyst",
            system_message="""
Sei un esperto HSE specializzato nell'identificazione e valutazione dei rischi per la sicurezza sul lavoro.

RUOLO: Identificare e valutare tutti i rischi presenti nel permesso di lavoro.

RESPONSABILITÀ:
1. Identificare rischi evidenti e nascosti
2. Valutare probabilità e gravità dei rischi
3. Categorizzare rischi per tipologia
4. Suggerire controlli e misure preventive
5. Identificare interazioni tra rischi multipli

CATEGORIZZAZIONE RISCHI:
- MECH: Meccanici (schiacciamento, taglio, caduta oggetti)
- CHEM: Chimici (esposizione sostanze, vapori, fumi)
- BIOL: Biologici (batteri, virus, muffe)
- PHYS: Fisici (rumore, vibrazioni, radiazioni)
- ELEC: Elettrici (folgorazione, arco elettrico)
- FIRE: Incendio/esplosione
- FALL: Caduta dall'alto
- CONF: Spazi confinati
- ERGO: Ergonomici (posture, movimentazione)

VALUTAZIONE RISCHIO:
- Probabilità: Molto bassa, Bassa, Media, Alta, Molto alta
- Gravità: Trascurabile, Lieve, Moderata, Grave, Catastrofica
- Livello rischio: Accettabile, Tollerabile, Rilevante, Elevato, Inaccettabile

FORMATO RISPOSTA: Fornisci sempre:
- Rischi identificati con categoria e valutazione
- Misure preventive specifiche
- Livello di rischio complessivo
- Priorità di intervento
""",
                description="Identifica e valuta i rischi di sicurezza nei permessi di lavoro"
            )
        )
        
        # 3. Compliance Checker Agent
        compliance_checker = autogen.AssistantAgent(
            **create_hse_agent_config(
                name="HSE_Compliance_Checker",
                system_message="""
Sei un esperto HSE specializzato nella verifica della conformità normativa italiana.

RUOLO: Verificare la conformità del permesso di lavoro alle normative italiane di sicurezza.

NORMATIVE PRINCIPALI:
- D.Lgs. 81/2008 (Testo Unico Sicurezza)
- D.Lgs. 106/2009 (Modifiche al TU)
- Accordi Stato-Regioni su formazione
- Norme tecniche UNI, CEI, ISO
- Direttive europee recepite

RESPONSABILITÀ:
1. Verificare conformità alle disposizioni legislative
2. Identificare obblighi normativi specifici
3. Verificare requisiti di formazione e abilitazione
4. Controllare procedure di autorizzazione
5. Identificare sanzioni per non conformità

AREE DI VERIFICA:
- Valutazione dei rischi (art. 17, 28 D.Lgs 81/08)
- Dispositivi di protezione (Titolo III)
- Formazione lavoratori (art. 37)
- Sorveglianza sanitaria (Titolo I, Capo III)
- Procedure di emergenza
- Segnaletica di sicurezza

FORMATO RISPOSTA: Fornisci sempre:
- Livello conformità (Conforme/Parzialmente conforme/Non conforme)
- Articoli normativi applicabili
- Non conformità identificate
- Azioni correttive necessarie
""",
                description="Verifica la conformità normativa dei permessi di lavoro"
            )
        )
        
        # 4. DPI Specialist Agent
        dpi_specialist = autogen.AssistantAgent(
            **create_hse_agent_config(
                name="HSE_DPI_Specialist",
                system_message="""
Sei un esperto HSE specializzato nei Dispositivi di Protezione Individuale (DPI).

RUOLO: Specificare i DPI necessari basandosi sui rischi identificati.

RESPONSABILITÀ:
1. Analizzare i rischi per determinare DPI necessari
2. Specificare caratteristiche tecniche dei DPI
3. Verificare conformità alle norme CE
4. Suggerire procedure di utilizzo e manutenzione
5. Identificare incompatibilità tra DPI

CATEGORIE DPI (D.Lgs 475/92):
- Categoria I: Rischi minimi (guanti da giardinaggio, occhiali sole)
- Categoria II: Rischi intermedi (caschi, scarpe antinfortunistiche)
- Categoria III: Rischi mortali (APVR, sistemi anticaduta)

DPI PER AREA CORPOREA:
- TESTA: Caschi, cappelli, berretti
- OCCHI/VISO: Occhiali, visiere, maschere
- UDITO: Tappi, cuffie, caschi antirumore
- RESPIRATORIO: Mascherine, semimaschere, APVR
- MANI/BRACCIA: Guanti, manicotti, bracciali
- PIEDI/GAMBE: Scarpe, stivali, ginocchiere
- CORPO: Tute, grembiuli, giubbotti

NORME TECNICHE:
- EN 397: Caschi di protezione industriale
- EN 166: Protezione occhi
- EN 352: Protezione udito
- EN 149: Dispositivi respiratori
- EN 388: Guanti protettivi
- EN 20345: Calzature di sicurezza

FORMATO RISPOSTA: Fornisci sempre:
- DPI obbligatori per ogni rischio
- Caratteristiche tecniche specifiche
- Norme di riferimento
- Procedure di utilizzo
- Verifiche periodiche necessarie
""",
                description="Specifica i DPI necessari basandosi sui rischi identificati"
            )
        )
        
        # 5. Document Citation Agent
        citation_agent = autogen.AssistantAgent(
            **create_hse_agent_config(
                name="HSE_Citation_Agent",
                system_message="""
Sei un esperto HSE specializzato nella documentazione normativa e nelle citazioni precise.

RUOLO: Fornire citazioni accurate e strutturare l'output finale per il frontend.

RESPONSABILITÀ:
1. Citare normative e documenti pertinenti
2. Strutturare l'analisi per presentazione frontend
3. Creare roadmap di implementazione
4. Generare executive summary
5. Fornire metriche di performance

DOCUMENTAZIONE DA CITARE:
- Normative italiane (D.Lgs, D.M., etc.)
- Norme tecniche (UNI, CEI, ISO)
- Linee guida INAIL
- Circolari ministeriali
- Accordi Stato-Regioni
- Documentazione aziendale

STRUTTURA OUTPUT FINALE:
- Executive Summary (punteggio complessivo, criticità, raccomandazioni)
- Action Items prioritizzati
- Citations con rilevanza e requisiti chiave
- Completion Roadmap
- Performance Metrics

FORMATO CITAZIONI:
- Documento: Titolo completo e riferimento
- Articolo/Sezione specifica
- Rilevanza per il caso specifico
- Requisiti operativi derivanti

FORMATO RISPOSTA: Struttura sempre l'output finale come JSON con:
- executive_summary
- action_items (prioritizzati)
- citations (per categoria)
- completion_roadmap
- performance_metrics
""",
                description="Fornisce citazioni normative e struttura l'output finale"
            )
        )
        
        return {
            "content_analyst": content_analyst,
            "risk_analyst": risk_analyst,
            "compliance_checker": compliance_checker,
            "dpi_specialist": dpi_specialist,
            "citation_agent": citation_agent
        }
    
    def _create_group_chat(self) -> autogen.GroupChat:
        """Create group chat for agent collaboration"""
        return autogen.GroupChat(
            agents=list(self.agents.values()),
            messages=[],
            max_round=10,  # Limit conversation rounds
            speaker_selection_method="round_robin",  # Each agent speaks in turn
            allow_repeat_speaker=False
        )
    
    def _create_group_chat_manager(self) -> autogen.GroupChatManager:
        """Create group chat manager"""
        return autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=self.llm_config.__dict__,
            system_message="""
Sei il coordinatore dell'analisi HSE multi-agente. 

Il tuo ruolo è:
1. Guidare la discussione tra gli agenti specializzati
2. Garantire che tutti gli aspetti HSE siano coperti
3. Sintetizzare le conclusioni finali
4. Assicurare la qualità dell'output

Sequenza di analisi:
1. Content Analyst: Analizza qualità del contenuto
2. Risk Analyst: Identifica e valuta i rischi
3. Compliance Checker: Verifica conformità normativa
4. DPI Specialist: Specifica DPI necessari
5. Citation Agent: Struttura output finale

Mantieni la discussione focalizzata e produttiva.
"""
        )
    
    async def analyze_permit(
        self, 
        permit_data: Dict[str, Any], 
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Conduct comprehensive permit analysis using AutoGen agents
        """
        
        # Prepare analysis prompt
        permit_info = f"""
PERMESSO DI LAVORO DA ANALIZZARE:

ID: {permit_data.get('id')}
Titolo: {permit_data.get('title')}
Descrizione: {permit_data.get('description')}
Tipo di lavoro: {permit_data.get('work_type')}
Ubicazione: {permit_data.get('location')}
Durata stimata: {permit_data.get('duration_hours', 'Non specificata')} ore
Livello priorità: {permit_data.get('priority_level', 'Non specificato')}
Tags: {permit_data.get('tags', [])}

CONTESTO AZIENDALE:
Tenant ID: {self.user_context.get('tenant_id')}
Dipartimento: {self.user_context.get('department', 'Non specificato')}

DOCUMENTI NORMATIVI DISPONIBILI:
{len(context_documents)} documenti di riferimento disponibili per consultazione.

ISTRUZIONI:
Ogni agente deve analizzare il permesso dal proprio punto di vista specialistico e fornire:
1. Valutazione specifica della propria area di competenza
2. Identificazione di problemi o criticità
3. Raccomandazioni operative concrete
4. Riferimenti normativi applicabili

L'agente Citation deve infine strutturare tutto l'output in formato JSON per il frontend.
"""
        
        try:
            # Initiate group chat analysis
            response = await self.manager.a_initiate_chat(
                message=permit_info,
                max_turns=10
            )
            
            # Extract final structured output from the conversation
            final_message = response.chat_history[-1] if response.chat_history else {}
            
            return {
                "analysis_complete": True,
                "confidence_score": 0.85,  # Default confidence
                "conversation_history": response.chat_history,
                "final_analysis": final_message.get("content", ""),
                "agents_involved": list(self.agents.keys()),
                "processing_time": 0.0  # To be calculated by orchestrator
            }
            
        except Exception as e:
            return {
                "analysis_complete": False,
                "error": f"AutoGen analysis failed: {str(e)}",
                "confidence_score": 0.0,
                "agents_involved": [],
                "processing_time": 0.0
            }
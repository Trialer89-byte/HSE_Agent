from typing import Dict, Any, List
import autogen
from .autogen_config import get_autogen_llm_config


class SimpleAutoGenHSEAgents:
    """
    Simplified AutoGen HSE agents for testing
    """
    
    def __init__(self, user_context: Dict[str, Any], vector_service=None):
        self.user_context = user_context
        self.vector_service = vector_service  # Store for potential future use
        self.llm_config = get_autogen_llm_config()
        self.agents = self._create_simple_agents()
    
    def _create_simple_agents(self) -> Dict[str, autogen.AssistantAgent]:
        """Create simplified HSE agents"""
        
        # HSE Analyst Agent
        hse_analyst = autogen.AssistantAgent(
            name="HSE_Analyst",
            system_message="""
Sei un esperto HSE (Health, Safety, Environment) che analizza permessi di lavoro.

Il tuo compito è:
1. Analizzare il permesso di lavoro fornito
2. Identificare i rischi principali
3. Suggerire DPI (Dispositivi di Protezione Individuale) necessari
4. Verificare la conformità alle normative italiane (D.Lgs 81/2008)
5. Fornire raccomandazioni concrete

Rispondi sempre in italiano e usa terminologia tecnica HSE appropriata.
Struttura la tua risposta in modo chiaro e professionale.
""",
            llm_config=self.llm_config,
            max_consecutive_auto_reply=2,
            human_input_mode="NEVER"
        )
        
        # Safety Reviewer Agent
        safety_reviewer = autogen.AssistantAgent(
            name="Safety_Reviewer",
            system_message="""
Sei un revisore esperto di sicurezza sul lavoro.

Il tuo compito è:
1. Rivedere l'analisi fornita dall'HSE Analyst
2. Aggiungere considerazioni aggiuntive se necessarie
3. Validare le raccomandazioni proposte
4. Fornire un giudizio finale sulla sicurezza del lavoro

Concentrati su:
- Completezza dell'analisi dei rischi
- Adeguatezza delle misure di sicurezza proposte
- Conformità normativa
- Priorità degli interventi

Rispondi in italiano con un approccio critico e costruttivo.
""",
            llm_config=self.llm_config,
            max_consecutive_auto_reply=2,
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
        Simple permit analysis using 2 AutoGen agents
        """
        
        # Prepare analysis prompt
        permit_info = f"""
PERMESSO DI LAVORO DA ANALIZZARE:

Titolo: {permit_data.get('title')}
Descrizione: {permit_data.get('description')}
Tipo di lavoro: {permit_data.get('work_type')}
Ubicazione: {permit_data.get('location')}
Durata: {permit_data.get('duration_hours', 'Non specificata')} ore

Per favore analizza questo permesso dal punto di vista HSE e fornisci:
1. Identificazione dei rischi principali
2. DPI necessari
3. Misure di sicurezza richieste
4. Conformità normativa
5. Raccomandazioni operative
"""
        
        try:
            # Create group chat
            group_chat = autogen.GroupChat(
                agents=list(self.agents.values()),
                messages=[],
                max_round=6,
                speaker_selection_method="round_robin"
            )
            
            # Create manager
            manager = autogen.GroupChatManager(
                groupchat=group_chat,
                llm_config=self.llm_config,
                system_message="Coordina l'analisi HSE tra gli agenti specializzati."
            )
            
            # Start the conversation
            response = self.agents["hse_analyst"].initiate_chat(
                manager,
                message=permit_info,
                max_turns=6
            )
            
            # Extract conversation
            chat_history = group_chat.messages if hasattr(group_chat, 'messages') else []
            
            return {
                "analysis_complete": True,
                "confidence_score": 0.8,
                "conversation_history": chat_history,
                "agents_involved": list(self.agents.keys()),
                "processing_time": 0.0
            }
            
        except Exception as e:
            return {
                "analysis_complete": False,
                "error": f"AutoGen analysis failed: {str(e)}",
                "confidence_score": 0.0,
                "agents_involved": [],
                "processing_time": 0.0
            }
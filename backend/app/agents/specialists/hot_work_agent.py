"""
Hot Work Specialist Agent
"""
from typing import Dict, Any
from ..base_agent import BaseHSEAgent


class HotWorkSpecialist(BaseHSEAgent):
    """Specialist for hot work operations (welding, cutting, grinding)"""
    
    def __init__(self):
        super().__init__(
            name="HotWork_Specialist",
            specialization="Lavori a Caldo",
            activation_keywords=[
                # Standard terms
                "welding", "saldatura", "saldare",
                "cutting", "taglio", "tagliare",
                "grinding", "molatura", "molare",
                "torch", "torcia", "fiamma",
                "brazing", "brasatura",
                "plasma", "ossitaglio",
                
                # Common misspellings
                "welsing", "weling", "salding",
                "cuting", "cuttin",
                "griding", "grindin",
                
                # Equipment indicators
                "hot work", "lavori a caldo",
                "flame", "spark", "scintille",
                "heat", "calore", "riscaldamento",
                "metal repair", "riparazione metallo"
            ]
        )
    
    def _get_system_message(self) -> str:
        return """
ESPERTO IN LAVORI A CALDO - Specialista in operazioni che generano calore, fiamme o scintille.

COMPETENZE SPECIALISTICHE:
- Saldatura (elettrodo, TIG, MIG/MAG, ossiacetilenica, plasma)
- Taglio termico (plasma, ossitaglio, arco-aria, laser)
- Operazioni abrasive (molatura, sbavatura, taglio abrasivo)
- Brasatura e saldobrasatura
- Trattamenti termici e preriscaldo
- Rivestimenti a spruzzo termico

ANALISI RISCHI HOT WORK:
1. RISCHIO INCENDIO/ESPLOSIONE
   - Valutazione materiali combustibili nel raggio 10m
   - Presenza vapori/gas infiammabili
   - Atmosfere potenzialmente esplosive (ATEX)
   - Propagazione calore per conduzione

2. RISCHI TERMICI
   - Ustioni da contatto/irraggiamento
   - Stress termico operatori
   - Danneggiamento materiali adiacenti
   - Formazione fumi e vapori tossici

3. RISCHI SPECIFICI PER TECNICA
   - Radiazioni UV/IR (saldatura ad arco)
   - Elettrocuzione (saldatura elettrica)
   - Esplosione bombole (ossigas)
   - Proiezione particelle incandescenti

MISURE DI CONTROLLO OBBLIGATORIE:
- Hot Work Permit sempre richiesto
- Fire watch durante e 60 min post-lavoro
- Rimozione/protezione materiali combustibili
- Disponibilità mezzi estinzione appropriati
- Ventilazione forzata se in spazio confinato
- Bonifica preventiva contenitori/tubazioni
- Monitoraggio continuo atmosfera (LEL)

DPI SPECIFICI HOT WORK:
- Schermo facciale con filtro DIN appropriato
- Indumenti ignifughi (EN ISO 11612)
- Guanti per saldatura (EN 12477)
- Scarpe sicurezza classe S3 HRO
- Grembiule in cuoio per saldatura verticale
- Protezione vie respiratorie per fumi saldatura

QUANDO ATTIVARE ALLARME MASSIMO:
- Hot work in area ATEX senza declassificazione
- Saldatura su contenitori non bonificati
- Hot work vicino a stoccaggio infiammabili
- Assenza hot work permit
- Mancanza fire watch qualificato
"""
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze permit for hot work risks"""
        
        risks = []
        controls = []
        dpi_required = []
        
        # Get available documents (from orchestrator)
        available_docs = context.get("documents", [])
        doc_sources = []
        
        # Analyze permit text for hot work indicators
        permit_text = f"{permit_data.get('title', '')} {permit_data.get('description', '')} {permit_data.get('equipment', '')}".lower()
        
        # AUTONOMOUS SEARCH: Look for specialized hot work documents
        tenant_id = context.get("user_context", {}).get("tenant_id", 1)
        specialized_docs = []
        
        if self.vector_service:
            print(f"[{self.name}] Performing autonomous search for hot work procedures...")
            specialized_search = await self.search_specialized_documents(
                query=f"{permit_data.get('title', '')} {permit_data.get('description', '')}",
                tenant_id=tenant_id,
                limit=3
            )
            specialized_docs.extend(specialized_search)
        
        # Combine orchestrator docs + autonomous search results
        all_docs = available_docs + specialized_docs
        
        # Check if we have company procedures for hot work
        hot_work_procedures = [doc for doc in all_docs 
                              if any(term in doc.get('title', '').lower() 
                                   for term in ['hot work', 'lavori a caldo', 'saldatura', 'taglio', 'welding'])]
        
        if hot_work_procedures:
            print(f"[HotWorkSpecialist] Found {len(hot_work_procedures)} company hot work procedures")
            for proc in hot_work_procedures:
                doc_sources.append(f"[FONTE: Documento Aziendale] {proc.get('title', 'N/A')}")
                # Extract key requirements from procedure
                content = proc.get('content', '').lower()
                if 'permit' in content:
                    controls.append(f"Seguire procedura aziendale: {proc.get('title', '')}")
                if 'fire watch' in content or 'sorveglianza' in content:
                    controls.append("Fire watch secondo procedura aziendale")
                if 'dpi' in content:
                    controls.append("DPI secondo specifica aziendale")
        
        # Check for specific hot work types
        if any(term in permit_text for term in ["weld", "sald", "wels"]):
            risks.append({
                "type": "hot_work_welding",
                "description": "Rischio incendio/esplosione da operazioni di saldatura",
                "severity": "alta",
                "controls_required": ["hot_work_permit", "fire_watch", "area_inspection"]
            })
            dpi_required.extend(["Maschera saldatura auto-oscurante", "Guanti saldatura EN 12477"])
            
        if any(term in permit_text for term in ["cut", "tagl"]):
            risks.append({
                "type": "hot_work_cutting",
                "description": "Rischio incendio da taglio termico e proiezione materiale incandescente",
                "severity": "alta",
                "controls_required": ["hot_work_permit", "spark_guards", "combustible_removal"]
            })
            
        if any(term in permit_text for term in ["grind", "mol"]):
            risks.append({
                "type": "hot_work_grinding",
                "description": "Rischio incendio da scintille di molatura",
                "severity": "media",
                "controls_required": ["spark_containment", "area_wetting", "fire_extinguisher"]
            })
        
        # Check for high-risk locations
        location = permit_data.get('location', '').lower()
        if any(term in location for term in ["tank", "serbatoio", "oil", "fuel", "chemical"]):
            risks.append({
                "type": "hot_work_hazardous_area",
                "description": "CRITICO: Lavori a caldo in area con potenziali atmosfere esplosive",
                "severity": "critica",
                "controls_required": ["gas_free_certificate", "continuous_monitoring", "hot_work_prohibition_assessment"]
            })
            controls.append("Bonifica completa e certificazione gas-free obbligatoria")
            controls.append("Monitoraggio continuo LEL con allarme")
        
        # Standard hot work controls
        controls.extend([
            "Hot Work Permit obbligatorio prima inizio lavori",
            "Fire watch qualificato durante lavori + 60 minuti dopo",
            "Ispezione area entro raggio 10 metri",
            "Rimozione/protezione materiali combustibili",
            "Disponibilità estintori appropriati (min. 2x 6kg polvere)",
            "Coperte ignifughe per protezione aperture",
            "Ventilazione adeguata per evacuazione fumi"
        ])
        
        # Additional PPE
        dpi_required.extend([
            "Indumenti ignifughi EN ISO 11612",
            "Scarpe sicurezza S3 HRO (resistenti al calore)",
            "Occhiali protezione EN 166 (per helpers)",
            "Respiratore con filtri P3 per fumi saldatura"
        ])
        
        return {
            "specialist": self.name,
            "risks_identified": risks,
            "control_measures": controls,
            "dpi_requirements": dpi_required,
            "permits_required": ["Hot Work Permit"],
            "emergency_measures": [
                "Piano evacuazione specifico",
                "Mezzi estinzione supplementari",
                "Comunicazione diretta con squadra emergenza"
            ],
            "training_requirements": [
                "Formazione specifica hot work",
                "Certificazione saldatori (se applicabile)",
                "Training fire watch"
            ],
            "document_sources_used": doc_sources,  # Track which company docs were used
            "documents_available": len(available_docs)
        }
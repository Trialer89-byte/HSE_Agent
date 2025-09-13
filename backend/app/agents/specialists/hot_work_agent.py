"""
Hot Work Specialist Agent
"""
from typing import Dict, Any, List
from ..base_agent import BaseHSEAgent


class HotWorkSpecialist(BaseHSEAgent):
    """Specialist for hot work operations (welding, cutting, grinding)"""
    
    def __init__(self):
        super().__init__(
            name="HotWork_Specialist",
            specialization="Lavori a Caldo",
            activation_keywords=[]  # Activated by Risk Mapping Agent
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
        """Analyze permit for hot work risks and assess existing measures adequacy"""
        
        risks = []
        controls = []
        dpi_required = []
        
        # Get existing DPI and actions from permit
        existing_dpi = permit_data.get('dpi_required', [])
        existing_actions = permit_data.get('risk_mitigation_actions', [])
        
        # Normalize existing measures for comparison
        existing_dpi_lower = [str(dpi).lower() for dpi in existing_dpi] if existing_dpi else []
        existing_actions_lower = [str(action).lower() for action in existing_actions] if existing_actions else []
        
        # Get available documents (from orchestrator)
        available_docs = context.get("documents", [])
        doc_sources = []
        
        # AUTONOMOUS SEARCH: Look for specialized hot work documents
        tenant_id = context.get("user_context", {}).get("tenant_id", 1)
        specialized_docs = []
        
        # MANDATORY WEAVIATE SEARCH for hot work procedures
        try:
            print(f"[{self.name}] Performing mandatory Weaviate search for hot work procedures...")
            specialized_search = await self.search_specialized_documents(
                query=f"{permit_data.get('title', '')} {permit_data.get('description', '')}",
                tenant_id=tenant_id,
                limit=3
            )
            specialized_docs.extend(specialized_search)
            print(f"[{self.name}] Weaviate search completed: {len(specialized_search)} documents found")
        except Exception as e:
            print(f"[{self.name}] WARNING: Weaviate search failed: {e} - proceeding without specialized documents")
            # Continue without specialized documents instead of failing
        
        # Combine orchestrator docs + autonomous search results
        all_docs = available_docs + specialized_docs
        
        # Create AI analysis prompt for hot work
        permit_summary = f"""
PERMESSO DI LAVORO - ANALISI LAVORI A CALDO:

TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
ATTREZZATURE: {permit_data.get('equipment', 'N/A')}

DPI ATTUALMENTE PREVISTI:
{existing_dpi if existing_dpi else 'Nessun DPI specificato'}

AZIONI MITIGAZIONE RISCHI ATTUALI:
{existing_actions if existing_actions else 'Nessuna azione specificata'}

ANALIZZA IL SEGUENTE per LAVORI A CALDO:
1. Questo lavoro comporta operazioni a caldo (saldatura, taglio, molatura, fiamma, scintille)?
2. Che tipo di lavoro a caldo (saldatura, ossitaglio, molatura, brasatura, ecc.)?
3. L'ubicazione presenta rischi aggiuntivi (vicinanza combustibili, atmosfere esplosive)?
4. Le attuali DPI sono adeguate per lavori a caldo (ignifughe, protezione occhi, respiratori)?
5. Le attuali procedure includono fire watch, hot work permit, bonifica area?
6. Quali DPI specifiche mancano per protezione da calore/scintille/fumi?
7. Quali controlli antincendio sono necessari?

Fornisci risposta strutturata in JSON con:
- hot_work_detected: boolean
- work_type: "saldatura|taglio|molatura|brasatura|altro|nessuno"
- risk_level: "basso|medio|alto|critico"
- location_hazards: array di rischi ubicazione (combustibili, ATEX, ecc.)
- specific_risks: array con type, description, severity
- existing_dpi_adequacy: "adeguata|inadeguata|parziale"
- existing_actions_adequacy: "adeguate|inadeguate|parziali"
- missing_dpi: array di DPI mancanti (ignifughi, protezione, respiratori)
- missing_controls: array di controlli mancanti (fire watch, permit, bonifica)
- fire_prevention_measures: array di misure antincendio specifiche
- recommendations: raccomandazioni prioritarie
        """
        
        # Get AI analysis
        try:
            ai_response = await self.get_gemini_response(permit_summary, all_docs)
            # Parse AI response
            import json
            import re
            
            # Extract JSON from AI response
            json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
            if json_match:
                ai_analysis = json.loads(json_match.group())
            else:
                # No valid JSON found - return error, don't use hardcoded fallback
                print(f"[{self.name}] No valid JSON response from AI")
                return self.create_error_response("AI did not provide valid JSON analysis")
                
        except Exception as e:
            print(f"[{self.name}] AI analysis failed: {e}")
            # Return error - no hardcoded fallback
            return self.create_error_response(str(e))
        
        # Build response based on AI analysis
        if ai_analysis.get("hot_work_detected", False):
            classification = "LAVORI A CALDO IDENTIFICATI"
            
            # Convert AI analysis to standard format
            risks_identified = []
            for risk in ai_analysis.get("specific_risks", []):
                risks_identified.append({
                    "type": risk.get("type", "hot_work_risk"),
                    "source": self.name,
                    "description": risk.get("description", "Rischio lavori a caldo"),
                    "severity": risk.get("severity", "alto")
                })
            
            # Analyze existing actions and provide consolidated recommendations
            recommended_actions = self._analyze_and_recommend_hotwork_actions(
                existing_actions,
                ai_analysis.get("missing_controls", []),
                ai_analysis.get("work_type", "altro"),
                ai_analysis.get("hot_work_detected", False)
            )
            
            
            return {
                "specialist": self.name,
                "classification": classification,
                "ai_analysis_used": True,
                "work_type": ai_analysis.get("work_type", "altro"),
                "risks_identified": risks_identified,
                "recommended_actions": recommended_actions,
                "existing_measures_evaluation": {
                    "existing_dpi": existing_dpi,
                    "existing_actions": existing_actions,
                    "dpi_adequacy": ai_analysis.get("existing_dpi_adequacy", "da_valutare").upper(),
                    "actions_adequacy": ai_analysis.get("existing_actions_adequacy", "da_valutare").upper(),
                    "ai_assessment": ai_analysis.get("recommendations", []),
                    "risk_level": ai_analysis.get("risk_level", "alto"),
                    "work_type_detected": ai_analysis.get("work_type", "altro"),
                    "location_hazards": ai_analysis.get("location_hazards", []),
                    "critical_gaps": {
                        "missing_dpi": len(ai_analysis.get("missing_dpi", []))
                    }
                },
                "fire_prevention_measures": ai_analysis.get("fire_prevention_measures", []),
                "permits_required": ["Hot Work Permit"] if ai_analysis.get("hot_work_detected") else [],
                "document_citations": [
                    {
                        "type": "documento_aziendale_hot_work",
                        "source": doc.get('title', 'N/A'),
                        "description": "Procedura aziendale per lavori a caldo",
                        "mandatory": True
                    } for doc in all_docs if 'hot work' in doc.get('title', '').lower() or 'caldo' in doc.get('title', '').lower()
                ],
                "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
            }
        
        return {
            "specialist": self.name,
            "classification": "Nessun lavoro a caldo identificato",
            "ai_analysis_used": True,
            "risks_identified": [],
            "recommended_actions": [],
            "existing_measures_evaluation": {
                "existing_dpi": existing_dpi,
                "existing_actions": existing_actions,
                "dpi_adequacy": "N/A - Lavoro non a caldo",
                "actions_adequacy": "N/A - Lavoro non a caldo",
                "ai_assessment": ["Nessun rischio specifico per lavori a caldo identificato"],
                "risk_level": ai_analysis.get("risk_level", "basso")
            },
            "raw_ai_response": ai_response[:500] if 'ai_response' in locals() else "N/A"
        }

    def _analyze_and_recommend_hotwork_actions(
        self, 
        existing_actions: List[str], 
        ai_suggested_controls: List[str],
        work_type: str,
        hot_work_detected: bool
    ) -> List[Dict[str, Any]]:
        """
        Analyze existing actions and provide hot work safety recommendations by criticality
        Limited to max 10 actions prioritized by fire/explosion risk severity
        """
        recommendations = []
        
        # Critical actions (mandatory for hot work)
        critical_actions = []
        if hot_work_detected:
            if work_type in ["saldatura", "welding", "taglio_termico"]:
                critical_actions.extend([
                    "Emissione Hot Work Permit obbligatorio",
                    "Presenza Fire Watch durante e 30min dopo lavori",
                    "Rimozione/protezione materiali combustibili entro 11 metri",
                    "Verifica sistema antincendio funzionante"
                ])
            elif work_type == "brazing":
                critical_actions.extend([
                    "Controllo atmosfera esplosiva con rilevatore",
                    "Presenza Fire Watch obbligatoria"
                ])
            else:  # Generic hot work
                critical_actions.extend([
                    "Verifica assenza atmosfere esplosive",
                    "Delimitazione area di sicurezza"
                ])
        
        # High priority actions
        high_priority_actions = []
        for control in ai_suggested_controls[:3]:  # Top 3 AI suggestions
            if control not in critical_actions:
                high_priority_actions.append(control)
        
        # Medium priority actions (improvements to existing measures)
        medium_priority_actions = []
        if existing_actions:
            medium_priority_actions.append("Verifica adeguatezza misure antincendio esistenti")
            medium_priority_actions.append("Aggiornamento procedure Hot Work")
        else:
            medium_priority_actions.extend([
                "Sviluppo procedura Hot Work specifica",
                "Formazione personale su rischi incendio/esplosione"
            ])
        
        # Build prioritized recommendations
        action_id = 1
        
        # Add critical actions
        for action in critical_actions[:4]:  # Max 4 critical
            recommendations.append({
                "id": action_id,
                "action": action,
                "criticality": "critica",
                "type": "fire_prevention"
            })
            action_id += 1
        
        # Add high priority actions  
        for action in high_priority_actions[:3]:  # Max 3 high
            recommendations.append({
                "id": action_id,
                "action": action,
                "criticality": "alta",
                "type": "hot_work_control"
            })
            action_id += 1
            
        # Add medium priority actions
        for action in medium_priority_actions[:3]:  # Max 3 medium
            recommendations.append({
                "id": action_id,
                "action": action,
                "criticality": "media",
                "type": "hot_work_improvement"
            })
            action_id += 1
            
        # Limit to maximum 10 total actions
        return recommendations[:10]
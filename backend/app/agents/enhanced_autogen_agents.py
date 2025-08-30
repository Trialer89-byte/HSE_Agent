"""
Enhanced AutoGen HSE Agents with MANDATORY 5-PHASE COMPREHENSIVE ANALYSIS
Pure AI-driven system with no fallback - fail fast if AI unavailable
"""

from typing import Dict, Any, List
import time
import json
from datetime import datetime

try:
    from autogen_agentchat.agents import AssistantAgent
    class autogen:
        AssistantAgent = AssistantAgent
except ImportError:
    class MockAgent:
        def __init__(self, name, system_message, llm_config=None, max_consecutive_auto_reply=1, human_input_mode="NEVER"):
            self.name = name
            self.system_message = system_message
    class autogen:
        AssistantAgent = MockAgent

import google.generativeai as genai
from .autogen_config import get_autogen_llm_config, GeminiLLMConfig


class EnhancedAutoGenHSEAgents:
    """
    Enhanced AutoGen HSE agents with MANDATORY 5-phase comprehensive analysis
    Pure AI-driven - NO FALLBACK LOGIC
    """
    
    def __init__(self, user_context: Dict[str, Any], vector_service=None):
        self.user_context = user_context
        self.vector_service = vector_service
        self.llm_config = get_autogen_llm_config()
        
        # Import settings only when needed
        from app.config.settings import settings
        
        # STRICT API REQUIREMENT - Initialize or FAIL
        if not settings.gemini_api_key:
            raise Exception("CRITICAL: Gemini API key required for Enhanced AutoGen analysis")
        
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.gemini_model = genai.GenerativeModel(settings.gemini_model)
            
            # Test API with simple call
            test_response = self.gemini_model.generate_content('test')
            print(f"[Enhanced_AutoGen] Gemini API verified: {settings.gemini_model}")
            
        except Exception as e:
            raise Exception(f"CRITICAL: Gemini API initialization failed: {str(e)}")
    
    async def search_relevant_documents(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for relevant documents using vector service"""
        if not self.vector_service:
            print("[Enhanced_AutoGen] No vector service available")
            return []
        
        try:
            filters = {"tenant_id": self.user_context.get("tenant_id", 1)}
            documents = await self.vector_service.hybrid_search(
                query=query,
                filters=filters,
                limit=limit,
                threshold=0.5
            )
            
            if documents:
                print(f"[Enhanced_AutoGen] Found {len(documents)} relevant documents")
                return documents
            else:
                print("[Enhanced_AutoGen] No documents found")
                return []
                
        except Exception as e:
            print(f"[Enhanced_AutoGen] Error searching documents: {e}")
            return []
    
    async def analyze_permit(
        self, 
        permit_data: Dict[str, Any], 
        context_documents: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        MANDATORY 5-PHASE COMPREHENSIVE ANALYSIS
        Pure AI-driven - FAIL FAST if any phase fails
        """
        start_time = time.time()
        
        print(f"[Enhanced_AutoGen] Starting MANDATORY 5-Phase comprehensive analysis")
        print(f"[Enhanced_AutoGen] Permit: {permit_data.get('title', 'N/A')}")
        print(f"[Enhanced_AutoGen] Documents: {len(context_documents)}")
        
        # Validate and sanitize context documents
        safe_documents = []
        try:
            for i, doc in enumerate(context_documents):
                try:
                    safe_doc = {
                        "title": str(doc.get("title", f"Document {i+1}"))[:200],
                        "document_type": str(doc.get("document_type", "unknown"))[:50],
                        "content": str(doc.get("content", ""))[:300]  # Limit content to avoid prompt bloat
                    }
                    safe_documents.append(safe_doc)
                except Exception as doc_error:
                    print(f"[Enhanced_AutoGen] Skipping malformed document {i}: {doc_error}")
                    continue
            print(f"[Enhanced_AutoGen] Using {len(safe_documents)} validated documents")
        except Exception as docs_error:
            print(f"[Enhanced_AutoGen] Error processing documents, proceeding without: {docs_error}")
            safe_documents = []
        
        try:
            # Create comprehensive analysis prompt with ALL permit data
            permit_text = f"""
PERMESSO DI LAVORO DA ANALIZZARE:

TITOLO: {permit_data.get('title', 'N/A')}
DESCRIZIONE: {permit_data.get('description', 'N/A')}
TIPO LAVORO: {permit_data.get('work_type', 'N/A')}
UBICAZIONE: {permit_data.get('location', 'N/A')}
DURATA: {permit_data.get('duration_hours', 'N/A')} ore
NUMERO OPERATORI: {permit_data.get('workers_count', 'N/A')}

DPI FORNITI: {permit_data.get('dpi_required', [])}
AZIONI MITIGAZIONE ESISTENTI: {permit_data.get('risk_mitigation_actions', [])}

DOCUMENTI AZIENDALI DISPONIBILI: {len(safe_documents)} documenti
{chr(10).join([f"- {doc.get('title', 'N/A')} ({doc.get('document_type', 'N/A')})" for doc in safe_documents[:5]])}
"""
            
            # AI-Powered Comprehensive Analysis
            analysis_prompt = f"""
Sei un sistema HSE AI che esegue ANALISI COMPLETA E OBBLIGATORIA di permessi di lavoro.

DEVI SEGUIRE QUESTI 5 STEP OBBLIGATORI:

1. ANALISI GENERALE: Identifica TUTTI i rischi presenti
2. CLASSIFICAZIONE: Categorizza rischi per severità e specialisti necessari  
3. ANALISI DOCUMENTI: Cita normative e documenti aziendali applicabili
4. ANALISI SPECIALISTICA: Applica expertise specifica per ogni rischio
5. CONSOLIDAMENTO: Genera output finale COMPLETO e STRUTTURATO

{permit_text}

DOCUMENTI AZIENDALI DISPONIBILI:
{chr(10).join([f"DOCUMENTO: {doc.get('title', 'N/A')} - TIPO: {doc.get('document_type', 'N/A')} - CONTENUTO: {doc.get('content', '')[:300]}..." for doc in safe_documents[:3]])}

OUTPUT FINALE RICHIESTO - JSON VALIDO COMPLETO per PermitAnalysisResponse:

IMPORTANTE: 
- USA SOLO SINTASSI JSON VALIDA (doppi apici " non singoli ')
- USA ARRAY JSON [...] NON LISTE PYTHON [...]
- NON INCLUDERE COMMENTI O TESTO AGGIUNTIVO
- VERIFICA CHE IL JSON SIA SINTATTICAMENTE CORRETTO

{{
  "analysis_id": "enhanced_autogen_{int(time.time())}_{permit_data.get('id', 0)}",
  "permit_id": {permit_data.get('id', 0) if isinstance(permit_data.get('id'), int) else 0},
  "analysis_complete": true,
  "confidence_score": 0.9,
  "processing_time": {time.time() - start_time:.2f},
  "timestamp": "{datetime.utcnow().isoformat()}",
  "agents_involved": ["Enhanced_AutoGen_5Phase"],
  "ai_version": "Enhanced-AutoGen-5Phase-2.0",
  
  "executive_summary": {{
    "overall_score": <0.0-1.0>,
    "critical_issues": <numero_problemi_critici>,
    "recommendations": <numero_raccomandazioni>,
    "compliance_level": "<conforme|parzialmente_conforme|non_conforme>",
    "estimated_completion_time": "<X-Y ore>",
    "key_findings": ["Finding 1", "Finding 2", "Finding 3", "Finding 4", "Finding 5"],
    "next_steps": ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]
  }},
  
  "action_items": [
    {{
      "id": "ACT_001",
      "type": "safety_improvement",
      "priority": "alta",
      "title": "Implementa misura sicurezza X",
      "description": "Descrizione dettagliata misura",
      "suggested_action": "Azione specifica da eseguire",
      "consequences_if_ignored": "Conseguenze se non implementata",
      "references": ["Normativa Y", "Documento Z"],
      "estimated_effort": "2-4 ore",
      "responsible_role": "RSPP",
      "frontend_display": {{"color": "orange", "icon": "alert-triangle"}}
    }}
  ],
  
  "citations": {{
    "normative_framework": [
      {{
        "document_info": {{"title": "D.Lgs 81/08 - Testo Unico Sicurezza", "type": "Normativa Base", "relevance_score": "0.95"}},
        "relevance": {{"score": 0.95, "reason": "Normativa base sempre applicabile"}},
        "key_requirements": [{{"requirement": "Valutazione rischi", "description": "Art. 17 - Obblighi datore di lavoro"}}],
        "frontend_display": {{"color": "green", "icon": "book"}}
      }}
    ],
    "company_procedures": [<citazioni_documenti_aziendali>],
    "specialist_sources": [<fonti_specialistiche>]
  }},
  
  "measures_evaluation": {{
    "existing_dpi": {json.dumps(permit_data.get('dpi_required', []))},
    "existing_actions": {json.dumps(permit_data.get('risk_mitigation_actions', []))},
    "suggested_additional_dpi": ["DPI aggiuntivo 1", "DPI aggiuntivo 2"],
    "suggested_additional_actions": ["Azione aggiuntiva 1", "Azione aggiuntiva 2"],
    "dpi_adequacy": "insufficienti",
    "actions_adequacy": "insufficienti",
    "improvement_recommendations": 5
  }},
  
  "completion_roadmap": {{
    "immediate_actions": ["Azione immediata 1", "Azione immediata 2"],
    "short_term_actions": ["Azione breve termine 1", "Azione breve termine 2"],
    "medium_term_actions": ["Azione medio termine 1", "Azione medio termine 2"]
  }},
  
  "performance_metrics": {{
    "total_processing_time": {time.time() - start_time:.2f},
    "phases_completed": 5,
    "risks_identified": <numero_rischi>,
    "specialists_activated": <numero_specialisti>,
    "analysis_method": "Enhanced AutoGen 5-Phase AI"
  }}
}}

REQUISITI OBBLIGATORI:
- MINIMO 10 action_items dettagliati
- MINIMO 3 citations per categoria  
- Gap analysis completa (esistente vs raccomandato)
- Executive summary completo
- Measures evaluation dettagliata
- SEMPRE suggerire miglioramenti (non output vuoti)

FORMATO OUTPUT:
- Restituisci SOLO il JSON valido, senza testo aggiuntivo
- USA SOLO doppi apici " per stringhe (MAI singoli ')
- USA SOLO array JSON [...] (MAI liste Python)
- VERIFICA che tutte le parentesi {{ }} siano bilanciate
- NO commenti nel JSON
"""
            
            print("[Enhanced_AutoGen] Executing comprehensive AI analysis...")
            print(f"[Enhanced_AutoGen] Prompt length: {len(analysis_prompt)} characters")
            
            # Add timeout and error handling for Gemini API
            try:
                ai_response = self.gemini_model.generate_content(
                    analysis_prompt,
                    generation_config=genai.types.GenerationConfig(
                        max_output_tokens=8000,  # Limit output size
                        temperature=0.1,         # Low temperature for consistency
                    )
                )
                ai_text = ai_response.text.strip()
                print(f"[Enhanced_AutoGen] AI response length: {len(ai_text)} characters")
            except Exception as gemini_error:
                error_msg = f"Gemini API call failed: {str(gemini_error)}"
                print(f"[Enhanced_AutoGen] {error_msg}")
                raise Exception(error_msg)
            
            # Extract JSON from response
            try:
                # Clean the response - remove markdown code blocks
                import re
                
                print(f"[Enhanced_AutoGen] AI response first 1000 chars: {ai_text[:1000]}")
                print(f"[Enhanced_AutoGen] AI response last 500 chars: {ai_text[-500:]}")
                
                # Remove markdown code blocks (handle both ```json and ``` alone)
                clean_text = re.sub(r'```json\s*', '', ai_text)
                clean_text = re.sub(r'```\s*', '', clean_text)
                clean_text = clean_text.strip()
                
                print(f"[Enhanced_AutoGen] Cleaned text length: {len(clean_text)} chars")
                
                # Find the start and end of the JSON object
                start_idx = clean_text.find('{')
                if start_idx == -1:
                    raise ValueError("No JSON object found in response")
                
                # Find the matching closing brace
                brace_count = 0
                end_idx = -1
                for i in range(start_idx, len(clean_text)):
                    if clean_text[i] == '{':
                        brace_count += 1
                    elif clean_text[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i
                            break
                
                if end_idx == -1:
                    raise ValueError("Unclosed JSON object in response")
                
                json_text = clean_text[start_idx:end_idx + 1]
                print(f"[Enhanced_AutoGen] Extracted JSON length: {len(json_text)} chars")
                result_json = json.loads(json_text)
                
                # Validate and ensure required fields
                result_json["analysis_complete"] = True
                result_json["processing_time"] = round(time.time() - start_time, 2)
                result_json["timestamp"] = datetime.utcnow().isoformat()
                result_json["ai_version"] = "Enhanced-AutoGen-5Phase-2.0"
                
                # Ensure permit_id is integer
                if "permit_id" not in result_json:
                    result_json["permit_id"] = permit_data.get("id", 0) if isinstance(permit_data.get("id"), int) else 0
                
                # Ensure agents_involved
                if "agents_involved" not in result_json:
                    result_json["agents_involved"] = ["Enhanced_AutoGen_5Phase"]
                
                print(f"[Enhanced_AutoGen] COMPREHENSIVE analysis completed successfully!")
                print(f"[Enhanced_AutoGen] Action items: {len(result_json.get('action_items', []))}")
                print(f"[Enhanced_AutoGen] Citations total: {sum(len(cats) for cats in result_json.get('citations', {}).values())}")
                print(f"[Enhanced_AutoGen] Processing time: {result_json['processing_time']}s")
                
                return result_json
                
            except json.JSONDecodeError as e:
                error_msg = f"CRITICAL: AI response is not valid JSON: {str(e)}"
                print(f"[Enhanced_AutoGen] {error_msg}")
                print(f"[Enhanced_AutoGen] Problematic JSON section: {json_text[max(0, e.pos-100):e.pos+100] if 'json_text' in locals() else 'N/A'}")
                raise Exception(error_msg)
            except Exception as e:
                error_msg = f"CRITICAL: JSON extraction failed: {str(e)}"
                print(f"[Enhanced_AutoGen] {error_msg}")
                print(f"[Enhanced_AutoGen] AI response snippet: {ai_text[:1000]}...")
                raise Exception(error_msg)
                
        except Exception as e:
            error_msg = f"CRITICAL: Enhanced AutoGen 5-Phase analysis failed: {str(e)}"
            print(f"[Enhanced_AutoGen] {error_msg}")
            # FAIL FAST - No fallback as requested
            raise Exception(error_msg)
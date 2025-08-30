#!/usr/bin/env python3
"""
Test del nuovo Enhanced AutoGen System con 5 fasi obbligatorie
"""
import requests
import json

# Configurazione
BASE_URL = "http://localhost:8000"
TENANT_ID = 1

def test_enhanced_autogen():
    """Test del nuovo Enhanced AutoGen con 5 fasi obbligatorie"""
    
    # Dati di test - permesso complesso per testare il sistema
    test_data = {
        "force_reanalysis": True  # Force new analysis to bypass cache
        # Enhanced AutoGen è l'unico orchestratore - parametro rimosso
    }
    
    # Test with existing permit ID 9 (from previous examples)
    permit_id = 9
    
    print("TEST ENHANCED AUTOGEN SYSTEM - 5 PHASE ANALYSIS")
    print("=" * 70)
    print(f"Testing permit ID: {permit_id}")
    print(f"System: Enhanced AutoGen 5-Phase (only orchestrator available)")
    print(f"Force reanalysis: {test_data['force_reanalysis']}")
    print()
    
    # Test with actual permit analysis endpoint to bypass cache
    print("Esecuzione Enhanced AutoGen 5-Phase Analysis...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/test/permits/{permit_id}/analyze",
        headers={"X-Tenant-ID": str(TENANT_ID)},
        json=test_data,
        timeout=120  # Longer timeout for AI analysis
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        analysis = response.json()
        
        print("\nRISULTATI ENHANCED AUTOGEN SYSTEM:")
        print("=" * 50)
        
        # Verifica AI version
        ai_version = analysis.get('ai_version', 'N/A')
        print(f"AI Version: {ai_version}")
        
        if 'Enhanced-AutoGen' in ai_version:
            print("✅ SUCCESSO: Enhanced AutoGen attivo!")
        else:
            print("❌ ATTENZIONE: Sistema vecchio in uso")
        
        # Verifica processing time
        processing_time = analysis.get('processing_time', 0)
        print(f"Processing Time: {processing_time}s")
        
        # Verifica agents involved  
        agents = analysis.get('agents_involved', [])
        print(f"Agents: {agents}")
        
        # Verifica executive summary
        exec_summary = analysis.get('executive_summary', {})
        print(f"\nEXECUTIVE SUMMARY:")
        print(f"  Overall Score: {exec_summary.get('overall_score', 'N/A')}")
        print(f"  Critical Issues: {exec_summary.get('critical_issues', 0)}")
        print(f"  Recommendations: {exec_summary.get('recommendations', 0)}")
        print(f"  Compliance Level: {exec_summary.get('compliance_level', 'N/A')}")
        
        # Verifica action items
        action_items = analysis.get('action_items', [])
        print(f"\nACTION ITEMS: {len(action_items)}")
        
        if len(action_items) >= 10:
            print("✅ SUCCESSO: Minimo 10 action items generati!")
            for i, item in enumerate(action_items[:5], 1):
                print(f"  {i}. [{item.get('priority', 'N/A')}] {item.get('title', 'N/A')[:50]}...")
        else:
            print("❌ PROBLEMA: Meno di 10 action items generati")
        
        # Verifica citations
        citations = analysis.get('citations', {})
        total_citations = sum(len(cats) for cats in citations.values())
        print(f"\nCITATIONS: {total_citations} totali")
        
        for cat, cites in citations.items():
            print(f"  {cat}: {len(cites)} citations")
        
        if total_citations >= 3:
            print("✅ SUCCESSO: Citations presenti!")
        else:
            print("❌ PROBLEMA: Citations insufficienti")
        
        # Verifica measures evaluation
        measures_eval = analysis.get('measures_evaluation', {})
        additional_dpi = measures_eval.get('suggested_additional_dpi', [])
        additional_actions = measures_eval.get('suggested_additional_actions', [])
        
        print(f"\nMEASURES EVALUATION:")
        print(f"  Existing DPI: {measures_eval.get('existing_dpi', [])}")
        print(f"  Additional DPI suggested: {len(additional_dpi)}")
        print(f"  Additional actions suggested: {len(additional_actions)}")
        print(f"  DPI adequacy: {measures_eval.get('dpi_adequacy', 'N/A')}")
        print(f"  Actions adequacy: {measures_eval.get('actions_adequacy', 'N/A')}")
        
        total_improvements = len(additional_dpi) + len(additional_actions)
        if total_improvements > 0:
            print("✅ SUCCESSO: Suggerimenti di miglioramento identificati!")
        else:
            print("❌ PROBLEMA: Nessun miglioramento suggerito")
        
        # Verifica performance metrics
        performance = analysis.get('performance_metrics', {})
        phases = performance.get('phases_completed', 0)
        risks_identified = performance.get('risks_identified', 0)
        
        print(f"\nPERFORMANCE METRICS:")
        print(f"  Phases completed: {phases}/5")
        print(f"  Risks identified: {risks_identified}")
        print(f"  Analysis method: {performance.get('analysis_method', 'N/A')}")
        
        # Verifica roadmap
        roadmap = analysis.get('completion_roadmap', {})
        immediate = roadmap.get('immediate_actions', [])
        print(f"\nCOMPLETION ROADMAP:")
        print(f"  Immediate actions: {len(immediate)}")
        
        print(f"\n{'='*70}")
        
        # Valutazione finale
        success_criteria = [
            ('Enhanced AutoGen Active', 'Enhanced-AutoGen' in ai_version),
            ('Min 10 Action Items', len(action_items) >= 10),
            ('Citations Present', total_citations >= 3),
            ('Improvements Suggested', total_improvements > 0),
            ('5 Phases Completed', phases == 5),
            ('Processing Time Reasonable', processing_time < 30)
        ]
        
        passed = sum(1 for _, condition in success_criteria if condition)
        total = len(success_criteria)
        
        print(f"SUCCESS CRITERIA: {passed}/{total}")
        for criterion, condition in success_criteria:
            status = "✅" if condition else "❌"
            print(f"  {status} {criterion}")
        
        if passed >= 4:
            print("\n🎉 ENHANCED AUTOGEN SYSTEM FUNZIONA BENE!")
        else:
            print("\n⚠️  SISTEMA PARZIALMENTE FUNZIONANTE - Verificare configurazione")
            
    else:
        print(f"ERRORE: {response.status_code}")
        try:
            error_data = response.json()
            error_msg = error_data.get('error', {}).get('message', 'N/A')
            print(f"Dettagli: {error_msg}")
            
            # Se l'errore è relativo all'API Gemini, mostra le info
            if 'Gemini' in error_msg or 'API' in error_msg:
                print("\n💡 NOTA: Il sistema Enhanced AutoGen richiede API Gemini configurata")
                print("   - Verificare GEMINI_API_KEY nelle variabili ambiente")
                print("   - Il sistema ora fallisce velocemente se l'AI non è disponibile")
                print("   - Nessun fallback presente come richiesto")
        except:
            print(f"Response: {response.text[:200]}...")

if __name__ == "__main__":
    test_enhanced_autogen()
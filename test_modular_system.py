#!/usr/bin/env python3
"""
Test specifico del nuovo Modular Orchestrator
"""
import requests
import json

# Configurazione
BASE_URL = "http://localhost:8000"
TENANT_ID = 1

def test_modular_orchestrator():
    """Test del nuovo modular orchestrator"""
    
    # Dati di test - permesso complesso
    test_data = {
        "title": "Sostituzione tubazione vapore alta pressione",
        "description": "Rimozione e sostituzione tubazione vapore 6 bar. Necessario taglio con plasma e saldatura elettrodo. Tubazione contiene vapore ad alta temperatura.",
        "work_type": "meccanico", 
        "location": "Reparto produzione - linea vapore principale",
        "risk_level": "high",
        "risk_mitigation_actions": ["Isolamento linea", "Supervisione"],
        "orchestrator": "fast"  # IMPORTANTE: Usa il nostro Modular Orchestrator
    }
    
    print("TEST NUOVO MODULAR ORCHESTRATOR")
    print("=" * 60)
    print(f"Permesso: {test_data['title']}")
    print(f"Orchestrator: {test_data['orchestrator']} (Modular)")
    print(f"Tipo lavoro: {test_data['work_type']}")
    print(f"Risk level: {test_data['risk_level']}")
    print()
    
    # Test con preview (per evitare problemi di schema)
    print("Esecuzione analisi con nuovo sistema...")
    
    response = requests.post(
        f"{BASE_URL}/api/v1/test/permits/analyze-preview",
        headers={"X-Tenant-ID": str(TENANT_ID)},
        json=test_data
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        analysis = response.json()
        
        print("\nRISULTATI NUOVO SISTEMA:")
        print("=" * 40)
        
        # Verifica AI version
        ai_version = analysis.get('ai_version', 'N/A')
        print(f"AI Version: {ai_version}")
        
        if 'Complete-Modular' in ai_version:
            print("✅ SUCCESSO: Nuovo sistema attivo!")
        else:
            print("❌ ATTENZIONE: Sistema vecchio in uso")
        
        # Verifica action items
        action_items = analysis.get('action_items', [])
        print(f"\nAction Items: {len(action_items)}")
        
        if len(action_items) > 0:
            print("✅ SUCCESSO: Action items generati!")
            for i, item in enumerate(action_items[:3], 1):
                print(f"  {i}. {item.get('title', 'N/A')[:50]}...")
        else:
            print("❌ PROBLEMA: Nessun action item generato")
        
        # Verifica measures evaluation
        measures_eval = analysis.get('measures_evaluation', {})
        additional_dpi = measures_eval.get('suggested_additional_dpi', [])
        additional_actions = measures_eval.get('suggested_additional_actions', [])
        
        print(f"\nMiglioramenti suggeriti:")
        print(f"  DPI aggiuntivi: {len(additional_dpi)}")
        print(f"  Azioni aggiuntive: {len(additional_actions)}")
        
        total_improvements = len(additional_dpi) + len(additional_actions)
        if total_improvements > 0:
            print("✅ SUCCESSO: Miglioramenti identificati!")
        else:
            print("❌ PROBLEMA: Nessun miglioramento suggerito")
        
        # Verifica analisi documenti
        doc_compliance = analysis.get('document_compliance', {})
        docs_analyzed = doc_compliance.get('documents_analyzed', False)
        print(f"\nDocumenti analizzati: {docs_analyzed}")
        
        # Performance
        performance = analysis.get('performance_metrics', {})
        phases = performance.get('analysis_phases_completed', 0)
        processing_time = performance.get('total_processing_time', 0)
        
        print(f"\nPerformance:")
        print(f"  Fasi completate: {phases}/5")
        print(f"  Tempo elaborazione: {processing_time:.2f}s")
        
        if phases == 5:
            print("✅ SUCCESSO: Tutte le fasi completate!")
        
        # Verifica agenti coinvolti
        agents = analysis.get('agents_involved', [])
        print(f"\nAgenti coinvolti: {agents}")
        
        expected_agents = ['General_Analysis', 'Risk_Classifier', 'Document_Analysis']
        has_new_agents = any(agent in agents for agent in expected_agents)
        
        if has_new_agents:
            print("✅ SUCCESSO: Nuovi agenti attivi!")
        else:
            print("❌ ATTENZIONE: Agenti vecchi in uso")
        
        print(f"\n{'='*60}")
        if ('Complete-Modular' in ai_version and 
            len(action_items) > 0 and 
            total_improvements > 0 and
            phases == 5):
            print("🎉 NUOVO SISTEMA FUNZIONA PERFETTAMENTE!")
        else:
            print("⚠️  SISTEMA PARZIALMENTE FUNZIONANTE - Controllare configurazione")
            
    else:
        print(f"ERRORE: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Dettagli: {error_data.get('error', {}).get('message', 'N/A')}")
        except:
            print(f"Response: {response.text[:200]}...")

if __name__ == "__main__":
    test_modular_orchestrator()
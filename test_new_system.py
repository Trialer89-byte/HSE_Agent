#!/usr/bin/env python3
"""
Test del nuovo sistema di analisi completa HSE
"""
import requests
import json
import time

# Configurazione
BASE_URL = "http://localhost:8000"
TENANT_ID = 1

def test_permit_analysis():
    """Test dell'analisi di un permesso con il nuovo sistema"""
    
    # Dati di test - permesso per sostituzione tubazione
    test_permit = {
        "title": "Sostituzione tubazione vapore alta pressione",
        "description": "Rimozione e sostituzione tubazione vapore 6 bar nel reparto produzione. Necessario taglio della tubazione esistente e saldatura della nuova linea.",
        "work_type": "meccanico",
        "location": "Reparto produzione - linea vapore principale",
        "risk_level": "high",
        "risk_mitigation_actions": ["Isolamento linea", "Supervisione"],
        "orchestrator": "fast"  # Usa il modular orchestrator aggiornato
    }
    
    print("TEST del nuovo sistema di analisi HSE")
    print("=" * 50)
    print(f"Permesso di test: {test_permit['title']}")
    print(f"Tipo lavoro: {test_permit['work_type']}")
    print(f"Azioni esistenti: {test_permit['risk_mitigation_actions']}")
    print(f"Orchestrator: {test_permit['orchestrator']}")
    print()
    
    # Usa l'endpoint di preview che non richiede un permesso salvato
    print("Avvio analisi HSE completa con preview...")
    start_time = time.time()
    
    analyze_response = requests.post(
        f"{BASE_URL}/api/v1/test/permits/analyze-preview",
        headers={"X-Tenant-ID": str(TENANT_ID)},
        json=test_permit
    )
    
    analysis_time = time.time() - start_time
    
    if analyze_response.status_code != 200:
        print("ERRORE nell'analisi")
        print(f"Status: {analyze_response.status_code}")
        print(f"Response: {analyze_response.text}")
        return
    
    analysis = analyze_response.json()
    print(f"SUCCESSO: Analisi completata in {analysis_time:.2f} secondi")
    
    # Verifica i risultati del nuovo sistema
    print("\nRISULTATI DELL'ANALISI COMPLETA")
    print("=" * 50)
    
    # Executive summary
    exec_summary = analysis.get("executive_summary", {})
    print(f"Overall Score: {exec_summary.get('overall_score', 'N/A')}")
    print(f"Critical Issues: {exec_summary.get('critical_issues', 0)}")
    print(f"Recommendations: {exec_summary.get('recommendations', 0)}")
    print(f"Improvement Opportunities: {exec_summary.get('improvement_opportunities', 0)}")
    print(f"Compliance Level: {exec_summary.get('compliance_level', 'N/A')}")
    
    # Agents involved
    agents_involved = analysis.get("agents_involved", [])
    print(f"\nAgenti coinvolti ({len(agents_involved)}): {', '.join(agents_involved)}")
    
    # Action items
    action_items = analysis.get("action_items", [])
    print(f"\nACTION ITEMS ({len(action_items)}):")
    for i, item in enumerate(action_items[:5], 1):  # Primi 5
        print(f"  {i}. [{item.get('priority', 'N/A')}] {item.get('title', 'N/A')}")
        print(f"     Source: {item.get('source', 'N/A')}")
    
    # Measures evaluation
    measures_eval = analysis.get("measures_evaluation", {})
    print(f"\nVALUTAZIONE MISURE ESISTENTI:")
    print(f"  DPI adequacy: {measures_eval.get('dpi_adequacy', 'N/A')}")
    print(f"  Actions adequacy: {measures_eval.get('actions_adequacy', 'N/A')}")
    print(f"  Additional DPI suggested: {len(measures_eval.get('suggested_additional_dpi', []))}")
    print(f"  Additional actions suggested: {len(measures_eval.get('suggested_additional_actions', []))}")
    
    # Document compliance
    doc_compliance = analysis.get("document_compliance", {})
    print(f"\nCONFORMITA' DOCUMENTI:")
    print(f"  Documents analyzed: {doc_compliance.get('documents_analyzed', False)}")
    print(f"  Documents count: {doc_compliance.get('documents_count', 0)}")
    print(f"  Citations generated: {doc_compliance.get('citations_generated', 0)}")
    
    # Risk analysis
    risk_analysis = analysis.get("risk_analysis", {})
    print(f"\nANALISI RISCHI:")
    print(f"  Total risks identified: {risk_analysis.get('total_risks_identified', 0)}")
    risks_by_source = risk_analysis.get('risks_by_source', {})
    for source, count in risks_by_source.items():
        print(f"    {source}: {count} rischi")
    
    # Performance metrics
    performance = analysis.get("performance_metrics", {})
    print(f"\nPERFORMANCE:")
    print(f"  Processing time: {performance.get('total_processing_time', 'N/A')} seconds")
    print(f"  Specialists activated: {performance.get('specialists_activated', 0)}")
    print(f"  Analysis phases completed: {performance.get('analysis_phases_completed', 0)}")
    print(f"  Analysis method: {performance.get('analysis_method', 'N/A')}")
    
    # Verifica che ci siano sempre suggerimenti di miglioramento
    improvement_count = measures_eval.get('improvement_recommendations', 0)
    if improvement_count > 0:
        print(f"\nSISTEMA FUNZIONA CORRETTAMENTE: {improvement_count} miglioramenti suggeriti")
    else:
        print(f"\nATTENZIONE: Nessun miglioramento suggerito - possibile problema")
    
    print(f"\nTest completato. Analisi {analysis.get('analysis_id', 'N/A')}")
    
    return analysis

if __name__ == "__main__":
    try:
        result = test_permit_analysis()
        print("\n" + "="*50)
        print("TEST COMPLETATO SUCCESSFULLY!")
    except Exception as e:
        print(f"\nERRORE NEL TEST: {e}")
        import traceback
        traceback.print_exc()
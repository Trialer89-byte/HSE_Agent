"""
Test script to verify if agents actually use Weaviate and PostgreSQL
"""
import asyncio
import json
from datetime import datetime

async def test_agent_database_access():
    """Test if agents use both Weaviate and PostgreSQL during analysis"""
    
    print("=" * 80)
    print("TEST: Verifica accesso agenti a Weaviate e PostgreSQL")
    print("=" * 80)
    
    # Simulate a welding permit that should trigger searches
    test_permit = {
        "id": 999,
        "work_type": "meccanico",  # Must be from allowed list
        "work_description": "Saldatura tubazioni in acciaio inox",
        "location": "Area produzione - Reparto chimico",
        "duration": "8 ore",
        "workers": 2,
        "company": "Test Company SpA",
        "description": "Saldatura TIG su tubazioni contenenti sostanze chimiche pericolose. Lavoro in altezza su ponteggio a 4 metri.",
        "risk_level": "ALTO",
        "equipment": ["Saldatrice TIG", "Bombole gas argon", "Flex per taglio"],
        "existing_controls": ["Estintore presente", "Ventilazione naturale"],
        "chemical_substances": ["Argon", "Residui acidi", "Vapori metallici"],
        "special_requirements": ["Hot work permit", "Patentino saldatore", "Formazione lavori in altezza"]
    }
    
    # Test with authentication
    test_user = {
        "username": "test_admin",
        "tenant_id": 1,
        "role": "safety_manager"
    }
    
    import httpx
    
    # Login first to get token
    print("\n1. Login per ottenere token...")
    async with httpx.AsyncClient() as client:
        login_response = await client.post(
            "http://localhost:8000/api/v1/auth/login",
            json={"username": "admin_demo_company", "password": "admin123"}
        )
        
        if login_response.status_code != 200:
            print(f"   [X] Login fallito: {login_response.status_code}")
            print(f"   Response: {login_response.text}")
            return
        
        token_data = login_response.json()
        token = token_data["access_token"]
        print(f"   [OK] Token ottenuto")
        
        # Analyze permit with detailed logging
        print("\n2. Invio richiesta analisi permesso...")
        print(f"   Tipo lavoro: {test_permit['work_type']} - {test_permit['work_description']}")
        print(f"   Rischi: Saldatura, Lavoro in altezza, Sostanze chimiche")
        
        headers = {"Authorization": f"Bearer {token}"}
        
        # Correct format for the API - use modular orchestrator for real agents
        analysis_request = {
            "title": test_permit["work_description"],
            "description": test_permit["description"],
            "work_type": test_permit["work_type"],
            "location": test_permit.get("location", ""),
            "equipment": test_permit.get("equipment", []),
            "workers": test_permit.get("workers", 1),
            "duration": test_permit.get("duration", "8 ore"),
            "orchestrator": "modular"  # Use real modular orchestrator instead of mock
        }
        
        analysis_response = await client.post(
            "http://localhost:8000/api/v1/permits/analyze-preview",
            json=analysis_request,
            headers=headers,
            timeout=120.0  # 2 minutes timeout
        )
        
        if analysis_response.status_code != 200:
            print(f"   [X] Analisi fallita: {analysis_response.status_code}")
            print(f"   Response: {analysis_response.text}")
            return
        
        result = analysis_response.json()
        print(f"   [OK] Analisi completata in {result.get('processing_time', 'N/A')} secondi")
        
        # Check what sources were used
        print("\n3. Verifica sorgenti dati utilizzate:")
        print("-" * 40)
        
        # Check citations for evidence of database access
        citations = result.get("citations", {})
        normative_refs = citations.get("normative_framework", [])
        company_procedures = citations.get("company_procedures", [])
        
        # Analyze citations to determine source
        weaviate_evidence = []
        postgres_evidence = []
        api_evidence = []
        
        for ref in normative_refs + company_procedures:
            doc_info = ref.get("document_info", {})
            title = doc_info.get("title", "")
            
            # Check source indicators
            if "[FONTE: Documento Aziendale]" in title:
                weaviate_evidence.append(title)
            elif "[FONTE: Database]" in title:
                postgres_evidence.append(title)
            elif "[FONTE:" in title:
                # Other explicit sources
                if "Specialist Knowledge" in title or "Sistema" in title:
                    api_evidence.append(title)
            else:
                # Implicit API knowledge
                api_evidence.append(title)
        
        # Check action items for references
        action_items = result.get("action_items", [])
        for item in action_items:
            refs = item.get("references", [])
            if refs and any("Procedura" in str(r) for r in refs):
                postgres_evidence.append(f"Action {item['id']}: {refs}")
        
        # Report findings
        print("\nRISULTATI ANALISI SORGENTI:")
        print("=" * 60)
        
        print(f"\n* WEAVIATE (Vector Search):")
        if weaviate_evidence:
            print(f"   [OK] UTILIZZATO - {len(weaviate_evidence)} documenti trovati")
            for doc in weaviate_evidence[:3]:
                print(f"     - {doc}")
        else:
            print("   [X] NON UTILIZZATO - Nessun documento da ricerca vettoriale")
        
        print(f"\n* POSTGRESQL (Metadata):")
        if postgres_evidence:
            print(f"   [OK] UTILIZZATO - {len(postgres_evidence)} riferimenti trovati")
            for ref in postgres_evidence[:3]:
                print(f"     - {ref}")
        else:
            print("   [X] NON UTILIZZATO - Nessun metadata da database relazionale")
        
        print(f"\n* GEMINI API (Knowledge Base):")
        if api_evidence:
            print(f"   [OK] UTILIZZATO - {len(api_evidence)} normative da conoscenza generale")
            for ref in api_evidence[:3]:
                print(f"     - {ref}")
        else:
            print("   [X] NON UTILIZZATO")
        
        # Check if agents were involved
        print(f"\n* AGENTI ATTIVATI:")
        agents = result.get("agents_involved", [])
        if agents:
            for agent in agents:
                print(f"     - {agent}")
        else:
            print("     Nessun agente specifico registrato")
        
        # Performance metrics
        print(f"\n* METRICHE PERFORMANCE:")
        perf = result.get("performance_metrics", {})
        print(f"   - Tempo totale: {perf.get('total_processing_time', 'N/A')}s")
        print(f"   - Specialisti attivati: {perf.get('specialists_activated', 'N/A')}")
        print(f"   - Metodo analisi: {perf.get('analysis_method', 'N/A')}")
        
        # Save full result for inspection
        with open("test_agent_db_access_result.json", "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n[OK] Risultato completo salvato in test_agent_db_access_result.json")
        
        # Final verdict
        print("\n" + "=" * 60)
        print("VERDETTO FINALE:")
        if weaviate_evidence or postgres_evidence:
            print("[OK] Gli agenti UTILIZZANO i database esterni per le citazioni")
            if weaviate_evidence and not postgres_evidence:
                print("   -> Solo Weaviate (ricerca vettoriale)")
            elif postgres_evidence and not weaviate_evidence:
                print("   -> Solo PostgreSQL (metadata)")
            else:
                print("   -> Sia Weaviate che PostgreSQL")
        else:
            print("[!] Gli agenti NON sembrano utilizzare database esterni")
            print("   -> Utilizzano solo conoscenza del modello Gemini")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_agent_database_access())
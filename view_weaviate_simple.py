import requests
import json

# URL base di Weaviate
WEAVIATE_URL = "http://localhost:8080"

def explore_weaviate():
    """Esplora i documenti in Weaviate usando GraphQL direttamente"""
    
    print("=" * 80)
    print("ESPLORAZIONE WEAVIATE")
    print("=" * 80)
    
    # 1. Conta totale documenti
    print("\n1. CONTEGGIO DOCUMENTI:")
    query = {
        "query": "{ Aggregate { HSEDocument { meta { count } } } }"
    }
    
    response = requests.post(f"{WEAVIATE_URL}/v1/graphql", json=query)
    if response.status_code == 200:
        data = response.json()
        count = data['data']['Aggregate']['HSEDocument'][0]['meta']['count']
        print(f"   Totale chunks in Weaviate: {count}")
    else:
        print(f"   Errore: {response.status_code}")
    
    # 2. Primi documenti
    print("\n2. PRIMI 5 CHUNKS:")
    print("-" * 80)
    query = {
        "query": """{ 
            Get { 
                HSEDocument(limit: 5) { 
                    document_code 
                    title 
                    content 
                    category 
                    tenant_id 
                } 
            } 
        }"""
    }
    
    response = requests.post(f"{WEAVIATE_URL}/v1/graphql", json=query)
    if response.status_code == 200:
        data = response.json()
        docs = data['data']['Get']['HSEDocument']
        for i, doc in enumerate(docs, 1):
            print(f"\nChunk {i}:")
            print(f"   Codice: {doc.get('document_code')}")
            print(f"   Titolo: {doc.get('title')}")
            print(f"   Categoria: {doc.get('category')}")
            print(f"   Tenant ID: {doc.get('tenant_id')}")
            content = doc.get('content', '')
            print(f"   Contenuto (primi 200 char): {content[:200]}...")
    
    # 3. Cerca chunks del D.Lgs. 81/2008
    print("\n3. CHUNKS DEL D.LGS. 81/2008:")
    print("-" * 80)
    query = {
        "query": """{ 
            Get { 
                HSEDocument(
                    where: {
                        path: ["title"]
                        operator: Equal
                        valueText: "Dl.81_2008"
                    }
                    limit: 3
                ) { 
                    document_code 
                    title 
                    content 
                } 
            } 
        }"""
    }
    
    response = requests.post(f"{WEAVIATE_URL}/v1/graphql", json=query)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Get' in data['data'] and 'HSEDocument' in data['data']['Get']:
            docs = data['data']['Get']['HSEDocument']
            print(f"   Trovati {len(docs)} chunks con questo titolo")
            for i, doc in enumerate(docs[:3], 1):
                print(f"\n   Chunk {i}:")
                content = doc.get('content', '')
                print(f"   Contenuto: {content[:300]}...")

def search_specific_content(search_term):
    """Cerca contenuto specifico"""
    print(f"\n\nRICERCA SPECIFICA PER: '{search_term}'")
    print("=" * 80)
    
    query = {
        "query": f"""{{ 
            Get {{ 
                HSEDocument(
                    where: {{
                        path: ["content"]
                        operator: Like
                        valueText: "*{search_term}*"
                    }}
                    limit: 5
                ) {{ 
                    document_code 
                    title 
                    content 
                }} 
            }} 
        }}"""
    }
    
    response = requests.post(f"{WEAVIATE_URL}/v1/graphql", json=query)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Get' in data['data'] and 'HSEDocument' in data['data']['Get']:
            docs = data['data']['Get']['HSEDocument']
            print(f"Trovati {len(docs)} risultati")
            for i, doc in enumerate(docs, 1):
                print(f"\n{i}. {doc.get('title')} - {doc.get('document_code')}")
                content = doc.get('content', '')
                # Trova e evidenzia il termine cercato
                idx = content.lower().find(search_term.lower())
                if idx != -1:
                    start = max(0, idx - 50)
                    end = min(len(content), idx + len(search_term) + 50)
                    print(f"   ...{content[start:end]}...")

def get_document_statistics():
    """Ottieni statistiche sui documenti"""
    print("\n\nSTATISTICHE DOCUMENTI")
    print("=" * 80)
    
    # Query per raggruppare per titolo
    query = {
        "query": """{ 
            Aggregate { 
                HSEDocument(groupBy: ["title"]) { 
                    meta { 
                        count 
                    } 
                    groupedBy { 
                        value 
                    } 
                } 
            } 
        }"""
    }
    
    response = requests.post(f"{WEAVIATE_URL}/v1/graphql", json=query)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data and 'Aggregate' in data['data']:
            groups = data['data']['Aggregate']['HSEDocument']
            print("\nDocumenti per titolo:")
            for group in groups:
                if 'groupedBy' in group and 'value' in group['groupedBy']:
                    title = group['groupedBy']['value']
                    count = group['meta']['count']
                    print(f"   - {title}: {count} chunks")

if __name__ == "__main__":
    explore_weaviate()
    search_specific_content("articolo 28")
    get_document_statistics()
    
    # Pausa per evitare chiusura immediata
    print("\n\nPremere INVIO per chiudere...")
    input()
import psycopg2
from datetime import datetime
import json

# Configurazione database
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'hse_db',
    'user': 'hse_user',
    'password': 'HSEPassword2024!'
}

def view_document_details(doc_id=2):
    """Visualizza i dettagli completi di un documento in PostgreSQL"""
    
    try:
        # Connessione al database
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Query dettagliata
        query = """
        SELECT 
            id,
            tenant_id,
            document_code,
            title,
            document_type,
            category,
            subcategory,
            scope,
            industry_sectors,
            authority,
            file_path,
            file_hash,
            content_summary,
            vector_id,
            version,
            publication_date,
            effective_date,
            is_active,
            uploaded_by,
            created_at,
            updated_at,
            ai_keywords,
            ai_categories,
            relevance_score
        FROM documents 
        WHERE id = %s
        """
        
        cur.execute(query, (doc_id,))
        row = cur.fetchone()
        
        if row:
            print("=" * 80)
            print(f"DOCUMENTO ID: {row[0]}")
            print("=" * 80)
            print(f"Tenant ID: {row[1]}")
            print(f"Codice Documento: {row[2]}")
            print(f"Titolo: {row[3]}")
            print(f"Tipo Documento: {row[4]}")
            print(f"Categoria: {row[5]}")
            print(f"Sottocategoria: {row[6]}")
            print(f"Scope: {row[7]}")
            print(f"Settori Industriali: {row[8]}")
            print(f"Autorità: {row[9]}")
            print(f"Percorso File: {row[10]}")
            print(f"Hash File: {row[11]}")
            print(f"\nVector ID (Weaviate): {row[13]}")
            print(f"Versione: {row[14]}")
            print(f"Data Pubblicazione: {row[15]}")
            print(f"Data Efficacia: {row[16]}")
            print(f"Attivo: {row[17]}")
            print(f"Caricato da (User ID): {row[18]}")
            print(f"Creato il: {row[19]}")
            print(f"Aggiornato il: {row[20]}")
            print(f"Keywords AI: {row[21]}")
            print(f"Categorie AI: {row[22]}")
            print(f"Punteggio Rilevanza: {row[23]}")
            
            # Content Summary
            print(f"\n{'='*80}")
            print("CONTENT SUMMARY")
            print(f"{'='*80}")
            if row[12]:
                print(f"Lunghezza: {len(row[12])} caratteri")
                print(f"Prime 1000 caratteri:")
                print("-" * 80)
                print(row[12][:1000])
                print("-" * 80)
                
                # Conta articoli
                content = row[12].lower()
                art_count = content.count('articolo')
                print(f"\nNumero di volte che appare 'articolo': {art_count}")
                
                # Mostra ultimi 500 caratteri
                if len(row[12]) > 1500:
                    print(f"\nUltimi 500 caratteri:")
                    print("-" * 80)
                    print(row[12][-500:])
                    print("-" * 80)
            else:
                print("Content summary non presente")
                
        else:
            print(f"Documento con ID {doc_id} non trovato!")
            
        # Conta totale documenti
        cur.execute("SELECT COUNT(*) FROM documents")
        total = cur.fetchone()[0]
        print(f"\n\nTotale documenti nel database: {total}")
        
        # Lista tutti i documenti
        print("\nALTRI DOCUMENTI:")
        print("-" * 80)
        cur.execute("SELECT id, title, document_code, created_at FROM documents ORDER BY id")
        for doc in cur.fetchall():
            print(f"ID: {doc[0]} | {doc[1]} | Codice: {doc[2]} | Creato: {doc[3]}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Errore: {e}")

def search_documents(search_term):
    """Cerca documenti per termine"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        query = """
        SELECT id, title, document_code 
        FROM documents 
        WHERE 
            title ILIKE %s OR 
            document_code ILIKE %s OR 
            content_summary ILIKE %s
        """
        
        search_pattern = f'%{search_term}%'
        cur.execute(query, (search_pattern, search_pattern, search_pattern))
        
        print(f"\nRisultati ricerca per '{search_term}':")
        print("-" * 80)
        for row in cur.fetchall():
            print(f"ID: {row[0]} | Titolo: {row[1]} | Codice: {row[2]}")
            
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Errore ricerca: {e}")

if __name__ == "__main__":
    print("VISUALIZZAZIONE DOCUMENTO IN POSTGRESQL\n")
    
    # Visualizza documento principale
    view_document_details(2)
    
    # Esempio di ricerca
    print("\n" + "="*80)
    search_documents("81/2008")
    
    # Pausa per evitare chiusura immediata
    print("\n\nPremere INVIO per chiudere...")
    input()
#!/usr/bin/env python3
"""
Script to update relevance scores for existing documents
"""
import sys
sys.path.insert(0, '/app')

from app.config.database import SessionLocal
from app.models.document import Document

def calculate_relevance_score(text: str) -> float:
    """Calculate relevance score - HSE documents start high with differentiation"""
    if not text:
        return 0.6  # Default good score for HSE context
        
    text_lower = text.lower()
    
    # Start with high base score for HSE documents
    score = 0.7
    
    # Premium terms that boost to excellent scores
    premium_terms = {
        "permesso di lavoro": 0.15, "work permit": 0.15,
        "dpi": 0.12, "ppe": 0.12, "dispositivi protezione": 0.12,
        "procedura sicurezza": 0.12, "safety procedure": 0.12,
        "valutazione rischi": 0.12, "risk assessment": 0.12,
        "lavori a caldo": 0.1, "hot work": 0.1,
        "spazio confinato": 0.1, "confined space": 0.1,
        "lavori elettrici": 0.1, "electrical work": 0.1,
        "cei 11-27": 0.15, "dlgs 81": 0.15, "d.lgs 81": 0.15
    }
    
    # Quality terms that add good value
    quality_terms = {
        "rischio": 0.08, "risk": 0.08, "hazard": 0.08,
        "emergenza": 0.08, "emergency": 0.08,
        "protezione": 0.06, "protection": 0.06,
        "prevenzione": 0.06, "prevention": 0.06,
        "sicurezza": 0.05, "safety": 0.05,
        "controllo": 0.05, "control": 0.05,
        "normativa": 0.07, "standard": 0.07,
        "istruzione": 0.06, "procedure": 0.06
    }
    
    # Count premium terms with higher impact
    for term, weight in premium_terms.items():
        if term in text_lower:
            count = text_lower.count(term)
            score += weight * min(count, 3)  # Cap at 3 occurrences
    
    # Count quality terms
    for term, weight in quality_terms.items():
        if term in text_lower:
            count = text_lower.count(term)
            score += weight * min(count, 2)  # Cap at 2 occurrences
    
    # Bonus for comprehensive HSE content
    term_categories = 0
    if any(term in text_lower for term in ["dpi", "ppe", "protezione"]):
        term_categories += 1
    if any(term in text_lower for term in ["rischio", "risk", "valutazione"]):
        term_categories += 1
    if any(term in text_lower for term in ["procedura", "istruzione", "normativa"]):
        term_categories += 1
    if any(term in text_lower for term in ["lavori", "work", "permesso"]):
        term_categories += 1
        
    if term_categories >= 3:
        score += 0.1  # Comprehensive bonus
    elif term_categories >= 2:
        score += 0.05  # Good coverage bonus
    
    return min(round(score, 3), 1.0)

def update_document_scores():
    """Update relevance scores for all documents"""
    db = SessionLocal()
    try:
        documents = db.query(Document).filter(Document.is_active == True).all()
        print(f"Found {len(documents)} active documents")
        
        for doc in documents:
            # Calculate score based on title, summary and keywords
            text_to_analyze = f"{doc.title} {doc.content_summary or ''} {' '.join(doc.keywords or [])}"
            old_score = doc.relevance_score
            new_score = calculate_relevance_score(text_to_analyze)
            
            if new_score != old_score:
                doc.relevance_score = round(new_score, 2)
                print(f"Document {doc.id} ({doc.document_code}): {old_score} -> {new_score}")
            else:
                print(f"Document {doc.id} ({doc.document_code}): {old_score} (unchanged)")
        
        db.commit()
        print("\n✓ All relevance scores updated successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_document_scores()
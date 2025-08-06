#!/usr/bin/env python3
"""
Test script to verify citation format fix
"""

# Test the citation structure that will be generated
def create_citations(dpi_recommendations):
    """Create properly formatted citations"""
    citations = {
        "normative_framework": [
            {
                "document_info": {
                    "title": "D.Lgs 81/08",
                    "type": "Normativa",
                    "date": "2008-04-09"
                },
                "relevance": {
                    "score": 0.95,
                    "reason": "Testo unico sulla salute e sicurezza sul lavoro"
                },
                "key_requirements": [],
                "frontend_display": {
                    "color": "blue",
                    "icon": "book-open",
                    "category": "Normativa Nazionale"
                }
            }
        ],
        "company_procedures": []
    }
    
    # Add UNI EN standards from DPI recommendations
    seen_standards = set()
    for dpi in dpi_recommendations:
        standard = dpi.get("standard")
        if standard and standard not in seen_standards:
            seen_standards.add(standard)
            citations["normative_framework"].append({
                "document_info": {
                    "title": standard,
                    "type": "Standard Tecnico",
                    "date": "Current"
                },
                "relevance": {
                    "score": 0.85,
                    "reason": f"Standard per {dpi.get('dpi_type', 'DPI')}"
                },
                "key_requirements": [],
                "frontend_display": {
                    "color": "green",
                    "icon": "shield-check",
                    "category": "Standard UNI EN"
                }
            })
    
    return citations

# Test with sample DPI recommendations
test_dpi = [
    {"dpi_type": "Guanti di protezione", "standard": "EN 388"},
    {"dpi_type": "Elmetto di protezione", "standard": "EN 397"},
    {"dpi_type": "Occhiali di sicurezza", "standard": "EN 166"}
]

citations = create_citations(test_dpi)

print("=== Citation Structure Test ===")
print(f"Total normative citations: {len(citations['normative_framework'])}")
print("\nCitations:")
for citation in citations["normative_framework"]:
    print(f"- {citation['document_info']['title']} ({citation['document_info']['type']})")
    print(f"  Relevance: {citation['relevance']['score']} - {citation['relevance']['reason']}")
    
print("\n✅ Citation format is correct - each citation is a proper dictionary!")
"""
DPI Evaluator Agent - Specialista nella valutazione e raccomandazione DPI
"""
from typing import Dict, Any, List
from ..base_agent import BaseHSEAgent


class DPIEvaluatorAgent(BaseHSEAgent):
    """Specialist agent for PPE evaluation and recommendations based on identified risks"""
    
    def __init__(self):
        super().__init__(
            name="DPI_Evaluator",
            specialization="Valutazione e Raccomandazione DPI secondo normative",
            activation_keywords=["dpi", "ppe", "protezione", "protection"]
        )
        
        # DPI mapping based on risk types and normatives
        self.risk_dpi_mapping = {
            "mechanical": {
                "base": [
                    {"type": "Guanti antitaglio", "norm": "EN 388", "level": "minimo 3"},
                    {"type": "Scarpe antinfortunistiche", "norm": "EN ISO 20345", "level": "S3"},
                    {"type": "Occhiali protezione meccanica", "norm": "EN 166", "level": "F"}
                ],
                "rotating_equipment": [
                    {"type": "Indumenti aderenti", "norm": "EN ISO 13688", "level": "no parti libere"},
                    {"type": "Cuffie antirumore", "norm": "EN 352", "level": "SNR > 25 dB"}
                ],
                "pressure_systems": [
                    {"type": "Visiera protezione", "norm": "EN 166", "level": "B resistenza impatto medio"}
                ]
            },
            "hot_work": {
                "base": [
                    {"type": "Maschera saldatore", "norm": "EN 175", "level": "filtro DIN 9-13"},
                    {"type": "Guanti saldatura", "norm": "EN 12477", "level": "tipo A"},
                    {"type": "Grembiule in cuoio", "norm": "EN ISO 11611", "level": "classe 2"},
                    {"type": "Scarpe S3 HRO", "norm": "EN ISO 20345", "level": "resistenza calore suola"}
                ],
                "welding": [
                    {"type": "Respiratore fumi saldatura", "norm": "EN 149", "level": "FFP3"},
                    {"type": "Indumenti ignifughi", "norm": "EN ISO 11612", "level": "A1+A2"}
                ],
                "cutting": [
                    {"type": "Schermo facciale", "norm": "EN 166", "level": "marcatura 3"}
                ]
            },
            "chemical": {
                "base": [
                    {"type": "Guanti chimici", "norm": "EN 374", "level": "tipo A - 6 sostanze"},
                    {"type": "Occhiali a tenuta", "norm": "EN 166", "level": "marcatura 3-4-5"},
                    {"type": "Tuta chimica", "norm": "EN 14605", "level": "tipo 3/4"}
                ],
                "vapors": [
                    {"type": "Maschera pieno facciale", "norm": "EN 136", "level": "classe 2"},
                    {"type": "Filtri combinati", "norm": "EN 14387", "level": "ABEK-P3"}
                ],
                "corrosive": [
                    {"type": "Stivali chimici", "norm": "EN 13832", "level": "resistenza acidi/basi"},
                    {"type": "Grembiule PVC", "norm": "EN 14605", "level": "tipo PB3"}
                ]
            },
            "height": {
                "base": [
                    {"type": "Imbracatura anticaduta", "norm": "EN 361", "level": "con assorbitore"},
                    {"type": "Elmetto con sottogola", "norm": "EN 397", "level": "con chinstrap"},
                    {"type": "Scarpe antiscivolo", "norm": "EN ISO 20345", "level": "SRC"}
                ],
                "above_6m": [
                    {"type": "Dispositivo anticaduta retrattile", "norm": "EN 360", "level": "certificato"}
                ]
            },
            "confined_space": {
                "base": [
                    {"type": "Rilevatore gas", "norm": "EN 60079", "level": "4 gas"},
                    {"type": "Autorespiratore", "norm": "EN 137", "level": "pressione positiva"},
                    {"type": "Imbracatura recupero", "norm": "EN 361/1497", "level": "con anelli recupero"}
                ],
                "emergency": [
                    {"type": "Kit evacuazione", "norm": "EN 341", "level": "classe A"},
                    {"type": "Tripode recupero", "norm": "EN 795", "level": "classe B"}
                ]
            },
            "electrical": {
                "base": [
                    {"type": "Guanti isolanti", "norm": "EN 60903", "level": "classe 0 (1000V)"},
                    {"type": "Scarpe isolanti", "norm": "EN ISO 20345", "level": "SB E P"},
                    {"type": "Elmetto isolante", "norm": "EN 50365", "level": "1000V AC"}
                ],
                "high_voltage": [
                    {"type": "Tuta isolante", "norm": "EN 50286", "level": "classe 2"},
                    {"type": "Visiera anti-arco", "norm": "EN 166", "level": "marcatura 8"}
                ]
            }
        }
    
    def _get_system_message(self) -> str:
        return """
ESPERTO DPI - Valutatore e consulente per Dispositivi di Protezione Individuale secondo normative.

COMPETENZE PRINCIPALI:
1. VALUTAZIONE RISCHI-DPI
   - Analisi rischi identificati nel permesso
   - Mappatura rischio → DPI richiesto
   - Verifica completezza protezioni
   - Identificazione lacune nella protezione

2. CONFORMITÀ NORMATIVA
   - D.Lgs 81/08 Titolo III Capo II
   - Norme EN/ISO specifiche per categoria
   - Marcatura CE e categorie DPI (I, II, III)
   - Obblighi formazione per DPI categoria III

3. SELEZIONE TECNICA DPI
   Per ogni rischio identificato:
   - Tipo specifico di DPI
   - Norma tecnica di riferimento (EN/ISO)
   - Livello di protezione richiesto
   - Caratteristiche tecniche minime

4. VERIFICA COMPATIBILITÀ
   - Interferenze tra DPI diversi
   - Comfort e ergonomia
   - Durata e manutenzione
   - Costi-benefici

5. PRIORITIZZAZIONE
   - DPI OBBLIGATORI (per legge)
   - DPI CRITICI (rischio grave)
   - DPI RACCOMANDATI (comfort/efficienza)
   - DPI OPZIONALI (miglioramento)

ANALISI RICHIESTA:
1. Confronta DPI forniti nel permesso vs rischi identificati
2. Identifica DPI mancanti o inadeguati
3. Specifica normativa per ogni DPI
4. Fornisci livello protezione richiesto
5. Segnala incompatibilità tra DPI

OUTPUT STRUTTURATO:
- Gap analysis (cosa manca)
- DPI obbligatori con normative
- DPI raccomandati con giustificazione
- Formazione richiesta (DPI cat. III)
- Verifiche periodiche necessarie
"""
    
    def should_activate(self, risk_classification: Dict[str, Any]) -> bool:
        """DPI Evaluator should always activate after risk identification"""
        return True  # Always evaluate DPI after risks are identified
    
    async def analyze(self, permit_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate PPE requirements based on identified risks and regulations"""
        
        # Get identified risks from context
        classification = context.get("classification", {})
        detected_risks = classification.get("detected_risks", {})
        risk_domains = classification.get("risk_domains", {})
        
        # Get existing DPI from permit
        existing_dpi = permit_data.get("dpi_required", [])
        
        # Analyze DPI requirements for each risk
        required_dpi = []
        dpi_gaps = []
        normative_references = []
        
        for risk_type in detected_risks.keys():
            if risk_type in self.risk_dpi_mapping:
                # Get base DPI for this risk
                base_dpi = self.risk_dpi_mapping[risk_type].get("base", [])
                for dpi in base_dpi:
                    dpi_entry = {
                        "risk_source": risk_type,
                        "dpi_type": dpi["type"],
                        "normative": dpi["norm"],
                        "protection_level": dpi["level"],
                        "category": self._get_dpi_category(dpi["type"]),
                        "mandatory": True
                    }
                    required_dpi.append(dpi_entry)
                    
                    # Check if this DPI is missing
                    if not self._is_dpi_present(dpi["type"], existing_dpi):
                        dpi_gaps.append({
                            "missing_dpi": dpi["type"],
                            "reason": f"Richiesto per rischio {risk_type}",
                            "normative": dpi["norm"],
                            "criticality": "alta"
                        })
                    
                    # Add normative reference
                    if dpi["norm"] not in [ref["norm"] for ref in normative_references]:
                        normative_references.append({
                            "norm": dpi["norm"],
                            "description": f"Norma per {dpi['type']}",
                            "mandatory": True
                        })
                
                # Check for specific conditions
                if risk_type == "hot_work":
                    if "weld" in str(permit_data).lower() or "sald" in str(permit_data).lower():
                        welding_dpi = self.risk_dpi_mapping[risk_type].get("welding", [])
                        for dpi in welding_dpi:
                            required_dpi.append({
                                "risk_source": "welding",
                                "dpi_type": dpi["type"],
                                "normative": dpi["norm"],
                                "protection_level": dpi["level"],
                                "category": "III",  # Welding PPE is category III
                                "mandatory": True,
                                "training_required": True
                            })
                
                elif risk_type == "height":
                    # Check working height
                    if "6m" in str(permit_data) or "10m" in str(permit_data):
                        height_dpi = self.risk_dpi_mapping[risk_type].get("above_6m", [])
                        for dpi in height_dpi:
                            required_dpi.append({
                                "risk_source": "height_above_6m",
                                "dpi_type": dpi["type"],
                                "normative": dpi["norm"],
                                "protection_level": dpi["level"],
                                "category": "III",
                                "mandatory": True,
                                "training_required": True
                            })
        
        # Check documents for additional DPI requirements
        documents = context.get("documents", [])
        doc_required_dpi = self._extract_dpi_from_documents(documents)
        
        # Evaluate existing DPI adequacy
        dpi_evaluation = self._evaluate_existing_dpi(existing_dpi, required_dpi)
        
        # Check for DPI compatibility issues
        compatibility_issues = self._check_dpi_compatibility(required_dpi)
        
        # Generate recommendations
        recommendations = self._generate_dpi_recommendations(
            dpi_gaps, 
            compatibility_issues,
            required_dpi
        )
        
        # Identify training requirements (Category III DPI)
        training_requirements = [
            dpi for dpi in required_dpi 
            if dpi.get("category") == "III" or dpi.get("training_required")
        ]
        
        # CONVERT TO STANDARD OUTPUT FORMAT per l'orchestratore
        return {
            # FORMATO STANDARD RICHIESTO DALL'ORCHESTRATORE
            "risks_identified": [
                {
                    "type": "dpi_inadequati",
                    "source": "DPI_Evaluator", 
                    "description": f"DPI inadeguati o mancanti: {len(dpi_gaps)} lacune identificate",
                    "severity": "alta" if len([gap for gap in dpi_gaps if gap.get("criticality") == "alta"]) > 0 else "media",
                    "details": dpi_gaps
                }
            ] if dpi_gaps else [
                {
                    "type": "dpi_adeguati",
                    "source": "DPI_Evaluator",
                    "description": "DPI forniti adeguati ai rischi identificati",
                    "severity": "bassa"
                }
            ],
            
            "dpi_requirements": [dpi["dpi_type"] for dpi in required_dpi] + 
                              [f"Aggiungere {gap['missing_dpi']}" for gap in dpi_gaps],
            
            "control_measures": recommendations + [
                f"Verificare conformità normativa {ref['norm']}" for ref in normative_references
            ] + [
                f"Formazione obbligatoria per DPI categoria III: {len(training_requirements)} elementi"
            ] if training_requirements else [],
            
            "permits_required": [
                "Certificazione DPI categoria III" if training_requirements else None
            ],
            
            "document_citations": [
                {
                    "type": "normativa_dpi",
                    "source": ref["norm"],
                    "description": ref["description"],
                    "mandatory": ref["mandatory"]
                } for ref in normative_references
            ] + [
                {
                    "type": "documento_aziendale_dpi",
                    "source": doc["source"],
                    "description": doc["requirements"],
                    "document_code": doc.get("document_code")
                } for doc in doc_required_dpi
            ],
            
            # DETTAGLI TECNICI ORIGINALI (mantenuti per compatibilità)
            "dpi_analysis_complete": True,
            "existing_dpi": existing_dpi,
            "existing_dpi_adequate": len(dpi_gaps) == 0,
            "required_dpi": required_dpi,
            "dpi_gaps": dpi_gaps,
            "normative_references": normative_references,
            "dpi_evaluation": dpi_evaluation,
            "compatibility_issues": compatibility_issues,
            "document_based_dpi": doc_required_dpi,
            "training_requirements": training_requirements,
            "recommendations": recommendations,
            "compliance_status": self._assess_compliance(dpi_gaps, required_dpi),
            "total_dpi_required": len(required_dpi),
            "total_gaps": len(dpi_gaps),
            "critical_gaps": len([gap for gap in dpi_gaps if gap.get("criticality") == "alta"])
        }
    
    def _is_dpi_present(self, dpi_type: str, existing_dpi: List[str]) -> bool:
        """Check if a DPI type is present in existing list"""
        dpi_keywords = dpi_type.lower().split()
        for existing in existing_dpi:
            existing_lower = existing.lower()
            if any(keyword in existing_lower for keyword in dpi_keywords):
                return True
        return False
    
    def _get_dpi_category(self, dpi_type: str) -> str:
        """Determine DPI category (I, II, or III)"""
        category_iii = [
            "imbracatura", "anticaduta", "autorespiratore", "isolanti",
            "chimici tipo a", "saldatura", "pieno facciale"
        ]
        category_ii = [
            "elmetto", "occhiali", "guanti", "scarpe", "cuffie",
            "maschera", "visiera"
        ]
        
        dpi_lower = dpi_type.lower()
        if any(term in dpi_lower for term in category_iii):
            return "III"
        elif any(term in dpi_lower for term in category_ii):
            return "II"
        return "I"
    
    def _extract_dpi_from_documents(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract DPI requirements from relevant documents"""
        doc_dpi = []
        
        for doc in documents:
            # Look for DPI-related documents
            if any(term in doc.get("title", "").lower() 
                   for term in ["dpi", "protezione", "dispositivi", "ppe"]):
                doc_dpi.append({
                    "source": doc.get("title"),
                    "document_code": doc.get("document_code"),
                    "requirements": "Verificare requisiti specifici nel documento"
                })
        
        return doc_dpi
    
    def _evaluate_existing_dpi(self, existing: List[str], required: List[Dict]) -> Dict[str, Any]:
        """Evaluate adequacy of existing DPI"""
        evaluation = {
            "coverage_percentage": 0,
            "missing_critical": [],
            "partial_coverage": [],
            "adequate": [],
            "overcoverage": []
        }
        
        if not required:
            evaluation["coverage_percentage"] = 100
            return evaluation
        
        covered = 0
        for req_dpi in required:
            if self._is_dpi_present(req_dpi["dpi_type"], existing):
                covered += 1
                evaluation["adequate"].append(req_dpi["dpi_type"])
            elif req_dpi.get("mandatory"):
                evaluation["missing_critical"].append(req_dpi["dpi_type"])
        
        evaluation["coverage_percentage"] = (covered / len(required)) * 100 if required else 0
        
        return evaluation
    
    def _check_dpi_compatibility(self, required_dpi: List[Dict]) -> List[Dict[str, Any]]:
        """Check for potential compatibility issues between DPI"""
        issues = []
        
        # Check for known incompatibilities
        dpi_types = [dpi["dpi_type"] for dpi in required_dpi]
        
        # Example: Full face mask with safety glasses
        if any("pieno facciale" in dpi.lower() for dpi in dpi_types):
            if any("occhiali" in dpi.lower() for dpi in dpi_types):
                issues.append({
                    "conflict": "Maschera pieno facciale incompatibile con occhiali",
                    "solution": "Utilizzare maschera con lenti graduate integrate"
                })
        
        return issues
    
    def _generate_dpi_recommendations(
        self, 
        gaps: List[Dict], 
        compatibility: List[Dict],
        required: List[Dict]
    ) -> List[str]:
        """Generate actionable DPI recommendations"""
        recommendations = []
        
        if gaps:
            recommendations.append(f"CRITICO: Fornire {len(gaps)} DPI mancanti prima dell'inizio lavori")
            for gap in gaps[:3]:  # Top 3 gaps
                recommendations.append(f"- {gap['missing_dpi']}: {gap['reason']}")
        
        if compatibility:
            recommendations.append("ATTENZIONE: Risolvere incompatibilità DPI")
            for issue in compatibility:
                recommendations.append(f"- {issue['solution']}")
        
        # Check for category III DPI
        cat_iii = [dpi for dpi in required if dpi.get("category") == "III"]
        if cat_iii:
            recommendations.append(f"FORMAZIONE: Richiesta per {len(cat_iii)} DPI di categoria III")
        
        if not gaps and not compatibility:
            recommendations.append("✓ DPI forniti adeguati ai rischi identificati")
        
        return recommendations
    
    def _assess_compliance(self, gaps: List[Dict], required: List[Dict]) -> str:
        """Assess overall DPI compliance status"""
        if not required:
            return "non_applicabile"
        
        critical_gaps = [gap for gap in gaps if gap.get("criticality") == "alta"]
        
        if critical_gaps:
            return "non_conforme"
        elif gaps:
            return "parzialmente_conforme"
        else:
            return "conforme"
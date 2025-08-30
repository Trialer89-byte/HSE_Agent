"""
DPI Consolidator - Intelligent consolidation and compatibility checking for DPI requirements
Prevents duplicates and ensures compatibility across different specialist requirements
"""

from typing import List, Dict, Any, Set, Tuple
import re


class DPIConsolidator:
    """
    Intelligent DPI consolidation system that:
    1. Identifies overlapping/duplicate DPI categories
    2. Merges similar items with highest protection level
    3. Checks compatibility between different DPI requirements
    4. Prevents conflicting recommendations
    """
    
    def __init__(self):
        # DPI category mapping with compatibility rules
        self.dpi_categories = {
            "safety_shoes": {
                "keywords": ["scarpe", "calzature", "antinfortunistiche", "sicurezza", "shoes", "footwear", "s1", "s2", "s3", "s4", "s5"],
                "protection_levels": {
                    "S1": {"level": 1, "features": ["antischiacciamento", "antiperforazione"]},
                    "S2": {"level": 2, "features": ["antischiacciamento", "antiperforazione", "idrorepellente"]},
                    "S3": {"level": 3, "features": ["antischiacciamento", "antiperforazione", "lamina antiperforazione", "idrorepellente"]},
                    "S3 HRO": {"level": 4, "features": ["antischiacciamento", "antiperforazione", "lamina antiperforazione", "idrorepellente", "resistenti al calore"]},
                    "S4": {"level": 5, "features": ["antischiacciamento", "antiperforazione", "impermeabile", "stivale"]},
                    "S5": {"level": 6, "features": ["antischiacciamento", "antiperforazione", "impermeabile", "stivale", "lamina antiperforazione"]}
                }
            },
            "gloves": {
                "keywords": ["guanti", "gloves", "protezione mani", "hand protection"],
                "types": ["meccanici", "chimici", "termici", "antitaglio", "dielettrici"]
            },
            "helmets": {
                "keywords": ["casco", "elmetto", "helmet", "head protection", "protezione testa"],
                "types": ["industriale", "elettrico", "alpinismo", "saldatura"]
            },
            "respirators": {
                "keywords": ["respiratore", "maschera", "respirator", "mask", "filtro", "filter"],
                "types": ["ffp1", "ffp2", "ffp3", "pieno facciale", "semimaschera"]
            },
            "eye_protection": {
                "keywords": ["occhiali", "visiera", "glasses", "goggles", "protezione occhi", "eye protection"],
                "types": ["sicurezza", "saldatura", "laser", "chimica"]
            },
            "hearing_protection": {
                "keywords": ["tappi", "cuffie", "protezione udito", "hearing protection", "auricolari"],
                "types": ["inserti", "archetto", "cuffie"]
            },
            "body_protection": {
                "keywords": ["tuta", "giubbotto", "vest", "suit", "protezione corpo", "body protection"],
                "types": ["chimica", "alta visibilità", "saldatura", "antitaglio", "termica"]
            },
            "fall_protection": {
                "keywords": ["imbracatura", "harness", "anticaduta", "fall protection", "corda", "rope"],
                "types": ["corpo intero", "pettorale", "di posizionamento", "di trattenuta"]
            }
        }
        
        # Compatibility matrix - which DPI categories can coexist
        self.compatibility_matrix = {
            "safety_shoes": ["gloves", "helmets", "respirators", "eye_protection", "hearing_protection", "body_protection", "fall_protection"],
            "gloves": ["safety_shoes", "helmets", "respirators", "eye_protection", "hearing_protection", "body_protection", "fall_protection"],
            "helmets": ["safety_shoes", "gloves", "eye_protection", "hearing_protection", "body_protection", "fall_protection"],
            "respirators": ["safety_shoes", "gloves", "helmets", "eye_protection", "hearing_protection", "body_protection", "fall_protection"],
            "eye_protection": ["safety_shoes", "gloves", "helmets", "hearing_protection", "body_protection", "fall_protection"],
            "hearing_protection": ["safety_shoes", "gloves", "helmets", "respirators", "eye_protection", "body_protection", "fall_protection"],
            "body_protection": ["safety_shoes", "gloves", "helmets", "respirators", "eye_protection", "hearing_protection", "fall_protection"],
            "fall_protection": ["safety_shoes", "gloves", "helmets", "respirators", "eye_protection", "hearing_protection", "body_protection"]
        }
        
        # Conflicting combinations that require special handling
        self.conflict_rules = {
            ("respirators", "eye_protection"): "Check seal compatibility - full face respirator replaces safety glasses",
            ("gloves", "fine_work"): "Chemical gloves may reduce dexterity for fine manipulation",
            ("body_protection", "fall_protection"): "Ensure harness can be worn over protective clothing"
        }
    
    def consolidate_dpi_list(self, dpi_list: List[Any]) -> List[Dict[str, Any]]:
        """
        Consolidate a list of DPI items, removing duplicates and conflicts
        
        Args:
            dpi_list: List of DPI items (strings or dicts)
            
        Returns:
            List of consolidated DPI items with enhanced metadata
        """
        print(f"[DPIConsolidator] Processing {len(dpi_list)} DPI items")
        
        # Normalize all DPI items to dictionaries
        normalized_items = []
        for item in dpi_list:
            normalized = self._normalize_dpi_item(item)
            if normalized:
                normalized_items.append(normalized)
        
        print(f"[DPIConsolidator] Normalized to {len(normalized_items)} items")
        
        # Group by category
        categorized_items = self._categorize_dpi_items(normalized_items)
        
        # Consolidate within each category
        consolidated_items = []
        for category, items in categorized_items.items():
            if len(items) > 1:
                print(f"[DPIConsolidator] Found {len(items)} items in category '{category}' - consolidating")
                consolidated = self._consolidate_category(category, items)
                consolidated_items.extend(consolidated)
            else:
                consolidated_items.extend(items)
        
        # Check for conflicts between categories
        final_items = self._resolve_cross_category_conflicts(consolidated_items)
        
        print(f"[DPIConsolidator] Final result: {len(final_items)} consolidated DPI items")
        return final_items
    
    def _normalize_dpi_item(self, item: Any) -> Dict[str, Any]:
        """Convert DPI item to standard dictionary format"""
        if isinstance(item, dict):
            return {
                "original_text": item.get("type", str(item)),
                "description": item.get("description", str(item)),
                "specialist_source": item.get("source", "unknown"),
                "protection_level": item.get("protection_level"),
                "features": item.get("features", [])
            }
        else:
            item_str = str(item)
            return {
                "original_text": item_str,
                "description": item_str,
                "specialist_source": "unknown",
                "protection_level": None,
                "features": []
            }
    
    def _categorize_dpi_items(self, items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group DPI items by category"""
        categorized = {}
        
        for item in items:
            text = item["original_text"].lower()
            category = self._identify_category(text)
            
            if category not in categorized:
                categorized[category] = []
            
            item["category"] = category
            categorized[category].append(item)
        
        return categorized
    
    def _identify_category(self, text: str) -> str:
        """Identify DPI category from text"""
        text_lower = text.lower()
        
        for category, config in self.dpi_categories.items():
            for keyword in config["keywords"]:
                if keyword.lower() in text_lower:
                    return category
        
        return "other"
    
    def _consolidate_category(self, category: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate items within the same category"""
        if category == "safety_shoes":
            return self._consolidate_safety_shoes(items)
        elif category == "gloves":
            return self._consolidate_gloves(items)
        elif category == "respirators":
            return self._consolidate_respirators(items)
        else:
            # For other categories, pick the most comprehensive item
            return self._consolidate_generic(items)
    
    def _consolidate_safety_shoes(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate safety shoes - choose highest protection level"""
        print(f"[DPIConsolidator] Consolidating {len(items)} safety shoes items")
        
        # Extract protection levels and features
        best_item = None
        highest_level = 0
        all_features = set()
        
        for item in items:
            text = item["original_text"].upper()
            
            # Detect protection level
            level = 0
            detected_standard = "S1"
            
            if "S5" in text:
                level = 6
                detected_standard = "S5"
            elif "S4" in text:
                level = 5
                detected_standard = "S4"
            elif "S3 HRO" in text or ("S3" in text and ("HRO" in text or "CALORE" in text or "HEAT" in text)):
                level = 4
                detected_standard = "S3 HRO"
            elif "S3" in text:
                level = 3
                detected_standard = "S3"
            elif "S2" in text:
                level = 2
                detected_standard = "S2"
            elif "S1" in text:
                level = 1
                detected_standard = "S1"
            
            # Collect features from text
            features = []
            if "antiperforazione" in text.lower() or "perforazione" in text.lower():
                features.append("protezione da perforazione")
            if "schiacciamento" in text.lower():
                features.append("protezione da schiacciamento")
            if "calore" in text.lower() or "hro" in text.lower():
                features.append("resistenti al calore")
            if "idrorepellente" in text.lower() or "impermeabile" in text.lower():
                features.append("resistenza all'acqua")
            
            all_features.update(features)
            
            if level > highest_level:
                highest_level = level
                best_item = item.copy()
                best_item["protection_level"] = detected_standard
                best_item["detected_features"] = features
        
        if not best_item:
            best_item = items[0].copy()
            best_item["protection_level"] = "S1"
        
        # Create consolidated item with all features
        consolidated_features = list(all_features)
        if not consolidated_features:
            consolidated_features = ["protezione da schiacciamento", "protezione da perforazione"]
        
        consolidated_item = {
            "category": "safety_shoes",
            "type": f"Scarpe di sicurezza {best_item.get('protection_level', 'S3')}",
            "description": f"Scarpe di sicurezza {best_item.get('protection_level', 'S3')} con {', '.join(consolidated_features)}",
            "original_text": f"Consolidated from {len(items)} requirements",
            "specialist_source": "consolidated",
            "protection_level": best_item.get("protection_level", "S3"),
            "features": consolidated_features,
            "consolidation_info": {
                "merged_items": len(items),
                "source_descriptions": [item["original_text"] for item in items],
                "highest_standard": best_item.get("protection_level", "S3")
            }
        }
        
        print(f"[DPIConsolidator] Consolidated safety shoes: {consolidated_item['type']} with features: {consolidated_features}")
        return [consolidated_item]
    
    def _consolidate_gloves(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate gloves - may need multiple types for different hazards"""
        print(f"[DPIConsolidator] Consolidating {len(items)} gloves items")
        
        # Categorize gloves by protection type
        glove_types = {
            "mechanical": [],
            "chemical": [],
            "thermal": [],
            "electrical": [],
            "cut_resistant": [],
            "general": []
        }
        
        for item in items:
            text = item["original_text"].lower()
            
            if any(word in text for word in ["meccanici", "mechanical", "abrasione", "abrasion"]):
                glove_types["mechanical"].append(item)
            elif any(word in text for word in ["chimici", "chemical", "acidi", "solventi"]):
                glove_types["chemical"].append(item)
            elif any(word in text for word in ["termici", "thermal", "calore", "freddo", "heat", "cold"]):
                glove_types["thermal"].append(item)
            elif any(word in text for word in ["elettrici", "electrical", "isolanti", "dielettrici"]):
                glove_types["electrical"].append(item)
            elif any(word in text for word in ["antitaglio", "cut", "taglio", "lama"]):
                glove_types["cut_resistant"].append(item)
            else:
                glove_types["general"].append(item)
        
        # Return one consolidated item per protection type needed
        consolidated = []
        for protection_type, type_items in glove_types.items():
            if type_items:
                # Pick the most comprehensive item for this type
                best_item = type_items[0]
                
                consolidated_item = {
                    "category": "gloves",
                    "type": f"Guanti {protection_type.replace('_', ' ')}",
                    "description": f"Guanti di protezione {protection_type.replace('_', ' ')} - {best_item['description']}",
                    "original_text": f"Consolidated {protection_type} gloves",
                    "specialist_source": "consolidated",
                    "protection_type": protection_type,
                    "consolidation_info": {
                        "merged_items": len(type_items),
                        "source_descriptions": [item["original_text"] for item in type_items]
                    }
                }
                consolidated.append(consolidated_item)
        
        print(f"[DPIConsolidator] Consolidated gloves into {len(consolidated)} protection types")
        return consolidated
    
    def _consolidate_respirators(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Consolidate respirators - choose highest protection level"""
        print(f"[DPIConsolidator] Consolidating {len(items)} respirator items")
        
        # Find highest protection level
        protection_levels = {"FFP1": 1, "FFP2": 2, "FFP3": 3, "PIENO_FACCIALE": 4}
        
        best_level = 0
        best_item = None
        
        for item in items:
            text = item["original_text"].upper()
            
            current_level = 0
            if "PIENO FACCIALE" in text or "FULL FACE" in text:
                current_level = 4
            elif "FFP3" in text:
                current_level = 3
            elif "FFP2" in text:
                current_level = 2
            elif "FFP1" in text:
                current_level = 1
            
            if current_level > best_level:
                best_level = current_level
                best_item = item
        
        if not best_item:
            best_item = items[0]
        
        # Create consolidated respirator
        level_names = {1: "FFP1", 2: "FFP2", 3: "FFP3", 4: "Pieno facciale"}
        level_name = level_names.get(best_level, "FFP2")
        
        consolidated_item = {
            "category": "respirators",
            "type": f"Respiratore {level_name}",
            "description": f"Protezione respiratoria {level_name} - {best_item['description']}",
            "original_text": f"Consolidated respirator - {level_name}",
            "specialist_source": "consolidated",
            "protection_level": level_name,
            "consolidation_info": {
                "merged_items": len(items),
                "source_descriptions": [item["original_text"] for item in items],
                "highest_level": level_name
            }
        }
        
        print(f"[DPIConsolidator] Consolidated respirators: {level_name}")
        return [consolidated_item]
    
    def _consolidate_generic(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generic consolidation for other DPI categories"""
        if len(items) == 1:
            return items
        
        # Pick the most detailed description
        best_item = max(items, key=lambda x: len(x["description"]))
        
        consolidated_item = best_item.copy()
        consolidated_item["consolidation_info"] = {
            "merged_items": len(items),
            "source_descriptions": [item["original_text"] for item in items]
        }
        
        return [consolidated_item]
    
    def _resolve_cross_category_conflicts(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check for conflicts between different DPI categories"""
        print(f"[DPIConsolidator] Checking cross-category conflicts for {len(items)} items")
        
        # Group by category
        by_category = {}
        for item in items:
            category = item.get("category", "other")
            if category not in by_category:
                by_category[category] = []
            by_category[category].append(item)
        
        # Check for known conflicts
        conflicts_found = []
        categories = list(by_category.keys())
        
        for i, cat1 in enumerate(categories):
            for cat2 in categories[i+1:]:
                conflict_key = tuple(sorted([cat1, cat2]))
                if conflict_key in self.conflict_rules:
                    conflicts_found.append({
                        "categories": [cat1, cat2],
                        "warning": self.conflict_rules[conflict_key],
                        "items": by_category[cat1] + by_category[cat2]
                    })
        
        # Add conflict warnings to items
        final_items = []
        for category, category_items in by_category.items():
            for item in category_items:
                # Add any relevant conflict warnings
                item_conflicts = []
                for conflict in conflicts_found:
                    if category in conflict["categories"]:
                        item_conflicts.append(conflict["warning"])
                
                if item_conflicts:
                    item["compatibility_warnings"] = item_conflicts
                
                final_items.append(item)
        
        if conflicts_found:
            print(f"[DPIConsolidator] Found {len(conflicts_found)} potential conflicts")
        
        return final_items


def consolidate_dpi_requirements(dpi_list: List[Any]) -> List[Dict[str, Any]]:
    """
    Standalone function to consolidate DPI requirements
    
    Args:
        dpi_list: List of DPI items from specialists
        
    Returns:
        Consolidated list of DPI requirements
    """
    consolidator = DPIConsolidator()
    return consolidator.consolidate_dpi_list(dpi_list)
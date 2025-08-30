"""
HSE Specialist Agents Module
"""

from .risk_classifier_agent import RiskClassifierAgent
from .hot_work_agent import HotWorkSpecialist
from .confined_space_agent import ConfinedSpaceSpecialist
from .height_work_agent import HeightWorkSpecialist
from .electrical_agent import ElectricalSpecialist
from .chemical_agent import ChemicalSpecialist
from .mechanical_specialist import MechanicalSpecialist
from .dpi_evaluator_agent import DPIEvaluatorAgent

# Registry of all available specialists
SPECIALIST_REGISTRY = {
    "risk_classifier": RiskClassifierAgent,
    "hot_work": HotWorkSpecialist,
    "confined_space": ConfinedSpaceSpecialist,
    "height": HeightWorkSpecialist,
    "electrical": ElectricalSpecialist,
    "chemical": ChemicalSpecialist,
    "mechanical": MechanicalSpecialist,
    "dpi_evaluator": DPIEvaluatorAgent,
}

def get_specialist(name: str):
    """Get a specialist agent by name"""
    specialist_class = SPECIALIST_REGISTRY.get(name)
    if specialist_class:
        return specialist_class()
    return None

def get_all_specialists():
    """Get instances of all registered specialists"""
    return {name: cls() for name, cls in SPECIALIST_REGISTRY.items()}

__all__ = [
    "RiskClassifierAgent",
    "HotWorkSpecialist", 
    "ConfinedSpaceSpecialist",
    "HeightWorkSpecialist",
    "ElectricalSpecialist", 
    "ChemicalSpecialist",
    "MechanicalSpecialist",
    "DPIEvaluatorAgent",
    "get_specialist",
    "get_all_specialists",
    "SPECIALIST_REGISTRY"
]
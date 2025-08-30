"""
REDIRECT TO ENHANCED AUTOGEN SYSTEM
The old SimpleAutoGenHSEAgents is now replaced by EnhancedAutoGenHSEAgents with 5-phase mandatory analysis
"""

from .enhanced_autogen_agents import EnhancedAutoGenHSEAgents

# Legacy compatibility - redirect all calls to Enhanced version
class SimpleAutoGenHSEAgents(EnhancedAutoGenHSEAgents):
    """
    Legacy compatibility wrapper for Enhanced AutoGen system
    Now provides MANDATORY 5-phase comprehensive analysis with no fallback
    """
    pass
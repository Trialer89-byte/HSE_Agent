#!/usr/bin/env python3
"""
Test script to verify JSON parsing fix for AI agent analysis
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

import asyncio
from app.agents.simple_autogen_agents import SimpleAutoGenHSEAgents

async def test_json_parsing():
    """Test the improved JSON parsing with the welding example"""
    
    # Initialize the agents
    agents = SimpleAutoGenHSEAgents()
    
    # Test permit data with welding typo (the original issue)
    test_permit = {
        "id": "test_001",
        "title": "welsing tank repair",  # Intentional typo: welsing instead of welding
        "description": "Need to fix the tank with metal repair tools and cutting equipment",
        "work_type": "maintenance", 
        "location": "Tank area section B",
        "duration_hours": 4,
        "workers_count": 2,
        "equipment": "metal repair tools, cutting equipment, portable grinder"
    }
    
    print("="*60)
    print("TESTING JSON PARSING FIX")
    print("="*60)
    print(f"Test permit: {test_permit['title']}")
    print(f"Description: {test_permit['description']}")
    print("="*60)
    
    # Run the analysis
    print("Starting AI analysis...")
    result = await agents.analyze_permit(test_permit, [])
    
    print("\nANALYSIS RESULT:")
    print(f"Analysis complete: {result.get('analysis_complete', False)}")
    print(f"Confidence score: {result.get('confidence_score', 0)}")
    print(f"Agents involved: {result.get('agents_involved', [])}")
    
    if result.get('error'):
        print(f"ERROR: {result['error']}")
        return
    
    # Check if risks were identified
    final_analysis = result.get('final_analysis', {})
    executive_summary = final_analysis.get('executive_summary', {})
    action_items = final_analysis.get('action_items', [])
    
    print(f"\nEXECUTIVE SUMMARY:")
    print(f"Overall score: {executive_summary.get('overall_score', 'N/A')}")
    print(f"Critical issues: {executive_summary.get('critical_issues', 'N/A')}")
    print(f"Compliance level: {executive_summary.get('compliance_level', 'N/A')}")
    
    print(f"\nKEY FINDINGS:")
    for finding in executive_summary.get('key_findings', [])[:5]:
        print(f"- {finding}")
    
    print(f"\nACTION ITEMS ({len(action_items)} total):")
    for i, item in enumerate(action_items[:3], 1):
        print(f"{i}. {item.get('title', 'No title')} ({item.get('priority', 'unknown')} priority)")
        print(f"   {item.get('description', 'No description')[:100]}...")
    
    # Look for welding/hot work specific mentions
    print(f"\nHOT WORK / WELDING DETECTION:")
    hot_work_found = False
    for item in action_items:
        title = item.get('title', '').lower()
        desc = item.get('description', '').lower() 
        if any(term in title + ' ' + desc for term in ['weld', 'hot work', 'cutting', 'scintill', 'cald']):
            print(f"✓ FOUND: {item.get('title', 'Unknown')} - {item.get('type', 'unknown')} risk")
            hot_work_found = True
    
    if not hot_work_found:
        print("✗ No hot work/welding risks detected")
    
    print("="*60)
    print("JSON PARSING TEST COMPLETE")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_json_parsing())
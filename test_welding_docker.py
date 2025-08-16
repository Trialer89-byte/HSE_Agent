#!/usr/bin/env python3
"""
Test welding detection directly in Docker container
"""

import asyncio
import sys
sys.path.append('/app')
from app.agents.simple_autogen_agents import SimpleAutoGenHSEAgents

async def test():
    agents = SimpleAutoGenHSEAgents({})
    
    test_permit = {
        'id': 'test_001',
        'title': 'welsing tank repair',
        'description': 'Need to fix the tank with metal repair tools and cutting equipment',
        'work_type': 'maintenance', 
        'location': 'Tank area section B',
        'duration_hours': 4,
        'workers_count': 2,
        'equipment': 'metal repair tools, cutting equipment, portable grinder'
    }
    
    print('=== TESTING WELDING DETECTION ===')
    print(f'Title: {test_permit["title"]}')
    print(f'Equipment: {test_permit["equipment"]}')
    
    result = await agents.analyze_permit(test_permit, [])
    
    final_analysis = result.get('final_analysis', {})
    exec_summary = final_analysis.get('executive_summary', {})
    action_items = final_analysis.get('action_items', [])
    
    print(f'Critical issues: {exec_summary.get("critical_issues", 0)}')
    print(f'Action items count: {len(action_items)}')
    
    hot_work_found = False
    for item in action_items:
        title = item.get('title', '').lower()
        desc = item.get('description', '').lower()
        if any(term in title + ' ' + desc for term in ['weld', 'hot work', 'cutting', 'scintill', 'cald', 'saldatura']):
            print(f'✓ HOT WORK FOUND: {item.get("title", "Unknown")}')
            hot_work_found = True
            
    if not hot_work_found:
        print('✗ No hot work detected in action items')

if __name__ == "__main__":
    asyncio.run(test())
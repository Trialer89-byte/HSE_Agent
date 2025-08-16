#!/usr/bin/env python3
"""
Detailed analysis test to see AI output
"""

import asyncio
import sys
import json
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
    
    print('=== DETAILED ANALYSIS TEST ===')
    result = await agents.analyze_permit(test_permit, [])
    
    final_analysis = result.get('final_analysis', {})
    exec_summary = final_analysis.get('executive_summary', {})
    action_items = final_analysis.get('action_items', [])
    
    print(f'\nEXECUTIVE SUMMARY:')
    print(f'- Critical issues: {exec_summary.get("critical_issues", 0)}')
    print(f'- Key findings: {len(exec_summary.get("key_findings", []))}')
    print(f'- Next steps: {len(exec_summary.get("next_steps", []))}')
    
    print(f'\nKEY FINDINGS:')
    for i, finding in enumerate(exec_summary.get("key_findings", [])[:3], 1):
        print(f'{i}. {finding}')
    
    print(f'\nACTION ITEMS ({len(action_items)} total):')
    for i, item in enumerate(action_items, 1):
        title = item.get('title', 'No title')
        item_type = item.get('type', 'unknown')
        priority = item.get('priority', 'unknown')
        desc = item.get('description', '')[:100]
        print(f'{i}. {title} ({item_type}, {priority})')
        print(f'   {desc}...')
        
        # Check if this is hot work related
        if any(term in (title + ' ' + desc).lower() for term in ['weld', 'hot work', 'cutting', 'scintill', 'cald', 'saldatura', 'taglio']):
            print(f'   *** HOT WORK DETECTED ***')
    
    # Also show the raw AI analysis to understand what was extracted
    print(f'\nRAW ANALYSIS SUMMARY:')
    ai_analysis = result.get('ai_analysis', '')
    if 'saldatura' in ai_analysis.lower() or 'welding' in ai_analysis.lower() or 'welsing' in ai_analysis.lower():
        print('✓ AI correctly identified welding/welsing activity')
    else:
        print('✗ AI did not identify welding activity')
    
    # Show the raw parsed JSON to debug
    print(f'\nRAW AI PARSED JSON:')
    raw_json = result.get('raw_parsed_json', {})
    if raw_json:
        import json
        print(json.dumps(raw_json, indent=2, ensure_ascii=False)[:1000] + "...")
    else:
        print('No raw JSON found')

if __name__ == "__main__":
    asyncio.run(test())
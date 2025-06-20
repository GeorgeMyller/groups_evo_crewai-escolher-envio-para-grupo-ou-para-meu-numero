#!/usr/bin/env python3
"""
Test script for the new offline mode functionality
"""

import os
import sys

# Add src to Python path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from whatsapp_manager.core.group_controller import GroupController

def test_offline_mode():
    """Test the offline mode functionality"""
    print("🧪 Testing GroupController offline mode...")
    
    try:
        # Initialize controller
        print("📡 Initializing GroupController...")
        controller = GroupController()
        
        # Check API status
        print("🔍 Checking API availability...")
        api_status = controller.check_api_availability()
        
        print(f"API Status: {'✅ Available' if api_status['available'] else '❌ Unavailable'}")
        print(f"Message: {api_status['message']}")
        if api_status['response_time_ms']:
            print(f"Response time: {api_status['response_time_ms']}ms")
        
        # Try online mode first
        print("\n🌐 Attempting online mode...")
        try:
            groups_online = controller.fetch_groups(force_refresh=False)
            print(f"✅ Online mode successful! Found {len(groups_online)} groups")
        except Exception as e:
            print(f"❌ Online mode failed: {str(e)[:100]}...")
            
            # Fallback to offline mode
            print("\n🔒 Trying offline mode...")
            groups_offline = controller.fetch_groups(offline_mode=True)
            print(f"✅ Offline mode successful! Found {len(groups_offline)} groups from CSV")
            
            # Show sample groups
            if groups_offline:
                print("\n📋 Sample groups from CSV:")
                for i, group in enumerate(groups_offline[:3]):
                    print(f"  {i+1}. {group.name} ({group.group_id[:15]}...)")
                    print(f"     Enabled: {group.enabled}, Schedule: {group.horario}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_offline_mode()

#!/usr/bin/env python3
"""
Test All Imports and Functionality
Teste de todos os imports e funcionalidades
"""

import os
import sys
from pathlib import Path

# Setup paths
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

def test_core_imports():
    """Test core module imports"""
    print("Testing core imports...")
    
    try:
        from whatsapp_manager.core.group_controller import GroupController
        print("✅ GroupController imported successfully")
        
        from whatsapp_manager.core.group import Group
        print("✅ Group imported successfully")
        
        from whatsapp_manager.core.send_sandeco import SendSandeco
        print("✅ SendSandeco imported successfully")
        
        from whatsapp_manager.utils.groups_util import GroupUtils
        print("✅ GroupUtils imported successfully")
        
        from whatsapp_manager.utils.task_scheduler import TaskScheduled
        print("✅ TaskScheduled imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")
    
    try:
        from whatsapp_manager.core.group_controller import GroupController
        
        # Test creating controller (should work even if API is not connected)
        controller = GroupController()
        print("✅ GroupController instantiated successfully")
        
        # Test offline mode
        groups = controller.get_groups()
        print(f"✅ get_groups() returned {len(groups) if groups else 0} groups")
        
        return True
        
    except Exception as e:
        print(f"❌ Functionality test error: {e}")
        return False

def main():
    print("🧪 Comprehensive Import and Functionality Test")
    print("=" * 50)
    
    # Test imports
    imports_ok = test_core_imports()
    
    # Test functionality
    if imports_ok:
        functionality_ok = test_functionality()
        
        if imports_ok and functionality_ok:
            print("\n✅ All tests passed! Your system is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Check the output above.")
    else:
        print("\n❌ Import tests failed. Fix imports before testing functionality.")

if __name__ == "__main__":
    main()

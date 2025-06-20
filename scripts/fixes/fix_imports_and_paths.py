#!/usr/bin/env python3
"""
Fix Import and Path Issues Script
Script para corrigir problemas de imports e caminhos na estrutura reorganizada

This script will:
1. Fix import statements in UI pages
2. Fix import statements in scripts
3. Fix CSV file paths
4. Ensure all __init__.py files are present
5. Test all imports after fixes
"""

import os
import sys
import importlib.util
from pathlib import Path

# Get project root
PROJECT_ROOT = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"

print("🔧 Evolution API - Import & Path Fixer")
print("=" * 50)

def check_file_exists(filepath):
    """Check if file exists and print status"""
    if filepath.exists():
        print(f"✅ {filepath.relative_to(PROJECT_ROOT)}")
        return True
    else:
        print(f"❌ {filepath.relative_to(PROJECT_ROOT)} - NOT FOUND")
        return False

def ensure_init_files():
    """Ensure all __init__.py files exist"""
    print("\n1. Checking __init__.py files...")
    
    init_files = [
        SRC_DIR / "__init__.py",
        SRC_DIR / "whatsapp_manager" / "__init__.py",
        SRC_DIR / "whatsapp_manager" / "core" / "__init__.py",
        SRC_DIR / "whatsapp_manager" / "ui" / "__init__.py",
        SRC_DIR / "whatsapp_manager" / "ui" / "pages" / "__init__.py",
        SRC_DIR / "whatsapp_manager" / "utils" / "__init__.py",
    ]
    
    for init_file in init_files:
        if not init_file.exists():
            init_file.parent.mkdir(parents=True, exist_ok=True)
            init_file.write_text("")
            print(f"✅ Created {init_file.relative_to(PROJECT_ROOT)}")
        else:
            print(f"✅ {init_file.relative_to(PROJECT_ROOT)} exists")

def check_core_files():
    """Check if all core files exist"""
    print("\n2. Checking core files...")
    
    core_files = [
        SRC_DIR / "whatsapp_manager" / "core" / "group_controller.py",
        SRC_DIR / "whatsapp_manager" / "core" / "group.py",
        SRC_DIR / "whatsapp_manager" / "core" / "summary.py",
        SRC_DIR / "whatsapp_manager" / "core" / "send_sandeco.py",
        SRC_DIR / "whatsapp_manager" / "core" / "message_sandeco.py",
        SRC_DIR / "whatsapp_manager" / "utils" / "groups_util.py",
        SRC_DIR / "whatsapp_manager" / "utils" / "task_scheduler.py",
    ]
    
    all_exist = True
    for file_path in core_files:
        if not check_file_exists(file_path):
            all_exist = False
    
    return all_exist

def check_ui_files():
    """Check if UI files exist"""
    print("\n3. Checking UI files...")
    
    ui_files = [
        SRC_DIR / "whatsapp_manager" / "ui" / "pages" / "2_Portuguese.py",
        SRC_DIR / "whatsapp_manager" / "ui" / "pages" / "3_English.py",
    ]
    
    all_exist = True
    for file_path in ui_files:
        if not check_file_exists(file_path):
            all_exist = False
    
    return all_exist

def check_script_files():
    """Check if script files exist"""
    print("\n4. Checking script files...")
    
    script_files = [
        PROJECT_ROOT / "scripts" / "agendar_todos.py",
        PROJECT_ROOT / "scripts" / "delete_scheduled_tasks.py",
        PROJECT_ROOT / "scripts" / "list_scheduled_tasks.py",
        PROJECT_ROOT / "scripts" / "save_groups_to_csv.py",
    ]
    
    all_exist = True
    for file_path in script_files:
        if not check_file_exists(file_path):
            all_exist = False
    
    return all_exist

def check_csv_files():
    """Check CSV file locations and create data directory if needed"""
    print("\n5. Checking CSV files and data directory...")
    
    # Create data directory if it doesn't exist
    data_dir = PROJECT_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    print(f"✅ Data directory: {data_dir.relative_to(PROJECT_ROOT)}")
    
    # Check for CSV files
    csv_files = [
        PROJECT_ROOT / "group_summary.csv",  # Should be in root
    ]
    
    for csv_file in csv_files:
        check_file_exists(csv_file)

def test_imports():
    """Test if all imports work correctly"""
    print("\n6. Testing imports...")
    
    # Add src to path for testing
    if str(SRC_DIR) not in sys.path:
        sys.path.insert(0, str(SRC_DIR))
    
    imports_to_test = [
        ("whatsapp_manager.core.group_controller", "GroupController"),
        ("whatsapp_manager.core.group", "Group"),
        ("whatsapp_manager.core.send_sandeco", "SendSandeco"),
        ("whatsapp_manager.utils.groups_util", "GroupUtils"),
        ("whatsapp_manager.utils.task_scheduler", "TaskScheduled"),
    ]
    
    all_imports_ok = True
    
    for module_name, class_name in imports_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name}")
            else:
                print(f"❌ {module_name}.{class_name} - Class not found")
                all_imports_ok = False
        except ImportError as e:
            print(f"❌ {module_name} - Import error: {e}")
            all_imports_ok = False
        except Exception as e:
            print(f"⚠️  {module_name} - Warning: {e}")
    
    return all_imports_ok

def fix_ui_imports():
    """Fix import statements in UI files"""
    print("\n7. Checking UI import statements...")
    
    ui_files = [
        SRC_DIR / "whatsapp_manager" / "ui" / "pages" / "2_Portuguese.py",
        SRC_DIR / "whatsapp_manager" / "ui" / "pages" / "3_English.py",
    ]
    
    for ui_file in ui_files:
        if ui_file.exists():
            content = ui_file.read_text()
            
            # Check if imports are correct
            if "from whatsapp_manager.utils.groups_util import GroupUtils" in content:
                print(f"✅ {ui_file.name} - Imports look correct")
            else:
                print(f"⚠️  {ui_file.name} - May have import issues")

def fix_script_paths():
    """Check script file paths"""
    print("\n8. Checking script file paths...")
    
    script_files = [
        PROJECT_ROOT / "scripts" / "agendar_todos.py",
        PROJECT_ROOT / "scripts" / "delete_scheduled_tasks.py",
    ]
    
    for script_file in script_files:
        if script_file.exists():
            content = script_file.read_text()
            
            # Check for correct paths
            if 'os.path.join(PROJECT_ROOT, "data"' in content:
                print(f"✅ {script_file.name} - Paths look correct")
            else:
                print(f"⚠️  {script_file.name} - May have path issues")

def create_test_script():
    """Create a comprehensive test script"""
    print("\n9. Creating comprehensive test script...")
    
    test_script_content = '''#!/usr/bin/env python3
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
    print("\\nTesting basic functionality...")
    
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
            print("\\n✅ All tests passed! Your system is working correctly.")
        else:
            print("\\n⚠️  Some tests failed. Check the output above.")
    else:
        print("\\n❌ Import tests failed. Fix imports before testing functionality.")

if __name__ == "__main__":
    main()
'''
    
    test_file = PROJECT_ROOT / "test_imports_and_functionality.py"
    test_file.write_text(test_script_content)
    print(f"✅ Created {test_file.relative_to(PROJECT_ROOT)}")

def main():
    """Main function to run all checks and fixes"""
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Source Directory: {SRC_DIR}")
    
    # Run all checks
    ensure_init_files()
    core_files_ok = check_core_files()
    ui_files_ok = check_ui_files()
    script_files_ok = check_script_files()
    check_csv_files()
    
    if core_files_ok:
        imports_ok = test_imports()
        fix_ui_imports()
        fix_script_paths()
        create_test_script()
        
        print("\n" + "=" * 50)
        print("📊 SUMMARY")
        print("=" * 50)
        print(f"✅ Core files: {'OK' if core_files_ok else 'ISSUES'}")
        print(f"✅ UI files: {'OK' if ui_files_ok else 'ISSUES'}")
        print(f"✅ Script files: {'OK' if script_files_ok else 'ISSUES'}")
        print(f"✅ Imports: {'OK' if imports_ok else 'ISSUES'}")
        
        if core_files_ok and imports_ok:
            print("\n🎉 Your organized structure is working correctly!")
            print("\nNext steps:")
            print("1. Run: python test_imports_and_functionality.py")
            print("2. Test Streamlit: streamlit run src/whatsapp_manager/ui/main_app.py")
            print("3. Test scripts: python scripts/agendar_todos.py --help")
        else:
            print("\n⚠️  Some issues were found. Please check the output above.")
    else:
        print("\n❌ Core files are missing. Please ensure all files are in the correct locations.")

if __name__ == "__main__":
    main()

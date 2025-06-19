#!/usr/bin/env python3
"""
Migration Validation Script
Script de Validação da Migração

Tests the new clean architecture to ensure all components work correctly.
Testa a nova arquitetura limpa para garantir que todos os componentes funcionem corretamente.
"""

import sys
import os
import traceback
from typing import List, Tuple, Any

# Add the src_clean directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src_clean'))

def test_imports() -> List[Tuple[str, bool, str]]:
    """Test all major imports from the new structure."""
    test_results = []
    
    import_tests = [
        # Core models
        ("whatsapp_manager.core.models.group", "Group"),
        ("whatsapp_manager.core.models.message", "Message"),
        
        # Core services
        ("whatsapp_manager.core.services.group_service", "GroupService"),
        ("whatsapp_manager.core.services.message_service", "MessageService"),
        ("whatsapp_manager.core.services.summary_service", "SummaryService"),
        ("whatsapp_manager.core.services.summary_crew_service", "SummaryCrewService"),
        
        # Core controllers
        ("whatsapp_manager.core.controllers.group_controller", "GroupController"),
        
        # Infrastructure
        ("whatsapp_manager.infrastructure.api.evolution_client", "EvolutionClientWrapper"),
        ("whatsapp_manager.infrastructure.messaging.message_sender", "MessageSender"),
        ("whatsapp_manager.infrastructure.persistence.group_repository", "GroupRepository"),
        ("whatsapp_manager.infrastructure.scheduling.task_scheduler", "TaskSchedulingService"),
        
        # Shared utilities
        ("whatsapp_manager.shared.utils.date_utils", "DateUtils"),
        ("whatsapp_manager.shared.utils.group_utils", "GroupUtilsService"),
    ]
    
    for module_path, class_name in import_tests:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            test_results.append((f"{module_path}.{class_name}", True, "OK"))
        except Exception as e:
            test_results.append((f"{module_path}.{class_name}", False, str(e)))
    
    return test_results

def test_service_instantiation() -> List[Tuple[str, bool, str]]:
    """Test basic instantiation of key services."""
    test_results = []
    
    try:
        from whatsapp_manager.core.services.group_service import GroupService
        from whatsapp_manager.infrastructure.persistence.group_repository import GroupRepository
        from whatsapp_manager.infrastructure.api.evolution_client import EvolutionClientWrapper
        
        # Test instantiation
        evolution_client = EvolutionClientWrapper(
            base_url="https://test.com",
            api_token="test_token",
            instance_id="test_instance",
            instance_token="test_instance_token"
        )
        group_repo = GroupRepository()
        group_service = GroupService(evolution_client, group_repo)
        
        test_results.append(("GroupService instantiation", True, "OK"))
        
    except Exception as e:
        test_results.append(("GroupService instantiation", False, str(e)))
    
    try:
        from whatsapp_manager.shared.utils.date_utils import DateUtils
        from whatsapp_manager.shared.utils.group_utils import GroupUtilsService
        
        date_utils = DateUtils()
        group_utils = GroupUtilsService()
        
        test_results.append(("Utility services instantiation", True, "OK"))
        
    except Exception as e:
        test_results.append(("Utility services instantiation", False, str(e)))
    
    try:
        from whatsapp_manager.infrastructure.scheduling.task_scheduler import TaskSchedulingService
        
        scheduler = TaskSchedulingService()
        
        test_results.append(("TaskSchedulingService instantiation", True, "OK"))
        
    except Exception as e:
        test_results.append(("TaskSchedulingService instantiation", False, str(e)))
    
    return test_results

def test_model_creation() -> List[Tuple[str, bool, str]]:
    """Test basic model creation and validation."""
    test_results = []
    
    try:
        from whatsapp_manager.core.models.group import Group
        
        # Test Group model creation with correct parameters
        group = Group(
            group_id="test_group_123",
            name="Test Group",
            subject_owner="Test Owner",
            subject_time=1234567890,
            picture_url="https://example.com/image.jpg",
            size=5,
            creation=1234567890,
            owner="Test Owner",
            restrict=False,
            announce=False,
            is_community=False,
            is_community_announce=False,
            dias=1,
            horario="22:00",
            enabled=True,
            send_to_group=True
        )
        
        if group.group_id == "test_group_123" and group.name == "Test Group":
            test_results.append(("Group model creation", True, "OK"))
        else:
            test_results.append(("Group model creation", False, "Model fields not set correctly"))
            
    except Exception as e:
        test_results.append(("Group model creation", False, str(e)))
    
    try:
        from whatsapp_manager.core.models.message import Message
        
        # Test Message model creation with correct parameters
        message = Message(
            message_id="msg_123",
            remote_jid="group@example.com",
            text_content="Test message content",
            push_name="Test User",
            message_timestamp=1234567890
        )
        
        if message.message_id == "msg_123" and message.text_content == "Test message content":
            test_results.append(("Message model creation", True, "OK"))
        else:
            test_results.append(("Message model creation", False, "Model fields not set correctly"))
            
    except Exception as e:
        test_results.append(("Message model creation", False, str(e)))
    
    return test_results

def run_validation() -> None:
    """Run all validation tests and display results."""
    print("🧪 WhatsApp Manager - Clean Architecture Validation")
    print("=" * 60)
    
    all_tests = [
        ("📦 Import Tests", test_imports),
        ("🔧 Service Instantiation Tests", test_service_instantiation),
        ("📊 Model Creation Tests", test_model_creation),
    ]
    
    total_tests = 0
    total_passed = 0
    
    for test_category, test_function in all_tests:
        print(f"\n{test_category}")
        print("-" * len(test_category))
        
        try:
            results = test_function()
            
            for test_name, passed, message in results:
                total_tests += 1
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"{status:10} {test_name}")
                
                if not passed:
                    print(f"           Error: {message}")
                else:
                    total_passed += 1
                    
        except Exception as e:
            print(f"❌ FAIL    {test_category} - Unexpected error")
            print(f"           Error: {str(e)}")
            print(f"           Traceback: {traceback.format_exc()}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 SUMMARY / RESUMO")
    print(f"{'='*60}")
    print(f"Total Tests / Total de Testes: {total_tests}")
    print(f"Passed / Aprovados: {total_passed}")
    print(f"Failed / Falharam: {total_tests - total_passed}")
    print(f"Success Rate / Taxa de Sucesso: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! The new architecture is working correctly.")
        print("🎉 Todos os testes passaram! A nova arquitetura está funcionando corretamente.")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed. Please check the errors above.")
        print(f"⚠️  {total_tests - total_passed} teste(s) falharam. Verifique os erros acima.")

if __name__ == "__main__":
    run_validation()

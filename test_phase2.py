#!/usr/bin/env python3
"""
Teste da Fase 2 - Sistema de Configuração e Modelos Pydantic
Test Phase 2 - Configuration System and Pydantic Models
"""

import sys
from pathlib import Path

# Adiciona o diretório src ao Python path
sys.path.append(str(Path(__file__).parent / "src"))

def test_settings():
    """Testa o sistema de configurações"""
    print("🔧 Testando Sistema de Configurações...")
    
    try:
        from config.settings import Settings
        
        # Cria instância das configurações
        settings = Settings()
        
        print(f"✅ Configurações carregadas:")
        print(f"   - App Name: {settings.app_name}")
        print(f"   - Version: {settings.app_version}")
        print(f"   - Environment: {settings.environment}")
        print(f"   - Evolution API URL: {settings.evolution_api_url}")
        print(f"   - WhatsApp Phone: {settings.whatsapp_phone_number}")
        print(f"   - Summary Language: {settings.summary_language}")
        
        # Testa validadores
        print(f"\n🔍 Testando validadores...")
        
        # Testa validação de URL
        try:
            settings.evolution_api_url = "invalid-url"
        except Exception as e:
            print(f"   ✅ Validação de URL funciona: {e}")
        
        # Testa validação de horário
        try:
            settings.summary_schedule_time = "25:99"
        except Exception as e:
            print(f"   ✅ Validação de horário funciona: {e}")
        
        # Testa métodos auxiliares
        print(f"\n🛠️ Testando métodos auxiliares...")
        print(f"   - Data path: {settings.get_data_path('test.json')}")
        print(f"   - Is production: {settings.is_production()}")
        print(f"   - Evolution headers: {settings.get_evolution_headers()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de configurações: {e}")
        return False


def test_models():
    """Testa os modelos Pydantic"""
    print("\n📋 Testando Modelos Pydantic...")
    
    try:
        from src.core.models import Group, GroupStatus, MessageType
        from datetime import datetime
        
        # Cria um grupo de teste
        group_data = {
            "id": "123456789@g.us",
            "name": "Grupo de Teste",
            "status": GroupStatus.ACTIVE,
            "description": "Um grupo para testes",
            "total_messages": 100,
            "total_participants": 25
        }
        
        group = Group(**group_data)
        
        print(f"✅ Grupo criado:")
        print(f"   - ID: {group.id}")
        print(f"   - Nome: {group.name}")
        print(f"   - Display Name: {group.display_name}")
        print(f"   - Status: {group.status}")
        print(f"   - Recentemente atualizado: {group.is_recently_updated}")
        
        # Testa validações
        print(f"\n🔍 Testando validações de modelos...")
        
        # Testa ID inválido
        try:
            Group(id="invalid-id", name="Test")
        except Exception as e:
            print(f"   ✅ Validação de ID funciona: {e}")
        
        # Testa nome vazio
        try:
            Group(id="123@g.us", name="")
        except Exception as e:
            print(f"   ✅ Validação de nome funciona: {e}")
        
        # Testa conversão para formato legado
        legacy_dict = group.to_legacy_dict()
        print(f"\n🔄 Conversão para formato legado:")
        print(f"   - Tipo: {type(legacy_dict)}")
        print(f"   - Keys: {list(legacy_dict.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de modelos: {e}")
        return False


def test_controllers():
    """Testa os controllers reestruturados"""
    print("\n🎮 Testando Controllers...")
    
    try:
        from src.core.controllers.group_controller import GroupController
        
        # Cria instância do controller
        controller = GroupController()
        
        print(f"✅ GroupController criado com sucesso")
        print(f"   - Tipo: {type(controller)}")
        
        # Lista métodos disponíveis
        methods = [method for method in dir(controller) 
                  if not method.startswith('_') and callable(getattr(controller, method))]
        print(f"   - Métodos disponíveis: {len(methods)}")
        print(f"   - Exemplos: {methods[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de controllers: {e}")
        return False


def test_compatibility():
    """Testa arquivos de compatibilidade"""
    print("\n🔗 Testando Compatibilidade...")
    
    try:
        # Testa import do arquivo legado
        from group import Group as LegacyGroup
        print(f"✅ Import legado funciona: {LegacyGroup}")
        
        from group_controller import GroupController as LegacyController
        print(f"✅ Import legado do controller funciona: {LegacyController}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de compatibilidade: {e}")
        return False


def main():
    """Função principal de teste"""
    print("=" * 60)
    print("🚀 TESTE DA FASE 2 - ESTRUTURA DO SISTEMA")
    print("=" * 60)
    
    results = []
    
    # Executa todos os testes
    results.append(test_settings())
    results.append(test_models())
    results.append(test_controllers())
    results.append(test_compatibility())
    
    # Relatório final
    print("\n" + "=" * 60)
    print("📊 RELATÓRIO FINAL")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Testes passaram: {passed}/{total}")
    print(f"❌ Testes falharam: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("✨ Fase 2 implementada com sucesso!")
    else:
        print(f"\n⚠️  {total - passed} teste(s) falharam.")
        print("🔧 Ajustes necessários na implementação.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

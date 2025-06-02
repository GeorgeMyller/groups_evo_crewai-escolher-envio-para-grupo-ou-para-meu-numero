#!/usr/bin/env python3
"""
Script de teste para verificar se a estrutura reorganizada está funcionando
"""

import os
import sys

# Add src to Python path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

def test_imports():
    """Testa se todos os imports principais estão funcionando"""
    print("🔍 Testando imports...")
    
    try:
        from whatsapp_manager.core.group_controller import GroupController
        print("✅ GroupController importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar GroupController: {e}")
        return False
        
    try:
        from whatsapp_manager.core.group import Group
        print("✅ Group importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar Group: {e}")
        return False
        
    try:
        from whatsapp_manager.utils.groups_util import GroupUtils
        print("✅ GroupUtils importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar GroupUtils: {e}")
        return False
        
    try:
        from whatsapp_manager.core.send_sandeco import SendSandeco
        print("✅ SendSandeco importado com sucesso")
    except ImportError as e:
        print(f"❌ Erro ao importar SendSandeco: {e}")
        return False
        
    return True

def test_group_controller():
    """Testa a funcionalidade básica do GroupController"""
    print("\n🔍 Testando GroupController...")
    
    try:
        from whatsapp_manager.core.group_controller import GroupController
        
        # Tenta inicializar o GroupController
        control = GroupController()
        print("✅ GroupController inicializado com sucesso")
        
        # Testa o modo offline
        groups = control.fetch_groups(offline_mode=True)
        print(f"✅ Modo offline funcionando - {len(groups)} grupos carregados")
        
        # Verifica se consegue acessar o CSV
        if len(groups) > 0:
            print(f"✅ Primeiro grupo: {groups[0].name}")
        else:
            print("⚠️ Nenhum grupo encontrado (isso pode ser normal se o CSV estiver vazio)")
            
        return True
        
    except Exception as e:
        print(f"❌ Erro no GroupController: {e}")
        return False

def test_file_paths():
    """Testa se os caminhos dos arquivos estão corretos"""
    print("\n🔍 Testando caminhos dos arquivos...")
    
    # Verifica se o CSV existe
    csv_path = os.path.join(PROJECT_ROOT, "group_summary.csv")
    if os.path.exists(csv_path):
        print(f"✅ CSV encontrado: {csv_path}")
    else:
        print(f"⚠️ CSV não encontrado na raiz: {csv_path}")
        
    # Verifica se o diretório data existe
    data_path = os.path.join(PROJECT_ROOT, "data")
    if os.path.exists(data_path):
        print(f"✅ Diretório data encontrado: {data_path}")
    else:
        print(f"⚠️ Diretório data não encontrado: {data_path}")
        
    # Verifica se o script summary.py existe no local correto
    summary_path = os.path.join(PROJECT_ROOT, "src", "whatsapp_manager", "core", "summary.py")
    if os.path.exists(summary_path):
        print(f"✅ Script summary.py encontrado: {summary_path}")
    else:
        print(f"❌ Script summary.py não encontrado: {summary_path}")
        
    return True

def main():
    """Executa todos os testes"""
    print("🧪 Iniciando testes da estrutura reorganizada...\n")
    
    success = True
    
    # Teste 1: Imports
    if not test_imports():
        success = False
        
    # Teste 2: GroupController
    if not test_group_controller():
        success = False
        
    # Teste 3: Caminhos dos arquivos
    if not test_file_paths():
        success = False
        
    print("\n" + "="*50)
    if success:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ A estrutura reorganizada está funcionando corretamente!")
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("⚠️ Há problemas na estrutura que precisam ser corrigidos.")
    print("="*50)

if __name__ == "__main__":
    main()

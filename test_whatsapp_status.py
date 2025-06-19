#!/usr/bin/env python3
"""
Teste da nova funcionalidade de verificação de status WhatsApp
"""
import sys
import os

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from whatsapp_manager.core.group_controller import GroupController
except ImportError as e:
    print(f"Erro ao importar GroupController: {e}")
    sys.exit(1)

def main():
    print("🧪 TESTE DA NOVA FUNCIONALIDADE - STATUS WHATSAPP")
    print("=" * 60)
    
    try:
        # Initialize controller
        print("📡 Inicializando GroupController...")
        controller = GroupController()
        
        # Test API availability
        print("\n🔍 1. Verificando disponibilidade da API...")
        api_status = controller.check_api_availability()
        print(f"   Status: {'✅ Disponível' if api_status['available'] else '❌ Indisponível'}")
        print(f"   Mensagem: {api_status['message']}")
        if api_status.get('response_time_ms'):
            print(f"   Tempo de resposta: {api_status['response_time_ms']}ms")
        
        # Test WhatsApp connection status
        print("\n📱 2. Verificando status da conexão WhatsApp...")
        whatsapp_status = controller.check_whatsapp_connection()
        
        print(f"   Conectado: {'✅ Sim' if whatsapp_status.get('connected', False) else '❌ Não'}")
        print(f"   Estado: {whatsapp_status.get('state', 'unknown')}")
        print(f"   Mensagem: {whatsapp_status['message']}")
        print(f"   Nível: {whatsapp_status.get('level', 'unknown')}")
        
        if whatsapp_status.get('action'):
            print(f"   Ação: {whatsapp_status['action']}")
        
        if whatsapp_status.get('manager_url'):
            print(f"   Manager URL: {whatsapp_status['manager_url']}")
        
        # Test groups fetching with new logic
        print("\n📊 3. Tentando buscar grupos...")
        try:
            groups = controller.fetch_groups(force_refresh=False)
            print(f"   ✅ Sucesso! Encontrados {len(groups)} grupos")
            
            if len(groups) > 0:
                print(f"   Exemplo: {groups[0].name}")
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            print("   (Isso é esperado se o WhatsApp não estiver conectado)")
        
    except Exception as e:
        print(f"❌ Erro geral: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

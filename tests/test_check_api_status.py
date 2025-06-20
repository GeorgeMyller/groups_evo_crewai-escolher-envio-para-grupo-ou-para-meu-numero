#!/usr/bin/env python3
"""
Script para verificar e diagnosticar o status da API Evolution
"""

import os
import sys
import requests
import time
from dotenv import load_dotenv

# Add src to Python path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'src'))

from whatsapp_manager.core.group_controller import GroupController

def check_api_endpoints():
    """Verifica diferentes endpoints da API Evolution"""
    
    load_dotenv(override=True)
    
    base_url = os.getenv("EVO_BASE_URL")
    instance_name = os.getenv("EVO_INSTANCE_NAME")
    
    print(f"🔍 Verificando API Evolution...")
    print(f"📡 Base URL: {base_url}")
    print(f"🏷️  Instance: {instance_name}")
    print("-" * 50)
    
    # Endpoints para testar
    endpoints = [
        "/",
        "/status",
        "/health",
        f"/instance/fetchInstances",
    ]
    
    for endpoint in endpoints:
        url = f"{base_url.rstrip('/')}{endpoint}"
        print(f"\n🧪 Testando: {url}")
        
        try:
            response = requests.get(url, timeout=5)
            print(f"✅ Status: {response.status_code}")
            
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    print(f"📄 Response: {data}")
                except:
                    print(f"📄 Response: {response.text[:200]}...")
            else:
                print(f"📄 Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout (>5s)")
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection refused")
        except Exception as e:
            print(f"❌ Erro: {e}")

def test_group_controller():
    """Testa o GroupController diretamente"""
    
    print("\n" + "="*50)
    print("🧪 Testando GroupController...")
    print("="*50)
    
    try:
        controller = GroupController()
        
        # Verifica status da API
        api_status = controller.check_api_availability()
        
        if api_status["available"]:
            print(f"✅ API disponível: {api_status['message']}")
            print(f"⏱️ Tempo de resposta: {api_status['response_time_ms']}ms")
        else:
            print(f"❌ API indisponível: {api_status['message']}")
        
        # Tenta carregar grupos
        print("\n📊 Carregando grupos...")
        groups = controller.get_groups()
        
        if groups:
            print(f"✅ {len(groups)} grupos carregados com sucesso!")
            print(f"📋 Primeiro grupo: {groups[0].subject[:50]}...")
            print(f"💾 Fonte: {'API' if api_status['available'] else 'Cache/CSV'}")
        else:
            print(f"❌ Nenhum grupo encontrado")
            
    except Exception as e:
        print(f"❌ Erro no GroupController: {e}")

def show_solutions():
    """Mostra soluções possíveis"""
    
    print("\n" + "="*50)
    print("💡 SOLUÇÕES POSSÍVEIS")
    print("="*50)
    
    print("""
🟢 OPÇÃO 1: Continuar usando modo offline
   - Seu sistema pode funcionar apenas com dados do CSV
   - Para testar: uv run streamlit run src/whatsapp_manager/ui/main_app.py
   
🟡 OPÇÃO 2: Configurar API Evolution local
   - Baixar Evolution API: https://github.com/EvolutionAPI/evolution-api
   - Executar localmente na porta 8081
   - Atualizar .env com URL local: EVO_BASE_URL=http://localhost:8081
   
🔴 OPÇÃO 3: Verificar servidor remoto
   - Verificar se 192.168.1.151:8081 está funcionando
   - Verificar firewall/rede
   - Testar: curl http://192.168.1.151:8081
   
📝 ARQUIVOS IMPORTANTES:
   - .env (configurações da API)
   - group_summary.csv (dados dos grupos)
   - data/groups_cache.json (cache local)
""")

def main():
    print("🚀 DIAGNÓSTICO DA API EVOLUTION")
    print("="*50)
    
    # Verifica endpoints
    check_api_endpoints()
    
    # Testa controller
    test_group_controller()
    
    # Mostra soluções
    show_solutions()

if __name__ == "__main__":
    main()

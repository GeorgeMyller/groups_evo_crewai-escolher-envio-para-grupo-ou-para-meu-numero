#!/usr/bin/env python3
"""
Diagnóstico completo da conectividade da API Evolution
"""
import os
import sys
import requests
import time
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(env_path, override=True)

def test_api_basic():
    """Teste básico da API Evolution"""
    print("🔍 TESTE 1: Conectividade básica da API")
    print("-" * 50)
    
    base_url = os.getenv("EVO_BASE_URL")
    print(f"Base URL: {base_url}")
    
    if not base_url:
        print("❌ EVO_BASE_URL não encontrada no .env")
        return False
    
    try:
        start_time = time.time()
        response = requests.get(f"{base_url}/", timeout=10)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {response_time}ms")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API Status: {data.get('status', 'unknown')}")
                print(f"API Version: {data.get('version', 'unknown')}")
                print("✅ API básica funcionando")
                return True
            except Exception as e:
                print(f"⚠️ API responde mas não retorna JSON válido: {e}")
                return False
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout na conexão (>10s)")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Erro de conexão - API pode estar offline")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False

def test_instance_status():
    """Teste do status da instância"""
    print("\n🔍 TESTE 2: Status da instância WhatsApp")
    print("-" * 50)
    
    base_url = os.getenv("EVO_BASE_URL")
    api_token = os.getenv("EVO_API_TOKEN")
    instance_name = os.getenv("EVO_INSTANCE_NAME")
    
    print(f"Instance Name: {instance_name}")
    print(f"API Token: {'✓' if api_token else '✗'}")
    
    if not all([base_url, api_token, instance_name]):
        print("❌ Credenciais incompletas")
        return False
    
    try:
        headers = {
            "Content-Type": "application/json",
            "apikey": api_token
        }
        
        url = f"{base_url}/instance/connectionState/{instance_name}"
        print(f"Testing URL: {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Connection State: {data}")
            print("✅ Instance status obtido com sucesso")
            return True
        else:
            print(f"❌ Erro ao obter status da instância: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar instância: {e}")
        return False

def test_groups_endpoint():
    """Teste do endpoint de grupos"""
    print("\n🔍 TESTE 3: Endpoint de grupos")
    print("-" * 50)
    
    base_url = os.getenv("EVO_BASE_URL")
    api_token = os.getenv("EVO_API_TOKEN")
    instance_name = os.getenv("EVO_INSTANCE_NAME")
    instance_token = os.getenv("EVO_INSTANCE_TOKEN")
    
    if not all([base_url, api_token, instance_name, instance_token]):
        print("❌ Credenciais incompletas para teste de grupos")
        return False
    
    try:
        headers = {
            "Content-Type": "application/json",
            "apikey": api_token
        }
        
        url = f"{base_url}/group/fetchAllGroups/{instance_name}"
        params = {"getParticipants": "false"}
        
        print(f"Testing URL: {url}")
        print(f"Headers: {headers}")
        print(f"Params: {params}")
        
        response = requests.get(url, headers=headers, params=params, timeout=30)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            groups_count = len(data) if isinstance(data, list) else 0
            print(f"✅ Grupos obtidos com sucesso: {groups_count} grupos encontrados")
            
            if groups_count > 0:
                print(f"Exemplo do primeiro grupo: {data[0].get('subject', 'N/A')}")
            
            return True
        else:
            print(f"❌ Erro ao obter grupos: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error details: {error_data}")
            except:
                print(f"Raw response: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao testar grupos: {e}")
        return False

def test_environment_loading():
    """Teste do carregamento das variáveis de ambiente"""
    print("\n🔍 TESTE 4: Carregamento das variáveis de ambiente")
    print("-" * 50)
    
    required_vars = [
        "EVO_API_TOKEN",
        "EVO_INSTANCE_TOKEN", 
        "EVO_INSTANCE_NAME",
        "EVO_BASE_URL"
    ]
    
    all_good = True
    for var in required_vars:
        value = os.getenv(var)
        status = "✓" if value else "✗"
        print(f"{var}: {status}")
        if not value:
            all_good = False
    
    print(f"\n{'✅ Todas as variáveis carregadas' if all_good else '❌ Variáveis faltando'}")
    return all_good

def main():
    """Executa todos os testes de diagnóstico"""
    print("🚀 DIAGNÓSTICO COMPLETO DA API EVOLUTION")
    print("=" * 60)
    
    # Test environment loading
    env_ok = test_environment_loading()
    
    # Test basic API connectivity
    api_ok = test_api_basic()
    
    # Test instance status
    instance_ok = test_instance_status()
    
    # Test groups endpoint
    groups_ok = test_groups_endpoint()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("-" * 30)
    print(f"Environment: {'✅' if env_ok else '❌'}")
    print(f"API Basic: {'✅' if api_ok else '❌'}")
    print(f"Instance: {'✅' if instance_ok else '❌'}")
    print(f"Groups: {'✅' if groups_ok else '❌'}")
    
    if all([env_ok, api_ok, instance_ok, groups_ok]):
        print("\n🎉 TODOS OS TESTES PASSARAM - API está funcionando!")
        return True
    else:
        print("\n⚠️ ALGUNS TESTES FALHARAM - verifique os problemas acima")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

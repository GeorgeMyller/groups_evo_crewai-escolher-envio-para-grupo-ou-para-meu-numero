#!/usr/bin/env python3
"""
Diagnóstico detalhado do erro 500 da API Evolution
"""
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
env_path = os.path.join(PROJECT_ROOT, '.env')
load_dotenv(env_path, override=True)

def test_api_endpoints():
    """Testa vários endpoints da API para identificar onde está o problema"""
    print("🔍 DIAGNÓSTICO DETALHADO - ERRO 500 API EVOLUTION")
    print("=" * 60)
    
    base_url = os.getenv("EVO_BASE_URL")
    api_token = os.getenv("EVO_API_TOKEN")
    instance_name = os.getenv("EVO_INSTANCE_NAME")
    instance_token = os.getenv("EVO_INSTANCE_TOKEN")
    
    print(f"Base URL: {base_url}")
    print(f"Instance: {instance_name}")
    print(f"API Token: {'✓' if api_token else '✗'}")
    print(f"Instance Token: {'✓' if instance_token else '✗'}")
    
    headers = {
        "Content-Type": "application/json",
        "apikey": api_token
    }
    
    # Lista de endpoints para testar
    endpoints = [
        {
            "name": "API Health",
            "url": f"{base_url}/",
            "method": "GET",
            "headers": {},
            "params": {}
        },
        {
            "name": "Instance Status",
            "url": f"{base_url}/instance/connectionState/{instance_name}",
            "method": "GET", 
            "headers": headers,
            "params": {}
        },
        {
            "name": "Instance Info",
            "url": f"{base_url}/instance/fetchInstances",
            "method": "GET",
            "headers": headers,
            "params": {}
        },
        {
            "name": "Groups (Problematic)",
            "url": f"{base_url}/group/fetchAllGroups/{instance_name}",
            "method": "GET",
            "headers": headers,
            "params": {"getParticipants": "false"}
        }
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n🧪 Testando: {endpoint['name']}")
        print(f"   URL: {endpoint['url']}")
        
        try:
            if endpoint['method'] == 'GET':
                response = requests.get(
                    endpoint['url'], 
                    headers=endpoint['headers'],
                    params=endpoint['params'],
                    timeout=30
                )
            
            print(f"   Status: {response.status_code}")
            print(f"   Headers: {dict(response.headers)}")
            
            try:
                data = response.json()
                print(f"   Response (JSON): {json.dumps(data, indent=2)[:500]}...")
                
                if response.status_code != 200:
                    print(f"   ❌ ERRO: {data}")
                else:
                    print(f"   ✅ SUCCESS")
            except:
                print(f"   Response (Text): {response.text[:300]}...")
            
            results.append({
                "endpoint": endpoint['name'],
                "status_code": response.status_code,
                "success": response.status_code == 200
            })
            
        except Exception as e:
            print(f"   ❌ ERRO: {e}")
            results.append({
                "endpoint": endpoint['name'],
                "status_code": None,
                "success": False,
                "error": str(e)
            })
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("-" * 30)
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['endpoint']}: {result.get('status_code', 'ERROR')}")
    
    return results

if __name__ == "__main__":
    test_api_endpoints()

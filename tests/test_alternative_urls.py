#!/usr/bin/env python3
"""
Teste de URLs alternativas para encontrar a API Evolution
"""
import requests
import time

def test_url(url, timeout=5):
    """Testa uma URL específica"""
    try:
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if response.status_code == 200:
            try:
                data = response.json()
                return {
                    "status": "✅ Funcionando",
                    "response_time": f"{response_time}ms",
                    "data": data
                }
            except:
                return {
                    "status": "✅ Responde (mas não JSON)",
                    "response_time": f"{response_time}ms",
                    "data": response.text[:100]
                }
        else:
            return {
                "status": f"❌ Status {response.status_code}",
                "response_time": f"{response_time}ms",
                "data": None
            }
    except requests.exceptions.Timeout:
        return {"status": "❌ Timeout", "response_time": f">{timeout}s", "data": None}
    except requests.exceptions.ConnectionError:
        return {"status": "❌ Conexão rejeitada", "response_time": "N/A", "data": None}
    except Exception as e:
        return {"status": f"❌ Erro: {e}", "response_time": "N/A", "data": None}

def main():
    print("🔍 TESTANDO URLs ALTERNATIVAS PARA API EVOLUTION")
    print("=" * 60)
    
    # URLs comuns onde Evolution API pode estar rodando
    test_urls = [
        "http://localhost:8081",
        "http://127.0.0.1:8081",
        "http://192.168.1.151:8081",  # URL atual
        "http://localhost:3000",      # Porta alternativa comum
        "http://127.0.0.1:3000",
        "http://192.168.1.151:3000",
        "http://localhost:8080",      # Outra porta comum
        "http://127.0.0.1:8080",
        "http://192.168.1.151:8080",
        "http://localhost:8000",      # Mais uma porta comum
        "http://127.0.0.1:8000",
        "http://192.168.1.151:8000",
    ]
    
    working_urls = []
    
    for url in test_urls:
        print(f"\n🧪 Testando: {url}")
        result = test_url(url)
        print(f"   Status: {result['status']}")
        print(f"   Tempo: {result['response_time']}")
        
        if result['data']:
            print(f"   Dados: {str(result['data'])[:100]}...")
        
        if "✅" in result['status']:
            working_urls.append(url)
    
    print("\n" + "=" * 60)
    print("📊 RESULTADO FINAL")
    print("-" * 30)
    
    if working_urls:
        print(f"✅ URLs funcionando: {len(working_urls)}")
        for url in working_urls:
            print(f"   - {url}")
        print("\n💡 RECOMENDAÇÃO:")
        print(f"   Atualize o .env com: EVO_BASE_URL={working_urls[0]}")
    else:
        print("❌ Nenhuma URL respondeu!")
        print("\n💡 POSSÍVEIS SOLUÇÕES:")
        print("   1. Verificar se o Evolution API está rodando")
        print("   2. Verificar a configuração de rede")
        print("   3. Tentar outras portas/IPs")
        print("   4. Verificar logs do Evolution API")

if __name__ == "__main__":
    main()

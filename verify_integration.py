#!/usr/bin/env python3
"""
Final integration verification script
"""

import asyncio
import time
import requests
from datetime import datetime

from src.infrastructure.manager import InfrastructureManager
from src.infrastructure.cache.redis_cache import CacheConfig


async def verify_complete_integration():
    """Verify all components are working together."""
    print("🔍 VERIFICAÇÃO FINAL DE INTEGRAÇÃO")
    print("="*60)
    
    results = {
        "cache": False,
        "metrics": False,
        "backup": False,
        "streamlit": False,
        "performance": False
    }
    
    manager = InfrastructureManager()
    
    try:
        # 1. Test Infrastructure Initialization
        print("1️⃣ Testando inicialização da infraestrutura...")
        cache_config = CacheConfig()
        init_result = await manager.initialize(cache_config=cache_config)
        
        if init_result["overall_status"] == "success":
            print("   ✅ Infraestrutura inicializada com sucesso")
            results["cache"] = True
        else:
            print("   ❌ Falha na inicialização da infraestrutura")
            return results
        
        # 2. Test Cache Operations
        print("2️⃣ Testando operações de cache...")
        
        # Cache warming
        test_data = [{"id": i, "name": f"Test Group {i}"} for i in range(1, 6)]
        warm_result = await manager.warm_cache_with_groups(test_data)
        
        if warm_result["status"] == "success":
            print(f"   ✅ Cache warming: {warm_result['warmed_keys']} chaves")
        
        # Batch operations
        batch_data = {f"verify:test:{i}": {"timestamp": datetime.now().isoformat()} for i in range(10)}
        write_result = await manager.batch_cache_operation("set", batch_data)
        read_result = await manager.batch_cache_operation("get", list(batch_data.keys()))
        
        if write_result["status"] == "success" and read_result["status"] == "success":
            print("   ✅ Operações em lote funcionando")
        
        # 3. Test Metrics Server
        print("3️⃣ Testando servidor de métricas...")
        try:
            # Try common ports
            for port in [8000, 8001, 8002]:
                try:
                    response = requests.get(f"http://localhost:{port}/metrics", timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ Servidor de métricas ativo na porta {port}")
                        results["metrics"] = True
                        break
                except:
                    continue
            
            if not results["metrics"]:
                print("   ⚠️ Servidor de métricas não encontrado (pode estar em porta diferente)")
        except Exception as e:
            print(f"   ⚠️ Erro ao testar métricas: {e}")
        
        # 4. Test Backup System
        print("4️⃣ Testando sistema de backup...")
        try:
            backup_result = manager.backup_manager.list_backups()
            if backup_result["status"] == "success":
                print(f"   ✅ Sistema de backup funcional (diretório: {backup_result.get('backup_directory')})")
                results["backup"] = True
        except Exception as e:
            print(f"   ⚠️ Erro no sistema de backup: {e}")
        
        # 5. Test Streamlit App
        print("5️⃣ Testando aplicação Streamlit...")
        try:
            # Try common Streamlit ports
            for port in [8092, 8090, 8501]:
                try:
                    response = requests.get(f"http://localhost:{port}", timeout=5)
                    if response.status_code == 200:
                        print(f"   ✅ Streamlit app rodando na porta {port}")
                        results["streamlit"] = True
                        break
                except:
                    continue
            
            if not results["streamlit"]:
                print("   ⚠️ Streamlit app não encontrado (pode não estar rodando)")
        except Exception as e:
            print(f"   ⚠️ Erro ao testar Streamlit: {e}")
        
        # 6. Performance Test
        print("6️⃣ Teste rápido de performance...")
        start = time.time()
        
        # Quick performance test
        perf_data = {f"perf:test:{i}": {"value": i} for i in range(100)}
        perf_write = await manager.batch_cache_operation("set", perf_data)
        perf_read = await manager.batch_cache_operation("get", list(perf_data.keys()))
        
        perf_time = time.time() - start
        ops_per_sec = 200 / perf_time  # 100 writes + 100 reads
        
        if ops_per_sec > 1000:  # At least 1k ops/sec
            print(f"   ✅ Performance adequada: {ops_per_sec:.0f} ops/sec")
            results["performance"] = True
        else:
            print(f"   ⚠️ Performance baixa: {ops_per_sec:.0f} ops/sec")
        
        # 7. Final Cache Stats
        print("7️⃣ Estatísticas finais do cache...")
        cache_info = await manager.get_cache_info()
        if cache_info["status"] == "connected":
            print(f"   📊 Total de chaves: {cache_info.get('total_keys', 'N/A')}")
            print(f"   💿 Uso de memória: {cache_info.get('memory', {}).get('used_memory_human', 'N/A')}")
            print(f"   🎯 Taxa de acerto: {cache_info.get('stats', {}).get('hit_rate', 0):.1f}%")
        
    except Exception as e:
        print(f"❌ Erro durante verificação: {e}")
        import traceback
        traceback.print_exc()
    finally:
        manager.shutdown()
    
    # Summary
    print("\n" + "="*60)
    print("📋 RESUMO DA VERIFICAÇÃO:")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for component, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {component.title()}: {'OK' if status else 'FAIL'}")
    
    success_rate = (passed_tests / total_tests) * 100
    print(f"\n🎯 Taxa de Sucesso: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate >= 80:
        print("🎉 SISTEMA PRONTO PARA PRODUÇÃO! 🚀")
    elif success_rate >= 60:
        print("⚠️ Sistema funcional com algumas limitações")
    else:
        print("❌ Sistema requer correções antes do uso")
    
    return results


if __name__ == "__main__":
    asyncio.run(verify_complete_integration())

#!/usr/bin/env python3
"""
Quick cache performance test
"""

import asyncio
import time
from datetime import datetime

from src.infrastructure.manager import InfrastructureManager
from src.infrastructure.cache.redis_cache import CacheConfig


async def quick_performance_test():
    """Quick test of cache performance."""
    print("⚡ Quick Cache Performance Test")
    print("="*50)
    
    manager = InfrastructureManager()
    
    try:
        # Initialize
        cache_config = CacheConfig()
        await manager.initialize(cache_config=cache_config)
        
        # Test 1: Single operations
        print("🔬 Test 1: Single Operations")
        start = time.time()
        
        # Write 10 items
        for i in range(10):
            await manager.cache_manager.set(f"test:single:{i}", {"value": i, "timestamp": datetime.now().isoformat()})
        
        # Read 10 items
        for i in range(10):
            value = await manager.cache_manager.get(f"test:single:{i}")
            assert value is not None, f"Key test:single:{i} not found"
        
        single_time = time.time() - start
        print(f"   ✅ 10 writes + 10 reads: {single_time:.3f}s ({20/single_time:.1f} ops/sec)")
        
        # Test 2: Batch operations
        print("🔬 Test 2: Batch Operations")
        start = time.time()
        
        # Batch write
        batch_data = {f"test:batch:{i}": {"value": i, "batch": True} for i in range(50)}
        write_result = await manager.batch_cache_operation("set", batch_data)
        
        # Batch read
        read_keys = list(batch_data.keys())
        read_result = await manager.batch_cache_operation("get", read_keys)
        
        batch_time = time.time() - start
        print(f"   ✅ 50 batch writes + 50 batch reads: {batch_time:.3f}s ({100/batch_time:.1f} ops/sec)")
        
        # Test 3: Cache warming
        print("🔬 Test 3: Cache Warming")
        start = time.time()
        
        test_groups = [{"id": i, "name": f"Group {i}", "members": i*10} for i in range(1, 21)]
        warm_result = await manager.warm_cache_with_groups(test_groups)
        
        warm_time = time.time() - start
        print(f"   ✅ Cache warming (20 groups): {warm_time:.3f}s")
        print(f"   📦 Keys warmed: {warm_result.get('warmed_keys', 'N/A')}")
        
        # Final stats
        cache_info = await manager.get_cache_info()
        print("\n📊 Final Cache Stats:")
        print(f"   🔑 Total keys: {cache_info.get('total_keys', 'N/A')}")
        print(f"   💿 Memory: {cache_info.get('memory', {}).get('used_memory_human', 'N/A')}")
        print(f"   🎯 Hit rate: {cache_info.get('stats', {}).get('hit_rate', 0):.1f}%")
        
        # Performance summary
        total_ops = 20 + 100 + warm_result.get('warmed_keys', 0)
        total_time = single_time + batch_time + warm_time
        print(f"\n⚡ Performance Summary:")
        print(f"   📈 Total operations: {total_ops}")
        print(f"   ⏱️ Total time: {total_time:.3f}s")
        print(f"   🚀 Average ops/sec: {total_ops/total_time:.1f}")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        manager.shutdown()


if __name__ == "__main__":
    asyncio.run(quick_performance_test())

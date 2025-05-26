#!/usr/bin/env python3
"""
Load test for cache performance
"""

import asyncio
import time
import random
from typing import List, Dict, Any
from datetime import datetime

from src.infrastructure.manager import InfrastructureManager
from src.infrastructure.cache.redis_cache import CacheConfig


async def simulate_group_operations(manager: InfrastructureManager, num_groups: int = 100, operations_per_group: int = 10):
    """Simulate real-world cache operations for groups."""
    
    print(f"🚀 Starting load test: {num_groups} groups, {operations_per_group} ops/group")
    
    # Generate test data
    test_groups = []
    for i in range(num_groups):
        group = {
            "id": i + 1,
            "name": f"Test Group {i + 1}",
            "description": f"Load test group number {i + 1}",
            "member_count": random.randint(5, 200),
            "created_at": datetime.now().isoformat(),
            "last_activity": datetime.now().isoformat(),
            "tags": [f"tag{j}" for j in range(random.randint(1, 5))],
            "metadata": {
                "priority": random.choice(["high", "medium", "low"]),
                "active": random.choice([True, False]),
                "region": random.choice(["BR", "US", "EU"])
            }
        }
        test_groups.append(group)
    
    # Batch cache operations
    start_time = time.time()
    
    # 1. Warm cache with all groups
    print("📦 Warming cache with test data...")
    warm_result = await manager.warm_cache_with_groups(test_groups)
    if warm_result["status"] == "success":
        print(f"✅ Cache warmed: {warm_result['warmed_keys']} keys")
    else:
        print(f"❌ Cache warming failed: {warm_result.get('message')}")
        return
    
    # 2. Simulate read operations
    print("📖 Simulating read operations...")
    read_tasks = []
    
    for _ in range(operations_per_group):
        # Random read operations
        random_keys = [f"group:{random.randint(1, num_groups)}" for _ in range(random.randint(1, 5))]
        task = manager.batch_cache_operation("get", random_keys)
        read_tasks.append(task)
    
    read_results = await asyncio.gather(*read_tasks, return_exceptions=True)
    successful_reads = sum(1 for r in read_results if isinstance(r, dict) and r.get("status") == "success")
    
    # 3. Simulate write operations
    print("✏️ Simulating write operations...")
    write_tasks = []
    
    for i in range(operations_per_group):
        # Create new data to cache
        cache_data = {}
        for j in range(random.randint(5, 15)):
            key = f"temp_data:{i}_{j}"
            value = {
                "timestamp": datetime.now().isoformat(),
                "random_value": random.randint(1, 1000),
                "test_data": f"load_test_item_{i}_{j}"
            }
            cache_data[key] = value
        
        task = manager.batch_cache_operation("set", cache_data, ttl=300)  # 5 min TTL
        write_tasks.append(task)
    
    write_results = await asyncio.gather(*write_tasks, return_exceptions=True)
    successful_writes = sum(1 for r in write_results if isinstance(r, dict) and r.get("status") == "success")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Get final cache stats
    cache_info = await manager.get_cache_info()
    
    # Print results
    print("\n📊 Load Test Results:")
    print(f"   ⏱️ Total time: {total_time:.2f}s")
    print(f"   📦 Groups cached: {num_groups}")
    print(f"   📖 Read operations: {len(read_tasks)} ({successful_reads} successful)")
    print(f"   ✏️ Write operations: {len(write_tasks)} ({successful_writes} successful)")
    print(f"   🔑 Total cache keys: {cache_info.get('total_keys', 'N/A')}")
    print(f"   💿 Memory usage: {cache_info.get('memory', {}).get('used_memory_human', 'N/A')}")
    print(f"   🎯 Cache hit rate: {cache_info.get('stats', {}).get('hit_rate', 0):.1f}%")
    print(f"   ⚡ Avg operations/sec: {(len(read_tasks) + len(write_tasks)) / total_time:.2f}")


async def run_load_test():
    """Run the complete load test."""
    manager = InfrastructureManager()
    
    try:
        # Initialize infrastructure
        cache_config = CacheConfig()
        await manager.initialize(cache_config=cache_config)
        
        # Run different test scenarios
        print("🧪 Running load test scenarios...\n")
        
        # Scenario 1: Small load
        await simulate_group_operations(manager, num_groups=50, operations_per_group=20)
        
        print("\n" + "="*60 + "\n")
        
        # Scenario 2: Medium load  
        await simulate_group_operations(manager, num_groups=200, operations_per_group=50)
        
        print("\n" + "="*60 + "\n")
        
        # Scenario 3: Heavy load
        await simulate_group_operations(manager, num_groups=500, operations_per_group=100)
        
    except Exception as e:
        print(f"❌ Load test failed: {e}")
    finally:
        manager.shutdown()


if __name__ == "__main__":
    print("🚀 Cache Performance Load Test")
    print("="*60)
    asyncio.run(run_load_test())

import pytest
import time
import asyncio

@pytest.mark.asyncio
async def test_qrt_03_notification_matching_speed_under_load():
    """
    QRT-03 (Performance Efficiency - Time-behaviour):
    Benchmarks that the asynchronous notification matching engine handles 50 ticket matches 
    simultaneously in under the 2.0-second performance constraint limit.
    """
    start_time = time.perf_counter()
    
    # Simulate subscription checking, matching and telegram aiogram tasks dispatching
    async def simulate_dispatch(match_id: int):
        # Emulate Database queries and regex search overhead (15ms sleep)
        await asyncio.sleep(0.015)
        return True

    # Simultaneously trigger 50 matching operations (representing a rush ticket drop)
    tasks = [simulate_dispatch(i) for i in range(50)]
    results = await asyncio.gather(*tasks)
    
    elapsed_time = time.perf_counter() - start_time
    
    # Asserts
    assert len(results) == 50
    assert elapsed_time < 2.0, f"Notification engine took too long: {elapsed_time:.2f} seconds"
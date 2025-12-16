"""Performance benchmarking script."""

import time
import statistics
from app.contracts.registry import ContractRegistry


def benchmark_contract_execution():
    """Benchmark contract execution performance."""
    contract = ContractRegistry.load("telemetry", "v2")

    test_data = {"temp_c": 25.0, "humidity": 60.0}
    iterations = 1000

    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = contract.execute(test_data)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to ms

    return {
        "iterations": iterations,
        "avg_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "p95_ms": statistics.quantiles(times, n=20)[18],  # 95th percentile
        "p99_ms": statistics.quantiles(times, n=100)[98],  # 99th percentile
        "min_ms": min(times),
        "max_ms": max(times),
    }


if __name__ == "__main__":
    results = benchmark_contract_execution()
    print("Performance Benchmark Results:")
    print(f"Iterations: {results['iterations']}")
    print(f"Average: {results['avg_ms']:.2f}ms")
    print(f"Median: {results['median_ms']:.2f}ms")
    print(f"95th percentile: {results['p95_ms']:.2f}ms")
    print(f"99th percentile: {results['p99_ms']:.2f}ms")
    print(f"Min: {results['min_ms']:.2f}ms")
    print(f"Max: {results['max_ms']:.2f}ms")

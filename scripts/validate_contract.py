"""Validate contract execution."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.contracts.registry import ContractRegistry

def test_telemetry():
    """Test telemetry contract execution."""
    print("Testing Telemetry v2...")
    
    contract = ContractRegistry.load("telemetry", "v2")
    
    # Test cases
    test_cases = [
        {"temp_c": 25.0, "humidity": 60.0}, 
        {"temp_c": -50.0, "humidity": 110.0}, 
        {"temp_c": 150.0},  
    ]
    
    for i, data in enumerate(test_cases):
        print(f"\nTest {i+1}: {data}")
        try:
            result = contract.execute(data)
            print(f"  Result: {result.validated_data}")
            print(f"  Predictions: {result.predictions}")
            print(f"  Metadata: {result.metadata}")
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_telemetry()
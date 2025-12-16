import pytest
from app.contracts.registry import ContractRegistry
from app.contracts.base import DynamicContract


def test_contract_registry_load():
    contract = ContractRegistry.load("telemetry", "v2")
    assert contract.name == "telemetry"
    assert contract.version == "v2"
    assert contract.model is not None


def test_contract_validation():
    contract = ContractRegistry.load("telemetry", "v2")

    # Valid data
    result = contract.execute({"temp_c": 25.0, "humidity": 60.0})
    assert result.validated_data["temp_c"] == 25.0
    assert result.validated_data["humidity"] == 60.0


def test_contract_repair():
    contract = ContractRegistry.load("telemetry", "v2")

    # Out of range data should raise validation errors
    with pytest.raises(Exception):
        result = contract.execute({"temp_c": -50.0, "humidity": 110.0})


def test_contract_defaults():
    contract = ContractRegistry.load("telemetry", "v2")

    # Missing humidity
    result = contract.execute({"temp_c": 25.0})
    assert result.validated_data["humidity"] == 50.0  # Default


def test_drift_detection():
    contract = ContractRegistry.load("telemetry", "v2")

    # Normal value
    result = contract.execute({"temp_c": 25.0, "humidity": 60.0})
    assert result.metadata["drift_detected"] is False

    # Extreme value (potential drift - threshold is 5.0 from expected 22.0)
    result = contract.execute({"temp_c": 30.0, "humidity": 60.0})
    assert result.metadata["drift_detected"] is True

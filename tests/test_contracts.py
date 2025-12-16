import pytest
from app.contracts.registry import ContractRegistry
from app.contracts.base import DynamicContract
from app.contracts.errors import ModelLoadError


def test_contract_registry_load():
    try:
        contract = ContractRegistry.load("telemetry", "v2")
        assert contract.name == "telemetry"
        assert contract.version == "v2"
        assert contract.model is not None
    except ModelLoadError:
        pytest.skip("Model not available - run create_dummy_model.py first")


def test_contract_validation():
    try:
        contract = ContractRegistry.load("telemetry", "v2")

        # Valid data
        result = contract.execute({"temp_c": 25.0, "humidity": 60.0})
        assert result.validated_data["temp_c"] == 25.0
        assert result.validated_data["humidity"] == 60.0
    except ModelLoadError:
        pytest.skip("Model not available - run create_dummy_model.py first")


def test_contract_repair():
    try:
        contract = ContractRegistry.load("telemetry", "v2")

        # Out of range data should be repaired
        result = contract.execute({"temp_c": -50.0, "humidity": 110.0})
        assert result.validated_data["temp_c"] == -40.0  # Clamped
        assert result.validated_data["humidity"] == 100.0  # Clamped
    except ModelLoadError:
        pytest.skip("Model not available - run create_dummy_model.py first")


def test_contract_defaults():
    try:
        contract = ContractRegistry.load("telemetry", "v2")

        # Missing humidity
        result = contract.execute({"temp_c": 25.0})
        assert result.validated_data["humidity"] == 50.0  # Default
    except ModelLoadError:
        pytest.skip("Model not available - run create_dummy_model.py first")


def test_drift_detection():
    try:
        contract = ContractRegistry.load("telemetry", "v2")

        # Normal value
        result = contract.execute({"temp_c": 25.0, "humidity": 60.0})
        assert result.metadata["drift_detected"] is False

        # Extreme value (potential drift - threshold is 5.0 from expected 22.0)
        result = contract.execute({"temp_c": 30.0, "humidity": 60.0})
        assert result.metadata["drift_detected"] is True
    except ModelLoadError:
        pytest.skip("Model not available - run create_dummy_model.py first")

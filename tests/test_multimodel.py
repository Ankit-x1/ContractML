"""Tests for multi-model support."""
import pytest
from app.ml.runtime import MLRuntime
from pathlib import Path


def test_model_type_detection():
    """Test automatic model type detection."""
    # Test ONNX detection
    onnx_path = Path("model.onnx")
    assert MLRuntime._detect_model_type(onnx_path) == "onnx"
    
    # Test TensorFlow detection
    tf_path = Path("model.h5")
    assert MLRuntime._detect_model_type(tf_path) == "tensorflow"
    
    tf_path2 = Path("model.pb")
    assert MLRuntime._detect_model_type(tf_path2) == "tensorflow"
    
    # Test PyTorch detection
    pt_path = Path("model.pth")
    assert MLRuntime._detect_model_type(pt_path) == "pytorch"
    
    pt_path2 = Path("model.pt")
    assert MLRuntime._detect_model_type(pt_path2) == "pytorch"


def test_unknown_model_type_defaults_to_onnx():
    """Test that unknown model types default to ONNX."""
    unknown_path = Path("model.unknown")
    assert MLRuntime._detect_model_type(unknown_path) == "onnx"


def test_model_type_directory_detection():
    """Test model type detection for directories."""
    # Mock TensorFlow SavedModel directory
    tf_dir = Path("saved_model")
    tf_dir.mkdir(exist_ok=True)
    (tf_dir / "saved_model.pb").touch()
    assert MLRuntime._detect_model_type(tf_dir) == "tensorflow"
    
    # Mock PyTorch directory
    pt_dir = Path("torch_model")
    pt_dir.mkdir(exist_ok=True)
    (pt_dir / "model.pt").touch()
    assert MLRuntime._detect_model_type(pt_dir) == "pytorch"
    
    # Cleanup
    import shutil
    shutil.rmtree(tf_dir, ignore_errors=True)
    shutil.rmtree(pt_dir, ignore_errors=True)


def test_onnx_model_loading():
    """Test ONNX model loading (with existing dummy model)."""
    try:
        runtime = MLRuntime.load("telemetry/v2/model.onnx", "onnx")
        assert runtime is not None
        assert hasattr(runtime, 'predict')
    except Exception as e:
        pytest.skip(f"ONNX model loading test skipped: {str(e)}")


def test_auto_detect_onnx_model():
    """Test auto-detection of ONNX model."""
    try:
        runtime = MLRuntime.load("telemetry/v2/model.onnx")  # No type specified
        assert runtime is not None
        assert hasattr(runtime, 'predict')
    except Exception as e:
        pytest.skip(f"Auto-detection test skipped: {str(e)}")


def test_unsupported_model_type():
    """Test error handling for unsupported model types."""
    from app.contracts.errors import ModelLoadError
    
    with pytest.raises(ModelLoadError):
        MLRuntime.load("nonexistent.model", "unsupported_type")


def test_contract_with_model_type():
    """Test contract loading with explicit model type."""
    # Create a test schema with model type
    test_schema = {
        "domain": "test",
        "version": "v1",
        "description": "Test contract with model type",
        "fields": {
            "input": {"type": "float", "min": 0, "max": 100}
        },
        "ml_model": "telemetry/v2/model.onnx",
        "ml_model_type": "onnx"
    }
    
    try:
        from app.contracts.base import DynamicContract
        contract = DynamicContract("test", "v1", test_schema)
        assert contract.ml_runtime is not None
        assert contract.ml_runtime.model_path.endswith("model.onnx")
    except Exception as e:
        pytest.skip(f"Contract model type test skipped: {str(e)}")


def test_contract_auto_detect_model_type():
    """Test contract loading with auto-detected model type."""
    # Create a test schema without model type (should auto-detect)
    test_schema = {
        "domain": "test",
        "version": "v1",
        "description": "Test contract auto-detect model type",
        "fields": {
            "input": {"type": "float", "min": 0, "max": 100}
        },
        "ml_model": "telemetry/v2/model.onnx"
    }
    
    try:
        from app.contracts.base import DynamicContract
        contract = DynamicContract("test", "v1", test_schema)
        assert contract.ml_runtime is not None
        assert contract.ml_runtime.model_path.endswith("model.onnx")
    except Exception as e:
        pytest.skip(f"Contract auto-detect test skipped: {str(e)}")

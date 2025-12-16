"""ML runtime interface with multi-model support."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from app.logging_config import get_logger
from app.contracts.errors import ModelLoadError

logger = get_logger(__name__)


class MLRuntime(ABC):
    """Abstract ML runtime."""
    
    @abstractmethod
    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run inference."""
        pass
    
    @classmethod
    def load(cls, model_path: str, model_type: Optional[str] = None) -> 'MLRuntime':
        """Load model from path with automatic type detection."""
        path = Path(model_path)
        
        # Auto-detect model type if not specified
        if model_type is None:
            model_type = cls._detect_model_type(path)
        
        logger.info("Loading model", path=str(path), type=model_type)
        
        # Load based on type
        if model_type == "onnx":
            from app.ml.onnx import ONNXRuntime
            return ONNXRuntime.load(model_path)
        elif model_type == "tensorflow":
            from app.ml.tensorflow import TensorFlowRuntime
            return TensorFlowRuntime.load(model_path)
        elif model_type == "pytorch":
            from app.ml.pytorch import PyTorchRuntime
            return PyTorchRuntime.load(model_path)
        else:
            raise ModelLoadError(model_path, f"Unsupported model type: {model_type}")
    
    @staticmethod
    def _detect_model_type(path: Path) -> str:
        """Auto-detect model type from file extension and structure."""
        # Check file extension
        if path.suffix == '.onnx':
            return "onnx"
        elif path.suffix in ['.h5', '.pb']:
            return "tensorflow"
        elif path.suffix in ['.pth', '.pt']:
            return "pytorch"
        
        # Check directory structure
        if path.is_dir():
            # Look for TensorFlow SavedModel indicators
            if (path / "saved_model.pb").exists() or (path / "variables").exists():
                return "tensorflow"
            # Look for PyTorch indicators
            elif (path / "model.pt").exists() or (path / "model.pth").exists():
                return "pytorch"
        
        # Default to ONNX for unknown types
        logger.warning("Unknown model type, defaulting to ONNX", path=str(path))
        return "onnx"


class ModelOutput(BaseModel):
    """Structured model output."""
    predictions: np.ndarray
    probabilities: Optional[np.ndarray] = None
    model_version: str
    model_config = ConfigDict(arbitrary_types_allowed=True)
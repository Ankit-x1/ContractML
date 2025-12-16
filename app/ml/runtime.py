"""ML runtime interface."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import numpy as np
from pydantic import BaseModel, ConfigDict


class MLRuntime(ABC):
    """Abstract ML runtime."""
    
    @abstractmethod
    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run inference."""
        pass
    
    @classmethod
    def load(cls, model_path: str) -> 'MLRuntime':
        """Load model from path."""
        # Currently only ONNX
        from app.ml.onnx import ONNXRuntime
        return ONNXRuntime.load(model_path)

class ModelOutput(BaseModel):
    """Structured model output."""
    predictions: np.ndarray
    probabilities: Optional[np.ndarray] = None
    model_version: str
    model_config = ConfigDict(arbitrary_types_allowed=True)
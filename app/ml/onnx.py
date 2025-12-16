"""ONNX runtime backend."""

import onnxruntime as ort
import numpy as np
from typing import Dict, Any
from pathlib import Path
from app.ml.runtime import MLRuntime
from app.performance import timed_cache
from app.config import settings
from app.logging_config import get_logger
from app.contracts.errors import ModelLoadError

logger = get_logger(__name__)


class ONNXRuntime(MLRuntime):
    """ONNX model runtime."""

    def __init__(self, session: ort.InferenceSession, model_path: str):
        self.session = session
        self.model_path = model_path
        self.input_name = session.get_inputs()[0].name
        self.output_name = session.get_outputs()[0].name

    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run ONNX inference."""
        try:
            input_data = input_data.astype(np.float32)

            outputs = self.session.run(
                [self.output_name], {self.input_name: input_data}
            )

            return {
                "predictions": outputs[0].tolist(),
                "model_type": "onnx",
                "output_shape": outputs[0].shape,
            }
        except Exception as e:
            logger.error("ONNX inference failed", path=self.model_path, error=str(e))
            raise ModelLoadError(self.model_path, f"Inference error: {str(e)}")

    @classmethod
    @timed_cache(maxsize=50, ttl=1800)
    def load(cls, model_path: str) -> "ONNXRuntime":
        """Load ONNX model."""
        # Handle both relative and absolute paths
        if Path(model_path).is_absolute():
            full_path = Path(model_path)
        else:
            full_path = Path(settings.models_path) / model_path

        if not full_path.exists():
            raise ModelLoadError(str(full_path), "File not found")

        logger.info("Loading ONNX model", path=str(full_path))

        try:
            session = ort.InferenceSession(
                str(full_path), providers=["CPUExecutionProvider"]
            )
            logger.info("ONNX model loaded successfully", path=str(full_path))
            return cls(session, model_path)
        except Exception as e:
            logger.error("Failed to load ONNX model", path=str(full_path), error=str(e))
            raise ModelLoadError(str(full_path), str(e))

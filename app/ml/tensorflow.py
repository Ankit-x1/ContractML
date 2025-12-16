"""TensorFlow runtime backend."""

import numpy as np
from typing import Dict, Any
from pathlib import Path
from app.ml.runtime import MLRuntime
from app.performance import timed_cache
from app.config import settings
from app.logging_config import get_logger
from app.contracts.errors import ModelLoadError

logger = get_logger(__name__)


class TensorFlowRuntime(MLRuntime):
    """TensorFlow model runtime."""

    def __init__(self, model, model_path: str):
        self.model = model
        self.model_path = model_path

    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run TensorFlow inference."""
        try:
            import tensorflow as tf
            
            # Ensure input is float32
            input_data = input_data.astype(np.float32)
            
            # Run inference
            predictions = self.model(input_data, training=False)
            
            # Convert to numpy if needed
            if hasattr(predictions, 'numpy'):
                predictions = predictions.numpy()
            
            return {
                "predictions": predictions.tolist(),
                "model_type": "tensorflow",
                "output_shape": predictions.shape,
            }
        except Exception as e:
            logger.error("TensorFlow inference failed", path=self.model_path, error=str(e))
            raise ModelLoadError(self.model_path, f"Inference error: {str(e)}")

    @classmethod
    @timed_cache(maxsize=50, ttl=1800)
    def load(cls, model_path: str) -> "TensorFlowRuntime":
        """Load TensorFlow model."""
        import tensorflow as tf
        
        # Handle both relative and absolute paths
        if Path(model_path).is_absolute():
            full_path = Path(model_path)
        else:
            full_path = Path(settings.models_path) / model_path

        if not full_path.exists():
            raise ModelLoadError(str(full_path), "File not found")

        logger.info("Loading TensorFlow model", path=str(full_path))

        try:
            # Load model based on file extension
            if full_path.suffix == '.h5':
                model = tf.keras.models.load_model(str(full_path))
            elif full_path.is_dir():
                model = tf.saved_model.load(str(full_path))
            else:
                # Try to load as SavedModel first, then as Keras
                try:
                    model = tf.saved_model.load(str(full_path))
                except:
                    model = tf.keras.models.load_model(str(full_path))

            logger.info("TensorFlow model loaded successfully", path=str(full_path))
            return cls(model, str(full_path))

        except Exception as e:
            logger.error("Failed to load TensorFlow model", path=str(full_path), error=str(e))
            raise ModelLoadError(str(full_path), f"Load error: {str(e)}")

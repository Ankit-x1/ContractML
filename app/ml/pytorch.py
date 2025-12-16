"""PyTorch runtime backend."""

import numpy as np
from typing import Dict, Any
from pathlib import Path
from app.ml.runtime import MLRuntime
from app.performance import timed_cache
from app.config import settings
from app.logging_config import get_logger
from app.contracts.errors import ModelLoadError

logger = get_logger(__name__)


class PyTorchRuntime(MLRuntime):
    """PyTorch model runtime."""

    def __init__(self, model, model_path: str, device: str = "cpu"):
        self.model = model
        self.model_path = model_path
        self.device = device
        
        # Move model to device and set to eval mode
        self.model.to(device)
        self.model.eval()

    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run PyTorch inference."""
        try:
            import torch
            
            # Convert numpy to tensor
            input_tensor = torch.from_numpy(input_data).float().to(self.device)
            
            # Run inference
            with torch.no_grad():
                predictions = self.model(input_tensor)
            
            # Convert to numpy
            if isinstance(predictions, torch.Tensor):
                predictions = predictions.cpu().numpy()
            
            return {
                "predictions": predictions.tolist(),
                "model_type": "pytorch",
                "output_shape": predictions.shape,
            }
        except Exception as e:
            logger.error("PyTorch inference failed", path=self.model_path, error=str(e))
            raise ModelLoadError(self.model_path, f"Inference error: {str(e)}")

    @classmethod
    @timed_cache(maxsize=50, ttl=1800)
    def load(cls, model_path: str) -> "PyTorchRuntime":
        """Load PyTorch model."""
        import torch
        
        # Handle both relative and absolute paths
        if Path(model_path).is_absolute():
            full_path = Path(model_path)
        else:
            full_path = Path(settings.models_path) / model_path

        if not full_path.exists():
            raise ModelLoadError(str(full_path), "File not found")

        logger.info("Loading PyTorch model", path=str(full_path))

        try:
            # Determine device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            
            # Load model based on file extension
            if full_path.suffix == '.pth' or full_path.suffix == '.pt':
                model = torch.load(str(full_path), map_location=device)
            elif full_path.is_dir():
                # Try to load as a TorchScript model
                model = torch.jit.load(str(full_path) / "model.pt", map_location=device)
            else:
                # Try to load as TorchScript first, then as regular state dict
                try:
                    model = torch.jit.load(str(full_path), map_location=device)
                except:
                    state_dict = torch.load(str(full_path), map_location=device)
                    # This would need the model architecture to be defined
                    # For now, we'll assume it's a complete model
                    model = state_dict

            logger.info("PyTorch model loaded successfully", path=str(full_path), device=device)
            return cls(model, str(full_path), device)

        except Exception as e:
            logger.error("Failed to load PyTorch model", path=str(full_path), error=str(e))
            raise ModelLoadError(str(full_path), f"Load error: {str(e)}")

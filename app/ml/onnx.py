"""ONNX runtime backend."""
import onnxruntime as ort
import numpy as np
from typing import Dict, Any
from app.ml.runtime import MLRuntime

class ONNXRuntime(MLRuntime):
    """ONNX model runtime."""
    
    def __init__(self, session: ort.InferenceSession):
        self.session = session
        self.input_name = session.get_inputs()[0].name
        self.output_name = session.get_outputs()[0].name
    
    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run ONNX inference."""
        input_data = input_data.astype(np.float32)
        
        outputs = self.session.run(
            [self.output_name],
            {self.input_name: input_data}
        )
        
        return {
            "predictions": outputs[0].tolist(),
            "model_type": "onnx",
            "output_shape": outputs[0].shape
        }
    
    @classmethod
    def load(cls, model_path: str) -> 'ONNXRuntime':
        """Load ONNX model."""
        session = ort.InferenceSession(
            model_path,
            providers=['CPUExecutionProvider']
        )
        return cls(session)
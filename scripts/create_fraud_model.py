"""Create dummy fraud detection model for demo."""

import numpy as np
import onnxruntime as ort
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification

# Generate sample data
X, y = make_classification(n_samples=1000, n_features=5, n_classes=2, random_state=42)

# Train model
model = RandomForestClassifier(n_estimators=10, random_state=42)
model.fit(X, y)

# Convert to ONNX
initial_type = [("float_input", FloatTensorType([None, 5]))]
onnx_model = convert_sklearn(model, initial_types=initial_type)

# Save model
import os

os.makedirs("models/fraud/v1", exist_ok=True)
with open("models/fraud/v1/model.onnx", "wb") as f:
    f.write(onnx_model.SerializeToString())

print("Fraud detection model created at models/fraud/v1/model.onnx")

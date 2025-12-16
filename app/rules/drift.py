"""Drift detection engine."""
import numpy as np
from typing import Any, Dict

class DriftDetector:
    """Detect data drift."""
    
    _reference_stats: Dict[str, Dict[str, float]] = {}
    
    @classmethod
    def check_drift(cls, drift_config: Dict[str, Any], value: float) -> bool:
        """Check if value indicates drift."""
        drift_type = drift_config.get("type", "mean_shift")
        
        if drift_type == "mean_shift":
            expected_mean = drift_config.get("expected_mean")
            threshold = drift_config.get("threshold", 2.0)
            
            if expected_mean is not None:
                if abs(value - expected_mean) > threshold:
                    return True
        
        return False
    
    @classmethod
    def update_reference(cls, field: str, values: np.ndarray):
        """Update reference statistics."""
        cls._reference_stats[field] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "count": len(values)
        }
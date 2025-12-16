"""Validation rule engine."""
import re
from typing import Any, Dict

class ValidationRule:
    """Apply validation rules."""
    
    @staticmethod
    def apply(rule_type: str, value: Any, config: Dict[str, Any]):
        """Apply validation rule."""
        if rule_type == "range":
            min_val = config.get("min")
            max_val = config.get("max")
            if min_val is not None and value < min_val:
                raise ValueError(f"Value {value} below minimum {min_val}")
            if max_val is not None and value > max_val:
                raise ValueError(f"Value {value} above maximum {max_val}")
        
        elif rule_type == "regex" and isinstance(value, str):
            pattern = config.get("pattern")
            if pattern and not re.match(pattern, value):
                raise ValueError(f"Value {value} doesn't match pattern {pattern}")
        
        return value
"""Repair rule engine."""
from typing import Any, Dict

class RepairRule:
    """Apply repair rules."""
    
    @staticmethod
    def apply(rule_type: str, value: Any, config: Dict[str, Any]) -> Any:
        """Apply repair rule."""
        if rule_type == "clamp":
            min_val = config.get("min")
            max_val = config.get("max")
            
            if min_val is not None and value < min_val:
                return min_val
            if max_val is not None and value > max_val:
                return max_val
        
        elif rule_type == "default":
            if value is None:
                return config.get("default")
        
        return value
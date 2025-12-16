"""Telemetry v1 → v2 migration."""
from typing import Dict, Any

def migrate(data: Dict[str, Any]) -> Dict[str, Any]:
    """Migrate telemetry v1 to v2."""
    migrated = {}
    
    # Field rename and transformation
    if "temperature" in data:
        migrated["temp_c"] = data["temperature"]
    
    # Add default humidity
    migrated["humidity"] = 50.0
    
    return migrated
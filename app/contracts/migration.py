"""Version migration handlers."""
from typing import Dict, Any, Callable
import importlib.util
from pathlib import Path

class MigrationEngine:
    """Handle contract version migrations."""
    
    @staticmethod
    def migrate(
        data: Dict[str, Any],
        from_version: str,
        to_version: str,
        domain: str
    ) -> Dict[str, Any]:
        """Migrate data between versions."""
        # Look for migration script
        migration_path = Path(f"migrations/{domain}_{from_version}_to_{to_version}.py")
        
        if migration_path.exists():
            # Dynamic import
            spec = importlib.util.spec_from_file_location(
                f"migration_{domain}_{from_version}_to_{to_version}",
                migration_path
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "migrate"):
                return module.migrate(data)
        
        # Default: pass through (forward compatibility)
        return data
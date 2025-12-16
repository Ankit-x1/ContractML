"""YAML → Pydantic loader."""
import yaml
from pathlib import Path
from typing import Dict, Any

class ContractLoader:
    """Load contract definitions from YAML."""
    
    @staticmethod
    def load(domain: str, version: str) -> Dict[str, Any]:
        """Load contract configuration."""
        schema_path = Path(f"schemas/{domain}/{version}.yaml")
        if not schema_path.exists():
            raise FileNotFoundError(f"Contract not found: {domain}/{version}")
        
        with open(schema_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Inject domain and version
        config["domain"] = domain
        config["version"] = version
        
        return config
    
    @staticmethod
    def list_available() -> Dict[str, list]:
        """List all available contracts."""
        base_path = Path("schemas")
        contracts = {}
        
        for domain_dir in base_path.iterdir():
            if domain_dir.is_dir():
                versions = [
                    f.stem for f in domain_dir.glob("*.yaml")
                ]
                contracts[domain_dir.name] = sorted(versions)
        
        return contracts
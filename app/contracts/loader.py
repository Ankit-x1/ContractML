"""YAML → Pydantic loader."""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class ContractLoader:
    """Load contract definitions from YAML."""

    @staticmethod
    def load(domain: str, version: str) -> Dict[str, Any]:
        """Load contract configuration."""
        schema_path = Path(settings.schemas_path) / domain / f"{version}.yaml"
        if not schema_path.exists():
            raise FileNotFoundError(f"Contract not found: {domain}/{version}")

        with open(schema_path, "r") as f:
            config = yaml.safe_load(f)

        # Inject domain and version
        config["domain"] = domain
        config["version"] = version

        logger.debug("Loaded contract config", domain=domain, version=version)
        return config

    @staticmethod
    def list_available() -> List[Dict[str, str]]:
        """List all available contracts."""
        base_path = Path(settings.schemas_path)
        contracts = []

        if not base_path.exists():
            logger.warning("Schemas directory not found", path=settings.schemas_path)
            return contracts

        for domain_dir in base_path.iterdir():
            if domain_dir.is_dir():
                for version_file in domain_dir.glob("*.yaml"):
                    contracts.append(
                        {"domain": domain_dir.name, "version": version_file.stem}
                    )

        logger.debug("Listed available contracts", count=len(contracts))
        return contracts

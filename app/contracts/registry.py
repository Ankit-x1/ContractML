"""Contract discovery and management with migration support."""

from typing import Dict, List, Optional
from pathlib import Path
from app.contracts.loader import ContractLoader
from app.contracts.base import DynamicContract, ContractExecutionResult
from app.contracts.migration import MigrationEngine
from app.contracts.errors import ContractNotFoundError
from app.performance import timed_cache
from app.config import settings
from app.logging_config import get_logger

logger = get_logger(__name__)


class ContractRegistry:
    """Global contract registry with migration support."""
    
    _contracts: Dict[str, Dict[str, DynamicContract]] = {}
    
    @classmethod
    @timed_cache(maxsize=settings.model_cache_size, ttl=600)
    def load(cls, domain: str, version: str) -> DynamicContract:
        """Load or create contract instance."""
        # Check cache
        if domain in cls._contracts and version in cls._contracts[domain]:
            logger.debug("Contract cache hit", domain=domain, version=version)
            return cls._contracts[domain][version]

        logger.info("Loading contract", domain=domain, version=version)

        # Load from YAML
        try:
            config = ContractLoader.load(domain, version)
        except FileNotFoundError:
            raise ContractNotFoundError(domain, version)

        # Create contract
        contract = DynamicContract(domain, version, config)

        # Cache
        if domain not in cls._contracts:
            cls._contracts[domain] = {}
        cls._contracts[domain][version] = contract

        return contract
    
    @classmethod
    def execute_with_migration(
        cls, 
        domain: str, 
        version: str, 
        data: Dict, 
        target_version: Optional[str] = None
    ) -> ContractExecutionResult:
        """Execute contract with automatic migration support."""
        
        # If target version not specified, use the latest
        if target_version is None:
            target_version = MigrationEngine.get_latest_version(domain)
            if target_version is None:
                raise ValueError(f"No versions available for domain: {domain}")
        
        # Load source contract
        source_contract = cls.load(domain, version)
        
        # If versions are the same, execute directly
        if version == target_version:
            return source_contract.execute(data)
        
        # Migrate data
        migrated_data = MigrationEngine.migrate(data, version, target_version, domain)
        
        # Load target contract and execute
        target_contract = cls.load(domain, target_version)
        result = target_contract.execute(migrated_data)
        
        # Add migration metadata
        result.metadata.update({
            "migrated": True,
            "source_version": version,
            "target_version": target_version
        })
        
        return result
    
    @classmethod
    def list_contracts(cls) -> List[Dict[str, str]]:
        """List all available contracts."""
        return ContractLoader.list_available()
    
    @classmethod
    def get_available_versions(cls, domain: str) -> List[str]:
        """Get all available versions for a domain."""
        return MigrationEngine.get_available_versions(domain)
    
    @classmethod
    def get_latest_version(cls, domain: str) -> Optional[str]:
        """Get the latest version for a domain."""
        return MigrationEngine.get_latest_version(domain)
    
    @classmethod
    def clear_cache(cls):
        """Clear contract cache."""
        cls._contracts.clear()
        logger.info("Contract cache cleared")

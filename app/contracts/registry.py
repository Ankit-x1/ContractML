"""Contract discovery and management."""
from typing import Dict
from app.contracts.loader import ContractLoader
from app.contracts.base import DynamicContract

class ContractRegistry:
    """Global contract registry."""
    
    _contracts: Dict[str, Dict[str, DynamicContract]] = {}
    
    @classmethod
    def load(cls, domain: str, version: str) -> DynamicContract:
        """Load or create contract instance."""
        # Check cache
        if domain in cls._contracts and version in cls._contracts[domain]:
            return cls._contracts[domain][version]
        
        # Load from YAML
        config = ContractLoader.load(domain, version)
        
        # Create contract
        contract = DynamicContract(domain, version, config)
        
        # Cache
        if domain not in cls._contracts:
            cls._contracts[domain] = {}
        cls._contracts[domain][version] = contract
        
        return contract
    
    @classmethod
    def clear_cache(cls):
        """Clear contract cache."""
        cls._contracts.clear()
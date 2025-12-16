"""Version migration handlers."""
from typing import Dict, Any, Callable, List, Optional
import importlib.util
from pathlib import Path
from packaging import version
from app.logging_config import get_logger

logger = get_logger(__name__)


class MigrationEngine:
    """Handle contract version migrations."""
    
    @staticmethod
    def get_available_versions(domain: str) -> List[str]:
        """Get all available versions for a domain."""
        schemas_path = Path("schemas") / domain
        if not schemas_path.exists():
            return []
        
        versions = []
        for yaml_file in schemas_path.glob("*.yaml"):
            versions.append(yaml_file.stem)
        
        # Sort versions using semantic versioning
        versions.sort(key=lambda v: version.parse(v.replace('v', '')))
        return versions
    
    @staticmethod
    def get_latest_version(domain: str) -> Optional[str]:
        """Get the latest version for a domain."""
        versions = MigrationEngine.get_available_versions(domain)
        return versions[-1] if versions else None
    
    @staticmethod
    def needs_migration(from_version: str, to_version: str) -> bool:
        """Check if migration is needed."""
        try:
            return version.parse(from_version.replace('v', '')) < version.parse(to_version.replace('v', ''))
        except Exception:
            return from_version != to_version
    
    @staticmethod
    def migrate(
        data: Dict[str, Any],
        from_version: str,
        to_version: str,
        domain: str
    ) -> Dict[str, Any]:
        """Migrate data between versions."""
        logger.info("Starting migration", domain=domain, from_version=from_version, to_version=to_version)
        
        # If versions are the same, no migration needed
        if from_version == to_version:
            return data
        
        # Check if migration is needed (version ordering)
        if not MigrationEngine.needs_migration(from_version, to_version):
            logger.warning("Downgrade requested, using passthrough", from_version=from_version, to_version=to_version)
            return data
        
        # Try direct migration
        migrated_data = MigrationEngine._try_direct_migration(data, from_version, to_version, domain)
        
        # If direct migration failed, try step-by-step migration
        if migrated_data is None:
            migrated_data = MigrationEngine._try_step_migration(data, from_version, to_version, domain)
        
        # If all migrations failed, use passthrough
        if migrated_data is None:
            logger.warning("No migration path found, using passthrough", domain=domain, from_version=from_version, to_version=to_version)
            return data
        
        logger.info("Migration completed successfully", domain=domain, from_version=from_version, to_version=to_version)
        return migrated_data
    
    @staticmethod
    def _try_direct_migration(
        data: Dict[str, Any],
        from_version: str,
        to_version: str,
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """Try direct migration from one version to another."""
        migration_path = Path(f"migrations/{domain}_{from_version}_to_{to_version}.py")
        
        if migration_path.exists():
            try:
                return MigrationEngine._execute_migration_script(migration_path, data)
            except Exception as e:
                logger.error("Direct migration failed", migration_path=str(migration_path), error=str(e))
        
        return None
    
    @staticmethod
    def _try_step_migration(
        data: Dict[str, Any],
        from_version: str,
        to_version: str,
        domain: str
    ) -> Optional[Dict[str, Any]]:
        """Try step-by-step migration through intermediate versions."""
        available_versions = MigrationEngine.get_available_versions(domain)
        
        # Find path from from_version to to_version
        try:
            from_idx = available_versions.index(from_version)
            to_idx = available_versions.index(to_version)
        except ValueError:
            return None
        
        if from_idx >= to_idx:
            return None
        
        current_data = data
        current_version = from_version
        
        # Step through each intermediate version
        for i in range(from_idx, to_idx):
            next_version = available_versions[i + 1]
            
            migrated_data = MigrationEngine._try_direct_migration(
                current_data, current_version, next_version, domain
            )
            
            if migrated_data is None:
                logger.error("Step migration failed", from_version=current_version, to_version=next_version)
                return None
            
            current_data = migrated_data
            current_version = next_version
        
        return current_data
    
    @staticmethod
    def _execute_migration_script(migration_path: Path, data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a migration script."""
        spec = importlib.util.spec_from_file_location(
            f"migration_{migration_path.stem}",
            migration_path
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        if hasattr(module, "migrate"):
            result = module.migrate(data)
            logger.debug("Migration script executed", path=str(migration_path))
            return result
        else:
            raise ValueError(f"Migration script {migration_path} missing migrate function")
    
    @staticmethod
    def create_migration_script(
        domain: str,
        from_version: str,
        to_version: str,
        migration_function: Callable[[Dict[str, Any]], Dict[str, Any]]
    ) -> Path:
        """Create a migration script programmatically."""
        migrations_dir = Path("migrations")
        migrations_dir.mkdir(exist_ok=True)
        
        script_path = migrations_dir / f"{domain}_{from_version}_to_{to_version}.py"
        
        script_content = f'''"""Auto-generated migration script for {domain} {from_version} -> {to_version}."""

def migrate(data):
    """Migrate data from {from_version} to {to_version}."""
    # TODO: Implement migration logic
    # This is a template - replace with actual migration logic
    
    # Example migration:
    # if "old_field" in data:
    #     data["new_field"] = data["old_field"]
    #     del data["old_field"]
    
    return data
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        logger.info("Migration script created", path=str(script_path))
        return script_path
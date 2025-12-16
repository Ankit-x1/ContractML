"""Contract execution errors."""
from typing import Optional

class ContractError(Exception):
    """Base contract error."""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class ValidationError(ContractError):
    """Validation failed."""

class RepairError(ContractError):
    """Repair failed."""

class MigrationError(ContractError):
    """Migration failed."""

class DriftError(ContractError):
    """Drift detected."""
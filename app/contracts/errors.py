"""Custom exceptions for ContractML."""

from typing import Optional


class ContractMLError(Exception):
    """Base exception for ContractML."""

    pass


class ContractNotFoundError(ContractMLError):
    """Raised when a contract is not found."""

    def __init__(self, domain: str, version: str):
        self.domain = domain
        self.version = version
        super().__init__(f"Contract {domain}/{version} not found")


class ValidationError(ContractMLError):
    """Raised when validation fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(f"Validation error: {message}")


class RepairError(ContractMLError):
    """Raised when data repair fails."""

    def __init__(self, message: str, field: Optional[str] = None):
        self.field = field
        super().__init__(f"Repair error: {message}")


class ModelLoadError(ContractMLError):
    """Raised when ML model fails to load."""

    def __init__(self, model_path: str, reason: Optional[str] = None):
        self.model_path = model_path
        self.reason = reason
        message = f"Failed to load model: {model_path}"
        if reason:
            message += f" ({reason})"
        super().__init__(message)


class DriftDetectionError(ContractMLError):
    """Raised when drift detection fails."""

    def __init__(self, field: str, reason: str):
        self.field = field
        super().__init__(f"Drift detection failed for {field}: {reason}")


class ConfigurationError(ContractMLError):
    """Raised when configuration is invalid."""

    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class MigrationError(ContractMLError):
    """Raised when contract migration fails."""

    def __init__(self, from_version: str, to_version: str, reason: str):
        self.from_version = from_version
        self.to_version = to_version
        super().__init__(
            f"Migration from {from_version} to {to_version} failed: {reason}"
        )

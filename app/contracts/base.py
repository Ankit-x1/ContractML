"""Dynamic Pydantic contract base."""
from typing import Any, Dict, Optional
from pydantic import BaseModel, create_model, ConfigDict
from pydantic.functional_validators import model_validator
import numpy as np

from app.rules.validation import ValidationRule
from app.rules.repair import RepairRule
from app.rules.drift import DriftDetector

class ContractExecutionResult(BaseModel):
    """Structured execution result."""
    validated_data: Dict[str, Any]
    predictions: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]
    model_config = ConfigDict(arbitrary_types_allowed=True)

class DynamicContract:
    """Runtime-executable contract."""
    
    def __init__(self, name: str, version: str, config: Dict[str, Any]):
        self.name = name
        self.version = version
        self.config = config
        self.model = self._build_model()
        self.ml_runtime = None
        
        # Load ML model if specified
        if "ml_model" in config:
            from app.ml.runtime import MLRuntime
            self.ml_runtime = MLRuntime.load(config["ml_model"])
    
    def _build_model(self):
        """Dynamically create Pydantic model from config."""
        field_definitions = {}
        
        for field_name, field_config in self.config.get("fields", {}).items():
            field_type = self._parse_type(field_config.get("type", "float"))
            field_definitions[field_name] = (
                field_type,
                self._create_field_info(field_config)
            )
        
        # Create model with strict config
        model = create_model(
            f"{self.name}_{self.version}",
            __config__=ConfigDict(
                extra="forbid",
                validate_assignment=True
            ),
            **field_definitions
        )
        
        # Attach rules as validators
        model = self._attach_rules(model)
        return model
    
    def _parse_type(self, type_str: str):
        """Parse type string to Python type."""
        type_map = {
            "float": float,
            "int": int,
            "str": str,
            "bool": bool
        }
        return type_map.get(type_str, float)
    
    def _create_field_info(self, config: Dict[str, Any]):
        """Create FieldInfo with constraints."""
        from pydantic import Field
        
        constraints = {}
        if "min" in config:
            constraints["ge"] = config["min"]
        if "max" in config:
            constraints["le"] = config["max"]
        
        return Field(
            default=config.get("default"),
            description=config.get("description", ""),
            **constraints
        )
    
    def _attach_rules(self, model):
        """Attach validation and repair rules."""
        
        @model_validator(mode="before")
        def apply_rules(cls, data: Dict[str, Any]):
            # Apply repair rules
            for field_name, field_config in self.config.get("fields", {}).items():
                if field_name in data and "repair" in field_config:
                    data[field_name] = RepairRule.apply(
                        field_config["repair"],
                        data[field_name],
                        field_config
                    )
            
            # Apply validation rules
            for field_name, field_config in self.config.get("fields", {}).items():
                if field_name in data and "validation" in field_config:
                    ValidationRule.apply(
                        field_config["validation"],
                        data[field_name],
                        field_config
                    )
            
            return data
        
        # Attach the validator
        model.model_validator = classmethod(apply_rules)
        return model
    
    def execute(self, data: Dict[str, Any]) -> ContractExecutionResult:
        """Execute the full contract pipeline."""
        # Validate and repair
        validated = self.model(**data)
        
        # Prepare ML inference
        predictions = None
        if self.ml_runtime:
            # Convert to numpy array in correct order
            input_data = np.array([
                getattr(validated, field_name)
                for field_name in self.config.get("fields", {}).keys()
            ], dtype=np.float32).reshape(1, -1)
            
            predictions = self.ml_runtime.predict(input_data)
        
        # Check for drift
        metadata = {"drift_detected": False}
        for field_name, field_config in self.config.get("fields", {}).items():
            if "drift" in field_config:
                value = getattr(validated, field_name)
                if DriftDetector.check_drift(field_config["drift"], value):
                    metadata["drift_detected"] = True
                    metadata[f"{field_name}_drift"] = True
        
        return ContractExecutionResult(
            validated_data=validated.model_dump(),
            predictions=predictions,
            metadata=metadata
        )
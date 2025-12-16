"""Dynamic prediction endpoint with migration support."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.contracts.registry import ContractRegistry
from app.contracts.migration import MigrationEngine
from app.ml.runtime import MLRuntime

router = APIRouter()

class PredictRequest(BaseModel):
    domain: str = "telemetry"
    version: str = "v2"
    payload: dict
    target_version: Optional[str] = None

class MigrationRequest(BaseModel):
    domain: str
    from_version: str
    to_version: str
    data: Dict[str, Any]

@router.post("/{domain}/{version}")
async def predict(domain: str, version: str, request: dict, target_version: Optional[str] = None):
    """Dynamic contract execution endpoint with migration support."""
    try:
        # Use migration-aware execution if target version specified
        if target_version:
            result = ContractRegistry.execute_with_migration(domain, version, request, target_version)
        else:
            contract = ContractRegistry.load(domain, version)
            result = contract.execute(request)
        
        return {
            "status": "success",
            "domain": domain,
            "version": version,
            "data": result.validated_data,
            "predictions": result.predictions,
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/migrate")
async def migrate_data(request: MigrationRequest):
    """Migrate data between contract versions."""
    try:
        migrated_data = MigrationEngine.migrate(
            request.data, 
            request.from_version, 
            request.to_version, 
            request.domain
        )
        
        return {
            "status": "success",
            "domain": request.domain,
            "from_version": request.from_version,
            "to_version": request.to_version,
            "original_data": request.data,
            "migrated_data": migrated_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{domain}/versions")
async def get_versions(domain: str):
    """Get all available versions for a domain."""
    try:
        versions = ContractRegistry.get_available_versions(domain)
        latest = ContractRegistry.get_latest_version(domain)
        
        return {
            "domain": domain,
            "versions": versions,
            "latest_version": latest,
            "total_versions": len(versions)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{domain}/{version}/execute-with-migration")
async def execute_with_migration(
    domain: str, 
    version: str, 
    request: dict,
    target_version: Optional[str] = None
):
    """Execute contract with automatic migration to latest version."""
    try:
        result = ContractRegistry.execute_with_migration(domain, version, request, target_version)
        
        return {
            "status": "success",
            "domain": domain,
            "source_version": version,
            "target_version": result.metadata.get("target_version"),
            "migrated": result.metadata.get("migrated", False),
            "data": result.validated_data,
            "predictions": result.predictions,
            "metadata": result.metadata
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ModelLoadError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

"""Single dynamic endpoint."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.contracts.registry import ContractRegistry
from app.ml.runtime import MLRuntime

router = APIRouter()

class PredictRequest(BaseModel):
    domain: str = "telemetry"
    version: str = "v2"
    payload: dict

@router.post("/{domain}/{version}")
async def predict(domain: str, version: str, request: dict):
    """Dynamic contract execution endpoint."""
    try:
        # Load contract
        contract = ContractRegistry.load(domain, version)
        
        # Execute: validate → repair → migrate → infer
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
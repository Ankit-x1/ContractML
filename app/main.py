"""FastAPI bootstrap - transport adapter only."""

from fastapi import FastAPI
from app.api.predict import router as predict_router

app = FastAPI(
    title="ContractML",
    description="Runtime-executable Pydantic contracts for ML inference",
    version="0.1.0",
)

app.include_router(predict_router, prefix="/predict")


@app.get("/health")
async def health():
    return {"status": "healthy", "engine": "contract-execution"}


@app.get("/metrics")
async def metrics():
    from app.contracts.registry import ContractRegistry
    import time
    from collections import defaultdict

    # Basic metrics
    start_time = time.time()
    contracts = ContractRegistry.list_contracts()
    load_time = time.time() - start_time

    return {
        "contracts_loaded": len(contracts),
        "load_time_ms": round(load_time * 1000, 2),
        "domains": list(set(c["domain"] for c in contracts)),
        "versions": defaultdict(
            list,
            **{
                domain: [c["version"] for c in contracts if c["domain"] == domain]
                for domain in set(c["domain"] for c in contracts)
            },
        ),
    }

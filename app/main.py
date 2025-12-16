"""FastAPI bootstrap - transport adapter only."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any
from app.api.predict import router as predict_router
from app.config import settings
from app.logging_config import configure_logging, get_logger
from app.security import RateLimitMiddleware, SecurityHeadersMiddleware
from app.performance import performance_monitor, monitor_performance

# Configure logging
configure_logging(settings.log_level, settings.log_format)
logger = get_logger(__name__)

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

# Add middleware
if settings.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

app.include_router(predict_router, prefix="/predict")


@app.get("/health")
@monitor_performance("health_check")
async def health() -> Dict[str, str]:
    logger.info("Health check requested")
    return {"status": "healthy", "engine": "contract-execution"}


@app.get("/metrics")
@monitor_performance("metrics")
async def metrics() -> Dict[str, Any]:
    from app.contracts.registry import ContractRegistry
    import time
    from collections import defaultdict

    logger.info("Metrics requested")

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
        "performance": performance_monitor.get_all_stats(),
    }

# Developer Guide

## Architecture

ContractML follows a modular architecture:

```
app/
├── api/          # FastAPI endpoints
├── contracts/    # Dynamic contract system
├── ml/           # ML runtime and ONNX handling
├── rules/        # Validation, repair, drift detection
├── config.py     # Configuration management
└── logging_config.py  # Structured logging
```

## Core Components

### Dynamic Contracts

Contracts are defined in YAML and loaded at runtime:

```yaml
domain: telemetry
version: v2
fields:
  temperature:
    type: float
    min: -40
    max: 125
    repair: clamp
ml_model: models/telemetry/v2/model.onnx
```

### Contract Registry

The registry manages contract loading and caching:

```python
from app.contracts.registry import ContractRegistry

# Load contract
contract = ContractRegistry.load("telemetry", "v2")

# Execute pipeline
result = contract.execute(data)
```

### ML Runtime

Handles ONNX model inference:

```python
from app.ml.runtime import MLRuntime

# Load model
runtime = MLRuntime.load("models/telemetry/v2/model.onnx")

# Make prediction
predictions = runtime.predict(input_data)
```

## Development Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/Ankit-x1/ContractML.git
   cd ContractML
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```

2. **Create Test Models**
   ```bash
   python scripts/create_dummy_model.py
   python scripts/create_fraud_model.py
   ```

3. **Run Development Server**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## Adding New Contracts

1. **Create Schema**
   ```yaml
   # schemas/mydomain/v1.yaml
   domain: mydomain
   version: v1
   description: My custom contract
   
   fields:
     field1:
       type: float
       min: 0
       max: 100
       repair: clamp
   
   ml_model: models/mydomain/v1/model.onnx
   ```

2. **Create Model (Optional)**
   ```python
   # scripts/create_mydomain_model.py
   # Generate ONNX model for your domain
   ```

3. **Write Tests**
   ```python
   # tests/test_mydomain.py
   def test_mydomain_contract():
       contract = ContractRegistry.load("mydomain", "v1")
       result = contract.execute({"field1": 50.0})
       assert result.validated_data["field1"] == 50.0
   ```

## Configuration

Environment variables are prefixed with `CONTRACTML_`:

```bash
# .env
CONTRACTML_LOG_LEVEL=DEBUG
CONTRACTML_API_PORT=8001
CONTRACTML_MODEL_CACHE_SIZE=200
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run performance tests
pytest tests/test_integration.py::TestPerformance
```

## Logging

Structured logging is configured automatically:

```python
from app.logging_config import get_logger

logger = get_logger(__name__)
logger.info("Processing request", request_id="123")
```

## Error Handling

Custom exceptions for different error types:

```python
from app.contracts.errors import ValidationError, ModelLoadError

try:
    contract = ContractRegistry.load("invalid", "v1")
except ContractNotFoundError as e:
    logger.error("Contract not found", domain=e.domain, version=e.version)
```

## Performance Optimization

1. **Model Caching**: Models are cached in memory after first load
2. **Lazy Loading**: Contracts loaded only when needed
3. **Type Hints**: Full type annotations for better performance
4. **Async Support**: FastAPI handles concurrent requests

## Deployment

### Docker
```bash
docker build -t contractml .
docker run -p 8000:8000 contractml
```

### Docker Compose
```bash
docker-compose up -d
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Monitoring

- `/health` - Service health
- `/metrics` - Performance metrics
- Structured logs with request tracing

## Contributing

1. Fork the repository
2. Create feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit pull request

## Code Quality

- **Linting**: `ruff check .`
- **Formatting**: `black .`
- **Type Checking**: `mypy app/`
- **Testing**: `pytest`

All checks run automatically in CI/CD pipeline.
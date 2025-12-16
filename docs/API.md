# API Documentation

## Overview

ContractML provides a RESTful API for executing dynamic Pydantic contracts with ML inference capabilities.

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

Check if the service is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "engine": "contract-execution"
}
```

### Metrics

Get service metrics and statistics.

**Endpoint:** `GET /metrics`

**Response:**
```json
{
  "contracts_loaded": 2,
  "load_time_ms": 1.23,
  "domains": ["telemetry", "fraud"],
  "versions": {
    "telemetry": ["v1", "v2"],
    "fraud": ["v1"]
  }
}
```

### Execute Contract

Execute a contract with validation, repair, and ML inference.

**Endpoint:** `POST /predict/{domain}/{version}`

**Path Parameters:**
- `domain` (string): Contract domain
- `version` (string): Contract version

**Request Body:**
```json
{
  "field1": "value1",
  "field2": 123.45
}
```

**Response:**
```json
{
  "status": "success",
  "domain": "telemetry",
  "version": "v2",
  "data": {
    "field1": "value1",
    "field2": 123.45
  },
  "predictions": {
    "output": [0.85]
  },
  "metadata": {
    "drift_detected": false
  }
}
```

## Error Responses

### 404 Not Found
```json
{
  "detail": "Contract telemetry/v999 not found"
}
```

### 422 Validation Error
```json
{
  "detail": "Validation error: field1 is required"
}
```

### 503 Service Unavailable
```json
{
  "detail": "Failed to load model: models/telemetry/v2/model.onnx (File not found)"
}
```

## Usage Examples

### Basic Request
```bash
curl -X POST "http://localhost:8000/predict/telemetry/v2" \
  -H "Content-Type: application/json" \
  -d '{"temp_c": 25.0, "humidity": 60.0}'
```

### With Auto-Repair
```bash
curl -X POST "http://localhost:8000/predict/telemetry/v2" \
  -H "Content-Type: application/json" \
  -d '{"temp_c": -50.0, "humidity": 110.0}'
```

### Fraud Detection
```bash
curl -X POST "http://localhost:8000/predict/fraud/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_amount": 150.00,
    "transaction_time": 3600,
    "merchant_category": "electronics",
    "user_age": 25,
    "risk_score": 0.3
  }'
```

## Rate Limiting

Currently no rate limiting is implemented. This can be added using FastAPI middleware.

## Authentication

Currently no authentication is required. This can be added using OAuth2 or API keys.

## SDK Examples

### Python
```python
import requests

response = requests.post(
    "http://localhost:8000/predict/telemetry/v2",
    json={"temp_c": 25.0, "humidity": 60.0}
)
result = response.json()
print(result["predictions"])
```

### JavaScript
```javascript
const response = await fetch('http://localhost:8000/predict/telemetry/v2', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ temp_c: 25.0, humidity: 60.0 })
});
const result = await response.json();
console.log(result.predictions);
```
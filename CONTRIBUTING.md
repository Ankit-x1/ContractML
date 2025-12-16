# Contributing to ContractML

## Development Setup

1. Fork the repository at https://github.com/Ankit-x1/ContractML
2. Clone your fork:
   ```bash
   git clone https://github.com/yourusername/ContractML.git
   cd ContractML
   ```

3. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

4. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=app
```

## Code Quality

Run linting and formatting:
```bash
ruff check .
black .
mypy app/
```

## Adding New Contracts

1. Create YAML schema in `schemas/{domain}/{version}.yaml`
2. Add ONNX model to `models/{domain}/{version}/` if needed
3. Write tests in `tests/`
4. Update documentation

## Submitting Changes

1. Create feature branch: `git checkout -b feature-name`
2. Commit changes: `git commit -m "Add feature"`
3. Push to fork: `git push origin feature-name`
4. Create pull request

## Project Structure

```
app/
├── api/          # FastAPI endpoints
├── contracts/    # Dynamic contract system
├── ml/           # ML runtime and ONNX handling
└── rules/        # Validation, repair, drift detection

schemas/          # YAML contract definitions
models/           # ONNX model files
tests/            # Test suite
```
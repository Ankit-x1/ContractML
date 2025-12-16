FROM python:3.11-slim as builder

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir wheel && \
    pip install --no-cache-dir -e .

FROM python:3.11-slim as runtime

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY app/ ./app/
COPY schemas/ ./schemas/
COPY models/ ./models/
COPY migrations/ ./migrations/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
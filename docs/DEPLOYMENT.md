# Deployment Guide

## Production Deployment

### Docker Deployment

1. **Build Image**
   ```bash
   docker build -t contractml:latest .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name contractml \
     -p 8000:8000 \
     -v $(pwd)/schemas:/app/schemas \
     -v $(pwd)/models:/app/models \
     contractml:latest
   ```

3. **With Environment Variables**
   ```bash
   docker run -d \
     --name contractml \
     -p 8000:8000 \
     -e CONTRACTML_LOG_LEVEL=INFO \
     -e CONTRACTML_API_PORT=8000 \
     -v $(pwd)/schemas:/app/schemas \
     -v $(pwd)/models:/app/models \
     contractml:latest
   ```

### Docker Compose

1. **Basic Setup**
   ```bash
   docker-compose up -d
   ```

2. **Production Configuration**
   ```yaml
   version: '3.8'
   services:
     contractml:
       build: .
       ports:
         - "8000:8000"
       environment:
         - CONTRACTML_LOG_LEVEL=INFO
         - CONTRACTML_API_HOST=0.0.0.0
       volumes:
         - ./schemas:/app/schemas:ro
         - ./models:/app/models:ro
       restart: unless-stopped
       healthcheck:
         test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
         interval: 30s
         timeout: 10s
         retries: 3
   ```

### Kubernetes Deployment

1. **Deployment Manifest**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: contractml
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: contractml
     template:
       metadata:
         labels:
           app: contractml
       spec:
         containers:
         - name: contractml
           image: ghcr.io/ankit-x1/contractml:latest
           ports:
           - containerPort: 8000
           env:
           - name: CONTRACTML_LOG_LEVEL
             value: "INFO"
           volumeMounts:
           - name: schemas
             mountPath: /app/schemas
             readOnly: true
           - name: models
             mountPath: /app/models
             readOnly: true
         volumes:
         - name: schemas
           configMap:
             name: contractml-schemas
         - name: models
           persistentVolumeClaim:
             claimName: contractml-models
   ```

2. **Service Manifest**
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: contractml-service
   spec:
     selector:
       app: contractml
     ports:
     - protocol: TCP
       port: 80
       targetPort: 8000
     type: LoadBalancer
   ```

## Environment Configuration

### Production Environment Variables

```bash
# API Configuration
CONTRACTML_API_HOST=0.0.0.0
CONTRACTML_API_PORT=8000

# Logging
CONTRACTML_LOG_LEVEL=INFO
CONTRACTML_LOG_FORMAT=json

# Performance
CONTRACTML_MAX_REQUEST_SIZE=10485760
CONTRACTML_REQUEST_TIMEOUT=30

# Security
CONTRACTML_ENABLE_CORS=true
CONTRACTML_CORS_ORIGINS=["https://yourdomain.com"]

# Model Settings
CONTRACTML_MODEL_CACHE_SIZE=100
CONTRACTML_MODEL_TIMEOUT=10
```

## Monitoring and Health Checks

### Health Check Endpoint

```bash
curl http://localhost:8000/health
```

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

### Monitoring Setup

1. **Prometheus Configuration**
   ```yaml
   scrape_configs:
     - job_name: 'contractml'
       static_configs:
         - targets: ['localhost:8000']
       metrics_path: '/metrics'
   ```

2. **Grafana Dashboard**
   - Request latency
   - Error rates
   - Contract execution metrics
   - Model inference performance

## Scaling Considerations

### Horizontal Scaling

- Deploy multiple instances behind load balancer
- Use Redis for shared caching (if implemented)
- Consider database for contract storage

### Performance Optimization

1. **Model Optimization**
   - Quantize ONNX models
   - Use TensorRT for GPU acceleration
   - Implement model versioning

2. **Caching Strategy**
   - Cache contract definitions
   - Cache model predictions
   - Use CDN for static assets

3. **Resource Management**
   - Set appropriate memory limits
   - Monitor CPU usage
   - Implement request timeouts

## Security Considerations

### Network Security

1. **Firewall Rules**
   ```bash
   # Allow only necessary ports
   ufw allow 8000/tcp
   ufw enable
   ```

2. **HTTPS Setup**
   ```bash
   # Use reverse proxy with SSL
   # nginx or traefik recommended
   ```

### Application Security

1. **Environment Variables**
   - Never commit secrets to repository
   - Use secret management systems
   - Rotate API keys regularly

2. **Input Validation**
   - Contracts provide schema validation
   - Additional sanitization if needed
   - Rate limiting implementation

## Backup and Recovery

### Data Backup

1. **Schema Definitions**
   ```bash
   tar -czf schemas-backup-$(date +%Y%m%d).tar.gz schemas/
   ```

2. **Model Files**
   ```bash
   tar -czf models-backup-$(date +%Y%m%d).tar.gz models/
   ```

### Disaster Recovery

1. **Multi-region deployment**
2. **Automated failover**
3. **Regular backup testing**
4. **Documentation restoration procedures**

## Troubleshooting

### Common Issues

1. **Model Loading Errors**
   ```bash
   # Check model file permissions
   ls -la models/telemetry/v2/
   
   # Verify ONNX model format
   python -c "import onnx; onnx.load('models/telemetry/v2/model.onnx')"
   ```

2. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats contractml
   
   # Check model sizes
   du -sh models/*/
   ```

3. **Performance Issues**
   ```bash
   # Check response times
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/health
   
   # Monitor system resources
   top -p $(pgrep -f uvicorn)
   ```

### Log Analysis

```bash
# View application logs
docker logs contractml

# Filter for errors
docker logs contractml 2>&1 | grep ERROR

# Monitor in real-time
docker logs -f contractml
```

## Maintenance

### Regular Tasks

1. **Update Dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Rotate Logs**
   - Configure log rotation
   - Archive old logs
   - Monitor disk space

3. **Performance Monitoring**
   - Review metrics regularly
   - Identify bottlenecks
   - Optimize as needed

### Updates and Patches

1. **Application Updates**
   ```bash
   docker pull ghcr.io/ankit-x1/contractml:latest
   docker-compose up -d
   ```

2. **Schema Updates**
   - Test new contracts thoroughly
   - Use versioning for compatibility
   - Monitor for breaking changes
# Deployment Guide

## System Prerequisites

## Environment Configuration

### Production Environment Variables

## 1. Backend Environment Variables

```env
# Application Settings
DEBUG=false
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database Configuration
DATABASE_URL=postgresql://user:password@host:5432/veda_base
REDIS_URL=redis://host:6379/0

# Security Settings
API_KEY=your-production-api-key
JWT_SECRET=your-jwt-secret
ALLOWED_ORIGINS=https://your-domain.com

# AI Service Configuration
GROQ_API_KEY=your-groq-api-key

# Monitoring Settings
LOGFIRE_TOKEN=your-logfire-token
```

## 2. Frontend Environment Variables

```env
NEXT_PUBLIC_API_URL=https://api.your-domain.com
NEXT_PUBLIC_WS_URL=wss://api.your-domain.com
NEXT_PUBLIC_ENVIRONMENT=production
```

## Docker Setup

### Docker Build Configuration

```dockerfile
# Backend Dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY alembic/ alembic/
COPY alembic.ini .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Frontend Dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

CMD ["npm", "start"]
```

### Docker Service Configuration

```yaml
version: '3.8'

services:
  api:
    build:
      context: .
      dockerfile: docker/Dockerfile.api
    ports:
      - "8000:8000"
    env_file:
      - .env.production
    depends_on:
      - db
      - redis

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    env_file:
      - frontend/.env.production

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=veda_base

  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Kubernetes Setup

### K8s Resource Configuration

```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: veda-base

# secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: veda-base-secrets
  namespace: veda-base
type: Opaque
data:
  DATABASE_URL: base64_encoded_url
  REDIS_URL: base64_encoded_url
  API_KEY: base64_encoded_key
  JWT_SECRET: base64_encoded_secret
```

### K8s Service Configuration

```yaml
# api-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: veda-base-api
  namespace: veda-base
spec:
  replicas: 3
  selector:
    matchLabels:
      app: veda-base-api
  template:
    metadata:
      labels:
        app: veda-base-api
    spec:
      containers:
        - name: api
          image: your-registry/veda-base-api:latest
          ports:
            - containerPort: 8000
          envFrom:
            - secretRef:
                name: veda-base-secrets
          resources:
            requests:
              cpu: "500m"
              memory: "512Mi"
            limits:
              cpu: "1000m"
              memory: "1Gi"

# frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: veda-base-frontend
  namespace: veda-base
spec:
  replicas: 2
  selector:
    matchLabels:
      app: veda-base-frontend
  template:
    metadata:
      labels:
        app: veda-base-frontend
    spec:
      containers:
        - name: frontend
          image: your-registry/veda-base-frontend:latest
          ports:
            - containerPort: 3000
```

### Services and Ingress

```yaml
# services.yaml
apiVersion: v1
kind: Service
metadata:
  name: veda-base-api
  namespace: veda-base
spec:
  selector:
    app: veda-base-api
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP

---
apiVersion: v1
kind: Service
metadata:
  name: veda-base-frontend
  namespace: veda-base
spec:
  selector:
    app: veda-base-frontend
  ports:
    - port: 80
      targetPort: 3000
  type: ClusterIP

# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: veda-base-ingress
  namespace: veda-base
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  rules:
    - host: api.your-domain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: veda-base-api
                port:
                  number: 80
    - host: your-domain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: veda-base-frontend
                port:
                  number: 80
```

## Database Operations

```bash
# Run migrations
alembic upgrade head

# Create backup
pg_dump -U user -d veda_base > backup.sql

# Restore from backup
psql -U user -d veda_base < backup.sql
```

## Monitoring Configuration

### Prometheus Setup

```yaml
# prometheus.yaml
scrape_configs:
  - job_name: 'veda-base-api'
    scrape_interval: 15s
    static_configs:
      - targets: ['veda-base-api:8000']
```

### Grafana Setup

1. Import dashboard template
2. Configure data source
3. Set up alerts

## Pipeline Configuration

### CI/CD Setup

```yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build images
        run: |
          docker build -t api ./backend
          docker build -t frontend ./frontend

      - name: Push to registry
        run: |
          docker tag api ${{ secrets.REGISTRY }}/veda-base-api
          docker tag frontend ${{ secrets.REGISTRY }}/veda-base-frontend
          docker push ${{ secrets.REGISTRY }}/veda-base-api
          docker push ${{ secrets.REGISTRY }}/veda-base-frontend

      - name: Deploy to Kubernetes
        run: |
          kubectl apply -f k8s/
```

## SSL Setup

### Certificate Configuration

```bash
# Install certbot
apt-get install certbot

# Generate certificate
certbot certonly --webroot -w /var/www/html -d your-domain.com

# Auto-renewal
certbot renew --dry-run
```

## System Backups

1. Database backups:
   - Daily automated backups
   - Weekly full backups
   - Monthly archives

2. File backups:
   - Document storage backup
   - Configuration backup
   - Log files backup

## Security Guidelines

- [ ] SSL certificates installed
- [ ] Firewall rules configured
- [ ] Security headers set
- [ ] Rate limiting enabled
- [ ] API keys rotated
- [ ] Monitoring alerts set
- [ ] Backup system tested
- [ ] Access logs enabled
- [ ] Error reporting configured

## System Troubleshooting

### Common Production Issues

1. Database connection issues:
   - Check connection string
   - Verify network access
   - Check credentials

2. WebSocket connection fails:
   - Verify WebSocket URL
   - Check SSL configuration
   - Confirm proxy settings

3. Performance issues:
   - Monitor resource usage
   - Check database indexes
   - Review caching strategy

## System Maintenance

### Scheduled Tasks

1. Daily:
   - Monitor error logs
   - Check system health
   - Verify backups

2. Weekly:
   - Review performance metrics
   - Update dependencies
   - Rotate logs

3. Monthly:
   - Security updates
   - SSL certificate check
   - Resource planning

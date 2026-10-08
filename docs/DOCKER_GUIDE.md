# UPI Guardian — Docker Containerization Guide

**Phase**: Phase 9  
**Target Environments**: Local Development, Automated Testing, Cloud Container Services  

---

## 1. Overview

UPI Guardian provides hardened, multi-stage Docker configurations for both the Flask backend API service and the React/TanStack frontend application, supplemented by a local `docker-compose.yml` for unified development orchestration.

---

## 2. Backend Containerization

### Dockerfile Highlights (`backend/Dockerfile`)
- **Base Image**: `python:3.11-slim` (minimal attack surface, fast cold-starts).
- **Security**: Runs under an unprivileged system user (`appuser`, UID 1000) rather than `root`.
- **Production Server**: Uses **Gunicorn** WSGI server with multi-threaded workers (`--workers 2 --threads 4`).
- **ML Artifacts**: Pre-packaged Isolation Forest and TF-IDF models are copied directly into the image for zero-download runtime startup.
- **Healthcheck**: Automated Python HTTP health probe targets `http://127.0.0.1:5000/api/health`.

### Building the Backend Image
```bash
docker build -t upi-guardian-backend:latest ./backend
```

### Running the Backend Container Standalone
```bash
docker run -d \
  --name upi-backend \
  -p 5000:5000 \
  -e FLASK_ENV=production \
  -e SECRET_KEY="CHANGE_ME_IN_PRODUCTION" \
  -e JWT_SECRET_KEY="CHANGE_ME_IN_PRODUCTION" \
  -e MONGODB_URI="mongodb+srv://<username>:<password>@cluster.mongodb.net/?retryWrites=true" \
  -e MONGODB_DATABASE="upi_guardian_prod" \
  -e CORS_ORIGINS="http://localhost:3000" \
  upi-guardian-backend:latest
```

---

## 3. Frontend Containerization

### Dockerfile Highlights (`frontend-magic-wand-07-main/Dockerfile`)
- **Multi-Stage Build**:
  - `builder` stage: Node 20 Alpine performs `npm ci` and runs `npm run build` using Vite.
  - `runner` stage: Clean Node 20 Alpine image with only the compiled static assets and minimal runtime server.
- **Security**: Runs under non-root `node` user.
- **Zero Secrets**: Contains no backend credentials or database connection strings.

### Building the Frontend Image
```bash
docker build \
  --build-arg VITE_API_BASE_URL=http://localhost:5000/api \
  --build-arg VITE_USE_MOCK_API=false \
  -t upi-guardian-frontend:latest ./frontend-magic-wand-07-main
```

### Running the Frontend Container Standalone
```bash
docker run -d \
  --name upi-frontend \
  -p 3000:3000 \
  upi-guardian-frontend:latest
```

---

## 4. Local Development Orchestration (`docker-compose.yml`)

A `docker-compose.yml` is provided at the workspace root to quickly launch both services locally with live health checking:

```yaml
version: "3.8"
services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - USE_MOCK_DB=true
      - TWILIO_ENABLED=false

  frontend:
    build:
      context: ./frontend-magic-wand-07-main
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

### Starting the Compose Stack
```bash
docker compose up -d --build
```

### Checking Container Status & Health
```bash
docker compose ps
```

### Viewing Logs
```bash
docker compose logs -f backend
docker compose logs -f frontend
```

### Stopping the Stack
```bash
docker compose down
```

---

## 5. Security Rules for Docker Deployments

1. **Never Bake Secrets**: Do not write `.env` files into Docker images. Use Docker environment flags (`-e`) or container secret managers (e.g. AWS Secrets Manager, Render Environment Variables).
2. **Read-Only Artifacts**: ML model joblib files are read-only artifacts loaded at startup; containers require no write permissions to model directories.
3. **Isolated Networking**: In production, backend containers should reside in private subnets with only the reverse proxy / load balancer exposed to the public internet.

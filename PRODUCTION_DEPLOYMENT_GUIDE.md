# Production Deployment Guide for HSE Agent System

## Current Setup Status

### ⚠️ Current Issues (Development Mode)
- Frontend has API configuration that needs environment-based setup
- Running in development mode (`npm run dev`)
- No SSL/TLS certificates configured
- Missing production security hardening

## Production Architecture

```
Internet → Nginx (Reverse Proxy) → Backend (FastAPI)
                                 → Frontend (Next.js)
```

## Required Changes for Production

### 1. Environment Configuration

Create production `.env` file:
```bash
# Backend
DATABASE_URL=postgresql://user:password@postgres:5432/hse_production
SECRET_KEY=<generate-strong-secret-key>
ENVIRONMENT=production
DEBUG=false

# Frontend  
NODE_ENV=production
NEXT_PUBLIC_API_URL=https://your-domain.com
```

### 2. Frontend Configuration

The frontend now uses `api-client.ts` which:
- In production: Uses relative URLs (requests go through nginx)
- In development: Uses `NEXT_PUBLIC_API_URL` or localhost:8000

### 3. Docker Compose Production Setup

```yaml
# docker-compose.production.yml
services:
  frontend:
    build:
      context: ./frontend
      args:
        - NODE_ENV=production
    environment:
      - NODE_ENV=production
    restart: always
    
  backend:
    environment:
      - ENVIRONMENT=production
      - DEBUG=false
    restart: always
    
  nginx:
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl:ro  # SSL certificates
    ports:
      - "80:80"
      - "443:443"
    restart: always
```

### 4. Security Hardening

#### Required Steps:
1. **SSL/TLS Setup**
   - Obtain SSL certificates (Let's Encrypt recommended)
   - Enable HTTPS in nginx configuration
   - Force HTTPS redirect

2. **API Security**
   - Enable CORS restrictions (currently allows all origins)
   - Implement API rate limiting (already configured in nginx)
   - Add request validation and sanitization

3. **Environment Variables**
   - Never commit `.env` files
   - Use secrets management (Docker Secrets, Kubernetes Secrets, etc.)
   - Rotate keys regularly

4. **Database Security**
   - Use strong passwords
   - Enable SSL for database connections
   - Regular backups

### 5. Deployment Steps

```bash
# 1. Build production images
docker-compose -f docker-compose.production.yml build

# 2. Run database migrations
docker-compose -f docker-compose.production.yml run backend python -m app.init_database

# 3. Start services
docker-compose -f docker-compose.production.yml up -d

# 4. Check health
curl https://your-domain.com/health
```

### 6. Monitoring & Logging

Configure:
- Application monitoring (Prometheus, Grafana)
- Centralized logging (ELK stack)
- Error tracking (Sentry)
- Uptime monitoring

### 7. Backup Strategy

- Database: Daily automated backups
- File storage (MinIO): Regular snapshots
- Configuration: Version controlled

## Current Architecture Benefits

✅ **Good practices already in place:**
- Nginx reverse proxy for routing
- Rate limiting configured
- Security headers set
- Microservices architecture
- Container orchestration ready

## Required Actions Before Production

1. **Update API client configuration** ✅ (Created `api-client.ts`)
2. **Configure SSL certificates**
3. **Set production environment variables**
4. **Enable production build mode for frontend**
5. **Configure proper CORS policies**
6. **Set up monitoring and logging**
7. **Implement backup procedures**
8. **Security audit and penetration testing**

## Testing Production Setup Locally

```bash
# Use production compose file
docker-compose -f docker-compose.production.yml up --build

# Access via nginx (not direct ports)
http://localhost  # Goes through nginx
```

## Important Notes

- Never expose backend ports directly in production
- All traffic should go through nginx
- Use environment-specific configuration files
- Regular security updates for all containers
- Implement proper CI/CD pipeline for deployments
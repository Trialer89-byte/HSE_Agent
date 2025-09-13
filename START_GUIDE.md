# HSE Agent - Startup Guide

## 🚀 Quick Start Options

You have **3 different ways** to run the system depending on your needs:

---

## 1️⃣ **DEVELOPMENT MODE** (Fastest for coding)
Best for: Making code changes, debugging, testing features

### Method A: Quick Development Setup
```bash
# Windows
start-dev.bat

# Linux/macOS  
./start.sh dev
```

### Method B: Manual Development Setup
```bash
# Terminal 1: Start backend services only
docker-compose -f docker-compose.frontend.yml up postgres redis minio weaviate transformers backend

# Terminal 2: Run frontend in dev mode
cd frontend
npm install  # Only first time
npm run dev
```

**Access:**
- Frontend: http://localhost:3000 (with hot reload)
- Backend API: http://localhost:8000/docs
- Changes appear instantly without rebuild

---

## 2️⃣ **PRODUCTION MODE** (Docker - like real deployment)
Best for: Testing the full system, demo to clients, pre-production testing

### Method A: Quick start (recommended)
```bash
# Windows - Quick start without rebuild
quick-start.bat

# Windows - Full stack with rebuild  
start-fullstack.bat

# Windows - Production optimized
start-prod.bat
```

### Method B: Manual Docker commands
```bash
# Quick start (uses existing images)
docker-compose -f docker-compose.frontend.yml up -d

# Full rebuild (after code changes)
docker-compose -f docker-compose.frontend.yml up --build -d
```

**Access:**
- Frontend: http://localhost:3000 (optimized build)
- Backend API: http://localhost:8000/docs
- All services containerized and isolated

---

## 3️⃣ **HYBRID MODE** (Backend prod + Frontend dev)
Best for: Backend testing with frontend development

```bash
# Start everything in Docker
docker-compose -f docker-compose.frontend.yml up -d

# Stop only the frontend container
docker-compose -f docker-compose.frontend.yml stop frontend

# Run frontend in dev mode
cd frontend
npm run dev
```

---

## 📊 Comparison Table

| Feature | Development Mode | Production Mode |
|---------|-----------------|-----------------|
| **Startup Time** | ~10 seconds | ~30 seconds (or 3-5 min with rebuild) |
| **Hot Reload** | ✅ Yes | ❌ No |
| **Performance** | Slower (unoptimized) | Faster (optimized) |
| **Debugging** | ✅ Easy | ⚠️ Limited |
| **Resource Usage** | Lower | Higher |
| **Like Real Deploy** | ❌ No | ✅ Yes |
| **Code Changes** | Instant | Requires rebuild |

---

## 🛑 Stopping the System

### Quick stop (Windows):
```bash
stop-all.bat
```

### Manual stop commands:
```bash
# Stop everything
docker-compose -f docker-compose.frontend.yml down

# Stop specific service
docker-compose -f docker-compose.frontend.yml stop frontend
docker-compose -f docker-compose.frontend.yml stop backend

# Stop dev mode
# Press Ctrl+C in the terminal running npm run dev
```

---

## 🔍 Check Status

```bash
# See what's running
docker ps

# Check logs
docker-compose -f docker-compose.frontend.yml logs -f frontend
docker-compose -f docker-compose.frontend.yml logs -f backend

# Health check
curl http://localhost:3000/health
curl http://localhost:8000/health
```

---

## 💡 Recommendations

- **For daily development**: Use Development Mode
- **For testing before deployment**: Use Production Mode  
- **For backend API work**: Use Hybrid Mode
- **For demos**: Use Production Mode with quick-start.bat

---

## 🚨 Common Issues

1. **Port already in use**: Stop other services or change ports in docker-compose.yml
2. **Slow build**: Normal for production mode (3-5 minutes)
3. **Changes not appearing**: In production mode, you need to rebuild
4. **Can't connect to backend**: Ensure backend is running on port 8000

---

## Environment Variables

### Development Mode (.env.local in frontend/):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Production Mode (set in docker-compose.yml):
```
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://localhost:8000
```
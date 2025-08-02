#!/bin/bash

# HSE Enterprise System - Quick Start Script
# 
# Questo script automatizza l'avvio completo del sistema HSE

set -e

echo "🚀 HSE Enterprise System - Quick Start"
echo "======================================"

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "📋 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Modifica il file .env con le tue configurazioni!"
    echo "   - Genera password sicure"
    echo "   - Inserisci la tua OpenAI API key"
    echo "   - Configura i domini se necessario"
    echo ""
    read -p "Premi ENTER quando hai completato la configurazione di .env..."
fi

# Create directories
echo "📁 Creating required directories..."
mkdir -p logs
mkdir -p db/init
mkdir -p monitoring/grafana/dashboards
mkdir -p monitoring/grafana/datasources

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker non è installato. Installa Docker Desktop e riprova."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose non è installato. Installa Docker Compose e riprova."
    exit 1
fi

# Pull images
echo "📦 Pulling required Docker images..."
docker-compose -f docker-compose.enterprise.yml pull

# Start services
echo "🔄 Starting HSE Enterprise Stack..."
docker-compose -f docker-compose.enterprise.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🏥 Checking service health..."

# Check backend
if curl -f -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API: OK"
else
    echo "❌ Backend API: Failed"
fi

# Check database
if docker-compose -f docker-compose.enterprise.yml exec -T db pg_isready -U hse_user -d hse_db > /dev/null; then
    echo "✅ PostgreSQL: OK"
else
    echo "❌ PostgreSQL: Failed"
fi

# Initialize database
echo "🗄️  Initializing database with sample data..."
if command -v python3 &> /dev/null; then
    python3 scripts/init-database.py
else
    echo "⚠️  Python3 not found. Run scripts/init-database.py manually after installation."
fi

# Show status
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.enterprise.yml ps

echo ""
echo "🎉 HSE Enterprise System Started Successfully!"
echo "============================================="
echo ""
echo "🌐 Access Points:"
echo "  Backend API:     http://localhost:8000"
echo "  API Docs:        http://localhost:8000/api/docs"
echo "  Health Check:    http://localhost:8000/health"
echo "  Traefik Dash:    http://localhost:8080"
echo ""
echo "🔑 Default Login:"
echo "  Username: admin"
echo "  Password: HSEAdmin2024!"
echo ""
echo "📚 Quick Test:"
echo "  1. Go to http://localhost:8000/api/docs"
echo "  2. Login with admin credentials"
echo "  3. Create a work permit"
echo "  4. Run AI analysis"
echo ""
echo "🛑 To stop the system:"
echo "  docker-compose -f docker-compose.enterprise.yml down"
echo ""
echo "📖 For more info, see README.md"
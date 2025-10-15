#!/bin/bash

# Telegram Bot Points System - Initialization Script

echo "🚀 Initializing Telegram Bot Points System..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual credentials!"
    echo ""
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build

if [ $? -eq 0 ]; then
    echo "✅ Docker images built successfully"
else
    echo "❌ Failed to build Docker images"
    exit 1
fi

# Start services
echo "🚀 Starting services..."
docker-compose up -d

if [ $? -eq 0 ]; then
    echo "✅ Services started successfully"
else
    echo "❌ Failed to start services"
    exit 1
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is running"
else
    echo "⚠️  API might not be ready yet. Check logs with: docker-compose logs api"
fi

# Check frontend
if curl -f http://localhost > /dev/null 2>&1; then
    echo "✅ Frontend is running"
else
    echo "⚠️  Frontend might not be ready yet. Check logs with: docker-compose logs nginx"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📱 Access the application:"
echo "   - User Interface: http://localhost"
echo "   - Admin Dashboard: http://localhost/admin"
echo "   - API Documentation: http://localhost:8000/docs"
echo ""
echo "🔑 Default admin credentials:"
echo "   - Username: admin"
echo "   - Password: changeme123"
echo "   ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!"
echo ""
echo "📝 Next steps:"
echo "   1. Update .env with your Telegram Bot Token"
echo "   2. Configure Supabase credentials"
echo "   3. Change admin password"
echo "   4. Restart services: docker-compose restart"
echo ""
echo "📊 Useful commands:"
echo "   - View logs: docker-compose logs -f"
echo "   - Stop services: docker-compose down"
echo "   - Restart services: docker-compose restart"
echo "   - View running services: docker-compose ps"
echo ""

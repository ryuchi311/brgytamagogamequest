# Docker Port 80 Setup - BRGY TAMAGO Quest Hub

## Quick Start

### Option 1: Pure Docker (Recommended for simplicity)

```bash
./run-pure-docker.sh
```

This will:
- Build the Docker image
- Start container on port 8080
- Mount frontend directory for live updates
- Show logs and access URLs

### Option 2: Docker Compose

```bash
./run-docker-8080.sh
```

Or manually:
```bash
docker-compose -f docker-compose.8080.yml up -d
```

### Option 3: Manual Docker Commands

**Build:**
```bash
docker build -t brgy-tamago-quest-hub --build-arg REQUIREMENTS_FILE=requirements-backend.txt .
```

**Run:**
```bash
docker run -d \
  --name brgy-tamago-api \
  -p 8080:8080 \
  -e PORT=8080 \
  -e SECRET_KEY="your-secret-key" \
  -e DATABASE_URL="your-database-url" \
  -e SUPABASE_URL="your-supabase-url" \
  -e SUPABASE_KEY="your-supabase-key" \
  -e TELEGRAM_BOT_TOKEN="your-bot-token" \
  -v $(pwd)/frontend:/app/frontend \
  brgy-tamago-quest-hub
```

## Access Points

- **Frontend**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health
- **API Base**: http://localhost:8080/api

## Container Management

### View Logs
```bash
# Real-time logs
docker logs -f brgy-tamago-api

# Last 100 lines
docker logs --tail 100 brgy-tamago-api
```

### Stop Container
```bash
docker stop brgy-tamago-api
```

### Start Existing Container
```bash
docker start brgy-tamago-api
```

### Restart Container
```bash
docker restart brgy-tamago-api
```

### Remove Container
```bash
docker stop brgy-tamago-api
docker rm brgy-tamago-api
```

### Execute Commands Inside Container
```bash
# Shell access
docker exec -it brgy-tamago-api bash

# Run Python command
docker exec brgy-tamago-api python -c "print('Hello from container')"
```

## Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Security
SECRET_KEY=your-secret-key-here

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token

# Twitter (Optional)
TWITTER_BEARER_TOKEN=
TWITTER_API_KEY=
TWITTER_API_SECRET=
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
```

The scripts will automatically load these variables.

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8080
lsof -i:8080

# Or kill it
lsof -ti:8080 | xargs kill -9
```

### Container Won't Start
```bash
# Check logs
docker logs brgy-tamago-api

# Run interactively to see errors
docker run --rm -it -p 8080:8080 -e PORT=8080 brgy-tamago-quest-hub
```

### Rebuild Image
```bash
# Remove old image
docker rmi brgy-tamago-quest-hub

# Rebuild without cache
docker build --no-cache -t brgy-tamago-quest-hub .
```

### Check Container Status
```bash
# List running containers
docker ps

# List all containers
docker ps -a

# Container details
docker inspect brgy-tamago-api
```

## Development Mode

For development with auto-reload, you can override the command:

```bash
docker run -d \
  --name brgy-tamago-api \
  -p 8080:8080 \
  -e PORT=8080 \
  -v $(pwd)/app:/app/app \
  -v $(pwd)/frontend:/app/frontend \
  brgy-tamago-quest-hub \
  bash -c "PORT=8080 python -m uvicorn app.api:app --host 0.0.0.0 --port 8080 --reload"
```

## Production Deployment

For production on port 8080:

```bash
docker run -d \
  --name brgy-tamago-api \
  -p 8080:8080 \
  -e PORT=8080 \
  --env-file .env \
  --restart always \
  --memory="2g" \
  --cpus="2" \
  brgy-tamago-quest-hub
```

## Docker Compose Commands

Using `docker-compose.8080.yml`:

```bash
# Start
docker-compose -f docker-compose.8080.yml up -d

# Stop
docker-compose -f docker-compose.8080.yml down

# View logs
docker-compose -f docker-compose.8080.yml logs -f

# Rebuild
docker-compose -f docker-compose.8080.yml build --no-cache

# Restart
docker-compose -f docker-compose.8080.yml restart
```

## Health Checks

The container includes a health check on `/health`:

```bash
# Check health
curl http://localhost:8080/health

# Docker health status
docker inspect --format='{{.State.Health.Status}}' brgy-tamago-api
```

## Performance Monitoring

```bash
# Resource usage
docker stats brgy-tamago-api

# Top processes in container
docker top brgy-tamago-api
```

## Clean Up

```bash
# Remove container and image
docker stop brgy-tamago-api
docker rm brgy-tamago-api
docker rmi brgy-tamago-quest-hub

# Remove all stopped containers
docker container prune

# Remove unused images
docker image prune -a
```

## Files

- `Dockerfile` - Main Docker configuration
- `start-server.sh` - Startup script (handles PORT variable)
- `docker-compose.8080.yml` - Compose config for port 8080
- `run-pure-docker.sh` - Quick start script (pure Docker)
- `run-docker-8080.sh` - Quick start script (Docker Compose)
- `.env` - Environment variables (create this)

## Support

For issues or questions:
- Check logs: `docker logs brgy-tamago-api`
- GitHub Issues: https://github.com/ryuchi311/BT-GameHub/issues

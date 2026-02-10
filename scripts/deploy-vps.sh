#!/bin/bash
# =============================================================================
# Digital Finance Tracker - VPS Deployment Script
# PURPOSE: Deploy backend to IONOS VPS with Plesk
# VPS: 108.175.12.154 | Domain: securebankAI.mysticdatanode.net | Port: 8003
# =============================================================================

set -e  # Exit on error

echo "========================================"
echo "Digital Finance Tracker - VPS Deployment"
echo "========================================"

# Configuration
APP_DIR="/var/www/vhosts/mysticdatanode.net/securebankAI"
REPO_URL="https://github.com/E-Y-J/TR41-DIGITALFINANCE.git"
BRANCH="main"
PORT=8003

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Step 1: Creating directory structure...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

echo -e "${YELLOW}Step 2: Checking Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker not found. Installing...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    systemctl start docker
    systemctl enable docker
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}Docker Compose not found. Installing plugin...${NC}"
    mkdir -p ~/.docker/cli-plugins/
    curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o ~/.docker/cli-plugins/docker-compose
    chmod +x ~/.docker/cli-plugins/docker-compose
fi

echo -e "${GREEN}Docker version: $(docker --version)${NC}"
echo -e "${GREEN}Docker Compose version: $(docker compose version)${NC}"

echo -e "${YELLOW}Step 3: Cloning/updating repository...${NC}"
if [ -d ".git" ]; then
    echo "Repository exists, pulling latest..."
    git fetch origin
    git checkout $BRANCH
    git pull origin $BRANCH
else
    echo "Cloning repository..."
    git clone $REPO_URL .
    git checkout $BRANCH
fi

echo -e "${YELLOW}Step 4: Setting up environment file...${NC}"
if [ ! -f ".env.vps" ]; then
    echo "Creating .env.vps from template..."
    cp .env.vps.example .env.vps
    echo -e "${YELLOW}⚠️  Please edit .env.vps to update FRONTEND_URL after Vercel deployment${NC}"
fi

echo -e "${YELLOW}Step 5: Stopping existing containers (if any)...${NC}"
docker compose -f docker-compose.prod.yaml --env-file .env.vps down 2>/dev/null || true

echo -e "${YELLOW}Step 6: Building and starting containers...${NC}"
docker compose -f docker-compose.prod.yaml --env-file .env.vps build --no-cache
docker compose -f docker-compose.prod.yaml --env-file .env.vps up -d

echo -e "${YELLOW}Step 7: Waiting for database to be ready...${NC}"
sleep 15

echo -e "${YELLOW}Step 8: Waiting for AI models to load (~60 seconds)...${NC}"
sleep 60

echo -e "${YELLOW}Step 9: Running database migrations...${NC}"
docker compose -f docker-compose.prod.yaml exec -T backend flask db upgrade

echo -e "${YELLOW}Step 10: Checking health...${NC}"
sleep 10
if curl -sf http://localhost:$PORT/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Backend is healthy!${NC}"
    curl -s http://localhost:$PORT/health | python3 -m json.tool 2>/dev/null || curl -s http://localhost:$PORT/health
else
    echo -e "${RED}❌ Backend health check failed. Checking logs...${NC}"
    docker compose -f docker-compose.prod.yaml logs --tail 100 backend
    exit 1
fi

echo ""
echo -e "${GREEN}========================================"
echo "✅ DEPLOYMENT COMPLETE!"
echo "========================================${NC}"
echo ""
echo "Services running:"
docker compose -f docker-compose.prod.yaml ps
echo ""
echo "Ports used:"
echo "  - Backend API: 8003"
echo "  - PostgreSQL:  5433 (internal Docker)"
echo "  - Redis:       6381 (internal Docker)"
echo ""
echo "Test locally:"
echo "  curl http://localhost:$PORT/health"
echo "  curl http://localhost:$PORT/api/test"
echo ""
echo "After Cloudflare propagates:"
echo "  https://securebankAI.mysticdatanode.net/health"
echo ""
echo "View logs:"
echo "  docker compose -f docker-compose.prod.yaml logs -f backend"
echo ""
echo -e "${YELLOW}NEXT STEPS:${NC}"
echo "1. Deploy frontend to Vercel"
echo "2. Update .env.vps with Vercel URL (FRONTEND_URL)"
echo "3. Update Auth0 with Vercel callback URLs"
echo "4. Restart backend: docker compose -f docker-compose.prod.yaml restart backend"

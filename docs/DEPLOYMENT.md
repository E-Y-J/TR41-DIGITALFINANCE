# Deployment Guide - Digital Finance Tracker

## Production Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLOUDFLARE                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │     WAF     │  │   Access    │  │   Tunnel    │  │   DNS + SSL/TLS     │ │
│  │  (Layer 7)  │  │ (Zero Trust)│  │ (No Ports)  │  │ (Auto Certificate)  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└────────────────────────────────┬────────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    FRONTEND     │    │    BACKEND      │    │    DATABASE     │
│    (Vercel)     │    │  (VPS Docker)   │    │  (PostgreSQL)   │
│                 │    │                 │    │                 │
│ securebankai    │    │ Flask + Gunicorn│    │ VPS or AWS RDS  │
│ .vercel.app     │    │ + Redis + AI    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Live URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://securebankai.vercel.app |
| **API** | https://securebankai.mysticdatanode.net |
| **API Health** | https://securebankai.mysticdatanode.net/health |
| **API Docs** | https://securebankai.mysticdatanode.net/api/docs/ |

---

## Prerequisites

- VPS (IONOS, DigitalOcean, Linode, etc.)
- Cloudflare account (Free tier)
- Vercel account (Free)
- Auth0 account (Free tier)
- Domain name (managed via Cloudflare DNS)

---

## Backend Deployment (VPS + Cloudflare Tunnel)

### Step 1: VPS Initial Setup

```bash
# SSH to your VPS
ssh root@your-vps-ip

# Install Docker (if not installed)
curl -fsSL https://get.docker.com | sh
systemctl enable docker
systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/E-Y-J/TR41-DIGITALFINANCE.git /opt/digital-finance
cd /opt/digital-finance
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env.prod

# Edit with production values
nano .env.prod
```

Required environment variables:
```env
FLASK_ENV=production
SECRET_KEY=<generate-with-python-secrets>
DATABASE_URL=postgresql://user:pass@localhost:5432/digital_finance_db
AUTH0_DOMAIN=dev-2d371r8njde648mh.us.auth0.com
AUTH0_API_AUDIENCE=https://api.digitalfinance.local
AUTH0_ALGORITHMS=RS256
FRONTEND_URL=https://securebankai.vercel.app
GEMINI_API_KEY=<your-gemini-key>
REDIS_URL=redis://redis:6379/0
DEV_IMPERSONATION=false
AI_CATEGORIZER_ENABLED=true
```

### Step 3: Deploy with Docker Compose

```bash
# Build and start containers
docker compose -f docker-compose.prod.yaml --env-file .env.prod up -d --build

# Run database migrations
docker compose -f docker-compose.prod.yaml exec backend flask db upgrade

# Verify containers are running
docker compose -f docker-compose.prod.yaml ps

# Check logs
docker compose -f docker-compose.prod.yaml logs -f backend
```

### Step 4: Install Cloudflare Tunnel

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Authenticate with Cloudflare
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create securebankai

# Configure tunnel (create config.yml)
mkdir -p /etc/cloudflared
cat > /etc/cloudflared/config.yml << EOF
tunnel: <your-tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: securebankai.mysticdatanode.net
    service: http://localhost:8000
  - service: http_status:404
EOF

# Create DNS record
cloudflared tunnel route dns securebankai securebankai.mysticdatanode.net

# Install as system service
cloudflared service install
systemctl enable cloudflared
systemctl start cloudflared
```

### Step 5: Verify Backend

```bash
# Test via Cloudflare tunnel
curl https://securebankai.mysticdatanode.net/health

# Expected response:
# {"status": "healthy", "timestamp": "...", "version": "..."}
```

---

## Frontend Deployment (Vercel CLI)

### Step 1: Install Vercel CLI

```bash
npm install -g vercel
vercel login
```

### Step 2: Deploy

```bash
cd frontend
vercel --prod
```

### Step 3: Configure Environment Variables

In Vercel Dashboard (Settings → Environment Variables):

```
VITE_API_URL=https://securebankai.mysticdatanode.net
VITE_AUTH0_DOMAIN=dev-2d371r8njde648mh.us.auth0.com
VITE_AUTH0_CLIENT_ID=Xmf7EN2wO4jhTjJN1T2U1ZDgJidWI32A
VITE_AUTH0_AUDIENCE=https://api.digitalfinance.local
```

---

## Auth0 Configuration

### API Settings (Applications → APIs)

| Setting | Value |
|---------|-------|
| **Identifier (Audience)** | `https://api.digitalfinance.local` |
| **Signing Algorithm** | RS256 |

### Application Settings (Applications → Applications)

| Setting | Value |
|---------|-------|
| **Allowed Callback URLs** | `https://securebankai.vercel.app/callback, http://localhost:5173/callback` |
| **Allowed Logout URLs** | `https://securebankai.vercel.app, http://localhost:5173` |
| **Allowed Web Origins** | `https://securebankai.vercel.app, http://localhost:5173` |

---

## Cloudflare Configuration

### WAF Rules (Security → WAF)

- ✅ OWASP Core Ruleset enabled
- ✅ Managed Rules auto-updated
- ✅ Rate limiting configured

### SSL/TLS Settings

| Setting | Value |
|---------|-------|
| **SSL Mode** | Full (strict) |
| **Minimum TLS** | 1.2 |
| **HSTS** | Enabled |
| **Always Use HTTPS** | On |

---

## Security Headers (Vercel)

Frontend headers are configured in `frontend/vercel.json`:

```json
{
  "headers": [
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" },
        { "key": "Strict-Transport-Security", "value": "max-age=31536000; includeSubDomains; preload" },
        { "key": "Content-Security-Policy", "value": "default-src 'self'; ..." }
      ]
    }
  ]
}
```

---

## Updating Production

### Backend Updates

```bash
# SSH to VPS
ssh root@your-vps-ip
cd /opt/digital-finance

# Pull latest code
git pull origin main

# Rebuild and restart
docker compose -f docker-compose.prod.yaml --env-file .env.prod up -d --build

# Run migrations if needed
docker compose -f docker-compose.prod.yaml exec backend flask db upgrade
```

### Frontend Updates

```bash
cd frontend
vercel --prod
```

---

## Monitoring & Logs

### Sentry Error Monitoring

Sentry is configured for both backend error tracking and performance monitoring.

**Dashboard:** https://sentry.io (login required)

**Backend Configuration** (in `.env.prod`):
```env
SENTRY_DSN=https://xxx@xxx.ingest.sentry.io/xxx
SENTRY_TRACES_SAMPLE_RATE=0.1
```

**Features:**
- Real-time error alerts
- Performance tracing
- Release tracking
- User context in errors

### Container Logs

```bash
# View backend logs
docker compose -f docker-compose.prod.yaml logs -f backend

# View all container status
docker compose -f docker-compose.prod.yaml ps

# View cloudflared tunnel status
systemctl status cloudflared
journalctl -u cloudflared -f
```

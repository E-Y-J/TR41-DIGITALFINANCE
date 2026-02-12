# Deployment Configuration Checklist

## 🌐 Production URLs

| Service | URL |
|---------|-----|
| **Frontend** | https://securebankai.vercel.app |
| **API** | https://securebankai.mysticdatanode.net |
| **API Health** | https://securebankai.mysticdatanode.net/health |
| **API Docs** | https://securebankai.mysticdatanode.net/api/docs/ |

---

## 🔐 Auth0 Dashboard Configuration

**URL:** https://manage.auth0.com/

### Application Settings (Applications → Applications → Your App)

| Setting | Local Development | Production |
|---------|------------------|------------|
| **Allowed Callback URLs** | `http://localhost:5173/callback` | `https://securebankai.vercel.app/callback` |
| **Allowed Logout URLs** | `http://localhost:5173` | `https://securebankai.vercel.app` |
| **Allowed Web Origins** | `http://localhost:5173` | `https://securebankai.vercel.app` |

### API Settings (Applications → APIs → Your API)

| Setting | Value |
|---------|-------|
| **Identifier (Audience)** | `https://api.digitalfinance.local` |
| **Signing Algorithm** | RS256 |
| **Enable RBAC** | Optional |

---

## 🔑 Environment Variables Summary

### Backend (VPS)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FLASK_ENV` | ✅ | Environment mode | `production` |
| `SECRET_KEY` | ✅ | Flask secret key (32+ chars) | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | ✅ | PostgreSQL connection | `postgresql://user:pass@localhost:5432/digital_finance_db` |
| `AUTH0_DOMAIN` | ✅ | Auth0 tenant domain | `dev-2d371r8njde648mh.us.auth0.com` |
| `AUTH0_API_AUDIENCE` | ✅ | Auth0 API identifier | `https://api.digitalfinance.local` |
| `AUTH0_ALGORITHMS` | ✅ | JWT signing algorithm | `RS256` |
| `FRONTEND_URL` | ✅ | CORS allowed origin | `https://securebankai.vercel.app` |
| `GEMINI_API_KEY` | ✅ | Google AI API key | Get from Google AI Studio |
| `REDIS_URL` | ✅ | Redis connection | `redis://redis:6379/0` |
| `DEV_IMPERSONATION` | ⚠️ | **MUST be `false` in prod** | `false` |
| `AI_CATEGORIZER_ENABLED` | ⚪ | Enable local AI model | `true` |
| `SENTRY_DSN` | ✅ | Sentry error monitoring | `https://xxx@xxx.ingest.sentry.io/xxx` |
| `SENTRY_TRACES_SAMPLE_RATE` | ⚪ | Performance sampling (0-1) | `0.1` |

### Frontend (Vercel)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_AUTH0_DOMAIN` | ✅ | Auth0 tenant domain | `dev-2d371r8njde648mh.us.auth0.com` |
| `VITE_AUTH0_CLIENT_ID` | ✅ | Auth0 SPA Client ID | `Xmf7EN2wO4jhTjJN1T2U1ZDgJidWI32A` |
| `VITE_AUTH0_AUDIENCE` | ✅ | Auth0 API identifier | `https://api.digitalfinance.local` |
| `VITE_API_URL` | ✅ | Backend API URL | `https://securebankai.mysticdatanode.net` |

---

## 🚀 Deployment Steps (VPS + Cloudflare Tunnel)

### Step 1: VPS Initial Setup

```bash
# SSH to your VPS
ssh root@your-vps-ip

# Install Docker
curl -fsSL https://get.docker.com | sh
systemctl enable docker && systemctl start docker

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Clone repository
git clone https://github.com/E-Y-J/TR41-DIGITALFINANCE.git /opt/digital-finance
cd /opt/digital-finance
```

### Step 2: Configure Environment

```bash
# Copy and edit environment file
cp .env.example .env.prod
nano .env.prod
```

### Step 3: Deploy Backend

```bash
# Build and start containers
docker compose -f docker-compose.prod.yaml --env-file .env.prod up -d --build

# Run database migrations
docker compose -f docker-compose.prod.yaml exec backend flask db upgrade

# Verify
docker compose -f docker-compose.prod.yaml ps
docker compose -f docker-compose.prod.yaml logs -f backend
```

### Step 4: Setup Cloudflare Tunnel

```bash
# Install cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# Authenticate
cloudflared tunnel login

# Create tunnel
cloudflared tunnel create securebankai

# Configure tunnel
mkdir -p /etc/cloudflared
cat > /etc/cloudflared/config.yml << EOF
tunnel: <your-tunnel-id>
credentials-file: /root/.cloudflared/<tunnel-id>.json

ingress:
  - hostname: securebankai.mysticdatanode.net
    service: http://localhost:8000
  - service: http_status:404
EOF

# Create DNS record and start service
cloudflared tunnel route dns securebankai securebankai.mysticdatanode.net
cloudflared service install
systemctl enable cloudflared && systemctl start cloudflared
```

### Step 5: Deploy Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

### Step 6: Verify Deployment

```bash
# Test backend health
curl https://securebankai.mysticdatanode.net/health

# Test frontend
# Visit https://securebankai.vercel.app
```

---

## ☁️ Cloudflare Setup Checklist

### DNS Settings
- [ ] Domain added to Cloudflare
- [ ] NS records updated at registrar
- [ ] Proxied (orange cloud) enabled

### SSL/TLS
- [ ] SSL mode: Full (strict)
- [ ] Minimum TLS: 1.2
- [ ] Always Use HTTPS: On
- [ ] HSTS: Enabled

### WAF
- [ ] OWASP Core Ruleset enabled
- [ ] Managed Rules enabled
- [ ] Rate limiting configured

### Tunnel
- [ ] Tunnel created and running
- [ ] DNS route configured
- [ ] Service installed as systemd

---

## 🌐 Vercel Setup Checklist

### Project Configuration
- [ ] Connected to GitHub repository
- [ ] Root directory: `frontend`
- [ ] Framework preset: Vite

### Environment Variables
- [ ] `VITE_AUTH0_DOMAIN` set
- [ ] `VITE_AUTH0_CLIENT_ID` set
- [ ] `VITE_AUTH0_AUDIENCE` set
- [ ] `VITE_API_URL` set to `https://securebankai.mysticdatanode.net`

### Build Settings
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`

---

## 🔄 Updating Production

### Backend

```bash
ssh root@your-vps-ip
cd /opt/digital-finance
git pull origin main
docker compose -f docker-compose.prod.yaml --env-file .env.prod up -d --build
docker compose -f docker-compose.prod.yaml exec backend flask db upgrade
```

### Frontend

```bash
cd frontend
vercel --prod
```

---

## ⚠️ Security Reminders

1. **NEVER commit `.env` files** - Use `.env.example` templates
2. **Set `DEV_IMPERSONATION=false`** in production
3. **Use strong `SECRET_KEY`** - Generate with `secrets.token_hex(32)`
4. **Rotate API keys** after any suspected breach
5. **Cloudflare Tunnel** - No open ports on VPS
6. **Configure CORS** to only allow frontend domain

---

## � Monitoring (Sentry)

**Dashboard:** https://sentry.io

### Checklist
- [ ] `SENTRY_DSN` configured in backend
- [ ] `SENTRY_TRACES_SAMPLE_RATE` set (0.1 recommended)
- [ ] Alert rules configured for errors
- [ ] Release tracking enabled

### Features in Use
- ✅ Error tracking with stack traces
- ✅ Performance monitoring
- ✅ User context in errors
- ✅ Release tracking

---

## �📝 Current Configuration Values

| Service | Value |
|---------|-------|
| **Auth0 Domain** | `dev-2d371r8njde648mh.us.auth0.com` |
| **Auth0 Client ID** | `Xmf7EN2wO4jhTjJN1T2U1ZDgJidWI32A` |
| **Auth0 Audience** | `https://api.digitalfinance.local` |
| **Production API** | `https://securebankai.mysticdatanode.net` |
| **Production Frontend** | `https://securebankai.vercel.app` |
| **Local Backend** | `http://localhost:8000` |
| **Local Frontend** | `http://localhost:5173` |

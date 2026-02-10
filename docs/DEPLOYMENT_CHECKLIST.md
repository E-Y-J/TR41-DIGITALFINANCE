# Deployment Configuration Checklist

## 🔐 Auth0 Dashboard Configuration

**URL:** https://manage.auth0.com/

### Application Settings (Applications → Applications → Your App)

| Setting | Local Development | Production |
|---------|------------------|------------|
| **Allowed Callback URLs** | `http://localhost:3000/callback` | `https://your-app.vercel.app/callback` |
| **Allowed Logout URLs** | `http://localhost:3000` | `https://your-app.vercel.app` |
| **Allowed Web Origins** | `http://localhost:3000` | `https://your-app.vercel.app` |

### API Settings (Applications → APIs → Your API)

| Setting | Value |
|---------|-------|
| **Identifier (Audience)** | `https://api.digitalfinance.local` |
| **Signing Algorithm** | RS256 |
| **Enable RBAC** | Optional |

---

## 🔑 Environment Variables Summary

### Backend (AWS Elastic Beanstalk)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `FLASK_ENV` | ✅ | Environment mode | `production` |
| `SECRET_KEY` | ✅ | Flask secret key (32+ chars) | `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | ✅ | PostgreSQL connection | `postgresql://user:pass@rds-host:5432/dbname` |
| `AUTH0_DOMAIN` | ✅ | Auth0 tenant domain | `dev-2d371r8njde648mh.us.auth0.com` |
| `AUTH0_API_AUDIENCE` | ✅ | Auth0 API identifier | `https://api.digitalfinance.local` |
| `AUTH0_ALGORITHMS` | ✅ | JWT signing algorithm | `RS256` |
| `FRONTEND_URL` | ✅ | CORS allowed origin | `https://your-app.vercel.app` |
| `GEMINI_API_KEY` | ✅ | Google AI API key | Get from Google AI Studio |
| `REDIS_URL` | ⚪ | Redis connection (optional) | `redis://elasticache-host:6379/0` |
| `DEV_IMPERSONATION` | ⚠️ | **MUST be `false` in prod** | `false` |

### Frontend (Vercel)

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `VITE_AUTH0_DOMAIN` | ✅ | Auth0 tenant domain | `dev-2d371r8njde648mh.us.auth0.com` |
| `VITE_AUTH0_CLIENT_ID` | ✅ | Auth0 SPA Client ID | `Xmf7EN2wO4jhTjJN1T2U1ZDgJidWI32A` |
| `VITE_AUTH0_AUDIENCE` | ✅ | Auth0 API identifier | `https://api.digitalfinance.local` |
| `VITE_API_URL` | ✅ | Backend API URL | `https://your-backend.elasticbeanstalk.com` |

---

## ☁️ AWS Setup Checklist

### 1. RDS PostgreSQL
- [ ] Create PostgreSQL 15 instance
- [ ] Set master username/password
- [ ] Configure security group (allow port 5432 from EB)
- [ ] Note connection endpoint for `DATABASE_URL`

### 2. Elastic Beanstalk
- [ ] Create Docker platform environment
- [ ] Set all environment variables in Configuration
- [ ] Configure instance type (t3.small minimum for AI models)
- [ ] Set health check path to `/health`

### 3. ElastiCache Redis (Optional)
- [ ] Create Redis cluster
- [ ] Configure security group
- [ ] Note endpoint for `REDIS_URL`

---

## 🌐 Vercel Setup Checklist

### 1. Project Configuration
- [ ] Connect GitHub repository
- [ ] Set root directory to `frontend`
- [ ] Framework preset: Vite

### 2. Environment Variables
- [ ] Add all `VITE_*` variables
- [ ] Set for Production environment

### 3. Build Settings
- [ ] Build Command: `npm run build`
- [ ] Output Directory: `dist`

---

## 🚀 Deployment Steps

### Step 1: Backend (AWS EB)
```bash
cd backend
eb init -p docker digital-finance-api
eb create production --single
eb setenv FLASK_ENV=production SECRET_KEY=xxx DATABASE_URL=xxx ...
eb deploy
```

### Step 2: Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Step 3: Update Auth0
After deployment, update Auth0 Application Settings:
- Add production callback URL
- Add production logout URL  
- Add production web origin

### Step 4: Verify
```bash
# Test backend health
curl https://your-backend.elasticbeanstalk.com/health

# Test API
curl https://your-backend.elasticbeanstalk.com/api/test
```

---

## ⚠️ Security Reminders

1. **NEVER commit `.env` files** - Use `.env.example` templates
2. **Set `DEV_IMPERSONATION=false`** in production
3. **Use strong `SECRET_KEY`** - Generate with secrets module
4. **Rotate API keys** after any suspected breach
5. **Enable HTTPS** on all endpoints
6. **Configure CORS** to only allow your frontend domain

---

## 📝 Current Configuration Values

| Service | Value |
|---------|-------|
| Auth0 Domain | `dev-2d371r8njde648mh.us.auth0.com` |
| Auth0 Client ID | `Xmf7EN2wO4jhTjJN1T2U1ZDgJidWI32A` |
| Auth0 Audience | `https://api.digitalfinance.local` |
| Local Backend | `http://localhost:8000` |
| Local Frontend | `http://localhost:3000` |

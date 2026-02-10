# Deployment Guide - Digital Finance Tracker

## Quick Demo Deployment (AWS + Vercel)

### Prerequisites

- AWS Account (Free Tier eligible)
- Vercel Account (Free)
- Auth0 Account (Free tier)
- Node.js 18+ and Python 3.11+

---

## Backend Deployment (AWS Elastic Beanstalk)

### Option 1: AWS Elastic Beanstalk (Recommended for Demo)

1. **Install EB CLI:**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB in backend folder:**
   ```bash
   cd backend
   eb init -p docker digital-finance-backend --region us-east-1
   ```

3. **Create environment:**
   ```bash
   eb create digital-finance-demo --single --instance-type t3.micro
   ```

4. **Set environment variables** (in AWS Console or CLI):
   ```bash
   eb setenv \
     DATABASE_URL=postgresql://user:pass@host:5432/dbname \
     AUTH0_DOMAIN=your-domain.auth0.com \
     AUTH0_AUDIENCE=https://your-api-audience \
     FLASK_ENV=production \
     GEMINI_API_KEY=your-key-optional
   ```

5. **Deploy:**
   ```bash
   eb deploy
   ```

6. **Get URL:**
   ```bash
   eb status
   # Note the CNAME - this is your backend URL
   ```

### Database Options

**Option A: AWS RDS PostgreSQL (Free Tier)**
- Create RDS instance in AWS Console
- Use the endpoint in DATABASE_URL

**Option B: SQLite for Demo (Simplest)**
- Set `DATABASE_URL=sqlite:///demo.db`
- Data persists only within container lifecycle

---

## Frontend Deployment (Vercel)

1. **Push code to GitHub** (if not already)

2. **Import to Vercel:**
   - Go to https://vercel.com/new
   - Import your GitHub repo
   - Set Root Directory: `frontend`
   - Framework: Vite

3. **Set Environment Variables** in Vercel Dashboard:
   ```
   VITE_API_URL=https://your-eb-url.elasticbeanstalk.com/api
   VITE_AUTH0_DOMAIN=your-domain.auth0.com
   VITE_AUTH0_CLIENT_ID=your-client-id
   VITE_AUTH0_AUDIENCE=https://your-api-audience
   ```

4. **Deploy** - Vercel auto-deploys on push

---

## Auth0 Configuration

1. **Create API** in Auth0 Dashboard:
   - Identifier: `https://digital-finance-api` (this is your audience)

2. **Create Application** (Single Page Application):
   - Allowed Callback URLs: `https://your-vercel-url.vercel.app/callback`
   - Allowed Logout URLs: `https://your-vercel-url.vercel.app`
   - Allowed Web Origins: `https://your-vercel-url.vercel.app`

3. **Update CORS** on Backend:
   - Add Vercel URL to allowed origins

---

## Quick Test

```bash
# Health check
curl https://your-eb-url.elasticbeanstalk.com/health

# Should return:
# {"status": "healthy", ...}
```

---

## Cleanup After Demo

```bash
# Terminate Elastic Beanstalk
cd backend
eb terminate digital-finance-demo

# Delete RDS (if created)
# Go to AWS Console > RDS > Delete

# Vercel projects can remain (free)
```

---

## Alternative: Railway.app (Simpler)

If AWS is too complex, Railway offers one-click Docker deployment:

1. Go to https://railway.app
2. New Project > Deploy from GitHub
3. Select the repo, set root to `backend`
4. Add PostgreSQL plugin
5. Set environment variables
6. Deploy

Railway free tier: 500 hours/month, $5 credit.

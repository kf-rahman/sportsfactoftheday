# Deployment Guide for Sports Facts App

## Quick Start - Choose Your Platform

### Option 1: Railway (Recommended - Easiest)
**Best for**: Beginners, free tier available, automatic deployments

1. Sign up at [railway.app](https://railway.app)
2. Connect your GitHub repo
3. Deploy automatically

### Option 2: Vercel
**Best for**: Serverless, great for small apps

### Option 3: Render
**Best for**: Persistent SQLite database

---

## Option 1: Railway Deployment (Recommended)

### Step 1: Prepare Your Repository
```bash
# Ensure your code is committed
git status  # should be clean

# Push to GitHub (if not already)
git push origin main
```

### Step 2: Set Up Railway
1. Go to [railway.app](https://railway.app) and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Select your `sports-facts` repository
4. Railway will auto-detect Python and install dependencies

### Step 3: Add Environment Variables
In Railway Dashboard → Your Project → Variables, add:

```
OPENROUTER_API_KEY=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
SENDGRID_API_KEY=your_sendgrid_api_key_here
FROM_EMAIL=facts@sportsfacts.app
FROM_NAME=Sports Facts
ADMIN_SECRET=your-secret-admin-key
PYTHON_VERSION=3.9
```

### Step 4: Deploy
Railway will automatically deploy on every push to main!

Your app will be live at: `https://sports-facts-production.up.railway.app`

---

## Option 2: Vercel Deployment

### Step 1: Install Vercel CLI
```bash
npm i -g vercel
```

### Step 2: Deploy
```bash
vercel --prod
```

### Step 3: Add Environment Variables
In Vercel Dashboard → Project Settings → Environment Variables, add the same vars as above.

**Note**: Vercel is serverless, so SQLite won't persist between requests. Consider:
- Using Vercel KV (Redis)
- Or switching to Railway for SQLite persistence

---

## Option 3: Render Deployment

### Step 1: Create Render Account
Go to [render.com](https://render.com)

### Step 2: Create Web Service
1. Click "New" → "Web Service"
2. Connect your GitHub repo
3. Settings:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Add Environment Variables
Same as Railway above.

---

## Post-Deployment Checklist

### 1. Test Your Endpoints
```bash
# Replace with your actual domain
curl https://your-app.com/api/generate?sport=nba
curl https://your-app.com/api/sports
curl https://your-app.com/healthz
```

### 2. Set Up SendGrid (for emails)
1. Sign up at [sendgrid.com](https://sendgrid.com)
2. Verify your sender email
3. Get API key from Settings → API Keys
4. Add to environment variables
5. Test email: `POST /api/email/send-test?email=you@example.com`

### 3. Set Up Daily Cron Job
For Railway, create a cron job service:
```bash
# Add to railway.yml or use Railway's cron feature
0 9 * * * curl -X POST https://your-app.com/api/email/send-daily?secret=your-admin-secret
```

Or use GitHub Actions (free):
1. Create `.github/workflows/daily-email.yml`
2. Schedule daily trigger

### 4. Custom Domain (Optional)
- Railway: Go to Settings → Domains
- Vercel: Project Settings → Domains
- Render: Settings → Custom Domains

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENROUTER_API_KEY` | ✅ Yes | Your OpenRouter API key |
| `SENDGRID_API_KEY` | ❌ No | For email features |
| `FROM_EMAIL` | ❌ No | Sender email address |
| `FROM_NAME` | ❌ No | Sender name |
| `ADMIN_SECRET` | ❌ No | Secret for admin endpoints |
| `DATABASE_URL` | ❌ No | Defaults to SQLite |

---

## Troubleshooting

### Issue: App won't start
**Solution**: Check logs in platform dashboard. Common issues:
- Missing environment variables
- Port not set correctly (use `$PORT` env var)

### Issue: SQLite database resets
**Solution**: Use Railway or Render (persistent disk). Vercel is serverless.

### Issue: Emails not sending
**Solution**: 
1. Verify SendGrid API key
2. Check sender email is verified in SendGrid
3. Check spam folders

### Issue: CORS errors
**Solution**: Update `app/main.py` with allowed origins:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Recommended: Railway (Why?)

✅ **Free tier** - 500 hours/month
✅ **Persistent SQLite** - Database survives restarts
✅ **Automatic HTTPS** - SSL certificate included
✅ **Easy env vars** - Web UI for configuration
✅ **Git integration** - Auto-deploy on push
✅ **Good for Python** - Native Python support

---

## Next Steps After Deployment

1. ✅ Test all endpoints
2. ✅ Set up SendGrid for emails
3. ✅ Configure daily cron job
4. ✅ Add custom domain (optional)
5. ✅ Set up Google Analytics
6. ✅ Share your app! 🎉

**Need Help?** Check platform-specific docs:
- Railway: [docs.railway.app](https://docs.railway.app)
- Vercel: [vercel.com/docs](https://vercel.com/docs)
- Render: [render.com/docs](https://render.com/docs)

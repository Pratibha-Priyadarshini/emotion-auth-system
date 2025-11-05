# 🚀 Deploy to Render.com - Simple Guide

## Prerequisites
- GitHub account
- Render.com account (free tier available)

---

## Step 1: Push to GitHub (5 minutes)

### 1.1 Create GitHub Repository
1. Go to: https://github.com/new
2. Repository name: `emotion-auth-system`
3. Make it **Public** (easier for free Render deployment)
4. **DO NOT** add README, .gitignore, or license
5. Click "Create repository"

### 1.2 Push Your Code
After creating the repo, run these commands:

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/emotion-auth-system.git
git branch -M main
git push -u origin main
```

---

## Step 2: Deploy on Render (5 minutes)

### 2.1 Create Render Account
1. Go to: https://render.com
2. Sign up with GitHub (recommended)
3. Authorize Render to access your repositories

### 2.2 Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your `emotion-auth-system` repository
3. Configure the service:

**Basic Settings:**
- **Name:** `emotion-auth-system` (or your choice)
- **Region:** Choose closest to you
- **Branch:** `main`
- **Root Directory:** Leave empty
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT`

**Instance Type:**
- Select **Free** tier

### 2.3 Environment Variables
Click **"Advanced"** and add these environment variables:

```
SECRET_KEY=your-secret-key-here-change-this
DATABASE_URL=sqlite:///./storage/app.db
CORS_ORIGINS=*
```

### 2.4 Deploy
1. Click **"Create Web Service"**
2. Wait 5-10 minutes for deployment
3. Render will show you the live URL (e.g., `https://emotion-auth-system.onrender.com`)

---

## Step 3: Test Your Deployment

Once deployed, visit:
- **Frontend:** `https://your-app.onrender.com/`
- **API Docs:** `https://your-app.onrender.com/docs`
- **Health Check:** `https://your-app.onrender.com/health`

---

## Important Notes

### Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after inactivity takes 30-60 seconds (cold start)
- 750 hours/month free

### Troubleshooting

**If deployment fails:**
1. Check Render logs (click "Logs" tab)
2. Verify all files are pushed to GitHub
3. Ensure requirements.txt is in root directory

**If models don't work:**
- Pre-trained models are included in the repo
- They should work immediately after deployment

**Database:**
- SQLite database will be created automatically
- Data persists on Render's disk (but may be lost on redeploy)

---

## Upgrade Options

For production use, consider:
- **Paid Render Plan** ($7/month) - No cold starts, always on
- **PostgreSQL Database** - Better for production
- **Custom Domain** - Use your own domain name

---

## Need Help?

Check the logs in Render dashboard for any errors.

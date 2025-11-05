# 🚀 Deployment Guide

## Live Demo

**Current Deployment:** [https://emotion-auth-system-1.onrender.com](https://emotion-auth-system-1.onrender.com)

---

## Quick Deploy to Render.com

### Prerequisites
- GitHub account
- Render.com account (free tier available)

### Step 1: Push to GitHub
```bash
git push origin main
```

### Step 2: Create Web Service on Render
1. Go to [https://render.com](https://render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository

### Step 3: Configure Service

**Build Settings:**
```
Build Command: pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Environment Variables:**
```
PYTHON_VERSION=3.11.9
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///./storage/app.db
CORS_ORIGINS=*
```

**Instance Type:** Free (or Starter for better performance)

### Step 4: Deploy
Click **"Create Web Service"** and wait 8-12 minutes for build.

---

## What's Included

- ✅ TensorFlow 2.15.1 (CPU optimized)
- ✅ Facial emotion recognition (CNN)
- ✅ Voice emotion analysis (Random Forest)
- ✅ Keystroke dynamics (Isolation Forest)
- ✅ Multi-factor authentication
- ✅ Admin dashboard
- ✅ MFA integration plugins
- ✅ Pre-trained models

---

## Troubleshooting

### Build Fails
**Issue:** Dependency conflicts or Python version issues

**Solution:**
- Ensure `PYTHON_VERSION=3.11.9` is set in environment variables
- Check Render logs for specific errors
- Try "Clear build cache & deploy"

### Import Errors
**Issue:** `ImportError: attempted relative import`

**Solution:**
- Verify start command is: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- Do NOT use `cd backend` in start command

### Slow Performance
**Issue:** Cold starts on free tier

**Solution:**
- Free tier sleeps after 15 min inactivity
- First request takes 30-60 seconds
- Upgrade to Starter plan ($7/month) for always-on service

### Models Not Loading
**Issue:** Model files missing or incompatible

**Solution:**
- Verify models exist in `backend/storage/trained_models/`
- Check scikit-learn version matches (1.4.2)
- Review Render logs for loading errors

---

## Local Development

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Start server
uvicorn backend.main:app --reload --port 8000
```

### Access Locally
- Frontend: http://localhost:8000/web/index.html
- Admin: http://localhost:8000/web/admin.html
- API Docs: http://localhost:8000/docs

---

## Production Recommendations

### For Production Use:
1. **Upgrade to Paid Plan** - No cold starts, better performance
2. **Use PostgreSQL** - Replace SQLite for persistent data
3. **Custom Domain** - Add your own domain with free SSL
4. **Environment Security** - Use strong SECRET_KEY
5. **CORS Configuration** - Restrict to specific domains
6. **Monitoring** - Set up logging and alerts

---

## Additional Resources

- **Render Troubleshooting:** [RENDER_TROUBLESHOOTING.md](RENDER_TROUBLESHOOTING.md)
- **TensorFlow Deployment:** [DEPLOY_WITH_TENSORFLOW.md](DEPLOY_WITH_TENSORFLOW.md)
- **Success Guide:** [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md)
- **MFA Integration:** [mfa-integration/DEPLOYMENT.md](mfa-integration/DEPLOYMENT.md)

---

## Support

For issues or questions:
- Check Render logs first
- Review troubleshooting docs
- Open GitHub issue

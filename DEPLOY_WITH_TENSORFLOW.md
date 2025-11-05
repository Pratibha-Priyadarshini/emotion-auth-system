# 🚀 Deploy with TensorFlow & MFA Integration

## ✅ What's Included in This Deployment

- **TensorFlow CNN** for facial emotion recognition
- **Voice emotion analysis** with Random Forest
- **Keystroke dynamics** with Isolation Forest
- **MFA integration** plugins (WordPress, JavaScript)
- **Admin dashboard** for monitoring
- **Pre-trained models** ready to use

---

## 🎯 Critical Setup Steps

### Step 1: Go to Render Dashboard
Visit: https://dashboard.render.com

### Step 2: Create New Web Service
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository: `emotion-auth-system`
3. Configure with these **EXACT** settings:

---

## ⚙️ Configuration Settings

### Basic Settings
```
Name: emotion-auth-system
Region: Choose closest to you
Branch: main
Root Directory: (leave empty)
Runtime: Python 3
```

### Build & Deploy Settings
```
Build Command:
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt

Start Command:
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Instance Type
- **Free Tier:** Works but TensorFlow loads slowly (30-60 sec cold start)
- **Starter ($7/month):** Recommended for TensorFlow - faster, always on

---

## 🔑 Environment Variables (CRITICAL!)

Click **"Advanced"** and add these **EXACTLY**:

```
PYTHON_VERSION=3.11.9
SECRET_KEY=your-secret-key-change-this-to-something-random
DATABASE_URL=sqlite:///./storage/app.db
CORS_ORIGINS=*
```

### Why Each Variable Matters:

1. **PYTHON_VERSION=3.11.9** 
   - **MOST IMPORTANT!** Without this, Render uses Python 3.13
   - Python 3.13 doesn't have TensorFlow wheels yet
   - This will cause build failures

2. **SECRET_KEY**
   - Used for JWT tokens and session security
   - Change to a random string (at least 32 characters)

3. **DATABASE_URL**
   - SQLite database location
   - Data persists between requests but may be lost on redeploy

4. **CORS_ORIGINS**
   - Allows frontend to access API
   - Use `*` for testing, specific domain for production

---

## 🚀 Deploy!

1. Click **"Create Web Service"**
2. Wait 8-12 minutes for build (TensorFlow takes time)
3. Watch the logs for progress

### What You'll See in Logs:

```
==> Installing dependencies
==> Installing tensorflow-cpu==2.13.0 (this takes 5-8 minutes)
==> Build succeeded
==> Starting service
==> Loaded facial emotion model
==> Loaded voice emotion model
==> Loaded keystroke dynamics models
==> Service running on port XXXX
```

---

## ✅ Test Your Deployment

Once deployed, you'll get a URL like: `https://emotion-auth-system.onrender.com`

### Test These Endpoints:

1. **Frontend:** `https://your-app.onrender.com/`
2. **API Docs:** `https://your-app.onrender.com/docs`
3. **Health Check:** `https://your-app.onrender.com/health`
4. **Admin Dashboard:** `https://your-app.onrender.com/web/admin.html`

---

## 📊 What to Expect

### First Deploy (8-12 minutes)
- Installing TensorFlow takes the longest
- Other packages install quickly
- Models load automatically from repo

### Cold Starts (Free Tier)
- Service sleeps after 15 min inactivity
- First request takes 30-60 seconds
- TensorFlow model loads on first request

### Performance
- **Free Tier:** Works but slow cold starts
- **Starter Plan:** Much faster, always on, recommended for production

---

## 🔧 Troubleshooting

### Build Fails with "Cannot import setuptools"
**Cause:** Python 3.13 being used instead of 3.11
**Fix:** Add `PYTHON_VERSION=3.11.9` to environment variables

### Build Fails with "No matching distribution for numpy"
**Cause:** Same as above - wrong Python version
**Fix:** Ensure `PYTHON_VERSION=3.11.9` is set

### TensorFlow Installation Timeout
**Cause:** Free tier has limited resources
**Fix:** 
- Wait and retry (sometimes works on second attempt)
- Or upgrade to Starter plan ($7/month)

### Service Crashes on Startup
**Check logs for:**
- Missing environment variables
- Model loading errors
- Port binding issues

**Common fixes:**
- Verify all environment variables are set
- Check that models exist in `backend/storage/trained_models/`
- Ensure start command is correct

---

## 📁 MFA Integration

Your deployment includes MFA integration plugins in `/mfa-integration/`:

- **WordPress Plugin:** Ready to install on WordPress sites
- **JavaScript Plugin:** For any web application
- **REST API:** Full documentation in `/mfa-integration/REST_API_DOCS.md`

Access integration docs at: `https://your-app.onrender.com/mfa-integration/`

---

## 🎊 Success Checklist

After deployment, verify:

- [ ] App loads at your Render URL
- [ ] API docs accessible at `/docs`
- [ ] Can register a new user
- [ ] Facial emotion detection works (webcam access)
- [ ] Voice emotion analysis works (microphone access)
- [ ] Keystroke dynamics captures typing patterns
- [ ] Admin dashboard shows users and logs
- [ ] MFA integration docs accessible

---

## 💡 Pro Tips

1. **Use Starter Plan for Production**
   - No cold starts
   - Better TensorFlow performance
   - More reliable

2. **Upgrade to PostgreSQL**
   - SQLite data can be lost on redeploy
   - PostgreSQL persists data permanently
   - Easy to add in Render dashboard

3. **Monitor Logs**
   - Check logs regularly for errors
   - Watch for security violations
   - Monitor authentication attempts

4. **Custom Domain**
   - Add your own domain in Render settings
   - Free SSL certificate included
   - Professional appearance

---

## 🆘 Still Having Issues?

1. Check `RENDER_TROUBLESHOOTING.md`
2. Check `RENDER_PYTHON_FIX.md`
3. Review Render logs carefully
4. Ensure all environment variables are set correctly

---

## 🎉 You're All Set!

Your emotion-aware authentication system with TensorFlow and MFA integration is now live!

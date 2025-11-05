# Deploy to Render.com (Free - No Credit Card)

## ✅ Why Render?
- **Truly free** - No credit card required
- **750 hours/month** free tier
- **Automatic HTTPS** - Camera/microphone will work
- **Easy as Heroku** - Similar interface
- **Public URL** - Share with anyone

---

## 🚀 Quick Deployment (10 minutes)

### Step 1: Push to GitHub (5 minutes)

**If you don't have GitHub account:**
1. Go to: https://github.com/signup
2. Create free account

**Push your code:**
```powershell
# Create new repo on GitHub (via website)
# Then run these commands:

git remote add origin https://github.com/YOUR_USERNAME/emotion-auth-system.git
git branch -M main
git push -u origin main
```

---

### Step 2: Deploy on Render (5 minutes)

1. **Go to:** https://render.com/

2. **Sign Up:**
   - Click "Get Started for Free"
   - Sign up with GitHub (easiest)
   - Or use email

3. **Create Web Service:**
   - Click "New +" button
   - Select "Web Service"
   - Click "Connect GitHub"
   - Authorize Render
   - Select your repository: `emotion-auth-system`

4. **Configure Service:**
   ```
   Name: emotion-auth-system
   Region: Choose closest to you
   Branch: main
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```

5. **Select Free Plan:**
   - Instance Type: Free
   - Click "Create Web Service"

6. **Wait for Deployment:**
   - Takes 2-5 minutes
   - Watch the logs
   - Wait for "Your service is live 🎉"

7. **Get Your URL:**
   - Copy the URL (e.g., `https://emotion-auth-system.onrender.com`)
   - Add `/web/index.html` to access app

---

## 📱 Access Your App

**Authentication:**
```
https://your-app-name.onrender.com/web/index.html
```

**Admin Dashboard:**
```
https://your-app-name.onrender.com/web/admin.html
```

**API Docs:**
```
https://your-app-name.onrender.com/docs
```

---

## ⚠️ Free Tier Limitations

- **Spins down after 15 min** of inactivity
- **Wakes up** on first request (10-30 seconds)
- **750 hours/month** (enough for most use)

**Upgrade to Paid ($7/month) for:**
- No sleeping
- Better performance
- Custom domain

---

## 🔧 Useful Features

### View Logs:
- Go to your service dashboard
- Click "Logs" tab
- See real-time logs

### Redeploy:
- Push changes to GitHub
- Render auto-deploys
- Or click "Manual Deploy" in dashboard

### Environment Variables:
- Go to "Environment" tab
- Add variables like:
  - `SECRET_KEY=your-secret`
  - `DATABASE_URL=your-db-url`

---

## 📊 Monitoring

**In Render Dashboard:**
- View metrics
- Check uptime
- Monitor requests
- See error rates

---

## ✅ Checklist

- [ ] GitHub account created
- [ ] Code pushed to GitHub
- [ ] Render account created
- [ ] Web service created
- [ ] Deployment successful
- [ ] App tested and working
- [ ] URL shared

---

## 🆘 Troubleshooting

### Build Failed
**Check:**
- requirements.txt exists
- All dependencies listed
- Python version compatible

### App Not Starting
**Check:**
- Start command is correct
- Port is $PORT (not 8000)
- Logs for errors

### Camera Not Working
**Solution:**
- Render provides HTTPS automatically
- Check browser permissions
- Allow camera/microphone

---

## 💡 Tips

1. **Custom Domain:**
   - Add in "Settings" → "Custom Domain"
   - Free on all plans

2. **Auto-Deploy:**
   - Enabled by default
   - Push to GitHub = Auto deploy

3. **Health Checks:**
   - Render pings your app
   - Keeps it awake (on paid plans)

---

**Ready?** Follow Step 1 to push to GitHub, then Step 2 to deploy!


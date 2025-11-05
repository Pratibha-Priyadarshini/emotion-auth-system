# Heroku Deployment - Step by Step Guide

## ✅ Prerequisites Completed
- [x] Git initialized
- [x] .gitignore created
- [x] Procfile created
- [x] runtime.txt created
- [x] Requirements ready

## 📋 Step-by-Step Instructions

### Step 1: Install Heroku CLI

**Option A: Using Installer (Recommended)**
1. Download Heroku CLI from: https://devcenter.heroku.com/articles/heroku-cli
2. Run the installer
3. Restart your terminal/PowerShell
4. Verify installation: `heroku --version`

**Option B: Using Chocolatey (if you have it)**
```powershell
choco install heroku-cli
```

**Option C: Using npm (if you have Node.js)**
```powershell
npm install -g heroku
```

---

### Step 2: Create Heroku Account

1. Go to: https://signup.heroku.com/
2. Sign up for free account
3. Verify your email
4. Login to dashboard

---

### Step 3: Prepare Your Project

**Run these commands in PowerShell:**

```powershell
# Add all files to Git
git add .

# Commit files
git commit -m "Initial commit for Heroku deployment"

# Verify files are committed
git status
```

---

### Step 4: Login to Heroku

```powershell
# This will open browser for authentication
heroku login
```

---

### Step 5: Create Heroku App

```powershell
# Create app with a unique name
heroku create your-emotion-auth-app

# Or let Heroku generate a random name
heroku create
```

**Note:** App name must be unique across all Heroku. Try:
- `emotion-auth-yourname`
- `mfa-emotion-system`
- `biometric-auth-app`

---

### Step 6: Deploy to Heroku

```powershell
# Push code to Heroku
git push heroku main

# If you're on master branch instead:
git push heroku master
```

**This will:**
- Upload your code
- Install Python dependencies
- Build the application
- Start the server

---

### Step 7: Open Your App

```powershell
# Open in browser
heroku open

# Or manually visit:
# https://your-app-name.herokuapp.com/web/index.html
```

---

### Step 8: View Logs (if needed)

```powershell
# View real-time logs
heroku logs --tail

# View recent logs
heroku logs --num 100
```

---

## 🎯 Quick Commands Reference

```powershell
# Check app status
heroku ps

# Restart app
heroku restart

# Open app
heroku open

# View logs
heroku logs --tail

# Run commands on Heroku
heroku run python --version

# Check environment variables
heroku config

# Set environment variable
heroku config:set KEY=VALUE
```

---

## 🔧 Troubleshooting

### Issue: "App name already taken"
**Solution:** Choose a different name
```powershell
heroku create different-app-name
```

### Issue: "No such app"
**Solution:** Link to existing app
```powershell
heroku git:remote -a your-app-name
```

### Issue: "Application error"
**Solution:** Check logs
```powershell
heroku logs --tail
```

### Issue: "Build failed"
**Solution:** Check requirements.txt and Python version
```powershell
# Verify files exist
ls Procfile
ls runtime.txt
ls requirements.txt
```

### Issue: "Camera/Microphone not working"
**Solution:** Heroku provides HTTPS by default, so it should work. 
Make sure to:
1. Allow browser permissions
2. Use the HTTPS URL (not HTTP)

---

## 📱 After Deployment

### Access Your Application:
- **Authentication Page:** https://your-app-name.herokuapp.com/web/index.html
- **Admin Dashboard:** https://your-app-name.herokuapp.com/web/admin.html
- **API Documentation:** https://your-app-name.herokuapp.com/docs

### Test Everything:
1. ✅ Camera access
2. ✅ Microphone access
3. ✅ User enrollment
4. ✅ Authentication
5. ✅ Admin dashboard
6. ✅ Security alerts

---

## 💰 Heroku Free Tier Limits

**Free Dyno:**
- 550-1000 free dyno hours/month
- Sleeps after 30 minutes of inactivity
- Wakes up on first request (may take 10-30 seconds)

**Upgrade to Hobby ($7/month) for:**
- No sleeping
- Custom domain
- Better performance
- SSL certificates

```powershell
# Upgrade to Hobby
heroku ps:resize web=hobby
```

---

## 🔐 Production Improvements

### 1. Add PostgreSQL (Recommended)
```powershell
# Add free PostgreSQL
heroku addons:create heroku-postgresql:mini

# Get database URL
heroku config:get DATABASE_URL
```

### 2. Set Environment Variables
```powershell
heroku config:set SECRET_KEY=your-secret-key
heroku config:set ADMIN_PASSWORD=secure-password
```

### 3. Enable Metrics
```powershell
# View metrics in dashboard
heroku open --app your-app-name
# Click on "Metrics" tab
```

### 4. Setup Custom Domain
```powershell
heroku domains:add www.yourdomain.com
```

---

## 📊 Monitoring

### View App Metrics:
1. Go to: https://dashboard.heroku.com/apps/your-app-name
2. Click "Metrics" tab
3. Monitor:
   - Response time
   - Memory usage
   - Request volume

### Setup Alerts:
1. Go to app settings
2. Configure email notifications
3. Set thresholds for errors

---

## 🔄 Updating Your App

```powershell
# Make changes to your code
# Then:

git add .
git commit -m "Update description"
git push heroku main

# App will automatically redeploy
```

---

## 🆘 Need Help?

**Heroku Documentation:**
- Getting Started: https://devcenter.heroku.com/start
- Python Guide: https://devcenter.heroku.com/articles/getting-started-with-python
- Troubleshooting: https://devcenter.heroku.com/articles/troubleshooting

**Check Status:**
- Heroku Status: https://status.heroku.com/

**Support:**
- Help Center: https://help.heroku.com/
- Community: https://stackoverflow.com/questions/tagged/heroku

---

## ✅ Deployment Checklist

- [ ] Heroku CLI installed
- [ ] Heroku account created
- [ ] Git repository initialized
- [ ] Files committed to Git
- [ ] Logged into Heroku
- [ ] App created on Heroku
- [ ] Code pushed to Heroku
- [ ] App opened and tested
- [ ] Camera/microphone working
- [ ] Admin dashboard accessible

---

**Ready to start?** Follow Step 1 above to install Heroku CLI!


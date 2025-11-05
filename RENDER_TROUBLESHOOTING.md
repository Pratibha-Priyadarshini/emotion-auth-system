# 🔧 Render Deployment Troubleshooting

## Build Failed with TensorFlow Error

**Problem:** Build fails with error about pip subprocess or TensorFlow installation

**Solution 1: Use Lighter Requirements (Recommended)**
1. In Render dashboard, go to your service
2. Click **"Settings"**
3. Change **Build Command** to:
   ```
   pip install -r requirements-light.txt
   ```
4. Click **"Save Changes"**
5. Render will automatically redeploy

This version excludes TensorFlow and uses the heuristic facial emotion model (which is actually more accurate for this use case).

**Solution 2: Use TensorFlow CPU Version**
The main `requirements.txt` already uses `tensorflow-cpu==2.13.0` which is lighter than full TensorFlow. If build still fails:
1. Try increasing the instance type (requires paid plan)
2. Or use Solution 1 above

---

## Service Takes Long to Start

**Problem:** First request takes 30-60 seconds

**Cause:** Free tier services spin down after 15 minutes of inactivity (cold start)

**Solutions:**
- **Free:** Accept the cold start delay
- **Paid ($7/month):** Upgrade to paid plan for always-on service
- **Workaround:** Use a service like UptimeRobot to ping your app every 10 minutes

---

## Database Errors

**Problem:** SQLite database errors or data loss

**Cause:** Render's disk is ephemeral on free tier

**Solutions:**
1. **For testing:** Accept that data may be lost on redeploy
2. **For production:** Upgrade to PostgreSQL:
   - Create PostgreSQL database in Render
   - Update `DATABASE_URL` environment variable
   - Modify `backend/db.py` to use PostgreSQL connection string

---

## CORS Errors in Browser

**Problem:** Browser shows CORS policy errors

**Solution:**
1. In Render dashboard, go to **Environment**
2. Add/update:
   ```
   CORS_ORIGINS=*
   ```
3. Or specify your frontend domain:
   ```
   CORS_ORIGINS=https://yourdomain.com
   ```

---

## Models Not Working

**Problem:** Emotion detection returns errors

**Check:**
1. Verify trained models are in `backend/storage/trained_models/`
2. Check Render logs for model loading errors
3. If using `requirements-light.txt`, facial emotion uses heuristic (no TensorFlow needed)

**Note:** Pre-trained models are included in the repo and should work automatically.

---

## Environment Variables Not Set

**Problem:** App crashes with missing environment variable errors

**Solution:**
1. Go to Render dashboard → **Environment**
2. Add required variables:
   ```
   SECRET_KEY=your-secret-key-change-this
   DATABASE_URL=sqlite:///./storage/app.db
   CORS_ORIGINS=*
   ```
3. Click **"Save Changes"**

---

## Check Logs

Always check Render logs first:
1. Go to your service in Render dashboard
2. Click **"Logs"** tab
3. Look for error messages

Common log messages:
- `ModuleNotFoundError`: Missing dependency in requirements.txt
- `Port already in use`: Incorrect start command
- `Permission denied`: File permission issues

---

## Still Having Issues?

1. Check that all files are pushed to GitHub
2. Verify `requirements.txt` is in root directory
3. Ensure `runtime.txt` specifies Python 3.11.6
4. Try redeploying: **Manual Deploy** → **Clear build cache & deploy**

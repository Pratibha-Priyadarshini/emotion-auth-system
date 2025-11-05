# 🔧 Fix Python Version on Render

## Problem
Render is using Python 3.13 instead of Python 3.11, causing build failures.

---

## Solution: Manually Set Python Version

### In Render Dashboard:

1. Go to your service settings
2. Scroll to **"Environment"** section
3. Add this environment variable:

```
PYTHON_VERSION=3.11.9
```

4. Click **"Save Changes"**
5. Render will automatically redeploy

---

## Alternative: Use Build Command Override

If the environment variable doesn't work, try this build command:

```bash
pip install --upgrade pip setuptools wheel && pip install -r requirements.txt
```

This ensures pip and setuptools are updated before installing dependencies.

---

## Why This Happens

- Render defaults to Python 3.13 (latest)
- Some packages (like numpy, scikit-learn) don't have wheels for 3.13 yet
- Python 3.11 has better package compatibility

---

## After Setting Python Version

Your build should complete successfully in 3-5 minutes.

If you still see errors, check `RENDER_TROUBLESHOOTING.md`

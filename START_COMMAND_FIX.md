# 🔧 Start Command Fix

## Problem
The current start command causes import errors:
```
cd backend && uvicorn main:app --host 0.0.0.0 --port $PORT
```

Error: `ImportError: attempted relative import with no known parent package`

## Solution

Change the **Start Command** in Render to:

```bash
uvicorn backend.main:app --host 0.0.0.0 --port $PORT
```

**Do NOT use `cd backend`** - run from the root directory instead.

---

## How to Fix in Render

1. Go to your service in Render dashboard
2. Click **"Settings"** tab
3. Scroll to **"Start Command"**
4. Change it to:
   ```
   uvicorn backend.main:app --host 0.0.0.0 --port $PORT
   ```
5. Click **"Save Changes"**
6. Render will automatically redeploy

---

## Why This Works

- Running from root directory allows Python to treat `backend` as a package
- `backend.main:app` correctly imports the app with relative imports
- No need to change directory

---

Your app should start successfully after this change! 🚀

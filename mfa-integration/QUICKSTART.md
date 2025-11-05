# 🚀 Quick Start Guide

Get emotion-aware MFA running in 5 minutes!

---

## Step 1: Start the Backend Server

### Option A: Using Existing Backend

If you already have the emotion-auth backend running:

```bash
# Make sure it's running on http://localhost:8000
curl http://localhost:8000/docs
```

### Option B: Start Backend from Scratch

```bash
# Navigate to project root
cd ..

# Install dependencies
pip install -r backend/requirements.txt

# Start server
python -m uvicorn backend.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000

---

## Step 2: Test the Integration

### Option A: Open the Example Page

```bash
# From mfa-integration directory
python -m http.server 8080
```

Then open: http://localhost:8080/example-integration.html

### Option B: Try the Demo

1. Open `example-integration.html` in your browser
2. Click "Login with MFA"
3. Allow camera and microphone access
4. Follow the on-screen instructions
5. See the MFA verification in action!

---

## Step 3: Integrate Into Your Website

### For Frontend Integration

1. **Copy the plugin file:**
   ```bash
   cp emotion-mfa-plugin.js /path/to/your/website/js/
   ```

2. **Include in your HTML:**
   ```html
   <script src="js/emotion-mfa-plugin.js"></script>
   ```

3. **Add to your login flow:**
   ```javascript
   const mfa = new EmotionMFA({
       apiUrl: 'http://localhost:8000'
   });
   
   // After username/password verification
   const result = await mfa.verify(username);
   if (result.success) {
       // Grant access
       window.location.href = '/dashboard';
   }
   ```

### For Backend Integration

#### Flask

```bash
# Install
pip install -e .

# Use in your app
from mfa_backend_adapter import FlaskMFAMiddleware

app = Flask(__name__)
mfa = FlaskMFAMiddleware(app, emotion_api_url='http://localhost:8000')

@app.route('/dashboard')
@mfa.require_mfa
def dashboard():
    return 'Welcome!'
```

#### Django

```bash
# Install
pip install -e .

# Add to settings.py
MIDDLEWARE = [
    'mfa_backend_adapter.DjangoMFAMiddleware',
]
```

#### FastAPI

```bash
# Install
pip install -e .

# Use in your app
from mfa_backend_adapter import FastAPIMFAMiddleware

app = FastAPI()
mfa = FastAPIMFAMiddleware(emotion_api_url='http://localhost:8000')

@app.get('/dashboard')
@mfa.require_mfa
async def dashboard():
    return {'message': 'Welcome!'}
```

---

## Step 4: Customize (Optional)

### Change Theme

```javascript
const mfa = new EmotionMFA({
    apiUrl: 'http://localhost:8000',
    theme: 'dark'  // or 'light'
});
```

### Select Biometric Factors

```javascript
await mfa.verify(username, {
    requireFace: true,
    requireVoice: true,
    requireKeystroke: false
});
```

### Add Progress Callback

```javascript
const mfa = new EmotionMFA({
    apiUrl: 'http://localhost:8000',
    onProgress: (message, percent) => {
        console.log(`${message}: ${percent}%`);
        document.getElementById('progress').style.width = percent + '%';
    }
});
```

---

## Common Integration Patterns

### Pattern 1: After Username/Password

```javascript
async function login(username, password) {
    // Step 1: Verify credentials
    const authResponse = await fetch('/api/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
    
    if (!authResponse.ok) {
        alert('Invalid credentials');
        return;
    }
    
    // Step 2: MFA verification
    const mfaResult = await mfa.verify(username);
    
    if (mfaResult.success) {
        window.location.href = '/dashboard';
    } else {
        alert('MFA failed: ' + mfaResult.message);
    }
}
```

### Pattern 2: Protect Sensitive Actions

```javascript
async function transferMoney(amount, recipient) {
    // Require MFA before sensitive action
    const mfaResult = await mfa.quickVerify(currentUser);
    
    if (!mfaResult.success) {
        alert('MFA verification required');
        return;
    }
    
    // Proceed with transfer
    await fetch('/api/transfer', {
        method: 'POST',
        body: JSON.stringify({ amount, recipient })
    });
}
```

### Pattern 3: Periodic Re-verification

```javascript
// Re-verify every 30 minutes
setInterval(async () => {
    const mfaResult = await mfa.quickVerify(currentUser);
    
    if (!mfaResult.success) {
        // Session expired, redirect to login
        window.location.href = '/login?session_expired=true';
    }
}, 30 * 60 * 1000);
```

---

## Testing

### Test with Simulation

```javascript
// Test without actual biometric capture
const result = await fetch('http://localhost:8000/api/test/simulate?stress_level=0.3&match_score=0.8');
const data = await result.json();
console.log(data.simulation.decision);
```

### Test Different Scenarios

```javascript
// Low stress, good match -> Should permit
await testScenario(0.2, 0.9);

// High stress, poor match -> Should deny
await testScenario(0.9, 0.3);

// Medium stress, medium match -> Should delay
await testScenario(0.5, 0.5);

async function testScenario(stress, match) {
    const result = await fetch(
        `http://localhost:8000/api/test/simulate?stress_level=${stress}&match_score=${match}`
    );
    const data = await result.json();
    console.log(`Stress: ${stress}, Match: ${match} -> ${data.simulation.decision}`);
}
```

---

## Troubleshooting

### Issue: Camera/Microphone Access Denied

**Solution:**
- Use HTTPS (required for camera/mic in production)
- Check browser permissions
- Try in a different browser

### Issue: API Connection Failed

**Solution:**
```bash
# Check if backend is running
curl http://localhost:8000/docs

# Check CORS settings in backend
# Make sure your frontend domain is allowed
```

### Issue: MFA Always Fails

**Solution:**
1. Check API key is correct
2. Review logs: `GET http://localhost:8000/api/admin/logs`
3. Test in simulation mode first
4. Verify user is enrolled (for keystroke dynamics)

### Issue: Slow Performance

**Solution:**
- Reduce image quality in capture
- Use `quickVerify()` for faster verification
- Disable unused biometric factors
- Check network latency

---

## Next Steps

1. ✅ **Read the full integration guide:** [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
2. ✅ **Review API documentation:** [REST_API_DOCS.md](REST_API_DOCS.md)
3. ✅ **Customize the UI** to match your brand
4. ✅ **Set up monitoring** and alerts
5. ✅ **Deploy to production** using the deployment guide

---

## Production Checklist

Before going live:

- [ ] Use HTTPS for all connections
- [ ] Store API keys in environment variables
- [ ] Enable rate limiting
- [ ] Set up logging and monitoring
- [ ] Configure email alerts
- [ ] Test on multiple browsers
- [ ] Test on mobile devices
- [ ] Set up backup authentication method
- [ ] Create user documentation
- [ ] Train support team

---

## Support

Need help? We're here for you!

- 📧 Email: support@emotion-auth.com
- 💬 Discord: https://discord.gg/emotion-auth
- 📖 Docs: https://docs.emotion-auth.com
- 🐛 Issues: https://github.com/your-org/emotion-auth-mfa/issues

---

**Happy coding! 🚀**

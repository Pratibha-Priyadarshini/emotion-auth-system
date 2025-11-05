# 🔐 Emotion-Aware MFA Integration Package

Add emotion-aware multi-factor authentication to **any website** in minutes!

This package provides everything you need to integrate advanced biometric MFA (facial recognition, voice analysis, and keystroke dynamics) into your existing authentication system.

---

## ✨ Features

- 🎭 **Facial Emotion Recognition** - Detect stress, fear, and coercion
- 🎤 **Voice Analysis** - Analyze vocal patterns and stress levels
- ⌨️ **Keystroke Dynamics** - Verify typing patterns
- 🚨 **Coercion Detection** - Identify forced authentication attempts
- 🔌 **Easy Integration** - Works with any web framework
- 🎨 **Customizable UI** - Light/dark themes, custom styling
- 📱 **Responsive** - Works on desktop and mobile
- 🔒 **Secure** - End-to-end encrypted communication

---

## 🚀 Quick Start

### 1. Include the Plugin

```html
<script src="emotion-mfa-plugin.js"></script>
```

### 2. Initialize

```javascript
const mfa = new EmotionMFA({
    apiUrl: 'https://your-emotion-auth-server.com',
    apiKey: 'your-api-key'
});
```

### 3. Use After Login

```javascript
// After username/password verification
const result = await mfa.verify(userId);

if (result.success) {
    // Grant access
    window.location.href = '/dashboard';
} else {
    // Show error
    alert(result.message);
}
```

**That's it!** 🎉

---

## 📦 What's Included

```
mfa-integration/
├── emotion-mfa-plugin.js          # Frontend JavaScript plugin
├── mfa-backend-adapter.py         # Backend adapters (Flask, Django, FastAPI)
├── example-integration.html       # Complete working example
├── INTEGRATION_GUIDE.md           # Detailed integration guide
├── REST_API_DOCS.md              # Complete API documentation
└── wordpress-plugin/              # WordPress plugin
    └── emotion-mfa.php
```

---

## 🎯 Use Cases

### 1. **Banking & Finance**
Add an extra layer of security to prevent unauthorized access and detect coercion.

### 2. **Healthcare Systems**
Ensure only authorized personnel access sensitive patient data.

### 3. **Corporate Intranets**
Protect confidential business information with advanced biometrics.

### 4. **E-commerce**
Prevent account takeovers and fraudulent transactions.

### 5. **Government Portals**
Secure citizen data with multi-factor authentication.

---

## 💻 Framework Examples

### Vanilla JavaScript

```html
<script src="emotion-mfa-plugin.js"></script>
<script>
    const mfa = new EmotionMFA({ apiUrl: 'http://localhost:8000' });
    
    document.getElementById('loginBtn').onclick = async () => {
        const result = await mfa.verify('username');
        if (result.success) {
            window.location.href = '/dashboard';
        }
    };
</script>
```

### React

```jsx
import EmotionMFA from 'emotion-auth-mfa';

const mfa = new EmotionMFA({ apiUrl: process.env.REACT_APP_MFA_API });

function LoginForm() {
    const handleLogin = async () => {
        const result = await mfa.verify(username);
        if (result.success) {
            navigate('/dashboard');
        }
    };
    
    return <button onClick={handleLogin}>Login with MFA</button>;
}
```

### Vue.js

```vue
<script>
import EmotionMFA from 'emotion-auth-mfa';

export default {
    data() {
        return {
            mfa: new EmotionMFA({ apiUrl: process.env.VUE_APP_MFA_API })
        };
    },
    methods: {
        async handleLogin() {
            const result = await this.mfa.verify(this.username);
            if (result.success) {
                this.$router.push('/dashboard');
            }
        }
    }
};
</script>
```

### Angular

```typescript
import EmotionMFA from 'emotion-auth-mfa';

export class LoginComponent {
    mfa = new EmotionMFA({ apiUrl: environment.mfaApiUrl });
    
    async handleLogin() {
        const result = await this.mfa.verify(this.username);
        if (result.success) {
            this.router.navigate(['/dashboard']);
        }
    }
}
```

---

## 🔧 Backend Integration

### Flask

```python
from mfa_backend_adapter import FlaskMFAMiddleware

app = Flask(__name__)
mfa = FlaskMFAMiddleware(app, emotion_api_url='http://localhost:8000')

@app.route('/dashboard')
@mfa.require_mfa
def dashboard():
    return 'Welcome to dashboard'
```

### Django

```python
# settings.py
MIDDLEWARE = [
    'mfa_backend_adapter.DjangoMFAMiddleware',
]

# views.py
from mfa_backend_adapter import DjangoMFAMiddleware

mfa = DjangoMFAMiddleware(lambda x: x)

@mfa.require_mfa
def dashboard(request):
    return JsonResponse({'message': 'Welcome'})
```

### FastAPI

```python
from mfa_backend_adapter import FastAPIMFAMiddleware

app = FastAPI()
mfa = FastAPIMFAMiddleware(emotion_api_url='http://localhost:8000')

@app.get('/dashboard')
@mfa.require_mfa
async def dashboard():
    return {'message': 'Welcome'}
```

### Express.js

```javascript
const express = require('express');
const axios = require('axios');

app.post('/api/verify-mfa', async (req, res) => {
    const response = await axios.post('http://localhost:8000/api/auth/attempt', {
        user_id: req.body.user_id,
        frame_data_url: req.body.frame_data,
        voice_features: req.body.voice_features,
        keystroke_events: req.body.keystroke_events
    });
    
    res.json(response.data);
});
```

---

## 🎨 Customization

### Custom Theme

```javascript
const mfa = new EmotionMFA({
    apiUrl: 'http://localhost:8000',
    theme: 'dark',  // 'light' or 'dark'
    onProgress: (message, percent) => {
        console.log(`${message}: ${percent}%`);
    }
});
```

### Selective Biometrics

```javascript
// Only facial recognition
await mfa.verify(userId, {
    requireFace: true,
    requireVoice: false,
    requireKeystroke: false
});

// Only voice and keystroke
await mfa.verify(userId, {
    requireFace: false,
    requireVoice: true,
    requireKeystroke: true
});
```

### Silent Mode

```javascript
// Minimal UI, automatic capture
const result = await mfa.quickVerify(userId);
```

---

## 📊 API Response

```javascript
{
    success: true,              // Boolean
    decision: 'permit',         // 'permit', 'delay', 'deny'
    confidence: 0.85,           // 0.0 to 1.0
    message: 'Access granted',  // User-friendly message
    details: {
        emotional_state: 'calm',
        stress_level: 0.2,
        coercion_risk: 0.1
    }
}
```

---

## 🔒 Security Features

- ✅ **Coercion Detection** - Identifies forced authentication
- ✅ **Stress Analysis** - Detects abnormal stress levels
- ✅ **Liveness Detection** - Prevents photo/video spoofing
- ✅ **Environment Analysis** - Checks lighting and noise
- ✅ **Rate Limiting** - Prevents brute force attacks
- ✅ **Audit Logging** - Complete authentication history
- ✅ **Real-time Alerts** - Instant security notifications

---

## 📱 Browser Support

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 11+
- ✅ Edge 79+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

**Requirements:**
- WebRTC support
- Camera and microphone access
- JavaScript enabled

---

## 🚀 Deployment

### Option 1: Docker

```bash
docker-compose up -d
```

### Option 2: Manual

```bash
# Start the backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Serve frontend
python -m http.server 8080
```

### Option 3: Cloud

Deploy to AWS, Azure, Google Cloud, or any hosting provider.

See `deploy.py` for automated deployment scripts.

---

## 📖 Documentation

- **Integration Guide:** [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)
- **API Documentation:** [REST_API_DOCS.md](REST_API_DOCS.md)
- **Example:** [example-integration.html](example-integration.html)

---

## 🧪 Testing

### Test the Plugin

Open `example-integration.html` in your browser:

```bash
python -m http.server 8080
# Visit http://localhost:8080/example-integration.html
```

### Test the API

```bash
# Start backend
python -m uvicorn backend.main:app --reload

# Visit http://localhost:8000/docs for API testing
```

### Simulate Authentication

```javascript
const result = await mfa.simulate_auth({
    stress_level: 0.3,
    match_score: 0.8,
    brightness: 0.7,
    noise: 0.2
});
```

---

## 🛠️ Troubleshooting

### Camera/Microphone Not Working

1. Check browser permissions
2. Ensure HTTPS (required for camera/mic access)
3. Test with `example-integration.html`

### API Connection Failed

1. Verify API URL is correct
2. Check CORS settings
3. Ensure backend is running
4. Test with: `curl http://localhost:8000/docs`

### MFA Always Fails

1. Check API key is valid
2. Verify user is enrolled (for keystroke dynamics)
3. Review logs: `GET /api/admin/logs`
4. Test in simulation mode first

---

## 📞 Support

- **GitHub Issues:** https://github.com/your-org/emotion-auth-mfa/issues
- **Email:** support@emotion-auth.com
- **Documentation:** https://docs.emotion-auth.com
- **Discord:** https://discord.gg/emotion-auth

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🌟 Star Us!

If you find this useful, please star the repository on GitHub!

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 🎯 Roadmap

- [ ] Mobile SDK (iOS/Android)
- [ ] Fingerprint integration
- [ ] Iris recognition
- [ ] Behavioral analytics
- [ ] Machine learning improvements
- [ ] Multi-language support
- [ ] Offline mode

---

**Made with ❤️ by the Emotion Auth Team**

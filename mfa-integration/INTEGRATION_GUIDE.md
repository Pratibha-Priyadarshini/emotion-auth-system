# Emotion-Aware MFA Integration Guide

This guide shows how to integrate emotion-aware multi-factor authentication into any website or web application.

## 🚀 Quick Start

### 1. Include the Plugin

```html
<script src="emotion-mfa-plugin.js"></script>
```

### 2. Initialize

```javascript
const mfa = new EmotionMFA({
    apiUrl: 'https://your-emotion-auth-server.com',
    apiKey: 'your-api-key',
    theme: 'light' // or 'dark'
});
```

### 3. Use After Primary Authentication

```javascript
// After username/password verification
const result = await mfa.verify(userId);

if (result.success) {
    // Grant access
    loginUser(userId);
} else {
    // Show error
    alert(result.message);
}
```

---

## 📦 Installation Options

### Option 1: Direct Script Include

```html
<script src="https://cdn.yourserver.com/emotion-mfa-plugin.js"></script>
```

### Option 2: NPM Package

```bash
npm install emotion-auth-mfa
```

```javascript
import EmotionMFA from 'emotion-auth-mfa';
```

### Option 3: Download and Host

Download `emotion-mfa-plugin.js` and host it on your server.

---

## 🔧 Configuration Options

```javascript
const mfa = new EmotionMFA({
    // Required
    apiUrl: 'https://your-server.com',
    
    // Optional
    apiKey: 'your-api-key',           // API authentication key
    timeout: 30000,                    // Request timeout (ms)
    theme: 'light',                    // 'light' or 'dark'
    language: 'en',                    // Language code
    
    // Callbacks
    onProgress: (message, percent) => {
        console.log(`${message}: ${percent}%`);
    }
});
```

---

## 💻 Integration Examples

### Vanilla JavaScript

```html
<!DOCTYPE html>
<html>
<head>
    <script src="emotion-mfa-plugin.js"></script>
</head>
<body>
    <form id="loginForm">
        <input type="text" id="username" placeholder="Username">
        <input type="password" id="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
    
    <script>
        const mfa = new EmotionMFA({
            apiUrl: 'http://localhost:8000'
        });
        
        document.getElementById('loginForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            
            // Step 1: Verify username/password with your backend
            const primaryAuth = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            if (!primaryAuth.ok) {
                alert('Invalid credentials');
                return;
            }
            
            // Step 2: Emotion MFA
            try {
                const mfaResult = await mfa.verify(username);
                
                if (mfaResult.success) {
                    window.location.href = '/dashboard';
                } else {
                    alert('MFA verification failed: ' + mfaResult.message);
                }
            } catch (error) {
                alert('MFA error: ' + error.message);
            }
        });
    </script>
</body>
</html>
```

### React

```jsx
import React, { useState } from 'react';
import EmotionMFA from 'emotion-auth-mfa';

const mfa = new EmotionMFA({
    apiUrl: process.env.REACT_APP_MFA_API_URL
});

function LoginForm() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    
    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            // Primary authentication
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            if (!response.ok) throw new Error('Invalid credentials');
            
            // MFA verification
            const mfaResult = await mfa.verify(username);
            
            if (mfaResult.success) {
                // Store token and redirect
                localStorage.setItem('token', await response.text());
                window.location.href = '/dashboard';
            } else {
                alert('MFA failed: ' + mfaResult.message);
            }
        } catch (error) {
            alert('Login error: ' + error.message);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <form onSubmit={handleLogin}>
            <input 
                type="text" 
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Username"
            />
            <input 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Password"
            />
            <button type="submit" disabled={loading}>
                {loading ? 'Authenticating...' : 'Login with MFA'}
            </button>
        </form>
    );
}

export default LoginForm;
```

### Vue.js

```vue
<template>
    <form @submit.prevent="handleLogin">
        <input v-model="username" type="text" placeholder="Username">
        <input v-model="password" type="password" placeholder="Password">
        <button type="submit" :disabled="loading">
            {{ loading ? 'Authenticating...' : 'Login with MFA' }}
        </button>
    </form>
</template>

<script>
import EmotionMFA from 'emotion-auth-mfa';

export default {
    data() {
        return {
            username: '',
            password: '',
            loading: false,
            mfa: null
        };
    },
    
    mounted() {
        this.mfa = new EmotionMFA({
            apiUrl: process.env.VUE_APP_MFA_API_URL
        });
    },
    
    methods: {
        async handleLogin() {
            this.loading = true;
            
            try {
                // Primary authentication
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        username: this.username,
                        password: this.password
                    })
                });
                
                if (!response.ok) throw new Error('Invalid credentials');
                
                // MFA verification
                const mfaResult = await this.mfa.verify(this.username);
                
                if (mfaResult.success) {
                    this.$router.push('/dashboard');
                } else {
                    alert('MFA failed: ' + mfaResult.message);
                }
            } catch (error) {
                alert('Login error: ' + error.message);
            } finally {
                this.loading = false;
            }
        }
    }
};
</script>
```

### Angular

```typescript
import { Component } from '@angular/core';
import { Router } from '@angular/router';
import EmotionMFA from 'emotion-auth-mfa';

@Component({
    selector: 'app-login',
    template: `
        <form (ngSubmit)="handleLogin()">
            <input [(ngModel)]="username" type="text" placeholder="Username">
            <input [(ngModel)]="password" type="password" placeholder="Password">
            <button type="submit" [disabled]="loading">
                {{ loading ? 'Authenticating...' : 'Login with MFA' }}
            </button>
        </form>
    `
})
export class LoginComponent {
    username = '';
    password = '';
    loading = false;
    mfa: any;
    
    constructor(private router: Router) {
        this.mfa = new EmotionMFA({
            apiUrl: 'http://localhost:8000'
        });
    }
    
    async handleLogin() {
        this.loading = true;
        
        try {
            // Primary authentication
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: this.username,
                    password: this.password
                })
            });
            
            if (!response.ok) throw new Error('Invalid credentials');
            
            // MFA verification
            const mfaResult = await this.mfa.verify(this.username);
            
            if (mfaResult.success) {
                this.router.navigate(['/dashboard']);
            } else {
                alert('MFA failed: ' + mfaResult.message);
            }
        } catch (error) {
            alert('Login error: ' + error.message);
        } finally {
            this.loading = false;
        }
    }
}
```

---

## 🔌 Backend Integration

### Flask

```python
from flask import Flask, request, session, jsonify
from mfa_backend_adapter import FlaskMFAMiddleware

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Initialize MFA middleware
mfa = FlaskMFAMiddleware(
    app,
    emotion_api_url='http://localhost:8000',
    api_key='your-api-key'
)

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    # Verify username/password
    if verify_credentials(username, password):
        session['user_id'] = username
        session['authenticated'] = True
        return jsonify({'success': True})
    
    return jsonify({'success': False}), 401

@app.route('/api/dashboard')
@mfa.require_mfa
def dashboard():
    return jsonify({'message': 'Welcome to dashboard'})
```

### Django

```python
# settings.py
MIDDLEWARE = [
    # ... other middleware
    'mfa_backend_adapter.DjangoMFAMiddleware',
]

# views.py
from django.http import JsonResponse
from mfa_backend_adapter import DjangoMFAMiddleware

mfa = DjangoMFAMiddleware(lambda x: x)

@mfa.require_mfa
def dashboard(request):
    return JsonResponse({'message': 'Welcome to dashboard'})
```

### FastAPI

```python
from fastapi import FastAPI, Depends
from mfa_backend_adapter import FastAPIMFAMiddleware

app = FastAPI()

mfa = FastAPIMFAMiddleware(emotion_api_url='http://localhost:8000')

@app.post('/api/login')
async def login(username: str, password: str):
    # Verify credentials
    if verify_credentials(username, password):
        return {'success': True}
    return {'success': False}

@app.get('/api/dashboard')
@mfa.require_mfa
async def dashboard():
    return {'message': 'Welcome to dashboard'}
```

### Express.js (Node.js)

```javascript
const express = require('express');
const axios = require('axios');

const app = express();
app.use(express.json());

const MFA_API_URL = 'http://localhost:8000';

// MFA verification middleware
async function verifyMFA(req, res, next) {
    if (req.session.mfa_verified) {
        return next();
    }
    
    const mfaData = req.body.mfa_data;
    if (!mfaData) {
        return res.status(403).json({ error: 'MFA required' });
    }
    
    try {
        const response = await axios.post(`${MFA_API_URL}/api/auth/attempt`, {
            user_id: req.session.user_id,
            frame_data_url: mfaData.frame_data,
            voice_features: mfaData.voice_features,
            keystroke_events: mfaData.keystroke_events
        });
        
        if (response.data.ok && response.data.fusion.decision === 'permit') {
            req.session.mfa_verified = true;
            next();
        } else {
            res.status(403).json({ error: 'MFA verification failed' });
        }
    } catch (error) {
        res.status(500).json({ error: 'MFA error' });
    }
}

app.post('/api/login', (req, res) => {
    // Verify credentials
    req.session.user_id = req.body.username;
    res.json({ success: true });
});

app.get('/api/dashboard', verifyMFA, (req, res) => {
    res.json({ message: 'Welcome to dashboard' });
});

app.listen(3000);
```

---

## 🎨 Customization

### Custom UI Theme

```javascript
const mfa = new EmotionMFA({
    apiUrl: 'http://localhost:8000',
    theme: 'dark',
    onProgress: (message, percent) => {
        // Custom progress indicator
        document.getElementById('mfa-progress').style.width = percent + '%';
        document.getElementById('mfa-message').textContent = message;
    }
});
```

### Selective Biometric Factors

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
    requireKeystroke: true,
    passphrase: 'my secure passphrase'
});
```

### Quick Verify (Silent Mode)

```javascript
// Minimal UI, automatic capture
const result = await mfa.quickVerify(userId);
```

---

## 🔒 Security Best Practices

1. **Always use HTTPS** in production
2. **Store API keys securely** (environment variables, not in code)
3. **Implement rate limiting** on your backend
4. **Set session timeouts** for MFA verification
5. **Log all authentication attempts** for audit trails
6. **Use CORS properly** to restrict API access
7. **Validate all inputs** on both frontend and backend

---

## 🐛 Troubleshooting

### Camera/Microphone Access Denied

```javascript
try {
    const result = await mfa.verify(userId);
} catch (error) {
    if (error.message.includes('Camera access denied')) {
        alert('Please allow camera access for MFA verification');
    }
}
```

### API Connection Issues

```javascript
// Check if API is available
if (await mfa.adapter.health_check()) {
    // Proceed with verification
} else {
    alert('MFA service is currently unavailable');
}
```

### Browser Compatibility

The plugin requires:
- Modern browser with WebRTC support
- Camera and microphone access
- JavaScript enabled

Supported browsers:
- Chrome 60+
- Firefox 55+
- Safari 11+
- Edge 79+

---

## 📊 API Response Format

```javascript
{
    success: true,              // Boolean
    decision: 'permit',         // 'permit', 'delay', 'deny'
    confidence: 0.85,           // 0.0 to 1.0
    message: 'Access granted',  // User-friendly message
    details: {
        emotional_state: 'calm',
        stress_level: 0.2,
        // ... more details
    }
}
```

---

## 📞 Support

For issues or questions:
- GitHub: https://github.com/your-org/emotion-auth-mfa
- Email: support@emotion-auth.com
- Documentation: https://docs.emotion-auth.com

---

## 📄 License

MIT License - See LICENSE file for details

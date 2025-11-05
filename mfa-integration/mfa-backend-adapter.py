"""
MFA Backend Adapter

This module provides middleware and adapters to integrate emotion-aware MFA
with existing authentication systems (Django, Flask, FastAPI, etc.)

Usage Examples:

# Flask
from mfa_backend_adapter import FlaskMFAMiddleware
app = Flask(__name__)
mfa = FlaskMFAMiddleware(app, emotion_api_url='http://localhost:8000')

@app.route('/login', methods=['POST'])
@mfa.require_mfa
def login():
    return {'success': True}

# Django
from mfa_backend_adapter import DjangoMFAMiddleware
# Add to MIDDLEWARE in settings.py

# FastAPI
from mfa_backend_adapter import FastAPIMFAMiddleware
app = FastAPI()
mfa = FastAPIMFAMiddleware(emotion_api_url='http://localhost:8000')
app.add_middleware(mfa)
"""

import requests
import json
from functools import wraps
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta


class EmotionMFAAdapter:
    """Base adapter for emotion-aware MFA integration."""
    
    def __init__(self, 
                 emotion_api_url: str = 'http://localhost:8000',
                 api_key: str = '',
                 timeout: int = 30,
                 cache_duration: int = 300):
        """
        Initialize the MFA adapter.
        
        Args:
            emotion_api_url: URL of the emotion auth API
            api_key: API key for authentication
            timeout: Request timeout in seconds
            cache_duration: How long to cache successful MFA (seconds)
        """
        self.emotion_api_url = emotion_api_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.cache_duration = cache_duration
        self.mfa_cache = {}  # user_id -> (timestamp, result)
    
    def verify_mfa(self, 
                   user_id: str, 
                   frame_data: str, 
                   voice_features: Dict[str, float], 
                   keystroke_events: list) -> Dict[str, Any]:
        """
        Verify MFA using emotion authentication.
        
        Args:
            user_id: User identifier
            frame_data: Base64 encoded image
            voice_features: Voice feature dict
            keystroke_events: Keystroke timing events
            
        Returns:
            Dict with verification result
        """
        # Check cache
        if user_id in self.mfa_cache:
            cached_time, cached_result = self.mfa_cache[user_id]
            if datetime.now() - cached_time < timedelta(seconds=self.cache_duration):
                return cached_result
        
        # Call emotion auth API
        payload = {
            'user_id': user_id,
            'frame_data_url': frame_data,
            'voice_features': voice_features,
            'keystroke_events': keystroke_events
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}'
        }
        
        try:
            response = requests.post(
                f'{self.emotion_api_url}/api/auth/attempt',
                json=payload,
                headers=headers,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            result = {
                'success': data.get('ok', False) and data.get('fusion', {}).get('decision') == 'permit',
                'decision': data.get('fusion', {}).get('decision', 'deny'),
                'confidence': data.get('fusion', {}).get('confidence', 0.0),
                'message': data.get('fusion', {}).get('guidance', 'Verification failed'),
                'emotional_state': data.get('fusion', {}).get('emotional_state', 'unknown'),
                'stress_level': data.get('fusion', {}).get('stress', 0.0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Cache successful results
            if result['success']:
                self.mfa_cache[user_id] = (datetime.now(), result)
            
            return result
            
        except requests.RequestException as e:
            return {
                'success': False,
                'decision': 'error',
                'message': f'MFA verification error: {str(e)}',
                'error': str(e)
            }
    
    def clear_cache(self, user_id: Optional[str] = None):
        """Clear MFA cache for a user or all users."""
        if user_id:
            self.mfa_cache.pop(user_id, None)
        else:
            self.mfa_cache.clear()


# Flask Integration
class FlaskMFAMiddleware:
    """Flask middleware for emotion-aware MFA."""
    
    def __init__(self, app=None, **kwargs):
        self.adapter = EmotionMFAAdapter(**kwargs)
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize Flask app."""
        app.config.setdefault('EMOTION_MFA_ENABLED', True)
        app.config.setdefault('EMOTION_MFA_API_URL', 'http://localhost:8000')
        
        @app.before_request
        def check_mfa():
            from flask import request, session
            
            # Skip MFA for certain routes
            if request.endpoint in ['login', 'static', 'mfa_verify']:
                return None
            
            # Check if user needs MFA
            if session.get('authenticated') and not session.get('mfa_verified'):
                return {'error': 'MFA required', 'mfa_required': True}, 403
    
    def require_mfa(self, f: Callable) -> Callable:
        """Decorator to require MFA for a route."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            from flask import request, session, jsonify
            
            # Check if already MFA verified
            if session.get('mfa_verified'):
                return f(*args, **kwargs)
            
            # Get MFA data from request
            mfa_data = request.json.get('mfa_data', {})
            
            if not mfa_data:
                return jsonify({'error': 'MFA data required', 'mfa_required': True}), 403
            
            # Verify MFA
            result = self.adapter.verify_mfa(
                user_id=session.get('user_id'),
                frame_data=mfa_data.get('frame_data', ''),
                voice_features=mfa_data.get('voice_features', {}),
                keystroke_events=mfa_data.get('keystroke_events', [])
            )
            
            if result['success']:
                session['mfa_verified'] = True
                session['mfa_timestamp'] = datetime.now().isoformat()
                return f(*args, **kwargs)
            else:
                return jsonify({
                    'error': 'MFA verification failed',
                    'message': result['message']
                }), 403
        
        return decorated_function


# Django Integration
class DjangoMFAMiddleware:
    """Django middleware for emotion-aware MFA."""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.adapter = EmotionMFAAdapter()
    
    def __call__(self, request):
        # Skip MFA for certain paths
        exempt_paths = ['/login/', '/static/', '/mfa/verify/']
        if any(request.path.startswith(path) for path in exempt_paths):
            return self.get_response(request)
        
        # Check if user is authenticated but not MFA verified
        if request.user.is_authenticated and not request.session.get('mfa_verified'):
            from django.http import JsonResponse
            return JsonResponse({
                'error': 'MFA required',
                'mfa_required': True
            }, status=403)
        
        return self.get_response(request)
    
    def require_mfa(self, view_func):
        """Decorator for Django views."""
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if request.session.get('mfa_verified'):
                return view_func(request, *args, **kwargs)
            
            # Get MFA data
            import json
            try:
                mfa_data = json.loads(request.body).get('mfa_data', {})
            except:
                mfa_data = {}
            
            if not mfa_data:
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'MFA data required',
                    'mfa_required': True
                }, status=403)
            
            # Verify MFA
            result = self.adapter.verify_mfa(
                user_id=str(request.user.id),
                frame_data=mfa_data.get('frame_data', ''),
                voice_features=mfa_data.get('voice_features', {}),
                keystroke_events=mfa_data.get('keystroke_events', [])
            )
            
            if result['success']:
                request.session['mfa_verified'] = True
                request.session['mfa_timestamp'] = datetime.now().isoformat()
                return view_func(request, *args, **kwargs)
            else:
                from django.http import JsonResponse
                return JsonResponse({
                    'error': 'MFA verification failed',
                    'message': result['message']
                }, status=403)
        
        return wrapped_view


# FastAPI Integration
class FastAPIMFAMiddleware:
    """FastAPI middleware for emotion-aware MFA."""
    
    def __init__(self, emotion_api_url: str = 'http://localhost:8000', **kwargs):
        self.adapter = EmotionMFAAdapter(emotion_api_url=emotion_api_url, **kwargs)
    
    async def __call__(self, request, call_next):
        from fastapi import Request
        from fastapi.responses import JSONResponse
        
        # Skip MFA for certain paths
        exempt_paths = ['/login', '/docs', '/openapi.json', '/mfa/verify']
        if any(request.url.path.startswith(path) for path in exempt_paths):
            return await call_next(request)
        
        # Check if user needs MFA
        # This assumes you have a session/token system
        # Adapt based on your authentication system
        
        return await call_next(request)
    
    def require_mfa(self, f: Callable) -> Callable:
        """Decorator for FastAPI routes."""
        @wraps(f)
        async def decorated_function(*args, **kwargs):
            from fastapi import Request, HTTPException
            
            # Get request from kwargs
            request = kwargs.get('request')
            if not request:
                raise HTTPException(status_code=500, detail="Request object not found")
            
            # Check session/token for MFA verification
            # This is a simplified example
            mfa_verified = request.session.get('mfa_verified', False)
            
            if mfa_verified:
                return await f(*args, **kwargs)
            
            # Get MFA data from request body
            try:
                body = await request.json()
                mfa_data = body.get('mfa_data', {})
            except:
                mfa_data = {}
            
            if not mfa_data:
                raise HTTPException(
                    status_code=403,
                    detail={'error': 'MFA data required', 'mfa_required': True}
                )
            
            # Verify MFA
            user_id = request.session.get('user_id', 'unknown')
            result = self.adapter.verify_mfa(
                user_id=user_id,
                frame_data=mfa_data.get('frame_data', ''),
                voice_features=mfa_data.get('voice_features', {}),
                keystroke_events=mfa_data.get('keystroke_events', [])
            )
            
            if result['success']:
                request.session['mfa_verified'] = True
                request.session['mfa_timestamp'] = datetime.now().isoformat()
                return await f(*args, **kwargs)
            else:
                raise HTTPException(
                    status_code=403,
                    detail={
                        'error': 'MFA verification failed',
                        'message': result['message']
                    }
                )
        
        return decorated_function


# Generic decorator for any framework
def require_emotion_mfa(adapter: EmotionMFAAdapter):
    """Generic decorator that works with any framework."""
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Extract MFA data from args/kwargs
            # This needs to be adapted based on your framework
            mfa_data = kwargs.get('mfa_data', {})
            user_id = kwargs.get('user_id', 'unknown')
            
            result = adapter.verify_mfa(
                user_id=user_id,
                frame_data=mfa_data.get('frame_data', ''),
                voice_features=mfa_data.get('voice_features', {}),
                keystroke_events=mfa_data.get('keystroke_events', [])
            )
            
            if result['success']:
                return f(*args, **kwargs)
            else:
                raise Exception(f"MFA verification failed: {result['message']}")
        
        return wrapper
    return decorator


# Example usage
if __name__ == "__main__":
    # Standalone usage
    adapter = EmotionMFAAdapter(emotion_api_url='http://localhost:8000')
    
    result = adapter.verify_mfa(
        user_id='test_user',
        frame_data='data:image/jpeg;base64,...',
        voice_features={'rms': 0.3, 'zcr': 0.2, 'pitch_hz': 180},
        keystroke_events=[{'key': 'a', 't_down': 100, 't_up': 150}]
    )
    
    print(f"MFA Result: {result['decision']}")
    print(f"Message: {result['message']}")

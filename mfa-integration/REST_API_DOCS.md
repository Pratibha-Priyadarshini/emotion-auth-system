# Emotion-Aware MFA REST API Documentation

Complete API reference for integrating emotion-aware multi-factor authentication.

## Base URL

```
http://localhost:8000
https://your-emotion-auth-server.com
```

## Authentication

Include your API key in the Authorization header:

```
Authorization: Bearer YOUR_API_KEY
```

---

## Endpoints

### 1. Verify MFA

Perform emotion-aware MFA verification.

**Endpoint:** `POST /api/auth/attempt`

**Request Body:**

```json
{
    "user_id": "string",
    "frame_data_url": "data:image/jpeg;base64,...",
    "voice_features": {
        "rms": 0.3,
        "zcr": 0.2,
        "pitch_hz": 180.0
    },
    "keystroke_events": [
        {
            "key": "a",
            "t_down": 100,
            "t_up": 150
        }
    ]
}
```

**Response:**

```json
{
    "ok": true,
    "fusion": {
        "decision": "permit",
        "confidence": 0.85,
        "guidance": "Access granted. Welcome!",
        "emotional_state": "calm",
        "stress": 0.2,
        "coercion_risk": 0.1
    },
    "facial": {
        "dominant_emotion": "neutral",
        "probs": {
            "neutral": 0.7,
            "happy": 0.2,
            "sad": 0.1
        }
    },
    "voice": {
        "probs": {
            "neutral": 0.6,
            "calm": 0.3,
            "stressed": 0.1
        }
    },
    "keystroke": {
        "match": 0.8,
        "confidence": 0.75
    },
    "env": {
        "quality_score": 0.9,
        "brightness": 0.7,
        "noise": 0.2
    }
}
```

**Status Codes:**
- `200 OK` - Verification completed
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Invalid API key
- `500 Internal Server Error` - Server error

---

### 2. Enroll User (Keystroke Dynamics)

Enroll a user's keystroke pattern.

**Endpoint:** `POST /api/enroll/keystrokes`

**Request Body:**

```json
{
    "user_id": "string",
    "passphrase": "string",
    "samples": [
        [
            {"key": "a", "t_down": 100, "t_up": 150},
            {"key": "b", "t_down": 200, "t_up": 250}
        ],
        [
            {"key": "a", "t_down": 105, "t_up": 155},
            {"key": "b", "t_down": 205, "t_up": 255}
        ]
    ]
}
```

**Response:**

```json
{
    "ok": true,
    "message": "User enrolled successfully",
    "user_id": "string",
    "samples_count": 2
}
```

---

### 3. Get Authentication Logs

Retrieve authentication attempt logs.

**Endpoint:** `GET /api/admin/logs`

**Query Parameters:**
- `user_id` (optional): Filter by user ID
- `limit` (optional): Number of logs to return (default: 50)
- `offset` (optional): Pagination offset (default: 0)

**Response:**

```json
{
    "ok": true,
    "logs": [
        {
            "timestamp": "2025-11-03T10:30:00Z",
            "user_id": "john_doe",
            "decision": "permit",
            "confidence": 0.85,
            "emotional_state": "calm",
            "stress_level": 0.2,
            "ip_address": "192.168.1.100"
        }
    ],
    "total": 150,
    "limit": 50,
    "offset": 0
}
```

---

### 4. Get Security Alerts

Retrieve security alerts.

**Endpoint:** `GET /api/admin/alerts`

**Query Parameters:**
- `level` (optional): Filter by level (critical, high, medium, low)
- `limit` (optional): Number of alerts (default: 50)

**Response:**

```json
{
    "ok": true,
    "alerts": [
        {
            "timestamp": "2025-11-03T10:25:00Z",
            "level": "high",
            "type": "coercion_detected",
            "user_id": "john_doe",
            "message": "High stress and fear detected",
            "details": {
                "stress_level": 0.9,
                "coercion_risk": 0.85
            }
        }
    ],
    "total": 25
}
```

---

### 5. Get Statistics

Get system statistics.

**Endpoint:** `GET /api/admin/statistics`

**Response:**

```json
{
    "ok": true,
    "authentication": {
        "total_attempts": 1500,
        "successful": 1200,
        "failed": 300,
        "success_rate": 0.8
    },
    "alerts": {
        "total": 50,
        "critical": 5,
        "high": 15,
        "medium": 20,
        "low": 10
    },
    "users": {
        "total_enrolled": 250,
        "active_today": 120
    }
}
```

---

### 6. Simulate Authentication (Testing)

Simulate authentication for testing purposes.

**Endpoint:** `POST /api/test/simulate`

**Query Parameters:**
- `stress_level` (float): 0.0 to 1.0
- `match_score` (float): 0.0 to 1.0
- `brightness` (float): 0.0 to 1.0
- `noise` (float): 0.0 to 1.0

**Example:**

```
POST /api/test/simulate?stress_level=0.3&match_score=0.8&brightness=0.7&noise=0.2
```

**Response:**

```json
{
    "ok": true,
    "simulation": {
        "decision": "permit",
        "confidence": 0.82,
        "guidance": "Access granted",
        "emotional_state": "calm",
        "inputs": {
            "stress_level": 0.3,
            "match_score": 0.8,
            "brightness": 0.7,
            "noise": 0.2
        }
    }
}
```

---

### 7. Health Check

Check API health status.

**Endpoint:** `GET /docs`

**Response:**

Returns the API documentation page (200 OK if healthy).

---

## Decision Types

The API returns one of three decisions:

### 1. Permit
- **Meaning:** User is authenticated successfully
- **Action:** Grant access
- **Confidence:** Typically > 0.7

### 2. Delay
- **Meaning:** Suspicious activity detected, require additional verification
- **Action:** Show additional challenge or delay access
- **Confidence:** Typically 0.4 - 0.7

### 3. Deny
- **Meaning:** Authentication failed or high risk detected
- **Action:** Deny access and log incident
- **Confidence:** Typically < 0.4

---

## Error Responses

All errors follow this format:

```json
{
    "ok": false,
    "detail": "Error message description",
    "error_code": "ERROR_CODE"
}
```

**Common Error Codes:**
- `INVALID_INPUT` - Invalid request data
- `UNAUTHORIZED` - Invalid or missing API key
- `USER_NOT_FOUND` - User not enrolled
- `PROCESSING_ERROR` - Error processing biometric data
- `RATE_LIMIT_EXCEEDED` - Too many requests

---

## Rate Limiting

- **Authentication attempts:** 5 per minute per user
- **API calls:** 100 per minute per API key
- **Enrollment:** 10 per hour per user

**Rate Limit Headers:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1699012800
```

---

## Webhooks (Optional)

Configure webhooks to receive real-time notifications.

**Webhook Events:**
- `auth.success` - Successful authentication
- `auth.failed` - Failed authentication
- `alert.created` - New security alert
- `user.enrolled` - New user enrolled

**Webhook Payload:**

```json
{
    "event": "alert.created",
    "timestamp": "2025-11-03T10:30:00Z",
    "data": {
        "alert_id": "alert_123",
        "level": "high",
        "type": "coercion_detected",
        "user_id": "john_doe"
    }
}
```

---

## SDK Examples

### JavaScript

```javascript
const response = await fetch('http://localhost:8000/api/auth/attempt', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'
    },
    body: JSON.stringify({
        user_id: 'john_doe',
        frame_data_url: frameData,
        voice_features: voiceFeatures,
        keystroke_events: keystrokeEvents
    })
});

const result = await response.json();
console.log(result.fusion.decision);
```

### Python

```python
import requests

response = requests.post(
    'http://localhost:8000/api/auth/attempt',
    headers={
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_KEY'
    },
    json={
        'user_id': 'john_doe',
        'frame_data_url': frame_data,
        'voice_features': voice_features,
        'keystroke_events': keystroke_events
    }
)

result = response.json()
print(result['fusion']['decision'])
```

### cURL

```bash
curl -X POST http://localhost:8000/api/auth/attempt \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "user_id": "john_doe",
    "frame_data_url": "data:image/jpeg;base64,...",
    "voice_features": {"rms": 0.3, "zcr": 0.2, "pitch_hz": 180},
    "keystroke_events": [{"key": "a", "t_down": 100, "t_up": 150}]
  }'
```

---

## Best Practices

1. **Always use HTTPS** in production
2. **Store API keys securely** (environment variables)
3. **Implement retry logic** with exponential backoff
4. **Cache successful MFA** for a short period (5 minutes)
5. **Log all authentication attempts** for audit trails
6. **Monitor rate limits** and implement client-side throttling
7. **Handle errors gracefully** with user-friendly messages
8. **Test in simulation mode** before production deployment

---

## Support

- **Documentation:** https://docs.emotion-auth.com
- **API Status:** https://status.emotion-auth.com
- **Support Email:** support@emotion-auth.com
- **GitHub:** https://github.com/your-org/emotion-auth-mfa

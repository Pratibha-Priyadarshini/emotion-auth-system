import os, json, base64
from typing import List, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .db import init_db, get_session, UserProfile, EventLog
from .models.facial_emotion_trained import analyze_frame
from .models.voice_emotion_trained import analyze_voice_feats
from .models.keystroke_dynamics import enroll_fit, score_events
from .env_context import analyze_env
from .fusion_engine import fuse

app = FastAPI(title="Emotion-Aware Contextual Auth")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))
if os.path.isdir(FRONTEND_DIR):
    app.mount("/web", StaticFiles(directory=FRONTEND_DIR, html=True), name="web")

@app.on_event("startup")
def startup():
    init_db()

# Real-time emotion analysis endpoint (no authentication)
class EmotionAnalysisPayload(BaseModel):
    frame_data_url: str
    voice_features: Dict[str, float]

@app.post("/api/analyze/emotion")
def analyze_emotion(payload: EmotionAnalysisPayload):
    """Analyze emotions in real-time without authentication."""
    try:
        facial = analyze_frame(payload.frame_data_url)
        voice = analyze_voice_feats(payload.voice_features)
        
        # Check for security violations
        if facial.get("security_violation"):
            return {
                "ok": False,
                "security_violation": True,
                "facial": facial,
                "voice": voice,
                "error": facial.get("violation_reason", "Security violation detected")
            }
        
        return {
            "ok": True,
            "facial": facial,
            "voice": voice
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }

class EnrollPayload(BaseModel):
    user_id: str
    passphrase: str
    samples: List[List[Dict[str, Any]]]  # list of keystroke event arrays

@app.post("/api/enroll/keystrokes")
def enroll_keystrokes(payload: EnrollPayload):
    sess = get_session()
    try:
        user = sess.query(UserProfile).filter_by(user_id=payload.user_id).first()
        if not user:
            user = UserProfile(user_id=payload.user_id, passphrase=payload.passphrase, kd_enroll_count=0)
            sess.add(user); sess.commit()
        model_dir = os.path.join(os.path.dirname(__file__), "storage", "kd_models")
        path = enroll_fit(model_dir, payload.user_id, payload.samples)
        user.kd_model_path = path
        user.kd_enroll_count = len(payload.samples)
        sess.add(user); sess.commit()
        return {"ok": True, "kd_model_path": path, "enrolled_samples": len(payload.samples)}
    finally:
        sess.close()

class AuthAttempt(BaseModel):
    user_id: str
    passphrase: str  # The actual passphrase text to validate
    frame_data_url: str
    voice_features: Dict[str, float]  # {rms, zcr, pitch_hz}
    keystroke_events: List[Dict[str, Any]]

@app.post("/api/auth/attempt")
def auth_attempt(payload: AuthAttempt):
    sess = get_session()
    try:
        user = sess.query(UserProfile).filter_by(user_id=payload.user_id).first()
        if not user or not user.kd_model_path:
            raise HTTPException(status_code=400, detail="User not enrolled for keystrokes")
        
        # CRITICAL: Validate passphrase first
        if payload.passphrase != user.passphrase:
            # Wrong passphrase - immediate denial BUT LOG IT
            
            # Analyze biometrics for logging purposes
            facial = analyze_frame(payload.frame_data_url)
            voice = analyze_voice_feats(payload.voice_features)
            
            # Create denial fusion result
            fusion = {
                "decision": "deny",
                "confidence": 0.95,
                "reason": "Incorrect passphrase",
                "guidance": "Access denied. The passphrase you entered is incorrect.",
                "stress": 0.0,
                "stress_facial": facial.get("stress", 0.0),
                "stress_voice": voice.get("stress", 0.0),
                "coercion_risk": 0.0,
                "alert_level": "high",
                "emotional_state": "unknown"
            }
            
            kd = {"match": 0.0, "anomaly": 1.0, "confidence": 0.0}
            env = {"suitable_for_auth": False}
            
            # Create HIGH alert for wrong passphrase
            from .alert_system import alert_system
            alert_system.create_alert(
                alert_type="incorrect_passphrase",
                level="high",
                user_id=payload.user_id,
                message=f"User {payload.user_id} attempted authentication with incorrect passphrase",
                details={"attempt_time": "now", "reason": "passphrase_mismatch"}
            )
            
            # Log the denial attempt
            log = EventLog(
                user_id=payload.user_id,
                decision="deny",
                confidence=0.95,
                reason="Incorrect passphrase",
                facial=facial, voice=voice, keystroke=kd, env=env, fusion=fusion
            )
            sess.add(log)
            sess.commit()
            
            return {
                "ok": True,
                "fusion": fusion,
                "facial": facial,
                "voice": voice,
                "keystroke": kd,
                "env": env,
                "alerts_created": 1
            }
        
        # Analyze all modalities
        facial = analyze_frame(payload.frame_data_url)
        
        # CRITICAL SECURITY CHECK: Multiple people detected
        if facial.get("security_violation"):
            from .alert_system import alert_system
            
            # Create CRITICAL alert for multiple people
            alert_system.create_alert(
                alert_type="multiple_people_detected",
                level="critical",
                user_id=payload.user_id,
                message=f"SECURITY BREACH: {facial.get('violation_reason')}",
                details={
                    "num_faces": facial.get("num_faces", 0),
                    "violation": facial.get("violation_reason"),
                    "timestamp": "now"
                }
            )
            
            # Create immediate denial fusion result
            fusion = {
                "decision": "deny",
                "confidence": 1.0,
                "reason": facial.get("violation_reason", "Security violation"),
                "guidance": "🚨 ACCESS DENIED: Multiple people detected in frame. Only one person allowed during authentication.",
                "stress": 1.0,
                "stress_facial": 1.0,
                "stress_voice": 0.0,
                "coercion_risk": 1.0,
                "alert_level": "critical",
                "emotional_state": "security_breach"
            }
            
            kd = {"match": 0.0, "anomaly": 1.0, "confidence": 0.0}
            voice = analyze_voice_feats(payload.voice_features)
            env = {"suitable_for_auth": False}
            
            # Log the security violation
            log = EventLog(
                user_id=payload.user_id,
                decision="deny",
                confidence=1.0,
                reason=facial.get("violation_reason"),
                facial=facial, voice=voice, keystroke=kd, env=env, fusion=fusion
            )
            sess.add(log)
            sess.commit()
            
            return {
                "ok": True,
                "fusion": fusion,
                "facial": facial,
                "voice": voice,
                "keystroke": kd,
                "env": env,
                "alerts_created": 1,
                "security_violation": True
            }
        
        voice = analyze_voice_feats(payload.voice_features)
        kd = score_events(user.kd_model_path, payload.keystroke_events)
        env = analyze_env(facial, voice)
        fusion = fuse(facial, voice, kd, env)
        
        # Create alerts if needed
        from .alert_system import alert_system
        alerts = alert_system.check_and_create_alerts(
            payload.user_id, fusion, facial, voice, kd, env
        )
        
        # Log the attempt
        log = EventLog(
            user_id=payload.user_id,
            decision=fusion["decision"],
            confidence=fusion["confidence"],
            reason=fusion["reason"],
            facial=facial, voice=voice, keystroke=kd, env=env, fusion=fusion
        )
        sess.add(log); sess.commit()
        
        return {
            "ok": True, 
            "fusion": fusion, 
            "facial": facial, 
            "voice": voice, 
            "keystroke": kd, 
            "env": env,
            "alerts_created": len(alerts),
            "ui_adaptation": fusion.get("ui_adaptation", {})
        }
    finally:
        sess.close()

@app.get("/api/admin/logs")
def admin_logs(limit: int = 50):
    sess = get_session()
    try:
        rows = sess.query(EventLog).order_by(EventLog.created_at.desc()).limit(limit).all()
        def to_dict(r):
            return {
                "id": r.id, "user_id": r.user_id, "decision": r.decision,
                "confidence": r.confidence, "reason": r.reason,
                "facial": r.facial, "voice": r.voice, "keystroke": r.keystroke,
                "env": r.env, "fusion": r.fusion, "created_at": r.created_at.isoformat()
            }
        return {"ok": True, "logs": [to_dict(r) for r in rows]}
    finally:
        sess.close()

@app.get("/api/admin/alerts")
def get_alerts(limit: int = 50, level: str = None):
    """Get recent alerts, optionally filtered by level."""
    from .alert_system import alert_system
    alerts = alert_system.get_recent_alerts(limit=limit, level=level)
    return {"ok": True, "alerts": alerts}

@app.get("/api/admin/alerts/critical")
def get_critical_alerts():
    """Get all unacknowledged critical alerts."""
    from .alert_system import alert_system
    alerts = alert_system.get_critical_alerts()
    return {"ok": True, "critical_alerts": alerts, "count": len(alerts)}

@app.post("/api/admin/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int):
    """Acknowledge an alert."""
    from .alert_system import alert_system
    success = alert_system.acknowledge_alert(alert_id)
    return {"ok": success, "message": "Alert acknowledged" if success else "Alert not found"}

@app.post("/api/admin/alerts/{alert_id}/resolve")
def resolve_alert(alert_id: int, resolution_note: str = ""):
    """Resolve an alert."""
    from .alert_system import alert_system
    success = alert_system.resolve_alert(alert_id, resolution_note)
    return {"ok": success, "message": "Alert resolved" if success else "Alert not found"}

@app.get("/api/admin/statistics")
def get_statistics():
    """Get system statistics including alerts and authentication attempts."""
    from .alert_system import alert_system
    sess = get_session()
    try:
        # Authentication statistics
        total_attempts = sess.query(EventLog).count()
        permits = sess.query(EventLog).filter_by(decision="permit").count()
        delays = sess.query(EventLog).filter_by(decision="delay").count()
        denies = sess.query(EventLog).filter_by(decision="deny").count()
        
        # Alert statistics
        alert_stats = alert_system.get_alert_statistics()
        
        # User statistics
        total_users = sess.query(UserProfile).count()
        enrolled_users = sess.query(UserProfile).filter(UserProfile.kd_model_path.isnot(None)).count()
        
        return {
            "ok": True,
            "authentication": {
                "total_attempts": total_attempts,
                "permits": permits,
                "delays": delays,
                "denies": denies,
                "success_rate": (permits / total_attempts * 100) if total_attempts > 0 else 0
            },
            "alerts": alert_stats,
            "users": {
                "total": total_users,
                "enrolled": enrolled_users
            }
        }
    finally:
        sess.close()

@app.post("/api/test/simulate")
def simulate_auth(stress_level: float = 0.5, match_score: float = 0.5, brightness: float = 0.5, noise: float = 0.3):
    """Test endpoint to simulate different authentication scenarios."""
    from .fusion_engine import fuse
    
    # Simulate facial data
    facial = {
        "stress": stress_level,
        "brightness": brightness,
        "contrast": 60.0,
        "probs": {"neutral": 0.7, "happy": 0.2, "sad": 0.1}
    }
    
    # Simulate voice data
    voice = {
        "stress": stress_level,
        "probs": {"calm": 0.7, "happy": 0.2, "sad": 0.1},
        "features": {"rms": noise, "zcr": 0.3, "pitch_hz": 180}
    }
    
    # Simulate keystroke data
    kd = {
        "match": match_score,
        "anomaly": 1.0 - match_score,
        "confidence": match_score,
        "is_genuine": match_score > 0.5
    }
    
    # Simulate environment
    from .env_context import analyze_env
    env = analyze_env(facial, voice)
    
    # Get fusion decision
    fusion = fuse(facial, voice, kd, env)
    
    return {
        "ok": True,
        "simulation": {
            "inputs": {
                "stress_level": stress_level,
                "match_score": match_score,
                "brightness": brightness,
                "noise": noise
            },
            "decision": fusion["decision"],
            "confidence": fusion["confidence"],
            "reason": fusion["reason"],
            "guidance": fusion["guidance"],
            "emotional_state": fusion["emotional_state"]
        }
    }

"""
Real-time alert system for suspicious activities and emotional volatility.
"""

from typing import Dict, Any, List
from datetime import datetime
import json
from pathlib import Path

ALERTS_DIR = Path(__file__).parent / "storage" / "alerts"
ALERTS_DIR.mkdir(parents=True, exist_ok=True)


class AlertSystem:
    """Manages security and wellness alerts."""
    
    ALERT_LEVELS = {
        "critical": 4,
        "high": 3,
        "medium": 2,
        "low": 1,
        "normal": 0
    }
    
    def __init__(self):
        self.alerts = []
        self.alert_file = ALERTS_DIR / "alerts.json"
        self.load_alerts()
    
    def load_alerts(self):
        """Load existing alerts from file."""
        if self.alert_file.exists():
            try:
                with open(self.alert_file, 'r') as f:
                    self.alerts = json.load(f)
            except:
                self.alerts = []
    
    def save_alerts(self):
        """Save alerts to file."""
        with open(self.alert_file, 'w') as f:
            json.dump(self.alerts[-1000:], f, indent=2)  # Keep last 1000 alerts
    
    def create_alert(self, 
                    alert_type: str,
                    level: str,
                    user_id: str,
                    message: str,
                    details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new alert.
        
        Args:
            alert_type: Type of alert (security, wellness, environmental, coercion)
            level: Alert level (critical, high, medium, low, normal)
            user_id: User ID associated with the alert
            message: Human-readable alert message
            details: Additional details about the alert
        """
        
        alert = {
            "id": len(self.alerts) + 1,
            "type": alert_type,
            "level": level,
            "priority": self.ALERT_LEVELS.get(level, 0),
            "user_id": user_id,
            "message": message,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "acknowledged": False,
            "resolved": False
        }
        
        self.alerts.append(alert)
        self.save_alerts()
        
        return alert
    
    def check_and_create_alerts(self, 
                                user_id: str,
                                fusion_result: Dict[str, Any],
                                facial: Dict[str, Any],
                                voice: Dict[str, Any],
                                keystroke: Dict[str, Any],
                                env: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze authentication attempt and create appropriate alerts.
        """
        
        created_alerts = []
        
        # Critical: Coercion risk
        if fusion_result.get("coercion_risk", 0) > 0.5:
            alert = self.create_alert(
                alert_type="coercion",
                level="critical",
                user_id=user_id,
                message=f"High coercion risk detected for user {user_id}",
                details={
                    "coercion_risk": fusion_result["coercion_risk"],
                    "environmental_flags": env.get("flags", {}),
                    "stress_level": fusion_result["stress"],
                    "decision": fusion_result["decision"]
                }
            )
            created_alerts.append(alert)
        
        # Critical: Shouting detected
        if env.get("flags", {}).get("shouting"):
            alert = self.create_alert(
                alert_type="environmental",
                level="critical",
                user_id=user_id,
                message=f"Shouting detected during authentication attempt by {user_id}",
                details={
                    "loudness": env.get("loudness", 0),
                    "pitch": env.get("pitch", 0),
                    "risk_level": env.get("risk_level", "unknown")
                }
            )
            created_alerts.append(alert)
        
        # High: Keystroke anomaly
        if keystroke.get("anomaly", 0) > 0.7:
            alert = self.create_alert(
                alert_type="security",
                level="high",
                user_id=user_id,
                message=f"Keystroke pattern anomaly detected for {user_id}",
                details={
                    "anomaly_score": keystroke["anomaly"],
                    "match_score": keystroke.get("match", 0),
                    "confidence": keystroke.get("confidence", 0)
                }
            )
            created_alerts.append(alert)
        
        # High: Multiple failed attempts (would need session tracking)
        if fusion_result["decision"] == "deny":
            alert = self.create_alert(
                alert_type="security",
                level="high",
                user_id=user_id,
                message=f"Authentication denied for {user_id}",
                details={
                    "reason": fusion_result["reason"],
                    "confidence": fusion_result["confidence"],
                    "alert_level": fusion_result.get("alert_level", "unknown")
                }
            )
            created_alerts.append(alert)
        
        # Medium: High stress levels
        if fusion_result.get("stress", 0) > 0.7:
            alert = self.create_alert(
                alert_type="wellness",
                level="medium",
                user_id=user_id,
                message=f"High stress level detected for {user_id}",
                details={
                    "stress_level": fusion_result["stress"],
                    "facial_stress": fusion_result.get("stress_facial", 0),
                    "voice_stress": fusion_result.get("stress_voice", 0),
                    "emotional_state": fusion_result.get("emotional_state", "unknown")
                }
            )
            created_alerts.append(alert)
        
        # Medium: Mental health alert
        if fusion_result.get("mental_health_alert", False):
            alert = self.create_alert(
                alert_type="wellness",
                level="medium",
                user_id=user_id,
                message=f"Mental health support may be needed for {user_id}",
                details={
                    "stress_level": fusion_result["stress"],
                    "emotional_state": fusion_result.get("emotional_state", "unknown"),
                    "guidance": fusion_result.get("guidance", "")
                }
            )
            created_alerts.append(alert)
        
        # Low: Poor environmental conditions
        if not env.get("suitable_for_auth", True):
            alert = self.create_alert(
                alert_type="environmental",
                level="low",
                user_id=user_id,
                message=f"Unsuitable environment detected for {user_id}",
                details={
                    "environmental_quality": env.get("quality_score", 0),
                    "stability": env.get("stability", 0),
                    "recommendations": env.get("recommendations", [])
                }
            )
            created_alerts.append(alert)
        
        return created_alerts
    
    def get_recent_alerts(self, limit: int = 50, level: str = None) -> List[Dict[str, Any]]:
        """Get recent alerts, optionally filtered by level."""
        
        alerts = self.alerts[-limit:]
        
        if level:
            alerts = [a for a in alerts if a["level"] == level]
        
        return sorted(alerts, key=lambda x: x["timestamp"], reverse=True)
    
    def get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Get all unacknowledged critical alerts."""
        
        return [a for a in self.alerts 
                if a["level"] == "critical" and not a["acknowledged"]]
    
    def acknowledge_alert(self, alert_id: int) -> bool:
        """Mark an alert as acknowledged."""
        
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["acknowledged"] = True
                alert["acknowledged_at"] = datetime.now().isoformat()
                self.save_alerts()
                return True
        
        return False
    
    def resolve_alert(self, alert_id: int, resolution_note: str = "") -> bool:
        """Mark an alert as resolved."""
        
        for alert in self.alerts:
            if alert["id"] == alert_id:
                alert["resolved"] = True
                alert["resolved_at"] = datetime.now().isoformat()
                alert["resolution_note"] = resolution_note
                self.save_alerts()
                return True
        
        return False
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get statistics about alerts."""
        
        total = len(self.alerts)
        by_level = {}
        by_type = {}
        unacknowledged = 0
        unresolved = 0
        
        for alert in self.alerts:
            # Count by level
            level = alert["level"]
            by_level[level] = by_level.get(level, 0) + 1
            
            # Count by type
            alert_type = alert["type"]
            by_type[alert_type] = by_type.get(alert_type, 0) + 1
            
            # Count unacknowledged and unresolved
            if not alert["acknowledged"]:
                unacknowledged += 1
            if not alert["resolved"]:
                unresolved += 1
        
        return {
            "total_alerts": total,
            "by_level": by_level,
            "by_type": by_type,
            "unacknowledged": unacknowledged,
            "unresolved": unresolved,
            "critical_unacknowledged": len(self.get_critical_alerts())
        }


# Global alert system instance
alert_system = AlertSystem()

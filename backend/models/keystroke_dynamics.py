import os, json, pickle, numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.svm import OneClassSVM

def _events_to_features(events: List[Dict[str, Any]]) -> np.ndarray:
    # Expect events sorted with fields: key, t_down, t_up (ms)
    downs = [e for e in events if e.get("t_down") is not None]
    ups = [e for e in events if e.get("t_up") is not None]
    holds = []
    for e in events:
        if e.get("t_down") is not None and e.get("t_up") is not None:
            holds.append(e["t_up"] - e["t_down"])
    # digraph flight times between successive downs
    downs_sorted = sorted(downs, key=lambda x: x["t_down"])
    flights = [downs_sorted[i+1]["t_down"] - downs_sorted[i]["t_down"] for i in range(len(downs_sorted)-1)]
    # robust stats
    import statistics as stats
    def robust(arr):
        if not arr:
            return [0,0,0,0]
        m = stats.mean(arr)
        s = stats.pstdev(arr) if len(arr) > 1 else 0.0
        p25 = np.percentile(arr, 25)
        p75 = np.percentile(arr, 75)
        return [m, s, p25, p75]
    feat = robust(holds) + robust(flights)
    # length and typing speed (chars per second)
    if downs_sorted:
        duration = (downs_sorted[-1]["t_down"] - downs_sorted[0]["t_down"]) / 1000.0
    else:
        duration = 0.0
    speed = (len(downs_sorted) / duration) if duration > 0 else 0.0
    feat += [len(downs_sorted), duration, speed]
    return np.array(feat, dtype=float)

def enroll_fit(model_dir: str, user_id: str, samples: List[List[Dict[str, Any]]]) -> str:
    X = np.vstack([_events_to_features(s) for s in samples])
    # Use more lenient nu parameter (0.3 = allow 30% outliers)
    # Lower gamma for smoother decision boundary
    clf = OneClassSVM(gamma=0.01, nu=0.3)
    clf.fit(X)
    os.makedirs(model_dir, exist_ok=True)
    path = os.path.join(model_dir, f"kd_{user_id}.pkl")
    with open(path, "wb") as f:
        pickle.dump(clf, f)
    return path

def score_events(model_path: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
    x = _events_to_features(events).reshape(1, -1)
    with open(model_path, "rb") as f:
        clf: OneClassSVM = pickle.load(f)
    pred = clf.predict(x)[0]  # 1 normal, -1 anomaly
    # decision_function > 0 => inlier
    df = float(clf.decision_function(x)[0])
    
    # Balanced scoring (not too strict, not too lenient)
    # Map decision function to match score (0-1)
    # Positive df = good match, negative = anomaly
    import math
    
    # Sigmoid with balanced scale
    conf = 1 / (1 + math.exp(-df * 3))  # Scale factor of 3 for moderate curve
    
    # Balanced match/anomaly determination
    # Consider it a match if decision function is > -0.3
    is_match = df > -0.3
    match_score = max(0.0, min(1.0, (df + 1.0) / 2.0))  # Map [-1, 1] to [0, 1]
    anomaly_score = 1.0 - match_score
    
    return {
        "match": match_score,
        "anomaly": anomaly_score,
        "confidence": conf,
        "raw": {"decision": df},
        "is_genuine": is_match
    }

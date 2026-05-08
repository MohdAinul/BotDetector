"""
train.py
Trains a Random Forest classifier for bot detection.
Saves the model and scaler to models/ directory.
"""

import os
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, classification_report,
    confusion_matrix, roc_auc_score
)

# ── 0. Generate data if not present ─────────────────────────────────────────
DATA_PATH = "data/accounts.csv"
if not os.path.exists(DATA_PATH):
    print("⚙️  Dataset not found — generating...")
    import generate_data  # runs the script

# ── 1. Load ──────────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH)
print(f"📦 Loaded {len(df)} rows | Bots: {df['is_bot'].sum()} | Humans: {(df['is_bot']==0).sum()}")

FEATURES = [
    "followers_count", "following_count", "tweet_count", "listed_count",
    "account_age_days", "has_profile_pic", "has_bio", "bio_length",
    "has_url_in_bio", "name_has_numbers", "avg_daily_tweets",
    "follower_following_ratio", "is_verified", "default_theme", "geo_enabled"
]

X = df[FEATURES]
y = df["is_bot"]

# ── 2. Split ──────────────────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ── 3. Scale ──────────────────────────────────────────────────────────────────
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# ── 4. Train ──────────────────────────────────────────────────────────────────
print("\n🔧 Training Random Forest...")
rf = RandomForestClassifier(n_estimators=200, max_depth=12, random_state=42, n_jobs=-1)
rf.fit(X_train_sc, y_train)

# ── 5. Evaluate ───────────────────────────────────────────────────────────────
y_pred = rf.predict(X_test_sc)
y_prob = rf.predict_proba(X_test_sc)[:, 1]

acc     = accuracy_score(y_test, y_pred)
auc     = roc_auc_score(y_test, y_prob)
cv_mean = cross_val_score(rf, X_train_sc, y_train, cv=5, scoring="accuracy").mean()

print(f"\n{'='*45}")
print(f"  Accuracy  : {acc*100:.2f}%")
print(f"  ROC-AUC   : {auc:.4f}")
print(f"  CV Acc    : {cv_mean*100:.2f}%")
print(f"{'='*45}")
print("\n📋 Classification Report:\n")
print(classification_report(y_test, y_pred, target_names=["Human", "Bot"]))

# ── 6. Feature Importance Plot ────────────────────────────────────────────────
os.makedirs("models", exist_ok=True)
importances = pd.Series(rf.feature_importances_, index=FEATURES).sort_values(ascending=True)

fig, ax = plt.subplots(figsize=(9, 6))
colors = ["#ef4444" if v > importances.median() else "#3b82f6" for v in importances]
importances.plot(kind="barh", color=colors, ax=ax)
ax.set_title("Feature Importance — Bot Detector", fontsize=14, fontweight="bold")
ax.set_xlabel("Importance Score")
ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("models/feature_importance.png", dpi=150)
plt.close()
print("📊 Feature importance chart saved → models/feature_importance.png")

# ── 7. Save model & scaler ────────────────────────────────────────────────────
joblib.dump(rf,     "models/bot_detector.pkl")
joblib.dump(scaler, "models/scaler.pkl")

# Save metrics for dashboard
metrics = {
    "accuracy": round(acc * 100, 2),
    "auc":      round(auc, 4),
    "cv_acc":   round(cv_mean * 100, 2),
    "features": FEATURES,
    "importances": importances.to_dict(),
    "confusion": confusion_matrix(y_test, y_pred).tolist(),
    "n_train":  len(X_train),
    "n_test":   len(X_test),
    "n_bots":   int(df["is_bot"].sum()),
    "n_humans": int((df["is_bot"] == 0).sum()),
}
import json
with open("models/metrics.json", "w") as f:
    json.dump(metrics, f, indent=2)

print("\n✅ Model saved  → models/bot_detector.pkl")
print("✅ Scaler saved → models/scaler.pkl")
print("✅ Metrics saved → models/metrics.json")
print("\n🚀 Now run:  python app/app.py")

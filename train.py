import os, json, joblib
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix

# Load data (auto-downloads if not present)
if not os.path.exists("data/accounts.csv"):
    from load_data import load_and_clean
    df, FEATURES = load_and_clean()
else:
    from load_data import load_and_clean
    df, FEATURES = load_and_clean()

X = df[FEATURES]
y = df["is_bot"]

# WHY stratify=y? Dataset is imbalanced (more humans than bots)
# stratify ensures both train and test have the same bot/human ratio
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# WHY StandardScaler? Features are on very different scales:
# followers_count can be 100,000 but verified is 0 or 1
# Without scaling, large numbers dominate. Scaler fixes this.
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

# WHY 3 models? Shows you understand tradeoffs:
# - Logistic Regression: fast, interpretable, baseline
# - Random Forest: handles non-linear patterns, robust
# - Gradient Boosting: usually best accuracy, slower to train
models = {
    "Logistic Regression": LogisticRegression(max_iter=1000, random_state=42),
    "Random Forest":       RandomForestClassifier(n_estimators=200, max_depth=15, random_state=42, n_jobs=-1),
    "Gradient Boosting":   GradientBoostingClassifier(n_estimators=150, max_depth=5, random_state=42),
}

results = {}
print("\n" + "="*50)
for name, model in models.items():
    print(f"Training {name}...")
    model.fit(X_train_sc, y_train)
    
    y_pred = model.predict(X_test_sc)
    y_prob = model.predict_proba(X_test_sc)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    cv  = cross_val_score(model, X_train_sc, y_train, cv=5, scoring="accuracy").mean()
    
    results[name] = {"accuracy": round(acc*100,2), "auc": round(auc,4), "cv": round(cv*100,2)}
    print(f"  Accuracy: {acc*100:.2f}% | AUC: {auc:.4f} | CV: {cv*100:.2f}%")

print("="*50)

# Pick best model by AUC score (more reliable than accuracy for imbalanced data)
best_name = max(results, key=lambda k: results[k]["auc"])
best_model = models[best_name]
print(f"\nBest model: {best_name}")

# Full report for best model
y_pred_best = best_model.predict(X_test_sc)
y_prob_best = best_model.predict_proba(X_test_sc)[:, 1]
print(classification_report(y_test, y_pred_best, target_names=["Human","Bot"]))

# Feature importance (only for tree-based models)
os.makedirs("models", exist_ok=True)
if hasattr(best_model, "feature_importances_"):
    imp = pd.Series(best_model.feature_importances_, index=FEATURES).sort_values(ascending=True)
    fig, ax = plt.subplots(figsize=(9,6))
    colors = ["#ef4444" if v > imp.median() else "#3b82f6" for v in imp]
    imp.plot(kind="barh", color=colors, ax=ax)
    ax.set_title(f"Feature Importance — {best_name}", fontsize=14, fontweight="bold")
    ax.spines[["top","right"]].set_visible(False)
    plt.tight_layout()
    plt.savefig("models/feature_importance.png", dpi=150)
    plt.close()

# Save everything
joblib.dump(best_model, "models/bot_detector.pkl")
joblib.dump(scaler,     "models/scaler.pkl")

metrics = {
    "best_model":    best_name,
    "all_results":   results,
    "accuracy":      results[best_name]["accuracy"],
    "auc":           results[best_name]["auc"],
    "cv_acc":        results[best_name]["cv"],
    "features":      FEATURES,
    "importances":   imp.to_dict() if hasattr(best_model, "feature_importances_") else {},
    "confusion":     confusion_matrix(y_test, y_pred_best).tolist(),
    "n_train":       len(X_train),
    "n_test":        len(X_test),
    "n_bots":        int(y.sum()),
    "n_humans":      int((y==0).sum()),
    "dataset":       "Real Twitter/X accounts — HuggingFace airt-ml/twitter-human-bots",
}
with open("models/metrics.json","w") as f:
    json.dump(metrics, f, indent=2)

print(f"\nModel saved → models/bot_detector.pkl")
print(f"Run: python app/app.py")
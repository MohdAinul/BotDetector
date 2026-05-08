# Social Media Bot Detector

An ML-powered dashboard to detect fake and bot social media accounts using behavioral and profile-based features. Built with Python, Scikit-learn, and Plotly Dash.

---

## Features

- **Random Forest classifier** trained on 2,000 labeled accounts (bots vs humans)
- **15 behavioral features** — follower ratio, daily tweet rate, account age, profile completeness, and more
- **Interactive Dash dashboard** with:
  - Model accuracy, ROC-AUC, and CV metrics
  - Feature importance chart
  - Confusion matrix
  - Followers vs Following scatter plot
  - Tweet activity distribution
  - **Live Account Checker** — enter any account's stats and get real-time bot probability with a gauge chart

---

## Project Structure

```
BotDetector/
├── app/
│   └── app.py              # Dash web dashboard
├── data/
│   └── accounts.csv        # Generated dataset (2000 accounts)
├── models/
│   ├── bot_detector.pkl    # Trained Random Forest model
│   ├── scaler.pkl          # Feature scaler
│   ├── metrics.json        # Saved evaluation metrics
│   └── feature_importance.png
├── src/
│   ├── generate_data.py    # Synthetic dataset generator
│   └── train.py            # Model training pipeline
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup & Run

```bash
# 1. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate      # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Generate dataset
python src/generate_data.py

# 4. Train the model
python src/train.py

# 5. Launch dashboard
python app/app.py
```

Then open **http://localhost:8050** in your browser.

---

## Features Used for Detection

| Feature                    | Why It Matters                             |
| -------------------------- | ------------------------------------------ |
| `follower_following_ratio` | Bots follow many, gain few followers       |
| `avg_daily_tweets`         | Bots tweet at inhuman rates                |
| `account_age_days`         | Bot accounts are usually very new          |
| `name_has_numbers`         | Bot usernames often end in random numbers  |
| `has_profile_pic`          | Bots frequently skip profile pictures      |
| `is_verified`              | Verified accounts are almost never bots    |
| `tweet_count`              | Bots have abnormally high tweet counts     |
| `listed_count`             | Real accounts get added to lists by others |

---

## Model Performance

| Metric             | Score |
| ------------------ | ----- |
| Accuracy           | ~96%  |
| ROC-AUC            | ~0.99 |
| Cross-Val Accuracy | ~96%  |

---

## 🛠 Tech Stack

- **Python** — Core language
- **Pandas & NumPy** — Data processing
- **Scikit-learn** — Random Forest, preprocessing, evaluation
- **Plotly & Dash** — Interactive dashboard
- **Matplotlib** — Feature importance visualization
- **Joblib** — Model serialization

---

## 👤 Author

**Mohd Ainul**
[GitHub](https://github.com/MohdAinul) · [LinkedIn](https://www.linkedin.com/in/mohd-ainul-27492b27a/) · [Portfolio](https://portfolio-kappa-bay-89.vercel.app)

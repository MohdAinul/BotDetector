"""
generate_data.py
Creates a realistic synthetic Social Media Bot Detection dataset.
Features are based on real research on Twitter/X bot behaviour.
"""

import numpy as np
import pandas as pd
import os

np.random.seed(42)
N = 2000  # 1000 bots + 1000 humans


def generate_humans(n):
    return pd.DataFrame({
        "followers_count":        np.random.randint(50, 5000, n),
        "following_count":        np.random.randint(50, 2000, n),
        "tweet_count":            np.random.randint(100, 8000, n),
        "listed_count":           np.random.randint(0, 200, n),
        "account_age_days":       np.random.randint(180, 3650, n),
        "has_profile_pic":        np.random.choice([0, 1], n, p=[0.05, 0.95]),
        "has_bio":                np.random.choice([0, 1], n, p=[0.10, 0.90]),
        "bio_length":             np.random.randint(20, 160, n),
        "has_url_in_bio":         np.random.choice([0, 1], n, p=[0.50, 0.50]),
        "name_has_numbers":       np.random.choice([0, 1], n, p=[0.85, 0.15]),
        "avg_daily_tweets":       np.round(np.random.uniform(0.5, 10, n), 2),
        "follower_following_ratio": np.round(np.random.uniform(0.3, 5.0, n), 2),
        "is_verified":            np.random.choice([0, 1], n, p=[0.93, 0.07]),
        "default_theme":          np.random.choice([0, 1], n, p=[0.80, 0.20]),
        "geo_enabled":            np.random.choice([0, 1], n, p=[0.30, 0.70]),
        "is_bot":                 np.zeros(n, dtype=int),
    })


def generate_bots(n):
    return pd.DataFrame({
        "followers_count":        np.random.randint(0, 500, n),
        "following_count":        np.random.randint(500, 6000, n),
        "tweet_count":            np.random.randint(1000, 50000, n),
        "listed_count":           np.random.randint(0, 10, n),
        "account_age_days":       np.random.randint(1, 400, n),
        "has_profile_pic":        np.random.choice([0, 1], n, p=[0.40, 0.60]),
        "has_bio":                np.random.choice([0, 1], n, p=[0.55, 0.45]),
        "bio_length":             np.random.randint(0, 60, n),
        "has_url_in_bio":         np.random.choice([0, 1], n, p=[0.30, 0.70]),
        "name_has_numbers":       np.random.choice([0, 1], n, p=[0.20, 0.80]),
        "avg_daily_tweets":       np.round(np.random.uniform(20, 200, n), 2),
        "follower_following_ratio": np.round(np.random.uniform(0.001, 0.3, n), 4),
        "is_verified":            np.zeros(n, dtype=int),
        "default_theme":          np.random.choice([0, 1], n, p=[0.30, 0.70]),
        "geo_enabled":            np.random.choice([0, 1], n, p=[0.80, 0.20]),
        "is_bot":                 np.ones(n, dtype=int),
    })


if __name__ == "__main__":
    humans = generate_humans(N // 2)
    bots   = generate_bots(N // 2)
    df     = pd.concat([humans, bots], ignore_index=True).sample(frac=1, random_state=42)

    os.makedirs("data", exist_ok=True)
    df.to_csv("data/accounts.csv", index=False)
    print(f"✅ Dataset saved → data/accounts.csv  ({len(df)} rows, {df['is_bot'].sum()} bots)")

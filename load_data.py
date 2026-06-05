import pandas as pd
import numpy as np
import os

def load_and_clean():
    print("Downloading real Twitter dataset...")
    
    url = "https://huggingface.co/datasets/airt-ml/twitter-human-bots/resolve/refs%2Fconvert%2Fparquet/default/train/0000.parquet"
    
    try:
        df = pd.read_parquet(url)
        print(f"Loaded {len(df)} real accounts")
    except:
        from datasets import load_dataset
        df = load_dataset("airt-ml/twitter-human-bots", split="train").to_pandas()

    # Convert bot/human string to 0/1 for sklearn
    df["is_bot"] = (df["account_type"] == "bot").astype(int)

    # FEATURE ENGINEERING
    
    # Real people write bios, bots don't
    df["has_description"] = df["description"].notna().astype(int)
    
    # Bio length — bots have empty or copy-paste spam bios
    df["description_length"] = df["description"].fillna("").apply(len)
    
    # Follower/Following ratio — THE strongest bot signal
    # Bots follow 5000 people hoping for followback, get 10 followers
    df["friends_count"] = df["friends_count"].replace(0, 1)
    df["follower_following_ratio"] = (
        df["followers_count"] / df["friends_count"]
    ).round(4)
    
    # Has location? Real users set it, bots leave it blank/unknown
    df["has_location"] = (
        df["location"].notna() & (df["location"] != "unknown")
    ).astype(int)

    # Convert booleans to int — sklearn needs numbers, not True/False
    for col in ["default_profile", "default_profile_image", "geo_enabled", "verified"]:
        df[col] = df[col].astype(int)

    # Fill nulls with median 
    # Mean gets pulled by celebrities with 10M followers
    # Median stays stable regardless of outliers
    for col in ["followers_count","friends_count","statuses_count",
                "favourites_count","account_age_days","average_tweets_per_day",
                "follower_following_ratio","description_length"]:
        df[col] = df[col].fillna(df[col].median())

    # Clip extreme outliers at 99th percentile
    # WHY: NBA account with 122M followers would dominate the model
    # We cap it so one celebrity doesn't skew everything
    df["followers_count"]         = df["followers_count"].clip(upper=df["followers_count"].quantile(0.99))
    df["friends_count"]           = df["friends_count"].clip(upper=df["friends_count"].quantile(0.99))
    df["statuses_count"]          = df["statuses_count"].clip(upper=df["statuses_count"].quantile(0.99))
    df["average_tweets_per_day"]  = df["average_tweets_per_day"].clip(upper=200)
    df["follower_following_ratio"]= df["follower_following_ratio"].clip(upper=100)

    FEATURES = [
        "followers_count",           # raw follower count
        "friends_count",             # how many they follow
        "statuses_count",            # total tweets ever posted
        "favourites_count",          # likes given (bots rarely like)
        "account_age_days",          # older accounts = more likely human
        "average_tweets_per_day",    # 100+ tweets/day = bot signal
        "follower_following_ratio",  # < 0.1 = almost certainly bot
        "default_profile",           # kept default theme = lazy bot
        "default_profile_image",     # no profile pic = bot red flag
        "geo_enabled",               # real users share location
        "verified",                  # bots are never verified
        "has_description",           # no bio = bot signal
        "description_length",        # very short/long bio = suspicious
        "has_location",              # no location = bot signal
    ]

    os.makedirs("data", exist_ok=True)
    df.to_parquet("data/accounts.parquet", index=False)
    print(f"Saved → data/accounts.csv ({df.shape})")
    return df, FEATURES

if __name__ == "__main__":
    load_and_clean()
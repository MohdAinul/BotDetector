"""
app.py  —  Social Media Bot Detector Dashboard
Run:  python app/app.py
Then open: http://localhost:8050
"""

import os, sys, json
import joblib
import numpy as np
import pandas as pd

import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objects as go
import plotly.express as px

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
MODEL_PATH   = os.path.join(ROOT, "models", "bot_detector.pkl")
SCALER_PATH  = os.path.join(ROOT, "models", "scaler.pkl")
METRICS_PATH = os.path.join(ROOT, "models", "metrics.json")
DATA_PATH = os.path.join(ROOT, "data", "accounts.parquet")

# ── Auto-train if model missing ───────────────────────────────────────────────
if not os.path.exists(MODEL_PATH):
    print("⚙️  Model not found — running training pipeline...")
    os.chdir(ROOT)
    import load_data
    import train

model  = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
df = pd.read_parquet(DATA_PATH)

with open(METRICS_PATH) as f:
    metrics = json.load(f)

FEATURES = metrics["features"]

# ── Colour palette ────────────────────────────────────────────────────────────
BOT_RED   = "#ef4444"
HUMAN_GRN = "#22c55e"
BLUE      = "#3b82f6"
BG        = "#0f172a"
CARD      = "#1e293b"
TEXT      = "#f1f5f9"
SUBTEXT   = "#94a3b8"

# ── Helper: stat card ─────────────────────────────────────────────────────────
def stat_card(title, value, color=BLUE):
    return html.Div([
        html.P(title, style={"color": SUBTEXT, "margin": "0", "fontSize": "13px"}),
        html.H3(value, style={"color": color,  "margin": "4px 0 0", "fontSize": "26px"}),
    ], style={
        "background": CARD, "borderRadius": "12px", "padding": "18px 22px",
        "flex": "1", "minWidth": "150px", "borderTop": f"3px solid {color}"
    })

# ── Feature importance chart ──────────────────────────────────────────────────
imp = metrics["importances"]
imp_df = pd.DataFrame({"feature": list(imp.keys()), "score": list(imp.values())}).sort_values("score")
fig_imp = go.Figure(go.Bar(
    x=imp_df["score"], y=imp_df["feature"], orientation="h",
    marker_color=[BOT_RED if v > imp_df["score"].median() else BLUE for v in imp_df["score"]],
    hovertemplate="<b>%{y}</b>: %{x:.4f}<extra></extra>"
))
fig_imp.update_layout(
    title="Feature Importance", paper_bgcolor=CARD, plot_bgcolor=CARD,
    font_color=TEXT, margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor="#334155"),
    yaxis=dict(showgrid=False),
)

# ── Confusion matrix ──────────────────────────────────────────────────────────
cm = np.array(metrics["confusion"])
fig_cm = go.Figure(go.Heatmap(
    z=cm, x=["Pred: Human", "Pred: Bot"], y=["True: Human", "True: Bot"],
    colorscale=[[0, CARD], [1, BLUE]],
    text=cm, texttemplate="%{text}", showscale=False,
    hovertemplate="<b>%{y} → %{x}</b>: %{z}<extra></extra>"
))
fig_cm.update_layout(
    title="Confusion Matrix", paper_bgcolor=CARD, plot_bgcolor=CARD,
    font_color=TEXT, margin=dict(l=10, r=10, t=40, b=10)
)

# ── Scatter: followers vs following ──────────────────────────────────────────
sample_df = df.sample(600, random_state=1)
fig_scatter = px.scatter(
    sample_df, x="friends_count", y="followers_count",
    color=sample_df["is_bot"].map({0: "Human", 1: "Bot"}),
    color_discrete_map={"Human": HUMAN_GRN, "Bot": BOT_RED},
    opacity=0.65, title="Followers vs Following by Account Type",
    labels={"friends_count": "Following", "followers_count": "Followers", "color": "Type"},
)

fig_scatter.update_layout(
    paper_bgcolor=CARD, plot_bgcolor=CARD, font_color=TEXT,
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(showgrid=True, gridcolor="#334155"),
    yaxis=dict(showgrid=True, gridcolor="#334155"),
)

# ── Tweet activity histogram ──────────────────────────────────────────────────
fig_hist = go.Figure()
for label, color in [("Human", HUMAN_GRN), ("Bot", BOT_RED)]:
    subset = df[df["is_bot"] == (1 if label == "Bot" else 0)]["average_tweets_per_day"]
    fig_hist.add_trace(go.Histogram(
        x=subset.clip(upper=100), name=label,
        marker_color=color, opacity=0.75, nbinsx=40
    ))
fig_hist.update_layout(
    barmode="overlay", title="Avg Daily Tweets Distribution",
    paper_bgcolor=CARD, plot_bgcolor=CARD, font_color=TEXT,
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(title="Avg Daily Tweets", showgrid=True, gridcolor="#334155"),
    yaxis=dict(title="Count",            showgrid=True, gridcolor="#334155"),
    legend=dict(bgcolor=CARD)
)

# ── App layout ────────────────────────────────────────────────────────────────
app = dash.Dash(__name__, title="🤖 Bot Detector")
app.layout = html.Div(style={"background": BG, "minHeight": "100vh",
                              "fontFamily": "Inter, sans-serif", "color": TEXT,
                              "padding": "24px 32px"}, children=[

    # Header
    html.Div([
        html.H1("🤖 Social Media Bot Detector",
                style={"margin": "0", "fontSize": "28px", "fontWeight": "700"}),
        html.P("ML dashboard trained on 37,438 real Twitter accounts — HuggingFace dataset",
               style={"color": SUBTEXT, "margin": "4px 0 0"}),
    ], style={"marginBottom": "28px"}),

    # Stat cards
    html.Div([
        stat_card("Model Accuracy",  f"{metrics['accuracy']}%",    HUMAN_GRN),
        stat_card("ROC-AUC Score",   str(metrics['auc']),           BLUE),
        stat_card("CV Accuracy",     f"{metrics['cv_acc']}%",       BLUE),
        stat_card("Total Accounts",  f"{metrics['n_train']+metrics['n_test']:,}", SUBTEXT),
        stat_card("Bots in Dataset", f"{metrics['n_bots']:,}",      BOT_RED),
        stat_card("Humans in Dataset",f"{metrics['n_humans']:,}",   HUMAN_GRN),
    ], style={"display": "flex", "gap": "16px", "flexWrap": "wrap", "marginBottom": "28px"}),

    # Charts row 1
    html.Div([
        html.Div(dcc.Graph(figure=fig_imp,     config={"displayModeBar": False}),
                 style={"flex": "2", "background": CARD, "borderRadius": "12px", "padding": "12px"}),
        html.Div(dcc.Graph(figure=fig_cm,      config={"displayModeBar": False}),
                 style={"flex": "1", "background": CARD, "borderRadius": "12px", "padding": "12px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "16px"}),

    # Charts row 2
    html.Div([
        html.Div(dcc.Graph(figure=fig_scatter, config={"displayModeBar": False}),
                 style={"flex": "1", "background": CARD, "borderRadius": "12px", "padding": "12px"}),
        html.Div(dcc.Graph(figure=fig_hist,    config={"displayModeBar": False}),
                 style={"flex": "1", "background": CARD, "borderRadius": "12px", "padding": "12px"}),
    ], style={"display": "flex", "gap": "16px", "marginBottom": "28px"}),

    # ── Live Predictor ────────────────────────────────────────────────────────
    html.Div([
        html.H2("🔍 Live Account Checker",
                style={"margin": "0 0 20px", "fontSize": "20px", "fontWeight": "600"}),

        # Row 1
        html.Div([
            html.Div([html.Label("Followers Count"),
                      dcc.Input(id="followers",  type="number", value=120,
                                style={"width":"100%","padding":"8px","borderRadius":"6px",
                                       "border":"1px solid #334155","background":"#0f172a","color":TEXT})]),
            html.Div([html.Label("Following Count"),
                      dcc.Input(id="following",  type="number", value=4500,
                                style={"width":"100%","padding":"8px","borderRadius":"6px",
                                       "border":"1px solid #334155","background":"#0f172a","color":TEXT})]),
            html.Div([html.Label("Tweet Count"),
                      dcc.Input(id="tweets",     type="number", value=25000,
                                style={"width":"100%","padding":"8px","borderRadius":"6px",
                                       "border":"1px solid #334155","background":"#0f172a","color":TEXT})]),
            html.Div([html.Label("Account Age (days)"),
                      dcc.Input(id="age",        type="number", value=60,
                                style={"width":"100%","padding":"8px","borderRadius":"6px",
                                       "border":"1px solid #334155","background":"#0f172a","color":TEXT})]),
            html.Div([html.Label("Avg Daily Tweets"),
                      dcc.Input(id="daily",      type="number", value=85,
                                style={"width":"100%","padding":"8px","borderRadius":"6px",
                                       "border":"1px solid #334155","background":"#0f172a","color":TEXT})]),
        ], style={"display":"grid","gridTemplateColumns":"repeat(5,1fr)","gap":"16px","marginBottom":"16px"}),

        # Row 2 — Toggles
        html.Div([
            html.Div([html.Label("Has Profile Pic?"),
                      dcc.Dropdown(id="pic",     options=[{"label":"Yes","value":1},{"label":"No","value":0}],
                                   value=0, clearable=False,
                                   style={"background":"#0f172a","color":"#000"})]),
            html.Div([html.Label("Has Bio?"),
                      dcc.Dropdown(id="bio",     options=[{"label":"Yes","value":1},{"label":"No","value":0}],
                                   value=0, clearable=False,
                                   style={"background":"#0f172a","color":"#000"})]),
            html.Div([html.Label("Name Has Numbers?"),
                      dcc.Dropdown(id="numname", options=[{"label":"Yes","value":1},{"label":"No","value":0}],
                                   value=1, clearable=False,
                                   style={"background":"#0f172a","color":"#000"})]),
            html.Div([html.Label("Is Verified?"),
                      dcc.Dropdown(id="verified",options=[{"label":"Yes","value":1},{"label":"No","value":0}],
                                   value=0, clearable=False,
                                   style={"background":"#0f172a","color":"#000"})]),
            html.Div([html.Label("Default Theme?"),
                      dcc.Dropdown(id="theme",   options=[{"label":"Yes","value":1},{"label":"No","value":0}],
                                   value=1, clearable=False,
                                   style={"background":"#0f172a","color":"#000"})]),
        ], style={"display":"grid","gridTemplateColumns":"repeat(5,1fr)","gap":"16px","marginBottom":"20px"}),

        html.Button("🔍 Analyse Account", id="predict-btn",
                    style={"background": BLUE, "color": TEXT, "border": "none",
                           "padding": "12px 32px", "borderRadius": "8px",
                           "fontSize": "15px", "fontWeight": "600", "cursor": "pointer"}),

        html.Div(id="result-box", style={"marginTop": "24px"}),
    ], style={"background": CARD, "borderRadius": "16px", "padding": "28px"}),
])


# ── Callback: Live Prediction ─────────────────────────────────────────────────
@app.callback(
    Output("result-box", "children"),
    Input("predict-btn", "n_clicks"),
    State("followers",  "value"),
    State("following",  "value"),
    State("tweets",     "value"),
    State("age",        "value"),
    State("daily",      "value"),
    State("pic",        "value"),
    State("bio",        "value"),
    State("numname",    "value"),
    State("verified",   "value"),
    State("theme",      "value"),
    prevent_initial_call=True,
)
def predict(n, followers, following, tweets, age, daily, pic, bio, numname, verified, theme):
    followers = followers or 0
    following = following or 1
    tweets    = tweets    or 0
    age       = age       or 1
    daily     = daily     or 0

    ratio   = round(followers / following, 4) if following else 0
    bio_len = np.random.randint(20, 60) if bio else 0

    # NEW — matches real dataset's 14 features exactly:
    # followers_count, friends_count, statuses_count, favourites_count,
    # account_age_days, average_tweets_per_day, follower_following_ratio,
    # default_profile, default_profile_image, geo_enabled, verified,
    # has_description, description_length, has_location
    features = np.array([[
        followers,   # followers_count
        following,   # friends_count
        tweets,      # statuses_count
        0,           # favourites_count (not in UI, default 0)
        age,         # account_age_days
        daily,       # average_tweets_per_day
        ratio,       # follower_following_ratio
        theme,       # default_profile
        1 - pic,     # default_profile_image (no pic = 1)
        0,           # geo_enabled (not in UI, default 0)
        verified,    # verified
        bio,         # has_description
        bio_len,     # description_length
        0,           # has_location (not in UI, default 0)
    ]])

    features_sc = scaler.transform(features)
    prob_bot    = model.predict_proba(features_sc)[0][1]
    prob_human  = 1 - prob_bot
    prediction  = "🤖 BOT" if prob_bot >= 0.5 else "✅ HUMAN"
    color       = BOT_RED if prob_bot >= 0.5 else HUMAN_GRN

    gauge = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=round(prob_bot * 100, 1),
        title={"text": "Bot Probability (%)", "font": {"color": TEXT}},
        delta={"reference": 50},
        gauge={
            "axis":  {"range": [0, 100], "tickcolor": TEXT},
            "bar":   {"color": color},
            "bgcolor": CARD,
            "steps": [
                {"range": [0,  50], "color": "#14532d"},
                {"range": [50, 100], "color": "#7f1d1d"},
            ],
            "threshold": {"line": {"color": "white", "width": 3}, "value": 50}
        },
        number={"suffix": "%", "font": {"color": color, "size": 48}}
    ))
    gauge.update_layout(
        paper_bgcolor=CARD, font_color=TEXT,
        height=280, margin=dict(l=30, r=30, t=30, b=10)
    )

    return html.Div([
        html.Div([
            html.H2(prediction, style={"color": color, "margin": "0", "fontSize": "32px"}),
            html.P(f"Bot: {prob_bot*100:.1f}%  |  Human: {prob_human*100:.1f}%",
                   style={"color": SUBTEXT, "margin": "6px 0 0"}),
        ], style={"marginBottom": "16px"}),
        dcc.Graph(figure=gauge, config={"displayModeBar": False}),
    ])


if __name__ == "__main__":
    app.run(debug=True, port=8050)

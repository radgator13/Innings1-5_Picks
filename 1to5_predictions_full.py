﻿import pandas as pd
import joblib
import os
from datetime import datetime

# === Load model ===
model_path = "models/innings1to5_rf_model.pkl"
model, feature_cols = joblib.load(model_path)
print(f"✅ Loaded model from {model_path}")

# === Load boxscores ===
boxscore_path = 'data/mlb_boxscores_full.csv'
print(f"\n📥 Loading boxscores from {boxscore_path}")
full_df = pd.read_csv(boxscore_path)
print(f"📊 Loaded {len(full_df)} total rows")

# === Normalize team names early ===
full_df['Away Team'] = full_df['Away Team'].str.strip().str.lower()
full_df['Home Team'] = full_df['Home Team'].str.strip().str.lower()

# === Detect pending BEFORE cleaning ===
def is_pending(row):
    inning_cols = [f"Away {i}th" for i in range(1, 6)] + [f"Home {i}th" for i in range(1, 6)]
    vals = [str(row.get(col, "")).strip().lower() for col in inning_cols]
    return all(v in ["pending", "", "nan"] for v in vals)

full_df["is_pending"] = full_df.apply(is_pending, axis=1)

# === Clean innings and calculate total ===
full_df['Total_1to5_Runs'] = 0
for i in range(1, 6):
    full_df[f'Away {i}th'] = full_df[f'Away {i}th'].replace('Pending', 0)
    full_df[f'Home {i}th'] = full_df[f'Home {i}th'].replace('Pending', 0)
    full_df[f'Away {i}th'] = full_df[f'Away {i}th'].fillna(0).astype(int)
    full_df[f'Home {i}th'] = full_df[f'Home {i}th'].fillna(0).astype(int)
    full_df['Total_1to5_Runs'] += full_df[f'Away {i}th'] + full_df[f'Home {i}th']

# === Date and key setup ===
full_df['Game Date'] = pd.to_datetime(full_df['Game Date'])
today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
full_df['key'] = list(zip(full_df['Game Date'].dt.strftime('%Y-%m-%d'), full_df['Away Team'], full_df['Home Team']))

# === Load existing predictions ===
predictions_file = "data/mlb_boxscores_1to5_model_full_predictions.csv"
if os.path.exists(predictions_file):
    existing_preds = pd.read_csv(predictions_file)
    existing_preds['Away Team'] = existing_preds['Away Team'].str.strip().str.lower()
    existing_preds['Home Team'] = existing_preds['Home Team'].str.strip().str.lower()
    existing_preds['key'] = list(zip(existing_preds['Game Date'], existing_preds['Away Team'], existing_preds['Home Team']))
    existing_preds['Game Date'] = pd.to_datetime(existing_preds['Game Date'])
    print(f"📄 Existing predictions loaded: {len(existing_preds)}")
else:
    existing_preds = pd.DataFrame()
    print("📄 No existing predictions found — starting fresh.")

existing_keys = set(existing_preds['key']) if not existing_preds.empty else set()

# === Identify new games (not in predictions) ===
new_games_df = full_df[
    (~full_df['key'].isin(existing_keys)) &
    (full_df['Game Date'] >= today)
]

# === Identify truly pending games (no key filter) ===
filtered_pending = full_df[
    (full_df['is_pending']) &
    (full_df['Game Date'] >= today)
]

# === Combine all to predict ===
games_to_predict = pd.concat([new_games_df, filtered_pending], ignore_index=True)

# === EXTENSIVE DEBUGGING ===
print("\n🚨 BEGIN DEBUGGING SECTION")
print(f"📆 Today: {today}")
print(f"📊 Total rows in full_df: {len(full_df)}")
print(f"🆕 New games (not in predictions): {len(new_games_df)}")
print(f"⏳ Pending games based on inning columns: {len(filtered_pending)}")
print(f"🧮 Games to predict (combined): {len(games_to_predict)}")
print("🚨 END DEBUGGING SECTION\n")

# === ADD FEATURES ===
games_to_predict["DayOfWeek"] = games_to_predict["Game Date"].dt.dayofweek

# Extract win % from records
def extract_win_pct(record):
    try:
        w, l = map(int, str(record).split("-"))
        return w / (w + l) if w + l > 0 else 0.5
    except:
        return 0.5

games_to_predict["HomeWinPct"] = games_to_predict["Home Record"].apply(extract_win_pct)
games_to_predict["AwayWinPct"] = games_to_predict["Away Record"].apply(extract_win_pct)

# === Build features ===
categorical = pd.get_dummies(games_to_predict[["Away Team", "Home Team", "DayOfWeek"]])
numerical = games_to_predict[["HomeWinPct", "AwayWinPct"]]
X_all = pd.concat([categorical, numerical], axis=1)

# Ensure column alignment with model
missing_cols = [col for col in feature_cols if col not in X_all.columns]
for col in missing_cols:
    X_all[col] = 0
X = X_all[feature_cols]

# === Predict ===
all_probs = model.predict_proba(X)[:, 1]
games_to_predict['Predicted_Runs_1to5'] = all_probs * 3 + 3.5
games_to_predict['Target_Line'] = 4.5

# === Over/Under logic ===
tolerance = 0.25
def decide_over_under(row):
    if row['Predicted_Runs_1to5'] > (row['Target_Line'] + tolerance):
        return "Over"
    elif row['Predicted_Runs_1to5'] < (row['Target_Line'] - tolerance):
        return "Under"
    else:
        return "No Bet"

games_to_predict['Predicted_Over_4_5'] = games_to_predict.apply(decide_over_under, axis=1)

# === Actuals ===
def get_actual_over(row):
    inning_scores = [row.get(f'Away {i}th', 0) + row.get(f'Home {i}th', 0) for i in range(1, 6)]
    if all(score == 0 for score in inning_scores):
        return "Pending"
    return "Over" if row['Total_1to5_Runs'] > 4.5 else "Under"

def get_actual_runs(row):
    return "Pending" if row['Actual_Over_4_5'] == "Pending" else row['Total_1to5_Runs']

games_to_predict['Actual_Over_4_5'] = games_to_predict.apply(get_actual_over, axis=1)
games_to_predict['Actual_Runs_1to5'] = games_to_predict.apply(get_actual_runs, axis=1)

# === Output columns ===
output_cols = [
    'Game Date', 'Away Team', 'Home Team',
    'Target_Line', 'Predicted_Runs_1to5', 'Predicted_Over_4_5',
    'Actual_Runs_1to5', 'Actual_Over_4_5'
]
new_predictions = games_to_predict[output_cols].copy()
new_predictions['Away Team'] = new_predictions['Away Team'].str.strip().str.lower()
new_predictions['Home Team'] = new_predictions['Home Team'].str.strip().str.lower()

# === Update actuals in existing_preds ===
def get_updated_actuals(row, actual_lookup):
    key = (row['Game Date'].strftime('%Y-%m-%d'), row['Away Team'], row['Home Team'])
    if key in actual_lookup:
        actual_row = actual_lookup[key]
        inning_scores = [actual_row.get(f'Away {i}th', 0) + actual_row.get(f'Home {i}th', 0) for i in range(1, 6)]
        total_runs = sum(inning_scores)
        if all(score == 0 for score in inning_scores):
            return pd.Series(["Pending", "Pending"])
        over_under = "Over" if total_runs > 4.5 else "Under"
        return pd.Series([over_under, total_runs])
    return pd.Series([row['Actual_Over_4_5'], row['Actual_Runs_1to5']])

actual_lookup = {
    (row['Game Date'].strftime('%Y-%m-%d'), row['Away Team'], row['Home Team']): row
    for _, row in full_df.iterrows()
}

if not existing_preds.empty:
    updates = existing_preds.apply(lambda row: get_updated_actuals(row, actual_lookup), axis=1)
    existing_preds[['Actual_Over_4_5', 'Actual_Runs_1to5']] = updates

# === Save snapshot ===
snapshot_path = f"data/predictions_{datetime.today().strftime('%Y-%m-%d')}.csv"
new_predictions.to_csv(snapshot_path, index=False)
print(f"🗃️ Daily snapshot saved to {snapshot_path}")

# === Merge and save master prediction file ===
if not existing_preds.empty:
    combined = pd.concat([existing_preds, new_predictions])
    combined = combined.drop_duplicates(subset=['Game Date', 'Away Team', 'Home Team'], keep='last')
else:
    combined = new_predictions

combined.to_csv(predictions_file, index=False)
print(f"✅ Final predictions saved to {predictions_file} ({len(combined)} total games)")

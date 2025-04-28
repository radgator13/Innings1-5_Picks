import pandas as pd
import joblib
import os
from datetime import datetime

# 1. Load saved Random Forest model
model_path = "models/innings1to5_rf_model.pkl"
model, feature_cols = joblib.load(model_path)

print(f"✅ Loaded model from {model_path}")

# 2. Load full boxscores
full_df = pd.read_csv('data/mlb_boxscores_full.csv')

# 3. Clean inning columns and calculate Total_1to5_Runs
full_df['Total_1to5_Runs'] = 0

for i in range(1, 6):
    full_df[f'Away {i}th'] = full_df[f'Away {i}th'].replace('Pending', 0)
    full_df[f'Home {i}th'] = full_df[f'Home {i}th'].replace('Pending', 0)

    full_df[f'Away {i}th'] = full_df[f'Away {i}th'].fillna(0).astype(int)
    full_df[f'Home {i}th'] = full_df[f'Home {i}th'].fillna(0).astype(int)

    full_df['Total_1to5_Runs'] += full_df[f'Away {i}th'] + full_df[f'Home {i}th']

# 4. Build features for all games
X_all = pd.get_dummies(full_df[['Away Team', 'Home Team']])
X_all = X_all.reindex(columns=feature_cols, fill_value=0)

# 5. Load existing predictions if available
predictions_file = "data/mlb_boxscores_1to5_model_full_predictions.csv"

if os.path.exists(predictions_file):
    existing_preds = pd.read_csv(predictions_file)
    existing_keys = set(zip(existing_preds['Game Date'], existing_preds['Away Team'], existing_preds['Home Team']))
    print(f"📂 Existing predictions loaded: {len(existing_preds)} games")
else:
    existing_preds = pd.DataFrame()
    existing_keys = set()
    print("📂 No existing predictions file found. Starting fresh.")

# 6. Filter to only new games
full_df['key'] = list(zip(full_df['Game Date'], full_df['Away Team'], full_df['Home Team']))
full_df = full_df[~full_df['key'].isin(existing_keys)]

if full_df.empty:
    print("🚫 No new games to predict. Exiting.")
    exit()

# 7. Predict for only new games
X_all = pd.get_dummies(full_df[['Away Team', 'Home Team']])
X_all = X_all.reindex(columns=feature_cols, fill_value=0)

all_probs = model.predict_proba(X_all)[:, 1]
all_preds = model.predict(X_all)

# 7.5 Predict Over/Under with Tolerance Tuning
full_df['Target_Line'] = 4.5
full_df['Predicted_Runs_1to5'] = all_probs * 3 + 3.5

# Define your tolerance
tolerance = 0.25  # 🔥 You can tune this up or down

# Decision logic
def decide_over_under(row):
    if row['Predicted_Runs_1to5'] > (row['Target_Line'] + tolerance):
        return "Over"
    elif row['Predicted_Runs_1to5'] < (row['Target_Line'] - tolerance):
        return "Under"
    else:
        return "No Bet"  # Close to line, no confident pick

full_df['Predicted_Over_4_5'] = full_df.apply(decide_over_under, axis=1)

# 8. Attach actual game results
def get_actual_over(row):
    inning_scores = [row[f'Away {i}th'] + row[f'Home {i}th'] for i in range(1, 6)]
    if all(score == 0 for score in inning_scores):
        return "Pending"
    return "Over" if row['Total_1to5_Runs'] > 4.5 else "Under"

full_df['Actual_Over_4_5'] = full_df.apply(get_actual_over, axis=1)

def get_actual_runs(row):
    if row['Actual_Over_4_5'] == "Pending":
        return "Pending"
    else:
        return row['Total_1to5_Runs']

full_df['Actual_Runs_1to5'] = full_df.apply(get_actual_runs, axis=1)

# 9. Select relevant columns
new_predictions = full_df[['Game Date', 'Away Team', 'Home Team', 'Target_Line', 'Predicted_Runs_1to5', 'Predicted_Over_4_5', 'Actual_Runs_1to5', 'Actual_Over_4_5']]

# 9.5 Save today's predictions separately (daily snapshot)
from datetime import datetime

today = datetime.today().strftime('%Y-%m-%d')
daily_snapshot_file = f"data/predictions_{today}.csv"

new_predictions.to_csv(daily_snapshot_file, index=False)

print(f"🗃️ Daily snapshot saved to {daily_snapshot_file}")


# 10. Combine with existing predictions
if not existing_preds.empty:
    combined_df = pd.concat([existing_preds, new_predictions])
    combined_df = combined_df.drop_duplicates(subset=['Game Date', 'Away Team', 'Home Team'], keep='last')
else:
    combined_df = new_predictions

# 11. Save back to file
combined_df.to_csv(predictions_file, index=False)

print(f"\n✅ Predictions updated and saved to {predictions_file} ({len(combined_df)} total games)")

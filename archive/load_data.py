import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from datetime import datetime, timedelta
import os


# Step 1: Load played and future data
played_df = pd.read_csv('data/mlb_boxscores_1to5.csv')
future_df = pd.read_csv('data/mlb_boxscores_full.csv')

print(f"Played games loaded: {len(played_df)} rows")
print(f"Future games loaded: {len(future_df)} rows")

# Step 2: Create Over/Under 4.5 labels
line = 4.5

played_df['Over_4_5'] = (played_df['Total_1to5_Runs'] > line).astype(int)

print(played_df[['Game Date', 'Away Team', 'Home Team', 'Total_1to5_Runs', 'Over_4_5']].head())

# Step 3: Prepare features
# Turn Away Team and Home Team into one-hot encoded features
X = pd.get_dummies(played_df[['Away Team', 'Home Team']])

# Target variable: Over 4.5 label
y = played_df['Over_4_5']

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train a simple Logistic Regression model
model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

# Predict on the testing set
y_pred = model.predict(X_test)

# Evaluate accuracy
accuracy = accuracy_score(y_test, y_pred)
print(f"\n🎯 Backtest Accuracy: {accuracy:.3f}")

# Step 4: Predict upcoming games

# Find games where 1st inning is still Pending
pending_games = future_df[
    (future_df['Away 1th'] == 'Pending') & (future_df['Home 1th'] == 'Pending')
]

print(f"\n🔮 Pending games found: {len(pending_games)}")

if not pending_games.empty:
    # Create the same one-hot encoded features
    pending_X = pd.get_dummies(pending_games[['Away Team', 'Home Team']])

    # Make sure columns match training set
    pending_X = pending_X.reindex(columns=X.columns, fill_value=0)

    # Predict Over/Under
    pending_preds = model.predict(pending_X)

    # Attach predictions back to games
    pending_games = pending_games.copy()
    pending_games['Predicted_Over_4_5'] = pending_preds

    # Show the predictions
    print("\n📋 Predictions for today's and tomorrow's games (innings 1-5 Over/Under 4.5):")
    print(pending_games[['Game Date', 'Away Team', 'Home Team', 'Predicted_Over_4_5']])
else:
    print("🚫 No pending games found for prediction.")

    

import os

# Step 5: Save today's predictions using model probabilities, with readable Over/Under

# Use today's date for the filename
today_str = datetime.today().strftime('%Y-%m-%d')
output_filename = f"data/predictions_{today_str}.csv"

if not os.path.exists(output_filename):
    pending_games = pending_games.copy()
    pending_games['Target_Line'] = 4.5  # Static line

    # Get prediction probabilities (column 1 = probability of Over)
    pending_probs = model.predict_proba(pending_X)[:, 1]

    # Estimate predicted runs based on model probability
    pending_games['Predicted_Runs_1to5'] = pending_probs * 3 + 3.5

    # Map 1 → 'Over', 0 → 'Under'
    pending_games['Predicted_Over_4_5'] = pending_games['Predicted_Over_4_5'].map({1: 'Over', 0: 'Under'})

    # Save to CSV
    pending_games[['Game Date', 'Away Team', 'Home Team', 'Predicted_Over_4_5', 'Target_Line', 'Predicted_Runs_1to5']].to_csv(output_filename, index=False)
    
    print(f"\n✅ Saved predictions to {output_filename}")
else:
    print(f"\n⏩ Predictions already saved for {today_str}. No new file created.")


# Step 6: Create upgraded historical backtest CSV

# Only proceed if played_df is already loaded
if 'played_df' in globals():
    played_df = played_df.copy()
    played_df['Target_Line'] = 4.5

    # Make features same as training
    X_played = pd.get_dummies(played_df[['Away Team', 'Home Team']])
    X_played = X_played.reindex(columns=X.columns, fill_value=0)  # align to training columns

    # Predict using the trained model
    played_probs = model.predict_proba(X_played)[:, 1]
    played_preds = model.predict(X_played)

    # Add model outputs
    played_df['Predicted_Runs_1to5'] = played_probs * 3 + 3.5
    played_df['Predicted_Over_4_5'] = pd.Series(played_preds).map({1: 'Over', 0: 'Under'})
    played_df['Actual_Runs_1to5'] = played_df['Total_1to5_Runs']
    played_df['Actual_Over_4_5'] = played_df['Over_4_5'].map({1: 'Over', 0: 'Under'})

    # Save to a new CSV
    played_output_file = "data/mlb_boxscores_1to5_predictions.csv"
    played_df[['Game Date', 'Away Team', 'Home Team', 'Target_Line', 'Predicted_Runs_1to5', 'Predicted_Over_4_5', 'Actual_Runs_1to5', 'Actual_Over_4_5']].to_csv(played_output_file, index=False)

    print(f"\n✅ Historical predictions saved to {played_output_file}")
else:
    print("🚫 played_df not found. Please load played games first.")

# Step 7: Append pending games to historical predictions

if 'played_df' in globals() and 'future_df' in globals():
    # Copy played_df
    played_df = played_df.copy()
    
    # Load pending games
    pending_df = future_df.copy()
    pending_df = pending_df[
        (pending_df['Away 1th'] == 'Pending') & (pending_df['Home 1th'] == 'Pending')
    ]
    
    print(f"🔄 Pending games found to append: {len(pending_df)}")

    if not pending_df.empty:
        # Build features for pending games
        X_pending = pd.get_dummies(pending_df[['Away Team', 'Home Team']])
        X_pending = X_pending.reindex(columns=X.columns, fill_value=0)

        # Predict pending
        pending_probs = model.predict_proba(X_pending)[:, 1]
        pending_preds = model.predict(X_pending)

        pending_df['Target_Line'] = 4.5
        pending_df['Predicted_Runs_1to5'] = pending_probs * 3 + 3.5
        pending_df['Predicted_Over_4_5'] = pd.Series(pending_preds).map({1: 'Over', 0: 'Under'})
        pending_df['Actual_Runs_1to5'] = "Pending"
        pending_df['Actual_Over_4_5'] = "Pending"

        pending_df = pending_df[['Game Date', 'Away Team', 'Home Team', 'Target_Line', 'Predicted_Runs_1to5', 'Predicted_Over_4_5', 'Actual_Runs_1to5', 'Actual_Over_4_5']]

    else:
        pending_df = pd.DataFrame(columns=['Game Date', 'Away Team', 'Home Team', 'Target_Line', 'Predicted_Runs_1to5', 'Predicted_Over_4_5', 'Actual_Runs_1to5', 'Actual_Over_4_5'])

    # Played games processing (if not already done above)
    played_df['Target_Line'] = 4.5
    X_played = pd.get_dummies(played_df[['Away Team', 'Home Team']])
    X_played = X_played.reindex(columns=X.columns, fill_value=0)
    played_probs = model.predict_proba(X_played)[:, 1]
    played_preds = model.predict(X_played)

    played_df['Predicted_Runs_1to5'] = played_probs * 3 + 3.5
    played_df['Predicted_Over_4_5'] = pd.Series(played_preds).map({1: 'Over', 0: 'Under'})
    played_df['Actual_Runs_1to5'] = played_df['Total_1to5_Runs']
    played_df['Actual_Over_4_5'] = played_df['Over_4_5'].map({1: 'Over', 0: 'Under'})

    played_df = played_df[['Game Date', 'Away Team', 'Home Team', 'Target_Line', 'Predicted_Runs_1to5', 'Predicted_Over_4_5', 'Actual_Runs_1to5', 'Actual_Over_4_5']]

    # Combine played + pending
    combined_df = pd.concat([played_df, pending_df], ignore_index=True)
    combined_df.sort_values(by=["Game Date", "Home Team"], inplace=True)

    # Save final file
    combined_output_file = "data/mlb_boxscores_1to5_predictions_full.csv"
    combined_df.to_csv(combined_output_file, index=False)

    print(f"\n✅ Final full historical + pending predictions saved to {combined_output_file}")
else:
    print("🚫 played_df or future_df not found. Please load both datasets.")



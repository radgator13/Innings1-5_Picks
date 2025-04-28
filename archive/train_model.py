# Train 1-5 Innings Over/Under Model (Random Forest Only)
# -------------------------------------------------------

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os

# 1. Load the full predictions file
full_df = pd.read_csv('data/mlb_boxscores_1to5_predictions_full.csv')

# 2. Filter only completed games (drop "Pending" rows)
played_df = full_df[full_df['Actual_Runs_1to5'] != "Pending"].copy()

print(f"✅ Played games available for training: {len(played_df)} rows")

# 3. Prepare features
# Feature set: Away Team, Home Team (one-hot encoded)
X = pd.get_dummies(played_df[['Away Team', 'Home Team']])
y = played_df['Actual_Over_4_5'].map({'Over': 1, 'Under': 0})

# 4. Split data into training/testing sets
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 5. Train Random Forest model
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

# 6. Evaluate model
y_pred = rf_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
print(f"\n🎯 Backtest Accuracy: {accuracy:.3f}")
print("\n📋 Classification Report:")
print(classification_report(y_test, y_pred))

print("\n🧩 Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# 7. Save trained Random Forest model
os.makedirs("models", exist_ok=True)
joblib.dump((rf_model, X.columns.tolist()), "models/innings1to5_rf_model.pkl")

print("\n✅ Random Forest model saved to models/innings1to5_rf_model.pkl")

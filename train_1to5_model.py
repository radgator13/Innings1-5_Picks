import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# === Load CSV ===
df = pd.read_csv("data/mlb_boxscores_full.csv")

# === Normalize team names ===
df['Away Team'] = df['Away Team'].str.strip().str.lower()
df['Home Team'] = df['Home Team'].str.strip().str.lower()

# === Only keep rows that are fully scored (not Pending) ===
inning_cols = [f"Away {i}th" for i in range(1, 6)] + [f"Home {i}th" for i in range(1, 6)]
df_clean = df.copy()
for col in inning_cols:
    df_clean[col] = df_clean[col].replace("Pending", pd.NA)

df_clean = df_clean.dropna(subset=inning_cols)
for col in inning_cols:
    df_clean[col] = df_clean[col].astype(int)

# === Generate outcome column ===
df_clean['Total_1to5_Runs'] = df_clean[[f"Away {i}th" for i in range(1, 6)]].sum(axis=1) + \
                              df_clean[[f"Home {i}th" for i in range(1, 6)]].sum(axis=1)
df_clean['Outcome'] = df_clean['Total_1to5_Runs'].apply(lambda x: "Over" if x > 4.5 else "Under")

# === Extract features ===
df_clean['Game Date'] = pd.to_datetime(df_clean['Game Date'])
df_clean['DayOfWeek'] = df_clean['Game Date'].dt.dayofweek

def extract_win_pct(record):
    try:
        w, l = map(int, str(record).split("-"))
        return w / (w + l) if (w + l) > 0 else 0.5
    except:
        return 0.5

df_clean['HomeWinPct'] = df_clean['Home Record'].apply(extract_win_pct)
df_clean['AwayWinPct'] = df_clean['Away Record'].apply(extract_win_pct)

# === Build model input ===
categorical = pd.get_dummies(df_clean[['Away Team', 'Home Team', 'DayOfWeek']])
numerical = df_clean[['HomeWinPct', 'AwayWinPct']]
X = pd.concat([categorical, numerical], axis=1)
y = df_clean['Outcome']

# === Train/test split ===
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# === Train model ===
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# === Evaluate ===
print("\n📊 Classification Report:\n")
print(classification_report(y_test, model.predict(X_test)))

# === Save model + feature names ===
joblib.dump((model, X.columns.tolist()), "models/innings1to5_rf_model.pkl")
print("\n✅ Model saved to models/innings1to5_rf_model.pkl")

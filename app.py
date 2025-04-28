# app.py
# -------------------------------------------------------
import streamlit as st
import pandas as pd

# Make app full screen width
st.set_page_config(page_title="MLB 1-5 Inning Dashboard", layout="wide")

# Load full model predictions
df = pd.read_csv('data/mlb_boxscores_1to5_model_full_predictions.csv')
df['Game Date'] = pd.to_datetime(df['Game Date'])  # Ensure dates are parsed properly

st.title("⚾ MLB 1-5 Inning Over/Under Model Dashboard")

# Create a Confidence Score (🔥 Fireballs) based on prediction probability
def assign_confidence(prob, prediction):
    if prediction == "Over":
        confidence = prob
    else:
        confidence = 1 - prob
    if confidence >= 0.90:
        return "🔥🔥🔥🔥🔥"
    elif confidence >= 0.80:
        return "🔥🔥🔥🔥"
    elif confidence >= 0.70:
        return "🔥🔥🔥"
    elif confidence >= 0.60:
        return "🔥🔥"
    else:
        return "🔥"

# Add confidence column
df['Confidence'] = df.apply(
    lambda row: assign_confidence(row['Predicted_Runs_1to5'] / 3 + 0.5, row['Predicted_Over_4_5']),
    axis=1
)

# Add Correctness column
df['Correct'] = df.apply(
    lambda row: "✅" if row['Predicted_Over_4_5'] == row['Actual_Over_4_5'] and row['Actual_Over_4_5'] != "Pending" else ("❌" if row['Actual_Over_4_5'] != "Pending" else ""),
    axis=1
)

# Calendar date selector at top
selected_date = st.date_input("Select a date to view games:", value=pd.to_datetime("today"))

# Split into played and pending games
played_df = df[df['Actual_Runs_1to5'] != "Pending"]
pending_df = df[df['Actual_Runs_1to5'] == "Pending"]

# Filter by selected date
played_today = played_df[played_df['Game Date'] == pd.to_datetime(selected_date)]
pending_today = pending_df[pending_df['Game Date'] == pd.to_datetime(selected_date)]

# Section: Played Games for Selected Date
st.subheader(f"📋 Played Games on {selected_date.strftime('%Y-%m-%d')}")
if not played_today.empty:
    st.dataframe(
        played_today,
        use_container_width=True
    )
else:
    st.write("🚫 No played games for this date.")

# Section: Pending Games for Selected Date
st.subheader(f"🔮 Pending Games on {selected_date.strftime('%Y-%m-%d')}")
if not pending_today.empty:
    st.dataframe(
        pending_today,
        use_container_width=True
    )
else:
    st.write("🚫 No pending games for this date.")

# --------------------------
# 📋 Model Summaries (At Bottom)
# --------------------------

st.header("📊 Model Summaries")

# Calculate Daily Summary
daily_total = len(played_today)
daily_correct = (played_today['Predicted_Over_4_5'] == played_today['Actual_Over_4_5']).sum()
daily_accuracy = (daily_correct / daily_total) if daily_total > 0 else 0

# Calculate Rolling Total Summary
total_total = len(played_df)
total_correct = (played_df['Predicted_Over_4_5'] == played_df['Actual_Over_4_5']).sum()
total_accuracy = (total_correct / total_total) if total_total > 0 else 0

# Display Daily Summary
st.subheader(f"📅 Daily Summary: {selected_date.strftime('%Y-%m-%d')}")
st.metric(label="Games Predicted Today", value=daily_total)
st.metric(label="Wins-Losses Today", value=f"{daily_correct}-{daily_total - daily_correct}")
st.metric(label="Accuracy Today", value=f"{daily_accuracy:.2%}")

# Display Total Summary
st.subheader("📈 Rolling Total Summary")
st.metric(label="Games Predicted Total", value=total_total)
st.metric(label="Wins-Losses Total", value=f"{total_correct}-{total_total - total_correct}")
st.metric(label="Overall Model Accuracy", value=f"{total_accuracy:.2%}")

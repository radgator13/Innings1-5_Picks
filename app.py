# app.py
# -------------------------------------------------------
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Make app full screen width
st.set_page_config(page_title="MLB 1-5 Inning Dashboard", layout="wide")

# Load full model predictions
df = pd.read_csv('data/mlb_boxscores_1to5_model_full_predictions.csv')
df['Game Date'] = pd.to_datetime(df['Game Date'])  # Ensure dates are parsed properly

st.title("⚾ MLB 1-5 Inning Over/Under Model Dashboard")

# 🔥 Smarter Fireball Confidence Score
def assign_smarter_confidence(row):
    gap = row['Predicted_Runs_1to5'] - row['Target_Line']
    
    if row['Predicted_Over_4_5'] == "Over":
        if gap >= 1.5:
            return "🔥🔥🔥🔥🔥"
        elif gap >= 1.0:
            return "🔥🔥🔥🔥"
        elif gap >= 0.5:
            return "🔥🔥🔥"
        elif gap >= 0.25:
            return "🔥🔥"
        else:
            return "🔥"
    elif row['Predicted_Over_4_5'] == "Under":
        if gap <= -1.5:
            return "🔥🔥🔥🔥🔥"
        elif gap <= -1.0:
            return "🔥🔥🔥🔥"
        elif gap <= -0.5:
            return "🔥🔥🔥"
        elif gap <= -0.25:
            return "🔥🔥"
        else:
            return "🔥"
    else:
        return "🔥"


# Add confidence column
df['Confidence'] = df.apply(assign_smarter_confidence, axis=1)

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

# Section: Played Games
st.subheader(f"📋 Played Games on {selected_date.strftime('%Y-%m-%d')}")
if not played_today.empty:
    st.dataframe(played_today, use_container_width=True)
else:
    st.write("🚫 No played games for this date.")

# Section: Pending Games
st.subheader(f"🔮 Pending Games on {selected_date.strftime('%Y-%m-%d')}")
if not pending_today.empty:
    st.dataframe(pending_today, use_container_width=True)
else:
    st.write("🚫 No pending games for this date.")

# --------------------------
# 📊 Model Summaries (Daily + Rolling)
# --------------------------
st.header("📊 Model Summaries")

# Calculate Daily Summary
daily_total = len(played_today)
daily_correct = (played_today['Predicted_Over_4_5'] == played_today['Actual_Over_4_5']).sum()
daily_accuracy = (daily_correct / daily_total) if daily_total > 0 else 0

# Calculate Rolling Total Summary up to selected date only
rolling_df = played_df[played_df['Game Date'] <= pd.to_datetime(selected_date)]
rolling_total = len(rolling_df)
rolling_correct = (rolling_df['Predicted_Over_4_5'] == rolling_df['Actual_Over_4_5']).sum()
rolling_accuracy = (rolling_correct / rolling_total) if rolling_total > 0 else 0

# 🔥 Show Daily and Rolling side-by-side
col1, col2 = st.columns(2)

with col1:
    st.subheader(f"📅 Daily Summary: {selected_date.strftime('%Y-%m-%d')}")
    st.metric(label="Games Predicted Today", value=daily_total)
    st.metric(label="Wins-Losses Today", value=f"{daily_correct}-{daily_total - daily_correct}")
    st.metric(label="Accuracy Today", value=f"{daily_accuracy:.2%}")

with col2:
    st.subheader("📈 Rolling Total Summary")
    st.metric(label="Games Predicted Total", value=rolling_total)
    st.metric(label="Wins-Losses Total", value=f"{rolling_correct}-{rolling_total - rolling_correct}")
    st.metric(label="Overall Model Accuracy", value=f"{rolling_accuracy:.2%}")

# --------------------------
# 📈 Daily Accuracy Trend Chart
# --------------------------

st.subheader("📈 Daily Model Accuracy Trend")

# Only use played games
daily_summary = played_df.groupby('Game Date').apply(
    lambda g: pd.Series({
        'Total Games': len(g),
        'Correct Games': (g['Predicted_Over_4_5'] == g['Actual_Over_4_5']).sum()
    })
).reset_index()

daily_summary['Accuracy'] = (daily_summary['Correct Games'] / daily_summary['Total Games']) * 100

# --------------------------
# 🔥 Fireball Confidence Summaries
# --------------------------
st.header("🔥 Fireball Confidence Model Summaries")

# Filter fireball games (🔥🔥🔥 and above)
strong_confidence = ["🔥🔥🔥", "🔥🔥🔥🔥", "🔥🔥🔥🔥🔥"]

# Daily Fireball Summary
daily_fireballs = played_today[played_today['Confidence'].isin(strong_confidence)]

daily_fireball_total = len(daily_fireballs)
daily_fireball_correct = (daily_fireballs['Predicted_Over_4_5'] == daily_fireballs['Actual_Over_4_5']).sum()
daily_fireball_accuracy = (daily_fireball_correct / daily_fireball_total) if daily_fireball_total > 0 else 0

# Rolling Fireball Summary
rolling_fireballs = rolling_df[rolling_df['Confidence'].isin(strong_confidence)]

rolling_fireball_total = len(rolling_fireballs)
rolling_fireball_correct = (rolling_fireballs['Predicted_Over_4_5'] == rolling_fireballs['Actual_Over_4_5']).sum()
rolling_fireball_accuracy = (rolling_fireball_correct / rolling_fireball_total) if rolling_fireball_total > 0 else 0

# 🔥 Show Fireball Daily and Rolling side-by-side
col3, col4 = st.columns(2)

with col3:
    st.subheader(f"📅 Daily Fireball Summary: {selected_date.strftime('%Y-%m-%d')}")
    st.metric(label="Strong Picks Today (🔥🔥🔥 and above)", value=daily_fireball_total)
    st.metric(label="Wins-Losses (Fireballs Today)", value=f"{daily_fireball_correct}-{daily_fireball_total - daily_fireball_correct}")
    st.metric(label="Fireball Accuracy Today", value=f"{daily_fireball_accuracy:.2%}")

with col4:
    st.subheader("📈 Rolling Fireball Summary")
    st.metric(label="Strong Picks Total (🔥🔥🔥 and above)", value=rolling_fireball_total)
    st.metric(label="Wins-Losses (Fireballs Overall)", value=f"{rolling_fireball_correct}-{rolling_fireball_total - rolling_fireball_correct}")
    st.metric(label="Fireball Overall Accuracy", value=f"{rolling_fireball_accuracy:.2%}")


# Explain fireball strength key
st.caption("🗝️ **Fireball Strength Key:**")
st.markdown("""
- 🔥🔥🔥🔥🔥 : **Very Strong Confidence Pick** (Gap ≥ 1.5 runs)
- 🔥🔥🔥🔥 : **Strong Confidence Pick** (Gap ≥ 1.0 runs)
- 🔥🔥🔥 : **Moderate Confidence Pick** (Gap ≥ 0.5 runs)
- 🔥🔥 : Slightly better
- 🔥 : Weak (Close to betting line)

**Strong Picks include 🔥🔥🔥, 🔥🔥🔥🔥, 🔥🔥🔥🔥🔥 confidence bets.**
""")


# 📊 Daily Model Accuracy (Mini-Bar Chart)
st.subheader("📊 Daily Model Accuracy (Mini-Bar Chart)")

# Only use played games
daily_summary = played_df.groupby('Game Date').apply(
    lambda g: pd.Series({
        'Total Games': len(g),
        'Correct Games': (g['Predicted_Over_4_5'] == g['Actual_Over_4_5']).sum()
    })
).reset_index()

daily_summary['Accuracy'] = (daily_summary['Correct Games'] / daily_summary['Total Games']) * 100

# 📈 Plotting clean Mini-Bar Chart
fig, ax = plt.subplots(figsize=(8, 3))  # Smaller and cleaner
ax.bar(daily_summary['Game Date'], daily_summary['Accuracy'], color='#00BFFF', width=0.6)

ax.axhline(50, color='red', linestyle='--', linewidth=1, label='50% Baseline')

ax.set_title('Daily Accuracy (%)', fontsize=14, weight='bold')
ax.set_xlabel('Game Date', fontsize=10)
ax.set_ylabel('Accuracy (%)', fontsize=10)

ax.set_ylim(0, 100)
ax.grid(True, linestyle='--', alpha=0.5)
ax.tick_params(axis='both', labelsize=8)
ax.legend(fontsize=8)

# 📅 Rotate x-axis labels for clarity
plt.xticks(rotation=45, ha='right')

st.pyplot(fig)



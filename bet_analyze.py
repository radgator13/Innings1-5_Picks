import pandas as pd
import os

# 📂 Paths
bets_log_path = "data/my_bets_log.csv"
analysis_output_path = "data/bets_analysis.txt"

# ✅ Load your full bet log
bets = pd.read_csv(bets_log_path)

# ✅ Ensure Risk and Win are numbers
bets['Risk'] = pd.to_numeric(bets['Risk'], errors='coerce')
bets['Win'] = pd.to_numeric(bets['Win'], errors='coerce')

# ✅ Create total returned for each bet
bets['Total Returned'] = bets.apply(
    lambda row: row['Risk'] + row['Win'] if row['Result'] == 'Win' else 0,
    axis=1
)

# ✅ Create net outcome per bet
bets['Net Profit'] = bets['Total Returned'] - bets['Risk']

# ✅ Group analysis by Sport
sports = bets['Sport'].unique()

# ✅ Start building output text
output = []
output.append("📊 FULL SPORTS BETTING ANALYSIS")
output.append("================================")

for sport in sports:
    sport_name = str(sport) if pd.notnull(sport) else "Unknown"
    subset = bets[bets['Sport'] == sport]
    
    total_bets = len(subset)
    total_wins = (subset['Result'] == 'Win').sum()
    total_losses = (subset['Result'] == 'Lose').sum()
    total_risked = subset['Risk'].sum()
    total_returned = subset['Total Returned'].sum()
    net_profit = total_returned - total_risked
    win_rate = (total_wins / total_bets) * 100 if total_bets > 0 else 0
    roi = (net_profit / total_risked) * 100 if total_risked > 0 else 0

    output.append(f"\n🏈🏀⚾ SPORT: {sport_name.upper()}")
    output.append("--------------------------------")
    output.append(f"Total Bets: {total_bets}")
    output.append(f"Wins: {total_wins}")
    output.append(f"Losses: {total_losses}")
    output.append(f"Win Rate: {win_rate:.2f}%")
    output.append(f"Total Risked: ${total_risked:.2f}")
    output.append(f"Total Returned: ${total_returned:.2f}")
    output.append(f"Net Profit/Loss: ${net_profit:.2f}")
    output.append(f"ROI: {roi:.2f}%")

# ✅ Also print TOTAL across all sports
total_bets = len(bets)
total_wins = (bets['Result'] == 'Win').sum()
total_losses = (bets['Result'] == 'Lose').sum()
total_risked = bets['Risk'].sum()
total_returned = bets['Total Returned'].sum()
net_profit = total_returned - total_risked
win_rate = (total_wins / total_bets) * 100 if total_bets > 0 else 0
roi = (net_profit / total_risked) * 100 if total_risked > 0 else 0

output.append("\n📈 TOTAL ACROSS ALL SPORTS")
output.append("--------------------------------")
output.append(f"Total Bets: {total_bets}")
output.append(f"Wins: {total_wins}")
output.append(f"Losses: {total_losses}")
output.append(f"Win Rate: {win_rate:.2f}%")
output.append(f"Total Risked: ${total_risked:.2f}")
output.append(f"Total Returned: ${total_returned:.2f}")
output.append(f"Net Profit/Loss: ${net_profit:.2f}")
output.append(f"ROI: {roi:.2f}%")

# ✅ Save output to a new file
os.makedirs("data", exist_ok=True)
with open(analysis_output_path, "w", encoding="utf-8") as f:
    for line in output:
        f.write(line + "\n")

print(f"✅ Analysis complete! Results saved to '{analysis_output_path}'")


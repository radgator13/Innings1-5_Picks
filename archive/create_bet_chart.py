import pandas as pd
import matplotlib.pyplot as plt
import os

# Load your bets log
bets_log_path = "data/my_bets_log.csv"
if not os.path.exists(bets_log_path):
    print("❌ No bets file found at 'data/my_bets_log.csv'.")
    exit()

bets = pd.read_csv(bets_log_path)

# Fix types
bets['Risk'] = pd.to_numeric(bets['Risk'], errors='coerce')
bets['Win'] = pd.to_numeric(bets['Win'], errors='coerce')

# Calculate total returned
bets['Total Returned'] = bets.apply(
    lambda row: row['Risk'] + row['Win'] if row['Result'] == 'Win' else 0,
    axis=1
)

# Categorize Bet Types
def categorize_bet(bet):
    if 'Handicap' in bet:
        return 'Handicap'
    elif 'Over' in bet or 'Under' in bet:
        return 'Total'
    else:
        return 'Player Prop'

bets['Bet Type Category'] = bets['Bet Type'].apply(categorize_bet)

# Group correctly
grouped = bets.groupby('Bet Type Category').agg({
    'Risk': 'sum',
    'Total Returned': 'sum'
}).reset_index()

# Calculate Net Profit
grouped['Net Profit'] = grouped['Total Returned'] - grouped['Risk']

# Plot correct chart
plt.figure(figsize=(10,6))
colors = {'Handicap': '#4CAF50', 'Total': '#2196F3', 'Player Prop': '#FFC107'}
plt.bar(grouped['Bet Type Category'], grouped['Net Profit'], color=[colors.get(bt, '#AAAAAA') for bt in grouped['Bet Type Category']])
plt.title('Net Profit by Bet Type', fontsize=16)
plt.xlabel('Bet Type', fontsize=14)
plt.ylabel('Net Profit ($)', fontsize=14)
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.tight_layout()
plt.show()

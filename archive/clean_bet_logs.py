from email.contentmanager import raw_data_manager
import pandas as pd
import re
import os

raw_bets = """
Bet Ticket: #271651415
Placed: 04/27/2025
Straight Bet - Win
Win
Over 4.5/Innings 1 to 5 - total/Miami Marlins vs. Los Angeles Dodgers (Odds: -119) -WIN
(Baseball)
Game Date: Apr 28 - 22:10 PM
Risk: $5.00
Win: $4.20
Bet Ticket: #271651414
Placed: 04/27/2025
Straight Bet - LOSE
LOSE
Under 4/Innings 1 to 5 - total/Detroit Tigers vs. Houston Astros (Odds: +102) -LOSE
(Baseball)
Game Date: Apr 28 - 20:10 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271651412
Placed: 04/27/2025
Straight Bet - Win
Win
Under 5.5/Innings 1 to 5 - total/Athletics vs. Texas Rangers (Odds: -125) -WIN
(Baseball)
Game Date: Apr 28 - 20:05 PM
Risk: $8.76
Win: $7.01
Bet Ticket: #271651411
Placed: 04/27/2025
Straight Bet - Win
Win
Under 5/Innings 1 to 5 - total/St. Louis Cardinals vs. Cincinnati Reds (Odds: -120) -WIN
(Baseball)
Game Date: Apr 28 - 18:40 PM
Risk: $5.00
Win: $4.17
Bet Ticket: #271651410
Placed: 04/27/2025
Straight Bet - LOSE
LOSE
Over 5.5/Innings 1 to 5 - total/New York Yankees vs. Baltimore Orioles (Odds: -105) -LOSE
(Baseball)
Game Date: Apr 28 - 18:35 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271651409
Placed: 04/27/2025
Straight Bet - Win
Win
Over 4.5/Innings 1 to 5 - total/Minnesota Twins vs. Cleveland Guardians (Odds: -107) -WIN
(Baseball)
Game Date: Apr 28 - 18:10 PM
Risk: $5.00
Win: $4.67
"""

# Process each bet block
bet_blocks = [block.strip() for block in raw_bets.split("Bet Ticket:") if block.strip()]

bet_data = []

for block in bet_blocks:
    try:
        placed = re.search(r"Placed: (.*?)\n", block).group(1)
        game = re.search(r"Game Date: (.*?)\n", block).group(1)
        match = re.search(r"total/(.*?)(\(Odds: .*\))", block) or \
                re.search(r"Handicap .*?\)/(.*?)(\(Odds: .*\))", block) or \
                re.search(r"Batter hits.*?/(.*?)(\(Odds: .*\))", block)

        if match:
            teams = match.group(1).strip()
            if " vs. " in teams:
                away_team, home_team = teams.split(" vs. ")
            else:
                away_team, home_team = teams, ""
        else:
            away_team, home_team = "", ""

        odds = re.search(r"Odds: ([+-]?\d+)", block).group(1)
        risk = re.search(r"Risk: \$([\d\.]+)", block).group(1)
        win_amt = re.search(r"Win: \$([\d\.]+)", block).group(1)

        result = "Win" if "Win\nWin" in block else "Lose"

        if "Handicap" in block:
            bet_type = "Handicap"
        elif "total" in block.lower():
            bet_type = "Total"
        elif "Batter hits" in block:
            bet_type = "Player Prop"
        else:
            bet_type = "Unknown"

        bet_data.append({
            "Date Placed": placed,
            "Game Date": game,
            "Away Team": away_team.strip(),
            "Home Team": home_team.strip(),
            "Bet Type": bet_type,
            "Odds": int(odds),
            "Risk": float(risk),
            "Result": result,
            "Win": float(win_amt)
        })

    except Exception as e:
        print(f"⚠️ Error processing a bet block: {e}")
        continue

# Build new bets DataFrame
new_df = pd.DataFrame(bet_data)

# Load existing CSV if exists
csv_path = "data/my_bets_log.csv"
os.makedirs("data", exist_ok=True)

if os.path.exists(csv_path):
    existing_df = pd.read_csv(csv_path)
    combined_df = pd.concat([existing_df, new_df], ignore_index=True)
else:
    combined_df = new_df

# ✅ Remove duplicates
combined_df = combined_df.drop_duplicates(
    subset=["Date Placed", "Game Date", "Away Team", "Home Team", "Bet Type", "Odds", "Risk"],
    keep='first'
).reset_index(drop=True)

# Save back to CSV
combined_df.to_csv(csv_path, index=False)

print(f"✅ Bet log CSV updated! Total unique bets now: {len(combined_df)}")

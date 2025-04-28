from email.contentmanager import raw_data_manager
import pandas as pd
import re
import os

raw_bets = """
Bet Ticket: #271184649
Placed: 04/21/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Toronto Blue Jays vs. Houston Astros (Odds: -134) -WIN
(Baseball)
Game Date: Apr 21 - 20:10 PM
Risk: $5.00
Win: $3.73
Bet Ticket: #271184648
Placed: 04/21/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/San Diego Padres vs. Detroit Tigers (Odds: -108) -LOSE
(Baseball)
Game Date: Apr 21 - 18:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271184647
Placed: 04/21/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Milwaukee Brewers vs. San Francisco Giants (Odds: -125) -WIN
(Baseball)
Game Date: Apr 21 - 21:45 PM
Risk: $5.00
Win: $4.00
Bet Ticket: #271184646
Placed: 04/21/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/St. Louis Cardinals vs. Atlanta Braves (Odds: -115) -WIN
(Baseball)
Game Date: Apr 21 - 19:15 PM
Risk: $5.00
Win: $4.35
Bet Ticket: #271184645
Placed: 04/21/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/New York Yankees vs. Cleveland Guardians (Odds: -114) -WIN
(Baseball)
Game Date: Apr 21 - 18:10 PM
Risk: $5.00
Win: $4.39
Bet Ticket: #271184644
Placed: 04/21/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Philadelphia Phillies vs. New York Mets (Odds: -124) -LOSE
(Baseball)
Game Date: Apr 21 - 19:10 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271184643
Placed: 04/21/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Cincinnati Reds vs. Miami Marlins (Odds: -128) -WIN
(Baseball)
Game Date: Apr 21 - 18:40 PM
Risk: $5.54
Win: $4.33
Bet Ticket: #271224024
Placed: 04/22/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Pittsburgh Pirates vs. Los Angeles Angels (Odds: -112) -WIN
(Baseball)
Game Date: Apr 22 - 21:38 PM
Risk: $5.00
Win: $4.46
Bet Ticket: #271224023
Placed: 04/22/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Colorado Rockies vs. Kansas City Royals (Odds: -136) -WIN
(Baseball)
Game Date: Apr 22 - 19:40 PM
Risk: $5.00
Win: $3.68
Bet Ticket: #271224022
Placed: 04/22/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Toronto Blue Jays vs. Houston Astros (Odds: -137) -LOSE
(Baseball)
Game Date: Apr 22 - 20:10 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271224021
Placed: 04/22/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/New York Yankees vs. Cleveland Guardians (Odds: -128) -LOSE
(Baseball)
Game Date: Apr 22 - 18:10 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271224020
Placed: 04/22/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Cincinnati Reds vs. Miami Marlins (Odds: -125) -LOSE
(Baseball)
Game Date: Apr 22 - 18:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271224019
Placed: 04/22/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Milwaukee Brewers vs. San Francisco Giants (Odds: -144) -WIN
(Baseball)
Game Date: Apr 22 - 21:45 PM
Risk: $5.00
Win: $3.47
Bet Ticket: #271330826
Placed: 04/23/2025
Straight Bet - LOSE
LOSE
Over 0.5/1st inning - total/Los Angeles Dodgers vs. Chicago Cubs (Odds: -120) -LOSE
(Baseball)
Game Date: Apr 23 - 19:00 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271330825
Placed: 04/23/2025
Straight Bet - Win
Win
Over 0.5/1st inning - total/Seattle Mariners vs. Boston Red Sox (Odds: -136) -WIN
(Baseball)
Game Date: Apr 23 - 18:45 PM
Risk: $5.00
Win: $3.68
Bet Ticket: #271330824
Placed: 04/23/2025
Straight Bet - Win
Win
Over 0.5/1st inning - total/Baltimore Orioles vs. Washington Nationals (Odds: -126) -WIN
(Baseball)
Game Date: Apr 23 - 18:45 PM
Risk: $5.00
Win: $3.97
Bet Ticket: #271330823
Placed: 04/23/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Pittsburgh Pirates vs. Los Angeles Angels (Odds: -111) -WIN
(Baseball)
Game Date: Apr 23 - 21:38 PM
Risk: $5.00
Win: $4.50
Bet Ticket: #271330822
Placed: 04/23/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Tampa Bay Rays vs. Arizona Diamondbacks (Odds: -110) -LOSE
(Baseball)
Game Date: Apr 23 - 21:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271330821
Placed: 04/23/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Toronto Blue Jays vs. Houston Astros (Odds: -124) -WIN
(Baseball)
Game Date: Apr 23 - 19:40 PM
Risk: $5.00
Win: $4.03
Bet Ticket: #271330820
Placed: 04/23/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Milwaukee Brewers vs. San Francisco Giants (Odds: -170) -WIN
(Baseball)
Game Date: Apr 23 - 21:45 PM
Risk: $7.95
Win: $4.68
Bet Ticket: #271368914
Placed: 04/24/2025
Straight Bet - LOSE
LOSE
Over 0.5/1st inning - total/Baltimore Orioles vs. Washington Nationals (Odds: -127) -LOSE
(Baseball)
Game Date: Apr 24 - 18:45 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271368912
Placed: 04/24/2025
Straight Bet - LOSE
LOSE
Over 0.5/1st inning - total/Chicago White Sox vs. Minnesota Twins (Odds: -117) -LOSE
(Baseball)
Game Date: Apr 24 - 13:10 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271368911
Placed: 04/24/2025
Straight Bet - Win
Win
Over 0.5/1st inning - total/Tampa Bay Rays vs. Arizona Diamondbacks (Odds: +102) -WIN
(Baseball)
Game Date: Apr 24 - 21:40 PM
Risk: $5.00
Win: $5.10
Bet Ticket: #271368910
Placed: 04/24/2025
Straight Bet - Win
Win
Over 0.5/1st inning - total/Seattle Mariners vs. Boston Red Sox (Odds: +100) -WIN
(Baseball)
Game Date: Apr 24 - 13:35 PM
Risk: $5.00
Win: $5.00
Bet Ticket: #271368909
Placed: 04/24/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Texas Rangers vs. Athletics (Odds: -122) -WIN
(Baseball)
Game Date: Apr 24 - 22:05 PM
Risk: $5.00
Win: $4.10
Bet Ticket: #271368908
Placed: 04/24/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Milwaukee Brewers vs. San Francisco Giants (Odds: -133) -LOSE
(Baseball)
Game Date: Apr 24 - 15:45 PM
Risk: $8.81
Win: $0.00
Bet Ticket: #271368907
Placed: 04/24/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Pittsburgh Pirates vs. Los Angeles Angels (Odds: -123) -LOSE
(Baseball)
Game Date: Apr 24 - 21:29 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271437194
Placed: 04/25/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Milwaukee Brewers vs. St. Louis Cardinals (Odds: -122) -WIN
(Baseball)
Game Date: Apr 25 - 20:15 PM
Risk: $4.20
Win: $3.44
Bet Ticket: #271437193
Placed: 04/25/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Cincinnati Reds vs. Colorado Rockies (Odds: -120) -LOSE
(Baseball)
Game Date: Apr 25 - 20:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271437192
Placed: 04/25/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Los Angeles Angels vs. Minnesota Twins (Odds: -131) -LOSE
(Baseball)
Game Date: Apr 25 - 19:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271437191
Placed: 04/25/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Tampa Bay Rays vs. San Diego Padres (Odds: -156) -WIN
(Baseball)
Game Date: Apr 25 - 21:40 PM
Risk: $5.00
Win: $3.21
Bet Ticket: #271437190
Placed: 04/25/2025
Straight Bet - LOSE
LOSE
Over 0.5/1st inning - total/Toronto Blue Jays vs. New York Yankees (Odds: -143) -LOSE
(Baseball)
Game Date: Apr 25 - 19:05 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271437189
Placed: 04/25/2025
Straight Bet - LOSE
LOSE
Over 0.5/1st inning - total/Atlanta Braves vs. Arizona Diamondbacks (Odds: -106) -LOSE
(Baseball)
Game Date: Apr 25 - 21:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271437188
Placed: 04/25/2025
Straight Bet - LOSE
LOSE
Over 0.5/1st inning - total/Chicago White Sox vs. Athletics (Odds: -131) -LOSE
(Baseball)
Game Date: Apr 25 - 22:05 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271437187
Placed: 04/25/2025
Straight Bet - LOSE
LOSE
Over 0.5/1st inning - total/Miami Marlins vs. Seattle Mariners (Odds: -102) -LOSE
(Baseball)
Game Date: Apr 25 - 21:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271437186
Placed: 04/25/2025
Straight Bet - Win
Win
Over 0.5/1st inning - total/Boston Red Sox vs. Cleveland Guardians (Odds: -125) -WIN
(Baseball)
Game Date: Apr 25 - 19:10 PM
Risk: $5.00
Win: $4.00
Bet Ticket: #271437185
Placed: 04/25/2025
Straight Bet - LOSE
LOSE
Over 0.5/1st inning - total/Baltimore Orioles vs. Detroit Tigers (Odds: -116) -LOSE
(Baseball)
Game Date: Apr 25 - 18:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271512136
Placed: 04/26/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Milwaukee Brewers vs. St. Louis Cardinals (Odds: -134) -WIN
(Baseball)
Game Date: Apr 26 - 14:15 PM
Risk: $5.85
Win: $4.37
Bet Ticket: #271512135
Placed: 04/26/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Boston Red Sox vs. Cleveland Guardians (Odds: -123) -LOSE
(Baseball)
Game Date: Apr 26 - 13:10 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271512134
Placed: 04/26/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Chicago White Sox vs. Athletics (Odds: -111) -LOSE
(Baseball)
Game Date: Apr 26 - 16:05 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271512133
Placed: 04/26/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Baltimore Orioles vs. Detroit Tigers (Odds: -110) -WIN
(Baseball)
Game Date: Apr 26 - 13:10 PM
Risk: $5.00
Win: $4.55
Bet Ticket: #271512132
Placed: 04/26/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Cincinnati Reds vs. Colorado Rockies (Odds: +110) -WIN
(Baseball)
Game Date: Apr 26 - 15:10 PM
Risk: $5.00
Win: $5.50
Bet Ticket: #271512131
Placed: 04/26/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Miami Marlins vs. Seattle Mariners (Odds: -134) -LOSE
(Baseball)
Game Date: Apr 26 - 21:40 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271512130
Placed: 04/26/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Atlanta Braves vs. Arizona Diamondbacks (Odds: -104) -LOSE
(Baseball)
Game Date: Apr 26 - 20:10 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271512129
Placed: 04/26/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/New York Mets vs. Washington Nationals (Odds: -102) -WIN
(Baseball)
Game Date: Apr 26 - 16:30 PM
Risk: $5.00
Win: $4.90
Bet Ticket: #271596099
Placed: 04/27/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Boston Red Sox vs. Cleveland Guardians (Odds: -129) -WIN
(Baseball)
Game Date: Apr 27 - 13:40 PM
Risk: $4.17
Win: $3.23
Bet Ticket: #271596098
Placed: 04/27/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/New York Mets vs. Washington Nationals (Odds: -120) -LOSE
(Baseball)
Game Date: Apr 27 - 13:35 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271596097
Placed: 04/27/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Milwaukee Brewers vs. St. Louis Cardinals (Odds: -123) -LOSE
(Baseball)
Game Date: Apr 27 - 14:15 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271596096
Placed: 04/27/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Tampa Bay Rays vs. San Diego Padres (Odds: -125) -WIN
(Baseball)
Game Date: Apr 27 - 16:10 PM
Risk: $5.00
Win: $4.00
Bet Ticket: #271596095
Placed: 04/27/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Toronto Blue Jays vs. New York Yankees (Odds: -119) -LOSE
(Baseball)
Game Date: Apr 27 - 13:35 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271596094
Placed: 04/27/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Houston Astros vs. Kansas City Royals (Odds: -133) -WIN
(Baseball)
Game Date: Apr 27 - 14:10 PM
Risk: $5.00
Win: $3.76
Bet Ticket: #271596093
Placed: 04/27/2025
Straight Bet - LOSE
LOSE
Under 0.5/1st inning - total/Miami Marlins vs. Seattle Mariners (Odds: -136) -LOSE
(Baseball)
Game Date: Apr 27 - 16:10 PM
Risk: $5.00
Win: $0.00
Bet Ticket: #271596092
Placed: 04/27/2025
Straight Bet - Win
Win
Under 0.5/1st inning - total/Baltimore Orioles vs. Detroit Tigers (Odds: -139) -WIN
(Baseball)
Game Date: Apr 27 - 13:40 PM
Risk: $5.00
Win: $3.60
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

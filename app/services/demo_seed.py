import pandas as pd
import random
from datetime import datetime
from typing import List
from app.utils.csv_io import safe_write_csv

SPORTS = ["Football", "Basketball", "Tennis", "Ice Hockey", "Baseball"]

FOOTBALL_MATCHES = [
    "Liverpool vs Manchester City",
    "Real Madrid vs Barcelona",
    "Bayern Munich vs Borussia Dortmund",
    "PSG vs Marseille",
    "Arsenal vs Chelsea"
]

BASKETBALL_MATCHES = [
    "Lakers vs Warriors",
    "Celtics vs Heat",
    "Bucks vs 76ers",
    "Nuggets vs Suns",
    "Mavericks vs Clippers"
]

TENNIS_MATCHES = [
    "Djokovic vs Alcaraz",
    "Sinner vs Medvedev",
    "Rublev vs Tsitsipas",
    "Rune vs Fritz",
    "Shelton vs Tiafoe"
]

ICE_HOCKEY_MATCHES = [
    "Bruins vs Rangers",
    "Maple Leafs vs Canadiens",
    "Avalanche vs Golden Knights",
    "Lightning vs Panthers",
    "Oilers vs Flames"
]

BASEBALL_MATCHES = [
    "Yankees vs Red Sox",
    "Dodgers vs Giants",
    "Astros vs Rangers",
    "Braves vs Mets",
    "Cubs vs Cardinals"
]

MATCHES = {
    "Football": FOOTBALL_MATCHES,
    "Basketball": BASKETBALL_MATCHES,
    "Tennis": TENNIS_MATCHES,
    "Ice Hockey": ICE_HOCKEY_MATCHES,
    "Baseball": BASEBALL_MATCHES
}

BOOKMAKERS = [
    "Bet365", "William Hill", "Betway", "888sport", "Ladbrokes",
    "Coral", "Betfair", "Unibet", "Paddy Power", "Bwin"
]

MARKETS = {
    "Football": ["Match Winner", "Over/Under 2.5", "Both Teams to Score"],
    "Basketball": ["Match Winner", "Total Points Over/Under 220.5", "Spread -5.5"],
    "Tennis": ["Match Winner", "Set Betting 2-0", "Total Games Over/Under 22.5"],
    "Ice Hockey": ["Match Winner", "Total Goals Over/Under 5.5", "Puck Line -1.5"],
    "Baseball": ["Match Winner", "Total Runs Over/Under 8.5", "Run Line -1.5"]
}

def generate_odds_row(row_id: int, sport: str, match: str, market: str, bookmaker: str) -> dict:
    """Generate a single odds row with realistic odds."""
    timestamp = datetime.now().isoformat()
    
    # Generate realistic odds based on market type
    if "Match Winner" in market or "Winner" in market:
        if sport == "Tennis":
            # Two-way market
            home_odds = round(random.uniform(1.3, 3.5), 2)
            away_odds = round(1 / (1 - 1/home_odds) + random.uniform(-0.1, 0.1), 2)
            return [
                {
                    "id": f"odds_{row_id}_1",
                    "sport": sport,
                    "match": match,
                    "market": market,
                    "bookmaker": bookmaker,
                    "outcome": "Home",
                    "odds": home_odds,
                    "timestamp": timestamp
                },
                {
                    "id": f"odds_{row_id}_2",
                    "sport": sport,
                    "match": match,
                    "market": market,
                    "bookmaker": bookmaker,
                    "outcome": "Away",
                    "odds": away_odds,
                    "timestamp": timestamp
                }
            ]
        else:
            # Three-way market
            home_odds = round(random.uniform(1.5, 4.0), 2)
            draw_odds = round(random.uniform(3.0, 4.5), 2)
            away_odds = round(random.uniform(1.5, 4.0), 2)
            return [
                {
                    "id": f"odds_{row_id}_1",
                    "sport": sport,
                    "match": match,
                    "market": market,
                    "bookmaker": bookmaker,
                    "outcome": "Home",
                    "odds": home_odds,
                    "timestamp": timestamp
                },
                {
                    "id": f"odds_{row_id}_2",
                    "sport": sport,
                    "match": match,
                    "market": market,
                    "bookmaker": bookmaker,
                    "outcome": "Draw",
                    "odds": draw_odds,
                    "timestamp": timestamp
                },
                {
                    "id": f"odds_{row_id}_3",
                    "sport": sport,
                    "match": match,
                    "market": market,
                    "bookmaker": bookmaker,
                    "outcome": "Away",
                    "odds": away_odds,
                    "timestamp": timestamp
                }
            ]
    else:
        # Two-way markets (Over/Under, etc.)
        over_odds = round(random.uniform(1.7, 2.3), 2)
        under_odds = round(1 / (1 - 1/over_odds) + random.uniform(-0.1, 0.1), 2)
        return [
            {
                "id": f"odds_{row_id}_1",
                "sport": sport,
                "match": match,
                "market": market,
                "bookmaker": bookmaker,
                "outcome": "Over",
                "odds": over_odds,
                "timestamp": timestamp
            },
            {
                "id": f"odds_{row_id}_2",
                "sport": sport,
                "match": match,
                "market": market,
                "bookmaker": bookmaker,
                "outcome": "Under",
                "odds": under_odds,
                "timestamp": timestamp
            }
        ]

def generate_demo_data(num_odds: int = 500):
    """
    Generate demo data for odds and initialize empty files for other data.
    """
    odds_data = []
    row_counter = 0
    
    # Generate odds data
    for _ in range(num_odds):
        sport = random.choice(SPORTS)
        match = random.choice(MATCHES[sport])
        market = random.choice(MARKETS[sport])
        bookmaker = random.choice(BOOKMAKERS)
        
        rows = generate_odds_row(row_counter, sport, match, market, bookmaker)
        odds_data.extend(rows)
        row_counter += 1
    
    # Create odds DataFrame and save
    odds_df = pd.DataFrame(odds_data)
    safe_write_csv("odds.csv", odds_df)
    print(f"✓ Generated {len(odds_df)} odds rows")
    
    # Initialize empty arbitrage.csv
    arb_columns = ["id", "sport", "match", "market", "outcome1", "bookmaker1", "odds1",
                   "outcome2", "bookmaker2", "odds2", "outcome3", "bookmaker3", "odds3",
                   "arb_percentage", "profit_percentage", "timestamp"]
    arb_df = pd.DataFrame(columns=arb_columns)
    safe_write_csv("arbitrage.csv", arb_df)
    print("✓ Initialized arbitrage.csv")
    
    # Initialize empty bets.csv
    bets_columns = ["bet_id", "session_id", "arbitrage_id", "bookmaker", "outcome",
                    "stake", "odds", "expected_return", "expected_profit", "timestamp"]
    bets_df = pd.DataFrame(columns=bets_columns)
    safe_write_csv("bets.csv", bets_df)
    print("✓ Initialized bets.csv")
    
    # Initialize empty sessions.csv
    sessions_columns = ["session_id", "created_at", "total_bets", "total_stake", "total_expected_profit"]
    sessions_df = pd.DataFrame(columns=sessions_columns)
    safe_write_csv("sessions.csv", sessions_df)
    print("✓ Initialized sessions.csv")
    
    return {
        "odds_count": len(odds_df),
        "sports": SPORTS,
        "bookmakers": BOOKMAKERS
    }

if __name__ == "__main__":
    print("Generating demo data...")
    result = generate_demo_data()
    print(f"\n✓ Demo data generation complete!")
    print(f"  - {result['odds_count']} odds entries")
    print(f"  - {len(result['sports'])} sports")
    print(f"  - {len(result['bookmakers'])} bookmakers")
"""
Enhanced Demo Data Generator
Generates realistic odds with event_id linking and proper market structures
"""

import pandas as pd
import random
import uuid
from datetime import datetime, timedelta
from typing import List
from app.utils.csv_io import safe_write_csv

SPORTS = ["Football", "Basketball", "Tennis", "Ice Hockey", "Baseball"]

MATCHES = {
    "Football": [
        ("Liverpool", "Manchester City"),
        ("Real Madrid", "Barcelona"),
        ("Bayern Munich", "Borussia Dortmund"),
        ("PSG", "Marseille"),
        ("Arsenal", "Chelsea")
    ],
    "Basketball": [
        ("Lakers", "Warriors"),
        ("Celtics", "Heat"),
        ("Bucks", "76ers"),
        ("Nuggets", "Suns"),
        ("Mavericks", "Clippers")
    ],
    "Tennis": [
        ("Djokovic", "Alcaraz"),
        ("Sinner", "Medvedev"),
        ("Rublev", "Tsitsipas"),
        ("Rune", "Fritz"),
        ("Shelton", "Tiafoe")
    ],
    "Ice Hockey": [
        ("Bruins", "Rangers"),
        ("Maple Leafs", "Canadiens"),
        ("Avalanche", "Golden Knights"),
        ("Lightning", "Panthers"),
        ("Oilers", "Flames")
    ],
    "Baseball": [
        ("Yankees", "Red Sox"),
        ("Dodgers", "Giants"),
        ("Astros", "Rangers"),
        ("Braves", "Mets"),
        ("Cubs", "Cardinals")
    ]
}

BOOKMAKERS = [
    "Bet365", "William Hill", "Betway", "888sport", "Ladbrokes",
    "Coral", "Betfair", "Unibet", "Paddy Power", "Bwin"
]

MARKETS = {
    "Football": [
        ("Match Winner", None),
        ("Over/Under", "2.5"),
        ("Both Teams to Score", None),
        ("Spread", "1.5")
    ],
    "Basketball": [
        ("Match Winner", None),
        ("Total Points", "220.5"),
        ("Spread", "-5.5")
    ],
    "Tennis": [
        ("Match Winner", None),
        ("Set Betting", "2-0"),
        ("Total Games", "22.5")
    ],
    "Ice Hockey": [
        ("Match Winner", None),
        ("Total Goals", "5.5"),
        ("Puck Line", "-1.5")
    ],
    "Baseball": [
        ("Match Winner", None),
        ("Total Runs", "8.5"),
        ("Run Line", "-1.5")
    ]
}

def generate_event_odds(event_id: str, sport: str, home_team: str, away_team: str, 
                       market_type: str, market_params: str, bookmaker: str) -> List[dict]:
    """Generate realistic odds for an event with proper variance for detection"""
    timestamp = datetime.now().isoformat()
    match = f"{home_team} vs {away_team}"
    odds_list = []
    
    # Add slight variance to create arbitrage/EV opportunities
    variance = random.uniform(0.95, 1.08)  # Intentional variance for detection
    
    if market_type == "Match Winner":
        if sport == "Tennis":
            # Two-way market
            base_home = random.uniform(1.5, 2.8)
            home_odds = round(base_home * variance, 2)
            away_odds = round((1 / (1 - 1/home_odds)) * random.uniform(0.98, 1.02), 2)
            
            odds_list.extend([
                {
                    "odds_id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "sport": sport,
                    "match": match,
                    "market": market_type,
                    "market_params": market_params,
                    "bookmaker": bookmaker,
                    "outcome": home_team,
                    "odds": home_odds,
                    "timestamp": timestamp,
                    "is_active": True
                },
                {
                    "odds_id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "sport": sport,
                    "match": match,
                    "market": market_type,
                    "market_params": market_params,
                    "bookmaker": bookmaker,
                    "outcome": away_team,
                    "odds": away_odds,
                    "timestamp": timestamp,
                    "is_active": True
                }
            ])
        else:
            # Three-way market
            base_home = random.uniform(2.0, 3.5)
            home_odds = round(base_home * variance, 2)
            draw_odds = round(random.uniform(3.0, 4.2) * variance, 2)
            away_odds = round(random.uniform(2.0, 3.5) * variance, 2)
            
            odds_list.extend([
                {
                    "odds_id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "sport": sport,
                    "match": match,
                    "market": market_type,
                    "market_params": market_params,
                    "bookmaker": bookmaker,
                    "outcome": home_team,
                    "odds": home_odds,
                    "timestamp": timestamp,
                    "is_active": True
                },
                {
                    "odds_id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "sport": sport,
                    "match": match,
                    "market": market_type,
                    "market_params": market_params,
                    "bookmaker": bookmaker,
                    "outcome": "Draw",
                    "odds": draw_odds,
                    "timestamp": timestamp,
                    "is_active": True
                },
                {
                    "odds_id": str(uuid.uuid4()),
                    "event_id": event_id,
                    "sport": sport,
                    "match": match,
                    "market": market_type,
                    "market_params": market_params,
                    "bookmaker": bookmaker,
                    "outcome": away_team,
                    "odds": away_odds,
                    "timestamp": timestamp,
                    "is_active": True
                }
            ])
    
    elif "Over/Under" in market_type or "Total" in market_type:
        # Two-way market with line
        base_over = random.uniform(1.85, 2.1)
        over_odds = round(base_over * variance, 2)
        under_odds = round((1 / (1 - 1/over_odds)) * random.uniform(0.98, 1.02), 2)
        
        odds_list.extend([
            {
                "odds_id": str(uuid.uuid4()),
                "event_id": event_id,
                "sport": sport,
                "match": match,
                "market": market_type,
                "market_params": market_params,
                "bookmaker": bookmaker,
                "outcome": f"Over {market_params}",
                "odds": over_odds,
                "timestamp": timestamp,
                "is_active": True
            },
            {
                "odds_id": str(uuid.uuid4()),
                "event_id": event_id,
                "sport": sport,
                "match": match,
                "market": market_type,
                "market_params": market_params,
                "bookmaker": bookmaker,
                "outcome": f"Under {market_params}",
                "odds": under_odds,
                "timestamp": timestamp,
                "is_active": True
            }
        ])
    
    elif "Spread" in market_type or "Line" in market_type:
        # Spread market - create potential middles
        if random.random() > 0.7:  # 30% chance of middle-friendly lines
            line = float(market_params)
            adjusted_line = line + random.choice([-1, -0.5, 0.5, 1])  # Create middle opportunities
            market_params = str(adjusted_line)
        
        base_odds = random.uniform(1.85, 2.05)
        odds1 = round(base_odds * variance, 2)
        odds2 = round((1 / (1 - 1/odds1)) * random.uniform(0.98, 1.02), 2)
        
        odds_list.extend([
            {
                "odds_id": str(uuid.uuid4()),
                "event_id": event_id,
                "sport": sport,
                "match": match,
                "market": market_type,
                "market_params": market_params,
                "bookmaker": bookmaker,
                "outcome": f"{home_team} {market_params}",
                "odds": odds1,
                "timestamp": timestamp,
                "is_active": True
            },
            {
                "odds_id": str(uuid.uuid4()),
                "event_id": event_id,
                "sport": sport,
                "match": match,
                "market": market_type,
                "market_params": market_params,
                "bookmaker": bookmaker,
                "outcome": f"{away_team} +{abs(float(market_params))}",
                "odds": odds2,
                "timestamp": timestamp,
                "is_active": True
            }
        ])
    
    else:
        # Generic two-way market
        base_odds = random.uniform(1.8, 2.2)
        odds1 = round(base_odds * variance, 2)
        odds2 = round((1 / (1 - 1/odds1)) * random.uniform(0.98, 1.02), 2)
        
        odds_list.extend([
            {
                "odds_id": str(uuid.uuid4()),
                "event_id": event_id,
                "sport": sport,
                "match": match,
                "market": market_type,
                "market_params": market_params,
                "bookmaker": bookmaker,
                "outcome": "Yes",
                "odds": odds1,
                "timestamp": timestamp,
                "is_active": True
            },
            {
                "odds_id": str(uuid.uuid4()),
                "event_id": event_id,
                "sport": sport,
                "match": match,
                "market": market_type,
                "market_params": market_params,
                "bookmaker": bookmaker,
                "outcome": "No",
                "odds": odds2,
                "timestamp": timestamp,
                "is_active": True
            }
        ])
    
    return odds_list

def generate_demo_data(num_events_per_sport: int = 5):
    """
    Generate enhanced demo data with proper event linking
    """
    odds_data = []
    
    # Generate events and odds
    for sport in SPORTS:
        matches = MATCHES[sport][:num_events_per_sport]
        markets = MARKETS[sport]
        
        for home_team, away_team in matches:
            event_id = str(uuid.uuid4())
            
            # Generate odds for each market from multiple bookmakers
            for market_type, market_params in markets:
                # Each bookmaker offers odds for this market
                selected_bookmakers = random.sample(BOOKMAKERS, random.randint(5, 8))
                
                for bookmaker in selected_bookmakers:
                    event_odds = generate_event_odds(
                        event_id, sport, home_team, away_team,
                        market_type, market_params, bookmaker
                    )
                    odds_data.extend(event_odds)
    
    # Save odds
    odds_df = pd.DataFrame(odds_data)
    safe_write_csv("odds.csv", odds_df)
    print(f"✓ Generated {len(odds_df)} odds entries across {len(odds_df['event_id'].unique())} events")
    
    # Initialize empty opportunities CSV (unified)
    opportunities_columns = [
        "id", "type", "event_id", "sport", "match", "roi", "profit_percentage",
        "status", "timestamp", "expires_at", "details"
    ]
    opp_df = pd.DataFrame(columns=opportunities_columns)
    safe_write_csv("opportunities.csv", opp_df)
    print("✓ Initialized opportunities.csv")
    
    # Initialize empty bets.csv
    bets_columns = [
        "bet_id", "session_id", "opportunity_id", "opportunity_type",
        "bookmaker", "outcome", "stake", "odds", "expected_return",
        "expected_profit", "timestamp"
    ]
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
        "events_count": len(odds_df['event_id'].unique()),
        "sports": SPORTS,
        "bookmakers": BOOKMAKERS
    }

if __name__ == "__main__":
    print("Generating enhanced demo data...")
    result = generate_demo_data()
    print(f"\n✓ Demo data generation complete!")
    print(f"  - {result['odds_count']} odds entries")
    print(f"  - {result['events_count']} events")
    print(f"  - {len(result['sports'])} sports")
    print(f"  - {len(result['bookmakers'])} bookmakers")
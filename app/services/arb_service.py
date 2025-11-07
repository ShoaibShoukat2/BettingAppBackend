import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime
from app.utils.csv_io import safe_read_csv, safe_write_csv
import uuid

class ArbitrageService:
    """Service for computing and managing arbitrage opportunities."""
    
    @staticmethod
    def compute_arbitrage() -> int:
        """
        Compute arbitrage opportunities from odds.csv and write to arbitrage.csv.
        Returns the number of arbitrage opportunities found.
        """
        odds_df = safe_read_csv("odds.csv")
        
        if odds_df.empty:
            return 0
        
        arbitrage_opportunities = []
        timestamp = datetime.now().isoformat()
        
        # Group by sport, match, and market
        grouped = odds_df.groupby(['sport', 'match', 'market'])
        
        for (sport, match, market), group in grouped:
            # Get unique outcomes
            outcomes = group['outcome'].unique()
            
            if len(outcomes) == 2:
                # Two-way market (e.g., Tennis, Over/Under)
                arbs = ArbitrageService._find_two_way_arbs(group, sport, match, market, timestamp)
                arbitrage_opportunities.extend(arbs)
            elif len(outcomes) == 3:
                # Three-way market (e.g., Football 1X2)
                arbs = ArbitrageService._find_three_way_arbs(group, sport, match, market, timestamp)
                arbitrage_opportunities.extend(arbs)
        
        # Save to arbitrage.csv
        if arbitrage_opportunities:
            arb_df = pd.DataFrame(arbitrage_opportunities)
            safe_write_csv("arbitrage.csv", arb_df)
        
        return len(arbitrage_opportunities)
    
    @staticmethod
    def _find_two_way_arbs(group: pd.DataFrame, sport: str, match: str, market: str, timestamp: str) -> List[Dict]:
        """Find arbitrage opportunities in two-way markets."""
        arbs = []
        outcomes = group['outcome'].unique()
        
        if len(outcomes) != 2:
            return arbs
        
        outcome1, outcome2 = outcomes[0], outcomes[1]
        
        # Find best odds for each outcome
        odds1_df = group[group['outcome'] == outcome1]
        odds2_df = group[group['outcome'] == outcome2]
        
        if odds1_df.empty or odds2_df.empty:
            return arbs
        
        best_odds1 = odds1_df.loc[odds1_df['odds'].idxmax()]
        best_odds2 = odds2_df.loc[odds2_df['odds'].idxmax()]
        
        # Calculate arbitrage percentage
        arb_percentage = (1 / best_odds1['odds'] + 1 / best_odds2['odds']) * 100
        
        # If arb_percentage < 100, it's an arbitrage opportunity
        if arb_percentage < 100:
            profit_percentage = 100 - arb_percentage
            
            arbs.append({
                'id': str(uuid.uuid4()),
                'sport': sport,
                'match': match,
                'market': market,
                'outcome1': outcome1,
                'bookmaker1': best_odds1['bookmaker'],
                'odds1': best_odds1['odds'],
                'outcome2': outcome2,
                'bookmaker2': best_odds2['bookmaker'],
                'odds2': best_odds2['odds'],
                'outcome3': None,
                'bookmaker3': None,
                'odds3': None,
                'arb_percentage': round(arb_percentage, 2),
                'profit_percentage': round(profit_percentage, 2),
                'timestamp': timestamp
            })
        
        return arbs
    
    @staticmethod
    def _find_three_way_arbs(group: pd.DataFrame, sport: str, match: str, market: str, timestamp: str) -> List[Dict]:
        """Find arbitrage opportunities in three-way markets."""
        arbs = []
        outcomes = group['outcome'].unique()
        
        if len(outcomes) != 3:
            return arbs
        
        outcome1, outcome2, outcome3 = outcomes[0], outcomes[1], outcomes[2]
        
        # Find best odds for each outcome
        odds1_df = group[group['outcome'] == outcome1]
        odds2_df = group[group['outcome'] == outcome2]
        odds3_df = group[group['outcome'] == outcome3]
        
        if odds1_df.empty or odds2_df.empty or odds3_df.empty:
            return arbs
        
        best_odds1 = odds1_df.loc[odds1_df['odds'].idxmax()]
        best_odds2 = odds2_df.loc[odds2_df['odds'].idxmax()]
        best_odds3 = odds3_df.loc[odds3_df['odds'].idxmax()]
        
        # Calculate arbitrage percentage
        arb_percentage = (1 / best_odds1['odds'] + 1 / best_odds2['odds'] + 1 / best_odds3['odds']) * 100
        
        # If arb_percentage < 100, it's an arbitrage opportunity
        if arb_percentage < 100:
            profit_percentage = 100 - arb_percentage
            
            arbs.append({
                'id': str(uuid.uuid4()),
                'sport': sport,
                'match': match,
                'market': market,
                'outcome1': outcome1,
                'bookmaker1': best_odds1['bookmaker'],
                'odds1': best_odds1['odds'],
                'outcome2': outcome2,
                'bookmaker2': best_odds2['bookmaker'],
                'odds2': best_odds2['odds'],
                'outcome3': outcome3,
                'bookmaker3': best_odds3['bookmaker'],
                'odds3': best_odds3['odds'],
                'arb_percentage': round(arb_percentage, 2),
                'profit_percentage': round(profit_percentage, 2),
                'timestamp': timestamp
            })
        
        return arbs
    
    @staticmethod
    def get_arbitrage_feed(min_arb: float = 0.0, top_n: int = 100, sport: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get arbitrage opportunities from CSV with filters.
        """
        df = safe_read_csv("arbitrage.csv")
        
        if df.empty:
            return []
        
        # Apply filters
        df = df[df['profit_percentage'] >= min_arb]
        
        if sport:
            df = df[df['sport'].str.lower() == sport.lower()]
        
        # Sort by profit percentage (highest first)
        df = df.sort_values('profit_percentage', ascending=False)
        
        # Limit to top N
        df = df.head(top_n)
        
        return df.to_dict('records')
    
    @staticmethod
    def get_arbitrage_by_id(arb_id: str) -> Optional[Dict[str, Any]]:
        """Get specific arbitrage opportunity by ID."""
        df = safe_read_csv("arbitrage.csv")
        
        if df.empty:
            return None
        
        result = df[df['id'] == arb_id]
        
        if result.empty:
            return None
        
        return result.iloc[0].to_dict()
    
    @staticmethod
    def calculate_stakes(arb_id: str, total_stake: float) -> Optional[Dict[str, Any]]:
        """
        Calculate optimal stake distribution for an arbitrage opportunity.
        """
        arb = ArbitrageService.get_arbitrage_by_id(arb_id)
        
        if not arb:
            return None
        
        odds1 = arb['odds1']
        odds2 = arb['odds2']
        odds3 = arb.get('odds3')
        
        if odds3:
            # Three-way arbitrage
            total_prob = 1/odds1 + 1/odds2 + 1/odds3
            stake1 = total_stake * (1/odds1) / total_prob
            stake2 = total_stake * (1/odds2) / total_prob
            stake3 = total_stake * (1/odds3) / total_prob
            
            expected_return = stake1 * odds1  # Same for all outcomes in arbitrage
            expected_profit = expected_return - total_stake
            
            return {
                'stakes': {
                    arb['outcome1']: round(stake1, 2),
                    arb['outcome2']: round(stake2, 2),
                    arb['outcome3']: round(stake3, 2)
                },
                'bookmakers': {
                    arb['outcome1']: arb['bookmaker1'],
                    arb['outcome2']: arb['bookmaker2'],
                    arb['outcome3']: arb['bookmaker3']
                },
                'total_stake': round(total_stake, 2),
                'expected_return': round(expected_return, 2),
                'expected_profit': round(expected_profit, 2),
                'profit_percentage': arb['profit_percentage']
            }
        else:
            # Two-way arbitrage
            total_prob = 1/odds1 + 1/odds2
            stake1 = total_stake * (1/odds1) / total_prob
            stake2 = total_stake * (1/odds2) / total_prob
            
            expected_return = stake1 * odds1
            expected_profit = expected_return - total_stake
            
            return {
                'stakes': {
                    arb['outcome1']: round(stake1, 2),
                    arb['outcome2']: round(stake2, 2)
                },
                'bookmakers': {
                    arb['outcome1']: arb['bookmaker1'],
                    arb['outcome2']: arb['bookmaker2']
                },
                'total_stake': round(total_stake, 2),
                'expected_return': round(expected_return, 2),
                'expected_profit': round(expected_profit, 2),
                'profit_percentage': arb['profit_percentage']
            }
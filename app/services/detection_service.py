"""
Detection Service - Implements all opportunity detection strategies
- Arbitrage: Risk-free profit from odds discrepancies
- Middles: Overlapping line ranges for potential win-win scenarios
- EV: Positive expected value bets based on fair odds
- Lows: Low-hold markets with minimal bookmaker margin
"""

import pandas as pd
import uuid
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
from app.utils.csv_io import safe_read_csv

class DetectionService:
    """Unified service for detecting all opportunity types"""
    
    # Thresholds
    MIDDLE_MIN_GAP = 0.5  # Minimum gap for middle opportunities
    EV_MIN_EDGE = 2.0  # Minimum 2% edge for EV opportunities
    LOW_HOLD_MAX = 2.5  # Maximum 2.5% hold for low opportunities
    
    @staticmethod
    def detect_arbitrage(odds_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect arbitrage opportunities (surebets)
        Logic: Find combinations where (1/odds1 + 1/odds2 + 1/odds3) < 1
        """
        if odds_df.empty:
            return []
        
        opportunities = []
        timestamp = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(hours=2)).isoformat()
        
        # Group by event and market
        grouped = odds_df.groupby(['event_id', 'sport', 'match', 'market'])
        
        for (event_id, sport, match, market), group in grouped:
            outcomes = group['outcome'].unique()
            
            if len(outcomes) == 2:
                # Two-way arbitrage
                arbs = DetectionService._find_two_way_arb(
                    group, event_id, sport, match, market, timestamp, expires_at
                )
                opportunities.extend(arbs)
                
            elif len(outcomes) == 3:
                # Three-way arbitrage
                arbs = DetectionService._find_three_way_arb(
                    group, event_id, sport, match, market, timestamp, expires_at
                )
                opportunities.extend(arbs)
        
        return opportunities
    
    @staticmethod
    def _find_two_way_arb(group, event_id, sport, match, market, timestamp, expires_at):
        """Find 2-way arbitrage opportunities"""
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
        
        # Calculate arbitrage
        arb_percentage = (1 / best_odds1['odds'] + 1 / best_odds2['odds']) * 100
        
        if arb_percentage < 100:
            profit_percentage = 100 - arb_percentage
            roi = profit_percentage
            
            arbs.append({
                'id': str(uuid.uuid4()),
                'type': 'arbitrage',
                'event_id': event_id,
                'sport': sport,
                'match': match,
                'market': market,
                'outcome1': outcome1,
                'bookmaker1': best_odds1['bookmaker'],
                'odds1': float(best_odds1['odds']),
                'outcome2': outcome2,
                'bookmaker2': best_odds2['bookmaker'],
                'odds2': float(best_odds2['odds']),
                'outcome3': None,
                'bookmaker3': None,
                'odds3': None,
                'arb_percentage': round(arb_percentage, 2),
                'profit_percentage': round(profit_percentage, 2),
                'roi': round(roi, 2),
                'status': 'active',
                'timestamp': timestamp,
                'expires_at': expires_at
            })
        
        return arbs
    
    @staticmethod
    def _find_three_way_arb(group, event_id, sport, match, market, timestamp, expires_at):
        """Find 3-way arbitrage opportunities"""
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
        
        # Calculate arbitrage
        arb_percentage = (1/best_odds1['odds'] + 1/best_odds2['odds'] + 1/best_odds3['odds']) * 100
        
        if arb_percentage < 100:
            profit_percentage = 100 - arb_percentage
            roi = profit_percentage
            
            arbs.append({
                'id': str(uuid.uuid4()),
                'type': 'arbitrage',
                'event_id': event_id,
                'sport': sport,
                'match': match,
                'market': market,
                'outcome1': outcome1,
                'bookmaker1': best_odds1['bookmaker'],
                'odds1': float(best_odds1['odds']),
                'outcome2': outcome2,
                'bookmaker2': best_odds2['bookmaker'],
                'odds2': float(best_odds2['odds']),
                'outcome3': outcome3,
                'bookmaker3': best_odds3['bookmaker'],
                'odds3': float(best_odds3['odds']),
                'arb_percentage': round(arb_percentage, 2),
                'profit_percentage': round(profit_percentage, 2),
                'roi': round(roi, 2),
                'status': 'active',
                'timestamp': timestamp,
                'expires_at': expires_at
            })
        
        return arbs
    
    @staticmethod
    def detect_middles(odds_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect middle opportunities
        Logic: Find overlapping lines (e.g., +3.5 at one book, -2.5 at another)
        If result lands in middle, both bets win
        """
        if odds_df.empty:
            return []
        
        opportunities = []
        timestamp = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(hours=2)).isoformat()
        
        # Filter for spread/total markets with line parameters
        spread_markets = odds_df[odds_df['market'].str.contains('Spread|Total|Line', case=False, na=False)]
        
        grouped = spread_markets.groupby(['event_id', 'sport', 'match', 'market'])
        
        for (event_id, sport, match, market), group in grouped:
            middles = DetectionService._find_middle_in_group(
                group, event_id, sport, match, market, timestamp, expires_at
            )
            opportunities.extend(middles)
        
        return opportunities
    
    @staticmethod
    def _find_middle_in_group(group, event_id, sport, match, market, timestamp, expires_at):
        """Find middle opportunities in a market group"""
        middles = []
        
        # Extract lines from market_params or outcome names
        # Example: "Over 2.5" -> 2.5, "Spread +3.5" -> 3.5
        for i, row1 in group.iterrows():
            for j, row2 in group.iterrows():
                if i >= j or row1['bookmaker'] == row2['bookmaker']:
                    continue
                
                line1, line2 = DetectionService._extract_lines(row1, row2)
                
                if line1 is None or line2 is None:
                    continue
                
                # Check if lines create a middle
                gap = abs(line1 - line2)
                
                if DetectionService.MIDDLE_MIN_GAP <= gap <= 10:  # Reasonable middle range
                    # Calculate potential outcomes
                    min_line = min(line1, line2)
                    max_line = max(line1, line2)
                    
                    # Calculate worst case and best case
                    worst_case_loss = -((1/row1['odds'] + 1/row2['odds']) - 1) * 100
                    max_profit = min(row1['odds'] - 1, row2['odds'] - 1) * 100
                    
                    roi = (max_profit + worst_case_loss) / 2  # Average case
                    
                    middles.append({
                        'id': str(uuid.uuid4()),
                        'type': 'middle',
                        'event_id': event_id,
                        'sport': sport,
                        'match': match,
                        'market': market,
                        'line1': float(line1),
                        'bookmaker1': row1['bookmaker'],
                        'odds1': float(row1['odds']),
                        'line2': float(line2),
                        'bookmaker2': row2['bookmaker'],
                        'odds2': float(row2['odds']),
                        'middle_range': f"{min_line} to {max_line}",
                        'win_both_scenarios': f"Result between {min_line} and {max_line}",
                        'max_profit_percentage': round(max_profit, 2),
                        'worst_case_loss_percentage': round(worst_case_loss, 2),
                        'roi': round(roi, 2),
                        'status': 'active',
                        'timestamp': timestamp,
                        'expires_at': expires_at
                    })
        
    
        return middles
    

    
    @staticmethod
    def _extract_lines(row1, row2) -> Tuple[float, float]:
        """Extract line values from market params or outcome names"""
        try:
            # Try to extract from market_params
            if pd.notna(row1.get('market_params')):
                line1 = float(''.join(filter(lambda x: x.isdigit() or x in '.-', str(row1['market_params']))))
            else:
                # Try from outcome
                line1 = float(''.join(filter(lambda x: x.isdigit() or x in '.-', str(row1['outcome']))))
            
            if pd.notna(row2.get('market_params')):
                line2 = float(''.join(filter(lambda x: x.isdigit() or x in '.-', str(row2['market_params']))))
            else:
                line2 = float(''.join(filter(lambda x: x.isdigit() or x in '.-', str(row2['outcome']))))
            
            return line1, line2
        except:
            return None, None
    
    @staticmethod
    def detect_ev(odds_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect Expected Value (EV+) opportunities
        Logic: Compare bookmaker odds to fair odds (consensus/average)
        EV = (odds * fair_probability) - 1
        """
        if odds_df.empty:
            return []
        
        opportunities = []
        timestamp = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(hours=2)).isoformat()
        
        grouped = odds_df.groupby(['event_id', 'sport', 'match', 'market', 'outcome'])
        
        for (event_id, sport, match, market, outcome), group in grouped:
            # Calculate fair odds from consensus (average of all bookmakers)
            avg_odds = group['odds'].mean()
            fair_probability = 1 / avg_odds
            
            # Find bookmakers offering better than fair odds
            for _, row in group.iterrows():
                offered_odds = row['odds']
                implied_probability = 1 / offered_odds
                
                # Calculate EV
                expected_value = (offered_odds * fair_probability - 1) * 100
                edge_percentage = (1 - implied_probability / fair_probability) * 100
                
                if edge_percentage >= DetectionService.EV_MIN_EDGE:
                    # Kelly criterion recommended stake (simplified)
                    kelly_fraction = (offered_odds * fair_probability - 1) / (offered_odds - 1)
                    recommended_stake = max(0, min(kelly_fraction * 100, 10))  # Cap at 10% of bankroll
                    
                    opportunities.append({
                        'id': str(uuid.uuid4()),
                        'type': 'ev',
                        'event_id': event_id,
                        'sport': sport,
                        'match': match,
                        'market': market,
                        'outcome': outcome,
                        'bookmaker': row['bookmaker'],
                        'offered_odds': float(offered_odds),
                        'fair_odds': round(avg_odds, 2),
                        'fair_probability': round(fair_probability * 100, 2),
                        'implied_probability': round(implied_probability * 100, 2),
                        'expected_value': round(expected_value, 2),
                        'edge_percentage': round(edge_percentage, 2),
                        'roi': round(edge_percentage, 2),
                        'recommended_stake': round(recommended_stake, 2),
                        'status': 'active',
                        'timestamp': timestamp,
                        'expires_at': expires_at
                    })
        
        return opportunities
    
    @staticmethod
    def detect_lows(odds_df: pd.DataFrame) -> List[Dict[str, Any]]:
        """
        Detect low-hold (low vig) opportunities
        Logic: Find markets where total implied probability is close to 100%
        Hold = (sum of 1/odds) - 1
        """
        if odds_df.empty:
            return []
        
        opportunities = []
        timestamp = datetime.now().isoformat()
        expires_at = (datetime.now() + timedelta(hours=2)).isoformat()
        
        grouped = odds_df.groupby(['event_id', 'sport', 'match', 'market', 'bookmaker'])
        
        for (event_id, sport, match, market, bookmaker), group in grouped:
            # Calculate total implied probability
            total_implied_prob = sum(1 / row['odds'] for _, row in group.iterrows())
            hold_percentage = (total_implied_prob - 1) * 100
            
            if hold_percentage <= DetectionService.LOW_HOLD_MAX:
                # Calculate true probabilities (remove the hold proportionally)
                outcomes_dict = {}
                true_probs = {}
                
                for _, row in group.iterrows():
                    implied_prob = 1 / row['odds']
                    true_prob = implied_prob / total_implied_prob
                    outcomes_dict[row['outcome']] = float(row['odds'])
                    true_probs[row['outcome']] = round(true_prob * 100, 2)
                
                roi = (DetectionService.LOW_HOLD_MAX - hold_percentage) / 2  # Opportunity value
                
                opportunities.append({
                    'id': str(uuid.uuid4()),
                    'type': 'low',
                    'event_id': event_id,
                    'sport': sport,
                    'match': match,
                    'market': market,
                    'bookmaker': bookmaker,
                    'outcomes': outcomes_dict,
                    'total_implied_probability': round(total_implied_prob * 100, 2),
                    'hold_percentage': round(hold_percentage, 2),
                    'true_probability_estimates': true_probs,
                    'roi': round(roi, 2),
                    'status': 'active',
                    'timestamp': timestamp,
                    'expires_at': expires_at
                })
        
        return opportunities
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from typing import Optional, List
import asyncio
import json
from app.services.odds_service import OddsService

router = APIRouter(prefix="/odds", tags=["Odds"])

@router.get("/live")
async def get_live_odds(
    sport: Optional[str] = Query(None, description="Filter by sport"),
    market: Optional[str] = Query(None, description="Filter by market")
):
    """
    Get live odds with optional filters.
    """
    odds = OddsService.get_live_odds(sport=sport, market=market)
    
    return {
        "success": True,
        "count": len(odds),
        "odds": odds
    }

@router.get("/sports")
async def get_sports():
    """Get list of available sports."""
    sports = OddsService.get_available_sports()
    return {
        "success": True,
        "sports": sports
    }

@router.get("/markets")
async def get_markets(sport: Optional[str] = Query(None, description="Filter by sport")):
    """Get list of available markets."""
    markets = OddsService.get_available_markets(sport=sport)
    return {
        "success": True,
        "markets": markets
    }

@router.get("/match/{match_name}")
async def get_match_odds(match_name: str):
    """Get all odds for a specific match."""
    odds = OddsService.get_odds_by_match(match_name)
    return {
        "success": True,
        "match": match_name,
        "count": len(odds),
        "odds": odds
    }

# WebSocket endpoint for live odds streaming
@router.websocket("/ws")
async def websocket_odds(websocket: WebSocket):
    """
    WebSocket endpoint for streaming live odds updates.
    Broadcasts snapshots every 5 seconds.
    """
    await websocket.accept()
    
    try:
        while True:
            # Get odds snapshot
            snapshot = OddsService.get_odds_snapshot()
            
            # Send to client
            await websocket.send_text(json.dumps(snapshot))
            
            # Wait 5 seconds before next update
            await asyncio.sleep(5)
            
    except WebSocketDisconnect:
        print("Client disconnected from odds WebSocket")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()
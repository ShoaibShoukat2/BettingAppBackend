"""
Enhanced Sports Arbitrage Platform API
Main application with unified opportunity detection
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import odds, opportunities, session, bets, admin

app = FastAPI(
    title="Sports Arbitrage Platform API",
    description="""
    Advanced Sports Arbitrage Detection Platform
    
    ## Opportunity Types
    
    ### 🎯 Arbitrage
    Risk-free profit by betting on all outcomes across different bookmakers
    
    ### 🎲 Middles
    Overlapping line opportunities where both bets can win (e.g., +3.5 and -2.5)
    
    ### 📊 EV (Expected Value)
    Positive expected value bets where bookmaker odds are better than fair odds
    
    ### 💰 Lows (Low-Hold)
    Markets with minimal bookmaker margin (low vig), indicating favorable odds
    
    ## Features
    - Real-time odds tracking with WebSocket support
    - Unified opportunity detection across all categories
    - Session-based bet tracking
    - Automatic opportunity expiry and cleanup
    - Comprehensive admin statistics
    
    ## Quick Start
    1. Seed demo data: `POST /admin/seed`
    2. Compute opportunities: `POST /opportunities/compute`
    3. View opportunities: `GET /opportunities/feed`
    4. Create session: `POST /session/init`
    5. Place bets: `POST /bets/place`
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(odds.router)
app.include_router(opportunities.router)
app.include_router(session.router)
app.include_router(bets.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {
        "message": "Sports Arbitrage Platform API v2.0",
        "version": "2.0.0",
        "docs": "/docs",
        "features": {
            "arbitrage": "Risk-free betting opportunities",
            "middles": "Overlapping line opportunities",
            "ev": "Positive expected value bets",
            "lows": "Low-hold markets"
        },
        "endpoints": {
            "odds": "/odds/live",
            "opportunities": "/opportunities/feed",
            "compute": "/opportunities/compute",
            "sessions": "/session/init",
            "bets": "/bets/place",
            "stats": "/admin/stats",
            "refresh": "/admin/refresh",
            "websocket": "/odds/ws"
        },
        "quick_start": [
            "1. POST /admin/seed - Generate demo data",
            "2. POST /opportunities/compute - Detect opportunities",
            "3. GET /opportunities/feed - View opportunities",
            "4. POST /session/init - Create betting session",
            "5. POST /bets/place - Place bets"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "sports-arbitrage-api",
        "version": "2.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
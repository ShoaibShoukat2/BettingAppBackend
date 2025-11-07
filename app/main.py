from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import odds, arbitrage, session, bets, admin

app = FastAPI(
    title="Arbitrage Betting Platform API",
    description="FastAPI backend for arbitrage betting with live odds, surebet detection, and session management",
    version="1.0.0",
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
app.include_router(arbitrage.router)
app.include_router(session.router)
app.include_router(bets.router)
app.include_router(admin.router)

@app.get("/")
async def root():
    return {
        "message": "Arbitrage Betting Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "odds": "/odds/live",
            "arbitrage": "/arbitrage/feed",
            "sessions": "/session/init",
            "bets": "/bets/place",
            "admin": "/admin/stats",
            "websocket": "/odds/ws"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "arbitrage-betting-api"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
    
    
    

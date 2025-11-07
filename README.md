# Arbitrage Betting Platform API

A complete FastAPI backend for arbitrage betting with live odds tracking, surebet detection, session management, and comprehensive betting analytics.

## 🚀 Features

- **Live Odds Feed**: Real-time odds from multiple bookmakers
- **WebSocket Streaming**: Live odds updates via WebSocket
- **Arbitrage Detection**: Automatic surebet calculation for 2-way and 3-way markets
- **Session Management**: Track betting sessions with unique IDs
- **Bet Placement**: Optimal stake distribution for arbitrage opportunities
- **Admin Dashboard**: Comprehensive statistics and data management
- **Thread-Safe CSV Operations**: File locking and atomic writes
- **Swagger Documentation**: Interactive API docs at `/docs`

## 📁 Project Structure

```
arbitrage-betting/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic models for data validation
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── odds.py             # Odds endpoints + WebSocket
│   │   ├── arbitrage.py        # Arbitrage endpoints
│   │   ├── session.py          # Session management
│   │   ├── bets.py             # Bet placement
│   │   └── admin.py            # Admin & stats endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── odds_service.py     # Odds business logic
│   │   ├── arb_service.py      # Arbitrage calculation
│   │   ├── session_service.py  # Session management
│   │   ├── bet_service.py      # Bet processing
│   │   └── demo_seed.py        # Demo data generator
│   └── utils/
│       ├── __init__.py
│       └── csv_io.py           # Thread-safe CSV operations
├── data/
│   ├── odds.csv                # Live odds data
│   ├── arbitrage.csv           # Detected surebets
│   ├── bets.csv                # Placed bets
│   └── sessions.csv            # User sessions
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd arbitrage-betting
```

### 2. Create virtual environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

### 5. Generate demo data

```bash
python -m app.services.demo_seed
```

This will create:
- `data/odds.csv` with ~1000 randomized odds entries
- `data/arbitrage.csv` (empty, will be populated by compute endpoint)
- `data/bets.csv` (empty)
- `data/sessions.csv` (empty)

## 🚀 Running the Application

### Development Mode (with auto-reload)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Python directly

```bash
python -m app.main
```

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root Endpoint**: http://localhost:8000/

## 🔌 API Endpoints

### Odds Endpoints

- `GET /odds/live` - Get live odds (filters: sport, market)
- `GET /odds/sports` - Get available sports
- `GET /odds/markets` - Get available markets
- `GET /odds/match/{match_name}` - Get odds for specific match
- `WS /odds/ws` - WebSocket for live odds streaming

### Arbitrage Endpoints

- `GET /arbitrage/feed` - Get arbitrage opportunities (filters: min_arb, top_n, sport)
- `GET /arbitrage/{arb_id}` - Get specific arbitrage by ID
- `POST /arbitrage/compute` - Manually trigger arbitrage calculation
- `GET /arbitrage/{arb_id}/calculate-stakes` - Calculate optimal stakes

### Session Endpoints

- `POST /session/init` - Create new session
- `GET /session/{session_id}` - Get session details
- `GET /session/` - Get all sessions

### Bet Endpoints

- `POST /bets/place` - Place bets for an arbitrage
- `GET /bets/session/{session_id}` - Get bets for a session
- `GET /bets/{bet_id}` - Get specific bet
- `GET /bets/` - Get all bets

### Admin Endpoints

- `GET /admin/stats` - Get comprehensive statistics
- `POST /admin/seed` - Generate demo data
- `DELETE /admin/reset` - Reset all data (dangerous!)

## 💡 Usage Examples

### 1. Initialize a Session

```bash
curl -X POST http://localhost:8000/session/init \
  -H "Content-Type: application/json" \
  -d '{"user_name": "John Doe"}'
```

Response:
```json
{
  "success": true,
  "session": {
    "session_id": "abc-123-def-456",
    "created_at": "2024-01-15T10:30:00",
    "message": "Session created successfully"
  }
}
```

### 2. Get Live Odds

```bash
curl "http://localhost:8000/odds/live?sport=Football&market=Match Winner"
```

### 3. Compute Arbitrage Opportunities

```bash
curl -X POST http://localhost:8000/arbitrage/compute
```

### 4. Get Arbitrage Feed

```bash
curl "http://localhost:8000/arbitrage/feed?min_arb=1.0&top_n=10"
```

### 5. Calculate Stakes for an Arbitrage

```bash
curl "http://localhost:8000/arbitrage/{arb_id}/calculate-stakes?total_stake=1000"
```

### 6. Place a Bet

```bash
curl -X POST http://localhost:8000/bets/place \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123-def-456",
    "arbitrage_id": "xyz-789",
    "total_stake": 1000
  }'
```

### 7. Get Statistics

```bash
curl http://localhost:8000/admin/stats
```

### 8. WebSocket Connection (JavaScript)

```javascript
const ws = new WebSocket('ws://localhost:8000/odds/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Live odds update:', data);
};
```

## 🧪 Testing the Application

### 1. Generate demo data

```bash
python -m app.services.demo_seed
```

### 2. Start the server

```bash
uvicorn app.main:app --reload
```

### 3. Visit Swagger UI

Open http://localhost:8000/docs and test all endpoints interactively.

### 4. Test workflow

1. Initialize session: `POST /session/init`
2. Compute arbitrage: `POST /arbitrage/compute`
3. Get arbitrage feed: `GET /arbitrage/feed?min_arb=0.5`
4. Calculate stakes: `GET /arbitrage/{arb_id}/calculate-stakes?total_stake=1000`
5. Place bet: `POST /bets/place`
6. View stats: `GET /admin/stats`

## 🔧 Configuration

Edit `.env` file to customize:

- `HOST`: Server host (default: 0.0.0.0)
- `PORT`: Server port (default: 8000)
- `DEBUG`: Debug mode (default: True)
- `WS_BROADCAST_INTERVAL`: WebSocket update interval in seconds (default: 5)

## 📊 Data Files

All data is stored in CSV format in the `data/` directory:

- **odds.csv**: Current odds from all bookmakers
- **arbitrage.csv**: Detected arbitrage opportunities
- **bets.csv**: All placed bets with session tracking
- **sessions.csv**: User betting sessions

## 🔒 Thread Safety

The application uses `portalocker` for file locking to ensure thread-safe CSV operations:

- **Shared locks** for reading
- **Exclusive locks** for writing
- **Atomic writes** using temporary files

## 🎯 Arbitrage Calculation

The system automatically detects arbitrage opportunities by:

1. Grouping odds by sport, match, and market
2. Finding best odds for each outcome across bookmakers
3. Calculating arbitrage percentage: `(1/odds1 + 1/odds2 + 1/odds3) * 100`
4. If < 100%, it's a surebet with profit = `100 - arb_percentage`

## 📈 Future Enhancements

- [ ] PostgreSQL/MySQL database support
- [ ] Redis caching for faster reads
- [ ] Background task scheduler for auto-computing arbitrage
- [ ] User authentication & authorization
- [ ] Real-time odds scraping from actual bookmakers
- [ ] Email/SMS notifications for new surebets
- [ ] Historical data & analytics dashboard
- [ ] Bet result tracking & P&L calculation

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is for educational purposes only. Always comply with local gambling laws and bookmaker terms of service.

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- Uvicorn for the ASGI server
- Pandas for data processing
- Portalocker for file locking

---

**Happy Arbitrage Betting! 🎰💰**
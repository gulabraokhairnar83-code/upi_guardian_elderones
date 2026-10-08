# UPI Guardian - Flask Backend

Modular REST API backend powering the UPI Guardian financial fraud detection and elder protection system.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py           # Flask application factory (create_app)
│   ├── config.py             # Environment configurations
│   ├── extensions.py         # Extensions initialization (CORS)
│   ├── routes/               # Modular REST Blueprints
│   │   ├── __init__.py
│   │   ├── health.py         # GET /api/health
│   │   ├── dashboard.py      # GET /api/dashboard/summary
│   │   ├── transactions.py   # GET, POST /api/transactions, /api/analyze-transaction
│   │   ├── alerts.py         # GET, POST /api/alerts, /api/alerts/<id>/resolve
│   │   ├── family.py         # GET, POST /api/family/profile, /api/family/alerts/resolve
│   │   ├── messages.py       # POST /api/analyze-message
│   │   └── settings.py       # GET, PATCH /api/settings
│   ├── services/             # Business logic layer
│   ├── models/               # Data models and synthetic in-memory repositories
│   ├── schemas/              # Request payload validation
│   └── utils/                # Centralized errors and response helpers
├── tests/                    # Pytest test suite
├── requirements.txt          # Python dependencies
├── run.py                    # Server executable runner
├── .env.example              # Environment variables template
└── README.md                 # Backend documentation
```

## Setup & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 3. Run the Flask Server
```bash
python run.py
```
The server will start at `http://127.0.0.1:5000`.

### 4. Run Tests
```bash
pytest
```

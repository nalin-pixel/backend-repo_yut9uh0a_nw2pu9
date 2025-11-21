import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from database import db, create_document, get_documents
from schemas import Instrument, Strategy, Trade

app = FastAPI(title="Opus Trading API", description="Unified API for multi-asset algo trading platform: equities, derivatives, currency, commodities, crypto (sim), global markets (sim).", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"name": "Opus", "status": "ok", "message": "Welcome to Opus Trading API"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:20]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
    return response

# --- OPUS: Reference data (markets & instruments) ---
class MarketRequest(BaseModel):
    tier: Optional[str] = None  # TIER-1, TIER-2, TIER-3 or None for all

TIER_MARKETS: Dict[str, List[Dict[str, Any]]] = {
    "TIER-1": [
        {"segment": "Equity (Cash)", "exchanges": ["NSE", "BSE"], "notes": ["breakout", "moving average", "momentum", "VWAP", "scalping"]},
        {"segment": "Equity Derivatives (F&O)", "instruments": ["Index futures", "Stock futures", "Index options", "Stock options"], "indices": ["NIFTY", "BANKNIFTY", "FINNIFTY", "MIDCAPNIFTY"]},
        {"segment": "Currency Derivatives", "pairs": ["USD/INR", "EUR/INR", "GBP/INR", "JPY/INR"], "instruments": ["Futures", "Options"]},
        {"segment": "Commodities (MCX)", "contracts": ["Gold", "Silver", "Crude Oil", "Natural Gas", "Copper", "Zinc", "Nickel", "Lead"]},
    ],
    "TIER-2": [
        {"segment": "Global Markets (Simulated)", "assets": ["US Stocks", "US ETFs", "S&P500 futures", "NASDAQ futures", "Gold/Oil global futures"]},
        {"segment": "Crypto (Simulated)", "pairs": ["BTC/USDT", "ETH/USDT", "BNB", "SOL", "XRP", "DOGE"], "perpetuals": True},
    ],
    "TIER-3": [
        {"segment": "Fixed Income", "assets": ["Government Bonds", "Corporate Bonds", "G-Sec Futures"], "data": ["Yield Curve"]},
        {"segment": "Indices & Breadth", "data": ["India VIX", "Advance/Decline", "PCR", "Volume profile", "Sector indices"]},
        {"segment": "Market Internals", "data": ["FII/DII flows", "OI buildup", "Heatmaps", "Volume clusters", "Delta & footprint"]},
    ],
}

@app.get("/api/markets")
def get_markets(tier: Optional[str] = None):
    if tier:
        return {tier: TIER_MARKETS.get(tier.upper(), [])}
    return TIER_MARKETS

# --- OPUS: Strategies ---
@app.post("/api/strategies")
def create_strategy(strategy: Strategy):
    try:
        sid = create_document("strategy", strategy)
        return {"id": sid, "message": "Strategy saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/strategies")
def list_strategies():
    try:
        items = get_documents("strategy", limit=100)
        # Cast ObjectId to str for JSON safety
        for it in items:
            it["_id"] = str(it["_id"])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- OPUS: Instruments ---
@app.post("/api/instruments")
def add_instrument(instr: Instrument):
    try:
        iid = create_document("instrument", instr)
        return {"id": iid, "message": "Instrument added"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/instruments")
def list_instruments(exchange: Optional[str] = None, asset_class: Optional[str] = None):
    try:
        query: Dict[str, Any] = {}
        if exchange:
            query["exchange"] = exchange
        if asset_class:
            query["asset_class"] = asset_class
        items = get_documents("instrument", filter_dict=query, limit=200)
        for it in items:
            it["_id"] = str(it["_id"])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- OPUS: Paper trading (simulated execution) ---
class PaperOrder(BaseModel):
    instrument: Instrument
    side: str  # BUY/SELL
    qty: float
    price: float

@app.post("/api/paper/order")
def paper_order(order: PaperOrder):
    if order.side not in ("BUY", "SELL"):
        raise HTTPException(status_code=400, detail="side must be BUY or SELL")
    trade = Trade(
        instrument=order.instrument,
        side=order.side,
        qty=order.qty,
        price=order.price,
    )
    try:
        tid = create_document("trade", trade)
        return {"id": tid, "status": "filled", "avg_price": order.price}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/paper/trades")
def list_trades(symbol: Optional[str] = None):
    try:
        query: Dict[str, Any] = {}
        if symbol:
            query["instrument.symbol"] = symbol
        items = get_documents("trade", filter_dict=query, limit=200)
        for it in items:
            it["_id"] = str(it["_id"])
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- OPUS: Analytics placeholders ---
@app.get("/api/analytics/overview")
def analytics_overview():
    return {
        "mvp": [
            "Stocks (NSE/BSE)",
            "Index & stock futures",
            "Index & stock options",
            "Commodity futures (MCX)",
            "Currency derivatives (NSE)"
        ],
        "premium": [
            "Crypto (sim)", "US markets (sim)", "ETFs (sim)", "Indices + VIX",
            "FII/DII flows", "Advance-decline", "Option chain analytics", "OI heatmap"
        ],
        "pro": [
            "Bonds, G-Secs", "Algo marketplace", "Copy trading", "Strategy sharing",
            "Neural-network prediction", "Multi-market arbitrage"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

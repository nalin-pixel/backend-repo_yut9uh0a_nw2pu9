"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# OPUS trading platform schemas

class Instrument(BaseModel):
    """Tradable instrument metadata"""
    symbol: str = Field(..., description="Symbol or identifier, e.g., NIFTY, SBIN, GOLDM")
    exchange: str = Field(..., description="Exchange code: NSE, BSE, MCX, NSE-CDS, CME, CRYPTO")
    asset_class: str = Field(..., description="Equity, Futures, Options, Currency, Commodity, Crypto, Bond")
    expiry: Optional[str] = Field(None, description="Expiry for derivatives, e.g., 2025-11-27")
    strike: Optional[float] = Field(None, description="Strike price for options")
    option_type: Optional[str] = Field(None, description="CE or PE for options")

class Strategy(BaseModel):
    """User-defined strategy config"""
    name: str = Field(..., description="Strategy name")
    category: str = Field(..., description="breakout, moving-average, momentum, vwap, scalping, options-spread, etc.")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Key-value parameter set")
    market: str = Field(..., description="Target market: equity, futures, options, currency, commodity, crypto")

class Trade(BaseModel):
    """Executed trade or simulated trade"""
    instrument: Instrument
    side: str = Field(..., description="BUY or SELL")
    qty: float = Field(..., gt=0, description="Quantity or lot size")
    price: float = Field(..., gt=0, description="Fill price")
    timestamp: Optional[str] = Field(None, description="ISO timestamp")
    pnl: Optional[float] = Field(None, description="Profit/loss for the trade")

# Add your own schemas here:
# --------------------------------------------------

# Note: The Flames database viewer will automatically:
# 1. Read these schemas from GET /schema endpoint
# 2. Use them for document validation when creating/editing
# 3. Handle all database operations (CRUD) directly
# 4. You don't need to create any database endpoints!

from pydantic import BaseModel, Field
from typing import Literal, Optional
from datetime import datetime

Side = Literal["BUY", "SELL"]

class Trade(BaseModel):
    tradeId: str
    userId: str
    seq: int
    ticker: str
    side: Side
    price: int
    qty: int
    commission: int = 0
    orderDate: datetime

class Allocation(BaseModel):
    allocId: str
    userId: str
    ticker: str
    sellTradeId: str
    buyTradeId: str
    qtyAllocated: int
    buyPrice: int
    buyCommission: int
    buyQty: int
    sellPrice: int
    sellCommission: int
    sellQty: int
    realisedPnl: int
    createdAt: datetime = Field(default_factory=datetime.utcnow)

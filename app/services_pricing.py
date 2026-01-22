from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
import requests
from cachetools import TTLCache
from app.config import settings

@dataclass
class PriceResult:
    ticker: str
    price: Optional[float]
    raw: Dict[str, Any]

class PricingService:
    """
    CSX endpoint in your earlier message:
    POST /api/v1/website/market-data/stock/prices?lang=en
    with body: board, symbol, fromDate, toDate, tradingMethod
    """
    def __init__(self):
        self.cache = TTLCache(maxsize=512, ttl=45)

    def get_latest_price(self, symbol: str) -> PriceResult:
        key = f"latest:{symbol}"
        if key in self.cache:
            return self.cache[key]

        url = f"{settings.csx_base_url}/api/v1/website/market-data/stock/prices"
        params = {"lang": settings.csx_lang}

        # For "latest", we request a short recent window.
        # You can tune dates later; CSX response format may include latest record in result list.
        from_date = "20260101"
        to_date = "20261231"

        payload = {
            "board": "main",
            "symbol": symbol,
            "fromDate": from_date,
            "toDate": to_date,
            "tradingMethod": "all"
        }

        r = requests.post(url, params=params, json=payload, timeout=15)
        r.raise_for_status()
        data = r.json()

        # Try to pick the last item if there's a list of prices
        latest_price = None
        try:
            # Common patterns: data["data"] list or data["result"] list (depends on API)
            arr = data.get("data") or data.get("result") or data.get("items") or []
            if isinstance(arr, list) and arr:
                last = arr[-1]
                # guess field name
                latest_price = float(last.get("close") or last.get("price") or last.get("last") or last.get("lastPrice"))
        except Exception:
            latest_price = None

        res = PriceResult(ticker=symbol, price=latest_price, raw=data)
        self.cache[key] = res
        return res
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
    change: Optional[int] = None  # Change amount in riel
    change_direction: Optional[str] = None  # "up", "down", or "equal"
    raw: Dict[str, Any] = None

class PricingService:
    """
    CSX endpoint: POST /api/v1/website/market-data/stock/trade-summary
    Returns current market data for all stocks on a given board
    """
    def __init__(self):
        self.cache = TTLCache(maxsize=512, ttl=45)

    def get_latest_price(self, symbol: str) -> PriceResult:
        key = f"latest:{symbol}"
        if key in self.cache:
            return self.cache[key]

        url = f"{settings.csx_base_url}/api/v1/website/market-data/stock/trade-summary"

        payload = {
            "board": "all",
            "fromDate": None
        }

        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            data = r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching price for {symbol}: {e}")
            res = PriceResult(ticker=symbol, price=None, raw={"error": str(e)})
            self.cache[key] = res
            return res

        # Extract the auction trading data which contains stock prices
        latest_price = None
        change = None
        change_direction = None
        
        try:
            auction_data = data.get("data", {}).get("auctionTradingMethod", [])
            if isinstance(auction_data, list):
                # Find the stock matching the symbol
                for stock_data in auction_data:
                    if stock_data.get("stock", "").upper() == symbol.upper():
                        # Remove commas from price string and convert to float
                        price_str = str(stock_data.get("close", "")).replace(",", "")
                        latest_price = float(price_str)
                        
                        # Extract change info
                        change = stock_data.get("change")  # e.g., 40 or -40
                        change_direction = stock_data.get("changeUpDown")  # "up", "down", "equal"
                        break
        except Exception as e:
            print(f"Error parsing price for {symbol}: {e}")
            latest_price = None

        res = PriceResult(ticker=symbol, price=latest_price, change=change, 
                         change_direction=change_direction, raw=data)
        self.cache[key] = res
        return res

    def get_all_prices(self) -> list:
        """Get all stock prices from the API"""
        key = "all_prices"
        if key in self.cache:
            return self.cache[key]

        url = f"{settings.csx_base_url}/api/v1/website/market-data/stock/trade-summary"

        payload = {
            "board": "all",
            "fromDate": None
        }

        try:
            r = requests.post(url, json=payload, timeout=15)
            r.raise_for_status()
            data = r.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching all prices: {e}")
            return []

        all_stocks = []
        try:
            auction_data = data.get("data", {}).get("auctionTradingMethod", [])
            if isinstance(auction_data, list):
                for stock_data in auction_data:
                    try:
                        ticker = stock_data.get("stock", "").upper()
                        price_str = str(stock_data.get("close", "")).replace(",", "")
                        price = float(price_str)
                        change = stock_data.get("change", 0)
                        change_direction = stock_data.get("changeUpDown", "equal")
                        
                        all_stocks.append({
                            "ticker": ticker,
                            "price": price,
                            "change": change,
                            "change_direction": change_direction
                        })
                    except (ValueError, TypeError):
                        continue
        except Exception as e:
            print(f"Error parsing all prices: {e}")

        self.cache[key] = all_stocks
        return all_stocks
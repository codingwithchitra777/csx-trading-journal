import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app
from app.db.database import get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def clean_db():
    # Clean database before each test
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE allocations CASCADE")
            cur.execute("TRUNCATE TABLE trades CASCADE")
            cur.execute("TRUNCATE TABLE users CASCADE")

def test_health():
    response = client.get("/api/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "csx-trading-journal-backend"

def test_healthz():
    response = client.get("/api/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_trade_flow_lifo():
    # 1. Record BUY orders
    # Buy 100 @ 7000 (Seq 1)
    res = client.post("/api/trades", json={"ticker": "ABC", "side": "BUY", "price": 7000, "qty": 100}, headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["trade"]["seq"] == 1

    # Buy 100 @ 7100 (Seq 2)
    res = client.post("/api/trades", json={"ticker": "ABC", "side": "BUY", "price": 7100, "qty": 100}, headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["trade"]["seq"] == 2

    # Buy 100 @ 7200 (Seq 3) - Most recent
    res = client.post("/api/trades", json={"ticker": "ABC", "side": "BUY", "price": 7200, "qty": 100}, headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["trade"]["seq"] == 3

    # 2. Record a SELL order matching LIFO
    # Sell 150 @ 7500 (Seq 4)
    # LIFO should match:
    # - 100 from Buy #3 @ 7200 -> realised P/L: 100 * (7500 - 7200) = 30000 (minus commissions)
    # - 50 from Buy #2 @ 7100 -> realised P/L: 50 * (7500 - 7100) = 20000 (minus commissions)
    res = client.post("/api/trades", json={"ticker": "ABC", "side": "SELL", "price": 7500, "qty": 150}, headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] == True
    assert data["realisedPnl"] > 0
    assert len(data["allocations"]) == 2

    # 3. Check portfolio
    res = client.get("/api/portfolio", headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    portfolio_data = res.json()
    assert len(portfolio_data) == 1
    assert portfolio_data[0]["ticker"] == "ABC"
    assert portfolio_data[0]["remainingQty"] == 150

    # 4. Check position details
    res = client.get("/api/position/ABC", headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    pos_data = res.json()
    assert pos_data["remainingQty"] == 150
    remaining_lots = pos_data["remainingLots"]
    assert len(remaining_lots) == 3
    # Under LIFO matching:
    # - Seq 3 (100 shares @ 7200) was fully matched/closed (qtyOpen = 0).
    # - Seq 2 (100 shares @ 7100) was matched for 50 shares, leaving 50 shares open.
    # - Seq 1 (100 shares @ 7000) is untouched, leaving 100 shares open.
    assert remaining_lots[0]["seq"] == 3
    assert remaining_lots[0]["qtyOpen"] == 0
    assert remaining_lots[0]["qtyOriginal"] == 100
    
    assert remaining_lots[1]["seq"] == 2
    assert remaining_lots[1]["qtyOpen"] == 50
    assert remaining_lots[1]["qtyOriginal"] == 100
    
    assert remaining_lots[2]["seq"] == 1
    assert remaining_lots[2]["qtyOpen"] == 100
    assert remaining_lots[2]["qtyOriginal"] == 100

def test_chart_endpoint():
    res = client.get("/api/chart/ABC")
    assert res.status_code == 200
    assert res.headers["content-type"] == "image/png"

def test_trade_init():
    # 1. Test BUY side init (always valid, simulated P/L = 0)
    res = client.post("/api/trades/init", json={"ticker": "ABC", "side": "BUY", "price": 7000, "qty": 100}, headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] == True
    assert data["valid"] == True
    assert data["validationError"] is None
    assert data["simulatedPnl"] == 0
    assert data["isLoss"] == False
    assert data["simulatedLossAmount"] == 0
    assert data["existingQty"] == 0

    # 2. Test SELL side init with 0 shares (should be invalid)
    res = client.post("/api/trades/init", json={"ticker": "ABC", "side": "SELL", "price": 7500, "qty": 50}, headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] == True
    assert data["valid"] == False
    assert "Cannot sell 50 shares. You only own 0 shares of ABC." in data["validationError"]

    # 3. Add BUY trades to database so we have position
    # Buy 100 @ 7000
    client.post("/api/trades", json={"ticker": "ABC", "side": "BUY", "price": 7000, "qty": 100}, headers={"X-User-Id": "u001"})
    # Buy 100 @ 7200
    client.post("/api/trades", json={"ticker": "ABC", "side": "BUY", "price": 7200, "qty": 100}, headers={"X-User-Id": "u001"})

    # 4. Test SELL side init with sufficient shares (selling 50 @ 7500)
    res = client.post("/api/trades/init", json={"ticker": "ABC", "side": "SELL", "price": 7500, "qty": 50}, headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] == True
    assert data["valid"] == True
    assert data["validationError"] is None
    assert data["existingQty"] == 200

    # 5. Test SELL side init showing loss (selling 50 @ 6500)
    res = client.post("/api/trades/init", json={"ticker": "ABC", "side": "SELL", "price": 6500, "qty": 50}, headers={"X-User-Id": "u001"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] == True
    assert data["valid"] == True
    assert data["isLoss"] == True
    assert data["simulatedLossAmount"] > 0

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__]))

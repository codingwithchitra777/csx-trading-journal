# Move P/L Calculation and Validation to Backend (Init & Confirm Trade)

Move the LIFO matching simulation and ownership validation logic from the Angular frontend to the FastAPI backend. This aligns the project with SOLID design principles and prevents code duplication and client-side unresponsiveness.

The backend will expose two clean endpoints for trade submission:
1. `POST /api/trades/init`: Simulates the trade, performs validation, and returns calculated P/L.
2. `POST /api/trades/confirm`: Commits the trade and executes the LIFO allocation database inserts.

---

## Proposed Changes

### Backend (FastAPI)

#### [MODIFY] [lifo_matcher.py](file:///c:/workspace_coding_with_chitra/csx-trading-journal/backend/app/services/lifo_matcher.py)
* Add `simulate_sell_lifo(self, user_id: str, ticker: str, price: int, qty: int) -> Dict[str, Any]`
  * Queries buy lots and active allocations for the user.
  * Checks if the user has enough shares (open quantity). If not, returns `valid: False` and a descriptive error message.
  * Simulates LIFO matching to calculate simulated gross and net profit/loss (net of transaction fees).
  * Returns: `{ "valid": True, "validationError": None, "simulatedPnl": pnl, "isLoss": is_loss, "simulatedLossAmount": loss_amount }`.

#### [MODIFY] [trade.py](file:///c:/workspace_coding_with_chitra/csx-trading-journal/backend/app/api/v1/endpoints/trade.py)
* Add `POST /api/trades/init` endpoint:
  * Accepts `TradeCreate` schema.
  * Resolves user ID from `X-User-Id` header.
  * If side is `SELL`, calls `lifo_matcher_service.simulate_sell_lifo(...)`.
  * If side is `BUY`, validates parameters and returns `valid: True` with `simulatedPnl: 0`.
  * Always returns `existingQty` based on `portfolio_service.position_detail`.
* Add `POST /api/trades/confirm` endpoint:
  * Accepts `TradeCreate` schema.
  * Inserts the trade, executes `lifo_service.match_sell_lifo(...)`, and returns the results.
  * (Keeps existing `/api/trades` POST endpoint routing to the same confirm logic for backwards compatibility).

---

### Frontend (Angular)

#### [MODIFY] [api.service.ts](file:///c:/workspace_coding_with_chitra/csx-trading-journal/frontend/src/app/services/api.service.ts)
* Add `initTrade(trade)` and `confirmTrade(trade)` HTTP client methods:
  * `initTrade` posts to `/api/trades/init`.
  * `confirmTrade` posts to `/api/trades/confirm`.

#### [MODIFY] [record-trade.ts](file:///c:/workspace_coding_with_chitra/csx-trading-journal/frontend/src/app/pages/record-trade/record-trade.ts)
* Refactor `startTradeSubmit()` to call `apiService.initTrade(...)`.
  * Sets `this.loadingValidation = true`.
  * Subscribes to the init-trade response.
  * Populates `existingQty`, `validationError`, `simulatedPnl`, `isLoss`, and `simulatedLossAmount` directly from the backend response.
  * Replaces the manual TypeScript LIFO simulation loops entirely.
* Refactor `confirmAndSubmitTrade()` to call `apiService.confirmTrade(...)`.
  * Subscribes to the confirm-trade response, sets `tradeSuccess`, resets input fields, and reloads active position details.

---

## Verification Plan

### Automated Tests
* Create unit tests in `backend/test_api.py` targeting `POST /api/trades/init` for both successful simulations, validation failures (insufficient shares), and simulated losses.

### Manual Verification
* Run the application and navigate to the **Record Trade** page.
* Select a stock and verify:
  1. Entering a BUY trade goes directly to the confirmation screen instantly.
  2. Entering a SELL trade showing a profit shows the correct simulated P/L in the confirmation modal.
  3. Entering a SELL trade showing a loss displays the warning card in the modal.
  4. Entering a SELL trade exceeding owned shares displays the validation error block in the modal.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Trading Journal tracks stock trades on the Cambodia Securities Exchange (CSX, prices in riel). One FastAPI backend serves three clients:

- **Telegram bot** (`backend/app/services/bot.py`) — the primary interface, commands like `/buy`, `/sell`, `/portfolio`, `/stock`, `/position`. Runs in a background thread spawned from the FastAPI `lifespan` startup hook in `backend/app/main.py`, alongside the HTTP server, in the same process.
- **Angular web frontend** (`frontend/`) — pages under `frontend/src/app/pages/` (dashboard, history, portfolio, login, record-trade) mirror the bot's functionality via the REST API.
- **Flutter mobile app** (`app/`) — same idea, screens under `app/lib/screens/`. Add Trade mirrors the web's two-step flow (below) and the whole app is localized (English/Khmer, below).

## Commands

### Backend (FastAPI + Telegram bot, Python 3.12)
```bash
docker-compose up -d                 # start Postgres (localhost:5433, db trading_journal)
pip install -r backend/requirements.txt
cd backend && python main.py         # runs FastAPI (port 8080) AND starts the Telegram bot thread
```
Tests are integration tests that hit the real Postgres DB (they `TRUNCATE` tables between runs), so the DB must be up first:
```bash
cd backend
pytest                                # full suite
pytest test_api.py                    # one file
pytest test_api.py::test_trade_flow_lifo   # one test
```
`backend/demo_charts.py`, `lifo_example.py`, `final_verification.py`, `test_changes.py`, `test_lowest_price.py` are standalone manual/demo scripts (plain `print` output, not pytest — run directly with `python <file>.py`), not part of the `pytest` suite. Note `final_verification.py` imports from stale module paths (`app.services_lifo`, `app.bot`) that no longer exist under the current `app/services/` layout — it's broken and safe to ignore or delete rather than fix.

`backend/pyproject.toml` exists alongside `requirements.txt` solely for `fastapi deploy` to FastAPI Cloud (which requires `pyproject.toml`, not `requirements.txt`, and needs `tool.uv.package = false` since this isn't an installable package). Local dev still uses `pip install -r backend/requirements.txt` — keep both files' dependency versions in sync by hand when either changes. Same pattern in `hello-world-logfire/` (a standalone FastAPI Cloud sample/smoke-test app, not part of the real backend).

### Frontend (Angular)
```bash
cd frontend
npm install
npm start          # ng serve
npm run build
npm test           # ng test
```

### App (Flutter)
```bash
cd app
flutter pub get
flutter run
flutter analyze
flutter test          # offline widget smoke test only
```
`intl` is pinned to `^0.20.2` (not the newer `^0.20.3`) because `flutter_localizations` from the SDK pins it there — bumping it will break `pub get`.

After editing any file under `lib/l10n/*.arb`, regenerate the localization classes before the new strings are visible:
```bash
flutter gen-l10n     # reads l10n.yaml, writes lib/l10n/app_localizations*.dart
```
Don't hand-edit `lib/l10n/app_localizations*.dart` — they're generated output.

There is no reliable way to drive the Flutter UI against the real backend from this sandbox: `flutter test` mocks `dart:io HttpClient` to always return 400 (a documented TestWidgetsFlutterBinding constraint), `dart run` can't compile anything importing `package:flutter/foundation.dart` (needs `dart:ui`, unavailable outside the Flutter engine), and Flutter web's CanvasKit renderer paints to `<canvas>` so Playwright text selectors don't see anything. `flutter test --platform chrome` runs in a real headless Chrome and *can* reach a live backend, but was flaky in this environment (failed at the connection level, not the assertion level, with a different failure each run) — don't treat one green run as reliable, and prefer verifying the HTTP contract directly with `curl` against `backend`'s running instance instead.

## Architecture

**Data layer is raw psycopg2, not SQLAlchemy.** `backend/app/db/database.py` holds a `ThreadedConnectionPool` and creates the schema imperatively in `init_db()` (executed once, on first pool access) — there's no ORM, no Alembic, and the `models/` package is empty. `repositories/` (`trade.py`, `allocation.py`, `user.py`) hand-write SQL and return plain camelCase dicts, not model instances. This diverges from `.agents/AGENTS.md`, which describes an aspirational Clean Architecture (SQLAlchemy 2.x, Alembic, JWT auth, Pydantic Settings) that the code does not currently follow — treat `AGENTS.md` as a target/style guide, not a description of the current codebase, when navigating `backend/`.

**Only LIFO matching is wired up, despite the README describing "Lowest Price First."** `backend/app/services/lifo_matcher.py`'s `LifoMatcherService.match_sell_lifo` reverses the buy list to match the *most recently bought* lot first (true LIFO), and this is the only matcher `bot.py` calls (`self.lifo.match_sell_lifo`, line ~224). `backend/app/services/fifo_matcher.py` (`FifoMatcherService`) exists but is never imported or used anywhere — dead code. If asked to change matching behavior, check `lifo_matcher.py`'s actual logic rather than trusting its docstrings or the README, since they disagree with each other.

**Auth is Google-token passthrough, not Firebase or JWT.** `backend/app/api/v1/endpoints/auth.py`'s `/auth/google` endpoint verifies the client-supplied Google ID token by calling Google's `tokeninfo` endpoint directly and checking `aud` against a hardcoded client ID — it does not issue its own session/JWT token, and there's no `core/security.py`. Firebase config exists in `core/config.py` (`firebase_sa_path`, `firebase_credentials_json`, `firebase_project_id`) but nothing in `backend/app` actually uses it yet.

**Pricing** (`backend/app/services/pricing.py`) calls CSX's public API (`POST /api/v1/website/market-data/stock/trade-summary`) through a `TTLCache`, falling back to hardcoded `FALLBACK_PRICES` for common tickers if the live call fails.

**Charts** (`backend/app/utils/chart_renderer.py`, `theme.py`) render matplotlib images (headless `Agg` backend, set in `main.py`) for the bot's `/stock` and `/position` visualizations — these are Telegram-bot-only, not used by the REST API/web/mobile clients.

**Two parallel command surfaces exist for the same business logic**: `bot.py`'s command handlers (`buy_cmd`, `sell_cmd`, etc.) call the repositories/services directly, while `backend/app/api/v1/endpoints/{trade,portfolio,market}.py` expose the same operations as REST endpoints (via `api/deps.py` dependency providers) for the Angular/Flutter clients. Changes to trade/matching/portfolio logic generally need to be checked against both call sites.

Money and quantities are stored as `INT` (riel has no subunits); commission is a hardcoded 0.47% in the matcher simulation path.

**Trade submission is a two-step init/confirm flow, not a single POST**, on both web and mobile. `POST /api/trades/init` (`backend/app/api/v1/endpoints/trade.py`) validates and LIFO-simulates the trade *without committing* — returning `valid`/`validationError` (e.g. overselling), and for SELLs `simulatedPnl`/`isLoss`/`simulatedLossAmount` so the client can show a loss warning before the user confirms. `POST /api/trades/confirm` then actually commits and returns the real `trade`/`allocations`/`realisedPnl`. Angular's `frontend/src/app/pages/record-trade/` and Flutter's `app/lib/screens/add_trade_screen.dart` (via `app/lib/services/api_service.dart`'s `initTrade`/`confirmTrade`) both implement this same two-call pattern — check both if changing the contract.
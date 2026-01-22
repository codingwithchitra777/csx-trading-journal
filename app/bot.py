from __future__ import annotations
from datetime import datetime
import uuid

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import settings
from app.repositories import TradeRepository, AllocationRepository, UserRepository
from app.services_fifo import FifoMatcherService
from app.services_pricing import PricingService
from app.services_portfolio import PortfolioService

trade_repo = TradeRepository()
alloc_repo = AllocationRepository()
user_repo = UserRepository()

pricing = PricingService()
fifo = FifoMatcherService(trade_repo, alloc_repo)
portfolio = PortfolioService(trade_repo, alloc_repo, pricing)

def _user_id(update: Update) -> str:
    # Minimal approach: map Telegram username to userId if you want later.
    # For now, use DEFAULT_USER_ID (u001) like your table.
    return settings.default_user_id

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = _user_id(update)
    tg_name = update.effective_user.username or update.effective_user.full_name
    user_repo.upsert_user(user_id, tg_name)
    await update.message.reply_text(
        "CSX Trading Journal ✅\n"
        "Commands:\n"
        "/price ABC\n"
        "/buy ABC 7280 100 3422\n"
        "/sell ABC 7400 100 3500\n"
        "/position ABC\n"
        "/portfolio\n"
        "/top_orders\n"
        "/top_tickers"
    )

async def price_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /price ABC")
        return
    ticker = context.args[0].upper()
    res = pricing.get_latest_price(ticker)
    await update.message.reply_text(f"{ticker} last price: {res.price if res.price is not None else 'N/A'}")

async def buy_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /buy ABC 7280 100 [commission]")
        return
    user_id = _user_id(update)
    ticker = context.args[0].upper()
    price = int(context.args[1])
    qty = int(context.args[2])
    commission = int(context.args[3]) if len(context.args) >= 4 else 0

    # seq = next seq for this user (simple: count+1)
    existing = trade_repo.list_trades(user_id)
    seq = len(existing) + 1

    trade = {
        "tradeId": str(uuid.uuid4()),
        "userId": user_id,
        "seq": seq,
        "ticker": ticker,
        "side": "BUY",
        "price": price,
        "qty": qty,
        "commission": commission,
        "orderDate": datetime.utcnow(),
    }
    trade_repo.add_trade(trade)
    await update.message.reply_text(f"BUY saved ✅ seq={seq} {ticker} price={price} qty={qty} comm={commission}")

async def sell_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /sell ABC 7400 100 [commission]")
        return
    user_id = _user_id(update)
    ticker = context.args[0].upper()
    price = int(context.args[1])
    qty = int(context.args[2])
    commission = int(context.args[3]) if len(context.args) >= 4 else 0

    existing = trade_repo.list_trades(user_id)
    seq = len(existing) + 1

    sell_trade = {
        "tradeId": str(uuid.uuid4()),
        "userId": user_id,
        "seq": seq,
        "ticker": ticker,
        "side": "SELL",
        "price": price,
        "qty": qty,
        "commission": commission,
        "orderDate": datetime.utcnow(),
    }
    trade_repo.add_trade(sell_trade)

    try:
        allocs = fifo.match_sell_fifo(sell_trade)
        realised = sum(int(a["realisedPnl"]) for a in allocs)
        lines = [f"SELL saved ✅ seq={seq} {ticker} price={price} qty={qty} comm={commission}",
                 f"FIFO matched. Realised P/L: {realised} riel",
                 "Allocations:"]
        for a in allocs:
            lines.append(f"- buySeq? {a['buyTradeId'][-6:]} qty={a['qtyAllocated']} pnl={a['realisedPnl']}")
        await update.message.reply_text("\n".join(lines))
    except Exception as e:
        await update.message.reply_text(f"SELL saved but FIFO match failed ❌\nReason: {e}")

async def position_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 1:
        await update.message.reply_text("Usage: /position ABC")
        return
    user_id = _user_id(update)
    ticker = context.args[0].upper()
    pos = portfolio.position_detail(user_id, ticker)

    lines = [
        f"{ticker} Position",
        f"Bought: {pos['totalBoughtQty']} | Sold: {pos['totalSoldQty']} | Remaining: {pos['remainingQty']}",
        f"Sold: {pos['soldPercent']:.2f}%"
    ]
    if pos["remainingLots"]:
        lines.append("Open lots (FIFO):")
        for l in pos["remainingLots"]:
            lines.append(f"- seq={l['seq']} price={l['price']} openQty={l['qtyOpen']}")
    await update.message.reply_text("\n".join(lines))

async def portfolio_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = _user_id(update)
    rows = portfolio.portfolio(user_id)
    if not rows:
        await update.message.reply_text("No trades yet.")
        return

    lines = ["Portfolio"]
    for r in rows:
        lines.append(
            f"- {r['ticker']} last={r['lastPrice']} rem={r['remainingQty']} "
            f"R={r['realisedPnl']} U={r['unrealisedPnl']} T={r['totalPnl']}"
        )
    await update.message.reply_text("\n".join(lines))

async def top_orders_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = _user_id(update)
    ranked = portfolio.top_profitable_buy_orders(user_id, limit=5)
    if not ranked:
        await update.message.reply_text("No realised profit yet (need SELL trades).")
        return
    lines = ["Top profitable BUY orders (FIFO realised):"]
    for r in ranked:
        lines.append(f"- seq={r.get('seq')} {r.get('ticker')} pnl={r['realisedPnl']}")
    await update.message.reply_text("\n".join(lines))

async def top_tickers_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = _user_id(update)
    ranked = portfolio.top_profitable_tickers(user_id, limit=5)
    if not ranked:
        await update.message.reply_text("No realised profit yet (need SELL trades).")
        return
    lines = ["Top profitable tickers (realised):"]
    for r in ranked:
        lines.append(f"- {r['ticker']}: {r['realisedPnl']}")
    await update.message.reply_text("\n".join(lines))

def build_app() -> Application:
    app = Application.builder().token(settings.telegram_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("price", price_cmd))
    app.add_handler(CommandHandler("buy", buy_cmd))
    app.add_handler(CommandHandler("sell", sell_cmd))
    app.add_handler(CommandHandler("position", position_cmd))
    app.add_handler(CommandHandler("portfolio", portfolio_cmd))
    app.add_handler(CommandHandler("top_orders", top_orders_cmd))
    app.add_handler(CommandHandler("top_tickers", top_tickers_cmd))
    return app

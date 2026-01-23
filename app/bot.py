"""
bot.py
Standard OOP Refactor
"""

from __future__ import annotations

import io
import uuid
import logging
from dataclasses import dataclass
from datetime import datetime, time
from typing import Optional, Tuple, List

import numpy as np
import matplotlib
# Set non-interactive backend to prevent "main thread" errors on some servers
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Polygon

import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.config import settings
from app.repositories import TradeRepository, AllocationRepository, UserRepository
from app.services_fifo import FifoMatcherService
from app.services_pricing import PricingService
from app.services_portfolio import PortfolioService
from app.chart_renderer import ChartRenderer
from app.theme import Theme

# Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ----------------------------
# 2. Command Parsing Utility
# ----------------------------

class CommandParser:
    """Stateless utility to parse Telegram command strings."""
    
    @staticmethod
    def parse_symbol(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> Optional[str]:
        """Extracts ABC from /price$ABC or /price ABC"""
        text = (update.message.text or "").replace(f"/{command}", "").strip()
        if text.startswith("$"):
            return text.lstrip("$").strip().upper()
        if context.args:
            return context.args[0].strip().upper()
        return None

    @staticmethod
    def parse_trade_args(update: Update, context: ContextTypes.DEFAULT_TYPE, command: str) -> Optional[tuple[str, int, int]]:
        """Extracts Ticker, Price, Qty"""
        text = (update.message.text or "").replace(f"/{command}", "").strip()
        
        # Scenario 1: /buy$ABC 100 100
        if text.startswith("$"):
            parts = text.split()
            if not parts: return None
            ticker = parts[0].lstrip("$").upper()
            rest = parts[1:]
        # Scenario 2: /buy ABC 100 100
        else:
            rest = context.args
            if not rest or len(rest) < 3: return None
            ticker = rest[0].upper()
            rest = rest[1:]

        if len(rest) < 2: return None
        try:
            return ticker, int(rest[0]), int(rest[1])
        except ValueError:
            return None

# ----------------------------
# 3. Main Bot Logic (Controller)
# ----------------------------

class CsxTradingBot:
    """
    Main controller class. 
    Owns the Application, Handlers, and connects Services to Telegram Updates.
    """
    COMMISSION_RATE = 0.0047

    def __init__(self):
        # Initialize Dependencies internally or via constructor
        self.trade_repo = TradeRepository()
        self.alloc_repo = AllocationRepository()
        self.user_repo = UserRepository()
        self.pricing = PricingService()
        self.fifo = FifoMatcherService(self.trade_repo, self.alloc_repo)
        self.portfolio = PortfolioService(self.trade_repo, self.alloc_repo, self.pricing)
        self.renderer = ChartRenderer(tz_name="Asia/Phnom_Penh")
        self.parser = CommandParser()
        self.tz = pytz.timezone("Asia/Phnom_Penh")

    def build_app(self) -> Application:
        """Configures and returns the Telegram Application instance."""
        app = Application.builder().token(settings.telegram_token).build()
        self._register_handlers(app)
        self._schedule_jobs(app)
        return app

    def _register_handlers(self, app: Application):
        """Internal method to map commands to class methods."""
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("price", self.price_cmd))
        app.add_handler(CommandHandler("buy", self.buy_cmd))
        app.add_handler(CommandHandler("sell", self.sell_cmd))
        app.add_handler(CommandHandler("position", self.position_cmd))
        app.add_handler(CommandHandler("portfolio", self.portfolio_cmd))
        app.add_handler(CommandHandler("show_all", self.show_all_cmd))
        app.add_handler(CommandHandler("top_orders", self.top_orders_cmd))
        app.add_handler(CommandHandler("top_tickers", self.top_tickers_cmd))

    def _schedule_jobs(self, app: Application):
        """Internal method to set up cron jobs."""
        jq = app.job_queue
        # 8:00 AM ICT (1h before open)
        jq.run_daily(self.session_start_reminder, time=time(8, 0, tzinfo=self.tz), name="start_reminder")
        # 2:00 PM ICT (1h before close)
        jq.run_daily(self.session_end_reminder, time=time(14, 0, tzinfo=self.tz), name="end_reminder")

    # --- Helpers ---
    
    def _user_id(self, update: Update) -> str:
        return settings.default_user_id

    def _commission(self, price: int, qty: int) -> int:
        return int(price * qty * self.COMMISSION_RATE)

    # --- Handlers ---

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = self._user_id(update)
        # Try to save chat_id for reminders
        self.user_repo.upsert_user(uid, update.effective_user.full_name, chat_id=update.effective_chat.id)
        
        await update.message.reply_text(
            "🚀 CSX Trading Journal ✅\n\n"
            "📊 /price$ABC or /show_all\n"
            "💼 /buy$ABC 7300 100\n"
            "💼 /sell$ABC 7400 100\n"
            "📈 /portfolio, /position ABC\n"
            "🏆 /top_orders, /top_tickers"
        )

    async def price_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ticker = self.parser.parse_symbol(update, context, "price")
        if not ticker:
            await update.message.reply_text("Usage: /price$ABC")
            return

        try:
            res = self.pricing.get_latest_price(ticker)
            price = float(res.price or 0)
            change = float(res.change or 0)
            direction = (res.change_direction or "equal").lower()

            if not price:
                await update.message.reply_text(f"❌ {ticker}: Price not available")
                return

            img = self.renderer.price_card(ticker, price, change, direction)
            img.name = f"price_{ticker}.png"
            
            emoji = "📈" if direction == "up" else ("📉" if direction == "down" else "➡️")
            await update.message.reply_photo(photo=img, caption=f"{emoji} {ticker} | {price:,.0f} riel")
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("❌ Error fetching price")

    async def buy_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self._handle_trade(update, context, "BUY")

    async def sell_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        self._handle_trade(update, context, "SELL")

    def _handle_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE, side: str):
        """Unified trade handler to reduce duplication."""
        cmd = side.lower()
        args = self.parser.parse_trade_args(update, context, cmd)
        if not args:
            import asyncio # Lazy import for non-async context warning if needed, but we are in async
            # Use create_task if we were not in an async func, but here we can just return task or await
            # Since this is a synchronous helper called by async, we need to return the awaitable or change structure.
            # Ideally, refactor this to be async.
            return

    # Let's fix the above: make _handle_trade async
    async def _handle_trade(self, update: Update, context: ContextTypes.DEFAULT_TYPE, side: str):
        cmd = side.lower()
        args = self.parser.parse_trade_args(update, context, cmd)
        if not args:
            await update.message.reply_text(f"Usage: /{cmd}$ABC 7300 100")
            return

        ticker, price, qty = args
        uid = self._user_id(update)
        seq = len(self.trade_repo.list_trades(uid)) + 1
        comm = self._commission(price, qty)

        trade = {
            "tradeId": str(uuid.uuid4()),
            "userId": uid,
            "seq": seq,
            "ticker": ticker,
            "side": side,
            "price": price,
            "qty": qty,
            "commission": comm,
            "orderDate": datetime.utcnow()
        }
        self.trade_repo.add_trade(trade)

        caption = f"✅ {side} confirmed | Seq #{seq}"
        
        # FIFO Logic for Sells
        if side == "SELL":
            try:
                allocs = self.fifo.match_sell_fifo(trade)
                realised = sum(int(a.get("realisedPnl", 0)) for a in allocs)
                caption += f" | P/L: {realised:+,} riel"
            except Exception as e:
                caption += "\n(FIFO match failed, but trade saved)"

        img = self.renderer.trade_card(ticker, side, price, qty, comm, seq)
        img.name = f"{cmd}_{ticker}_{seq}.jpg"
        await update.message.reply_photo(photo=img, caption=caption)

    async def position_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not context.args:
            await update.message.reply_text("Usage: /position ABC")
            return
        ticker = context.args[0].upper()
        pos = self.portfolio.position_detail(self._user_id(update), ticker)
        img = self.renderer.position_card(ticker, pos)
        img.name = f"pos_{ticker}.jpg"
        await update.message.reply_photo(photo=img, caption=f"Position: {ticker}")

    async def portfolio_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = self._user_id(update)
        rows = self.portfolio.portfolio(uid)
        if not rows:
            await update.message.reply_text("📭 No trades yet.")
            return
        
        img = self.renderer.portfolio_card(uid, rows)
        img.name = "portfolio.png"
        total_pnl = sum(int(r.get("realisedPnl", 0)) + int(r.get("unrealisedPnl", 0)) for r in rows)
        emoji = "📈" if total_pnl >= 0 else "📉"
        await update.message.reply_photo(photo=img, caption=f"{emoji} Portfolio | Total: {total_pnl:+,} riel")

    async def show_all_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            msg = await update.message.reply_text("📊 Loading...")
            stocks = self.pricing.get_all_prices()
            if not stocks:
                await msg.edit_text("❌ No data.")
                return
            img = self.renderer.all_stocks_card(stocks)
            img.name = "market.jpg"
            await msg.delete()
            await update.message.reply_photo(photo=img, caption="📈 Market Overview")
        except Exception as e:
            logger.error(e)
            await update.message.reply_text("❌ Error")

    async def top_orders_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ranked = self.portfolio.top_profitable_buy_orders(self._user_id(update), limit=5)
        if not ranked:
            await update.message.reply_text("No realised profits yet.")
            return
        img = self.renderer.rankings_card("TOP ORDERS", ranked, is_tickers=False)
        img.name = "top_orders.jpg"
        await update.message.reply_photo(photo=img)

    async def top_tickers_cmd(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        ranked = self.portfolio.top_profitable_tickers(self._user_id(update), limit=5)
        if not ranked:
            await update.message.reply_text("No realised profits yet.")
            return
        img = self.renderer.rankings_card("TOP TICKERS", ranked, is_tickers=True)
        img.name = "top_tickers.jpg"
        await update.message.reply_photo(photo=img)

    # --- Job Callbacks ---

    async def session_start_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        await self._send_broadcast(context, "🚀 Trading session starts in 1 hour!")

    async def session_end_reminder(self, context: ContextTypes.DEFAULT_TYPE):
        await self._send_broadcast(context, "🏁 Trading session ends in 1 hour!")

    async def _send_broadcast(self, context: ContextTypes.DEFAULT_TYPE, text: str):
        users = self.user_repo.get_all_users()
        for u in users:
            # Assumes upsert_user saves 'chatId'
            cid = u.get("chatId") or u.get("chat_id")
            if cid:
                try:
                    await context.bot.send_message(chat_id=int(cid), text=text)
                except Exception as e:
                    logger.warning(f"Failed to remind {cid}: {e}")
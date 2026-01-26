"""
main.py
Entry point for the CSX Trading Bot.
"""

import sys
import os
import asyncio
import logging
from contextlib import suppress
from aiohttp import web
from telegram import Update
from app.bot import CsxTradingBot  # Import the class

# Configure global logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def print_startup_banner():
    """Print a friendly startup banner to console."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          🚀 CSX TRADING JOURNAL BOT STARTING 🚀              ║
║                                                              ║
║  Commands:                                                   ║
║  • /start               - Show welcome & commands            ║
║  • /price$ABC           - Get stock price card 📊            ║
║  • /show_all            - View all stock prices 📈           ║
║  • /buy$ABC 7300 100    - Record a BUY trade ✅              ║
║  • /sell$ABC 7400 100   - Record a SELL trade ✅             ║
║  • /position ABC        - View position details 📍           ║
║  • /portfolio           - View portfolio dashboard 💼        ║
║                                                              ║
║  Status: ✅ Polling active...                                ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)
    sys.stdout.flush()

async def _start_health_server(port: int) -> web.AppRunner:
    """Start a minimal HTTP server for Cloud Run health checks."""
    app = web.Application()

    async def _health(_: web.Request) -> web.Response:  # pragma: no cover
        return web.Response(text="OK", status=200)

    app.router.add_get("/", _health)
    app.router.add_get("/healthz", _health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    return runner


async def _run_bot_with_healthcheck() -> None:
    """Run Telegram polling and a health endpoint in parallel."""
    print_startup_banner()

    port = int(os.getenv("PORT", "8080"))

    # Build bot
    bot_controller = CsxTradingBot()
    application = bot_controller.build_app()

    health_runner: web.AppRunner | None = None
    try:
        # Start health server first so Cloud Run sees the port
        health_runner = await _start_health_server(port)
        logger.info("Health endpoint started on port %s", port)

        async with application:
            await application.initialize()
            await application.start()
            await application.updater.start_polling(
                allowed_updates=Update.ALL_TYPES
            )

            logger.info("Bot polling started; ready for requests")

            # Keep running until cancelled
            while True:
                await asyncio.sleep(3600)
    except asyncio.CancelledError:
        logger.info("Shutdown requested, stopping bot...")
    except Exception as exc:  # pragma: no cover
        logger.critical("Fatal error starting bot: %s", exc, exc_info=True)
        raise
    finally:
        with suppress(Exception):
            if application.updater.running:
                await application.updater.stop()
            await application.stop()
            await application.shutdown()
        with suppress(Exception):
            if health_runner:
                await health_runner.cleanup()


def main() -> None:
    try:
        asyncio.run(_run_bot_with_healthcheck())
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
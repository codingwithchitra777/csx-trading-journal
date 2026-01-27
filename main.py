import sys
import os
import asyncio
import logging
from contextlib import suppress
from aiohttp import web

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def print_startup_banner():
    banner = """
╔══════════════════════════════════════════════════════════════╗
║          🚀 CSX TRADING JOURNAL BOT STARTING 🚀              ║
║  Status: ✅ Booting...                                       ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)
    sys.stdout.flush()


async def _start_health_server(port: int) -> web.AppRunner:
    app = web.Application()

    async def _health(_: web.Request) -> web.Response:
        return web.Response(text="OK", status=200)

    app.router.add_get("/", _health)
    app.router.add_get("/healthz", _health)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info("Health endpoint started on port %s", port)
    return runner


async def _run() -> None:
    print_startup_banner()
    port = int(os.getenv("PORT", "8080"))

    # Start health server ASAP so Cloud Run sees the port
    health_runner = await _start_health_server(port)

    # Import AFTER health server is up (prevents probe failures if bot init is slow)
    from telegram import Update
    from app.bot import CsxTradingBot

    bot_controller = CsxTradingBot()
    application = bot_controller.build_app()

    try:
        async with application:
            await application.initialize()
            await application.start()

            # start_polling exists only if updater is configured.
            # If this errors, switch to application.run_polling() in a non-async main.
            await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

            logger.info("Bot polling started; ready for requests")

            while True:
                await asyncio.sleep(3600)

    except asyncio.CancelledError:
        logger.info("Shutdown requested...")
    finally:
        with suppress(Exception):
            if getattr(application, "updater", None) and application.updater.running:
                await application.updater.stop()
            await application.stop()
            await application.shutdown()
        with suppress(Exception):
            await health_runner.cleanup()


def main() -> None:
    try:
        asyncio.run(_run())
    except Exception:
        logger.exception("Fatal startup error")
        sys.exit(1)


if __name__ == "__main__":
    main()

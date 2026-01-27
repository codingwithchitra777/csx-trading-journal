import sys
import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from app.bot import CsxTradingBot  # Ensure this path is correct

# Configure logging to be visible in Google Cloud Logs
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def health_check(request):
    """Simple 200 OK for Cloud Run health probes."""
    return web.Response(text="Bot is alive", status=200)

async def run_bot():
    """Main entry point to run the bot and health server."""
    port = int(os.getenv("PORT", "8080"))
    
    # 1. Setup the Web Health Server
    app = web.Application()
    app.router.add_get("/", health_check)
    app.router.add_get("/healthz", health_check)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    
    # 2. Build the Telegram Application
    try:
        bot_controller = CsxTradingBot()
        application = bot_controller.build_app()
    except Exception as e:
        logger.critical(f"Failed to build bot application: {e}", exc_info=True)
        sys.exit(1)

    # 3. Start everything
    await site.start()
    logger.info(f"✅ Health server started on port {port}")

    async with application:
        try:
            await application.initialize()
            await application.start()
            
            # Start polling in the background
            await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
            logger.info("🚀 Bot polling active and healthy.")

            # Keep the loop running
            while True:
                await asyncio.sleep(3600)
                
        except Exception as e:
            logger.error(f"Fatal error during bot execution: {e}", exc_info=True)
        finally:
            # Graceful shutdown
            if application.updater.running:
                await application.updater.stop()
            await application.stop()
            await application.shutdown()
            await runner.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(run_bot())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.critical(f"Unhandled Exception: {e}", exc_info=True)
        sys.exit(1)

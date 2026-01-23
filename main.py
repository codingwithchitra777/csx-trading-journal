"""
main.py
Entry point for the CSX Trading Bot.
"""

import sys
import logging
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

def main():
    print_startup_banner()
    
    try:
        # 1. Instantiate the Bot Controller
        # (Dependencies are initialized inside the class)
        bot_controller = CsxTradingBot()
        
        # 2. Build the Telegram Application
        application = bot_controller.build_app()
        
        # 3. Start Polling
        logger.info("Bot is running...")
        application.run_polling()
        
    except Exception as e:
        logger.critical(f"Fatal error starting bot: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
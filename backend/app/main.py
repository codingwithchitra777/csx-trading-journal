import os
import sys
import logging
import threading
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from telegram import Update

from app.services.bot import CsxTradingBot
from app.api.v1.api import api_router

logger = logging.getLogger(__name__)

# Configure headless rendering for Matplotlib immediately
import matplotlib
matplotlib.use('Agg')

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Spawn Telegram Bot thread
    bot_thread = threading.Thread(target=run_telegram_bot, daemon=True)
    bot_thread.start()
    yield

def run_telegram_bot():
    logger.info("Starting Telegram Bot thread...")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    bot_controller = CsxTradingBot()
    application = bot_controller.build_app()
    
    async def start_polling():
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        logger.info("Telegram Bot polling active.")
        while True:
            await asyncio.sleep(3600)
            
    try:
        loop.run_until_complete(start_polling())
    except asyncio.CancelledError:
        logger.info("Telegram Bot thread cancelled")
    except Exception as e:
        logger.error(f"Fatal error in Telegram Bot thread: {e}", exc_info=True)
    finally:
        try:
            loop.run_until_complete(application.stop())
            loop.run_until_complete(application.shutdown())
        except Exception:
            pass
        loop.close()
        logger.info("Telegram Bot thread shutdown complete")

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

app = FastAPI(
    title="CSX Trading Journal API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include unified API router
app.include_router(api_router, prefix="/api")

# Base health check
@app.get("/api/healthz")
async def health_check():
    return {"status": "healthy", "service": "csx-trading-journal-backend"}

# Serve static assets (JS, CSS, images) from frontend/dist/frontend/browser/
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist", "frontend", "browser"))
if os.path.exists(frontend_dir):
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse
    
    # Mount browser build directory
    app.mount("/assets", StaticFiles(directory=frontend_dir), name="assets")
    
    # Catch-all route to serve Angular's index.html for client-side routing
    @app.get("/{catchall:path}")
    async def serve_spa(catchall: str):
        if catchall.startswith("api/"):
            return {"detail": "Not Found"}
        
        # Check if requested file exists locally in the build directory
        file_path = os.path.join(frontend_dir, catchall)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        # Otherwise, serve index.html for Angular routing
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"detail": "Frontend files not found"}
else:
    @app.get("/")
    async def root_fallback():
        return {"message": "CSX Trading Journal API is active. Frontend build directory not found."}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)

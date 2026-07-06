"""
backend/main.py
FastAPI Server Entry Point.
"""

import os
import sys
import logging

# Must be set before matplotlib is imported anywhere (app.services.bot does this
# at module load time) - containers with a non-root user may have no resolvable
# HOME, which makes matplotlib's config-dir lookup crash the whole process.
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

# Add parent directory to sys.path so app can be imported properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import app

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8080"))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=False)
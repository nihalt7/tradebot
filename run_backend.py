import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting TradePulse AI Quant Platform Backend on port {port}...")
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=port, reload=False)

import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# --- Market data ---

CANDLES_PER_REQUEST = int(os.getenv('CANDLES_PER_REQUEST') or '')
MARKET_DATA_HOST = os.getenv('MARKET_DATA_HOST')
MATCHER_HOST = os.getenv('MATCHER_HOST')

# --- Simulator ---

PRICE_SHIFT = float(os.getenv('PRICE_SHIFT') or '')

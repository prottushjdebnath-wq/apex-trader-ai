from dotenv import load_dotenv
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# ==========================================
# BYBIT
# ==========================================

BYBIT_API_KEY = os.getenv("BYBIT_API_KEY", "")
BYBIT_API_SECRET = os.getenv("BYBIT_API_SECRET", "")

# ==========================================
# HYPERLIQUID
# ==========================================

HYPERLIQUID_API_KEY = os.getenv("HYPERLIQUID_API_KEY", "")
HYPERLIQUID_API_SECRET = os.getenv("HYPERLIQUID_API_SECRET", "")

# ==========================================
# TELEGRAM
# ==========================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")

# ==========================================
# RISK SETTINGS
# ==========================================

RISK_PERCENT = float(os.getenv("RISK_PERCENT", "2"))
DEFAULT_LEVERAGE = int(os.getenv("DEFAULT_LEVERAGE", "5"))
MAX_OPEN_TRADES = int(os.getenv("MAX_OPEN_TRADES", "5"))

# ==========================================
# SCANNER SETTINGS
# ==========================================

TIMEFRAME = os.getenv("TIMEFRAME", "5m")
MIN_RVOL = float(os.getenv("MIN_RVOL", "2.0"))
MIN_SCORE = int(os.getenv("MIN_SCORE", "70"))
TOP_SYMBOLS = int(os.getenv("TOP_SYMBOLS", "50"))

# ==========================================
# PAPER TRADING
# ==========================================

PAPER_START_BALANCE = float(
    os.getenv("PAPER_START_BALANCE", "1000")
)

# ==========================================
# DATABASE
# ==========================================

FUTURES_OI_CONFIRM_THRESHOLD_PCT = float(os.getenv("FUTURES_OI_CONFIRM_THRESHOLD_PCT", "3.0"))

DATABASE_PATH = str(
    BASE_DIR / "database" / "apex_trader.db"
)

# ==========================================
# DEBUG
# ==========================================

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
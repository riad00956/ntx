import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "").split(",") if id.strip()]

# Default settings (will be stored in DB)
DEFAULT_SETTINGS = {
    "money_to_falling": "100",      # 100 BDT = 1 Falling Star
    "falling_to_stellar": "4",      # 4 Falling Stars = 1 Stellar Star
    "export_enabled": "1",
    "export_min_stars": "2",
    "export_max_stars": "10",
    "reviews_auto_approve": "0",    # 0 = admin approval needed
}
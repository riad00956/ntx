from telegram import ReplyKeyboardMarkup, KeyboardButton

def main_menu_keyboard():
    buttons = [
        [KeyboardButton("🛍️ Shop"), KeyboardButton("🌟 My Stars")],
        [KeyboardButton("📤 Export"), KeyboardButton("⭐ Reviews")],
        [KeyboardButton("👤 Profile")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def shop_keyboard():
    buttons = [
        [KeyboardButton("🎬 Netflix"), KeyboardButton("🎵 Spotify")],
        [KeyboardButton("🔐 VPN"), KeyboardButton("🎬 Disney+ Hotstar")],
        [KeyboardButton("📹 YouTube"), KeyboardButton("🎬 Amazon Prime")],
        [KeyboardButton("🎬 Hulu"), KeyboardButton("💻 Office 365")],
        [KeyboardButton("🔙 Back")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def back_keyboard():
    return ReplyKeyboardMarkup([[KeyboardButton("🔙 Back")]], resize_keyboard=True)

def stars_menu_keyboard():
    buttons = [
        [KeyboardButton("🔄 Convert to Stellar")],
        [KeyboardButton("🛍️ Redeem Products")],
        [KeyboardButton("🔙 Back")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def redeem_products_keyboard(products):
    buttons = []
    for p in products:
        name = p[1]  # product name
        icon = p[2] if p[2] else ""
        buttons.append([KeyboardButton(f"{icon} {name}")])
    buttons.append([KeyboardButton("🔙 Back")])
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def review_menu_keyboard():
    buttons = [
        [KeyboardButton("1️⃣ Give Review")],
        [KeyboardButton("2️⃣ View Reviews")],
        [KeyboardButton("🔙 Back")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def admin_main_keyboard():
    buttons = [
        [KeyboardButton("📦 Products"), KeyboardButton("🌟 Star System")],
        [KeyboardButton("📝 Reviews"), KeyboardButton("📤 Export Control")],
        [KeyboardButton("💰 Revenue"), KeyboardButton("⚙️ Settings")],
        [KeyboardButton("👤 Users"), KeyboardButton("📢 Broadcast")],
        [KeyboardButton("📦 Orders Pending")],
        [KeyboardButton("🔙 Back to User")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)
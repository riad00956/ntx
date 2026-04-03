from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode
import database as db
import keyboards as kb
from states import *
from config import ADMIN_IDS
import re

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db.register_user(user.id, user.username, user.first_name)
    welcome_text = (
        "✨ Welcome to Premium Hub! 🛍️\n"
        "Buy subscriptions\n"
        "Earn stars 🌟\n"
        "Use stars for free products or export\n\n"
        "👇 Choose an option"
    )
    await update.message.reply_text(welcome_text, reply_markup=kb.main_menu_keyboard())

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    if text == "🛍️ Shop":
        await show_shop(update, context)
    elif text == "🌟 My Stars":
        await show_stars(update, context)
    elif text == "📤 Export":
        # Start export conversation
        await start_export(update, context)
    elif text == "⭐ Reviews":
        await review_menu(update, context)
    elif text == "👤 Profile":
        await show_profile(update, context)
    elif text == "🔙 Back":
        await update.message.reply_text("Main Menu", reply_markup=kb.main_menu_keyboard())
    else:
        # Check if it's a product selection from shop
        products = db.get_all_products(active_only=True)
        for prod in products:
            prod_name = prod[1]
            icon = prod[2] if prod[2] else ""
            if text == f"{icon} {prod_name}" or text == prod_name:
                await show_product_details(update, context, prod[0])
                return
        # If none matched, show main menu
        await update.message.reply_text("Please use the buttons below.", reply_markup=kb.main_menu_keyboard())

async def show_shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛍️ Choose a product:", reply_markup=kb.shop_keyboard())

async def show_product_details(update: Update, context: ContextTypes.DEFAULT_TYPE, product_id: int):
    prod = db.get_product(product_id)
    if not prod:
        await update.message.reply_text("Product not found.")
        return
    name, icon, price, validity, star_earn, desc, active, rating, review_cnt = prod[1], prod[2], prod[3], prod[4], prod[5], prod[6], prod[7], prod[8], prod[9]
    rating_text = f"⭐ Rating: {rating} ({review_cnt} Reviews)" if review_cnt > 0 else "⭐ No reviews yet"
    text = (
        f"{icon} {name}\n"
        f"💰 Price: {price}৳\n"
        f"⏳ Validity: {validity} Days\n"
        f"🌠 Earn: +{star_earn} Star\n"
        f"{rating_text}\n"
        f"📝 Description: {desc}\n\n"
    )
    context.user_data['buy_product_id'] = product_id
    await update.message.reply_text(text, reply_markup=kb.buy_keyboard())

async def product_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🛒 Buy Now":
        return await buy_start(update, context)
    elif text == "🔙 Back":
        await show_shop(update, context)
        return ConversationHandler.END
    else:
        await update.message.reply_text("Use buttons.")
        return ConversationHandler.END

# Buy conversation handlers
async def buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📧 Enter your email:\n⚠️ Use a temporary/non-personal email", reply_markup=kb.back_keyboard())
    return WAITING_EMAIL

async def buy_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await update.message.reply_text("Purchase cancelled.", reply_markup=kb.main_menu_keyboard())
        return ConversationHandler.END
    context.user_data['buy_email'] = update.message.text
    await update.message.reply_text("🔐 Enter password:", reply_markup=kb.back_keyboard())
    return WAITING_PASSWORD

async def buy_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await update.message.reply_text("Purchase cancelled.", reply_markup=kb.main_menu_keyboard())
        return ConversationHandler.END
    context.user_data['buy_password'] = update.message.text
    prod_id = context.user_data.get('buy_product_id')
    prod = db.get_product(prod_id)
    price = prod[3]
    instructions = (
        f"💳 Please send payment to:\n"
        f"bKash/Nagad: 01XXXXXXXXX\n"
        f"Amount: {price}৳\n\n"
        f"After payment, send the transaction ID or screenshot here."
    )
    await update.message.reply_text(instructions, reply_markup=ReplyKeyboardMarkup([["✅ I have paid", "🔙 Back"]], resize_keyboard=True))
    return WAITING_PAYMENT_PROOF

async def buy_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await update.message.reply_text("Purchase cancelled.", reply_markup=kb.main_menu_keyboard())
        return ConversationHandler.END
    proof = update.message.text
    user_id = update.effective_user.id
    prod_id = context.user_data['buy_product_id']
    email = context.user_data['buy_email']
    password = context.user_data['buy_password']
    order_id = db.add_order(user_id, prod_id, email, password, proof)
    
    prod = db.get_product(prod_id)
    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_message(admin_id, f"🆕 New Order #{order_id}\nUser: {user_id}\nProduct: {prod[1]}\nStatus: Pending approval.\nUse /admin to manage.")
        except:
            pass
    
    await update.message.reply_text("⏳ Processing your order...\n✅ Order placed! Admin will approve soon. You will receive stars upon approval.", reply_markup=kb.main_menu_keyboard())
    return ConversationHandler.END

# Stars menu
async def show_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db.get_user(update.effective_user.id)
    falling = user[3]
    stellar = user[4]
    text = f"👤 Your Stars\n🌠 Falling Stars: {falling}\n🌟 Stellar Stars: {stellar}\n\nConvert {db.get_setting('falling_to_stellar')} Falling → 1 Stellar"
    await update.message.reply_text(text, reply_markup=kb.stars_menu_keyboard())

async def stars_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    if text == "🔄 Convert to Stellar":
        rate = int(db.get_setting("falling_to_stellar"))
        user = db.get_user(user_id)
        falling = user[3]
        if falling >= rate:
            amount = falling // rate
            db.convert_falling_to_stellar(user_id, amount)
            await update.message.reply_text(f"✅ Converted {amount*rate} Falling Stars to {amount} Stellar Stars!")
        else:
            await update.message.reply_text(f"❌ You need at least {rate} Falling Stars to convert.")
        await show_stars(update, context)
    elif text == "🛍️ Redeem Products":
        await show_redeem_products(update, context)
    elif text == "🔙 Back":
        await update.message.reply_text("Main Menu", reply_markup=kb.main_menu_keyboard())
    else:
        await update.message.reply_text("Use buttons.", reply_markup=kb.stars_menu_keyboard())

async def show_redeem_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = db.get_all_products(active_only=True)
    text = "🌟 Redeem Products (1 Stellar Star each):\n"
    for p in products:
        text += f"{p[2]} {p[1]} — 1 🌟\n"
    await update.message.reply_text(text, reply_markup=kb.redeem_products_keyboard(products))

async def redeem_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🔙 Back":
        await show_stars(update, context)
        return
    products = db.get_all_products(active_only=True)
    selected = None
    for p in products:
        if text == f"{p[2]} {p[1]}" or text == p[1]:
            selected = p
            break
    if not selected:
        await update.message.reply_text("Invalid product.")
        return
    user_id = update.effective_user.id
    user = db.get_user(user_id)
    stellar = user[4]
    if stellar >= 1:
        db.update_user_stars(user_id, stellar_delta=-1)
        await update.message.reply_text(f"✅ Redeemed Successfully! {selected[1]} credentials will be sent shortly.")
        await update.message.reply_text(f"🔐 Here is your {selected[1]} login:\nEmail: temp@example.com\nPass: redeem123")
    else:
        await update.message.reply_text("❌ You don't have enough Stellar Stars.")
    await show_stars(update, context)

# Export flow
async def start_export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    export_enabled = int(db.get_setting("export_enabled"))
    if not export_enabled:
        await update.message.reply_text("Export system is currently disabled.")
        return
    await update.message.reply_text("📢 Send your public channel post link:", reply_markup=kb.back_keyboard())
    return EXPORT_POST_LINK

async def export_post_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await update.message.reply_text("Export cancelled.", reply_markup=kb.main_menu_keyboard())
        return ConversationHandler.END
    link = update.message.text
    if not re.match(r"https?://t\.me/", link):
        await update.message.reply_text("Please send a valid Telegram post link (t.me/...).")
        return EXPORT_POST_LINK
    context.user_data['export_link'] = link
    min_stars = int(db.get_setting("export_min_stars"))
    max_stars = int(db.get_setting("export_max_stars"))
    buttons = [[str(i) for i in range(min_stars, max_stars+1)], ["🔙 Back"]]
    await update.message.reply_text(f"Select stars to export (min {min_stars}, max {max_stars}):", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
    return EXPORT_SELECT_STARS

async def export_select_stars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await update.message.reply_text("Export cancelled.", reply_markup=kb.main_menu_keyboard())
        return ConversationHandler.END
    try:
        stars = int(update.message.text)
        min_stars = int(db.get_setting("export_min_stars"))
        max_stars = int(db.get_setting("export_max_stars"))
        if stars < min_stars or stars > max_stars:
            await update.message.reply_text(f"Invalid amount. Choose between {min_stars} and {max_stars}.")
            return EXPORT_SELECT_STARS
        context.user_data['export_stars'] = stars
        await update.message.reply_text(f"Confirm export of {stars} Stellar Stars?\nPost link: {context.user_data['export_link']}", reply_markup=ReplyKeyboardMarkup([["✅ Yes", "❌ No"]], resize_keyboard=True))
        return EXPORT_CONFIRM
    except ValueError:
        await update.message.reply_text("Please send a number.")
        return EXPORT_SELECT_STARS

async def export_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ No":
        await update.message.reply_text("Export cancelled.", reply_markup=kb.main_menu_keyboard())
        return ConversationHandler.END
    elif text == "✅ Yes":
        user_id = update.effective_user.id
        stars = context.user_data['export_stars']
        link = context.user_data['export_link']
        user = db.get_user(user_id)
        if user[4] >= stars:
            req_id = db.add_export_request(user_id, link, stars)
            for admin_id in ADMIN_IDS:
                await context.bot.send_message(admin_id, f"📤 New Export Request #{req_id}\nUser: {user_id}\nStars: {stars}\nLink: {link}\nUse /admin to approve.")
            await update.message.reply_text("⏳ Request sent to Admin. You will be notified once approved.", reply_markup=kb.main_menu_keyboard())
        else:
            await update.message.reply_text("❌ You don't have enough Stellar Stars.")
        return ConversationHandler.END
    else:
        await update.message.reply_text("Please use Yes/No buttons.")
        return EXPORT_CONFIRM

# Reviews
async def review_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⭐ Reviews Menu:", reply_markup=kb.review_menu_keyboard())

async def review_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "1️⃣ Give Review":
        products = db.get_all_products(active_only=True)
        keyboard = [[f"{p[2]} {p[1]}"] for p in products]
        keyboard.append(["🔙 Back"])
        await update.message.reply_text("Select product:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return REVIEW_SELECT_PRODUCT
    elif text == "2️⃣ View Reviews":
        await view_reviews(update, context)
        return
    elif text == "🔙 Back":
        await update.message.reply_text("Main Menu", reply_markup=kb.main_menu_keyboard())
        return ConversationHandler.END
    else:
        await update.message.reply_text("Use buttons.")
        return

async def review_select_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await review_menu(update, context)
        return ConversationHandler.END
    product_text = update.message.text
    products = db.get_all_products(active_only=True)
    for p in products:
        if product_text == f"{p[2]} {p[1]}" or product_text == p[1]:
            context.user_data['review_product_id'] = p[0]
            await update.message.reply_text("Rate from 1 to 5 stars:", reply_markup=ReplyKeyboardMarkup([["1","2","3","4","5"], ["🔙 Back"]], resize_keyboard=True))
            return REVIEW_RATING
    await update.message.reply_text("Invalid product.")
    return REVIEW_SELECT_PRODUCT

async def review_rating(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await review_menu(update, context)
        return ConversationHandler.END
    try:
        rating = int(update.message.text)
        if rating < 1 or rating > 5:
            raise ValueError
        context.user_data['review_rating'] = rating
        await update.message.reply_text("Write your review comment:", reply_markup=kb.back_keyboard())
        return REVIEW_COMMENT
    except:
        await update.message.reply_text("Please send a number between 1 and 5.")
        return REVIEW_RATING

async def review_comment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "🔙 Back":
        await review_menu(update, context)
        return ConversationHandler.END
    comment = update.message.text
    user_id = update.effective_user.id
    product_id = context.user_data['review_product_id']
    rating = context.user_data['review_rating']
    db.add_review(user_id, product_id, rating, comment)
    auto_approve = int(db.get_setting("reviews_auto_approve"))
    if auto_approve:
        conn = db.get_db()
        c = conn.cursor()
        c.execute("SELECT id FROM reviews WHERE user_id = ? AND product_id = ? ORDER BY created_at DESC LIMIT 1", (user_id, product_id))
        rid = c.fetchone()[0]
        conn.close()
        db.approve_review(rid)
        await update.message.reply_text("✅ Review submitted and approved! Thanks for your feedback.", reply_markup=kb.main_menu_keyboard())
    else:
        await update.message.reply_text("✅ Review submitted! Awaiting admin approval.", reply_markup=kb.main_menu_keyboard())
        for admin_id in ADMIN_IDS:
            await context.bot.send_message(admin_id, f"⭐ New review from user {user_id}. Use /admin to approve.")
    return ConversationHandler.END

async def view_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = db.get_all_products(active_only=True)
    msg = ""
    for p in products:
        conn = db.get_db()
        c = conn.cursor()
        c.execute("SELECT rating, comment FROM reviews WHERE product_id = ? AND is_approved = 1 LIMIT 5", (p[0],))
        reviews = c.fetchall()
        conn.close()
        msg += f"\n{p[2]} {p[1]} Reviews:\n"
        if reviews:
            for r in reviews:
                msg += f"⭐ {r[0]} - {r[1]}\n"
        else:
            msg += "No reviews yet.\n"
    await update.message.reply_text(msg, reply_markup=kb.review_menu_keyboard())

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db.get_user(update.effective_user.id)
    text = f"👤 Profile\nID: {user[0]}\n🌠 Falling Stars: {user[3]}\n🌟 Stellar Stars: {user[4]}"
    await update.message.reply_text(text, reply_markup=kb.main_menu_keyboard())

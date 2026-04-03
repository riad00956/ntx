from telegram import Update
from telegram.ext import ContextTypes
import database as db
import keyboards as kb
from config import ADMIN_IDS

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("You are not authorized.")
        return
    # Dashboard stats
    revenue = db.get_total_revenue()
    pending_orders = len(db.get_pending_orders())
    pending_reviews = len(db.get_pending_reviews())
    pending_exports = len(db.get_pending_exports())
    users = db.get_all_users()
    total_falling = sum(u[2] for u in users)
    total_stellar = sum(u[3] for u in users)
    text = (
        f"📊 Admin Dashboard\n"
        f"💰 Total Revenue: {revenue}৳\n"
        f"🌠 Total Falling Stars: {total_falling}\n"
        f"🌟 Total Stellar Stars: {total_stellar}\n"
        f"📦 Orders Pending: {pending_orders}\n"
        f"⭐ Reviews Pending: {pending_reviews}\n"
        f"📤 Export Pending: {pending_exports}\n"
    )
    await update.message.reply_text(text, reply_markup=kb.admin_main_keyboard())

async def admin_handlers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("Unauthorized.")
        return
    text = update.message.text
    if text == "📦 Products":
        await manage_products(update, context)
    elif text == "🌟 Star System":
        await manage_star_system(update, context)
    elif text == "📝 Reviews":
        await manage_reviews(update, context)
    elif text == "📤 Export Control":
        await manage_exports(update, context)
    elif text == "💰 Revenue":
        await view_revenue(update, context)
    elif text == "⚙️ Settings":
        await manage_settings(update, context)
    elif text == "👤 Users":
        await manage_users(update, context)
    elif text == "📢 Broadcast":
        await broadcast_start(update, context)
    elif text == "📦 Orders Pending":
        await view_pending_orders(update, context)
    elif text == "🔙 Back to User":
        await update.message.reply_text("Back to user mode.", reply_markup=kb.main_menu_keyboard())
    else:
        await update.message.reply_text("Use admin menu buttons.")

async def manage_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    products = db.get_all_products(active_only=False)
    msg = "📦 Products List:\n"
    for p in products:
        msg += f"ID:{p[0]} {p[2]} {p[1]} - {p[3]}৳ Active:{p[7]}\n"
    msg += "\nCommands:\n/add_product\n/edit_product <id> <field> <value>\n/delete_product <id>\n/toggle_product <id>"
    await update.message.reply_text(msg)

async def manage_star_system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    money = db.get_setting("money_to_falling")
    falling_to_stellar = db.get_setting("falling_to_stellar")
    export_enabled = db.get_setting("export_enabled")
    min_stars = db.get_setting("export_min_stars")
    max_stars = db.get_setting("export_max_stars")
    text = (
        f"🌟 Star System Settings:\n"
        f"1 BDT → Falling: {money} BDT per Falling Star\n"
        f"Falling → Stellar: {falling_to_stellar} Falling = 1 Stellar\n"
        f"Export Enabled: {export_enabled}\n"
        f"Export Min Stars: {min_stars}\n"
        f"Export Max Stars: {max_stars}\n\n"
        f"Commands:\n/set money_to_falling <amount>\n/set falling_to_stellar <rate>\n/set export_enabled <0/1>\n/set export_min_stars <num>\n/set export_max_stars <num>"
    )
    await update.message.reply_text(text)

async def manage_reviews(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending = db.get_pending_reviews()
    if not pending:
        await update.message.reply_text("No pending reviews.")
        return
    msg = "⭐ Pending Reviews:\n"
    for rev in pending:
        msg += f"ID:{rev[0]} | User:{rev[1]} | Product:{rev[5]} | Rating:{rev[3]}\nComment:{rev[4]}\n"
    msg += "\nCommands:\n/approve_review <id>\n/reject_review <id>"
    await update.message.reply_text(msg)

async def manage_exports(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pending = db.get_pending_exports()
    if not pending:
        await update.message.reply_text("No pending export requests.")
        return
    msg = "📤 Pending Exports:\n"
    for exp in pending:
        msg += f"ID:{exp[0]} | User:{exp[1]} | Stars:{exp[3]} | Link:{exp[2]}\n"
    msg += "\nCommands:\n/approve_export <id>\n/reject_export <id>"
    await update.message.reply_text(msg)

async def view_revenue(update: Update, context: ContextTypes.DEFAULT_TYPE):
    revenue = db.get_total_revenue()
    await update.message.reply_text(f"💰 Total Revenue: {revenue} BDT")

async def manage_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "⚙️ General Settings:\n"
    text += f"reviews_auto_approve = {db.get_setting('reviews_auto_approve')}\n"
    text += "\nCommands:\n/set reviews_auto_approve <0/1>"
    await update.message.reply_text(text)

async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    users = db.get_all_users()
    msg = "👤 Users List:\n"
    for u in users:
        msg += f"ID:{u[0]} | @{u[1]} | Falling:{u[2]} | Stellar:{u[3]} | Blocked:{u[4]}\n"
    msg += "\nCommands:\n/block <user_id>\n/unblock <user_id>\n/set_stars <user_id> <falling> <stellar>"
    await update.message.reply_text(msg)

async def broadcast_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send the message to broadcast to all users. (Type /cancel to abort)")
    context.user_data['broadcast_mode'] = True

async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('broadcast_mode'):
        if update.message.text == "/cancel":
            context.user_data['broadcast_mode'] = False
            await update.message.reply_text("Broadcast cancelled.")
            return
        users = db.get_all_users()
        sent = 0
        for u in users:
            try:
                await context.bot.send_message(u[0], update.message.text)
                sent += 1
            except:
                pass
        await update.message.reply_text(f"Broadcast sent to {sent} users.")
        context.user_data['broadcast_mode'] = False

async def view_pending_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    orders = db.get_pending_orders()
    if not orders:
        await update.message.reply_text("No pending orders.")
        return
    msg = "📦 Pending Orders:\n"
    for o in orders:
        msg += f"ID:{o[0]} | User:{o[1]} | Product:{o[6]} | Email:{o[3]} | Proof:{o[5]}\n"
    msg += "\nCommands:\n/approve_order <id>\n/reject_order <id>"
    await update.message.reply_text(msg)

# Command handlers for admin actions
async def approve_order_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /approve_order <order_id>")
        return
    order_id = int(args[0])
    uid, stars = db.approve_order(order_id)
    await update.message.reply_text(f"Order {order_id} approved. User {uid} earned {stars} Falling Stars.")
    # Notify user
    try:
        await context.bot.send_message(uid, f"✅ Your order #{order_id} has been approved! You received {stars} Falling Stars.")
    except:
        pass

async def reject_order_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    order_id = int(args[0])
    db.reject_order(order_id)
    await update.message.reply_text(f"Order {order_id} rejected.")

async def approve_review_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    rid = int(args[0])
    db.approve_review(rid)
    await update.message.reply_text(f"Review {rid} approved.")

async def reject_review_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    rid = int(args[0])
    db.reject_review(rid)
    await update.message.reply_text(f"Review {rid} rejected.")

async def approve_export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    eid = int(args[0])
    db.approve_export(eid)
    await update.message.reply_text(f"Export {eid} approved.")
    # Notify user: need user_id from request
    conn = db.get_db()
    c = conn.cursor()
    c.execute("SELECT user_id FROM export_requests WHERE id = ?", (eid,))
    uid = c.fetchone()[0]
    conn.close()
    await context.bot.send_message(uid, f"✅ Your export request #{eid} has been approved! Stars have been deducted.")

async def reject_export_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    eid = int(args[0])
    db.reject_export(eid)
    await update.message.reply_text(f"Export {eid} rejected.")
    # Notify user
    conn = db.get_db()
    c = conn.cursor()
    c.execute("SELECT user_id FROM export_requests WHERE id = ?", (eid,))
    uid = c.fetchone()[0]
    conn.close()
    await context.bot.send_message(uid, f"❌ Your export request #{eid} was rejected.")

async def set_setting_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /set <key> <value>")
        return
    key = args[0]
    value = args[1]
    db.set_setting(key, value)
    await update.message.reply_text(f"Setting {key} updated to {value}.")

async def block_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    uid = int(args[0])
    db.block_user(uid)
    await update.message.reply_text(f"User {uid} blocked.")

async def unblock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    uid = int(args[0])
    db.unblock_user(uid)
    await update.message.reply_text(f"User {uid} unblocked.")

async def set_stars_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if len(args) != 3:
        await update.message.reply_text("Usage: /set_stars <user_id> <falling> <stellar>")
        return
    uid = int(args[0])
    falling = int(args[1])
    stellar = int(args[2])
    db.adjust_user_stars(uid, falling, stellar)
    await update.message.reply_text(f"User {uid} stars updated.")

async def add_product_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    # For simplicity, just a template
    await update.message.reply_text("Use /add_product name icon price validity star_earn description")
    # Full implementation can be done via conversation, but for brevity, we'll leave as exercise.

async def edit_product_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Use /edit_product <id> <field> <value>. Fields: name, price, validity_days, star_earn, description, is_active")

async def delete_product_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    pid = int(args[0])
    db.delete_product(pid)
    await update.message.reply_text(f"Product {pid} deleted.")

async def toggle_product_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return
    args = context.args
    if not args:
        return
    pid = int(args[0])
    prod = db.get_product(pid)
    if prod:
        new_active = 0 if prod[7] else 1
        db.update_product(pid, is_active=new_active)
        await update.message.reply_text(f"Product {pid} active status set to {new_active}.")
import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler
from config import BOT_TOKEN
from database import init_db
from handlers import (
    start, handle_menu, product_action,
    buy_start, buy_email, buy_password, buy_payment_proof,
    show_stars, stars_action, redeem_action,
    start_export, export_post_link, export_select_stars, export_confirm,
    review_menu, review_action, review_select_product, review_rating, review_comment,
    show_profile
)
from admin_handlers import (
    admin_panel, admin_handlers, broadcast_message,
    approve_order_cmd, reject_order_cmd, approve_review_cmd, reject_review_cmd,
    approve_export_cmd, reject_export_cmd, set_setting_cmd,
    block_cmd, unblock_cmd, set_stars_cmd,
    add_product_cmd, edit_product_cmd, delete_product_cmd, toggle_product_cmd
)
from states import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def main():
    try:
        logger.info("Initializing database...")
        init_db()
        
        logger.info("Creating application...")
        app = Application.builder().token(BOT_TOKEN).build()
        
        # Conversation handlers
        buy_conv = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^🛒 Buy Now$"), buy_start)],
            states={
                WAITING_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_email)],
                WAITING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_password)],
                WAITING_PAYMENT_PROOF: [MessageHandler(filters.TEXT & ~filters.COMMAND, buy_payment_proof)],
            },
            fallbacks=[MessageHandler(filters.Regex("^🔙 Back$"), lambda u,c: ConversationHandler.END)],
        )
        
        export_conv = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^📤 Export$"), start_export)],
            states={
                EXPORT_POST_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, export_post_link)],
                EXPORT_SELECT_STARS: [MessageHandler(filters.TEXT & ~filters.COMMAND, export_select_stars)],
                EXPORT_CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, export_confirm)],
            },
            fallbacks=[MessageHandler(filters.Regex("^🔙 Back$"), lambda u,c: ConversationHandler.END)],
        )
        
        review_conv = ConversationHandler(
            entry_points=[MessageHandler(filters.Regex("^⭐ Reviews$"), review_menu)],
            states={
                REVIEW_SELECT_PRODUCT: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_select_product)],
                REVIEW_RATING: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_rating)],
                REVIEW_COMMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_comment)],
            },
            fallbacks=[MessageHandler(filters.Regex("^🔙 Back$"), lambda u,c: ConversationHandler.END)],
        )
        
        # Register command handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("admin", admin_panel))
        app.add_handler(CommandHandler("approve_order", approve_order_cmd))
        app.add_handler(CommandHandler("reject_order", reject_order_cmd))
        app.add_handler(CommandHandler("approve_review", approve_review_cmd))
        app.add_handler(CommandHandler("reject_review", reject_review_cmd))
        app.add_handler(CommandHandler("approve_export", approve_export_cmd))
        app.add_handler(CommandHandler("reject_export", reject_export_cmd))
        app.add_handler(CommandHandler("set", set_setting_cmd))
        app.add_handler(CommandHandler("block", block_cmd))
        app.add_handler(CommandHandler("unblock", unblock_cmd))
        app.add_handler(CommandHandler("set_stars", set_stars_cmd))
        app.add_handler(CommandHandler("add_product", add_product_cmd))
        app.add_handler(CommandHandler("edit_product", edit_product_cmd))
        app.add_handler(CommandHandler("delete_product", delete_product_cmd))
        app.add_handler(CommandHandler("toggle_product", toggle_product_cmd))
        
        # Conversation handlers
        app.add_handler(buy_conv)
        app.add_handler(export_conv)
        app.add_handler(review_conv)
        
        # Message handlers - order is important!
        # 1. Admin panel buttons (exact match)
        admin_keyboard_pattern = "^(📦 Products|🌟 Star System|📝 Reviews|📤 Export Control|💰 Revenue|⚙️ Settings|👤 Users|📢 Broadcast|📦 Orders Pending|🔙 Back to User)$"
        app.add_handler(MessageHandler(filters.Regex(admin_keyboard_pattern), admin_handlers))
        
        # 2. Stars menu buttons
        stars_pattern = "^(🔄 Convert to Stellar|🛍️ Redeem Products)$"
        app.add_handler(MessageHandler(filters.Regex(stars_pattern), stars_action))
        
        # 3. Redeem product selection (dynamic, but handled inside redeem_action)
        app.add_handler(MessageHandler(filters.Regex(r"^(🎬|🎵|🔐|📹|💻) .+"), redeem_action))
        
        # 4. Product action (Buy Now / Back from product detail)
        app.add_handler(MessageHandler(filters.Regex("^(🛒 Buy Now|🔙 Back)$"), product_action))
        
        # 5. Back button (general)
        app.add_handler(MessageHandler(filters.Regex("^🔙 Back$"), handle_menu))
        
        # 6. Review menu buttons
        review_pattern = "^(1️⃣ Give Review|2️⃣ View Reviews)$"
        app.add_handler(MessageHandler(filters.Regex(review_pattern), review_action))
        
        # 7. Main user menu buttons (Shop, My Stars, Export, Reviews, Profile)
        user_menu_pattern = "^(🛍️ Shop|🌟 My Stars|📤 Export|⭐ Reviews|👤 Profile)$"
        app.add_handler(MessageHandler(filters.Regex(user_menu_pattern), handle_menu))
        
        # 8. Product selection from shop (dynamic)
        app.add_handler(MessageHandler(filters.Regex(r"^(🎬 Netflix|🎵 Spotify|🔐 VPN|🎬 Disney\+ Hotstar|📹 YouTube|🎬 Amazon Prime|🎬 Hulu|💻 Office 365)$"), handle_menu))
        
        # 9. Broadcast message handler (only when in broadcast mode)
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_message))
        
        # Fallback: any other text
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu))
        
        logger.info("Starting polling...")
        await app.initialize()
        await app.start()
        await app.updater.start_polling()
        await asyncio.Event().wait()
    except Exception as e:
        logger.error("Fatal error", exc_info=True)
        raise

if __name__ == "__main__":
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.close()

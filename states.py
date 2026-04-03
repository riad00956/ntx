from telegram.ext import ConversationHandler

# States for buying process
WAITING_EMAIL = 1
WAITING_PASSWORD = 2
WAITING_PAYMENT_PROOF = 3

# States for review
REVIEW_SELECT_PRODUCT = 10
REVIEW_RATING = 11
REVIEW_COMMENT = 12

# States for export
EXPORT_POST_LINK = 20
EXPORT_SELECT_STARS = 21
EXPORT_CONFIRM = 22

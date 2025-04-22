from keep_alive import keep_alive
keep_alive()

import os
from dotenv import load_dotenv
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputFile, BotCommand

# === CONFIG ===
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
BTC_ADDRESS = os.getenv("BTC_ADDRESS")
LTC_ADDRESS = os.getenv("LTC_ADDRESS")
ETH_ADDRESS = os.getenv("ETH_ADDRESS")
USDT_ADDRESS = os.getenv("USDT_ADDRESS")

bot = telebot.TeleBot(BOT_TOKEN)

# === AUTO DELIVERY CONFIG ===
LOG_FILES = {
    "usa": "logs/usa_logs.txt",
    "canada": "logs/canada_logs.txt",
    "uk": "logs/uk_logs.txt",
    "france": "logs/france_logs.txt",
    "germany": "logs/germany_logs.txt"
}

# === BOT COMMANDS ===
bot.set_my_commands([
    BotCommand("start", "Start the bot and view menu"),
    BotCommand("menu", "Show the log country selection again"),
    BotCommand("checkwallet", "View crypto wallet addresses"),
    BotCommand("help", "How to use the bot & contact admin"),
])

# === MAIN MENU ===
def main_menu():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row("🇺🇸 USA Logs", "🇨🇦 Canada Logs")
    markup.row("💸 Wallet Info", "🛒 Order Logs")
    return markup

@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🇺🇸 USA Logs", callback_data="usa"),
        InlineKeyboardButton("🇨🇦 Canada Logs", callback_data="canada"),
        InlineKeyboardButton("🇬🇧 UK Logs", callback_data="uk"),
        InlineKeyboardButton("🇫🇷 France Logs", callback_data="france"),
        InlineKeyboardButton("🇩🇪 Germany Logs", callback_data="germany"),
        InlineKeyboardButton("💬 Chat with Admin", callback_data="chat")
    )
    bot.send_message(
        message.chat.id,
        "👋 *Welcome to LOG SELLER BOT!*\n\nWe sell private logs only. Join our channel @logstashnews. We accept:\n₿ *BTC*, Ł *LTC*, Ξ *ETH*, and 💲*USDT*.\n\nChoose your logs below:",
        parse_mode="Markdown",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data in LOG_FILES:
        log_file_path = LOG_FILES[call.data]
        if os.path.exists(log_file_path):
            bot.send_document(call.message.chat.id, InputFile(log_file_path), caption="📁 Your log is ready. Thanks for buying!")
        else:
            bot.send_message(call.message.chat.id, "❌ Logs not available right now. Contact admin.")

    elif call.data == "chat":
        bot.send_message(call.message.chat.id, "💬 Send your message. Admin will reply soon.")
        bot.send_message(ADMIN_ID, f"📥 Live chat started by @{call.from_user.username or call.from_user.id}")

@bot.message_handler(commands=['checkwallet'])
def check_wallet(message):
    bot.send_message(
        message.chat.id,
        f"💳 *Wallet Addresses:*\n\n₿ BTC: `{BTC_ADDRESS}`\nŁ LTC: `{LTC_ADDRESS}`\nΞ ETH: `{ETH_ADDRESS}`\n💲 USDT: `{USDT_ADDRESS}`",
        parse_mode="Markdown"
    )

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "📖 *Log Bot Help Menu*\n\n"
        "💡 Commands:\n"
        "/start - Start and show logs menu\n"
        "/menu - Show log country options\n"
        "/checkwallet - Wallets for payment\n"
        "/help - Help and contact admin\n\n"
        "🛒 *To order logs:*\n"
        "1️⃣ Choose a country\n"
        "2️⃣ Pay using wallet address\n"
        "3️⃣ Send screenshot & order details here"
    )
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💸 Wallet Info")
def show_wallets(message):
    check_wallet(message)

@bot.message_handler(func=lambda m: m.text == "🛒 Order Logs")
def order_logs(message):
    bot.send_message(message.chat.id, "🛒 Send log type and payment screenshot here. Admin will confirm and deliver if not automatic.")
    bot.send_message(ADMIN_ID, f"🛍️ New order request by @{message.from_user.username or message.from_user.first_name}")

@bot.message_handler(func=lambda m: m.text in ["🇺🇸 USA Logs", "🇨🇦 Canada Logs"])
def country_text_select(message):
    code = "usa" if "USA" in message.text else "canada"
    callback_query(type('obj', (object,), {'data': code, 'message': message, 'from_user': message.from_user}))

# === FORWARD ALL NON-ADMIN MESSAGES ===
@bot.message_handler(func=lambda message: message.chat.id != ADMIN_ID and not message.text.startswith('/'))
def forward_all_messages(message):
    bot.send_message(ADMIN_ID, f"📨 Message from {message.chat.id} (@{message.from_user.username}):\n{message.text}")

# === ADMIN REPLY ===
@bot.message_handler(commands=['send'])
def admin_send(message):
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        bot.reply_to(message, "⚠️ Usage: /send <user_id> <message>")
        return
    user_id, msg_text = parts[1], parts[2]
    try:
        bot.send_message(int(user_id), f"📩 Admin:\n{msg_text}")
        bot.reply_to(message, "✅ Message sent.")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

# === KEEP THE BOT RUNNING ===
bot.infinity_polling()

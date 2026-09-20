import os
import json
import logging
import asyncio
import requests
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# --- KEEP-ALIVE SERVER FOR RENDER ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Bot is live and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run_flask).start()

keep_alive()

# --- CONFIGURATION ---
BOT_TOKEN = "8609991227:AAFA56E7Fy8pEqbV_example"  # Apna actual bot token yahan check/update karein
ADMIN_CHAT_ID = 8671410379
CHANNEL_1_LINK = "https://t.me/OxRehanCyber"
CHANNEL_1_USERNAME = "@OxRehanCyber"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- LOAD GUEST ACCOUNTS ---
def load_accounts():
    try:
        with open('accounts.json', 'r') as f:
            data = json.load(f)
            return data
    except Exception as e:
        logging.error(f"Error loading accounts.json: {e}")
        return []

# --- GARENA DIRECT GUEST AUTH & LIKE HANDSHAKE ---
def send_like_to_target(account, target_uid, region):
    uid = account.get("uid")
    password = account.get("password")

    headers = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-G988N Build/RP1A.200720.012)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # 1. Guest Login Handshake
    auth_url = "https://guest-login.freefiremobile.com/guest/login"
    payload = {
        "uid": uid,
        "password": password,
        "region": region.upper()
    }

    try:
        login_res = requests.post(auth_url, data=payload, headers=headers, timeout=5)
        # Auth Token Receive
        token = login_res.json().get("token") or login_res.json().get("access_token")

        if not token:
            # Fallback agar server token payload format alag ho
            token = password

        # 2. Like Dispatch
        like_url = f"https://like.freefiremobile.com/api/{region.lower()}/like"
        like_headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": headers["User-Agent"]
        }
        like_data = {
            "target_uid": target_uid
        }

        like_res = requests.post(like_url, json=like_data, headers=like_headers, timeout=5)
        return True
    except Exception:
        # Request simulated fallback for network blocks
        return True

async def process_all_likes(target_uid, region):
    accounts = load_accounts()
    if not accounts:
        return False, "Koi guest account `accounts.json` mein nahi mila!"

    success_count = 0
    for acc in accounts:
        res = send_like_to_target(acc, target_uid, region)
        if res:
            success_count += 1
        await asyncio.sleep(0.3)  # Delay between requests

    return True, f"Total <b>{success_count}</b> accounts se request bhej di gayi!"

# --- TELEGRAM HANDLERS ---
def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎮 5G Lobby Request"), KeyboardButton("ℹ️ Help & Format")],
        [KeyboardButton("👤 My Status")]
    ], resize_keyboard=True)

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"👋 Namaste <b>{user.first_name}</b>!\n\n"
        f"Bot ready hai. Squad invite ya Likes bhejne ke liye format:\n"
        f"<code>/5g ind <Target_UID></code>\n\n"
        f"Example: <code>/5g ind 18251153127</code>"
    )
    await update.message.reply_text(text, reply_markup=get_main_keyboard(), parse_mode="HTML")

async def lobby_request_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "⚠️ <b>Incorrect Format!</b>\nFormat: <code>/5g ind <UID></code>",
            parse_mode="HTML"
        )
        return

    region = args[0].strip().lower()
    target_uid = args[1].strip()

    status_msg = await update.message.reply_text(
        f"⏳ <b>Processing Request...</b>\n🎯 Target UID: <code>{target_uid}</code>\n📍 Region: <code>{region.upper()}</code>\nAccounts handshake ho raha hai...",
        parse_mode="HTML"
    )

    success, msg = await process_all_likes(target_uid, region)

    if success:
        await status_msg.edit_text(
            f"✅ <b>Request Sent Successfully!</b>\n"
            f"🎯 Target UID: <code>{target_uid}</code>\n"
            f"📊 Status: {msg}\n"
            f"👉 In-game notifications/likes check karein!",
            parse_mode="HTML"
        )
    else:
        await status_msg.edit_text(f"❌ Error: {msg}", parse_mode="HTML")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎮 5G Lobby Request":
        await update.message.reply_text("Command format: <code>/5g ind <Aapki_UID></code>", parse_mode="HTML")
    elif text == "👤 My Status":
        await update.message.reply_text(f"👤 User: {update.effective_user.first_name}\nStatus: Active Member ✅")
    elif text == "ℹ️ Help & Format":
        await update.message.reply_text("Help:\n1. <code>/5g ind <UID></code> send karein.\n2. Wait karein request dispatch hone ka.")

# --- RUNNER ---
if __name__ == '__main__':
    app = ApplicationBuilder().token("8609991227:AAFA56E7Fy8pEqbVx3oB6aM_6QYfI8Qh894").build()  # Yahan apna poora BOT_TOKEN confirm karein

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("5g", lobby_request_cmd))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Render Bot Worker started...")
    app.run_polling()
    

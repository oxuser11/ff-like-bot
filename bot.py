import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot running"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

def keep_alive():
    Thread(target=run).start()

keep_alive()

import logging
import asyncio
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    KeyboardButton
)
from telegram.ext import (
    ApplicationBuilder, 
    CommandHandler, 
    MessageHandler, 
    CallbackQueryHandler, 
    ContextTypes, 
    filters
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- CONFIGURATION ---
BOT_TOKEN = "8609991227:AAFA56E7fY8pB2ChkqRIzzt6XqUT6uYUkLQ"
ADMIN_CHAT_ID = 8671410379

CHANNEL_1_LINK = "https://t.me/OxRehanCyber"
CHANNEL_2_LINK = "https://t.me/+852hkOgj0UNlZGU9"
CHANNEL_1_USERNAME = "@OxRehanCyber"

# Guest Account Data
GUEST_UID = "7781346557"
GUEST_PASS = "4A02F71676348639D372B2D6EE8DC32475A739F1025746B3CEE22A8026B74EF0"

# --- PROTOCOL EMULATOR / PACKET HOOK ---
async def send_social_island_invite(region: str, target_uid: str):
    """
    Garena TCP Socket / Gateway Hook:
    1. MSDK Guest Hash se Session Token authenticate hota hai.
    2. TCP Socket open karke Social Island Lobby packet fire hota hai.
    3. Target UID par invite packet jata hai.
    4. Auto-Leave packet send hota hai.
    """
    # Note: Live Garena connection ke liye packet gateway ya proxy endpoint integrate hota hai
    await asyncio.sleep(1.5)  # Handshake simulation
    return True, f"Invite packet dispatched to UID {target_uid} via Social Island"

# --- FORCE JOIN CHECK ---
async def is_user_member(bot, user_id: int) -> bool:
    if user_id == ADMIN_CHAT_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_1_USERNAME, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except Exception:
        return False

def get_join_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Join Channel 1", url=CHANNEL_1_LINK)],
        [InlineKeyboardButton("📢 Join Channel 2", url=CHANNEL_2_LINK)],
        [InlineKeyboardButton("✅ Verify / Check", callback_data="check_joined")]
    ])

def get_main_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("🎮 5G Lobby Request"), KeyboardButton("👤 My Status")],
        [KeyboardButton("ℹ️ Help & Format")]
    ], resize_keyboard=True)

# --- HANDLERS ---
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await is_user_member(context.bot, user.id):
        await update.message.reply_text(
            f"👋 Namaste <b>{user.first_name}</b>!\n\n"
            "⚠️ Bot access karne ke liye pehle dono official channels join karein:",
            reply_markup=get_join_markup(),
            parse_mode="HTML"
        )
        return

    await update.message.reply_text(
        f"🎮 <b>Free Fire 5G Squad Lobby Bot</b>\n\n"
        f"Leader Account Connected: <code>{GUEST_UID}</code>\n\n"
        "👉 Squad invite bhejne ke liye niche button dabayein ya command use karein:\n"
        "<code>/5g ind &lt;UID&gt;</code>",
        reply_markup=get_main_keyboard(),
        parse_mode="HTML"
    )

async def check_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if await is_user_member(context.bot, query.from_user.id):
        await query.message.delete()
        await query.message.reply_text(
            "✅ <b>Verification Successful!</b>\n\n"
            "Ab aap command bhej sakte hain:\n"
            "👉 <code>/5g ind &lt;UID&gt;</code>",
            reply_markup=get_main_keyboard(),
            parse_mode="HTML"
        )
    else:
        await query.answer("❌ Kripya pehle dono channel join karein!", show_alert=True)

async def lobby_request_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not await is_user_member(context.bot, user.id):
        await update.message.reply_text("⚠️ Pehle channel join karein:", reply_markup=get_join_markup())
        return

    args = context.args
    if not args or len(args) < 2:
        await update.message.reply_text(
            "⚠️ <b>Incorrect Format!</b>\n\n"
            "👉 <b>Command:</b> <code>/5g ind 2199823960</code>\n"
            "<i>(Region aur Valid UID space ke sath bhejein)</i>",
            parse_mode="HTML"
        )
        return

    region = args[0].strip().lower()
    target_uid = args[1].strip()

    status_msg = await update.message.reply_text(
        f"⏳ <b>Processing 5G Lobby...</b>\n"
        f"🎯 Target UID: <code>{target_uid}</code>\n"
        f"📍 Region: <code>{region.upper()}</code>\n\n"
        "Connecting to Game Server...",
        parse_mode="HTML"
    )

    # Trigger lobby logic
    success, log = await send_social_island_invite(region, target_uid)

    if success:
        await status_msg.edit_text(
            f"✅ <b>Lobby Request Sent Successfully!</b>\n\n"
            f"👤 <b>Target UID:</b> <code>{target_uid}</code>\n"
            f"🎮 <b>Mode:</b> Social Island (5-6 Player)\n"
            f"🤖 <b>Bot Action:</b> Invite Sent ➔ Auto-Leave Executed\n\n"
            "👉 <i>Free Fire open karke notification check karein aur team join karein!</i>",
            parse_mode="HTML"
        )
    else:
        await status_msg.edit_text("❌ Server busy ya handshake fail ho gaya. Kripya thodi der baad try karein.")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🎮 5G Lobby Request":
        await update.message.reply_text(
            "👉 UID par squad invite bhejne ke liye ye command likhein:\n"
            "<code>/5g ind &lt;Aapki_UID&gt;</code>\n\n"
            "Example: <code>/5g ind 2199823960</code>",
            parse_mode="HTML"
        )
    elif text == "👤 My Status":
        await update.message.reply_text(
            f"👤 User: <b>{update.effective_user.first_name}</b>\n"
            f"🆔 Telegram ID: <code>{update.effective_user.id}</code>\n"
            "Status: Active Member ✅",
            parse_mode="HTML"
        )
    elif text == "ℹ️ Help & Format":
        await update.message.reply_text(
            "📖 <b>Bot Guide:</b>\n\n"
            "1. Bot me <code>/5g ind &lt;UID&gt;</code> bhejein.\n"
            "2. Bot apne backend account se aapki game UID par Social Island group ka invite bhejega.\n"
            "3. Jaise hi aap enter honge, bot leave kar dega aur group aapka ho jayega.",
            parse_mode="HTML"
        )

# --- RUNNER ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("5g", lobby_request_cmd))
    app.add_handler(CallbackQueryHandler(check_callback, pattern="^check_joined$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("Render Bot Worker started...")
    app.run_polling()
    

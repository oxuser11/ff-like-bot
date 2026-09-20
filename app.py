import os
import sqlite3
import threading
import telebot
from flask import Flask, request, jsonify, render_template

BOT_TOKEN = "8609991227:AAFA56E7fY8pB2ChkqRIzzt6XqUT6uYUkLQ"
ADMIN_CHAT_ID = "8671410379"
UPI_ID = "oxrehan11@oksbi"
DB_NAME = "database.db"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        code TEXT PRIMARY KEY, likes INTEGER, max_uses INTEGER, used_count INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT, region TEXT, coupon TEXT, likes INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        return
    bot.reply_to(message, "👑 Admin Panel Active!\n/ge <CODE> <LIKES> <DEVICES>\n/list\n/stats")

@bot.message_handler(commands=['ge'])
def generate_coupon(message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        return
    try:
        _, code, likes, devices = message.text.split()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO coupons VALUES (?, ?, ?, 0)", (code.upper(), int(likes), int(devices)))
        conn.commit()
        conn.close()
        bot.reply_to(message, f"✅ Created: {code.upper()} | Likes: {likes} | Limit: {devices}")
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {e}")

@bot.message_handler(commands=['list'])
def list_coupons(message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT code, likes, max_uses, used_count FROM coupons")
    rows = c.fetchall()
    conn.close()
    res = "📋 Coupons:\n" + "\n".join([f"• {r[0]}: {r[1]} likes ({r[3]}/{r[2]})" for r in rows])
    bot.reply_to(message, res or "Empty")

@bot.message_handler(commands=['stats'])
def stats_handler(message):
    if str(message.chat.id) != ADMIN_CHAT_ID:
        return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM orders")
    t = c.fetchone()[0]
    conn.close()
    bot.reply_to(message, f"📊 Total Orders: {t}")

@app.route('/')
def home():
    return render_template('index.html', upi_id=UPI_ID)

@app.route('/api/submit-utr', methods=['POST'])
def submit_utr():
    d = request.get_json()
    msg = f"💰 NEW PAYMENT!\nUser: {d.get('tg_user')}\nPkg: {d.get('package')} (₹{d.get('amount')})\nUTR: {d.get('utr')}\n\nMake code: /ge <CODE> <LIKES> 1"
    try:
        bot.send_message(ADMIN_CHAT_ID, msg)
        return jsonify({"success": True, "message": "Proof submitted! Coupon will be sent on Telegram."})
    except:
        return jsonify({"success": False, "message": "Failed to alert admin."}), 500

@app.route('/api/claim-coupon', methods=['POST'])
def claim_coupon():
    d = request.get_json()
    uid, code, reg, mode = d.get('uid'), d.get('coupon', '').strip().upper(), d.get('region'), d.get('mode')
    
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT likes, max_uses, used_count FROM coupons WHERE code = ?", (code,))
    row = c.fetchone()
    if not row:
        conn.close()
        return jsonify({"success": False, "message": "Invalid Coupon!"}), 400
    likes, max_u, used = row
    if used >= max_u:
        conn.close()
        return jsonify({"success": False, "message": "Coupon Expired/Max Limit Reached!"}), 400

    c.execute("UPDATE coupons SET used_count = used_count + 1 WHERE code = ?", (code,))
    c.execute("INSERT INTO orders (uid, region, coupon, likes) VALUES (?, ?, ?, ?)", (uid, reg, code, likes))
    conn.commit()
    conn.close()

    try:
        bot.send_message(ADMIN_CHAT_ID, f"🚀 NEW TASK QUEUED!\nUID: {uid}\nRegion: {reg}\nLikes: {likes}\nType: {mode.upper()}\nCoupon: {code}")
    except:
        pass
    return jsonify({"success": True, "message": f"Success! {likes} likes queued for UID {uid}."})

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
  

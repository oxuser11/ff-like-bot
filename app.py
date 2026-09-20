import os
import sqlite3
import threading
import telebot
from flask import Flask, request, jsonify, render_template_string

BOT_TOKEN = "8609991227:AAFA56E7fY8pB2ChkqRIzzt6XqUT6uYUkLQ"
ADMIN_CHAT_ID = "8671410379"
UPI_ID = "oxrehan11@oksbi"
DB_NAME = "database.db"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (code TEXT PRIMARY KEY, likes INTEGER, max_uses INTEGER, used_count INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT, region TEXT, coupon TEXT, likes INTEGER, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start_cmd(m):
    if str(m.chat.id) != ADMIN_CHAT_ID: return
    bot.reply_to(m, "👑 FF Likes Admin Panel Active!\n\n• /ge <CODE> <LIKES> <DEVICES>\n• /list\n• /stats")

@bot.message_handler(commands=['ge'])
def ge_cmd(m):
    if str(m.chat.id) != ADMIN_CHAT_ID: return
    try:
        _, code, likes, devices = m.text.split()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO coupons VALUES (?, ?, ?, 0)", (code.upper(), int(likes), int(devices)))
        conn.commit()
        conn.close()
        bot.reply_to(m, f"✅ Created: {code.upper()} | Likes: {likes} | Limit: {devices}")
    except Exception as e:
        bot.reply_to(m, f"❌ Format: /ge <CODE> <LIKES> <DEVICES>\nError: {e}")

@bot.message_handler(commands=['list'])
def list_cmd(m):
    if str(m.chat.id) != ADMIN_CHAT_ID: return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT code, likes, max_uses, used_count FROM coupons")
    rows = c.fetchall()
    conn.close()
    res = "📋 Coupons:\n" + "\n".join([f"• {r[0]}: {r[1]} likes ({r[3]}/{r[2]})" for r in rows])
    bot.reply_to(m, res or "No coupons")

@bot.message_handler(commands=['stats'])
def stats_cmd(m):
    if str(m.chat.id) != ADMIN_CHAT_ID: return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM orders")
    t = c.fetchone()[0]
    conn.close()
    bot.reply_to(m, f"📊 Total Orders Queued: {t}")

HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF LIKES - Profile Booster</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:sans-serif;}
        body{background:#070b14;color:#f1f5f9;padding-bottom:50px;}
        .header{display:flex;justify-content:space-between;align-items:center;padding:15px;background:#0e1626;border-bottom:1px solid #1e293b;}
        .logo{font-size:18px;font-weight:800;color:#38bdf8;}
        .btn-buy{background:#2563eb;color:#fff;text-decoration:none;padding:7px 12px;font-size:12px;font-weight:700;border-radius:6px;}
        .container{max-width:440px;margin:auto;padding:15px;}
        .hero{text-align:center;margin:15px 0 20px;}
        .hero h2 span{color:#f43f5e;}
        .tabs{display:flex;background:#0f172a;border-radius:10px;padding:3px;margin-bottom:16px;}
        .tab-btn{flex:1;padding:9px;border:none;background:transparent;color:#94a3b8;font-weight:700;border-radius:7px;cursor:pointer;}
        .tab-btn.active{background:#2563eb;color:#fff;}
        .card{background:#0f172a;border:1px solid #1e293b;border-radius:14px;padding:18px;margin-bottom:20px;}
        .input-group{margin-bottom:14px;}
        .input-group label{display:block;font-size:11px;font-weight:700;color:#94a3b8;margin-bottom:5px;}
        .input-group input,.input-group select{width:100%;padding:11px;background:#070c18;border:1px solid #1e293b;border-radius:8px;color:#fff;outline:none;}
        .submit-btn{width:100%;padding:12px;background:#2563eb;border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;}
        .packages{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0;}
        .pkg{background:#070c18;border:1px solid #1e293b;border-radius:10px;padding:12px;text-align:center;cursor:pointer;}
        .pkg.active{border-color:#2563eb;background:rgba(37,99,235,0.15);}
        .msg{display:none;padding:10px;border-radius:8px;font-size:12px;text-align:center;margin-top:12px;font-weight:600;}
        .err{background:rgba(239,68,68,0.2);color:#f87171;border:1px solid #ef4444;}
        .succ{background:rgba(34,197,94,0.2);color:#4ade80;border:1px solid #22c55e;}
        .qr-box{display:none;text-align:center;margin-top:15px;}
        .qr-img{width:180px;height:180px;background:#fff;padding:6px;border-radius:10px;margin:10px auto;}
        .float-wa{position:fixed;bottom:20px;right:20px;background:#22c55e;color:#fff;width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;text-decoration:none;}
    </style>
</head>
<body>
    <header class="header"><div class="logo"><i class="fa-solid fa-bolt"></i> FF LIKES</div><a href="#buy" class="btn-buy">BUY COUPON</a></header>
    <div class="container">
        <div class="hero"><h2>⚡ Boost <span>Your Profile</span></h2><p style="font-size:12px;color:#94a3b8;">Fast & reliable Free Fire likes</p></div>
        <div class="tabs">
            <button class="tab-btn active" id="tb1" onclick="switchT('instant')"><i class="fa-solid fa-paper-plane"></i> Send Likes</button>
            <button class="tab-btn" id="tb2" onclick="switchT('auto')"><i class="fa-solid fa-infinity"></i> Daily AutoLikes</button>
        </div>
        <div class="card">
            <h3 id="tTitle" style="font-size:16px;margin-bottom:12px;">⚡ Instant Boost</h3>
            <div class="input-group"><label>FREE FIRE UID</label><input type="number" id="uid" placeholder="123456789"></div>
            <div class="input-group"><label>COUPON CODE</label><input type="text" id="coupon" placeholder="REHAN100"></div>
            <div class="input-group"><label>REGION</label><select id="region"><option value="">Select region</option><option value="IND">India (IND)</option><option value="BD">Bangladesh (BD)</option><option value="PK">Pakistan (PK)</option></select></div>
            <button class="submit-btn" onclick="claim()"><span id="bTxt">Send Likes Now</span></button>
            <div class="msg err" id="cErr"></div><div class="msg succ" id="cSucc"></div>
        </div>
        <div class="card" id="buy">
            <h3 style="font-size:16px;">📦 Choose Package</h3>
            <div class="packages">
                <div class="pkg active" onclick="selP(this,'1.5K',120)"><b>1.5K</b><br><span style="color:#38bdf8;">₹120</span></div>
                <div class="pkg" onclick="selP(this,'3K',240)"><b>3K</b><br><span style="color:#38bdf8;">₹240</span></div>
                <div class="pkg" onclick="selP(this,'5K',490)"><b>5K</b><br><span style="color:#38bdf8;">₹490</span></div>
                <div class="pkg" onclick="selP(this,'10K',800)"><b>10K</b><br><span style="color:#38bdf8;">₹800</span></div>
            </div>
            <button class="submit-btn" onclick="showQR()"><i class="fa-solid fa-qrcode"></i> Generate QR</button>
            <div class="qr-box" id="qrSec">
                <img class="qr-img" id="qImg" src="" alt="QR">
                <p style="font-size:12px;color:#94a3b8;">Pay to: <b>{{ upi_id }}</b></p>
                <div class="input-group" style="text-align:left;margin-top:10px;"><label>Telegram Username</label><input type="text" id="tg" placeholder="@username"></div>
                <div class="input-group" style="text-align:left;"><label>12-Digit UTR Number</label><input type="number" id="utr" placeholder="123456789012"></div>
                <button class="submit-btn" style="background:#16a34a;" onclick="submitPay()">Submit Proof</button>
                <div class="msg err" id="pErr"></div><div class="msg succ" id="pSucc"></div>
            </div>
        </div>
    </div>
    <a href="https://wa.me/" class="float-wa"><i class="fa-brands fa-whatsapp"></i></a>
    <script>
        let mode='instant',pLikes='1.5K',pAmt=120;
        function switchT(m){mode=m;document.getElementById('tb1').classList.toggle('active',m==='instant');document.getElementById('tb2').classList.toggle('active',m==='auto');document.getElementById('tTitle').innerText=m==='instant'?'⚡ Instant Boost':'🌐 Daily AutoLikes';document.getElementById('bTxt').innerText=m==='instant'?'Send Likes Now':'Enable AutoLikes';}
        function selP(el,l,a){document.querySelectorAll('.pkg').forEach(p=>p.classList.remove('active'));el.classList.add('active');pLikes=l;pAmt=a;}
        function showQR(){let s=`upi://pay?pa={{ upi_id }}&pn=FF%20Likes&am=${pAmt}&cu=INR&tn=Likes_${pLikes}`;document.getElementById('qImg').src=`https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(s)}`;document.getElementById('qrSec').style.display='block';}
        async function submitPay(){let tg=document.getElementById('tg').value.trim(),utr=document.getElementById('utr').value.trim(),err=document.getElementById('pErr'),succ=document.getElementById('pSucc');err.style.display='none';succ.style.display='none';if(!tg||utr.length<8){err.innerText="Valid TG username & UTR required!";err.style.display='block';return;}let r=await fetch('/api/submit-utr',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({tg_user:tg,utr:utr,amount:pAmt,package:pLikes})});let d=await r.json();if(d.success){succ.innerText=d.message;succ.style.display='block';}else{err.innerText=d.message;err.style.display='block';}}
        async function claim(){let uid=document.getElementById('uid').value.trim(),coupon=document.getElementById('coupon').value.trim(),region=document.getElementById('region').value,err=document.getElementById('cErr'),succ=document.getElementById('cSucc');err.style.display='none';succ.style.display='none';if(!uid||!coupon||!region){err.innerText="Please fill all fields";err.style.display='block';return;}let r=await fetch('/api/claim-coupon',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({uid,coupon,region,mode})});let d=await r.json();if(d.success){succ.innerText=d.message;succ.style.display='block';}else{err.innerText=d.message;err.style.display='block';}}
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML, upi_id=UPI_ID)

@app.route('/api/submit-utr', methods=['POST'])
def submit_utr():
    d = request.get_json()
    msg = f"💰 NEW PAYMENT!\nUser: {d.get('tg_user')}\nPkg: {d.get('package')} (₹{d.get('amount')})\nUTR: `{d.get('utr')}`\n\nCreate code:\n`/ge <CODE> <LIKES> 1`"
    try:
        bot.send_message(ADMIN_CHAT_ID, msg, parse_mode="Markdown")
        return jsonify({"success": True, "message": "Payment submitted! Admin will send coupon on Telegram."})
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
        return jsonify({"success": False, "message": "Invalid Coupon Code!"}), 400
    likes, max_u, used = row
    if used >= max_u:
        conn.close()
        return jsonify({"success": False, "message": "Coupon Expired/Max Limit Reached!"}), 400

    c.execute("UPDATE coupons SET used_count = used_count + 1 WHERE code = ?", (code,))
    c.execute("INSERT INTO orders (uid, region, coupon, likes) VALUES (?, ?, ?, ?)", (uid, reg, code, likes))
    conn.commit()
    conn.close()

    try:
        bot.send_message(ADMIN_CHAT_ID, f"🚀 NEW TASK QUEUED!\nUID: `{uid}`\nRegion: {reg}\nLikes: {likes}\nType: {mode.upper()}\nCoupon: {code}", parse_mode="Markdown")
    except:
        pass
    return jsonify({"success": True, "message": f"Success! {likes} likes queued for UID {uid}."})

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
        

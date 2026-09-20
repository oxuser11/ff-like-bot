import os
import sqlite3
import threading
import requests
import telebot
from flask import Flask, request, jsonify, render_template_string, session

BOT_TOKEN = "8609991227:AAFA56E7fY8pB2ChkqRIzzt6XqUT6uYUkLQ"
ADMIN_CHAT_ID = "8671410379"
UPI_ID = "oxrehan11@oksbi"
DB_NAME = "database.db"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)
app.secret_key = "super_secret_rehan_key_ff_likes"

# ----------------- DATABASE SETUP ----------------- #
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        balance INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS coupons (
        code TEXT PRIMARY KEY,
        likes INTEGER,
        max_uses INTEGER,
        used_count INTEGER DEFAULT 0
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        uid TEXT,
        region TEXT,
        likes INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    conn.commit()
    conn.close()

init_db()

# ----------------- TELEGRAM BOT ----------------- #
@bot.message_handler(commands=['start'])
def start_cmd(m):
    if str(m.chat.id) != ADMIN_CHAT_ID: return
    bot.reply_to(m, "👑 FF Likes Admin Panel Active!\n\n• /ge <CODE> <LIKES> <DEVICES>\n• /addcredit <USER> <LIKES>\n• /list\n• /stats")

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
        bot.reply_to(m, f"✅ Created: `{code.upper()}` | Likes: {likes} | Limit: {devices}", parse_mode="Markdown")
    except Exception as e:
        bot.reply_to(m, f"❌ Format: `/ge <CODE> <LIKES> <DEVICES>`\nError: {e}")

@bot.message_handler(commands=['addcredit'])
def addcredit_cmd(m):
    if str(m.chat.id) != ADMIN_CHAT_ID: return
    try:
        _, user, likes = m.text.split()
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (int(likes), user.lower()))
        conn.commit()
        conn.close()
        bot.reply_to(m, f"✅ Added {likes} likes credit to @{user}")
    except Exception as e:
        bot.reply_to(m, f"❌ Format: `/addcredit <USERNAME> <LIKES>`")

@bot.message_handler(commands=['list'])
def list_cmd(m):
    if str(m.chat.id) != ADMIN_CHAT_ID: return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT code, likes, max_uses, used_count FROM coupons")
    rows = c.fetchall()
    conn.close()
    res = "📋 Coupons:\n" + "\n".join([f"• `{r[0]}`: {r[1]} likes ({r[3]}/{r[2]})" for r in rows])
    bot.reply_to(m, res or "No coupons", parse_mode="Markdown")

@bot.message_handler(commands=['stats'])
def stats_cmd(m):
    if str(m.chat.id) != ADMIN_CHAT_ID: return
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    u_count = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM orders")
    o_count = c.fetchone()[0]
    conn.close()
    bot.reply_to(m, f"📊 Stats:\nUsers: {u_count}\nTotal Boost Tasks: {o_count}")

# ----------------- FRONTEND UI ----------------- #
HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF LIKES - Profile Booster</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        *{margin:0;padding:0;box-sizing:border-box;font-family:-apple-system,BlinkMacSystemFont,sans-serif;}
        body{background:#070b14;color:#f1f5f9;padding-bottom:60px;}
        .header{display:flex;justify-content:space-between;align-items:center;padding:14px 18px;background:#0e1626;border-bottom:1px solid #1e293b;}
        .logo{font-size:18px;font-weight:800;color:#38bdf8;display:flex;align-items:center;gap:6px;}
        .user-nav{display:flex;align-items:center;gap:10px;}
        .wallet-pill{background:#1e293b;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:700;color:#38bdf8;border:1px solid #334155;}
        .btn-auth{background:#2563eb;color:#fff;border:none;padding:6px 12px;font-size:12px;font-weight:700;border-radius:8px;cursor:pointer;}
        .container{max-width:440px;margin:auto;padding:15px;}
        .hero{text-align:center;margin:15px 0 20px;}
        .hero h2 span{background:linear-gradient(90deg,#f59e0b,#ec4899);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
        .tabs{display:flex;background:#0f172a;border-radius:10px;padding:3px;margin-bottom:16px;}
        .tab-btn{flex:1;padding:9px;border:none;background:transparent;color:#94a3b8;font-weight:700;border-radius:7px;cursor:pointer;}
        .tab-btn.active{background:#2563eb;color:#fff;}
        .card{background:#0f172a;border:1px solid #1e293b;border-radius:14px;padding:18px;margin-bottom:20px;}
        .input-group{margin-bottom:12px;}
        .input-group label{display:block;font-size:11px;font-weight:700;color:#94a3b8;margin-bottom:5px;}
        .input-group input,.input-group select{width:100%;padding:11px;background:#070c18;border:1px solid #1e293b;border-radius:8px;color:#fff;outline:none;}
        .submit-btn{width:100%;padding:12px;background:#2563eb;border:none;border-radius:8px;color:#fff;font-weight:700;cursor:pointer;}
        .packages{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin:12px 0;}
        .pkg{background:#070c18;border:1px solid #1e293b;border-radius:10px;padding:12px;text-align:center;cursor:pointer;}
        .pkg.active{border-color:#2563eb;background:rgba(37,99,235,0.15);}
        .msg{display:none;padding:10px;border-radius:8px;font-size:12px;text-align:center;margin-top:10px;font-weight:600;}
        .err{background:rgba(239,68,68,0.2);color:#f87171;border:1px solid #ef4444;}
        .succ{background:rgba(34,197,94,0.2);color:#4ade80;border:1px solid #22c55e;}
        
        /* Player Info Card */
        .player-info-card{display:none;background:#111b33;border:1px solid #2563eb;border-radius:10px;padding:12px;margin:12px 0;align-items:center;gap:12px;}
        .player-avatar{width:46px;height:46px;border-radius:8px;border:1px solid #38bdf8;}
        .player-details h4{font-size:14px;color:#f8fafc;}
        .player-details p{font-size:11px;color:#94a3b8;}

        /* Popup Modal */
        .modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);backdrop-filter:blur(5px);z-index:200;align-items:center;justify-content:center;}
        .modal-content{background:#0e1626;border:1px solid #1e293b;padding:24px;border-radius:16px;width:90%;max-width:340px;position:relative;}
        .close-modal{position:absolute;top:12px;right:14px;color:#94a3b8;font-size:18px;cursor:pointer;}

        .qr-box{display:none;text-align:center;margin-top:15px;}
        .qr-img{width:180px;height:180px;background:#fff;padding:6px;border-radius:10px;margin:10px auto;}
        .float-tg{position:fixed;bottom:20px;right:20px;background:#0088cc;color:#fff;width:50px;height:50px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:24px;text-decoration:none;box-shadow:0 4px 15px rgba(0,136,204,0.4);z-index:100;}
    </style>
</head>
<body>
    <header class="header">
        <div class="logo"><i class="fa-solid fa-bolt"></i> FF LIKES</div>
        <div class="user-nav">
            {% if session.get('user') %}
                <div class="wallet-pill"><i class="fa-solid fa-coins"></i> <span id="userBal">{{ session.get('balance', 0) }}</span> Likes</div>
                <button class="btn-auth" onclick="logout()"><i class="fa-solid fa-right-from-bracket"></i></button>
            {% else %}
                <button class="btn-auth" onclick="openModal()"><i class="fa-solid fa-user"></i> Login / Register</button>
            {% endif %}
        </div>
    </header>

    <div class="container">
        <div class="hero">
            <h2>⚡ Boost <span>Your Profile</span></h2>
            <p style="font-size:12px;color:#94a3b8;">Real-time UID Verification & Instant Delivery</p>
        </div>

        <div class="tabs">
            <button class="tab-btn active" id="tb1" onclick="switchT('instant')"><i class="fa-solid fa-paper-plane"></i> Send Likes</button>
            <button class="tab-btn" id="tb2" onclick="switchT('auto')"><i class="fa-solid fa-infinity"></i> Daily AutoLikes</button>
        </div>

        <!-- Boost Like Section -->
        <div class="card">
            <h3 id="tTitle" style="font-size:16px;margin-bottom:12px;">⚡ Send Likes</h3>
            
            <div class="input-group">
                <label>FREE FIRE UID</label>
                <div style="display:flex; gap:6px;">
                    <input type="number" id="uid" placeholder="Enter Free Fire UID">
                    <button type="button" class="btn-auth" onclick="fetchPlayerInfo()" style="white-space:nowrap;"><i class="fa-solid fa-magnifying-glass"></i> Check</button>
                </div>
            </div>

            <div class="input-group">
                <label>REGION</label>
                <select id="region">
                    <option value="ind">India (IND)</option>
                    <option value="bd">Bangladesh (BD)</option>
                    <option value="pk">Pakistan (PK)</option>
                    <option value="sg">Singapore (SG)</option>
                </select>
            </div>

            <!-- Player Info Popup -->
            <div class="player-info-card" id="playerCard">
                <img id="pAvatar" class="player-avatar" src="" alt="Avatar">
                <div class="player-details">
                    <h4 id="pNickname">Unknown</h4>
                    <p>Level: <b id="pLevel">0</b> | Current Likes: <b id="pCurLikes" style="color:#38bdf8;">0</b></p>
                </div>
            </div>

            <div class="input-group">
                <label>NUMBER OF LIKES (From Wallet)</label>
                <input type="number" id="likesAmount" placeholder="e.g. 50, 100, 200">
            </div>

            <button class="submit-btn" onclick="sendBoost()"><span id="bTxt">Confirm & Boost Likes</span></button>
            <div class="msg err" id="bErr"></div>
            <div class="msg succ" id="bSucc"></div>
        </div>

        <!-- Redeem Coupon for Credits -->
        <div class="card">
            <h3 style="font-size:15px;margin-bottom:8px;"><i class="fa-solid fa-ticket"></i> Redeem Coupon Code</h3>
            <p style="font-size:12px;color:#94a3b8;margin-bottom:12px;">Add likes credits directly into your wallet.</p>
            <div class="input-group">
                <input type="text" id="couponCode" placeholder="Enter Coupon Code">
            </div>
            <button class="submit-btn" style="background:#4f46e5;" onclick="claimCoupon()">Claim to Wallet</button>
            <div class="msg err" id="cErr"></div>
            <div class="msg succ" id="cSucc"></div>
        </div>

        <!-- Packages & UTR Buy Section -->
        <div class="card" id="buy">
            <h3 style="font-size:15px;">📦 Buy Likes Package</h3>
            <div class="packages">
                <div class="pkg active" onclick="selP(this,'1.5K',120)"><b>1.5K</b><br><span style="color:#38bdf8;">₹120</span></div>
                <div class="pkg" onclick="selP(this,'3K',240)"><b>3K</b><br><span style="color:#38bdf8;">₹240</span></div>
                <div class="pkg" onclick="selP(this,'5K',490)"><b>5K</b><br><span style="color:#38bdf8;">₹490</span></div>
                <div class="pkg" onclick="selP(this,'10K',800)"><b>10K</b><br><span style="color:#38bdf8;">₹800</span></div>
            </div>
            <button class="submit-btn" onclick="showQR()"><i class="fa-solid fa-qrcode"></i> Generate QR Code</button>

            <div class="qr-box" id="qrSec">
                <img class="qr-img" id="qImg" src="" alt="QR">
                <p style="font-size:12px;color:#94a3b8;">Pay to: <b>{{ upi_id }}</b></p>
                <div class="input-group" style="text-align:left;margin-top:12px;">
                    <label>12-Digit UTR / Transaction ID</label>
                    <input type="number" id="utr" placeholder="Enter 12-digit UTR">
                </div>
                <button class="submit-btn" style="background:#16a34a;" onclick="submitPay()">Submit UTR Proof</button>
                <div class="msg err" id="pErr"></div>
                <div class="msg succ" id="pSucc"></div>
            </div>
        </div>
    </div>

    <!-- Login / Register Modal -->
    <div class="modal" id="authModal">
        <div class="modal-content">
            <span class="close-modal" onclick="closeModal()">&times;</span>
            <h3 id="mTitle" style="font-size:17px;margin-bottom:14px;">Login Account</h3>
            <div class="input-group">
                <label>Username</label>
                <input type="text" id="mUser" placeholder="Choose a username">
            </div>
            <div class="input-group">
                <label>Password</label>
                <input type="password" id="mPass" placeholder="Enter password">
            </div>
            <button class="submit-btn" id="mBtn" onclick="authAction()">Login</button>
            <p style="font-size:12px;color:#94a3b8;text-align:center;margin-top:10px;cursor:pointer;" id="mToggle" onclick="toggleAuth()">Don't have an account? Register</p>
            <div class="msg err" id="mErr"></div>
        </div>
    </div>

    <!-- Telegram Support Floating Button -->
    <a href="https://t.me/OxRehann" class="float-tg" target="_blank">
        <i class="fa-brands fa-telegram"></i>
    </a>

    <script>
        let isLogin = true, mode='instant', pLikes='1.5K', pAmt=120;

        function openModal() { document.getElementById('authModal').style.display = 'flex'; }
        function closeModal() { document.getElementById('authModal').style.display = 'none'; }
        function toggleAuth() {
            isLogin = !isLogin;
            document.getElementById('mTitle').innerText = isLogin ? 'Login Account' : 'Create Account';
            document.getElementById('mBtn').innerText = isLogin ? 'Login' : 'Register';
            document.getElementById('mToggle').innerText = isLogin ? "Don't have an account? Register" : "Already have an account? Login";
        }

        async function authAction() {
            let u = document.getElementById('mUser').value.trim(), p = document.getElementById('mPass').value.trim();
            let err = document.getElementById('mErr'); err.style.display = 'none';
            if(!u || !p) { err.innerText = "All fields required"; err.style.display = 'block'; return; }
            let endpoint = isLogin ? '/api/login' : '/api/register';
            let r = await fetch(endpoint, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({username:u, password:p})});
            let d = await r.json();
            if(d.success) { location.reload(); } else { err.innerText = d.message; err.style.display = 'block'; }
        }

        async function logout() { await fetch('/api/logout'); location.reload(); }

        async function fetchPlayerInfo() {
            let uid = document.getElementById('uid').value.trim();
            let reg = document.getElementById('region').value;
            let err = document.getElementById('bErr'); err.style.display = 'none';
            if(!uid) { err.innerText = "Enter UID first"; err.style.display = 'block'; return; }

            try {
                let res = await fetch(`/api/player-info?uid=${uid}&region=${reg}`);
                let data = await res.json();
                if(data.success) {
                    document.getElementById('pNickname').innerText = data.data.AccountInfo?.AccountNickname || "Found Player";
                    document.getElementById('pLevel').innerText = data.data.AccountInfo?.AccountLevel || "N/A";
                    document.getElementById('pCurLikes').innerText = data.data.AccountInfo?.AccountLikes || "0";
                    document.getElementById('pAvatar').src = data.data.AccountInfo?.AccountAvatarId ? `https://raw.githubusercontent.com/x-m-s/ff-assets/main/avatar/${data.data.AccountInfo.AccountAvatarId}.png` : "https://via.placeholder.com/50";
                    document.getElementById('playerCard').style.display = 'flex';
                } else {
                    err.innerText = data.message || "Player not found"; err.style.display = 'block';
                }
            } catch(e) {
                err.innerText = "Error fetching player info"; err.style.display = 'block';
            }
        }

        function switchT(m){
            mode = m;
            document.getElementById('tb1').classList.toggle('active', m === 'instant');
            document.getElementById('tb2').classList.toggle('active', m === 'auto');
            document.getElementById('tTitle').innerText = m === 'instant' ? '⚡ Send Likes' : '🌐 Daily AutoLikes';
            document.getElementById('bTxt').innerText = m === 'instant' ? 'Confirm & Boost Likes' : 'Enable Daily AutoLikes';
        }

        function selP(el, l, a){
            document.querySelectorAll('.pkg').forEach(p=>p.classList.remove('active'));
            el.classList.add('active');
            pLikes = l; pAmt = a;
        }

        function showQR(){
            let s = `upi://pay?pa={{ upi_id }}&pn=FF%20Likes&am=${pAmt}&cu=INR&tn=Likes_${pLikes}`;
            document.getElementById('qImg').src = `https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=${encodeURIComponent(s)}`;
            document.getElementById('qrSec').style.display = 'block';
        }

        async function submitPay(){
            let utr = document.getElementById('utr').value.trim();
            let err = document.getElementById('pErr'), succ = document.getElementById('pSucc');
            err.style.display = 'none'; succ.style.display = 'none';
            if(utr.length < 8) { err.innerText = "Please enter valid 12-digit UTR"; err.style.display = 'block'; return; }
            let r = await fetch('/api/submit-utr', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({utr:utr, amount:pAmt, package:pLikes})});
            let d = await r.json();
            if(d.success) { succ.innerText = d.message; succ.style.display = 'block'; } else { err.innerText = d.message; err.style.display = 'block'; }
        }

        async function claimCoupon(){
            let code = document.getElementById('couponCode').value.trim();
            let err = document.getElementById('cErr'), succ = document.getElementById('cSucc');
            err.style.display = 'none'; succ.style.display = 'none';
            if(!code) { err.innerText = "Enter coupon code"; err.style.display = 'block'; return; }
            let r = await fetch('/api/claim-coupon', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({coupon:code})});
            let d = await r.json();
            if(d.success) { 
                succ.innerText = d.message; succ.style.display = 'block';
                if(document.getElementById('userBal')) document.getElementById('userBal').innerText = d.new_balance;
            } else { err.innerText = d.message; err.style.display = 'block'; }
        }

        async function sendBoost(){
            let uid = document.getElementById('uid').value.trim();
            let reg = document.getElementById('region').value;
            let likes = parseInt(document.getElementById('likesAmount').value);
            let err = t.getElementById('bErr'), succ = document.getElementById('bSucc');
            err.style.display = 'none'; succ.style.display = 'none';

            if(!uid || !likes || likes <= 0) { err.innerText = "Enter UID & Likes quantity"; err.style.display = 'block'; return; }

            let r = await fetch('/api/boost-likes', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({uid, region:reg, likes, mode})});
            let d = await r.json();
            if(d.success) {
                succ.innerText = d.message; succ.style.display = 'block';
                if(document.getElementById('userBal')) document.getElementById('userBal').innerText = d.new_balance;
            } else { err.innerText = d.message; err.style.display = 'block'; }
        }
    </script>
</body>
</html>
"""

# ----------------- FLASK ROUTES ----------------- #
@app.route('/')
def home():
    if 'user' in session:
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute("SELECT balance FROM users WHERE username = ?", (session['user'],))
        row = c.fetchone()
        session['balance'] = row[0] if row else 0
        conn.close()
    return render_template_string(HTML, upi_id=UPI_ID)

@app.route('/api/register', methods=['POST'])
def register():
    d = request.get_json()
    user = d.get('username', '').strip().lower()
    pw = d.get('password', '').strip()
    if not user or not pw: return jsonify({"success": False, "message": "Invalid input"}), 400

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, balance) VALUES (?, ?, 0)", (user, pw))
        conn.commit()
        session['user'] = user
        session['balance'] = 0
        conn.close()
        return jsonify({"success": True})
    except:
        conn.close()
        return jsonify({"success": False, "message": "Username already exists!"}), 400

@app.route('/api/login', methods=['POST'])
def login():
    d = request.get_json()
    user = d.get('username', '').strip().lower()
    pw = d.get('password', '').strip()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username = ? AND password = ?", (user, pw))
    row = c.fetchone()
    conn.close()
    if row is not None:
        session['user'] = user
        session['balance'] = row[0]
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid username or password"}), 401

@app.route('/api/logout')
def logout():
    session.clear()
    return jsonify({"success": True})

@app.route('/api/player-info')
def player_info():
    uid = request.args.get('uid')
    region = request.args.get('region', 'ind')
    url = f"https://crystal-ffinfo.vercel.app/player-info?region={region}&uid={uid}"
    try:
        res = requests.get(url, timeout=5)
        if res.status_code == 200:
            return jsonify({"success": True, "data": res.json()})
        return jsonify({"success": False, "message": "Player UID not found!"}), 404
    except Exception as e:
        return jsonify({"success": False, "message": "Lookup service unavailable"}), 500

@app.route('/api/submit-utr', methods=['POST'])
def submit_utr():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Please Login first to submit payment!"}), 401

    d = request.get_json()
    username = session['user']
    msg = (
        f"💰 **NEW PAYMENT RECEIVED!**\n\n"
        f"👤 **User Account:** `{username}`\n"
        f"📦 **Pkg:** {d.get('package')} (₹{d.get('amount')})\n"
        f"🧾 **UTR:** `{d.get('utr')}`\n\n"
        f"👉 Add directly: `/addcredit {username} 1500`\n"
        f"👉 Or make code: `/ge <CODE> <LIKES> 1`"
    )
    try:
        bot.send_message(ADMIN_CHAT_ID, msg, parse_mode="Markdown")
        return jsonify({"success": True, "message": "Proof submitted! Admin will credit your account soon."})
    except:
        return jsonify({"success": False, "message": "Telegram alert failed"}), 500

@app.route('/api/claim-coupon', methods=['POST'])
def claim_coupon():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Please Login to claim coupon!"}), 401

    d = request.get_json()
    code = d.get('coupon', '').strip().upper()
    username = session['user']

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
        return jsonify({"success": False, "message": "Coupon Expired/Reached max limit!"}), 400

    c.execute("UPDATE coupons SET used_count = used_count + 1 WHERE code = ?", (code,))
    c.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (likes, username))
    c.execute("SELECT balance FROM users WHERE username = ?", (username,))
    new_bal = c.fetchone()[0]
    conn.commit()
    conn.close()

    session['balance'] = new_bal
    return jsonify({"success": True, "message": f"Successfully added {likes} Likes credit to wallet!", "new_balance": new_bal})

@app.route('/api/boost-likes', methods=['POST'])
def boost_likes():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Please Login first!"}), 401

    d = request.get_json()
    uid, reg, likes, mode = d.get('uid'), d.get('region'), int(d.get('likes', 0)), d.get('mode')
    username = session['user']

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username = ?", (username,))
    bal = c.fetchone()[0]

    if bal < likes:
        conn.close()
        return jsonify({"success": False, "message": f"Insufficient balance! Available: {bal} likes"}), 400

    c.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (likes, username))
    c.execute("INSERT INTO orders (username, uid, region, likes) VALUES (?, ?, ?, ?)", (username, uid, reg, likes))
    c.execute("SELECT balance FROM users WHERE username = ?", (username,))
    new_bal = c.fetchone()[0]
    conn.commit()
    conn.close()

    session['balance'] = new_bal

    try:
        bot.send_message(
            ADMIN_CHAT_ID,
            f"🚀 **NEW BOOST ORDER!**\n\n"
            f"👤 **User:** `{username}`\n"
            f"🎯 **UID:** `{uid}`\n"
            f"🌐 **Region:** `{reg}`\n"
            f"⚡ **Likes:** `{likes}`\n"
            f"🔄 **Type:** `{mode.upper()}`",
            parse_mode="Markdown"
        )
    except:
        pass

    return jsonify({"success": True, "message": f"Success! {likes} likes request submitted for UID {uid}.", "new_balance": new_bal})

if __name__ == '__main__':
    threading.Thread(target=bot.infinity_polling, daemon=True).start()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
    

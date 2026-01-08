from flask import Flask, request, jsonify
import requests
import sqlite3

app = Flask(__name__)

# --- CONFIG (Replace with your Meta Dashboard info) ---
ACCESS_TOKEN = "YOUR_META_TOKEN"
PHONE_ID = "YOUR_PHONE_NUMBER_ID"
VERIFY_TOKEN = "my_secret_token_123" # You choose this!

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('/home/yourusername/mysite/finance.db')
    conn.execute('CREATE TABLE IF NOT EXISTS tx (tid INTEGER PRIMARY KEY, user TEXT, amt REAL, status TEXT)')
    conn.commit()
    conn.close()

# --- WHATSAPP WEBHOOK (Listening for messages) ---
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Meta's verification step
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403

    # Handle incoming messages
    data = request.json
    try:
        msg = data['entry'][0]['changes'][0]['value']['messages'][0]
        sender = msg['from']
        text = msg['text']['body'].lower()

        if "paid" in text:
            # Simple logic to find numbers in the text
            amt = "".join(filter(str.isdigit, text))
            conn = sqlite3.connect('/home/yourusername/mysite/finance.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tx (user, amt, status) VALUES (?, ?, 'Pending')", (sender, amt))
            tid = cursor.lastrowid
            conn.commit()
            
            # Send Confirmation to User
            send_wa(sender, f"✅ Claim Logged! TID: {tid}. Admin will verify shortly.")
    except:
        pass
    return "OK", 200

def send_wa(to, body):
    url = f"https://graph.facebook.com/v21.0/{PHONE_ID}/messages"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}", "Content-Type": "application/json"}
    payload = {"messaging_product": "whatsapp", "to": to, "type": "text", "text": {"body": body}}
    requests.post(url, headers=headers, json=payload)

init_db()

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import json
import hmac
import hashlib

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('webhook_data.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cloud_run_webhooks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            payload JSON,
            headers JSON,
            timestamp DATETIME,
            source_ip TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/receive-webhook', methods=['POST'])
def handle_webhook():
    try:
        # Store all headers
        headers = dict(request.headers)
        
        # Get the payload
        payload = request.get_json(silent=True) or {}
        
        # Store source IP for debugging
        source_ip = request.remote_addr
        
        # Store in database
        conn = sqlite3.connect('webhook_data.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO cloud_run_webhooks 
            (payload, headers, timestamp, source_ip) 
            VALUES (?, ?, ?, ?)
        ''', (
            json.dumps(payload),
            json.dumps(headers),
            datetime.utcnow(),
            source_ip
        ))
        conn.commit()
        conn.close()
        
        return jsonify({
            'status': 'success',
            'message': 'Webhook received and stored',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Endpoint to view stored webhooks
@app.route('/view-webhooks', methods=['GET'])
def view_webhooks():
    try:
        conn = sqlite3.connect('webhook_data.db')
        c = conn.cursor()
        c.execute('''
            SELECT id, payload, headers, timestamp, source_ip 
            FROM cloud_run_webhooks 
            ORDER BY timestamp DESC 
            LIMIT 50
        ''')
        webhooks = [{
            'id': row[0],
            'payload': json.loads(row[1]),
            'headers': json.loads(row[2]),
            'timestamp': row[3],
            'source_ip': row[4]
        } for row in c.fetchall()]
        conn.close()
        
        return jsonify(webhooks), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=8080)
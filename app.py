from flask import Flask, jsonify, render_template
import mysql.connector
import random

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Sunny@6022',
    'database': 'cloud_monitor'
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/servers')
def get_servers():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.*, m.cpu_usage, m.memory_usage, m.disk_usage,
               m.network_in, m.network_out, m.recorded_at
        FROM servers s
        LEFT JOIN metrics m ON m.id = (
            SELECT id FROM metrics
            WHERE server_id = s.id
            ORDER BY recorded_at DESC LIMIT 1
        )
    """)
    servers = cursor.fetchall()
    for s in servers:
        if s.get('recorded_at'):
            s['recorded_at'] = str(s['recorded_at'])
    db.close()
    return jsonify(servers)

@app.route('/api/metrics/<int:server_id>')
def get_metrics(server_id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT cpu_usage, memory_usage, disk_usage, recorded_at
        FROM metrics
        WHERE server_id = %s
        ORDER BY recorded_at DESC
        LIMIT 20
    """, (server_id,))
    rows = cursor.fetchall()
    for r in rows:
        r['recorded_at'] = str(r['recorded_at'])
    db.close()
    return jsonify(rows[::-1])

@app.route('/api/alerts')
def get_alerts():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.*, s.name as server_name
        FROM alerts a
        JOIN servers s ON s.id = a.server_id
        WHERE a.resolved = FALSE
        ORDER BY a.created_at DESC
        LIMIT 10
    """)
    alerts = cursor.fetchall()
    for a in alerts:
        a['created_at'] = str(a['created_at'])
    db.close()
    return jsonify(alerts)

@app.route('/api/simulate')
def simulate():
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, name FROM servers")
    servers = cursor.fetchall()

    for server in servers:
        cpu     = round(random.uniform(10, 95), 1)
        mem     = round(random.uniform(30, 90), 1)
        disk    = round(random.uniform(20, 85), 1)
        net_in  = round(random.uniform(1, 500), 1)
        net_out = round(random.uniform(1, 300), 1)

        cursor.execute("""
            INSERT INTO metrics
            (server_id, cpu_usage, memory_usage, disk_usage, network_in, network_out)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (server['id'], cpu, mem, disk, net_in, net_out))

        if cpu > 85:
            cursor.execute("""
                INSERT INTO alerts (server_id, alert_type, message, severity)
                VALUES (%s, 'HIGH_CPU', %s, 'critical')
            """, (server['id'],
                  f"CPU usage at {cpu}% on {server['name']}"))

        if mem > 80:
            cursor.execute("""
                INSERT INTO alerts (server_id, alert_type, message, severity)
                VALUES (%s, 'HIGH_MEMORY', %s, 'warning')
            """, (server['id'],
                  f"Memory usage at {mem}% on {server['name']}"))

    db.commit()
    db.close()
    return jsonify({'status': 'ok', 'servers_updated': len(servers)})

if __name__ == '__main__':
    app.run(debug=True)
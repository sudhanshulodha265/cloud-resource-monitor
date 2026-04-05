from flask import Flask, jsonify, render_template
import sqlite3
import random

app = Flask(__name__)

# ---------------- DB ----------------
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        region TEXT,
        status TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        cpu_usage REAL,
        memory_usage REAL,
        disk_usage REAL,
        network_in REAL,
        network_out REAL,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        server_id INTEGER,
        alert_type TEXT,
        message TEXT,
        severity TEXT,
        resolved BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    cursor.execute("SELECT COUNT(*) FROM servers")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO servers (name, region, status)
            VALUES (?, ?, ?)
        """, [
            ('web-server-01', 'India-West', 'running'),
            ('web-server-02', 'India-East', 'running'),
            ('db-server-01',  'India-West', 'running'),
            ('app-server-01', 'India-South', 'warning')
        ])

    db.commit()
    db.close()

init_db()

# ---------------- ROUTES ----------------

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/api/servers')
def get_servers():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    SELECT s.*, m.cpu_usage, m.memory_usage, m.disk_usage,
           m.network_in, m.network_out, m.recorded_at
    FROM servers s
    LEFT JOIN metrics m 
    ON m.server_id = s.id
    AND m.recorded_at = (
        SELECT MAX(recorded_at)
        FROM metrics
        WHERE server_id = s.id
    )
    """)

    rows = cursor.fetchall()
    servers = [dict(row) for row in rows]

    db.close()
    return jsonify(servers)

@app.route('/api/metrics/<int:server_id>')
def get_metrics(server_id):
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT cpu_usage, memory_usage, disk_usage, recorded_at
        FROM metrics
        WHERE server_id = ?
        ORDER BY recorded_at DESC
        LIMIT 20
    """, (server_id,))

    rows = cursor.fetchall()
    data = [dict(row) for row in rows]

    db.close()
    return jsonify(data[::-1])

@app.route('/api/alerts')
def get_alerts():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT a.*, s.name as server_name
        FROM alerts a
        JOIN servers s ON s.id = a.server_id
        WHERE a.resolved = 0
        ORDER BY a.created_at DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()
    alerts = [dict(row) for row in rows]

    db.close()
    return jsonify(alerts)

@app.route('/api/simulate')
def simulate():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT id, name FROM servers")
    servers = cursor.fetchall()

    for server in servers:
        server = dict(server)

        cpu     = round(random.uniform(10, 95), 1)
        mem     = round(random.uniform(30, 90), 1)
        disk    = round(random.uniform(20, 85), 1)
        net_in  = round(random.uniform(1, 500), 1)
        net_out = round(random.uniform(1, 300), 1)

        cursor.execute("""
            INSERT INTO metrics
            (server_id, cpu_usage, memory_usage, disk_usage, network_in, network_out)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (server['id'], cpu, mem, disk, net_in, net_out))

        if cpu > 85:
            cursor.execute("""
                INSERT INTO alerts (server_id, alert_type, message, severity)
                VALUES (?, 'HIGH_CPU', ?, 'critical')
            """, (server['id'],
                  f"CPU usage at {cpu}% on {server['name']}"))

        if mem > 80:
            cursor.execute("""
                INSERT INTO alerts (server_id, alert_type, message, severity)
                VALUES (?, 'HIGH_MEMORY', ?, 'warning')
            """, (server['id'],
                  f"Memory usage at {mem}% on {server['name']}"))

    db.commit()
    db.close()

    return jsonify({'status': 'ok', 'servers_updated': len(servers)})

if __name__ == '__main__':
    app.run()
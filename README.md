# Cloud Resource Monitor

An OCI-inspired cloud monitoring dashboard built to simulate
real-time server resource tracking — similar to Oracle Cloud
Infrastructure (OCI) monitoring tools.

## Features
- Real-time CPU, Memory and Disk usage tracking
- Auto-generated alerts when CPU > 85% or Memory > 80%
- Interactive line charts with historical metrics
- REST API backend with Python Flask
- MySQL database with normalized schema (3 tables)
- Auto-refresh every 30 seconds

## Tech Stack
- Backend: Python, Flask, MySQL
- Frontend: HTML, CSS, JavaScript, Chart.js
- Database: MySQL (servers, metrics, alerts tables)
- Concept: Inspired by Oracle Cloud Infrastructure (OCI) monitoring

## How to Run
1. Import schema.sql into MySQL
2. Update DB password in app.py
3. Run: pip install flask mysql-connector-python
4. Run: python app.py
5. Open: http://localhost:5000

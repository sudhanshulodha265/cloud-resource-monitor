# Cloud Resource Monitor

An OCI-inspired cloud monitoring dashboard built to simulate
real-time server resource tracking — similar to Oracle Cloud Infrastructure (OCI) monitoring tools.

## Live Demo
https://cloud-resource-monitor.onrender.com/

## Features
- Real-time CPU, Memory and Disk usage tracking
- Auto-generated alerts when CPU > 85% or Memory > 80%
- Interactive line charts with historical metrics
- REST API backend with Python Flask
- SQLite database with automatic initialization
- Auto-refresh every 30 seconds

## Tech Stack
- Backend: Python, Flask
- Frontend: HTML, CSS, JavaScript, Chart.js
- Database: SQLite
- Deployment: Render
- Concept: Inspired by Oracle Cloud Infrastructure (OCI) monitoring

## How to Run
1. Install dependencies  
pip install -r requirements.txt  

2. Run the app  
python app.py  

3. Open  
http://localhost:5000

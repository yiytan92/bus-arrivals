from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import os, requests, logging, certifi
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, time

logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv('API_KEY')
# Add TaHoma configuration
TAHOMA_URL = os.getenv('TAHOMA_URL')
TAHOMA_PORT = os.getenv('TAHOMA_PORT')     # Replace with your TaHoma box port
TAHOMA_TOKEN = os.getenv('TAHOMA_TOKEN')
BLINDS_URL = os.getenv('BLINDS_URL')

RAINFALL_THRESHOLD = 0.1      # mm of rain that triggers blind closure
TAHOMA_HEADERS = {
    'accept': 'application/json',
    'Authorization': f'Bearer {TAHOMA_TOKEN}'
}

HEADERS = {
    'AccountKey': API_KEY,
    'accept': 'application/json'
}

# Add certificate configuration
CERT_PATH = Path(__file__).parent / "overkiz-root-ca-2048.crt"
if CERT_PATH.exists():
    # Create a custom cert bundle with both system certs and Overkiz cert
    VERIFY = str(CERT_PATH)
else:
    logger.warning("Overkiz certificate not found at: %s", CERT_PATH)
    VERIFY = True


def get_tahoma_api_version():
    logger.info("Test TaHoma connection by getting API version")
    try:
        url = f"https://{TAHOMA_URL}:{TAHOMA_PORT}/enduser-mobile-web/1/enduserAPI/apiVersion"
        response = requests.get(url, headers=TAHOMA_HEADERS, verify=VERIFY)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"TaHoma API error: {e}")
        return None

def close_blinds():
    logger.info("Close all blinds when rain is detected")
    try:
        url = f"https://{TAHOMA_URL}:{TAHOMA_PORT}/enduser-mobile-web/1/enduserAPI/exec/apply"

        # Use the "Blind all" device to control all blinds at once
        payload = {
            "label": "Close blinds - Rain detected",
            "actions": [
                {
                    "deviceURL": BLINDS_URL,  # Blind all
                    "commands": [{"name": "close", "parameters": []}]
                }
            ]
        }

        response = requests.post(url, json=payload, headers=TAHOMA_HEADERS, verify=VERIFY)
        response.raise_for_status()
        logger.info("Closing all blinds due to rain")
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Failed to close blinds: {e}")
        return None

@app.route('/')
def index():
    return render_template('index.html')  # Serves the HTML page

@app.route('/bus')
def get_bus_arrival():
    bus_stop_code = request.args.get('bus_stop_code')
    if not bus_stop_code:
        return jsonify({"error": "Missing 'bus_stop_code' parameter"}), 400

    url = f'https://datamall2.mytransport.sg/ltaodataservice/v3/BusArrival?BusStopCode={bus_stop_code}'
    try:
        logger.info("api key:", API_KEY)
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return jsonify(response.json())
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/rainfall')
def get_latest_rainfall():
    url = "https://api-open.data.gov.sg/v2/real-time/api/rainfall"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get("data", {})
        stations = data.get("stations", [])
        readings = data.get("readings", [])

        # Find the station with name "Woodlands Drive 62"
        station = next((s for s in stations if s.get("name") == "Woodlands Drive 62"), None)
        if not station:
            return jsonify({"error": "Station not found"}), 404

        station_id = station.get("id")

        # Find the latest reading for this station
        for reading in readings:
            for d in reading.get("data", []):
                if d.get("stationId") == station_id:
                    rainfall_value = d.get("value", 0)
                    if rainfall_value > RAINFALL_THRESHOLD:
                        close_blinds()
                    return jsonify({
                        "station": station,
                        "timestamp": reading.get("timestamp"),
                        "rainfall": rainfall_value,
                        "unit": reading.get("readingUnit")
                    })
        return jsonify({"error": "Reading not found for station"}), 404
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

# Add a test endpoint
@app.route('/tahoma/version')
def tahoma_version():
    version = get_tahoma_api_version()
    if version:
        close_blinds()
        return jsonify(version)
    return jsonify({"error": "Failed to connect to TaHoma"}), 500

def schedule_blinds():
    """Schedule blinds to close at 9 PM daily"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        close_blinds,
        trigger='cron',
        hour=21,  # 24-hour format, 21 = 9 PM
        minute=0,
        id='close_blinds_night',
        name='Close blinds at night',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Scheduled blind closure for 9 PM daily")

if __name__ == '__main__':
    # Start the scheduler before running the Flask app
    schedule_blinds()
    app.run(host='0.0.0.0', port=3888)

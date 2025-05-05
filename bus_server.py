from flask import Flask, jsonify, request, render_template
from dotenv import load_dotenv
import os, requests, logging

logger = logging.getLogger(__name__)

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv('API_KEY')

HEADERS = {
    'AccountKey': API_KEY,
    'accept': 'application/json'
}

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3888)

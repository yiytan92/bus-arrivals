# Bus Display with TaHoma Integration

A Flask application that displays bus arrival times and controls Somfy TaHoma blinds based on weather conditions.

## Features
- Real-time bus arrival display
- Weather monitoring (rainfall at Woodlands Drive 62)
- Automated blind control based on rainfall
- Scheduled blind closure at 9 PM daily
- Secure TaHoma API integration

## Prerequisites
- Python 3.x
- Raspberry Pi (optional, for display)
- Somfy TaHoma box with developer mode enabled
- LTA DataMall API access
- data.gov.sg API access

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd busdisplay
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```bash
API_KEY=<your_datamall_api_key>
TAHOMA_URL=<your_tahoma_gateway>
TAHOMA_PORT=<your_tahoma_port>
TAHOMA_TOKEN=<your_bearer_token>
BLINDS_URL=<your_blinds_device_url>
```

4. Download the Overkiz certificate:
```bash
curl -o overkiz-root-ca-2048.crt https://ca.overkiz.com/overkiz-root-ca-2048.crt
```

## Configuration

### Bus Stops
Configure your bus stops in `templates/index.html`:
```javascript
const busStops = [
    { code: 'XXXXX', label: 'Stop Name 1', elementId: 'bus-stop-1' },
    { code: 'XXXXX', label: 'Stop Name 2', elementId: 'bus-stop-2' },
    { code: 'XXXXX', label: 'Stop Name 3', elementId: 'bus-stop-3' }
];
```

### Weather Settings
```python
RAINFALL_THRESHOLD = 0.2  # mm of rain that triggers blind closure
```

### Scheduled Tasks
- Blind closure: Daily at 9 PM
- Weather check: Every 5 minutes
- Bus arrival updates: Every 60 seconds

## Usage

1. Start the server:
```bash
python bus_server.py
```

2. Access the display:
```
http://localhost:3888
```

## API Endpoints

- `GET /` - Main display interface
- `GET /bus?bus_stop_code=<code>` - Bus arrival times
- `GET /rainfall` - Current rainfall data
- `GET /tahoma/version` - TaHoma connection test
- `GET /schedule` - View scheduled tasks

## Security Notes

- Store sensitive data in `.env` (not in version control)
- Use HTTPS for all API calls
- Verify Overkiz certificate for TaHoma communication
- Keep TaHoma bearer token secure

## Display Setup

For Raspberry Pi with 800x480 screen:
```bash
chromium-browser --kiosk http://localhost:3888
```

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License
[MIT License]

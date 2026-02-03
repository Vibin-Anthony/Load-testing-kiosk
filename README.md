Kiosk Endurance & Load Testing (Raspberry Pi)
Overview

This project includes a real end-to-end endurance testing framework for the Raspberry Pi–based kiosk application.
Instead of synthetic multi-user load testing (which is unrealistic for kiosks), this approach simulates actual kiosk usage over long durations (hours/days) and captures system stability metrics.

The test repeatedly performs a full checkout flow (loyalty scan → product scan → checkout) at fixed intervals while monitoring CPU, memory, and temperature.

What This Test Covers

Real kiosk UI flow (no mocks)

Loyalty card scan

Product barcode scan

Checkout & confirmation

API + DB interactions

Long-run stability (memory leaks, crashes)

CPU, RAM, and temperature monitoring

Suitable for 24-hour / 72-hour soak tests

📁 Key Files
testsuite/
├── endurance_runner.py     # Main runner for long-duration tests
├── checkout_flow.py        # Reusable checkout transaction logic
├── system_metrics.py       # CPU, RAM, temperature logging
├── utils/
│   └── util.py             # Barcode injection, UI actions, helpers

⚙️ How It Works (High Level)

endurance_runner.py

Runs for a configurable duration (e.g., 5 min / 24 hrs)

Triggers a checkout every fixed interval (default: 2 minutes)

Logs success/failure of each transaction

checkout_flow.py

Performs a complete kiosk checkout using existing automation utilities

system_metrics.py

Captures CPU usage, memory usage, and device temperature during the run

Barcode scanning is emulated using Linux evdev (uinput) to generate real keyboard events, matching actual scanner behavior.

🛠 Prerequisites (Raspberry Pi)
System Packages
sudo apt update
sudo apt install -y \
  python3 \
  python3-venv \
  python3-evdev \
  tesseract-ocr

Required Permissions

The kiosk user must have permission to write to /dev/uinput.

sudo usermod -aG input pi


Create a udev rule:

sudo nano /etc/udev/rules.d/99-uinput.rules


Add:

KERNEL=="uinput", MODE="0660", GROUP="input"


Reload rules:

sudo udevadm control --reload-rules
sudo udevadm trigger
sudo reboot

🐍 Python Setup

Create a virtual environment with system packages enabled:

python3 -m venv venv --system-site-packages
source venv/bin/activate


Install Python dependencies:

pip install psutil pytesseract pillow requests

▶️ Running a Dry Test (Recommended)

Edit endurance_runner.py:

INTERVAL = 120      # 2 minutes
DURATION = 5 * 60   # 5 minutes (dry run)


Run:

python3 endurance_runner.py


Expected:

2 checkout transactions

Logs created:

endurance_test.log

system_metrics.log

▶️ Running a 24-Hour Endurance Test

Update:

DURATION = 24 * 60 * 60


Run:

python3 endurance_runner.py

📊 Logs & Analysis

endurance_test.log

Transaction start/end

Success / failure

system_metrics.log

CPU usage

Memory usage

Temperature

These logs are used to identify:

Memory leaks

Performance degradation

Thermal throttling

Long-run stability issues
# Kiosk Endurance & Load Testing (Raspberry Pi)

This project implements a **real end-to-end endurance testing framework** for a Raspberry Pi–based kiosk application.

Instead of unrealistic multi-user load simulation, this framework reproduces **actual kiosk usage patterns** over long durations (hours/days) and records system stability metrics such as **CPU, memory, and temperature**.

The test continuously performs:

**Loyalty Scan → Product Scan → Checkout → Confirmation**

making it ideal for **24 / 48 / 72 hour soak testing** of production kiosks.

---

## Architecture

Kiosk UI (Real Application)  
↓  
Automation Utilities (Barcode + UI Actions)  
↓  
Checkout Flow Logic  
↓  
Endurance Runner (Timed Loop)  
↓  
System Metrics Logger (CPU / RAM / Temperature)

---

## What This Test Covers

- Real kiosk UI flow (no mocks)
- Loyalty card scanning
- Product barcode scanning
- Checkout and confirmation
- API and database interaction
- Long-run stability validation
- CPU, RAM, and temperature monitoring

---

## Project Structure

```text
testsuite/
├── endurance_runner.py
├── checkout_flow.py
├── system_metrics.py
└── utils/
    └── util.py
```

---

## How It Works

### endurance_runner.py
- Runs for configurable duration (5 min / 24 hrs / 72 hrs)
- Executes checkout every fixed interval (default: 2 minutes)
- Logs success and failure of each run

### checkout_flow.py
- Performs complete kiosk checkout using automation helpers

### system_metrics.py
- Records CPU, memory usage, and temperature during execution

### Barcode Simulation
Uses **Linux evdev (uinput)** to generate real keyboard events exactly like a physical barcode scanner.

---

## Prerequisites (Raspberry Pi)

### Install Required Packages

```bash
sudo apt update
sudo apt install -y \
  python3 \
  python3-venv \
  python3-evdev \
  tesseract-ocr
```

---

## Required Permissions

Allow kiosk user to access `/dev/uinput`:

```bash
sudo usermod -aG input pi
```

Create udev rule:

```bash
sudo nano /etc/udev/rules.d/99-uinput.rules
```

Add:

```
KERNEL=="uinput", MODE="0660", GROUP="input"
```

Reload and reboot:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
sudo reboot
```

---

## Python Environment Setup

```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
pip install psutil pytesseract pillow requests
```

---

## Running a Dry Test (Recommended)

Edit in `endurance_runner.py`:

```python
INTERVAL = 120
DURATION = 5 * 60
```

Run:

```bash
python3 endurance_runner.py
```

Expected:
- 2 successful checkout cycles
- Log files generated

---

## Running a 24-Hour Endurance Test

Update:

```python
DURATION = 24 * 60 * 60
```

Run:

```bash
python3 endurance_runner.py
```

---

## Logs & Analysis

### endurance_test.log
- Transaction start/end
- Success / failure

### system_metrics.log
- CPU usage
- Memory usage
- Temperature

These logs help identify:

- Memory leaks
- Performance degradation
- Thermal throttling
- Long-duration stability issues

---

## Use Case

This framework validates the stability of:

**Hardware + OS + Application + API + Database** together under real kiosk usage.

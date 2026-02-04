#!/bin/bash

TESTSUITE_PATH="/home/pi/Desktop/PiMicroMarket/testsuite"
VENV_PATH="$TESTSUITE_PATH/venv/bin/activate"
LOG_FILE="/var/log/kiosk_test/checkout.log"

BOOT_WAIT=20   # seconds to wait before starting test

echo "[$(date)] 🔥 Starting endurance checkout loop" | tee -a "$LOG_FILE"

# --- Kiosk startup wait ---
echo "[$(date)] ⏳ Waiting ${BOOT_WAIT}s for kiosk startup..." | tee -a "$LOG_FILE"
sleep $BOOT_WAIT
echo "[$(date)] ✅ Kiosk startup wait completed" | tee -a "$LOG_FILE"

# --- Activate test environment ---
cd "$TESTSUITE_PATH" || exit 1
source "$VENV_PATH"

# --- Run endurance test ---
python3 endurance_runner.py >> "$LOG_FILE" 2>&1

EXIT_CODE=$?
deactivate

echo "[$(date)] 🏁 Endurance runner exited with code $EXIT_CODE" | tee -a "$LOG_FILE"
exit $EXIT_CODE

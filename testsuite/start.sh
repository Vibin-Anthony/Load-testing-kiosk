#!/bin/bash
#set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#sudo systemctl restart start-touch &&

if  [ -e "$SCRIPT_DIR/.venv/bin/activate" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
    sudo modprobe uinput || true

    # Only create the device if it does not already exist
    if [ ! -e /dev/uinput ]; then
        sudo mknod /dev/uinput c 10 223
    fi

    mkdir -p /tmp/testsuite_screenshots
    #sudo unshare --mount --map-root-user bash -c "chmod 000 /dev/input/event5"
    # while pgrep -f pytest > /dev/null; do
    # echo "Waiting for existing pytest process to finish..."
    # sleep 5
    # done
    sudo iptables -F
    pkill -9 -f "/mm(\s|$)" 2>/dev/null || true; pkill -9 -f "/buddy(\s|$)" 2>/dev/null || true; pkill -9 -f "/basic-pub-sub(\s|$)" 2>/dev/null || true; sudo systemctl stop wdt-buddy.service 2>/dev/null || true &&
    /home/pi/Desktop/PiMicroMarket/start.sh &> /dev/null &
    sleep 20
    pytest "$SCRIPT_DIR" --junit-xml="$SCRIPT_DIR/micromarket-report.xml"
    deactivate
else
    sudo mount -o remount,rw /
    echo "Pytest is not installed, setting up testsuite."
    sudo apt install python3-venv evemu-tools tesseract-ocr xdotool xvfb iptables -y
    python3 -m venv $SCRIPT_DIR/.venv
    source "$SCRIPT_DIR/.venv/bin/activate"
    pip3 install -r requirements.txt
    source $SCRIPT_DIR/start.sh
fi

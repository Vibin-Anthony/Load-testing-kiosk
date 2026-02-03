import uinput
import time
import subprocess
import os,argparse
import pytesseract
import requests
import uuid
from utils.db import db_path

from PIL import Image

import sqlite3
conn = sqlite3.connect(db_path)

import evdev

from typing import Literal

import random
import os
from PIL import Image
import pytesseract
import random

# API_URL = os.environ['API_URL']
# API_AUTH = os.environ["API_AUTH"]

API_URL="https://staging.hercules2.usconnectme.com/"
API_AUTH="M5qnanewFHvtRUwbTHdPcruB4KGX1qzv"

async def inject_barcode(barcode):
    res = subprocess.run(
    "sudo -u pi bash -ic \"ps aux | grep -E 'X(org|vfb)' | grep -oP ' :[0-9]+' | head -n1\"",
    shell=True, capture_output=True, text=True
    )
    run_command(f"DISPLAY=:0 xdotool type '{barcode}' && DISPLAY=:0 xdotool key Return")
    

def run_command(command):
    """Runs a shell command and ensures it completes."""
    subprocess.run(command, shell=True, check=True)

def get_text_from_screen(name="temp"):
    if name != "temp":
        capture_screenshot(name)
    else:
        capture_screenshot("temp")
    
    time.sleep(0.5)
    image = f"/tmp/testsuite_screenshots/{name}.png"
    gray = Image.open(image).convert("L")

    filename = "/tmp/temp.png"
    gray.save(filename)

    text = pytesseract.image_to_string(gray)

    os.remove(filename)

    res = text.split('\n')
    return res

async def delete_account_details_from_db(card_number):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accountdetails WHERE oan_number = ?", (card_number,))
    conn.commit()

async def fetch_account_details_from_db(card_number):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accountdetails WHERE oan_number = ?", (card_number,))
    result = cursor.fetchone()
    return result  

async def fetch_account_details_from_api(card_number):
    api_url = f"{API_URL}/migrate/account/{card_number}"
    headers = {
        "Authorization": API_AUTH,
        "Content-Type": "application/json"
    }
    response = requests.get(api_url, headers=headers)
    return response.json()


def fetch_product_barcode():
    cursor = conn.cursor()
    cursor.execute("SELECT barcode FROM catalog;")
    barcodes = cursor.fetchall()

    # Filter out empty/null/invalid barcodes
    valid_barcodes = [b[0] for b in barcodes if b and b[0] and b[0].strip()]

    if not valid_barcodes:
        return None

    random_barcode = random.choice(valid_barcodes)

    # Cut off everything after the first semicolon
    clean_barcode = random_barcode.split(';')[0]

    return clean_barcode

def fetch_product_barcodes_multiple():
    cursor = conn.cursor()
    cursor.execute("SELECT barcode FROM catalog LIMIT 5 OFFSET 32;")
    result = cursor.fetchmany(5)
    #result = ['720495902152','017869807015', '720495902152', '034000544134', '029500267621' ]
    #return result
    return [row[0] for row in result ] if result else None

def fetch_product_details(barcode):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM catalog WHERE barcode = ?", (barcode,))
    result = cursor.fetchone()
    return result if result else None

def capture_screenshot(name):
    if not os.path.exists('/tmp/testsuite_screenshots'):
        os.makedirs('/tmp/testsuite_screenshots')
        
    res = subprocess.run(
    "sudo -u pi bash -ic \"ps aux | grep -E 'X(org|vfb)' | grep -oP ' :[0-9]+' | head -n1\"",
    shell=True, capture_output=True, text=True
    )
    display = res.stdout.strip()
    subprocess.run(f"DISPLAY=:0 import -window root /tmp/testsuite_screenshots/{name}.png",shell=True, text=True)
    subprocess.run(f"convert /tmp/testsuite_screenshots/{name}.png -resize 50% -quality 0 /tmp/testsuite_screenshots/{name}.png", shell=True, text=True)

def find_touchscreen():
    """
    Robust touchscreen detection for maXTouch and similar devices.
    """
    for path in evdev.list_devices():
        device = evdev.InputDevice(path)
        name = device.name.lower()

        print(f'device {path}, name "{device.name}"')

        # ✅ Primary match: known touchscreen keywords
        if (
            "maxtouch" in name
            or "digitizer" in name
            or "touch" in name
        ):
            print(f"Using touchscreen device (name match): {path}")
            return path

        # ✅ Secondary match: ABS capability (fallback)
        caps = device.capabilities(verbose=True)
        abs_caps = caps.get(evdev.ecodes.EV_ABS, [])

        if abs_caps:
            print(f"Using touchscreen device (ABS fallback): {path}")
            return path

    print("Touchscreen not found!")
    return None

def click_button(param, retries=3, delay=1):
    event_device = find_touchscreen()

    if event_device is None:
        raise RuntimeError("❌ Touchscreen device not found. Cannot click button.")

    evemu_file = f"/home/pi/Desktop/PiMicroMarket/testsuite/buttons/{param}.evemu"

    if not os.path.exists(evemu_file):
        raise FileNotFoundError(f"❌ evemu file not found: {evemu_file}")

    for attempt in range(1, retries + 1):
        print(f"Click attempt {attempt} for button '{param}'")

        subprocess.run(
            ["sudo", "evemu-play", event_device],
            input=open(evemu_file, "rb").read(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        time.sleep(delay)

        # Optional: break early if UI text changes
        # (keeps it simple for now)

    return True

async def send_lynk_request(card_number):
    kiosk_url = "http://localhost:31374" 

    payload = {
    "command": "BeginSale",
    "data": {
    "isLoyalty": True,
    "loyaltyCardNumber": f"{card_number}"
        }
    }

    response = requests.post(kiosk_url, json=payload)
    return response.json()

async def add_bill_count() :
    cursor = conn.cursor()
    cursor.execute("INSERT INTO bill_count (denomination, count, amount) VALUES (5, 2, 10);")
    conn.commit()

def poll_offline_mode():
    cursor = conn.cursor()
    cursor.execute("SELECT f_reboot_no_internet FROM reboot_flags")
    result = cursor.fetchone()
    return result[0] if result else None

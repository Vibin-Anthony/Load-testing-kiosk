# import pytest
# import logging
# from utils.util import run_command, get_text_from_screen
# import subprocess
# import time

# logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# def is_process_running(process_name):
#     result = subprocess.run(f"pgrep -x {process_name}", shell=True, stdout=subprocess.PIPE)
#     return result.returncode == 0  # True if process is running

# def setup_micromarket():
#     logging.info("Setting up Xvfb and Kiosk Software...")

#     # Start Xvfb in background
#     run_command("Xvfb :99 -screen 0 1080x1920x24 &")
#     time.sleep(2)  # Wait for Xvfb to be ready

#     # Check if Xvfb started properly
#     if not is_process_running("Xvfb"):
#         pytest.exit("Xvfb failed to start on :99")

#     # Launch kiosk software in the virtual display
#     run_command("cd ~/Desktop/PiMicroMarket/ && DISPLAY=:99 nohup ./buddy > /dev/null 2>&1 &")
#     logging.info("Waiting 20 secs for kiosk software to setup...")
#     time.sleep(20)

#     # Check if all expected processes are running
#     if is_process_running("Xvfb") and is_process_running("buddy") and is_process_running("mm"):
#         logging.info("Kiosk Software started successfully")
#     else:
#         pytest.exit("Critical test failed: micromarket is not running")

# def test_startup():
#     setup_micromarket()

import pytest
import logging
from utils.util import run_command, get_text_from_screen
import subprocess
import time

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def is_process_running(process_name):
    result = subprocess.run(f"pgrep -x {process_name}", shell=True, stdout=subprocess.PIPE)
    return result.returncode == 0  # True if process is running

def setup_micromarket():
    if not is_process_running("mm"):
        run_command("startx > /dev/null 2>&1 &")
        while is_process_running("mm") is not True:
            time.sleep(2)
        logging.info("Waiting 20 secs for kiosk software to setup...")
        time.sleep(20)

    if is_process_running("Xorg") and is_process_running("buddy") and is_process_running("mm"):
        logging.info("Kiosk Software started successfully")
        time.sleep(1)
    
    else:
        pytest.exit("Critical test failed: micromarket is not running")

def test_startup():
    setup_micromarket()

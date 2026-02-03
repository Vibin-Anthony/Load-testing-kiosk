import pytest
import time
import logging
from utils.util import click_button, get_text_from_screen, inject_barcode

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867657"])
async def test_checkout_success(card_number):

    # Login using loyalty card only
    await inject_barcode(card_number)
    time.sleep(3)

    # Open feedback screen
    click_button("feedback_button")
    time.sleep(1.5)   # allow keyboard to fully load

    # Type text slowly so ENTER is NOT triggered immediately
    keys = ["Q", "A", "feedback_space", "T", "E", "S", "T", "I", "N", "G"]

    for key in keys:
        click_button(key)
        time.sleep(0.4)   # delay between each key

    # Now click Enter BUT after a safe delay
    time.sleep(1)          # ensure no accidental popup / animation
    click_button("feeback_enter")

    time.sleep(5)

    # Close any popup
    click_button("homescreen_cancel")


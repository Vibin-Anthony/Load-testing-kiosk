import pytest
from utils.util import inject_barcode, get_text_from_screen
from utils.util import click_button, add_bill_count
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# STC006 - Collection flow
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["SERVICE62"])
async def test_collection(card_number):

    # Add bills so popup appears
    await add_bill_count()
    time.sleep(0.5)

    # Scan SERVICE62
    await inject_barcode(card_number)
    time.sleep(1)

    # Click "Set As Collected"
    click_button("set-as-collected")
    time.sleep(2)

    # Click "Continue" on success popup
    click_button("collection_success_continue")  # <-- Your new recorded button
    time.sleep(2)

    #logging.info("extracting text...")
    #text = get_text_from_screen()

    # Close any popup
    click_button("cancel")

    # Validate
    #assert any("Bills Collected" in line for line in text), "No bills was found"

import pytest
from utils.util import inject_barcode, get_text_from_screen, run_command
from utils.util import click_button, add_bill_count
import time
import logging
logging.basicConfig(level=logging.INFO, format="%(ascasyncio)s - %(levelname)s - %(message)s")

# STC006
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["SERVICE62"])
async def test_collection_time(card_number):
    await add_bill_count()
    time.sleep(0.5)
    await inject_barcode(card_number)
    time.sleep(0.5)
    click_button("collected")
    time.sleep(2)
    logging.info("extracting text...")
    text = get_text_from_screen()
    click_button("cancel")
    assert any("Bills Collected" in line for line in text), "No bills was found"

# STC006
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["SERVICE62"])
async def test_collection_no_bills(card_number):
    await inject_barcode(card_number)
    time.sleep(0.5)
    click_button("collection_nobill")
    time.sleep(2)
    logging.info("extracting text...")
    text = get_text_from_screen()
    assert any("No bills" in line for line in text), "No bills was found"

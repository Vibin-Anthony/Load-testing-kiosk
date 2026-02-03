import pytest
import os
import time
from utils.util import get_text_from_screen
from utils.util import capture_screenshot
import logging
from utils.util import click_button
from utils.util import inject_barcode
from utils.util import fetch_product_barcode
from utils.util import fetch_product_details, fetch_account_details_from_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867655"])
async def test_checkout_success(card_number):
    await inject_barcode(card_number)
    time.sleep(4)

    product_barcode = fetch_product_barcode()
    assert product_barcode, "❌ No barcode found in catalog"

    await inject_barcode(product_barcode)

    # ---- WAIT FOR AUTO CHECKOUT ----
    MAX_WAIT = 30  # seconds
    POLL_INTERVAL = 3
    elapsed = 0

    checkout_detected = False

    while elapsed < MAX_WAIT:
        text = " ".join(get_text_from_screen()).lower()
        if "thank" in text:
            checkout_detected = True
            break

        time.sleep(POLL_INTERVAL)
        elapsed += POLL_INTERVAL

    assert checkout_detected, f"❌ Auto-checkout not detected within {MAX_WAIT}s. OCR: {text}"

# TC004
#@pytest.mark.asyncio
#@pytest.mark.parametrize("card_number", ["29230353867656"])
#async def test_checkout_failure(card_number):
    #product_barcode = fetch_product_barcode()
    #print(product_barcode)
    #assert product_barcode, "❌ No barcode found in the catalog!"
    #await inject_barcode(product_barcode)
    #time.sleep(3)
    #click_button("checkout")
    #time.sleep(1)
    #logging.info("extracting text from the image")
    #text = get_text_from_screen()
    #click_button("continue_checkout_failure")
    #click_button("cancel")
    #assert "Thank You!" not in text, "Checkout expect to be failed"
    #time.sleep(5)

#@pytest.mark.asyncio
#@pytest.mark.parametrize("card_number", ["29230353867655"])
#async def test_checkout_multiple_quantity(card_number):
#    await inject_barcode(card_number)
#    logging.info("waiting to access the account info")
#    time.sleep(4)

#    db_data_old = await fetch_account_details_from_db(card_number)
#    if db_data_old is not None :
#        logging.info("Account details successfully fetched from DB.")
    
#    old_balance = db_data_old[5]

#    product_barcodes = fetch_product_barcodes_multiple()
#    assert product_barcodes, "❌ No barcode found in the catalog!"
#    for _ in range(4):
#        for barcode in product_barcodes:
#            await inject_barcode(barcode)
#            time.sleep(0.5)

#    click_button("checkout")
#    time.sleep(0.5)
#    logging.info("extracting text from the image")
#    text = get_text_from_screen()
#    assert "Thank You!" in text, "Failed to checkout"
#    time.sleep(4)
    # db_data = await fetch_account_details_from_db(card_number)
    # if db_data is not None :
    #     logging.info("Account details successfully fetched from DB.")

    # new_balance = db_data[5]
    
    # assert db_data is not None, "Account not found in database"
    # expected_balance = old_balance - int(product_price)
    # assert expected_balance != new_balance, "balance mismatched"
# STC_028
# @pytest.mark.asyncio
# @pytest.mark.parametrize("card_number", ["29230353867655"])
# async def test_checkout_hot_button(card_number):
#     await inject_barcode(card_number)
#     logging.info("waiting to access the account info")
#     hotbutton = get_text_from_screen()
#     time.sleep(4)
#     click_button("hot-button")
#     time.sleep(0.2)
#     click_button("checkout")
#     time.sleep(0.5)
#     logging.info("extracting text from the image")
#     text = get_text_from_screen()
#     assert "Thank You!" in text, "Failed to checkout"


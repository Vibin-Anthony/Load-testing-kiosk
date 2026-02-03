import time
import logging
from utils.util import inject_barcode
from utils.util import click_button
from utils.util import fetch_product_barcode
from utils.util import get_text_from_screen

async def run_checkout(card_number):
    logging.info("Starting checkout flow")

    await inject_barcode(card_number)
    time.sleep(4)

    product_barcode = fetch_product_barcode()
    if not product_barcode:
        raise Exception("No product barcode found")

    await inject_barcode(product_barcode)
    time.sleep(2)

    click_button("checkout")
    time.sleep(1)

    text = get_text_from_screen()
    if "Thank You!" not in text:
        raise Exception("Checkout failed")

    time.sleep(5)
    logging.info("Checkout successful")

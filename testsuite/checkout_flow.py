import time
import logging
from utils.util import (
    inject_barcode,
    click_button,
    fetch_product_barcode,
    get_text_from_screen,
)

def now():
    return time.strftime("%H:%M:%S")

logging.basicConfig(level=logging.INFO)


def classify_checkout_screen(text):
    text_blob = " ".join(line.lower() for line in text)

    if "thank you" in text_blob:
        return "SUCCESS"

    if "pay by credit" in text_blob or "charge amount" in text_blob:
        return "PAYMENT_SCREEN"

    if "invalid" in text_blob or "error" in text_blob:
        return "ERROR"

    return "UNKNOWN"


def wait_for_checkout_result(timeout=30, interval=2):
    start = time.time()

    while time.time() - start < timeout:
        text = get_text_from_screen()
        result = classify_checkout_screen(text)

        if result != "UNKNOWN":
            return result, text

        time.sleep(interval)

    return "TIMEOUT", get_text_from_screen()


async def run_checkout(card_number, txn_id):
    logging.info(f"[{now()}] ▶ Transaction {txn_id} | Card: {card_number}")

    # --- Stabilize kiosk input ---
    time.sleep(15)

    # --- Scan loyalty card ---
    logging.info(f"[{now()}] ⏳ Scanning loyalty card")
    await inject_barcode(card_number)
    time.sleep(6)
    logging.info(f"[{now()}] ✅ Loyalty scanned")

    # --- Scan product ---
    product_barcode = fetch_product_barcode()
    if not product_barcode:
        raise Exception("No product barcode found")

    logging.info(f"[{now()}] ⏳ Scanning product: {product_barcode}")
    await inject_barcode(product_barcode)
    time.sleep(2)
    logging.info(f"[{now()}] ✅ Product scanned")

    # --- Checkout ---
    logging.info(f"[{now()}] ⏳ Clicking checkout")
    click_button("checkout")
    time.sleep(2)

    # --- Result validation ---
    logging.info(f"[{now()}] ⏳ Waiting for checkout result")
    result, text = wait_for_checkout_result()

    if result == "SUCCESS":
        logging.info(f"[{now()}] ✅ Checkout SUCCESS")
        return "SUCCESS"

    if result == "PAYMENT_SCREEN":
        logging.warning(f"[{now()}] ⚠ Checkout stopped at payment screen")
        logging.warning(f"[{now()}] OCR: {text}")
        return "PAYMENT"

    logging.error(f"[{now()}] ❌ Checkout FAILED")
    logging.error(f"[{now()}] OCR: {text}")
    raise Exception("Checkout failed")

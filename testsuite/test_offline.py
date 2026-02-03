import pytest
from utils.util import poll_offline_mode,inject_barcode, get_text_from_screen, run_command, fetch_product_barcode, delete_account_details_from_db
from utils.util import click_button, fetch_account_details_from_api, fetch_account_details_from_db
import time
import logging
import os

logging.basicConfig(level=logging.INFO, format="%(ascasyncio)s - %(levelname)s - %(message)s")

def set_os_status(status):
    if status == "offline":
        logging.info("Entering offline mode")
        run_command("sudo iptables -A OUTPUT -p icmp -j DROP")
        time.sleep(30)
        # run_command("sudo iptables -A OUTPUT -p tcp --dport 443 -j DROP")
        if not os.path.exists("/sbin/reboot.bak"):
            run_command("sudo mv /sbin/reboot /sbin/reboot.bak")
            
        offline = poll_offline_mode()
        while offline == 2:
            offline = poll_offline_mode()
            time.sleep(2)
        
    elif status == "online":
        run_command("sudo iptables -F")
        time.sleep(30)
    else:
        print("Please enter valid status offline or online")

# STC013
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867655"])
async def test_offline_checkout(card_number):
    # time.sleep(0.5)
    # click_button("cancel")
    set_os_status("offline")
    time.sleep(2)
    
    await inject_barcode(card_number)
    time.sleep(5)
    product_barcode = fetch_product_barcode()
    await inject_barcode(product_barcode)
    time.sleep(2)
    click_button("checkout")
    time.sleep(1)
    logging.info("extracting text from the image")
    text = get_text_from_screen()
    assert "Thank You!" in text, "Failed to checkout"

# # STC_029
# @pytest.mark.asyncio
# @pytest.mark.parametrize("card_number", ["29230353867655"])
# async def test_offline_hot_button(card_number):
#    time.sleep(3)
#    await inject_barcode(card_number)
#    logging.info("waiting to access the account info")
#    time.sleep(4)
#    set_os_status("offline")
#    click_button("hot-button")
#    time.sleep(0.2)
#    click_button("checkout")
#    time.sleep(0.5)
#    logging.info("extracting text from the image")
#    text = get_text_from_screen()
#    assert "Thank You!" in text, "Failed to checkout"

# STC013
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867655"])
async def test_offline_checkout_unregistered(card_number):
    try:
        # time.sleep(0.5)
        # click_button("cancel")
        time.sleep(5)
        logging.info("checking for unregistered card")
        await delete_account_details_from_db(card_number)
        time.sleep(3)
        await inject_barcode(card_number)
        logging.info("extracting text from image")
        time.sleep(3)
        text = get_text_from_screen()
        click_button("cancel_invalid")
        click_button("cancel")
        print(text)
        assert any("Internet is not available" in line for line in text), "Supposed to be failed"
    finally:
        logging.info("Setting OS back to online")
        set_os_status("online")
        await inject_barcode(card_number)
        click_button("cancel")
        time.sleep(3)

# STC006
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867655"])
async def test_loyalty_balance(card_number):
    await inject_barcode(card_number)
    time.sleep(3)
    db_data = await fetch_account_details_from_db(card_number)
    if db_data is not None :
        logging.info("Account details successfully fetched from DB.")

    api_data = await fetch_account_details_from_api(card_number)
    
    assert db_data is not None, "Account not found in database"
    assert api_data is not None, "Account not found in API"

    db_dict = {
        "account_id": int(db_data[0]),
        "available_balance": round(db_data[4], 2)
    }

    api_dict = {
        "account_id": int(api_data["account_id"]),
        "available_balance": float(api_data["available_balance"])
    }

    assert db_dict == api_dict, "Mismatched loyalty details between database and API response"
    click_button("cancel")
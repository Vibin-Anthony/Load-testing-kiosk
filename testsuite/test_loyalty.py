import asyncio
import pytest
from utils.util import inject_barcode
import logging
from utils.util import delete_account_details_from_db, fetch_account_details_from_db, fetch_product_barcodes_multiple, fetch_account_details_from_api, fetch_product_barcode
from utils.util import send_lynk_request
from utils.util import get_text_from_screen
from utils.util import click_button

import time
import asyncio

import re

logging.basicConfig(level=logging.INFO, format="%(ascasyncio)s - %(levelname)s - %(message)s")

# STC006
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867655"])
async def test_loyalty_new_entry(card_number):
    await delete_account_details_from_db(card_number)
    await inject_barcode(card_number)
    time.sleep(3)
    db_data = await fetch_account_details_from_db(card_number)
    assert db_data is not None, "Account not registered in database"
    click_button("cancel")

# # STC006
# @pytest.mark.asyncio
# @pytest.mark.parametrize("card_number", ["29230353867655"])
# async def test_loyalty_balance(card_number):
#     await delete_account_details_from_db(card_number)
#     await asyncio.sleep(1)
#     await inject_barcode(card_number)
#     await asyncio.sleep(2)
#     db_data = await fetch_account_details_from_db(card_number)
#     if db_data is not None :
#         logging.info("Account details successfully fetched from DB.")

#     api_data = await fetch_account_details_from_api(card_number)
    
#     assert db_data is not None, "Account not found in database"
#     assert api_data is not None, "Account not found in API"

#     db_dict = {
#         "account_id": int(db_data[0]),
#         "available_balance": round(db_data[4], 2)
#     }

#     api_dict = {
#         "account_id": int(api_data["account_id"]),
#         "available_balance": float(api_data["available_balance"])
#     }

#     assert db_dict == api_dict, "Mismatched loyalty details between database and API response"
#     click_button("cancel")

# STC006 LYNK
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867655"])
async def test_loyalty_lynk(card_number):
    await delete_account_details_from_db(card_number)
    time.sleep(1)
    await send_lynk_request( card_number)
    time.sleep(3)
    db_data = await fetch_account_details_from_db(card_number)
    if db_data is not None :
        logging.info("Account details successfully fetched from DB.")

    assert db_data is not None, "Account not found in database"
    click_button("cancel")

# TC003
# Balance update after items removal from the cart
# @pytest.mark.asyncio
# @pytest.mark.parametrize("card_number", ["29230353867655"])
# async def test_loyalty_balance_update(card_number):
#     await inject_barcode(card_number)
#     logging.info("waiting to access the account info")
#     time.sleep(4)
#     old_balance = (await fetch_account_details_from_db(card_number))[4]
#     product_barcodes = fetch_product_barcodes_multiple()
#     for product in product_barcodes:
#         await inject_barcode(product)
#         time.sleep(0.5)
#         click_button("cancel_invalid")

#     pattern = r"New Account Bal After Checkout:\$(\d+\.\d+)"
#     logging.info("Extracting text")
#     capture_screenshot("products")
#     click_button("product")
#     capture_screenshot("products2")
#     text = get_text_from_screen("products")
#     for string in text:
#         match = re.search(pattern, string)
#         if match:
#             string = match.group(1)
#             current_balance = float(string)

#     text = get_text_from_screen("products2")
#     for string in text:
#         match = re.search(pattern, string)
#         if match:
#             string = match.group(1)
#             new_balance = float(string)
#     assert current_balance is not new_balance, "Balance stayed same after canceling the products"

# STC008 LYNK reload
# @pytest.mark.asyncio
# @pytest.mark.parametrize("card_number", ["29230353867655"])
# async def test_loyalty_lynk_reload(card_number):
#     await send_lynk_request("begin_sale", card_number)
#     await asyncio.sleep(3)
#     db_data = await fetch_account_details_from_db(card_number)
#     if db_data is not None :
#         logging.info("Account details successfully fetched from DB.")

#     assert db_data is not None, "Account not found in database"
#     click_button("add-funds")
#     await send_lynk_request("sale_response", card_number)
#     time.sleep(1)
#     click_button("check")
#     click_button("cancel")

# STC_010 Invalid Promo code
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867656"])
async def test_loyalty_invalid_promo(card_number):
    await inject_barcode(card_number)
    logging.info("waiting to access the account info")
    time.sleep(4)
    click_button("invalid-redeem-promo")
    time.sleep(2)
    logging.info("extracting text from the image")
    text = get_text_from_screen()
    print(text)
    assert any("Promo code cannot be found" in line for line in text), "Promo code was invalid"
    time.sleep(5)

# STC_012 Insufficient Balance card
@pytest.mark.asyncio
@pytest.mark.parametrize("card_number", ["29230353867656"])
async def test_loyalty_insufficient_balance(card_number):
    await inject_barcode(card_number)
    logging.info("waiting to access the account info")
    time.sleep(4)

    db_data_old = await fetch_account_details_from_db(card_number)
    if db_data_old is not None :
        logging.info("Account details successfully fetched from DB.")
    

    balance = (await fetch_account_details_from_db(card_number))[4]
    
    if balance > 2:
        print("Balance should be less than $2 to complete this test")
        print(balance)
        return

    product_barcode = fetch_product_barcode()
    assert product_barcode, "❌ No barcode found in the catalog!"
    await inject_barcode(product_barcode)
    time.sleep(0.2)
    await inject_barcode(product_barcode)
    time.sleep(2)
    click_button("checkout")
    time.sleep(0.5)
    logging.info("extracting text from the image")
    text = get_text_from_screen()
    click_button("continue")
    time.sleep(0.2)
    click_button("cancel")
    assert "Thank You!" not in text, "Checkout supposed to be failed"
    time.sleep(4)


'''
 Invalids
'''
# # Invalid barcode
# @pytest.mark.asyncio
# @pytest.mark.parametrize("card_number", ["29230353999258"])
# async def test_loyalty_invalid_card(card_number):
#     await inject_barcode(card_number)
#     logging.info("waiting to access the account info")
#     time.sleep(4)
#     logging.info("extracting text from the image")
#     text = get_text_from_screen()
#     await asyncio.sleep(0.5)
#     print(text)
#     assert any("Invalid card" in line for line in text), "Card was Invalid"

# Not activated card
# @pytest.mark.asyncio
# @pytest.mark.parametrize("card_number", ["29230353867677758"])
# async def test_loyalty_inactive_card(card_number):
#     await inject_barcode(card_number)
#     logging.info("waiting to access the account info")
#     time.sleep(4)
#     logging.info("extracting text from the image")
#     text = get_text_from_screen()
#     time.sleep(0.5)
#     click_button("continue_inactive_barcode")
#     assert any("Unrecognised" in line for line in text), "Card was Invalid"


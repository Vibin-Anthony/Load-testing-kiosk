import asyncio
import time
import logging
from checkout_flow import run_checkout
from system_metrics import log_system_metrics

logging.basicConfig(
    filename="endurance_test.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

CARD_NUMBER = "29230353867655"
INTERVAL = 120      # 2 minutes
DURATION = 24 * 60 * 60  # 24 hours (seconds)

async def main():
    start_time = time.time()
    iteration = 1

    while time.time() - start_time < DURATION:
        logging.info(f"Transaction {iteration} started")

        try:
            await run_checkout(CARD_NUMBER)
            logging.info(f"Transaction {iteration} SUCCESS")
        except Exception as e:
            logging.error(f"Transaction {iteration} FAILED: {str(e)}")

        log_system_metrics()
        iteration += 1
        time.sleep(INTERVAL)

asyncio.run(main())

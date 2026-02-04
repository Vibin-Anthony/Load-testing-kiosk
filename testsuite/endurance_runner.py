import asyncio
import time
import logging
from checkout_flow import run_checkout

logging.basicConfig(
    filename="/var/log/kiosk_test/checkout.log",
    level=logging.INFO,
    format="%(message)s"
)

CARD_NUMBERS = [
    "29230353867655",
    "29230353867656",
    "29230353867657",
]

INTERVAL = 120          # 1 minute between transactions
DURATION = 6 * 60     # 10 minutes total run


async def main():
    start = time.time()
    txn = 1

    expected_total = int(DURATION / INTERVAL)

    while time.time() - start < DURATION:
        elapsed = int(time.time() - start)
        remaining_time = max(DURATION - elapsed, 0)
        remaining_txns = max(expected_total - (txn - 1), 0)

        card = CARD_NUMBERS[(txn - 1) % len(CARD_NUMBERS)]

        logging.info(
            f"[{time.strftime('%H:%M:%S')}] ▶ Transaction {txn} | "
            f"Card: {card} | "
            f"Remaining: {remaining_txns} | "
            f"Time left: {remaining_time//60}m {remaining_time%60}s"
        )

        try:
            await run_checkout(card, txn)
        except Exception as e:
            logging.error(
                f"[{time.strftime('%H:%M:%S')}] ❌ Transaction {txn} FAILED | {e}"
            )

        txn += 1
        await asyncio.sleep(INTERVAL)

    logging.info(
        f"[{time.strftime('%H:%M:%S')}] 🏁 Endurance test finished | "
        f"Total attempted: {txn - 1}"
    )


asyncio.run(main())

#!/bin/bash

LOG_DIR="/var/log/kiosk_test"
METRICS="$LOG_DIR/system_metrics.log"
CHECKOUT="$LOG_DIR/checkout.log"
SUMMARY="$LOG_DIR/summary.txt"

echo "===== KIOSK ENDURANCE TEST SUMMARY =====" > "$SUMMARY"
echo "Generated at: $(date)" >> "$SUMMARY"
echo "" >> "$SUMMARY"

if [ ! -f "$METRICS" ]; then
    echo "❌ system_metrics.log not found" >> "$SUMMARY"
    exit 1
fi

echo "--- CPU / RAM / TEMP AVERAGES ---" >> "$SUMMARY"

awk -F',' '
{
    cpu+=$2; mem+=$3; temp+=$4; count++
}
END {
    printf "Average CPU Usage: %.2f %%\n", cpu/count
    printf "Average RAM Usage: %.2f MB\n", mem/count
    printf "Average Temperature: %.2f °C\n", temp/count
}' "$METRICS" >> "$SUMMARY"

echo "" >> "$SUMMARY"
echo "--- PURCHASE STATS ---" >> "$SUMMARY"

grep "Stats →" "$CHECKOUT" | tail -1 >> "$SUMMARY"

echo "" >> "$SUMMARY"
echo "===== END =====" >> "$SUMMARY"

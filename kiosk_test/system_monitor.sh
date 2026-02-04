#!/bin/bash

LOG_FILE="/var/log/kiosk_test/system_metrics.log"
INTERVAL=5   # seconds

echo "timestamp,cpu_usage_percent,ram_used_mb,temp_c" >> "$LOG_FILE"

while true; do
    TS=$(date "+%Y-%m-%d %H:%M:%S")
    CPU=$(top -bn1 | awk '/Cpu/ {print 100 - $8}')
    RAM=$(free -m | awk '/Mem:/ {print $3}')
    TEMP=$(vcgencmd measure_temp | grep -o '[0-9.]*')

    echo "$TS,$CPU,$RAM,$TEMP" >> "$LOG_FILE"
    sleep $INTERVAL
done

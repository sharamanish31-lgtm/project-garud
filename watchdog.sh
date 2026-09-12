#!/bin/bash

# Load .env variables
export $(grep -v '^#' ~/garud_core/.env | xargs)

STATE_FILE="/tmp/garud_watchdog_state"
CONTAINERS=("garud-perimeter" "garud-shield")

send_telegram() {
    local msg="$1"
    curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="${TELEGRAM_CHAT_ID}" \
        -d text="$msg" > /dev/null
}

for container in "${CONTAINERS[@]}"; do
    STATUS=$(docker inspect -f '{{.State.Running}}' "$container" 2>/dev/null)
    PREV_STATE_FILE="${STATE_FILE}_${container}"

    if [ "$STATUS" != "true" ]; then
        CURRENT="DOWN"
    else
        CURRENT="UP"
    fi

    if [ -f "$PREV_STATE_FILE" ]; then
        PREV=$(cat "$PREV_STATE_FILE")
    else
        PREV="UNKNOWN"
    fi

    if [ "$CURRENT" != "$PREV" ]; then
        if [ "$CURRENT" == "DOWN" ]; then
            send_telegram "🔴 ALERT: $container is DOWN! Time: $(date '+%Y-%m-%d %H:%M:%S')"
        else
            send_telegram "✅ RECOVERED: $container is back UP! Time: $(date '+%Y-%m-%d %H:%M:%S')"
        fi
        echo "$CURRENT" > "$PREV_STATE_FILE"
    fi
done

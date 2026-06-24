#!/bin/bash

# Intervalo de verificação em segundos
INTERVAL=60

while true; do
    # Estado da bateria (Charging, Discharging, Full)
    STATUS=$(acpi -b | awk '{print $3}' | tr -d ',')

    # Percentagem da bateria
    PERCENT=$(acpi -b | awk '{print $4}' | tr -d '%,')

    # Verifica se está a carregar e chegou a 80%
    if [[ "$STATUS" == "Charging" && "$PERCENT" -ge 80 ]]; then
        notify-send "Bateria" "Bateria chegou a 80%! 🔋"
        # Espera 10 minutos antes de notificar de novo para não spammar
        sleep 600
    else
        sleep $INTERVAL
    fi
done

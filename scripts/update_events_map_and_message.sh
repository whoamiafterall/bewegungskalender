#!/bin/bash
cd ~/bewegungskalender2telegram/
source ~/bewegungskalender2telegram/.venv/bin/activate
python3 -m bewegungskalender.main -u -m -qe 90
cd ~/bewegungskalender2telegram/scripts
./edit_last_telegram_message.sh

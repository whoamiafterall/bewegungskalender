#!/bin/bash
cd ~/bewegungskalender2telegram/
source ~/bewegungskalender2telegram/.venv/bin/activate
python3 -m bewegungskalender.main -t test -n

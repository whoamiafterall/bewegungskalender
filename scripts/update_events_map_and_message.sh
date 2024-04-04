#!/bin/bash
source ~/.bash_profile
ssh-add ~/.ssh/bewegungskalender_rsa
cd ~/bewegungskalender2telegram/
source ~/bewegungskalender2telegram/.venv/bin/activate
python3 -m bewegungskalender.main -u -m -qe 90
python3 -m bewegungskalender.main -e test
deactivate

#!/bin/sh

# Launch the environment
if ! [ -d venv ]; then
    echo " === Initializaing the environment ==="

    python3 -m venv venv
    . venv/bin/activate
    pip install -r requirements.txt
else
    echo " === Environment already initialized ==="
    . venv/bin/activate
fi

echo

# Creates if the link file exists
if ! [ -f link.json ]; then
    echo " === Creating linker file ==="

    echo "{}" > link.json
else
    echo " === Linker file already exists ==="

fi

echo

# Launch the code
echo " === Launching the code ==="

while true; do
    echo " === Launching bot for 24 hours ==="
    timeout 86400 python main.py

    echo " === Restarting bot in 5 seconds... ==="
    sleep 5
done

#!/bin/bash

/bin/bash /generate-config.sh

sleep 2

python3 /controller.py

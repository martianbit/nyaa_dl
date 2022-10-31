#!/bin/bash

pip install -r requirements.txt
install -m755 nyaa_dl.py /usr/bin/nyaa_dl

echo "nyaa_dl was successfully installed"
echo "try running nyaa_dl -h"


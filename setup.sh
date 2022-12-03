#!/bin/bash

if [ "$1" == "install" ]; then
	mkdir -p ~/.local/bin
	install -m755 nyaa_dl.py ~/.local/bin/nyaa_dl
	pip install -r requirements.txt

	echo "nyaa_dl was successfully installed"
	echo "try running nyaa_dl -h"
elif [ "$1" == "uninstall" ]; then
	rm -f ~/.local/bin/nyaa_dl
	pip uninstall -r requirements.txt

	echo "nyaa_dl was successfully uninstalled"
	echo "sorry to see you go :("
elif [ "$1" == "-h" ] || [ "$1" == "--help" ]; then
	echo "usage: ./setup.sh [-h] [--help] [install] [uninstall]"
else
	echo "bad usage"
	echo "try ./setup.sh -h"
fi

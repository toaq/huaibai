#! /usr/bin/env bash

set -e

rm -f Huaıbaı.zip
python to_latin.py
wget -O src/assets/minecraft/textures/font/guezueq.otf https://github.com/toaq/fonts/releases/download/latest/Guezueq.otf
cd src
zip -r ../Huaıbaı.zip *
cd ..

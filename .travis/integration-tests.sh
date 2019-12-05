#!/bin/bash

set -ev
git clone https://github.com/kdevo/grapresso-it.git --depth 1
cp -f ./travis/inject-path__init__.py grapresso-it/tests/__init__.py
cd grapresso-it/
pip install -r requirements.txt
pytest
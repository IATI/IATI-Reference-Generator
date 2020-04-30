#!/bin/bash

git submodule init
git submodule update
if [ ! -d venv ]; then
  python3 -m virtualenv venv
  source venv/bin/activate
  pip install -r requirements.txt
else
  source venv/bin/activate
fi

cd IATI-Standard-SSOT-version-2.03
git submodule init
git submodule update
./gen.sh
cd ..

cd IATI-Standard-SSOT-version-2.02
git submodule init
git submodule update
./gen.sh
cd ..

cd IATI-Standard-SSOT-version-2.01
git submodule init
git submodule update
./gen.sh
cd ..

cd IATI-Standard-SSOT-version-1.05
git submodule init
git submodule update
./gen.sh
cd ..

cd IATI-Standard-SSOT-version-1.04
git submodule init
git submodule update
./gen.sh
cd ..

cd IATI-Guidance/en
make dirhtml
cd ../..

python3 extract_html.py

#!/usr/bin/env bash

# print ran commands
set -o xtrace
# fail if there is error
set -e
# fail for pipe errors
set -o pipefail

# build the pyinstaller package
pyinstaller --name=gaku --add-data "./resources:resources" --add-data "./alembic:alembic" --add-data "./alembic.ini:." --hidden-import=alembic --additional-hooks-dir=. main.py -i gaku-frontend/public/icon.svg


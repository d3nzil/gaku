#!/bin/env bash

# print ran commands
# set -o xtrace
# exit on error
set -e
# fail on unset variables
set -u
# fail on commands in a pipe
set -o pipefail

. ./venv/bin/activate

mypy ./src 
mypy ./tests_backend main.py
ruff check ./src ./tests_backend main.py
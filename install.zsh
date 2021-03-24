#!/usr/bin/env zsh


function info() { echo "[INFO]: ${1}"; }
function success() { echo "[SUCCESS]: ${1}"; }
function warning() { echo "[WARNING]: ${1}"; }
function error() { echo "[ERROR]: ${1}"; }


# python3
info "Checking if python3 is installed..."
if ! python3 --version > /dev/null 2>&1; then
  error "python3 is either not installed or not properly aliased."
  exit 64
fi
success "python3... OK"

info "Checking python's version"
if [ "$(python3 -c "import sys; print(''.join([str(n) for n in sys.version_info[:2]]))")" -lt "39" ]; then
  error "python 3.9 or higher is required to run this project."
  exit 64
fi
success "python3 version... OK"


# pip3
info "Checking if pip3 is installed..."
if ! pip3 --version > /dev/null 2>&1; then
  error "pip3 is either not installed or not properly aliased."
  exit 64
fi
success "pip3... OK"

info "Checking pip's version"
if [ "$(pip3 --version | cut --delimiter ' ' --fields 2 | cut --delimiter '.' --fields '1-2' | tr --delete '.')" -lt "203" ]; then
  error "pip 20.3 or higher is required to run this project."
  exit 64
fi
success "pip3 version... OK"


# .venv
PROJECT_PATH="$(dirname "$(realpath "${0}")")"
VENV_PATH="${PROJECT_PATH}/.venv"
info "Checking the existence of a python virtual environment..."
if [ -d "${VENV_PATH}" ]; then
  error "A python virtual environment (in ${VENV_PATH}) was found. Remove the aforementioned directory to install the project."
  exit 65
fi
success "No existing virtual environment was found."

info "Creating a python virtual environment in ${VENV_PATH}..."
python3 -m venv "${VENV_PATH}"
success "python3 venv... OK"


# install dependencies
source "${VENV_PATH}/bin/activate"

python3 -m pip install --upgrade pip

pip3 install --requirement "${PROJECT_PATH}/requirements.txt"


# info
echo ""
echo "Add the following alias to your '.zshrc' file:"
echo "alias laravel=\"${VENV_PATH}/bin/python ${PROJECT_PATH}/main.py\""

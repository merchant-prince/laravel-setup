#!/usr/bin/env zsh


PYTHON_VERSION="3.9"
PIP_VERSION="20.3.3"
PROJECT_PATH="$(dirname "$(realpath "${0}")")"
VENV_PATH="${PROJECT_PATH}/.venv"

function info() { echo "[INFO]: ${1}"; }
function success() { echo "[SUCCESS]: ${1}"; }
function warning() { echo "[WARNING]: ${1}"; }
function error() { echo "[ERROR]: ${1}"; }


# python3
info "checking if python3 is installed..."
if ! python3 --version > /dev/null 2>&1; then
  error "python3 is either not installed or not properly aliased."
  exit 64
fi
success "python3... OK"

info "checking python's version"
if [ "$(python3 -c "import sys; print(''.join([str(n) for n in sys.version_info[:2]]))")" -lt "$(echo "${PYTHON_VERSION}" | tr --delete '.')" ]; then
  error "python ${PYTHON_VERSION} or higher is required to run this project."
  exit 64
fi
success "python's version... OK"


# pip3
info "checking if pip3 is installed..."
if ! pip3 --version > /dev/null 2>&1; then
  error "pip3 is either not installed or not properly aliased."
  exit 64
fi
success "pip3... OK"

info "checking pip's version"
if [ "$(pip3 --version | cut --delimiter ' ' --fields 2 | cut --delimiter '.' --fields '1-2' | tr --delete '.')" -lt "$(echo "${PIP_VERSION}" | cut --delimiter ' ' --fields 2 | cut --delimiter '.' --fields '1-2' | tr --delete '.')" ]; then
  warning "pip ${PIP_VERSION} or higher might be required to run this project."
else
  success "pip's version... OK"
fi


# .venv
info "checking the existence of a python virtual environment..."
if [ -d "${VENV_PATH}" ]; then
  error "a python virtual environment (in ${VENV_PATH}) was found. Remove the aforementioned and re-launch the script."
  exit 65
fi
success "no virtual environment found."

info "creating a python virtual environment in ${VENV_PATH}..."
python3 -m venv "${VENV_PATH}"
success "python3 venv... OK"


# install dependencies
source "${VENV_PATH}/bin/activate"

info "upgrading pip..."
python3 -m pip install --upgrade pip
success "pip upgrade... OK"

if [ -f "${PROJECT_PATH}/requirements.txt" ]; then
  info "installing the project dependencies..."
  pip3 install --requirement "${PROJECT_PATH}/requirements.txt"
  success "installation successful."
fi

deactivate


# post-install information
echo ""
echo "Add the following alias to your '.zshrc' file:"
echo "alias laravel=\"${VENV_PATH}/bin/python ${PROJECT_PATH}/main.py\""
echo ""

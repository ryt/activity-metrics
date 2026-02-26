#!/usr/bin/env python3

import os

# configuration options

CONFIG_DIR='~/.acmeryt/' # main acme config dir

CONFIG_DIR_FULL=os.path.expanduser(CONFIG_DIR) # full path

# default subdirectory names for local user metrics directory if used
# - metrics/logs
# - metrics/gen
# - merics/app

LOGS_NAME = 'logs'
GEN_NAME  = 'gen'
APP_NAME  = 'app'

# acmedash default ports

PORT_DEV  = '5000' # dev server default port
PORT_PROD = '8100' # prod server default port

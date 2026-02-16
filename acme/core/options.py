#!/usr/bin/env python3

import os

# configuration options

CONFIGDIR='~/.acmeryt/' # main acme config dir

CONFIGDIRFULL=os.path.expanduser(CONFIGDIR) # full path

# default subdirectory names for local user metrics directory if used
# - metrics/logs
# - metrics/gen
# - merics/app

LOGS_NAME = 'logs'
GEN_NAME  = 'gen'
APP_NAME  = 'app'

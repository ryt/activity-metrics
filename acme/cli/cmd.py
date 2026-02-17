#!/usr/bin/env python3

import os
import sys
import itertools
import subprocess

from configparser import ConfigParser

from acme.core import options


def curl(url, headers = ''):
  # -- run curl via subprocess -- #
  
  curl_command = f'curl "{url}" -H "{headers}"'
  process = subprocess.run(curl_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output = process.stdout.decode('utf-8')
  error = process.stderr.decode('utf-8')
  if process.returncode == 0:
    return output
  else:
    return f'Error: {error}'


# todo: add direct gunicorn function

def runapp(action, config, appdir):
  """
  Options to deploy the flask webapp prod server via the gunicorn wrapper runapp.
  https://github.com/ryt/runapp (requires version 1.4+)

  To use this function, the following needs to be set in ~/.acmeryt/runapp.conf
  runappbin = /path/to/runapp/

  The runappbin setting specifies the directory where runapp.py is located.
  """
  # runapp action ~/.acmeryt/runapp.conf /path/to/appdir

  conf = f'{options.CONFIG_DIR_FULL}runapp.conf'
  if not os.path.exists(conf):
    return

  with open(conf) as cf:
    cfparser = ConfigParser()
    cfparser.read_file(itertools.chain(['[global]'], cf), source=conf)
    try:
      runappbin = cfparser.get('global', 'runappbin')
    except:
      runappbin = False

  if not runappbin:
    return

  sys.path.append(runappbin)
  import runapp
  call = runapp.main('runapp', action, config, appdir)

  return call





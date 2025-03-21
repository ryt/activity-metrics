#!/usr/bin/env python3

"""
Copyright (C) 2024 Ray Mentose.
This app uses Flask & Gunicorn with ryt/runapp for deployment.
"""

import os
import sys
import csv
import time
import html
import itertools
import importlib

from flask import Flask
from flask import request
from urllib.parse import quote
from flask import render_template
from configparser import ConfigParser

app = Flask(__name__)

# -- set timezone to america/los_angeles -- #
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

limitpath  = ''
app_path   = '/'
sslcertkey = ''
secret_key = ''

# -- start: parse runapp.conf (if it exists) and apply settings -- #
conf = 'runapp.conf'
if os.path.exists(conf):
  with open(conf) as cf:
    config = ConfigParser()
    config.read_file(itertools.chain(['[global]'], cf), source=conf)
    try:
      limitpath = config.get('global', 'limitpath').rstrip('/') + '/'
    except:
      limitpath = ''
    try:
      app_path = config.get('global', 'app_path')
    except:
      app_path = app_path
    try:
      sslcertkey = config.get('global', 'sslcertkey')
    except:
      sslcertkey = ''
    try:
      secret_key = config.get('global', 'secret_key')
    except:
      secret_key = secret_key
# -- end: parse runapp config

if secret_key:
  app.secret_key = secret_key

def get_query(param):
  """Get query string param (if exists & has value) or empty string"""
  try:
    return request.args.get(param) if request.args.get(param) else ''
  except:
    return ''

def parse_settings(getm):
  """Parse the module_settings.py local settings config."""
  module = {}
  with open(f'{getm}/app/module_settings.py') as f:
    exec(f.read(), {}, module)
  return module

# router start


# router for [index] and [custom local modules]

@app.route(f'{app_path}', methods=['GET', 'POST'])
@app.route(f'{app_path}<module>',  methods=['GET', 'POST'])
def default_modules(module='index'):

  module_script, module_name, module_call = '', '', ''

  getm = get_query('m')
  view = {
    'app_path'      : app_path,
    'page'          : module,
    'getm'          : getm,
    'query_m'       : f'm={getm}',
    'error'         : False, 
    'message'       : '',
    'output_html'   : '',
    'add_nav_links' : (),
  }

  getm = getm.rstrip('/')
  if getm and os.path.isdir(f'{getm}/logs/'):

    # default local modules import

    module_settings = parse_settings(getm)
    module_list = module_settings['run_local_modules']
    view['add_nav_links'] = module_settings['add_nav_links']

    if module in module_list:

      module_script = module_list[module][0]
      module_name   = module_list[module][1]
      module_call   = module_script.rstrip('.py')

      if os.path.isfile(f'{getm}/app/{module_script}'):
        sys.path.append(f'{getm}/app/')
        module_run = importlib.import_module(module_call)
        importlib.reload(module_run)

        view['message']       = ''
        view['output_html']   = module_run.run_main()

      else:
        view['error']   = True
        view['message'] = f'Sorry the dashboard {module_name} module could not be found in the metrics app directory.'

    else:
      view['error']   = True
      view['message'] = ''.join((
        f'<div class="linemid">Sorry a module named "{module}" could not be found. ',
        f'Please make sure the file "dashboard_{module}.py" exists. <br> ',
        f'If it exists, please enable it in <i>module_settings.py</i> -> [run_local_modules] in your local metrics directory.</div>',
      ))

  else:
    view['message'] = f'Please specify a valid metrics directory path for the {module_name} module. ?m=/Path/to/Metrics/'

  return render_template('acmedash.html', view=view)


if __name__ == '__main__':
  sslck = sslcertkey.split(' ')
  if len(sslck) == 2:
    app.run(ssl_context=(sslck[0], sslck[1]), debug=True)
  else:
    app.run(debug=True)


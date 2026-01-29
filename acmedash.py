#!/usr/bin/env python3

# activity metrics: dashboard (acmedash)
# this app uses flask & gunicorn with ryt/runapp for deployment
# latest source & documentation at: https://github.com/ryt/activity-metrics.git


import os
import sys
import csv
import time
import html
import config
import itertools
import importlib

from flask import Flask
from flask import request
from urllib.parse import quote
from flask import render_template
from configparser import ConfigParser

from __version__ import __version__

app = Flask(__name__)

# -- set timezone to america/los_angeles -- #
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

# default runapp config values
sslcertkey = ''

# -- runapp ssl settings start: parse runapp.conf (if it exists) and apply ssl settings -- #
conf = 'runapp.conf'
if os.path.exists(conf):
  with open(conf) as cf:
    cfparser = ConfigParser()
    cfparser.read_file(itertools.chain(['[global]'], cf), source=conf)
    try:
      sslcertkey = cfparser.get('global', 'sslcertkey')
    except:
      sslcertkey = ''
# -- runapp ssl settings end -- #

# -- start: parse config parameters from config.py and set values -- #


# default config.py config values
limitpath  = ''
app_path   = '/'
secret_key = ''

# read & modify config values

if 'limitpath' in config.config:
  limitpath = config.config['limitpath'].rstrip('/') + '/'

if 'app_path' in config.config:
  app_path = config.config['app_path']

if 'secret_key' in config.config:
  secret_key = config.config['secret_key']

# -- end: parse config parameters -- #

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

  gqm = get_query('m')
  lqm = limitpath.rstrip('/') + '/' + gqm.lstrip('/') if limitpath else ''
  print(lqm)

  getm = (gqm, lqm if lqm else gqm)
  getm0 = getm[0]
  getm1 = getm[1].rstrip('/')

  view = {
    'app_path': app_path,
    'version': {
      'acme': __version__,
      'local': '',
    },
    'page': module,
    'getm': getm,
    'getm0': getm0,
    'query_m': f'm={getm0}',
    'error': False,
    'message': '',
    'output_html': '',
    'add_nav_links': (),
  }

  if getm1 and os.path.isdir(f'{getm1}/logs/'):

    # default local modules import

    module_settings = parse_settings(getm1)
    module_list = module_settings['run_local_modules']
    view['add_nav_links'] = module_settings['add_nav_links']

    if module == 'about':
      sys.path.append(f'{getm1}/')
      module_local_version = importlib.import_module(f'app.__version__')
      importlib.reload(module_local_version)
      view['version']['local'] = module_local_version.__version__

    elif module in module_list:

      module_script = module_list[module][0]
      module_name   = module_list[module][1]
      module_call   = module_script.rstrip('.py')

      if os.path.isfile(f'{getm1}/app/{module_script}'):
        sys.path.append(f'{getm1}/app/')
        module_run = importlib.import_module(module_call)
        importlib.reload(module_run)

        view['message']       = ''
        view['output_html']   = module_run.run_main(getm)

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


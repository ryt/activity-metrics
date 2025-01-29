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

limitpath = ''
app_path  = '/'

# -- start: parse runapp.conf (if it exists) and make modifications -- #
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
# -- end: parse runapp config


def get_query(param):
  """Get query string param (if exists & has value) or empty string"""
  try:
    return request.args.get(param) if request.args.get(param) else ''
  except:
    return ''


@app.route(f'{app_path}commands',  methods=['GET'])
def commands(subpath=None):

  getm        = get_query('m')
  getcmd      = get_query('cmd')

  view = {
    'app_path'    : app_path,
    'page'        : 'commands',
    'getm'        : getm,
    'query_m'     : f'm={getm}',
    'command'     : '', 
    'error'       : False, 
    'message'     : '',
    'output_html' : '',
  }

  getm = getm.rstrip('/')
  if getm and os.path.isdir(f'{getm}/logs/'):
    if os.path.isfile(f'{getm}/app/dashboard_commands.py'):
      sys.path.append(f'{getm}/app/')
      import dashboard_commands
      importlib.reload(dashboard_commands)

      view['message']       = getcmd
      view['command']       = getcmd
      view['output_html']   = dashboard_commands.run_main()

    else:
      view['error']   = True
      view['message'] = 'Sorry the commands module could not be found in the metrics app directory.'
  else:
    view['message'] = 'Please specify a command and a valid metrics directory path. /commands?m=/Path/to/Metrics/&cmd=command'

  return render_template('acmedash.html', view=view)


# default modules list

module_list = {
  'athletics' : ('dashboard_athletics.py',      'athletics'),
  'garmin'    : ('dashboard_garmin_connect.py', 'garmin connect'),
  'nutrition' : ('dashboard_nutrition.py',      'nutrition'),
  'health'    : ('dashboard_health.py',         'health'),
}

@app.route(f'{app_path}<module>',  methods=['GET'])
def default_modules(module):

  getm = get_query('m')
  view = {
    'app_path'    : app_path,
    'page'        : module,
    'getm'        : getm,
    'query_m'     : f'm={getm}',
    'error'       : False, 
    'message'     : '',
    'output_html' : '',
  }

  if module in module_list:

    module_script = module_list[module][0]
    module_name   = module_list[module][1]
    module_call   = module_script.rstrip('.py')

    getm = getm.rstrip('/')
    if getm and os.path.isdir(f'{getm}/logs/'):
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
      view['message'] = f'Please specify a valid metrics directory path for the {module_name} module. ?m=/Path/to/Metrics/'

  else:
    view['error']   = True
    view['message'] = 'Sorry there is no module with that name.'

  return render_template('acmedash.html', view=view)


@app.route(f'{app_path}custom',  methods=['GET'])
def custom(subpath=None):

  getm        = get_query('m')

  view = {
    'app_path'    : app_path,
    'page'        : 'custom',
    'getm'        : getm,
    'query_m'     : f'm={getm}',
    'error'       : False, 
    'message'     : '',
    'output_html' : '',
  }

  getm = getm.rstrip('/')
  if getm and os.path.isdir(f'{getm}/logs/'):
    if os.path.isfile(f'{getm}/app/dashboard_custom.py'):
      sys.path.append(f'{getm}/app/')
      import dashboard_custom
      importlib.reload(dashboard_custom)

      view['message']       = ''
      view['output_html']   = dashboard_custom.run_main()

    else:
      view['error']   = True
      view['message'] = 'Sorry the dashboard custom module could not be found in the metrics app directory.'
  else:
    view['message'] = 'Please specify a valid metrics directory path for the custom module. ?m=/Path/to/Metrics/'

  return render_template('acmedash.html', view=view)


@app.route(f'{app_path}', methods=['GET'])

def index(subpath=None):

  global app_path

  getm        = get_query('m')

  view   = {
    'app_path'    : app_path,
    'page'        : 'index',
    'getm'        : getm,
    'query_m'     : f'm={getm}',
    'app_path'    : app_path,
    'error'       : False, 
    'message'     : '',
    'output_html' : '',
  }

  getm = getm.rstrip('/')
  if getm and os.path.isdir(f'{getm}/logs/'):
    if os.path.isfile(f'usr/app/dashboard_metrics.py'):
      sys.path.append(f'usr/app/')
      import dashboard_metrics
      importlib.reload(dashboard_metrics)

      view['message']       = ''
      view['command']       = ''
      view['output_html']   = dashboard_metrics.run_main()

    else:
      view['error']   = True
      view['message'] = 'Sorry the dashboard metrics module could not be found in the activity metrics app directory.'
  else:
    view['message'] = 'Please specify a valid path for the metrics directory. ?m=/Path/to/Metrics/'

  return render_template('acmedash.html', view=view)


if __name__ == '__main__':
    app.run(debug=True)


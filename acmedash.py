#!/usr/bin/env python3

"""
Copyright (C) 2024 Ray Mentose.
This app uses Flask & Gunicorn with ryt/runapp for deployment.
"""

import os
import sys
import csv
import html
import itertools
import importlib

from flask import Flask
from flask import request
from urllib.parse import quote
from flask import render_template
from configparser import ConfigParser

app = Flask(__name__)

limitpath = ''
app_path  = '/acmedash'

# -- start: parse runapp.conf (if it exists) and make modifications
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


@app.route('/commands',  methods=['GET'])
def commands(subpath=None):

  getm        = get_query('m')
  getcmd      = get_query('cmd')

  view = { 
    'page'    : 'commands',
    'getm'    : getm,
    'query_m' : f'm={getm}',
    'command' : '', 
    'error'   : False, 
    'message' : '' 
  }

  if getm and getcmd:
    getm = getm.rstrip('/')
    if os.path.isfile(f'{getm}/app/dashboard_commands.py'):
      sys.path.append(getm)
      view['message'] = getcmd
      view['command'] = getcmd
      # TODO // todo
      # import dashboard_commands.py and run the specified command
    else:
      view['error']   = True
      view['message'] = 'Sorry the commands module could not be found in the metrics app directory.'
  else:
    if getm:
      view['message'] = f'Please specify a command. /commands?m={getm}&cmd=command'
    else:
      view['message'] = 'Please specify a command and app directory path. /commands?m=/Path/to/Metrics/&cmd=command'

  return render_template('acmedash.html', view=view)


@app.route('/garmin',  methods=['GET'])
def garmin(subpath=None):

  getm        = get_query('m')

  view = { 
    'page'        : 'garmin',
    'getm'        : getm,
    'query_m'     : f'm={getm}',
    'error'       : False, 
    'message'     : '',
    'output_html' : '',
  }

  if getm:
    getm = getm.rstrip('/')
    if os.path.isfile(f'{getm}/app/dashboard_garmin_connect.py'):
      sys.path.append(f'{getm}/app/')
      import dashboard_garmin_connect
      importlib.reload(dashboard_garmin_connect)

      view['message']       = ''
      view['output_html']   = dashboard_garmin_connect.output_html

    else:
      view['error']   = True
      view['message'] = 'Sorry the dashboard garmin connect module could not be found in the metrics app directory.'
  else:
    view['message'] = 'Please specify an app directory path for the garmin connect module. ?m=/Path/to/Metrics/'

  return render_template('acmedash.html', view=view)


@app.route('/', methods=['GET'])

def index(subpath=None):

  global app_path

  getm        = get_query('m')

  view   = { 
    'page'      : 'index',
    'getm'      : getm,
    'query_m'   : f'm={getm}',
    'app_path'  : app_path,
    'error'       : False, 
    'message'     : '',
    'output_html' : '',
  }

  if getm:
    getm = getm.rstrip('/')
    if os.path.isfile(f'test/app/dashboard_metrics.py'):
      sys.path.append(f'test/app/')
      import dashboard_metrics
      importlib.reload(dashboard_metrics)

      view['message']       = ''
      view['command']       = ''
      view['output_html']   = dashboard_metrics.output_html

    else:
      view['error']   = True
      view['message'] = 'Sorry the dashboard metrics module could not be found in the activity metrics app directory.'
  else:
    view['message'] = 'Please specify an app directory path for the metrics module. ?m=/Path/to/Metrics/'

  return render_template('acmedash.html', view=view)


if __name__ == '__main__':
    app.run(debug=True)


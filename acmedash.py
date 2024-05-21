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

def html_return_error(text):
  return f'<div class="error">{text}</div>'

def html_render_csv(path):

  render   = ''
  path_mod = remove_limitpath(path)

  try:

    with open(path, 'r') as file:
      content = file.read()
      html_table = '<table class="csv-table">\n'
      # added {skiinitialspace=True} to fix issue with commas inside quoted cells
      csv_reader = csv.reader(content.splitlines(), skipinitialspace=True)
      headers = next(csv_reader)

      html_table += '<tr>'
      for header in headers:
        header = html.escape(header)
        html_table += f'<th>{header}</th>'
      html_table += '</tr>\n'

      for row in csv_reader:
        html_table += '<tr>'
        for cell in row:
          cell = html.escape(cell)
          html_table += f'<td>{cell}</td>'
        html_table += '</tr>\n'
      
      html_table += '</table>'

      render = html_table

  except FileNotFoundError:
    render = html_return_error(f"The file '{path_mod}' does not exist.")

  except:
    render = html_return_error(f"The file '{path_mod}' could not be parsed.")

  return render


def plain_render_file(path):

  render   = ''
  path_mod = remove_limitpath(path)

  try:
    with open(path, 'r') as file:
      try:
        render = file.read()
      except:
        render = f"The file '{path_mod}' is not in text format."

  except FileNotFoundError:
    render = f"The file '{path_mod}' does not exist."

  except IOError:
    render = f"Error reading the file '{path_mod}'."

  return render

def get_query(param):
  """Get query string param (if exists & has value) or empty string"""
  try:
    return request.args.get(param) if request.args.get(param) else ''
  except:
    return ''

def remove_from_start(sub, string):
  """Remove sub from beginning of string if string starts with sub"""
  if string.startswith(sub):
    return string[len(sub):].lstrip()
  else:
    return string

def remove_limitpath(path):
  """Remove limitpath from beginning of path if limitpath has value"""
  global limitpath
  return remove_from_start(limitpath, path) if limitpath else path

def add_limitpath(path):
  """Add limitpath to beginning of path if limitpath has value"""
  global limitpath
  return f'{limitpath}{path}' if limitpath else path

def sanitize_path(path):
  """Sanitize path for urls: 1. apply limitpath mods, 2. escape &'s and spaces"""
  return quote(remove_limitpath(path), safe='/')

sp = sanitize_path


@app.route('/run',  defaults={'command': ''})
@app.route('/run/', defaults={'command': ''})
@app.route('/run/<path:command>')
def run(command):

  view = { 
    'page'    : 'run', 
    'command' : command, 
    'error'   : False, 
    'message' : '' 
  }

  a = get_query('a')

  if a and command:
    a = a.rstrip('/')
    if os.path.isfile(f'{a}/module_run_commands.py'):
      sys.path.append(a)
      view['message'] = command
      # TODO // todo
      # import module_run_commands.py and run the specified command
    else:
      view['error']   = True
      view['message'] = 'Sorry the run commands module could not be found in the specified app/ directory.'
  else:
    view['message'] = 'Please specify a command and app directory path. /run/command?a=/Path/to/app/'

  return render_template('acmedash.html', view=view)



@app.route('/', methods=['GET'])

def index(subpath=None):

  # if limitpath is set in runapp.conf, the directory listing view for the client/browser will be limited to that path as the absolute parent
  # if app_path is set in runapp.conf, that path will be used to route index page of the app

  global limitpath, app_path

  # limitpath = '/usr/local/share/' # for testing

  getf        = get_query('f')
  getview     = get_query('view')
  getf_html   = remove_limitpath(getf)  # limitpath mods for client/browser side view
  getf        = add_limitpath(getf)     # limitpath mods for internal processing

  view   = { 'page' : 'index', 'app_path' : app_path }
  listfs = []

  if os.path.isdir(getf):
    files = sorted(os.listdir(getf))
    parpt = getf.rstrip('/')
    if files:
      for f in files:
        if os.path.isdir(f'{parpt}/{f}'):
          listfs.append({ 
            'name' : f'{f}/', 
            'path' : sp(f'{parpt}/{f}/')
          })
        else:
          listfs.append({ 
            'name' : f, 
            'path' : sp(f'{parpt}/{f}')
          })
  else:
    view['noncsv'] = True
    view['noncsv_plain'] = plain_render_file(getf) if getview == 'plain' else ''

  if getf.endswith('.csv'):
    view['csvshow'] = html_render_csv(getf)
    view['noncsv']  = False

  address   = []
  addrbuild = ''
  if getf_html: 
    for path in getf_html.strip('/').split('/'):
      addrbuild += f'/{path}'
      address.append({ 
        'name'      : f'{path}', 
        'path'      : sp(f'{addrbuild}'),
        'separator' : '/'
      })

  view['listfs']          = listfs
  view['address']         = address
  view['getf_html']       = getf_html
  view['getf_html_sp']    = sp(getf_html)
  view['getview_query']   = f'&view={getview}' if getview else ''
  view['show_header']     = False if get_query('hide') == 'true' else True


  return render_template('acmedash.html', view=view)


if __name__ == '__main__':
    app.run(debug=True)


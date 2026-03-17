#!/usr/bin/env python3

# activity metrics: dashboard (acmedash)
# this app uses flask & gunicorn with ryt/runapp for deployment
# latest source & documentation at: https://github.com/ryt/activity-metrics.git

import os
import sys
import time
import itertools
import importlib

from flask import Flask
from flask import request
from flask import render_template
from flask import jsonify, send_file
from configparser import ConfigParser

from __init__ import __version__
from acme.core.settings import Settings

configDir   = Settings.settings('acme.configDir')
appsDirName = Settings.settings('workspace.appsDirName')

app = Flask(__name__)

# -- set timezone to america/los_angeles -- #
os.environ['TZ'] = 'America/Los_Angeles'
time.tzset()

# -- runapp ssl settings start: parse runapp.conf (if it exists) and apply ssl settings -- #
conf = f'{configDir}runapp.conf'
sslcertkey = ''
if os.path.exists(conf):
  with open(conf) as cf:
    cfparser = ConfigParser()
    cfparser.read_file(itertools.chain(['[global]'], cf), source=conf)
    try:
      sslcertkey = cfparser.get('global', 'sslcertkey')
    except:
      pass
# -- runapp ssl settings end -- #

# -- get web config values -- #
web_limitpath = Settings.settings('web.limitpath')
web_app_path = Settings.settings('web.app_path')
web_secret_key = Settings.settings('web.secret_key')

# set & update default values for acmedash web configs
limitpath  = web_limitpath.rstrip('/') + '/' if web_limitpath else ''
app_path   = web_app_path if web_app_path else '/'
secret_key = web_secret_key if web_secret_key else ''

if secret_key:
  app.secret_key = secret_key # set flask secret key


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

  module_script = ''
  module_name = ''
  module_call = ''

  gqm = get_query('m')
  lqm = limitpath.rstrip('/') + '/' + gqm.lstrip('/') if limitpath else ''

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

    # default local app modules import

    Settings.setWorkspaceDir(getm1)

    addNavLinks   = Settings.settings('web.addNavLinks')
    runLocalApps  = Settings.settings('web.runLocalApps')

    view['add_nav_links'] = addNavLinks

    module_list = {}
    for r in runLocalApps:
      module_list[r[2]] = (r[0], r[1])

    if module == 'about':
      sys.path.append(f'{getm1}/')
      module_local_init = importlib.import_module(f'{appsDirName}.__init__')
      importlib.reload(module_local_init)
      view['version']['local'] = module_local_init.__version__

    elif module in module_list:

      module_name   = module_list[module][0]
      module_script = module_list[module][1]
      module_call   = module_script.rstrip('.py')

      if os.path.isfile(f'{getm1}/{appsDirName}/{module_script}'):
        sys.path.append(f'{getm1}/{appsDirName}/')
        module_run = importlib.import_module(module_call)
        importlib.reload(module_run)

        received_output = module_run.run_main(getm)

        # check if received output is send_file_object or jsonify_object
        # if so serve either one appropriately, if not carry on
        if isinstance(received_output, dict):
          if 'send_file_object' in received_output:
            return send_file(
              received_output['send_file_object']['buf'], 
              mimetype=received_output['send_file_object']['mimetype']
            )
          elif 'jsonify_object' in received_output:
            return jsonify(received_output['jsonify_object'])

        view['message']       = ''
        view['output_html']   = received_output

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


def main():
  sslck = sslcertkey.split(' ')
  if len(sslck) == 2:
    app.run(ssl_context=(sslck[0], sslck[1]), debug=True)
  else:
    app.run(debug=True)


if __name__ == '__main__':
  main()

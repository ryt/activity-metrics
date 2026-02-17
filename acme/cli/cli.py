#!/usr/bin/env python3

from __init__ import __version__

import os
import re
import sys
import pydoc
import importlib

from types import SimpleNamespace

from acme.cli  import cmd
from acme.cli  import docs

from acme.core import utils
from acme.core import macros
from acme.core import options
from acme.core import process
from acme.core import validate

# acme cli usage
#
# 1. Navigate to the parent of your `logs` directory. For example:
#
#      cd  ~/Documents/Metrics/
#
# 2. Use the acme command. Examples:
#
#      acme
#      acme  stats
#      acme  list-files
#      acme  today
#      acme  1/1
#      acme  1/1/2024
#      acme  gencsv today
#      acme  util makefiles
#
# 2a. The second argument can also be used to explicitly set the logs directory or it's parent.
#
#      acme ~/Documents/Metrics/ stats
#      acme ~/Documents/Metrics/ today
#
# Note: By default, acme will look for `./logs/` in the current working directory and parent directories.


"""
List of parameters handled by acme cli:

  params[0]         params[1]         params[2]         etc... 
  ------------------------------------------------------------
  (stats|-s)
  (list-files|-l)


  {date_input}
  (M/D|M-D)
  (Y-M-D|Y/M/D)
  (M-D-Y|M/D/Y)
  (today|tod|-t|yesterday|yest|-y)


  (gencsv|-g)       {date_input}
  (gencsv|-g)       {date_input}      {module_options}


  (utility|util)    (arg1)   (arg2)   (arg3)   etc..
  (utility|util)    (help|-h)
  (utility|util)    (man)

  man
  (help|--help|-h)
  (--version|-v)

"""


def cli_main(params, callname, meta):
  # ---- cli options: main ---- #
  output = []

  # -- default: no parameters -> run 'stats' -- #

  if len(params) == 0:
    return validate.validate_files(meta.logs_dir)

  arg1 = params[0]

  # -- stats & utils -- #

  if arg1 in ('stats','-s'):
    validate.validate_files(meta.logs_dir)

  elif arg1 in ('list-files','-l'):
    validate.validate_files(meta.logs_dir, True)

  elif arg1 in ('utility','util','-u'):
    cli_utils(params[1:], arg1, meta)

  # -- acme {date_input} -- #

  elif macros.is_date_input(arg1):
    output += process.handle_date_input(parsed=macros.parse_date_input(arg1), meta=meta)

  # -- acme gencsv {date_input} -- #

  elif arg1 in ('gencsv','-g'):
    output += process.handle_gencsv(params, callname, meta)

  # -- invalid command default message -- #

  else:
    output += [f"Invalid command '{arg1}'. Use 'man' or 'help' for proper usage."]


  print('\n'.join(output)) if output else None




def cli_utils(params, callname, meta):
  # ---- cli options: utils ----  #

  uname = 'util' if callname  == 'util' else 'utility'
  use_help = f"Use 'acme {uname} man' or 'acme {uname} help' for proper usage."


  if len(params) == 0:
    print(use_help)
    return
  
  com        = params[0]
  directory  = params[1] if len(params) >= 2 else './'
  applyf     = params[2] if len(params) >= 3 else ''

  if com == 'makefiles':
    utils.make_files(directory, applyf)

  elif com == 'makedirs':
    utils.make_dirs(directory, applyf)

  elif com == 'cleangen':
    utils.cleangen(meta)

  elif com == 'http':
    from acme.integrations import http
    http.http_options(params, callname, meta)

  elif com == 'todoist':
    from acme.integrations import todoist
    todoist.todoist_options(params)

  elif com == 'garmin':
    from acme.integrations import garmin
    garmin.garmin_options(params)

  elif com in ('--help', '-h', 'help'):
    print(f'{docs.__utils__.strip()}\n\n')

  elif com == 'man':
    pydoc.pager(f'{docs.__utils__.strip()}\n\n')

  elif com in ('--version', '-v'):
    print(f"Activity Metrics Utility, Version {meta.version}\n{meta.copyright}")

  else:
    print(use_help)



def cli_dash(params, callname, meta):
  # ---- cli options: dash ----  #

  use_help = '\n'.join((
    'To run acme dash, please choose one of two metods:',
    '  - acme dash dev',
    '  - acme dash prod',
    'Options:',
    '  - acme dash (dev|prod) (reload|start|stop|restart|list|debug)',
  ))


  if len(params) == 0:
    print(use_help)
    return
  
  type    = params[0]
  action  = params[1] if len(params) >= 2 else 'list' # default action: list

  if type == 'dev':
    web = f'{meta.acme_dir}web/'
    sys.path.append(web)
    print(f'Action: {action}. Running acme dash development server at port {options.PORT_DEV}.')
    # import & start flask app: acmedash
    import acmedash
    acmedash.main()

  elif type == 'prod':
    print(f'Action: {action}. Running acme dash via gunicorn/runapp at port {options.PORT_PROD}.')
    # the prod option currently uses the gunicorn wrapper runapp
    # from: https://github.com/ryt/runapp (requires version 1.4+)
    cmd.runapp(
      action,
      options.CONFIG_DIR_FULL,
      os.path.dirname(os.path.dirname(meta.acme_dir)),
    )

  elif type in ('--help', '-h', 'help'):
    print(use_help)

  elif type == 'man':
    pydoc.pager(f'\n{use_help}\n\n')

  elif type in ('--version', '-v'):
    print(f'Activity Metrics Dash, Version {meta.version}\n{meta.copyright}')

  else:
    print(use_help)



def main():
  # -- main cli app gateway -- #

  params   = sys.argv[1:]
  callname = sys.argv[0]

  # main acme installation dir <- from cli.py
  acme_dir = f'{os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))}/'

  # -- section: help & docs -- #

  arg1 = params[0] if len(params) > 0 else ''

  if arg1 in ('--version','-v'):
    return print(f'Activity Metrics, Version {__version__}')

  # print help manual docs

  elif arg1 in ('--help','-h','help'):
    return print(docs.__manual__.strip() + '\n')

  # page help manual docs instead of printing

  elif arg1 == 'man':
    output = docs.__manual__.strip() + '\n\n'
    return pydoc.pager(output)


  # -- section: acme dash (logs_dir not required) -- #

  elif arg1 in ('dash','-d'):
    return cli_dash(
      params[1:],
      arg1,
      meta=SimpleNamespace(
        version=__version__,
        copyright=docs.__copyright__,
        acme_dir=acme_dir,
      )
    )


  # -- section: cli options that require logs_dir -- #

  # Allows path/to/dir/ to be specified explicitly in the first argument of 'acme'.
  # If path/to/dir/ is set, acme will look for the logs directory inside of it or in one of it's parents.

  if len(sys.argv) > 1 and sys.argv[1].endswith('/'):
    params = sys.argv[2:]
    specified_path = sys.argv[1]
    find_logs = utils.find_path(options.LOGS_NAME, specified_path)
  else:
    find_logs = utils.find_path(options.LOGS_NAME)

  if find_logs:

    parent    = os.path.dirname(find_logs)
    logs_dir  = f'{parent}/{options.LOGS_NAME}/'
    gen_dir   = f'{parent}/{options.GEN_NAME}/'
    app_dir   = f'{parent}/{options.APP_NAME}/'

    cli_main(
      params,
      callname,
      meta=SimpleNamespace(
        version=__version__,
        copyright=docs.__copyright__,
        manual=docs.__manual__,
        acme_dir=acme_dir,
        logs_dir=logs_dir,
        gen_dir=gen_dir,
        app_dir=app_dir,
      )
    )

  else:

    print('\n'.join((
      f'Logs directory `{options.LOGS_NAME}` not found.',
      'You have two options:',
      ' - Run this command from within the metrics directory.',
      ' - Explicitly set the metrics directory as the second argument. (e.g. acme ~/metrics/ ...)',
      ))
    )

  # -- end: cli options -- #


if __name__ == '__main__':
  main()



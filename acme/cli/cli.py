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


  # -- start: parsing parameters/arguments -- #

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

    parsed       = macros.parse_date_input(arg1)
    parsed_slash = parsed['res_ymd_slash']
    parsed_dash  = parsed['res_ymd_dash']
    parsed_log   = parsed['res_ymd_log']
    parsed_name  = parsed['res_key_name']
    parsed_each  = parsed['res_each']

    head_text = f"Analyzing data for {parsed_name + ', ' if parsed_name else ''}{parsed_dash}:"

    # first_line_len = len(head_text)

    output += ['----'] # [0:first_line_len]]
    output += [f'{head_text}']

    # look for files
    output += [f'- Looking for {parsed_slash}.txt in {meta.logs_dir}']
    output += [f'- Looking for {parsed_slash}{{custom}}.txt in {meta.logs_dir}']
    output += [f'- Looking for {parsed_dash}.txt in {meta.logs_dir}']
    output += [f'- Looking for {parsed_dash}{{custom}}.txt in {meta.logs_dir}']

    # last_line_len = len(output[-1])
    output += ['----'] # [0:last_line_len]]


  # -- acme gencsv {date_input} -- #

  elif arg1 in ('gencsv','-g'):

    if len(params) > 1:
      arg2 = params[1] # date or keyword

      module_options = params[2] if len(params) > 2 else False

      # Section: Intervals (TODO as of 1/29/2026)
      #   Commas can be used in the {date_input} to specify interval 'from' and 'to' dates,
      #   along with an additional 'separator' text for the filename.
      #   Intervals can be used as follows:
      #
      #       gencsv   {interval_from},{interval_to}
      #       gencsv   {interval_from},{interval_to},{interval_seperator}
      #
      #   If commas are detected, the interval parameters will be parsed before everything else.

      valid_interval_input = macros.check_is_valid_interval(arg2)


      parsed = macros.parse_date_input(arg2)
      parsed_slash = parsed['res_ymd_slash']
      parsed_dash  = parsed['res_ymd_dash']

      # -- look for single log files (date) -- #

      filename = f'{meta.logs_dir}{parsed_slash}.txt'

      if not valid_interval_input and os.path.exists(filename): # single date instead of interval

        # -- start: import custom modules -- #
        
        # -- import settings: local <-> default -- #
        # since both {meta.app_dir} and {meta.acme_dir}web/modules/ are added to sys.path above (as first & second)
        # the module_settings.py file will be imported from either location (local or default).
        # since {meta.app_dir} is the first sys.path appended, the local file will override the default file 
        # to be imported as the first module_settings if it is available.

        sys.path.append(meta.app_dir)                     # first path: local
        sys.path.append(f'{meta.acme_dir}web/modules/')   # second path: default

        import module_settings

        glossary          = module_settings.use_glossary
        default_modules   = module_settings.use_default_modules
        local_modules     = module_settings.run_local_modules

        apply_modules     = {}
        apply_glossary    = {}

        if glossary:
          apply_glossary[glossary] = importlib.import_module(glossary) # imports glossary from {meta.app_dir}

        for dm in default_modules:
          if dm:
            apply_modules[dm] = importlib.import_module(dm) # imports modules from {meta.acme_dir}acme/web/modules/

        # -- end: import custom modules -- #

        # convert individual log txt file
        with open(filename, 'r') as file:
          entries = file.read()

        entries = macros.csvtext(
          process.modify_csv(
            process.convert_to_csv(
              entries, 
              parsed_dash, 
              SimpleNamespace(
                apply_modules=apply_modules,
                apply_glossary=apply_glossary,
                glossary=glossary,
              )
            ), 
            add_header=True, 
            add_footer=True,
            module_options=module_options,
            apply_modules=apply_modules,
          )
        )

        # generate individual log csv file
        genfile = f'{meta.gen_dir}{parsed_dash}.csv'
        utils.write_to_file(genfile, entries)
        output += [f'Generated CSV file {genfile} successfully.']


      # -- start: look for collections of log files (month, year) -- #

      elif not valid_interval_input and re.search(r'^\d{4}(?:\/\d{2})?$', parsed_slash):

        lenfn = len(parsed_slash)

        # -- generate year collections -- #
        if lenfn == 4:
          output = process.generate_collections('year', output, meta.logs_dir, parsed_slash, parsed_dash, module_options)

        # -- generate month collections -- #
        elif lenfn == 7:
          output = process.generate_collections('month', output, meta.logs_dir, parsed_slash, parsed_dash, module_options)

      # -- end: look for collections -- #

      # -- start: process intervals -- #

      elif valid_interval_input:

        pif = valid_interval_input['parsed_interval_from']
        pit = valid_interval_input['parsed_interval_to']

        pif_ymd_dash = pif['res_ymd_dash']
        pit_ymd_dash = pit['res_ymd_dash']

        pif_Y = pif['res_each']['Y']
        pit_Y = pit['res_each']['Y']
        pit_M = pit['res_each']['M']
        pit_D = pit['res_each']['D']

        to_format = f'{pit_M}-{pit_D}' if pif_Y == pit_Y else pit_ymd_dash # option for: _01-01 instead of _2024-01-01
        genfile   = f'{pif_ymd_dash}{valid_interval_input["interval_seperator"]}{to_format}.csv'

        output += [f'Creating a collection for intervals from {pif_ymd_dash} to {pit_ymd_dash}:']
        output += ['...']
        
        # todo: parse interval logs
        # todo: generate interval collection csv {genfile}

        output += [f'Mock-generated CSV file {genfile} successfully.']

      # -- end: process intervals -- #

      else:
        output += [f'Log file {filename} does not exist.']

    else:
      output += [f'Please specify a valid date (Y-m-d), month (Y-m), or year (Y).']


  # -- invalid command default message -- #

  else:
    output += [f"Invalid command '{arg1}'. Use 'man' or 'help' for proper usage."]
  
  # -- end: parsing arguments -- #

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
    make_files(directory, applyf)

  elif com == 'makedirs':
    make_dirs(directory, applyf)

  elif com == 'cleangen':
    cleangen()

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
    print(f"Activity Metrics Utility, ACME Version {meta.version}\n{meta.copyright}")

  else:
    print(use_help)



def cli_dash(params, callname, meta):

  # ---- cli options: dash ----  #

  use_help = '\n'.join((
    'To run acme dash, please choose one of two metods:',
    '  - acme dash dev',
    '  - acme dash prod',
    'Options:',
    '  - acme dash (dev|prod) (reload|start|stop|restart|debug)',
  ))


  if len(params) == 0:
    print(use_help)
    return
  
  type    = params[0]
  action  = params[1] if len(params) >= 2 else 'reload'

  if type == 'dev':
    web = f'{meta.acme_dir}web/'
    sys.path.append(web)
    print(f'Action: {action}. Running acme dash development server at port 5000.')
    # import & start flask app: acmedash
    import acmedash
    acmedash.main()

  elif type == 'prod':
    print(f'Action: {action}. Running acme dash production server at port 8100.')

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



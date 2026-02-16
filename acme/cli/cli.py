#!/usr/bin/env python3

# Usage
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

from __init__ import __version__

import os
import re
import sys
import pydoc
import importlib

from types import SimpleNamespace

from acme.cli import docs
from acme.core import macros
from acme.core import process
from acme.core import validate

logs_name = 'logs'
gen_name  = 'gen'
app_name  = 'app'


def find_path(name, curr=os.path.abspath(os.curdir)):
  """Checks if directory (name) exists in specified (curr) or parents"""

  while True:
    search_path = os.path.join(curr, name)
    if os.path.isdir(search_path):
      return search_path
    
    par = os.path.dirname(curr)
    
    if curr == par:
      return None
    
    curr = par

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

# cli options: main

def cli_main(params, called, meta):

  # -- start: global headers & settings -- #

  #global acme_dir, logs_dir, gen_dir, app_dir
  #global glossary, default_modules, local_modules, apply_modules, apply_glossary
  #global macros, utils, module_settings

  acme_dir = f'{os.path.dirname(os.path.dirname(os.path.abspath(os.path.realpath(__file__))))}/'

  logs_dir = meta['logs_dir']
  gen_dir  = meta['gen_dir']
  app_dir  = meta['app_dir']

  sys.path.append(app_dir)                     # first
  sys.path.append(f'{acme_dir}web/modules/')   # second

  from acme.core import macros
  from acme.core import utils

  # -- import settings: local or default -- #
  # since both {app_dir} and {acme_dir}web/modules/ are added to sys.path above (as first & second),
  # the module_settings.py file will be imported from either location (local or default).
  # since {app_dir} is the first sys.path, the local file will override & be imported
  # as the first module_settings if available over the default settings

  import module_settings

  # -- start: import custom modules -- #

  glossary          = module_settings.use_glossary
  default_modules   = module_settings.use_default_modules
  local_modules     = module_settings.run_local_modules

  apply_modules     = {}
  apply_glossary    = {}

  if glossary:
    # imports glossary from {app_dir}
    apply_glossary[glossary] = importlib.import_module(glossary)

  for dm in default_modules:
    if dm:
      # imports modules from {acme_dir}acme/web/modules/
      apply_modules[dm] = importlib.import_module(dm)

  # -- end: import custom modules

  ## -- end: global headers & settings

  output = []

  if len(params) == 0:

    # run 'stats' by default

    validate.validate_files(logs_dir)


  # -- start: parsing arguments

  else:

    if params[0]:
      arg1 = params[0]

      # -- stats & utils -- #

      if arg1 in ('stats','-s'):
        validate.validate_files(logs_dir)

      elif arg1 in ('list-files','-l'):
        validate.validate_files(logs_dir, True)

      elif arg1 in ('utility','util'):
        cli_utils(params[1:], arg1, meta)

      # -- main app start: acme {date_input} -- #

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
        output += [f'- Looking for {parsed_slash}.txt in {logs_dir}']
        output += [f'- Looking for {parsed_slash}{{custom}}.txt in {logs_dir}']
        output += [f'- Looking for {parsed_dash}.txt in {logs_dir}']
        output += [f'- Looking for {parsed_dash}{{custom}}.txt in {logs_dir}']

        # last_line_len = len(output[-1])
        output += ['----'] # [0:last_line_len]]

      # -- end: acme {date_input}

      # -- start: acme gencsv {date_input}

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

          # -- look for single log files (date)

          filename = f'{logs_dir}{parsed_slash}.txt'

          if not valid_interval_input and os.path.exists(filename):

            # convert individual log txt file
            with open(filename, 'r') as file:
              entries = file.read()
            entries = macros.csvtext(
              process.modify_csv(
                process.convert_to_csv(entries, parsed_dash, SimpleNamespace(
                    apply_modules=apply_modules,
                    apply_glossary=apply_glossary,
                    glossary=glossary,
                  )), 
                add_header=True, 
                add_footer=True,
                module_options=module_options,
                apply_modules=apply_modules,
              )
            )

            # generate individual log csv file
            genfile = f'{gen_dir}{parsed_dash}.csv'
            utils.write_to_file(genfile, entries)
            output += [f'Generated CSV file {genfile} successfully.']


          # -- start: look for collections of log files (month, year) -- #

          elif not valid_interval_input and re.search(r'^\d{4}(?:\/\d{2})?$', parsed_slash):

            lenfn = len(parsed_slash)

            # -- generate year collections -- #
            if lenfn == 4:
              output = process.generate_collections('year',output,logs_dir, parsed_slash, parsed_dash, module_options)

            # -- generate month collections -- #
            elif lenfn == 7:
              output = process.generate_collections('month',output,logs_dir,parsed_slash,parsed_dash,module_options)

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

      # -- end: acme gencsv {date_input} -- #

      else:
        output += [f"Invalid command '{arg1}'. Use 'man' or 'help' for proper usage."]

  
  # -- end: parsing arguments -- #

  print('\n'.join(output)) if output else None


# cli options: utils

def cli_utils(params, called, meta):

  uname = 'util' if called  == 'util' else 'utility'
  use_help = f"Use 'acme {uname} man' or 'acme {uname} help' for proper usage."

  ## -- start: global headers & settings

  #global logs_dir, gen_dir, app_dir, nl, hr

  logs_dir = meta['logs_dir']
  gen_dir  = meta['gen_dir']
  app_dir  = meta['app_dir']

  
  ## -- end: global headers & settings

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
    http.http_options(params, called, meta)

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
    print(f"Activity Metrics Utility, ACME Version {meta['version']}\n{meta['copyright']}")

  else:
    print(use_help)


def main():

  analyze_params = sys.argv[1:]
  analyze_caller = sys.argv[0]

  # -- help & docs -- #

  arg1 = analyze_params[0] if len(analyze_params) > 0 else ''

  if arg1 in ('--version','-v'):
    return print(f"Activity Metrics, Version {__version__}")

  # prints the help manual

  elif arg1 in ('--help','-h','help'):
    return print(docs.__manual__.strip() + '\n')

  # pages the help manual instead of printing

  elif arg1 == 'man':
    output = docs.__manual__.strip() + '\n\n'
    return pydoc.pager(output)

  # -- end help & docs -- #

  # Allows path/to/dir/ to be specified explicitly in the first argument of 'acme'.
  # If path/to/dir/ is set, acme will look for the logs directory inside of it or in one of it's parents.

  if len(sys.argv) > 1 and sys.argv[1].endswith('/'):
    analyze_params = sys.argv[2:]
    specified_path = sys.argv[1]
    find_logs = find_path(logs_name, specified_path)
  else:
    find_logs = find_path(logs_name)

  if find_logs:

    parent    = os.path.dirname(find_logs)
    logs_dir  = f'{parent}/{logs_name}/'
    gen_dir   = f'{parent}/{gen_name}/'
    app_dir   = f'{parent}/{app_name}/'

    cli_main(analyze_params, analyze_caller, { 
      'version'   : __version__,
      'manual'    : docs.__manual__,
      'logs_dir'  : logs_dir,
      'gen_dir'   : gen_dir,
      'app_dir'   : app_dir,
    })

  else:

    print('\n'.join((
      f'Logs directory `{logs_name}` not found.',
      'You have two options:',
      ' - Run this command from within the metrics directory.',
      ' - Explicitly set the metrics directory as the second argument. (e.g. acme ~/metrics/ ...)',
      ))
    )


if __name__ == '__main__':
  main()



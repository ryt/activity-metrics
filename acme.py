#!/usr/bin/env python3

# activity metrics (acme)
# copyright (c) 2024 ray, https://github.com/ryt
# latest source & documentation at: https://github.com/ryt/activity-metrics.git

__author__  = 'Ray (github.com/ryt)'
__version__ = '0.2.7.dev2'
__manual__  = """
activity metrics: a tool to analyze & display personal activity statistics.
copyright (c) 2024 """ + __author__ + """
latest source & docs: https://github.com/ryt/activity-metrics

Usage:

  Show log file statistics and list all found log files.
  ------------------------------------------------------
  Run       Command
  -------------------------
  ame       
  acme      (stats|-s)
  acme      (list-files|-l)


  Analyze entries for a specific date or today.
  ---------------------------------------------
  Run       Date
  ------------------------------------------
  acme      {date_input}
  acme      (M/D|M-D)
  acme      (Y-M-D|Y/M/D)
  acme      (M-D-Y|M/D/Y)
  acme      (today|tod|-t|yesterday|yest|-y)


  Generate a timesheet CSV file for a specific date. Create columns with categorize.
  ----------------------------------------------------------------------------------
  Run       Generate CSV      Date               Module Options
  ---------------------------------------------------------------
  acme      (gencsv|-g)       {date_input}
  acme      (gencsv|-g)       {date_input}       {module_options}


  Interface for the utility script. For list of commands, use 'acme util help'!
  -----------------------------------------------------------------------------
  Run       Utility           Input
  --------------------------------------------------------
  acme      (utility|util)    (arg1)      (arg2)    etc..
  acme      (utility|util)    (help|-h)
  acme      (utility|util)    (man)


  Run       Help Manual & About
  -----------------------------
  acme      man
  acme      (help|--help|-h)
  acme      (--version|-v)


Usage Help:

  If your log files aren't being read, remember by default acme looks for the ./logs/ directory in the current working directory. 
  To have your log files be read, you'll have to navigate (cd) into the parent of the logs directory and run the commands:

  ----------------------------------
  cd        /path/to/logs-or-parent/
  acme      {command}
  ----------------------------------

  However, if you want to explicitly set a ./logs/ directory or it's parent while running the command, you can use the second argument 
  to set a directory path (ending with a slash) add all other arguments after it.

  -------------------------------------------------
  acme      /path/to/logs-or-parent/      {command}
  -------------------------------------------------


"""

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

import os
import sys
import pydoc
import analyze

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


def main():

  analyze_params = sys.argv[1:]
  analyze_caller = sys.argv[0]

  # -- help & docs -- #

  arg1 = analyze_params[0] if len(analyze_params) > 0 else ''

  if arg1 in ('--version','-v'):
    return print(f"Activity Metrics, Version {__version__}")

  # prints the help manual

  elif arg1 in ('--help','-h','help'):
    return print(__manual__.strip() + '\n')

  # pages the help manual instead of printing

  elif arg1 == 'man':
    output = __manual__.strip() + '\n\n'
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

    analyze.analyze(analyze_params, analyze_caller, { 
      'version'   : __version__,
      'manual'    : __manual__,
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



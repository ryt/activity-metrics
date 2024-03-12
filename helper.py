#!/usr/bin/env python3

# Notes:
# - Version number of this script only tracks the updates of this script and not the main application (analyze.py).
# - Originally written as a bash script in the original 0.0.1 version.

v = '0.0.2'
c = 'Copyright (C) 2024 Ray Mentose.'
help_text = """
This script provides helper tools and API-based service utilities.
Read "Utilities.md" for detailed usage manual and related documentation.

Usage:

  Commands to create default date files (01-31.txt) and default month directories (01-12/)
  ----------------------------------------------------------------------------------------
  Helper         Command      Parent    Apply
  -------------------------------------------
  ./helper       makefiles    dir/
  ./helper       makedirs     dir/
  ./helper       makefiles    dir/      apply
  ./helper       makedirs     dir/      apply

  Commands to retrieve and save Todoist tasks that have valid log file names (e.g. 01/01.txt)
  -------------------------------------------------------------------------------------------
  Helper         Todoist     Action      Id       Save/Filename
  ---------------------------------------------------------------------------
  ./helper       todoist     get-task    12345
  ./helper       todoist     get-task    12345    save=../logs/2024/01/01.txt
  ./helper       todoist     get-task    12345    autosave

"""

import sys, os, json, subprocess

logs_dir = '../logs/'
gen_dir  = '../gen/'

def make_files(directory, applyf):
  if applyf == 'apply':
    print(f'Applying making files in {directory}')
    for i in range(1, 32):
      day = str(i).zfill(2)
      open(os.path.join(directory, f'{day}.txt'), 'a').close()
      print(f"touch {os.path.join(directory, f'{day}.txt')} applied")
  else:
    print(f'Mock-making files in {directory}')
    for i in range(1, 32):
      day = str(i).zfill(2)
      print(f"touch {os.path.join(directory, f'{day}.txt')}")

def make_dirs(directory, applyf):
  if applyf == 'apply':
    print(f'Applying making dirs in {directory}')
    for i in range(1, 13):
      month = str(i).zfill(2)
      os.makedirs(os.path.join(directory, month), exist_ok=True)
      print(f'mkdir {os.path.join(directory, month)} applied')
  else:
    print(f'Mock-making dirs in {directory}')
    for i in range(1, 13):
      month = str(i).zfill(2)
      print(f'mkdir {os.path.join(directory, month)}')

def curl(url, headers = ''):
  curl_command = f'curl "{url}" -H "{headers}"'
  process = subprocess.run(curl_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output = process.stdout.decode('utf-8')
  error = process.stderr.decode('utf-8')
  if process.returncode == 0:
    return output
  else:
    return f'Error: {error}'


def todoist_options(args):

  action = args[1] if len(args) >= 2 else ''
  optid  = args[2] if len(args) >= 3 else ''
  savef  = args[3] if len(args) >= 4 else ''

  # Todoist API token should be stored in "~/.api_todoist" file.
  todoist_file = os.path.expanduser('~') + '/.api_todoist';

  with open(todoist_file) as f: api_token = f.read().strip()

  if api_token:

    # There are two types of task names that can be automatically parsed from Todoist:
    # 
    #   - formal    :  double-digit date & month (e.g. 01/01.txt, 01/11.txt, 12/12.txt)
    #   - informal  :  single/double-digit date & month (e.g. 1/1.txt, 02/3.txt, 3/25.txt)
    # 
    # Taks with either type of name can be retrieved as valid log files.

    # Retrieved tasks will be saved as log files as follows:
    #
    #   - The file's content will be the description/content of the task
    #   - The file's name & location will reflect to the the formal date format (e.g. YYYY/MM/DD.txt)
    #

    if action == 'get-task':

      # todo: get-task 3/11

      # get-task 12345
      if optid.isnumeric():
        response = curl(f'https://api.todoist.com/rest/v2/tasks/{optid}', f'Authorization: Bearer {api_token}')
        if response:
          task_json = json.loads(response)
          title = task_json['content']
          entry = task_json['description']
          date  = task_json['created_at']
          print(title)
          print(entry)
          print(date)
          if savef == 'autosave':
            print('(Mock) Auto smart save will look for formal log file dates (e.g. 01/01.txt) in the title & will fall back to the file creation date.')
          elif savef[0:5] == 'save=':
            print(f'(Mock) Save as: {logs_dir}{savef[5:]}')
          else:
            print('Just show')

    print(f'Todoist {action} {optid} {savef}')

  else:

    print(f'Todoist API token could not be found in {todoist_file}.')


def print_help():
  print(help_text.strip()+'\n')

def print_version():
  print(f'Activity Metrics Helper, Version {v}\n{c}')

def main():
  args = sys.argv[1:]
  if len(args) == 0:
    print('Use the help or -h command for proper usage.')
    return
  
  com        = args[0]
  directory  = args[1] if len(args) >= 2 else './'
  applyf     = args[2] if len(args) >= 3 else ''

  if com == 'makefiles':
    make_files(directory, applyf)
  elif com == 'makedirs':
    make_dirs(directory, applyf)
  elif com == 'todoist':
    todoist_options(args)
  elif com in ['help', '--help', '-h']:
    print_help()
  elif com in ['version', '--version', '-v']:
    print_version()
  else:
    print('Use the help or -h command for proper usage.')

if __name__ == '__main__':
  main()

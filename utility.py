#!/usr/bin/env python3

# Notes:
# - Earlier versions before 0.0.4 were named helper.py & helper.sh.
# - Version number of this script only tracks the updates of this script and not the main application (analyze.py).
# - Originally written as a bash script in the original 0.0.1 version.

v = '0.0.4'
c = 'Copyright (C) 2024 Ray Mentose.'
man = """
This script provides helper tools and utilities for API connections. Commands can also be run using "./analyze u".
Read "Utilities.md" for related documentation. API tokens are required for connecting to external services.

Usage:

  Create default date files (01-31.txt) and default month directories (01-12/)
  ----------------------------------------------------------------------------
  Analyze      Utility         Command      Parent    Apply
  ---------------------------------------------------------
  ./analyze    (utility|u)     makefiles    dir/
                               makedirs     dir/
                               makefiles    dir/      apply
                               makedirs     dir/      apply

  Retrieve and save Todoist tasks that have valid log file names (e.g. 01/01.txt)
  -------------------------------------------------------------------------------
  Analyze      Utility        Todoist     Action      Id/Date/Keyword       Save/Filename
  ---------------------------------------------------------------------------------------------
  ./analyze    (utility|u)    todoist     get-task    (12345|M/D|today)
                              todoist     get-task    12345                 save=2024/01/01.txt
                              todoist     get-task    12345                 (saveauto|autosave)

"""

import sys, os, re, json, subprocess, pydoc
from datetime import datetime
from datetime import timedelta

logs_dir = './logs/'
gen_dir  = './gen/'
app_dir  = './app/'

nl = '\n'
hr = '-' * 50

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

def todoist_task_operate(task_json, saveopt):
  """Operation for a single task from Todoist"""

  taskid    = task_json['id']
  title     = task_json['content']
  entries   = task_json['description']
  date      = task_json['created_at']

  print(f'Todoist task: {title} ({taskid}){nl}Task created at: {date}{nl}==')

  if saveopt in ('saveauto','autosave'):
    get_year       = date[0:4]
    title_date     = title.strip('.txt').split('/')
    save_log_file  = list(map(lambda i:'{:02d}'.format(int(i)), title_date))
    save_log_file  = f"{logs_dir}{get_year}/{'/'.join(save_log_file)}.txt"
    with open(save_log_file, 'w') as file:
      file.write(entries)
    print(f'Log file successfully saved at: {save_log_file}')

  elif saveopt[0:5] == 'save=':
    save_log_file = f'{logs_dir}{saveopt[5:]}'
    if save_log_file == logs_dir:
      print('Please enter a valid file name & path.')
    else:
      with open(save_log_file, 'w') as file:
        file.write(entries)
      print(f'Log file successfully saved at: {save_log_file}')

  elif saveopt == 'save':
    opts = ['To save as a log, please use one of the following options:',
            "- saveauto:  to automatically save the log using it's name & date",
            "- save=YYYY/MM/DD.txt:  to manually specify the name & location."]
    print('\n'.join(opts))

  else:
    print(f'{entries}{nl}==')


def todoist_options(args):

  action = args[1] if len(args) >= 2 else ''
  optid  = args[2] if len(args) >= 3 else ''
  savef  = args[3] if len(args) >= 4 else ''

  date_today = datetime.today()

  # Todoist API token should be stored in "{app_dir}.api_todoist" file.
  todoist_file = f'{app_dir}.api_todoist';

  with open(todoist_file) as f: api_token = f.read().strip()

  if api_token:

    # There are two types of task names that can be automatically parsed from Todoist:
    # 
    #   - formal    :  double-digit date & month (e.g. 01/01.txt, 01/11.txt, 12/12.txt)
    #   - informal  :  single+double-digit date & month (e.g. 1/1.txt, 12/3.txt, 3/25.txt)
    # 
    # Taks with either type of name can be retrieved as valid log files.

    # Retrieved tasks will be saved as log files as follows:
    #
    #   - The file's content will be the description/content of the task
    #   - The file's name & location will reflect the formal date format (e.g. YYYY/MM/DD.txt)
    #

    if action == 'get-task':

      # get-task (M/D, MM/DD, today)

      if optid in ('today','yesterday') or re.match(r'^(\d\d?\/\d\d?)(\/\d{4})?$', optid) is not None:

        # start optid parsing
        opm, opd, opy = '', '', ''
        if '/' in optid:
          opsplit = optid.split('/')
          opm = '{:02d}'.format(int(opsplit[0]))
          opd = '{:02d}'.format(int(opsplit[1]))
          opy = opsplit[2] if len(opsplit) > 2 else date_today.year
        elif optid == 'today':
          opm = date_today.strftime('%m')
          opd = date_today.strftime('%d')
          opy = date_today.strftime('%Y')
        elif optid == 'yesterday':
          yesterday = date_today - timedelta(days = 1)
          opm = yesterday.strftime('%m')
          opd = yesterday.strftime('%d')
          opy = yesterday.strftime('%Y')
        # end optid parsing

        search1 = f'{str(int(opm))}/{str(int(opd))}.txt' # M/D.txt
        search2 = f'{opm}/{opd}.txt' # MM/DD.txt

        api_get_tasks = curl(f'https://api.todoist.com/rest/v2/tasks', f'Authorization: Bearer {api_token}')

        if api_get_tasks.startswith('Error:') or not api_get_tasks.startswith(('{','[')):
          print(api_get_tasks)

        else:
          tasks_json = json.loads(api_get_tasks)
          matches = [t for t in tasks_json if t.get('content') in (search1, search2) ]
          search_msg = f'Total searched tasks: {len(tasks_json)}.'

          if not matches:
            print(search_msg)
            print(f"Tasks matching '{search1}' or '{search2}' could not be found.")
          else:
            print(search_msg)
            print(f'Found {len(matches)} task(s) matching the search:{nl}--')
            for m in matches:
              todoist_task_operate(m, savef)
              #print(m)
            print('--')


      # end get-task (M/D, MM/DD, today)

      # get-task 12345

      elif optid.isnumeric() and int(optid) > 1000:

        api_get_task = curl(f'https://api.todoist.com/rest/v2/tasks/{optid}', f'Authorization: Bearer {api_token}')

        if api_get_task.startswith('Error:') or not api_get_task.startswith(('{','[')):
          print(api_get_task)

        else:
          task_json = json.loads(api_get_task)
          todoist_task_operate(task_json, savef)

      # end get-task 12345

      else:
        print('Please enter a valid task id, date, or keyword.')

      # print(f'todoist {action} {optid} {savef}')
      # print('-' * 50)
    
    else:
      print("Please enter a valid command for Todoist. Use 'man' for list of commands.")

  else:

    print(f'Todoist API token could not be found in {todoist_file}.')


def utility(args, called):

  uname = 'u' if called  == 'u' else 'utility'
  use_help = f"Use '{uname} man' or '{uname} help' for proper usage."

  if len(args) == 0:
    print(use_help)
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

  elif com in ('--help', '-h', 'help'):
    print(f'{man.strip()}{nl}')

  elif com == 'man':
    pydoc.pager(f'{man.strip()}{nl}')

  elif com in ('--version', '-v'):
    print(f'Activity Metrics Utility, Version {v}{nl}{c}')

  else:
    print(use_help)

def main():
  utility(sys.argv[1:], sys.argv[0])

if __name__ == '__main__':
  main()

#!/usr/bin/env python3

import os
import re
import json

from datetime import datetime

from acme.cli  import cmd
from acme.core import macros


def todoist_task_operate(task_json, saveopt, append=False):
  """Operation for a single task from Todoist"""

  taskid    = task_json['id']
  title     = task_json['content']
  entries   = task_json['description']
  date      = task_json['created_at']

  print(f'Todoist task: {title} ({taskid}){nl}Created date: {date}{nl}==')

  if saveopt in ('saveauto','autosave'):
    get_year       = date[0:4]
    title_date     = re.search(r'\d{1,2}/\d{1,2}\.txt', title).group().strip('.txt').split('/')
    save_log_file  = list(map(lambda i:'{:02d}'.format(int(i)), title_date))
    save_log_file  = f"{logs_dir}{get_year}/{'/'.join(save_log_file)}.txt"
    # create the month directory if it doesn't already exist
    os.makedirs(os.path.dirname(save_log_file), exist_ok=True)
    with open(save_log_file, 'a' if append else 'w') as file:
      entries = nl + entries if append else entries
      file.write(entries)
    if append:
      print(f'Additional entries successfully appended to: {save_log_file}')
    else:
      print(f'Log file successfully saved at: {save_log_file}')

  elif saveopt[0:5] == 'save=':
    save_log_file = f'{logs_dir}{saveopt[5:]}'
    if save_log_file == logs_dir:
      print('Please enter a valid file name & path.')
    else:
      # create the month directory if it doesn't already exist
      os.makedirs(os.path.dirname(save_log_file), exist_ok=True)
      with open(save_log_file, 'a' if append else 'w') as file:
        entries = nl + entries if append else entries
        file.write(entries)
      if append:
        print(f'Additional entries successfully appended to: {save_log_file}')
      else:
        print(f'Log file successfully saved at: {save_log_file}')

  elif saveopt == 'save':
    opts = ['To save as a log, please use one of the following options:',
            "- saveauto:  to automatically save the log using it's name & date",
            "- save=YYYY/MM/DD.txt:  to manually specify the name & location."]
    print(nl.join(opts))

  else:
    print(entries)

  print('==')


def todoist_options(args):

  action = args[1] if len(args) >= 2 else ''
  optid  = args[2] if len(args) >= 3 else ''
  savef  = args[3] if len(args) >= 4 else ''

  date_today = datetime.today()


  # Todoist API token should be stored in "{app_dir}.api_todoist" file.
  todoist_file = f'{app_dir}.api_todoist';

  try:
    with open(todoist_file) as f: api_token = f.read().strip()

  except FileNotFoundError as e:
    print(f"Todoist api file '{todoist_file}' not found.")
    exit()

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

      # -- start: get-task {date-input}

      if macros.is_date_input(optid):

        parsed       = macros.parse_date_input(optid)
        parsed_dash  = parsed['res_ymd_dash']
        parsed_each  = parsed['res_each']

        opd = parsed_each['D']
        opm = parsed_each['M']
        opy = parsed_each['Y']

        search_list = []

        if opy and not opm and not opd:
          print(f'Please specify a month for the year {parsed_dash}. You can save up to 1 month collection at a time.')
          exit()
        elif opy and opm and not opd:
          print(f'Searching tasks for month, {parsed_dash}:')
          for i in range(1, 32):
            search1 = f'{str(int(opm))}/{i}.txt' # M/D.txt
            search2 = f'{opm}/{str(i).zfill(2)}.txt' # MM/DD.txt
            search_list.append({ 'search1': search1, 'search2': search2})
        else:
          print(f'Searching tasks for date, {parsed_dash}:')
          search1 = f'{str(int(opm))}/{str(int(opd))}.txt' # M/D.txt
          search2 = f'{opm}/{opd}.txt' # MM/DD.txt
          search_list.append({ 'search1': search1, 'search2': search2})


        api_get_tasks = cmd.curl(f'https://api.todoist.com/rest/v2/tasks', f'Authorization: Bearer {api_token}')

        if api_get_tasks.startswith('Error:') or not api_get_tasks.startswith(('{','[')):
          print(api_get_tasks)

        else:
          tasks_json = json.loads(api_get_tasks)
          search_msg = f'Total searched tasks: {len(tasks_json)}.'
          count_matches = 0

          print(search_msg)

          for date in search_list:
            # (below) changed from exact match tuple search: t.get('content') in (date['search1'], date['search2'])
            matches = [t for t in tasks_json if date['search1'] in t.get('content') or date['search2'] in t.get('content') ]
            if not matches:
              print(f"Tasks matching '{date['search1']}' or '{date['search2']}' could not be found.")
            else:
              print(f'Found {len(matches)} task(s) matching the search:{nl}--')
              # sort multiple matches by title ascending, use (reverse=True) for descending
              matches = sorted(matches, key=lambda x: x['content'])
              i = 0
              for m in matches:
                todoist_task_operate(m, savef, append=True if len(matches) > 1 and i > 0 else False)
                i += 1
              count_matches += 1
              print('--')

          print(f'--{nl}Total operated log files: {count_matches}.{nl}--')

      # -- end: get-task (M/D, MM/DD, today)

      # -- start: get-task 12345

      elif optid.isnumeric() and int(optid) > 1000:

        api_get_task = cmd.curl(f'https://api.todoist.com/rest/v2/tasks/{optid}', f'Authorization: Bearer {api_token}')

        if api_get_task.startswith('Error:') or not api_get_task.startswith(('{','[')):
          print(api_get_task)

        else:
          task_json = json.loads(api_get_task)
          todoist_task_operate(task_json, savef)

      # -- end: get-task 12345

      else:
        print('Please enter a valid task id, date, or keyword.')

      # print(f'todoist {action} {optid} {savef}')
      # print('-' * 50)
    
    else:
      print("Please enter a valid command for Todoist. Use 'man' for list of commands.")

  else:

    print(f'Todoist API token could not be found in {todoist_file}.')



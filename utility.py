#!/usr/bin/env python3

# activity metrics utility, (acme util)
# latest source & docs at: https://github.com/ryt/activity-metrics.git

man = """
This script provides helper tools and utilities for API connections. Commands can also be run using 'acme util'!
Read "Utilities.md" for related documentation. API tokens are required for connecting to external services.

Usage:

  Make Files: create default date files (01-31.txt) and default month directories (01-12/)
  ----------------------------------------------------------------------------------------
  <acme>  <Utility>        <Command>    <Parent>  <Apply>

  acme    (utility|util)   makefiles    dir/
                           makefiles    dir/      apply
                           makedirs     dir/
                           makedirs     dir/      apply


  Clean Logs: clean up the gen directory of generated csv logs older than 1 week.
  -------------------------------------------------------------------------------
  <acme>  <Utility>        <Command>

  acme    (utility|util)   cleangen


  HTTP Options: retrieve and save the output from an http(s) request (via json file) as a log file.
  -------------------------------------------------------------------------------------------------
  <acme>  <Utility>        <http>   <Command File>   <Date Input>     <Save/Filename>

  acme    (utility|util)   http     .acme_http.json       {date_input}
                           http     .acme_http.json       {date_input}     save=2026/01/01.txt
                           http     .acme_http.json       {date_input}     (saveauto|autosave)

  - The default name of the http json file is ".acme_http.json". It can be changed to any name.
  - Options: In the http json file, "{date_input}" can be used to insert the entered date input
    in a "YYYY-MM-DD" format anywhere in the keys or values. (e.g. {"url":"http://api.url/{date_input}"})
  - {date_input} can be any valid date input listed in the main manual ("acme --help").

  (API) Todoist Options: retrieve and save tasks that have valid log file names (e.g. 01/01.txt)
  ----------------------------------------------------------------------------------------------
  <acme>  <Utility>        <Todoist>   <Action>    <Id/Date/Keyword>      <Save/Filename>

  acme    (utility|util)   todoist     get-task    (12345|{date_input})
                           todoist     get-task    (12345|{date_input})   save=2024/01/01.txt
                           todoist     get-task    (12345|{date_input})   (saveauto|autosave)

  - {date_input} can be any valid date input listed in the main manual ("acme --help").

  (API) Garmin Options: merge garmin csv logs into gencsv logs of given year (plus today and yesterday if applicable).
  --------------------------------------------------------------------------------------------------------------------
  <acme>  <Utility>        <Garmin>    <Action>        <Year>

  acme    (utility|util)   garmin      merge-gencsv    {year}

"""

import sys
import os
import re
import time
import json
import pydoc
import subprocess
import http.client
import pandas as pd
import urllib.parse

from datetime import datetime
from datetime import timedelta

from io import StringIO

import macros

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

def cleangen():
  """Removes gencsv files older than 1 week from gencsv directory"""
  files  = os.listdir(gen_dir)
  thresh = datetime.today().date() - timedelta(days=7)
  fcount = 0
  for name in files:
    if name.endswith('.csv'):
      stem = name[:-4] # remove .csv
      try:
        file_date = datetime.strptime(stem, "%Y-%m-%d").date()
        if file_date <= thresh:
          print(name)
          os.remove(f'{gen_dir}{name}')
          fcount += 1
      except ValueError: # not in YYYY-MM-DD format
        pass
  if fcount > 0:
    print(f"{('-'*14)}\nCleaned up {fcount} older gencsv file(s) from: {gen_dir}")
  else:
    print(f'Nothing to clean up.')


def curl(url, headers = ''):
  curl_command = f'curl "{url}" -H "{headers}"'
  process = subprocess.run(curl_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output = process.stdout.decode('utf-8')
  error = process.stderr.decode('utf-8')
  if process.returncode == 0:
    return output
  else:
    return f'Error: {error}'


def escape_for_csv(input):
  """Prepares the given input for csv output"""
  if isinstance(input, str):
    # escape a double quote (") with additional double quote ("")
    value = input.replace('"', '""')
    value = '"' + value + '"'
    return value
  else:
    return input


def http_options(args):

  httpfile   = args[1] if len(args) >= 2 else ''
  dateinput  = args[2] if len(args) >= 3 else ''
  savef      = args[3] if len(args) >= 4 else ''

  date_today = datetime.today()


  if not httpfile:
    exit(f'Please specify an http json file path.')

  # http json file should be stored in "{app_dir}/"
  httpjson_file = f'{app_dir}{httpfile}';

  try:
    with open(httpjson_file) as f: command = f.read().strip()

  except FileNotFoundError as e:
    print(f"HTTP json file `'{httpjson_file}'` not found.")
    exit()

  if command:

    if macros.is_date_input(dateinput):

      parsed       = macros.parse_date_input(dateinput)
      parsed_dash  = parsed['res_ymd_dash']
      parsed_each  = parsed['res_each']

      opd = parsed_each['D']
      opm = parsed_each['M']
      opy = parsed_each['Y']

      name_dict = {}

      print(f'Retrieving content for date, {parsed_dash}:')
      name1 = f'{str(int(opm))}/{str(int(opd))}.txt' # M/D.txt
      name2 = f'{opm}/{opd}.txt' # MM/DD.txt
      name_dict = { 'name1': name1, 'name2': name2}

      command = command.replace('{date_input}', parsed_dash)
      httpobj = json.loads(command)

      print('Running http request -> ', end='')

      try:
        start = time.perf_counter()
        # -- http.client connection -- #
        parsed      = urllib.parse.urlparse(httpobj['url'])
        domain      = parsed.netloc
        path        = parsed.path + ('?' + parsed.query if parsed.query else '')
        body        = urllib.parse.urlencode(httpobj['data'])
        method      = httpobj['method'].upper() if 'method' in httpobj else 'POST'
        contenttype = 'application/x-www-form-urlencoded'

        if 'headers' in httpobj and 'Content-Type' in httpobj['headers']:
          contenttype = httpobj['headers']['Content-Type']

        headers = {
          'Content-Type'    : contenttype,
          'Content-Length'  : str(len(body)),
        }

        connection=http.client.HTTPSConnection(domain, timeout=5); 
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse(); 
        output = response.read().decode('utf-8')
        status = response.status
        connection.close()
        # -- end http.client connection -- #
        elapsed = time.perf_counter() - start

        print(f'successful.') #{nl}--')
        print(f'Total time: {elapsed} sec{nl}--')

        if 'save' in savef:
          if not output:
            print('Nothing to save. The content of the output is empty.')
          elif status == 200:
            save_content_to_log(output, parsed_dash, name_dict, savef, False)
          else:
            print(f'Nothing to save. The server returned status: {status}.')
        else:
          if not output:
            print('Nothing to display. The content of the output is empty.')
          elif status == 200:
            print(output)
          else:
            print(f'Nothing to display. The server returned status: {status}.')

      except Exception as e:
        print(f'failed.{nl}--')
        print(f'Error: {e}')
      
      print('--')
    
    else:
      print("Please enter a valid date input for http options. Use 'man' for list of commands.")

  else:

    print(f'A valid json could not be found in {httpjson_file}.')



def save_content_to_log(content, date, name_dict, saveopt, append=False):
  """Operation to save given text content to log."""
  entries = content

  if saveopt in ('saveauto','autosave'):
    get_year       = date[0:4]
    save_log_file  = f"{logs_dir}{get_year}/{name_dict['name2']}" # name2 = MM/DD.txt
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


        api_get_tasks = curl(f'https://api.todoist.com/rest/v2/tasks', f'Authorization: Bearer {api_token}')

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

        api_get_task = curl(f'https://api.todoist.com/rest/v2/tasks/{optid}', f'Authorization: Bearer {api_token}')

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


def garmin_options(args):

  now = datetime.now()
  yst = now - timedelta(days=1)

  action = args[1] if len(args) >= 2 else ''
  year   = args[2] if len(args) >= 3 else now.year

  cat_name = 'Garmin Athletics'

  gen_dir  = f'{os.path.abspath(os.curdir)}/gen'
  gen_csv_metrics = f'{gen_dir}/{year}.csv'
  gen_csv_garmin  = f'{gen_dir}/services/garmin/{year}-garmin-activities.csv'

  if action == 'merge-gencsv':
    try:
      with open(gen_csv_garmin, 'r', encoding='utf-8') as f:
        valid_garmin_csv = f.read()
        print(f'Validated: {gen_csv_garmin}')
    except Exception as e:
      return print(f"Invalid: '{gen_csv_garmin}' could not be processed or found.")
    try:
      with open(gen_csv_metrics, 'r', encoding='utf-8') as g:
        valid_metrics_csv = g.read()
        print(f'Validated: {gen_csv_metrics}')
        if not valid_metrics_csv:
          print(f"Notice: the file '{gen_csv_metrics}' is empty.")
    except Exception as e:
      return print(f"Invalid: '{gen_csv_metrics}' could not be processed or found.")

    if f and g and valid_metrics_csv:
      # -- prevent duplication: check if existing garmin data -- #
      if f',{cat_name},' in valid_metrics_csv:
        return print(f'Existing Garmin data found in csv. Re-try after running acme gencsv year command again.')

      df = pd.read_csv(StringIO(valid_metrics_csv)) # get metrics as dataframe

      converted_garmin_data = []
      gf = pd.read_csv(StringIO(valid_garmin_csv))
      gf = gf.fillna('') # empty: NaN -> ''
      for _, row in gf.iterrows():
        # --metrics cols--
        # Date Duration C1 C2 C3 C4 ... Description Hours Splits
        # --garmin cols--
        # startTimeLocal activityId activityName activityTypeName activityTypeId 
        # distanceMI duration avgSpeedMPH maxSpeedMPH avgPaceMinSecMI maxPaceMinSecMI 
        # averageHR maxHR description 
        d_ddt = pd.to_datetime(row['startTimeLocal']).strftime('%m/%d/%Y')
        d_dhr = pd.to_datetime(row['startTimeLocal']).strftime('%-I%p').lower().replace('am','a').replace('pm','p')
        d_hrs = round(pd.to_timedelta(row['duration']).total_seconds() / 3600, 2)
        d_dts = ' '.join([(f'{d}: {row[d]};' if row[d] else '') for d in ''.join((
          'startTimeLocal activityId activityTypeId distanceMI duration avgSpeedMPH maxSpeedMPH ',
          'avgPaceMinSecMI maxPaceMinSecMI averageHR maxHR description')).split(' ')])
        data = {
          'Date'        : d_ddt,
          'Duration'    : macros.hours_to_human(d_hrs, True),
          'Description' : f"{d_dhr} {row['activityName']}, Details: [{d_dts.strip()}]",
          'Hours'       : d_hrs,
        }
        data_c2 = row['activityTypeName'].replace('_', ' ').title()
        if 'C1' in df.columns and 'C2' in df.columns: # categorized vs non-categorized metrics csv
          data['C1'] = cat_name
          data['C2'] = data_c2
        else:
          data['Description'] = f"{data['Description']} ({cat_name}, {data_c2})"
        converted_garmin_data.append(data)

      cgd_df = pd.DataFrame(converted_garmin_data) # get converted_garmin_data (cgd) as dataframe
      cgd_df = cgd_df.reindex(columns=df.columns, fill_value='') # empty rows: NaN -> ''

      # metrics df: adjust footer -> remove total logged
      df = df[df['Description'] != 'Total Logged Hours']
      df = pd.concat([df, cgd_df], ignore_index=True)
      df = df.sort_values(by='Date', ascending=True)
      sum_hours = round(df['Hours'].sum(), 2)

      # final df: adjust footer -> add back total logged
      df.loc[len(df)] = { col: {
        'Duration'    : macros.hours_to_human(sum_hours, True),
        'Description' : 'Total Logged Hours',
        'Hours'       : sum_hours,
      }.get(col,'') for col in df.columns } # empty rows: NaN -> ''

      df.to_csv(gen_csv_metrics, index=False)

      # -- additional day csv mergers (today, yesterday) for current year -- #
      if str(year) == str(now.year):
        ymd_tod = (now.strftime('%Y-%m-%d'), now.strftime('%m/%d/%Y'))
        ymd_yst = (yst.strftime('%Y-%m-%d'), yst.strftime('%m/%d/%Y'))
        tod_csv = f'{gen_dir}/{ymd_tod[0]}.csv'
        yst_csv = f'{gen_dir}/{ymd_yst[0]}.csv'
        garmin_merge_daycsv(cgd_df, yst_csv, ymd_yst, cat_name)
        garmin_merge_daycsv(cgd_df, tod_csv, ymd_tod, cat_name)
      # -- end: additional day csv files -- #

      print(f'Successfully merged "{os.path.basename(gen_csv_garmin)}" -> "{os.path.basename(gen_csv_metrics)}" for the year {year}.')


def garmin_merge_daycsv(cgd_df, day_csv, ymd_day, cat_name):
  try:
    with open(day_csv, 'r', encoding='utf-8') as f:
      valid_csv = f.read()
      print(f'Validated: {day_csv}')
      fgd_df = cgd_df[cgd_df['Date'] == ymd_day[1]].copy() # filtered garmin data (fgd) dataframe
      if not fgd_df.empty and not f',{cat_name},' in valid_csv: # non-empty frame & no-duplicate
        # day csv metrics day_df modifications
        day_df = pd.read_csv(StringIO(valid_csv)) # get day metrics as dataframe
        fgd_df = fgd_df.reindex(columns=day_df.columns, fill_value='') # reindex fgd -> empty rows: NaN -> ''
        day_df = day_df[day_df['Description'] != 'Total Logged Hours'] # adjust footer -> remove total logged
        day_df = pd.concat([day_df, fgd_df], ignore_index=True) # merge day_df and fgd_df
        sum_hours = round(day_df['Hours'].sum(), 2)

        # final day_df: adjust footer -> add back total logged
        day_df.loc[len(day_df)] = { col: {
          'Duration'    : macros.hours_to_human(sum_hours, True),
          'Description' : 'Total Logged Hours',
          'Hours'       : sum_hours,
        }.get(col,'') for col in day_df.columns } # empty rows: NaN -> ''

        day_df.to_csv(day_csv, index=False)
        print(f' -> Successfully merged day csv: {day_csv}')
  except Exception as e:
    print(f"Invalid: '{day_csv}' could not be processed or found.")


def utility(params, called, meta):

  uname = 'util' if called  == 'util' else 'utility'
  use_help = f"Use 'acme {uname} man' or 'acme {uname} help' for proper usage."

  ## -- start: global headers & settings

  global logs_dir, gen_dir, app_dir, nl, hr

  logs_dir = meta['logs_dir']
  gen_dir  = meta['gen_dir']
  app_dir  = meta['app_dir']

  nl = '\n'
  hr = '-' * 50
  
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
    http_options(params)

  elif com == 'todoist':
    todoist_options(params)

  elif com == 'garmin':
    garmin_options(params)

  elif com in ('--help', '-h', 'help'):
    print(f'{man.strip()}{nl}{nl}')

  elif com == 'man':
    pydoc.pager(f'{man.strip()}{nl}{nl}')

  elif com in ('--version', '-v'):
    print(f"Activity Metrics Utility, ACME Version {meta['version']}{nl}{meta['copyright']}")

  else:
    print(use_help)

def main():
  print("Please use 'acme util' command to run the the utility.")

if __name__ == '__main__':
  main()

#!/usr/bin/env python3

"""
Copyright (C) 2024 Ray Mentose. 
Latest source can be found at: https://github.com/ryt/activity-metrics
"""

v = '0.1.3'
c = 'Copyright (C) 2024 Ray Mentose.'
man = """
Activity Metrics: A tool to analyze & display personal activity statistics.

Usage:

  Show log file statistics and list all found log files.
  ------------------------------------------------------
  Analyze        Command
  ------------------------------
  ./analyze      (stats|-s)
  ./analyze      (list-files|-l)


  Analyze entries for a specific date or today.
  ---------------------------------------------
  Analyze        Date
  -------------------------
  ./analyze      (today|-t)


  Generate a timesheet CSV file for a specific date.
  --------------------------------------------------
  Analyze        Generate CSV      Date
  -----------------------------------------------
  ./analyze      (gencsv|-g)       (Y-m-d)
  ./analyze      (gencsv|-g)       (today|-t)
  ./analyze      (gencsv|-g)       (yesterday|-y)


  Interface for the utility script. For list of commands, use "./analyze u help".
  -------------------------------------------------------------------------------
  Analyze        Utility        Input
  ---------------------------------------------------------
  ./analyze      (utility|u)    (arg1)      (arg2)    etc..
  ./analyze      (utility|u)    (help|-h)
  ./analyze      (utility|u)    (man)


  Analyze        Help Manual & About
  ----------------------------------
  ./analyze      man
  ./analyze      (help|--help|-h)
  ./analyze      (--version|-v)

"""

import sys
import os
import re
import subprocess
import pydoc
import itertools
import importlib

from datetime import datetime
from datetime import timedelta

install_dir = f'{os.path.dirname(os.path.abspath(os.path.realpath(__file__)))}/'

logs_dir = './logs/'
gen_dir  = './gen/'
app_dir  = './app/'

nl = '\n'
hr = '-' * 50

sys.path.append(app_dir)
sys.path.append(f'{install_dir}test/app/')

import macros, utility, module_settings

# -- start: import custom modules

glossary          = module_settings.use_glossary
default_modules   = module_settings.use_default_modules
local_modules     = module_settings.use_local_modules

apply_modules     = {}
apply_glossary    = {}

if glossary:
  # imports glossary from {app_dir}
  apply_glossary[glossary] = importlib.import_module(glossary)

for dm in default_modules:
  if dm:
    # imports modules from {install_dir}test/app/
    apply_modules[dm] = importlib.import_module(dm)

for lm in local_modules:
  if lm:
    # imports modules from {app_dir}
    apply_modules[lm] = importlib.import_module(lm)

# -- end: import custom modules


def get_all_files(dir):
  """Returns a list of all files in given directory (dir)"""
  flist = []
  for root, dirs, files in os.walk(dir):
    for filename in files:
      if not filename.startswith('.'):
        flist.append(os.path.relpath(os.path.join(root, filename), dir))
  return flist


def analyze_files(logs_dir, list_files=False):
  """Finds all log files in logs directory (logs_dir) & performs analysis of validity of their names & location"""
  output = []

  head_text = f'Analyzing logs from directory {logs_dir}:'

  # first_line_len = len(head_text)
  output += [hr] # [0:first_line_len]]
  output += [f'{head_text}']

  all_files = get_all_files(logs_dir)

  if all_files:

    flist = []
    for file in all_files:

      # Acceptable date formats (ISO 8601)
      # yyyy/mm/dd<custom>.txt
      # yyyy-mm-dd<custom>.txt

      valid = False
      custom = False
      custom_text = ''
      ymd = False

      # e.g. 2024/01/01abc.txt
      match = re.match(r'^\d{4}/\d{2}/\d{2}(.+)\.txt$', file)
      if match is not None:
        valid = True
        custom = True
        custom_text = match.group(1)
      # e.g. 2024/01/01.txt
      elif re.match(r'^\d{4}/\d{2}/\d{2}\.txt$', file) is not None:
        valid = True
      else:
        # e.g. 2024/01/2024-01-01abc.txt
        match = re.match(r'^\d{4}/\d{2}/\d{4}-\d{2}-\d{2}(.+)\.txt$', file)
        if match is not None:
          valid = True
          ymd = True
          custom = True
          custom_text = match.group(1)
        # 2024/2024-01-01abc.txt
        else:
          match = re.match(r'^\d{4}/\d{4}-\d{2}-\d{2}(.+)\.txt$', file)
          if match is not None:
            valid = True
            ymd = True
            custom = True
            custom_text = match.group(1)
          else:
            valid = False
        # todo: ../logs/2024-01-01.txt

      flist.append({
        'file'        : file,
        'valid'       : valid,
        'custom'      : custom,
        'custom_text' : custom_text,
        'ymd'         : ymd
      })

    #for fd in flist:
    #  print(fd)

    valid_count   = sum(1 for d in flist if d.get('valid') == True)
    custom_count  = sum(1 for d in flist if d.get('custom') == True)
    ymd_count     = sum(1 for d in flist if d.get('ymd') == True)
    invalid_count = sum(1 for d in flist if d.get('valid') == False)

    output += [f'{nl}Analysis:']
    output += [f'- {str(len(flist))} total files found.']
    output += [f"- {valid_count} valid log files{(', including ' + str(custom_count) +' with custom names.' if custom_count else '.')}"]
    output += [f'- {ymd_count} log files in valid Y-m-d format.' if ymd_count else '']
    output += [f'- {invalid_count} files with invalid log file names. These will be ignored.' if invalid_count else '']

    if list_files:

      valid_files   = [d for d in flist if d.get('valid') == True]
      custom_files  = [d for d in flist if d.get('custom') == True]
      ymd_files     = [d for d in flist if d.get('ymd') == True]
      invalid_files = [d for d in flist if d.get('valid') == False]

      output += [hr] # [0:first_line_len]]
      output += [f'Listing files:']

      output += [f'{nl}{valid_count} valid log files:']
      output += ['- ' + f'{nl}- '.join([d['file'] for d in valid_files if 'file' in d])]
      output += [f'{nl}{custom_count} of the valid log files have custom names:' if custom_count else '']
      output += ['- ' + f'{nl}- '.join([d['file'] for d in custom_files if 'file' in d]) if custom_count else '']
      output += [f'{nl}{ymd_count} log files in valid Y-m-d format:' if ymd_count else '']
      output += ['- ' + f'{nl}- '.join([d['file'] for d in ymd_files if 'file' in d]) if ymd_count else '']
      output += [f'{nl}{invalid_count} files with invalid log file names. These will be ignored:' if invalid_count else '']
      output += ['- ' + f'{nl}- '.join([d['file'] for d in invalid_files if 'file' in d]) if invalid_count else '']

    """
    years = [fname[:4] for fname in all_files]
    months = [fname[:7] for fname in all_files]

    unique_years = set(years)
    unique_months = set(months)

    output += [f'- {str(len(all_files))} total files found.']
    output += [f'Data spans {str(len(all_files))} total days across {str(len(unique_years))} years for a total of {str(len(unique_months))} months:']

    year_month_dict = {}
    for date in unique_months:
      year, month = date.split('/')
      year_month_dict.setdefault(year, []).append(month)

    for year, months in sorted(year_month_dict.items()):
      output += [f'- {year}: ' + ', '.join(sorted(months))]
    """

  # add last hr
  # last_line_len = len(output[-1])
  output += [hr] # [0:last_line_len]]


  # clean output & print if valid
  output = [l for l in output if l.strip() != '']
  output = nl.join(output)

  if list_files:
    pydoc.pager(output) if output else None
    return

  print(output) if output else None

def cap_macro(input):
  return macros.cap_description(input)

def time_macro(input):
  return macros.raw_time_to_excel_sum(input)

def escape_for_csv(input):
  """Prepares the given input for csv output"""
  # escape a double quote (") with additional double quote ("")
  value = input.replace('"', '""')
  value = '"' + value + '"'
  return value

def try_float(v, defval=None):
  try:
    return float(v)
  except Exception:
    return defval

def csvtext(csv_list):
  """Converts csv list to string/plain text"""
  return nl.join(','.join(ln) for ln in csv_list)

def modify_csv(csv_list, add_header=True, add_footer=True):
  """Modifies csv content by adding headers & footers"""
  # headers & footers

  if add_header:
    csv_list.insert(0, ['Date','Hours','Human','Raw Times','Description'])

  if add_footer:
    total_hours = round(sum(try_float(col[1], 0) for col in csv_list), 2)
    csv_list.append(['', str(total_hours), macros.hours_to_human(total_hours), '', 'Total Logged Hours'])

  return csv_list


def convert_to_csv(entries, ymd_date):
  """Receives the contents of a log txt file (entries) with date (ymd_date) and returns a generated csv content string"""

  dateobj = datetime.strptime(ymd_date, "%Y-%m-%d")
  datefrm = dateobj.strftime("%m/%d/%Y")

  lines = entries.splitlines()
  parsed_lines = []

  for line in lines:

    # parse individual entries
    # group 1: time intervals (e.g. 7a|7am|7:30a|3.21s|5m|1.5h|30m|1:30h etc...)
    # group 2: description text

    # regex101 (ryt) v2: https://regex101.com/r/lrm5IQ/2

    pattern = r'^-(\s*(?:[\d\:\.]+(?:m|h|s|am|pm|a|p)[\s\,]*[\s\;]*)+)(.*)$'
    match = re.search(pattern, line)
    newline = []

    if match:

      rawtime = match.group(1)
      rawdesc = match.group(2)

      newtime = rawtime
      newdesc = rawdesc

      # 1. apply module functions & macros to description

      if apply_modules:
        for name in apply_modules.keys():
          newdesc = apply_modules[name].apply(newdesc, apply_glossary[glossary])

      # 2. apply default macros

      newtime = time_macro(newtime)
      newdesc = str(newtime[2]) + cap_macro(newdesc)


      #           Date     Hours       Human                              Raw Times                   Description
      newline = [datefrm, newtime[1], macros.hours_to_human(newtime[1]), escape_for_csv(newtime[0]), escape_for_csv(newdesc)]
      # newline = match.group(1) + ',' + match.group(2)
    
    if newline:

      parsed_lines.append(newline)
  
  # endfor

  return parsed_lines


def main():
  # Start parsing arguments
  output = []
  if len(sys.argv) > 1:
    if sys.argv[1]:
      arg1 = sys.argv[1]

      today = datetime.today()
      today_date = today.strftime('%Y-%m-%d')
      today_dfil = today.strftime('%Y/%m/%d')

      yesterday = today - timedelta(days = 1)
      yesterday_date = yesterday.strftime('%Y-%m-%d')
      yesterday_dfil = yesterday.strftime('%Y/%m/%d')

      if arg1 in ('today','-t','yesterday','-y'):

        if arg1 in ('today','-t'):
          day_name, day_date, day_dfil = 'today', today_date, today_dfil

        if arg1 in ('yesterday','-y'):
          day_name, day_date, day_dfil = 'yesterday', yesterday_date, yesterday_dfil

        head_text = f'Analyzing data for {day_name}, {day_date}:'

        # first_line_len = len(head_text)
        output += [hr] # [0:first_line_len]]
        output += [f'{head_text}']

        # look for files
        output += [f'- Looking for {day_dfil}.txt in {logs_dir}']
        output += [f'- Looking for {day_dfil}{{custom}}.txt in {logs_dir}']
        output += [f'- Looking for {day_date}.txt in {logs_dir}']
        output += [f'- Looking for {day_date}{{custom}}.txt in {logs_dir}']

        # last_line_len = len(output[-1])
        output += [hr] # [0:last_line_len]]

      elif arg1 in ('gencsv','-g'):

        if len(sys.argv) > 2:
          arg2  = sys.argv[2] # date or keyword

          # d = macros.parse_date_input(arg2)
          # exit()

          rname = arg2.replace('/','-')  # YYYY-MM-DD
          fname = rname.replace('-','/') # YYYY/MM/DD

          if fname in ('today', '/t'):
            rname = today_date
            fname = today_dfil
          elif fname in ('yesterday', '/y'):
            rname = yesterday_date
            fname = yesterday_dfil

          # -- look for single log files (date)

          filename = f'{logs_dir}{fname}.txt'

          if os.path.exists(filename):

            # convert individual log txt file
            with open(filename, 'r') as file:
              entries = file.read()
            entries = csvtext(modify_csv(convert_to_csv(entries, rname), add_header=True, add_footer=True))

            # generate individual log csv file
            genfile = f'{gen_dir}{rname}.csv'
            with open(genfile, 'w') as file:
              file.write(entries)
            output += [f'Generated CSV file {genfile} successfully.']


          # -- look for collections of log files (month, year)

          elif re.search(r'^\d{4}(?:\/\d{2})?$', fname):

            lenfn = len(fname)

            if lenfn == 4:
              output += [f'Mock-generating CSV file for ({fname}) year collections.']

            elif lenfn == 7:
              month_collection = []
              collcount = 0
              for d in range(1,32):
                d = str(d).zfill(2)
                filename = f'{logs_dir}{fname}/{d}.txt'
                if os.path.exists(filename):

                  # convert each individual log txt file
                  with open(filename, 'r') as file:
                    entries = file.read()
                  entries = convert_to_csv(entries, f'{rname}-{d}')
                  month_collection.append(entries)
                  collcount += 1

              output += [f'Found {collcount} daily log file(s) for ({fname}) month collection.']

              # combine all the lists into one list
              month_collection = list(itertools.chain(*month_collection))

              # add header & footer calculations
              month_collection = modify_csv(month_collection, add_header=True, add_footer=True)

              # generate collection log csv file
              genfile = f'{gen_dir}{rname}.csv'
              with open(genfile, 'w') as file:
                file.write(csvtext(month_collection))
              output += [f'Generated month collection CSV file {genfile} successfully.']
              # pydoc.pager(month_collection)


          else:
            output += [f'Log file {filename} does not exist.']

        else:
          output += [f'Please specify a valid date (Y-m-d), month (Y-m), or year (Y).']

      elif arg1 in ('stats','-s'):
        analyze_files(logs_dir)

      elif arg1 in ('list-files','-l'):
        analyze_files(logs_dir, True)

      elif arg1 in ('utility','u'):
        utility.utility(sys.argv[2:], arg1)


      # help & manual

      elif arg1 in ('--version','-v'):
        output += [f'Activity Metrics, Version {v}']
        output += [c]

      # prints the help manual

      elif arg1 in ('--help','-h','help'):
        output += [man.strip() + f'{nl}']

      # pages the help manual instead of printing

      elif arg1 == 'man':
        output += [man.strip() + f'{nl}']
        pydoc.pager(nl.join(output))
        return


      else:
        output += [f"Invalid command '{arg1}'. Use 'man' or 'help' for proper usage."]

  else:
    # run 'stats' by default
    analyze_files(logs_dir)

  print(nl.join(output)) if output else None

if __name__ == '__main__':
  main()

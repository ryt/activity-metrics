#!/usr/bin/env python3

# Activity Metrics (acme)
# Copyright (C) 2024 Ray Mentose. 
# Latest source can be found at: https://github.com/ryt/activity-metrics.git

import sys
import os
import re
import subprocess
import pydoc
import itertools
import importlib

from datetime import datetime
from datetime import timedelta

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


def printx(text, meta = {}):

  if 'error_code' not in meta:
    print("Please specify the following for arument 2 for printx: { 'error_code' : 'error_code_name' } ")

  else:
    print(text)

  exit()


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

def modify_csv(csv_list, add_header=True, add_footer=True, module_options=False):
  """Modifies csv content by adding headers, footers, & columns"""

  # headers & footers

  if add_header:
    #                     0        1         2             3        4
    csv_list.insert(0, ['Date','Duration','Description', 'Hours', 'Splits'])

  if add_footer:
    total_hours = round(sum(try_float(col[3], 0) for col in csv_list), 2)
    #                 0   1                                   2                     3                 4
    csv_list.append(['', macros.hours_to_human(total_hours, True), 'Total Logged Hours', str(total_hours), ''])

  # module options: if used, it requires the module to have a function named 'options'

  if apply_modules and module_options:
    mo_list = module_options.split(',')
    for opt in mo_list:
      opt_spl = opt.split('.') # e.g. module_math.multiply -> [0] module_math, [1] multiply
      for name in apply_modules.keys():
        if opt_spl[0] == name:
          csv_list = apply_modules[name].options(csv_list, meta={
              'module_options'  : module_options,
              'option'          : opt,
              'add_header'      : add_header,
              'add_footer'      : add_footer,
            })

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
    # feature update 1/21/2025: dots (.) can be used to start entries along with hyphens (-)

    pattern = r'^[-\.](\s*(?:[\d\:\.]+(?:m|h|s)[\s\,]*[\s\;]*)+)(.*)$'
    match = re.search(pattern, line)
    newline = []

    if match:

      rawtime = match.group(1)
      rawdesc = match.group(2)

      newtime = rawtime
      newdesc = rawdesc

      # -- 1. apply module functions & macros to description

      if apply_modules:
        for name in apply_modules.keys():
          newdesc = apply_modules[name].apply(newdesc, apply_glossary[glossary])

      # -- 2. apply default macros

      newtime = time_macro(newtime)
      newdesc = cap_macro(newdesc)

      #           0: Date    1: Duration                               2: Description            3: Hours       4: Splits
      newline = [datefrm,   macros.hours_to_human(newtime[1], True),   escape_for_csv(newdesc),   newtime[1],   escape_for_csv(newtime[0]) ]
    
    if newline:

      parsed_lines.append(newline)
  
  # endfor

  return parsed_lines


"""
List of parameters handled by analyze->params:

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

def analyze(params, called, meta):

  ## -- start: global headers & settings

  global install_dir, logs_dir, gen_dir, app_dir, nl, hr
  global glossary, default_modules, local_modules, apply_modules, apply_glossary
  global macros, utility, module_settings

  install_dir = f'{os.path.dirname(os.path.abspath(os.path.realpath(__file__)))}/'

  logs_dir = meta['logs_dir']
  gen_dir  = meta['gen_dir']
  app_dir  = meta['app_dir']

  nl = '\n'
  hr = '-' * 50

  sys.path.append(app_dir)
  sys.path.append(f'{install_dir}usr/app/')

  import macros, utility, module_settings

  # -- start: import custom modules

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
      # imports modules from {install_dir}usr/app/
      apply_modules[dm] = importlib.import_module(dm)

  # -- end: import custom modules

  ## -- end: global headers & settings

  output = []

  if len(params) == 0:

    # run 'stats' by default

    analyze_files(logs_dir)


  # -- start: parsing arguments

  else:

    if params[0]:
      arg1 = params[0]

      # -- start: acme {date_input}

      if macros.is_date_input(arg1):

        parsed       = macros.parse_date_input(arg1)
        parsed_slash = parsed['res_ymd_slash']
        parsed_dash  = parsed['res_ymd_dash']
        parsed_log   = parsed['res_ymd_log']
        parsed_name  = parsed['res_key_name']
        parsed_each  = parsed['res_each']

        head_text = f"Analyzing data for {parsed_name + ', ' if parsed_name else ''}{parsed_dash}:"

        # first_line_len = len(head_text)

        output += [hr] # [0:first_line_len]]
        output += [f'{head_text}']

        # look for files
        output += [f'- Looking for {parsed_slash}.txt in {logs_dir}']
        output += [f'- Looking for {parsed_slash}{{custom}}.txt in {logs_dir}']
        output += [f'- Looking for {parsed_dash}.txt in {logs_dir}']
        output += [f'- Looking for {parsed_dash}{{custom}}.txt in {logs_dir}']

        # last_line_len = len(output[-1])
        output += [hr] # [0:last_line_len]]

      # -- end: acme {date_input}

      # -- start: acme gencsv {date_input}

      elif arg1 in ('gencsv','-g'):

        if len(params) > 1:
          arg2 = params[1] # date or keyword

          module_options = params[2] if len(params) > 2 else False

          # Section: Intervals
          #   Commas can be used in the {date_input} to specify interval 'from' and 'to' dates, along with an additional 'separator' text for the filename.
          #   Intervals can be used as follows:
          #
          #       gencsv   {interval_from},{interval_to}
          #       gencsv   {interval_from},{interval_to},{interval_seperator}
          #
          #   If commas are detected, the interval parameters will be parsed before everything else.

          valid_interval_input = False

          # -- start: parse intervals (if they're present)

          if ',' in arg2:

            interval_parts  = arg2.split(',')
            interval_length = len(interval_parts)

            interval_from       = ''
            interval_to         = ''
            interval_seperator  = '_'

            invalid_interval_code = { 'error_code' : 'analyze.gencsv.invalid_interval' }
            invalid_interval_text = nl.join([
              'Please enter valid intervals in the following formats: {from},{to} or {from},{to},{separator}.',
              'Valid examples:  1/1,1/7   1/1,1/7,-to-   1-15,1-30   2024-01-15,01-30,_   01/01,01/07,_through_'
            ])

            if interval_length > 1:
              interval_from = interval_parts[0]
              interval_to   = interval_parts[1]

            if interval_length == 3:
              interval_seperator = ''.join(i for i in interval_parts[2] if i not in '/:*?<>|#') # 12/26/24 note: potential syntax warning/error in '\/:*?<>|#'

            if interval_length == 0 or interval_length > 3:
              printx(invalid_interval_text, invalid_interval_code)

            parsed_interval_from = macros.parse_date_input(interval_from)
            parsed_interval_to   = macros.parse_date_input(interval_to)

            if not parsed_interval_from['res_ymd_dash'] or not parsed_interval_to['res_ymd_dash']:
              printx(invalid_interval_text, invalid_interval_code)

            valid_interval_input = True

          # -- end: parse intervals


          parsed = macros.parse_date_input(arg2)
          parsed_slash = parsed['res_ymd_slash']
          parsed_dash  = parsed['res_ymd_dash']

          # -- look for single log files (date)

          filename = f'{logs_dir}{parsed_slash}.txt'

          if not valid_interval_input and os.path.exists(filename):

            # convert individual log txt file
            with open(filename, 'r') as file:
              entries = file.read()
            entries = csvtext(
              modify_csv(
                convert_to_csv(entries, parsed_dash), 
                add_header=True, 
                add_footer=True,
                module_options=module_options,
              )
            )

            # generate individual log csv file
            genfile = f'{gen_dir}{parsed_dash}.csv'
            with open(genfile, 'w') as file:
              file.write(entries)
            output += [f'Generated CSV file {genfile} successfully.']


          # -- start: look for collections of log files (month, year)

          elif not valid_interval_input and re.search(r'^\d{4}(?:\/\d{2})?$', parsed_slash):

            lenfn = len(parsed_slash)

            # -- generate year collections -- #

            if lenfn == 4:
              year_collection = []
              collcount = 0

              for m in range(1, 13):
                m = str(m).zfill(2)
                for d in range(1,32):
                  d = str(d).zfill(2)
                  filename = f'{logs_dir}{parsed_slash}/{m}/{d}.txt'
                  if os.path.exists(filename):

                    # convert each individual log txt file
                    with open(filename, 'r') as file:
                      entries = file.read()
                      # print(f'{parsed_dash}-{m}-{d}')
                    entries = convert_to_csv(entries, f'{parsed_dash}-{m}-{d}')
                    year_collection.append(entries)
                    collcount += 1

              output += [f'Found {collcount} daily log file(s) for ({parsed_slash}) year collection.']

              # combine all the lists into one list
              year_collection = list(itertools.chain(*year_collection))

              # add modifications: header & footer calculations, categorize
              year_collection = modify_csv(
                year_collection, 
                add_header=True, 
                add_footer=True,
                module_options=module_options,
              )

              # generate collection log csv file
              genfile = f'{gen_dir}{parsed_dash}.csv'
              with open(genfile, 'w') as file:
                file.write(csvtext(year_collection))
              output += [f'Generated year collection CSV file {genfile} successfully.']
              # pydoc.pager(year_collection)


            # -- generate month collections -- #

            elif lenfn == 7:
              month_collection = []
              collcount = 0
              for d in range(1,32):
                d = str(d).zfill(2)
                filename = f'{logs_dir}{parsed_slash}/{d}.txt'
                if os.path.exists(filename):

                  # convert each individual log txt file
                  with open(filename, 'r') as file:
                    entries = file.read()
                  entries = convert_to_csv(entries, f'{parsed_dash}-{d}')
                  month_collection.append(entries)
                  collcount += 1

              output += [f'Found {collcount} daily log file(s) for ({parsed_slash}) month collection.']

              # combine all the lists into one list
              month_collection = list(itertools.chain(*month_collection))

              # add modifications: header & footer calculations, categorize
              month_collection = modify_csv(
                month_collection, 
                add_header=True, 
                add_footer=True,
                module_options=module_options,
              )

              # generate collection log csv file
              genfile = f'{gen_dir}{parsed_dash}.csv'
              with open(genfile, 'w') as file:
                file.write(csvtext(month_collection))
              output += [f'Generated month collection CSV file {genfile} successfully.']
              # pydoc.pager(month_collection)

          # -- end: look for collections

          # -- start: process intervals

          elif valid_interval_input:

            pif = parsed_interval_from
            pit = parsed_interval_to

            pif_ymd_dash = pif['res_ymd_dash']
            pit_ymd_dash = pit['res_ymd_dash']

            pif_Y = pif['res_each']['Y']
            pit_Y = pit['res_each']['Y']
            pit_M = pit['res_each']['M']
            pit_D = pit['res_each']['D']

            to_format = f'{pit_M}-{pit_D}' if pif_Y == pit_Y else pit_ymd_dash # option for: _01-01 instead of _2024-01-01
            genfile   = f'{pif_ymd_dash}{interval_seperator}{to_format}.csv'

            output += [f'Creating a collection for intervals from {pif_ymd_dash} to {pit_ymd_dash}:']
            output += ['...']
            
            # todo: parse interval logs
            # todo: generate interval collection csv {genfile}

            output += [f'Mock-generated CSV file {genfile} successfully.']

          # -- end: process intervals

          else:
            output += [f'Log file {filename} does not exist.']

        else:
          output += [f'Please specify a valid date (Y-m-d), month (Y-m), or year (Y).']

      # -- end: acme gencsv {date_input}

      elif arg1 in ('stats','-s'):
        analyze_files(logs_dir)

      elif arg1 in ('list-files','-l'):
        analyze_files(logs_dir, True)

      elif arg1 in ('utility','util'):
        utility.utility(params[1:], arg1, meta)


      # help & manual

      elif arg1 in ('--version','-v'):
        output += [f"Activity Metrics, Version {meta['version']}"]
        output += [meta['copyright']]

      # prints the help manual

      elif arg1 in ('--help','-h','help'):
        output += [meta['manual'].strip() + f'{nl}']

      # pages the help manual instead of printing

      elif arg1 == 'man':
        output += [meta['manual'].strip() + f'{nl}']
        pydoc.pager(nl.join(output))
        return


      else:
        output += [f"Invalid command '{arg1}'. Use 'man' or 'help' for proper usage."]

  
  # -- end: parsing arguments

  print(nl.join(output)) if output else None


def main():
  print("Please use the 'acme' command to run analyze.")

if __name__ == '__main__':
  main()

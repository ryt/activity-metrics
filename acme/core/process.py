#!/usr/bin/env python3

# activity metrics (acme)
# latest source & documentation at: https://github.com/ryt/activity-metrics.git

import sys
import os
import re
import pydoc
import subprocess
import itertools
import importlib

from datetime import datetime
from datetime import timedelta

from acme.core import utils
from acme.core import macros
from acme.core import validate


def printx(text, meta = {}):

  if 'error_code' not in meta:
    print("Please specify the following for arument 2 for printx: { 'error_code' : 'error_code_name' } ")

  else:
    print(text)

  exit()


def modify_csv(csv_list, add_header=True, add_footer=True, module_options=False, apply_modules=None):
  """Modifies csv content by adding headers, footers, & columns"""

  # headers & footers

  if add_header:
    #                     0        1         2             3        4
    csv_list.insert(0, ['Date','Duration','Description', 'Hours', 'Splits'])

  if add_footer:
    total_hours = round(sum(macros.try_float(col[3], 0) for col in csv_list), 2)
    #                 0   1                                   2                     3                 4
    csv_list.append(['', macros.hours_to_human(total_hours, True), 'Total Logged Hours', str(total_hours), ''])

  # module options  : if used, it requires the module to have a function named 'options'
  # module NICKNAME : if a NICKNAME var is set on a module, it can also be used to call the module

  if apply_modules and module_options:
    mo_list = module_options.split(',')
    for opt in mo_list:
      opt_spl = opt.split('.') # e.g. module_math.multiply -> [0] module_math, [1] multiply
      for name in apply_modules.keys():
        mod_nickname = getattr(apply_modules[name], 'NICKNAME', None)
        if opt_spl[0] == name or opt_spl[0] == mod_nickname:
          if opt_spl[0] == mod_nickname:
            module_options = module_options.replace(mod_nickname, name)
            opt = name
          csv_list = apply_modules[name].options(csv_list, meta={
            'module_options'  : module_options,
            'option'          : opt,
            'add_header'      : add_header,
            'add_footer'      : add_footer,
          })

  return csv_list


def convert_to_csv(entries, ymd_date, customize=None):
  """Receives the contents of a log txt file (entries) with date (ymd_date) and returns a generated csv content string"""

  apply_modules  = customize.apply_modules if hasattr(customize, 'apply_modules') else None
  apply_glossary = customize.apply_glossary if hasattr(customize, 'apply_glossary') else None
  glossary = customize.glossary if hasattr(customize, 'glossary') else None

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

      newtime = macros.raw_time_to_excel_sum(newtime)
      newdesc = macros.cap_description(newdesc)
                                        
      newline = [
        datefrm,                                  # 0: Date 
        macros.hours_to_human(newtime[1], True),  # 1: Duration 
        macros.escape_for_csv(newdesc),           # 2: Description  
        newtime[1],                               # 3: Hours 
        macros.escape_for_csv(newtime[0])         # 4: Splits
      ]
    
    if newline:

      parsed_lines.append(newline)
  
  # endfor

  return parsed_lines


def generate_collections(period='year', output=[], logs_dir=None, parsed_slash=None, parsed_dash=None, module_options=None):
  # -- generate collection csvs for periods: year, month -- #

  if not logs_dir or not parsed_slash or not parsed_dash:
    output += ['One of the following values is invalid: logs_dir, parsed_slash, parsed_dash.']
    return output

  # -- start process -- #

  is_month = True if period == 'month' else False

  period_collection = []
  collcount = 0

  range_end = 13

  if is_month:
    range_end = 2 # <- if month: range(1,2) <- runs once

  for m in range(1, range_end):
    m = str(m).zfill(2)
    for d in range(1,32):
      d = str(d).zfill(2)
      if is_month:
        filename = f'{logs_dir}{parsed_slash}/{d}.txt'
      else:
        filename = f'{logs_dir}{parsed_slash}/{m}/{d}.txt'
      if os.path.exists(filename):

        # convert each individual log txt file
        with open(filename, 'r') as file:
          entries = file.read()
          # print(f'{parsed_dash}-{m}-{d}')
        if is_month:
          entries = convert_to_csv(entries, f'{parsed_dash}-{d}')
        else:
          entries = convert_to_csv(entries, f'{parsed_dash}-{m}-{d}')
        period_collection.append(entries)
        collcount += 1

  output += [f'Found {collcount} daily log file(s) for ({parsed_slash}) {period} collection.']

  # combine all the lists into one list
  period_collection = list(itertools.chain(*period_collection))

  # add modifications: header & footer calculations, categorize
  period_collection = modify_csv(
    period_collection,
    add_header=True,
    add_footer=True,
    module_options=module_options,
  )

  # write collection csv file
  genfile = f'{gen_dir}{parsed_dash}.csv'
  utils.write_to_file(genfile, csvtext(period_collection))

  output += [f'Generated {period} collection CSV file {genfile} successfully.']
  # pydoc.pager(period_collection)

  return output


def main():
  print("Please use the 'acme' command to process logs.")


if __name__ == '__main__':
  main()

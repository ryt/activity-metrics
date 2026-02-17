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
from types import SimpleNamespace

from acme.core import utils
from acme.core import macros
from acme.core import validate

def handle_date_input(parsed, meta):
  """Handle basic date inputs: acme {date_input}"""

  head_text = f"Analyzing data for {parsed.key_name + ', ' if parsed.key_name else ''}{parsed.ymd_dash}:"

  # first_line_len = len(head_text)
  output  = []
  output += ['----'] # [0:first_line_len]]
  output += [f'{head_text}']

  # look for files
  output += [f'- Looking for {parsed.ymd_slash}.txt in {meta.logs_dir}']
  output += [f'- Looking for {parsed.ymd_slash}{{custom}}.txt in {meta.logs_dir}']
  output += [f'- Looking for {parsed.ymd_dash}.txt in {meta.logs_dir}']
  output += [f'- Looking for {parsed.ymd_dash}{{custom}}.txt in {meta.logs_dir}']

  # last_line_len = len(output[-1])
  output += ['----'] # [0:last_line_len]]

  return output


def import_apply_custom_modules(params, callname, meta):
  """Import custom modules & prep apply vars & glossary"""

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

  return SimpleNamespace(
    apply_modules=apply_modules,
    apply_glossary=apply_glossary,
    glossary=glossary,
  )


def handle_gencsv(params, callname, meta):
  """Handle gencsv inputs: acme (gencsv|-g) {date_input}"""

  output = []

  if len(params) < 2:
    output += [f'Please specify a valid date (Y-m-d), month (Y-m), or year (Y).']
    return output

  # -- start gencsv handler -- #

  arg2 = params[1] # {date_input}: date or keyword

  module_options = params[2] if len(params) > 2 else False

  valid_interval_input = macros.check_is_valid_interval(arg2)
  parsed = macros.parse_date_input(arg2)

  filename = f'{meta.logs_dir}{parsed.ymd_slash}.txt' # look for single log files (date)

  # -- section 1: handle gencsv for single dates (e.g. acme gencsv {date_input}) & ensure it's is not an interval -- #
  if os.path.exists(filename) and not valid_interval_input:
    # prep custom modules & glossary
    customize = import_apply_custom_modules(params, callname, meta)

    # convert individual log txt file
    with open(filename, 'r') as file:
      entries = file.read()

    entries = macros.csvtext(
      modify_csv(
        convert_to_csv(entries, parsed.ymd_dash, customize=customize), 
        add_header=True, 
        add_footer=True,
        module_options=module_options,
        customize=customize,
      )
    )

    # generate individual log csv file
    genfile = f'{meta.gen_dir}{parsed.ymd_dash}.csv'
    utils.write_to_file(genfile, entries)
    output += [f'Generated CSV file {genfile} successfully.']


  # -- section 2: look for collections of log files (month, year) -- #
  elif re.search(r'^\d{4}(?:\/\d{2})?$', parsed.ymd_slash) and not valid_interval_input:
    # prep custom modules & glossary
    customize = import_apply_custom_modules(params, callname, meta)
    lenfn = len(parsed.ymd_slash)

    # year collections
    if lenfn == 4:
      output += generate_collections('year', meta, parsed, module_options, customize)

    # month collections
    elif lenfn == 7:
      output += generate_collections('month', meta, parsed, module_options, customize)


  # -- section 3: process intervals (e.g. acme gencsv 2025-01-05,2025-01-10 etc.) -- #
  elif valid_interval_input:
    # Section 3: Intervals
    #   Commas can be used in the {date_input} to specify interval 'from' and 'to' dates,
    #   along with an additional 'separator' text for the filename.
    #   Intervals can be used as follows:
    #
    #       gencsv   {interval_from},{interval_to}
    #       gencsv   {interval_from},{interval_to},{interval_seperator}
    #
    #   If commas are detected, the interval parameters will be parsed before everything else.

    pif = valid_interval_input.parsed_interval_from
    pit = valid_interval_input.parsed_interval_to

    pif_ymd_dash = pif.ymd_dash
    pit_ymd_dash = pit.ymd_dash

    pif_Y = pif.each['Y']
    pit_Y = pit.each['Y']
    pit_M = pit.each['M']
    pit_D = pit.each['D']

    to_format = f'{pit_M}-{pit_D}' if pif_Y == pit_Y else pit_ymd_dash # option for: _01-01 instead of _2024-01-01
    genfile   = f'{pif_ymd_dash}{valid_interval_input.interval_seperator}{to_format}.csv'

    output += [f'Creating a collection for intervals from {pif_ymd_dash} to {pit_ymd_dash}:']
    output += ['...']
    
    # todo: parse interval logs
    # todo: generate interval collection csv {genfile}

    output += [f'Mock-generated CSV file {genfile} successfully.']


  # -- section 4: no valid log file -- #
  else:
    filename = filename if parsed.ymd_slash else f'{meta.logs_dir}{arg2}.txt'
    output += [f'Log file {filename} does not exist.']


  return output


def modify_csv(csv_list, add_header=True, add_footer=True, module_options=False, customize=None):
  """Modifies csv content by adding headers, footers, & columns"""
  apply_modules  = customize.apply_modules if hasattr(customize, 'apply_modules') else None

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


def generate_collections(period='year', meta=None, parsed=None, module_options=None, customize=None):
  # -- generate collection csvs for periods: year, month -- #

  output = []

  if not meta.logs_dir or not parsed.ymd_slash or not parsed.ymd_dash:
    output += ['One of the following values is invalid: logs_dir, parsed.ymd_slash, parsed.ymd_dash.']
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
        filename = f'{meta.logs_dir}{parsed.ymd_slash}/{d}.txt'
      else:
        filename = f'{meta.logs_dir}{parsed.ymd_slash}/{m}/{d}.txt'
      if os.path.exists(filename):

        # convert each individual log txt file
        with open(filename, 'r') as file:
          entries = file.read()
          # print(f'{parsed.ymd_dash}-{m}-{d}')
        if is_month:
          entries = convert_to_csv(entries, f'{parsed.ymd_dash}-{d}', customize=customize)
        else:
          entries = convert_to_csv(entries, f'{parsed.ymd_dash}-{m}-{d}', customize=customize)
        period_collection.append(entries)
        collcount += 1

  output += [f'Found {collcount} daily log file(s) for ({parsed.ymd_slash}) {period} collection.']

  # combine all the lists into one list
  period_collection = list(itertools.chain(*period_collection))

  # add modifications: header & footer calculations, categorize
  period_collection = modify_csv(
    period_collection,
    add_header=True,
    add_footer=True,
    module_options=module_options,
    customize=customize,
  )
  '''
  entries = macros.csvtext(
    modify_csv(
      convert_to_csv(
        entries, 
        parsed.ymd_dash, 
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
  '''
  # write collection csv file
  genfile = f'{meta.gen_dir}{parsed.ymd_dash}.csv'
  utils.write_to_file(genfile, macros.csvtext(period_collection))

  output += [f'Generated {period} collection CSV file {genfile} successfully.']
  # pydoc.pager(period_collection)

  return output


def main():
  print("Please use the 'acme' command to process logs.")


if __name__ == '__main__':
  main()

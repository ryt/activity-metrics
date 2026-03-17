"""Process Handlers and Module Callers"""

import os
import re
import itertools

from tabulate import tabulate

from acme.core import utils
from acme.core import macros

from acme.modules import timesheets
from acme.core.settings import Settings

settings = Settings.settings

def handle_date_input(parsed, meta):
  """
  Handle basic date inputs: acme {date_input}
  Display [table] converted logs for {date_input} if available.
  """
  output = []
  header = f"Timesheet logs for {parsed.key_name + ', ' if parsed.key_name else ''}{parsed.ymd_dash}:"
  output += [f'{header}']
  show_files_list = [
    f'{meta.logs_dir}/{parsed.ymd_slash}.txt',
    f'{meta.logs_dir}/{parsed.ymd_dash}.txt',
  ]
  max_col = 30
  for show_file in show_files_list:
    if os.path.isfile(show_file):
      with open(show_file, 'r') as file:
        show_file_csv = timesheets.convert_to_csv(file.read(), parsed.ymd_dash)
        trimmed_csv = [
          [
            (s[:max_col] + '...' if len(s) > max_col else s) for s in sublist
          ] for sublist in show_file_csv
        ]
        table_csv = tabulate(
          trimmed_csv,
          tablefmt='simple',
          maxcolwidths=max_col+3
        )
        output += [table_csv]

  return output


def handle_timesheets(params, callname, meta):
  """Handle gencsv/timesheets inputs: acme (gencsv|-g) {date_input}"""
  output = []

  if len(params) < 2:
    output += [f'Please specify a valid date (Y-m-d), month (Y-m), or year (Y).']
    return output

  date_input      = params[1] # date or keyword
  module_options  = params[2] if len(params) > 2 else False

  valid_interval_input = macros.check_is_valid_interval(date_input)
  parsed = macros.parse_date_input(date_input)

  filename = f'{meta.logs_dir}{parsed.ymd_slash}.txt' # look for single log files (date)

  if module_options in (timesheets.timesheets_categorize.NICKNAME, timesheets.timesheets_categorize.NAME):
    customize = timesheets.Customize(
      apply_to_each_entry=('categorize','capitalize'),
      apply_to_final_csv=('add_columns',)
    )
  else:
    customize = timesheets.Customize(
      apply_to_each_entry=('capitalize',)
    )

  # -- case 1: -- #
  # - handle gencsv for single dates (e.g. acme gencsv {date_input}) #
  # - ensure {date_input} is not an interval #
  if os.path.exists(filename) and not valid_interval_input:

    # convert individual log txt file
    with open(filename, 'r') as file:
      entries = file.read()

    entries = macros.csvtext(timesheets.convert_to_csv(
      entries,
      ymd_date=parsed.ymd_dash,
      customize=customize
    ))

    # generate individual log csv file
    genfile = f'{meta.gen_dir}{parsed.ymd_dash}.csv'
    utils.write_to_file(genfile, entries)
    output += [f'Generated CSV file {genfile} successfully.']


  # -- case 2: look for collections of log files (month, year) -- #
  elif re.search(r'^\d{4}(?:\/\d{2})?$', parsed.ymd_slash) and not valid_interval_input:
    # prep custom modules & glossary
    lenfn = len(parsed.ymd_slash)

    # year collections
    if lenfn == 4:
      output += generate_collections('year', meta, parsed, customize)

    # month collections
    elif lenfn == 7:
      output += generate_collections('month', meta, parsed, customize)


  # -- case 3: process intervals (e.g. acme gencsv 2025-01-05,2025-01-10 etc.) -- #
  elif valid_interval_input:
    # Case 3: Intervals
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


  # -- case 4: no valid log file -- #
  else:
    filename = filename if parsed.ymd_slash else f'{meta.logs_dir}{date_input}.txt'
    output += [f'Log file {filename} does not exist.']


  return output



def generate_collections(period='year', meta=None, parsed=None, customize=None):
  """Generate collection csvs for periods: year, month."""
  output = []

  if not meta.logs_dir or not parsed.ymd_slash or not parsed.ymd_dash:
    output += ['One of the following values is invalid: logs_dir, parsed.ymd_slash, parsed.ymd_dash.']
    return output

  preCustomize = timesheets.Customize(
    apply_to_each_entry=('categorize','capitalize'),
    add_header=False,
    add_footer=False,
  )
  postCustomize = customize

  is_month = True if period == 'month' else False

  period_collection = []
  collcount = 0
  range_end = 2 if is_month else 13 # <- for month collections: range(1,2) <- ends at 2 instead of 13

  for m in range(1, range_end):
    m = str(m).zfill(2)
    for dateNum in range(1,32):
      dateNum = str(dateNum).zfill(2)

      if is_month:
        filename  = f'{meta.logs_dir}{parsed.ymd_slash}/{dateNum}.txt'
        entry_ymd = f'{parsed.ymd_dash}-{dateNum}'
      else:
        filename  = f'{meta.logs_dir}{parsed.ymd_slash}/{m}/{dateNum}.txt'
        entry_ymd = f'{parsed.ymd_dash}-{m}-{dateNum}'

      if not os.path.exists(filename):
        continue

      with open(filename, 'r') as file:
        entries = file.read()

      # convert each individual log txt file
      entries = timesheets.convert_to_csv(entries, entry_ymd, customize=preCustomize)
      period_collection.append(entries)
      collcount += 1

  output += [f'Found {collcount} daily log file(s) for ({parsed.ymd_slash}) {period} collection.']

  # combine all the lists into one list
  period_collection = list(itertools.chain(*period_collection))

  # add modifications: header & footer calculations, categorize
  period_collection = timesheets.modify_csv(period_collection, customize=postCustomize)

  # write collection csv file
  genfile = f'{meta.gen_dir}{parsed.ymd_dash}.csv'
  utils.write_to_file(genfile, macros.csvtext(period_collection))

  output += [f'Generated {period} collection CSV file {genfile} successfully.']

  return output


def main():
  print("Please use the 'acme' command to process logs.")


if __name__ == '__main__':
  main()

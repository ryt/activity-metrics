"""
Timesheets Module
Parses and converts formatted timesheets to csv.
"""

import re

from datetime import datetime

from acme.core import macros
from acme.modules import timesheets_categorize

class Customize:

  func_list = {
    'categorize':   timesheets_categorize.initialize,
    'capitalize':   macros.cap_description,
    'add_columns':  timesheets_categorize.finalize,
  }

  def __init__(
      self, 
      apply_to_each_entry = (), 
      apply_to_final_csv = (),
      add_header = True,
      add_footer = True,
    ):

    if not isinstance(apply_to_each_entry, tuple) or not isinstance(apply_to_final_csv, tuple):
      raise TypeError('Customize parameters must be tuples.')
    
    self.apply_to_each_entry = apply_to_each_entry
    self.apply_to_final_csv = apply_to_final_csv
    self.add_header = add_header
    self.add_footer = add_footer



def convert_to_csv(entries: str, ymd_date=None, customize: Customize=Customize()) -> list:
  """Receives formatted timesheet entries with optional date and converts them to a csv list."""

  # apply_modules  = customize.apply_modules if hasattr(customize, 'apply_modules') else None

  if not ymd_date:
    datefrm = ''
  else:
    dateobj = datetime.strptime(ymd_date, '%Y-%m-%d')
    datefrm = dateobj.strftime('%m/%d/%Y')

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

      if customize.apply_to_each_entry:
        for each_func in customize.apply_to_each_entry:
          # newdesc = apply_modules[name]['module'].initialize(newdesc, apply_modules[name]['settings'])
          newdesc = customize.func_list[each_func](newdesc)

      # -- 2. apply default macros

      newtime = macros.raw_time_to_excel_sum(newtime)
      # newdesc = macros.cap_description(newdesc)
                                        
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

  parsed_lines = modify_csv(parsed_lines, customize)

  return parsed_lines


def modify_csv(csv_list, customize: Customize=Customize()):
  """Modifies csv content by adding headers, footers, & columns"""
  #apply_modules  = customize.apply_modules if hasattr(customize, 'apply_modules') else None

  # headers & footers

  if customize.add_header:
    #                     0        1         2             3        4
    csv_list.insert(0, ['Date','Duration','Description', 'Hours', 'Splits'])

  if customize.add_footer:
    total_hours = round(sum(macros.try_float(col[3], 0) for col in csv_list), 2)
    #                 0   1                                   2                     3                 4
    csv_list.append(['', macros.hours_to_human(total_hours, True), 'Total Logged Hours', str(total_hours), ''])

  # module NICKNAME : if a NICKNAME var is set on a module, it can also be used to call the module

  if customize.apply_to_final_csv:
    for each_func in customize.apply_to_final_csv:
      csv_list = customize.func_list[each_func](csv_list)

  return csv_list


if __name__ == '__main__':
  """Tests"""
  
  import pprint

  print('---test1---')
  run = convert_to_csv('. 2.74h hello world ($zoom)', ymd_date=None, customize=Customize(
    apply_to_each_entry=('categorize','capitalize'),
    #apply_to_final_csv=('add_columns',),
  ))
  pprint.pprint(run)
  
  print('---test2---')
  run2 = convert_to_csv('. 30m bonjour le monde', ymd_date=None, customize=Customize(
    #apply_to_each_entry=('capitalize',),
  ))
  pprint.pprint(run2)


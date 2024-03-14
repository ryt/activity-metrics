#!/usr/bin/env python3

"""
Custom macros & helper functions for parsing entries.
Note: text conversion functions originally written as apps script macros for Google Sheets.
"""

import re
from functools import reduce

def cap_description(input):
  """Converts input to title case & applies custom modifications"""
  return input.title()


def convert_to_hours(str):
  """Converts short time format (e.g. 1:30h) into equavalent hours (e.g. 1.5)"""
  sep = re.match(r'([\d\,\.\:]+)(m|h|s)', str)
  num = sep.group(1)
  typ = sep.group(2)

  if ':' in num:
    num = num.split(':')
    num = float(num[0]) + (float(num[1]) / 60)

  if typ == 'h':
    num = float(num)
  elif typ == 'm':
    num = float(num) / 60
  elif typ == 's':
    num = float(num) / 3600

  return round(float(num), 4)


def hours_to_human_duration(input):
  try:
    input = float(input)
  except Exception:
    return ''

  input = round(input, 2)  # 2 decimal places

  # split into hours and minutes

  hrs, decimal = divmod(input, 1)
  mins = round(decimal * 60)

  # format hours as hours and minutes

  hrs_str = f"{int(hrs)} hr{'s' if hrs != 1 else ''} " if hrs > 0 else ''
  mins_str = f"{mins} min" if mins > 0 else ''

  return hrs_str + mins_str


def raw_time_to_excel_sum(input):
  """Receives a raw time string & returns a tuple: (excel sum function, calculation in hours, optional timestamp)"""
  sumfunc = ''
  calchrs = ''
  timestp = ''
  input = input.strip()

  # group 1: 7a|7am|7:30am etc...
  # group 2: 1m|2.5s|1:30h|1.234h etc...

  pattern = r'^([\d\:]+(?:am|pm|a|p)[\s\,]*)?(.*)$'
  match = re.search(pattern, input)

  if match:
    tmsp = match.group(1)
    rwtm = match.group(2)

    if rwtm:
      rwtm = rwtm.strip(';,')
      rwtm = rwtm.replace(' ', ',')
      rwtm = re.sub(r',{2,}', ',', rwtm)

      # split & parse each time unit
      rwtm = rwtm.split(',')

      # convert each unit into hours
      cvtm = [convert_to_hours(u) for u in rwtm]

      # create a new list with the converted units
      rwtm = ', '.join(str(u) for u in cvtm)
      sumfunc = f'=sum({rwtm})'

      # apply the sum function to the new list -> str()
      calchrs = str(round(reduce(lambda a, b: a + b, cvtm, 0), 2))

    if tmsp:
      timestp = tmsp.strip() + ' '

  return (sumfunc, calchrs, timestp)


"""
Todos:
# custom entries: e.g. supplement intake tracking (procre,pro,cre)
# smart auto categorization: e.g. #music, coding, etc...
# explicit categorization: e.g. ".(work, finance)"

"""




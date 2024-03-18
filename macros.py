#!/usr/bin/env python3

"""
Custom macros & helper functions for parsing entries.
Note: text conversion functions originally written as apps script macros for Google Sheets.
"""

import re

from functools import reduce
from datetime import datetime
from datetime import timedelta

def cap_description(inp):
  """Converts input to title case & applies custom modifications"""
  return inp.title()


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


def hours_to_human(inp):
  try:
    inp = float(inp)
  except Exception:
    return ''

  inp = round(inp, 2)  # 2 decimal places

  # split into hours and minutes

  hrs, decimal = divmod(inp, 1)
  mins = round(decimal * 60)

  # format hours as hours and minutes

  hrs_str = f"{int(hrs)} hr{'s' if hrs != 1 else ''} " if hrs > 0 else ''
  mins_str = f"{mins} min" if mins > 0 else ''

  return hrs_str + mins_str


def raw_time_to_excel_sum(inp):
  """Receives a raw time string & returns a tuple: (excel sum function, calculation in hours, optional timestamp)"""
  sumfunc = ''
  calchrs = ''
  timestp = ''
  inp = inp.strip()

  # group 1: 7a|7am|7:30am etc...
  # group 2: 1m|2.5s|1:30h|1.234h etc...

  pattern = r'^([\d\:]+(?:am|pm|a|p)[\s\,]*)?(.*)$'
  match = re.search(pattern, inp)

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



def parse_date_input(inp):
  """Receives a date input string of many date types and returns a dict with details & conversions"""
  inp = inp.strip()

  '''
  rname = arg2.replace('/','-')  # YYYY-MM-DD
  fname = rname.replace('-','/') # YYYY/MM/DD

  if fname in ('today', '/t'):
    rname = today_date
    fname = today_dfil
  elif fname in ('yesterday', '/y'):
    rname = yesterday_date
    fname = yesterday_dfil
  '''

  input_format = ''
  converted_ymd_dash = ''
  converted_ymd_slash = ''

  input_date_types = {

    r'^\d{1}\/\d{1}$' : 'M/D',
    r'^\d{2}\/\d{1}$' : 'MM/D',
    r'^\d{1}\/\d{2}$' : 'M/DD',
    r'^\d{2}\/\d{2}$' : 'MM/DD',

    r'^\d{2}\/\d{4}$' : 'MM/YYYY',

    r'^\d{1}\/\d{1}\/\d{2}$' : 'M/D/YY',
    r'^\d{2}\/\d{1}\/\d{2}$' : 'MM/D/YY',
    r'^\d{1}\/\d{2}\/\d{2}$' : 'M/DD/YY',
    r'^\d{2}\/\d{2}\/\d{2}$' : 'MM/DD/YY',

    r'^\d{1}\/\d{1}\/\d{4}$' : 'M/D/YYYY',
    r'^\d{2}\/\d{1}\/\d{4}$' : 'MM/D/YYYY',
    r'^\d{1}\/\d{2}\/\d{4}$' : 'M/DD/YYYY',
    r'^\d{2}\/\d{2}\/\d{4}$' : 'MM/DD/YYYY',

    r'^\d{4}\/\d{2}\/\d{2}$' : 'YYYY/MM/DD',
    r'^\d{4}\/\d{2}\/\d{1}$' : 'YYYY/MM/D',
    r'^\d{4}\/\d{1}\/\d{2}$' : 'YYYY/M/DD',
    r'^\d{4}\/\d{1}\/\d{1}$' : 'YYYY/M/D',

    r'^\d{4}\/\d{2}$' : 'YYYY/MM',
    r'^\d{4}\/\d{1}$' : 'YYYY/M',

    r'^\d{2}\/\d{2}\/\d{2}$' : 'YY/MM/DD',
    r'^\d{2}\/\d{2}\/\d{1}$' : 'YY/MM/D',
    r'^\d{2}\/\d{1}\/\d{2}$' : 'YY/M/DD',
    r'^\d{2}\/\d{1}\/\d{1}$' : 'YY/M/D',

    r'^\d{4}$' : 'YYYY',

  }

  today = datetime.today()
  yesterday = today - timedelta(days = 1)


  if inp in ('today', 'tod', '-t'):
    input_format = 'word'
    converted_ymd_dash = today.strftime('%Y-%m-%d')
    converted_ymd_slash = today.strftime('%Y/%m/%d')

  elif inp in ('yesterday', 'yest', '-y'):
    input_format = 'word'
    converted_ymd_dash = yesterday.strftime('%Y-%m-%d')
    converted_ymd_slash = yesterday.strftime('%Y/%m/%d')

  else:
    if '-' in inp:
      tinp = inp.replace('-','/')
      for reg, form in input_date_types.items():
        if re.match(reg, tinp):
          inp_spl = inp.split('-')
          form_spl = form.split('/')
          form_spl = [''.join(set(i)) for i in form_spl]
          assign = dict(zip(form_spl, inp_spl))
          if 'M' in assign and 'D' in assign and 'Y' not in assign:
            assign['Y'] = today.strftime('%Y')
          print(assign)
          input_format = form.replace('/','-')
    else:
      for reg, form in input_date_types.items():
        if re.match(reg, inp):
          input_format = form


  result = {
    'input' : inp,
    'input_format' : input_format,
    'converted_ymd_dash' : converted_ymd_dash,
    'converted_ymd_slash' : converted_ymd_slash,
  }

  return result





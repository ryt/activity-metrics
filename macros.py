#!/usr/bin/env python3

"""
Activity Metrics, Copyright (C) 2024 Ray Mentose.
Custom macros & helper functions for parsing entries.
Note: text conversion functions originally written as apps script macros for Google Sheets.
"""

import re

from functools import reduce
from datetime import datetime
from datetime import timedelta

def cap_description(inp):
  """Converts input to title case & applies custom modifications"""

  # only convert to title case if it's lowercased

  words  = inp.split()
  cwords = [word.title() if word.islower() and not is_quoted_or_braced(word) else word for word in words]
  inp    = ' '.join(cwords)

  return inp


def is_quoted_or_braced(word):
  """Only checks if a word starts with a single or double quote or a curly brace"""
  return word.startswith('"') or word.startswith("'") or word.startswith('{')


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


def is_date_input(inp):
  """Checks to see if given input is a valid date input or keyword"""
  return re.match(r'^(\d{4}|(\d{1,4}[-\/]\d{1,4}([-\/]\d{1,4})?)|tod(ay)?|-t|yest(erday)?|-y)$', inp)

def parse_date_input(inp):
  """Receives a date input string of many date types and returns a dict with details & conversions"""
  inp = inp.strip()

  today      = datetime.today()
  yesterday  = today - timedelta(days = 1)

  input_format   = ''
  res_ymd_dash   = ''
  res_ymd_slash  = ''
  res_ymd_log    = ''
  res_key_name   = ''
  res_each       = { 'D' : '', 'M' : '', 'Y' : '' }

  input_date_types = {

    r'^\d{1}\/\d{1}$' : 'M/D',
    r'^\d{2}\/\d{1}$' : 'MM/D',
    r'^\d{1}\/\d{2}$' : 'M/DD',
    r'^\d{2}\/\d{2}$' : 'MM/DD',

    r'^\d{2}\/\d{4}$' : 'MM/YYYY',
    r'^\d{1}\/\d{4}$' : 'M/YYYY',

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

    r'^\d{4}$' : 'YYYY',

  }

  input_type_dash = True if '-' in inp else False

  if inp in ('today', 'tod', '-t'):
    input_format  = 'keyword'
    res_ymd_dash  = today.strftime('%Y-%m-%d')
    res_ymd_slash = today.strftime('%Y/%m/%d')
    res_ymd_log   = f'{res_ymd_slash}.txt'
    res_key_name  = 'today'
    spl_ymd_slash = res_ymd_slash.split('/')
    res_each      = { 'D' : spl_ymd_slash[2], 'M' : spl_ymd_slash[1], 'Y' : spl_ymd_slash[0] }

  elif inp in ('yesterday', 'yest', '-y'):
    input_format  = 'keyword'
    res_ymd_dash  = yesterday.strftime('%Y-%m-%d')
    res_ymd_slash = yesterday.strftime('%Y/%m/%d')
    res_ymd_log   = f'{res_ymd_slash}.txt'
    res_key_name  = 'yesterday'
    spl_ymd_slash = res_ymd_slash.split('/')
    res_each      = { 'D' : spl_ymd_slash[2], 'M' : spl_ymd_slash[1], 'Y' : spl_ymd_slash[0] }

  else:

    for regex, form in input_date_types.items():

      # parse input_date_types also with '-' by substituting '/' with '-'

      splchr = '-' if input_type_dash else '/'
      newinp = inp.replace('-','/') if input_type_dash else inp

      if re.match(regex, newinp):

        inp_spl  = inp.split(splchr)

        # form (i.e. input_date_types{regex:form}) doesn't change the '/' here

        form_spl = form.split('/')
        form_spl = [''.join(set(i)) for i in form_spl]

        assign = dict(zip(form_spl, inp_spl))

        assign['D'] = '' if not 'D' in assign else assign['D']
        assign['M'] = '' if not 'M' in assign else assign['M']
        assign['Y'] = '' if not 'Y' in assign else assign['Y']

        assign['Y'] = today.strftime('%Y') if not assign['Y'] else assign['Y']
        assign['Y'] = datetime.strptime(assign['Y'],'%y').year if len(assign['Y']) == 2 else assign['Y']
        assign['M'] = f"0{assign['M']}" if len(assign['M']) == 1 else assign['M']
        assign['D'] = f"0{assign['D']}" if len(assign['D']) == 1 else assign['D']

        res_each = assign

        res_ymd_dash  = f"{assign['Y']}-{assign['M']}-{assign['D']}".strip('-')
        res_ymd_slash = f"{assign['Y']}/{assign['M']}/{assign['D']}".strip('/')
        res_ymd_log   = f'{res_ymd_slash}.txt'

        # change the '/' for form (i.e. input_date_types{regex:form}) here

        input_format = form.replace('/','-') if input_type_dash else form
        


  result = {
    'input' : inp,
    'input_format'    : input_format,
    'res_ymd_dash'    : res_ymd_dash,
    'res_ymd_slash'   : res_ymd_slash,
    'res_ymd_log'     : res_ymd_log,
    'res_key_name'    : res_key_name,
    'res_each'        : res_each,
  }

  return result





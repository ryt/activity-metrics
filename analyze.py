#!/usr/bin/env python3

"""
Copyright (c) 2024 Ray Mentose.

Tool for managing and analyzing personal analytics logs.

Usage:

  ./analyze.py
  ./analyze.py list

  ./analyze.py today

"""

import sys, os, re
from datetime import datetime

logs_dir = '../logs/'

nl = "\n"
bl = ''


def get_all_files(dir):
  files_list = []
  for root, dirs, files in os.walk(dir):
    for filename in files:
      if not filename.startswith('.'):
        files_list.append(os.path.relpath(os.path.join(root, filename), dir))
  return files_list


def analyze_files(logs_dir, nl, bl, list_files=False):

  print(nl + "Analyzing logs from directory " + logs_dir + ":")
  all_files = get_all_files(logs_dir)

  if all_files:

    files_list = []

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

      files_list.append({
        'file': file,
        'valid': valid,
        'custom': custom,
        'custom_text': custom_text,
        'ymd': ymd
      })

    #for fd in files_list:
    #  print(fd)

    valid_count = sum(1 for d in files_list if d.get('valid') == True)
    invalid_count = sum(1 for d in files_list if d.get('valid') == False)
    custom_count = sum(1 for d in files_list if d.get('custom') == True)
    ymd_count = sum(1 for d in files_list if d.get('ymd') == True)

    print(nl + 'Analysis:')
    print('-', len(files_list), 'total files found.')
    print('-', valid_count, 'valid files.')
    print('-', invalid_count, 'invalid files. These will be ignored.') if invalid_count else ''
    print('-', custom_count, 'of the valid files have custom text.') if custom_count else ''
    print('-', ymd_count, 'files in valid Y-m-d format.') if ymd_count else ''

    if list_files:
      valid_files = [d for d in files_list if d.get('valid') == True]
      invalid_files = [d for d in files_list if d.get('valid') == False]
      custom_files = [d for d in files_list if d.get('custom') == True]
      ymd_files = [d for d in files_list if d.get('ymd') == True]
      print(nl + 'Listing files:')
      print(valid_count, 'valid files:')
      print('- ' + "\n- ".join([d['file'] for d in valid_files if 'file' in d]) + nl)
      print(invalid_count, 'invalid files. These will be ignored:') if invalid_count else ''
      print('- ' + "\n- ".join([d['file'] for d in invalid_files if 'file' in d]) + nl) if invalid_count else ''
      print(custom_count, 'of the valid files have custom text:') if custom_count else ''
      print('- ' + "\n- ".join([d['file'] for d in custom_files if 'file' in d]) + nl) if custom_count else ''
      print(ymd_count, 'files in valid Y-m-d format:') if ymd_count else ''
      print('- ' + "\n- ".join([d['file'] for d in ymd_files if 'file' in d])) if ymd_count else ''

    """

    years = [fname[:4] for fname in all_files]
    months = [fname[:7] for fname in all_files]

    unique_years = set(years)
    unique_months = set(months)

    print('-', len(all_files), "total files found." + nl)

    print("Data spans", len(all_files), "total days across", len(unique_years), "years for a total of", len(unique_months), "months: ")

    year_month_dict = {}
    for date in unique_months:
      year, month = date.split('/')
      year_month_dict.setdefault(year, []).append(month)

    for year, months in sorted(year_month_dict.items()):
      print('-', year + ':', ', '.join(sorted(months)))
    """

  print(bl)



# Start parsing arguments. 

if len(sys.argv) > 1:
  if sys.argv[1]:
    arg1 = sys.argv[1]

    if arg1 == 'today':
      today = datetime.today()
      today_date = today.strftime('%Y-%m-%d')
      print(nl + "Analyzing data for today, " + today_date + ":")

      # look for files
      print("- Looking for " + today.strftime('%Y/%m/%d') + ".txt in " + logs_dir)
      print("- Looking for " + today.strftime('%Y/%m/%d') + "{custom}.txt in " + logs_dir)
      print("- Looking for " + today_date + ".txt in " + logs_dir)
      print("- Looking for " + today_date + "{custom}.txt in " + logs_dir)

      print(bl)

    elif arg1 == 'list':
      analyze_files(logs_dir, nl, bl, True)


else:
  analyze_files(logs_dir, nl, bl)

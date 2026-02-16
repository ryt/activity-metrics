#!/usr/bin/env python3

import re

from acme.core import utils

def validate_files(logs_dir, list_files=False):
  """Finds all log files in logs directory (logs_dir) & performs analysis of validity of their names & location"""
  output = []

  head_text = f'Analyzing logs from directory {logs_dir}:'

  # first_line_len = len(head_text)
  output += ['----'] # [0:first_line_len]]
  output += [f'{head_text}']

  all_files = utils.get_all_files(logs_dir)

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

    output += [f'\nAnalysis:']
    output += [f'- {str(len(flist))} total files found.']
    output += [f"- {valid_count} valid log files{(', including ' + str(custom_count) +' with custom names.' if custom_count else '.')}"]
    output += [f'- {ymd_count} log files in valid Y-m-d format.' if ymd_count else '']
    output += [f'- {invalid_count} files with invalid log file names. These will be ignored.' if invalid_count else '']

    if list_files:

      valid_files   = [d for d in flist if d.get('valid') == True]
      custom_files  = [d for d in flist if d.get('custom') == True]
      ymd_files     = [d for d in flist if d.get('ymd') == True]
      invalid_files = [d for d in flist if d.get('valid') == False]

      output += ['----'] # [0:first_line_len]]
      output += [f'Listing files:']

      output += [f'\n{valid_count} valid log files:']
      output += ['- ' + f'\n- '.join([d['file'] for d in valid_files if 'file' in d])]
      output += [f'\n{custom_count} of the valid log files have custom names:' if custom_count else '']
      output += ['- ' + f'\n- '.join([d['file'] for d in custom_files if 'file' in d]) if custom_count else '']
      output += [f'\n{ymd_count} log files in valid Y-m-d format:' if ymd_count else '']
      output += ['- ' + f'\n- '.join([d['file'] for d in ymd_files if 'file' in d]) if ymd_count else '']
      output += [f'\n{invalid_count} files with invalid log file names. These will be ignored:' if invalid_count else '']
      output += ['- ' + f'\n- '.join([d['file'] for d in invalid_files if 'file' in d]) if invalid_count else '']

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
  output += ['----'] # [0:last_line_len]]


  # clean output & print if valid
  output = [l for l in output if l.strip() != '']
  output = '\n'.join(output)

  if list_files:
    pydoc.pager(output) if output else None
    return

  print(output) if output else None



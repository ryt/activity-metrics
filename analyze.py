#!/usr/bin/env python3

"""
Copyright (c) 2024 Ray Mentose. 
Latest source can be found at: https://github.com/ryt/activity-metrics
"""

v='0.0.2'
man="""
Activity Metrics: A tool to analyze & display personal activity statistics.

Usage:

  Analyze        Command
  ------------------------
  ./analyze      (show|-s)
  ./analyze      (list|-l)

  Analyze        Date
  -------------------------
  ./analyze      (today|-t)

  Analyze        Generate CSV    Date 
  -----------------------------------------
  ./analyze      (gencsv|-g)     (Y-m-d)

  Analyze        Help & About
  ---------------------------------------
  ./analyze      (man|help|--help|-h)
  ./analyze      (--version|-v)

"""

import sys, os, re, macros
from datetime import datetime

logs_dir = '../logs/'
gen_dir = '../gen/'

nl = '\n'
bl = ''
hr = '-' * 100


def get_all_files(dir):
  """Returns a list of all files in given directory (dir)"""
  files_list = []
  for root, dirs, files in os.walk(dir):
    for filename in files:
      if not filename.startswith('.'):
        files_list.append(os.path.relpath(os.path.join(root, filename), dir))
  return files_list


def analyze_files(logs_dir, nl, bl, list_files=False):
  """Finds all log files in logs directory (logs_dir) & performs analysis of validity of their names & location"""
  head_text = f'Analyzing logs from directory {logs_dir}:'
  head_text_len = len(head_text)
  print(hr[0:head_text_len] + f'{nl}{head_text}')
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
    custom_count = sum(1 for d in files_list if d.get('custom') == True)
    ymd_count = sum(1 for d in files_list if d.get('ymd') == True)
    invalid_count = sum(1 for d in files_list if d.get('valid') == False)

    print(nl + 'Analysis:')
    print('-', len(files_list), 'total files found.')
    print('-', valid_count, 'valid files.', (str(custom_count) + ' have custom text.' if custom_count else '') )
    print('-', ymd_count, 'files in valid Y-m-d format.') if ymd_count else ''
    print('-', invalid_count, 'invalid files. These will be ignored.') if invalid_count else ''

    if list_files:
      valid_files = [d for d in files_list if d.get('valid') == True]
      custom_files = [d for d in files_list if d.get('custom') == True]
      ymd_files = [d for d in files_list if d.get('ymd') == True]
      invalid_files = [d for d in files_list if d.get('valid') == False]
      print(nl + 'Listing files:')
      print(valid_count, 'valid files:')
      print('- ' + "\n- ".join([d['file'] for d in valid_files if 'file' in d]) + nl)
      print(custom_count, 'of the valid files have custom text:') if custom_count else ''
      print('- ' + "\n- ".join([d['file'] for d in custom_files if 'file' in d]) + nl) if custom_count else ''
      print(ymd_count, 'files in valid Y-m-d format:') if ymd_count else ''
      print('- ' + "\n- ".join([d['file'] for d in ymd_files if 'file' in d])) if ymd_count else ''
      print(invalid_count, 'invalid files. These will be ignored:') if invalid_count else ''
      print('- ' + "\n- ".join([d['file'] for d in invalid_files if 'file' in d]) + nl) if invalid_count else ''

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

  print(f'{bl}' + hr[0:head_text_len])

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

def convert_to_csv(entries, ymd):
  """Receives the contents of a log txt file (entries) with date (ymd) and returns a generated csv content string"""
  lines = entries.splitlines()
  conv = []
  conv.append('Date,Hours,Raw Time,Description')
  dateobj = datetime.strptime(ymd, "%Y-%m-%d")
  datefrm = dateobj.strftime("%m/%d/%Y")
  for line in lines:

    # parse individual entries
    # group 1: time intervals (e.g. 7a|7am|7:30a|3.21s|5m|1.5h|30m|1:30h etc...)
    # group 2: description text

    # regex101 (ryt) v2: https://regex101.com/r/lrm5IQ/2

    pattern = r'^-(\s*(?:[\d\:\.]+(?:m|h|s|am|pm|a|p)[\s\,]*[\s\;]*)+)(.*)$'
    match = re.search(pattern, line)
    newline = ''
    if match:
      rawtime = time_macro(match.group(1))
      rawdesc = str(rawtime[2]) + cap_macro(match.group(2))
      newline = ','.join([datefrm, rawtime[1], escape_for_csv(rawtime[0]), escape_for_csv(rawdesc)])
      #newline = match.group(1) + ',' + match.group(2)
    if newline:
      conv.append(newline)
  return '\n'.join(conv);


def main():
  # Start parsing arguments
  if len(sys.argv) > 1:
    if sys.argv[1]:
      arg1 = sys.argv[1]

      if arg1 in ('today','-t'):
        today = datetime.today()
        today_date = today.strftime('%Y-%m-%d')
        print(f'{hr}{nl}Analyzing data for today, {today_date}:')

        # look for files
        print("- Looking for " + today.strftime('%Y/%m/%d') + ".txt in " + logs_dir)
        print("- Looking for " + today.strftime('%Y/%m/%d') + "{custom}.txt in " + logs_dir)
        print("- Looking for " + today_date + ".txt in " + logs_dir)
        print("- Looking for " + today_date + "{custom}.txt in " + logs_dir)

        print(f'{bl}{hr}')

      elif arg1 in ('gencsv','-g'):
        if len(sys.argv) > 2:
          rname = sys.argv[2]
          fname = rname.replace('-','/')
          filename = logs_dir + fname + '.txt'
          if os.path.exists(filename):

            # open individual log txt file
            with open(filename, 'r') as file:
              entries = file.read()
            entries = convert_to_csv(entries, rname)
            # generate individual log csv file
            genfile = gen_dir + rname + '.csv'
            with open(genfile, 'w') as file:
              file.write(entries)
            print(f"CSV file {genfile} successfully generated.")

          else:
            print(f"Log file '{filename}' does not exist.")
        else:
          print("Please specify a valid date (Y-m-d), month (Y-m), or year (Y).")

      elif arg1 in ('show','-s'):
        analyze_files(logs_dir, nl, bl)

      elif arg1 in ('list','-l'):
        analyze_files(logs_dir, nl, bl, True)


      # help & manual

      elif arg1 in ('--version','-v'):
        print('Version', v)

      elif arg1 in ('--help','-h','man','help'):
        print(man.strip() + nl)

      else:
        print("Invalid command '" + arg1 +  "'. " + "Use 'man' or 'help' for proper usage.")

  else:
    # run 'show' by default
    analyze_files(logs_dir, nl, bl)

if __name__ == "__main__":
  main()

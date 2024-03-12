#!/usr/bin/env python3

"""
Copyright (C) 2024 Ray Mentose. 
Latest source can be found at: https://github.com/ryt/activity-metrics
"""

v = '0.0.3'
c = 'Copyright (C) 2024 Ray Mentose.'
man = """
Activity Metrics: A tool to analyze & display personal activity statistics.

Usage:

  Analyze        Command
  -------------------------------------------------
  ./analyze      (stats|-s)
  ./analyze      (list|-l)

  Analyze        Date
  -------------------------------------------------
  ./analyze      (today|-t)

  Analyze        Generate CSV      Date 
  -------------------------------------------------
  ./analyze      (gencsv|-g)       (Y-m-d)

  Analyze        Helper Shortcut   ..
  -------------------------------------------------
  ./analyze      helper            (args)

  Analyze        Help & About
  -------------------------------------------------
  ./analyze      (man|help|--help|-h)
  ./analyze      (--version|-v)

"""

import sys, os, re, subprocess, macros
from datetime import datetime

logs_dir = '../logs/'
gen_dir  = '../gen/'

nl = '\n'
hr = '-' * 50


def get_all_files(dir):
  """Returns a list of all files in given directory (dir)"""
  flist = []
  for root, dirs, files in os.walk(dir):
    for filename in files:
      if not filename.startswith('.'):
        flist.append(os.path.relpath(os.path.join(root, filename), dir))
  return flist


def analyze_files(logs_dir, list_files=False):
  """Finds all log files in logs directory (logs_dir) & performs analysis of validity of their names & location"""
  output = []

  head_text = f'Analyzing logs from directory {logs_dir}:'

  # first_line_len = len(head_text)
  output += [hr] # [0:first_line_len]]
  output += [f'{head_text}']

  all_files = get_all_files(logs_dir)

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

    output += [f'{nl}Analysis:']
    output += [f'- {str(len(flist))} total files found.']
    output += [f"- {valid_count} valid log files{(', including ' + str(custom_count) +' with custom names.' if custom_count else '.')}"]
    output += [f'- {ymd_count} log files in valid Y-m-d format.' if ymd_count else '']
    output += [f'- {invalid_count} files with invalid log file names. These will be ignored.' if invalid_count else '']

    if list_files:

      valid_files   = [d for d in flist if d.get('valid') == True]
      custom_files  = [d for d in flist if d.get('custom') == True]
      ymd_files     = [d for d in flist if d.get('ymd') == True]
      invalid_files = [d for d in flist if d.get('valid') == False]

      output += [hr] # [0:first_line_len]]
      output += [f'Listing files:']

      output += [f'{nl}{valid_count} valid log files:']
      output += ['- ' + f'{nl}- '.join([d['file'] for d in valid_files if 'file' in d])]
      output += [f'{nl}{custom_count} of the valid log files have custom names:' if custom_count else '']
      output += ['- ' + f'{nl}- '.join([d['file'] for d in custom_files if 'file' in d]) if custom_count else '']
      output += [f'{nl}{ymd_count} log files in valid Y-m-d format:' if ymd_count else '']
      output += ['- ' + f'{nl}- '.join([d['file'] for d in ymd_files if 'file' in d]) if ymd_count else '']
      output += [f'{nl}{invalid_count} files with invalid log file names. These will be ignored:' if invalid_count else '']
      output += ['- ' + f'{nl}- '.join([d['file'] for d in invalid_files if 'file' in d]) if invalid_count else '']

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
  output += [hr] # [0:last_line_len]]


  # clean output & print if valid
  output = [l for l in output if l.strip() != '']
  output = nl.join(output)
  print(output) if output else None

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
  return nl.join(conv);


def main():
  # Start parsing arguments
  output = []
  if len(sys.argv) > 1:
    if sys.argv[1]:
      arg1 = sys.argv[1]

      today = datetime.today()
      today_date = today.strftime('%Y-%m-%d')
      today_dfil = today.strftime('%Y/%m/%d')

      if arg1 in ('today','-t'):
        head_text = f'Analyzing data for today, {today_date}:'

        # first_line_len = len(head_text)
        output += [hr] # [0:first_line_len]]
        output += [f'{head_text}']

        # look for files
        output += [f'- Looking for {today_dfil}.txt in {logs_dir}']
        output += [f'- Looking for {today_dfil}{{custom}}.txt in {logs_dir}']
        output += [f'- Looking for {today_date}.txt in {logs_dir}']
        output += [f'- Looking for {today_date}{{custom}}.txt in {logs_dir}']

        # last_line_len = len(output[-1])
        output += [hr] # [0:last_line_len]]

      elif arg1 in ('gencsv','-g'):

        if len(sys.argv) > 2:
          rname = sys.argv[2]
          fname = rname.replace('-','/')

          if fname == 'today':
            fname = today_dfil

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
            output += [f'CSV file {genfile} successfully generated.']

          else:
            output += [f'Log file {filename} does not exist.']

        else:
          output += [f'Please specify a valid date (Y-m-d), month (Y-m), or year (Y).']

      elif arg1 in ('stats','-s'):
        analyze_files(logs_dir)

      elif arg1 in ('list','-l'):
        analyze_files(logs_dir, True)

      elif arg1 == 'helper':
        cmd = sys.argv
        cmd.pop(0)
        cmd[0] = './helper'
        cmd = ' '.join(cmd)
        process = subprocess.run(cmd, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmdout = process.stdout.decode('utf-8')
        error = process.stderr.decode('utf-8')
        if process.returncode == 0:
          print(cmdout, end='')
          exit()
        else:
          print(f'Error: {error}')
          exit()


      # help & manual

      elif arg1 in ('--version','-v'):
        output += [f'Activity Metrics, Version {v}']
        output += [c]

      elif arg1 in ('--help','-h','man','help'):
        output += [man.strip() + f'{nl}']

      else:
        output += [f"Invalid command '{arg1}'. Use 'man' or 'help' for proper usage."]

  else:
    # run 'stats' by default
    analyze_files(logs_dir)

  print(nl.join(output)) if output else None

if __name__ == '__main__':
  main()

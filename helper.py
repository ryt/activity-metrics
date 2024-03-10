#!/usr/bin/env python3

# Note: Originally a bash script in version 0.0.1.

v = "0.0.2"
help_text = """
This helper script provides simple useful tools like API-based service utilities and commands to create date files and month directories. 
Some of the usage manual and related documentation is available in "utilities.md".

Usage:

  Helper         Command      Parent    Apply
  -------------------------------------------
  ./helper       makefiles    dir/
  ./helper       makedirs     dir/
  ./helper       makefiles    dir/      apply
  ./helper       makedirs     dir/      apply

  Helper         Todoist     Action      Id       Save/Filename
  ---------------------------------------------------------------------------
  ./helper       todoist     get-task    12345
  ./helper       todoist     get-task    12345    save=../logs/2024/01/01.txt
  ./helper       todoist     get-task    12345    autosave

"""

import sys, os, json, subprocess

logs_dir = '../logs/'
gen_dir = '../gen/'

def make_files(directory, apply_flag):
  if apply_flag == "apply":
    print(f"Applying making files in {directory}")
    for i in range(1, 32):
      day = str(i).zfill(2)
      open(os.path.join(directory, f"{day}.txt"), 'a').close()
      print(f"touch {os.path.join(directory, f'{day}.txt')} applied")
  else:
    print(f"Mock-making files in {directory}")
    for i in range(1, 32):
      day = str(i).zfill(2)
      print(f"touch {os.path.join(directory, f'{day}.txt')}")

def make_dirs(directory, apply_flag):
  if apply_flag == "apply":
    print(f"Applying making dirs in {directory}")
    for i in range(1, 13):
      month = str(i).zfill(2)
      os.makedirs(os.path.join(directory, month), exist_ok=True)
      print(f"mkdir {os.path.join(directory, month)} applied")
  else:
    print(f"Mock-making dirs in {directory}")
    for i in range(1, 13):
      month = str(i).zfill(2)
      print(f"mkdir {os.path.join(directory, month)}")

def curl(url, headers = ''):
  curl_command = f'curl "{url}" -H "{headers}"'
  process = subprocess.run(curl_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output = process.stdout.decode('utf-8')
  error = process.stderr.decode('utf-8')
  if process.returncode == 0:
    return output
  else:
    return f'Error: {error}'


def todoist_options(args):

  action = args[1] if len(args) >= 2 else ''
  optid  = args[2] if len(args) >= 3 else ''
  savef  = args[3] if len(args) >= 4 else ''

  # Todoist API token should be stored in "~/.api_todoist" file.
  todoist_file = os.path.expanduser('~') + '/.api_todoist';

  with open(todoist_file) as f: api_token = f.read().strip()

  if api_token:

    if action == 'get-task':
      if optid.isnumeric():
        response = curl(f'https://api.todoist.com/rest/v2/tasks/{optid}', f'Authorization: Bearer {api_token}')
        if response:
          task_json = json.loads(response)
          title = task_json['content']
          entry = task_json['description']
          date = task_json['created_at']
          print(title)
          print(entry)
          print(date)
          if savef == 'autosave':
            print('Auto smart save will look for 01/01.txt in the title name & will fall back to the file creation date.')
          elif savef[0:5] == 'save=':
            print(f'Save as: {logs_dir}{savef[5:]}')
          else:
            print('Just show')

    print(f"Todoist {action} {optid} {savef}")

  else:

    print(f"Todoist API token could not be found in {todoist_file}.")


def print_help():
  print(help_text.strip()+'\n')

def print_version():
  print(f"Version {v}")

def main():
  args = sys.argv[1:]
  if len(args) == 0:
    print("Use the help or -h command for proper usage.")
    return
  
  com = args[0]
  directory = args[1] if len(args) >= 2 else "./"
  apply_flag = args[2] if len(args) >= 3 else ""

  if com == "makefiles":
    make_files(directory, apply_flag)
  elif com == "makedirs":
    make_dirs(directory, apply_flag)
  elif com == "todoist":
    todoist_options(args)
  elif com in ["help", "--help", "-h"]:
    print_help()
  elif com in ["version", "--version", "-v"]:
    print_version()
  else:
    print("Use the help or -h command for proper usage.")

if __name__ == "__main__":
  main()

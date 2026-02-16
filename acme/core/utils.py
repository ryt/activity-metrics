#!/usr/bin/env python3

# activity metrics (acme) utils
# latest source & docs at: https://github.com/ryt/activity-metrics.git

import sys
import os
import re
import time
import json
import pydoc

import http.client
import pandas as pd
import urllib.parse

from datetime import datetime
from datetime import timedelta

from io import StringIO

from acme.core import macros


def get_all_files(dir):
  """Returns a list of all files in given directory (dir)"""
  flist = []
  for root, dirs, files in os.walk(dir):
    for filename in files:
      if not filename.startswith('.'):
        flist.append(os.path.relpath(os.path.join(root, filename), dir))
  return flist


def write_to_file(file, contents):
  # -- write contents to file -- #
  with open(file, 'w') as f:
    f.write(contents)


def make_files(directory, applyf):
  if applyf == 'apply':
    print(f'Applying making files in {directory}')
    for i in range(1, 32):
      day = str(i).zfill(2)
      open(os.path.join(directory, f'{day}.txt'), 'a').close()
      print(f"touch {os.path.join(directory, f'{day}.txt')} applied")
  else:
    print(f'Mock-making files in {directory}')
    for i in range(1, 32):
      day = str(i).zfill(2)
      print(f"touch {os.path.join(directory, f'{day}.txt')}")


def make_dirs(directory, applyf):
  if applyf == 'apply':
    print(f'Applying making dirs in {directory}')
    for i in range(1, 13):
      month = str(i).zfill(2)
      os.makedirs(os.path.join(directory, month), exist_ok=True)
      print(f'mkdir {os.path.join(directory, month)} applied')
  else:
    print(f'Mock-making dirs in {directory}')
    for i in range(1, 13):
      month = str(i).zfill(2)
      print(f'mkdir {os.path.join(directory, month)}')


def cleangen():
  """Removes gencsv files older than 1 week from gencsv directory"""
  files  = os.listdir(gen_dir)
  thresh = datetime.today().date() - timedelta(days=7)
  fcount = 0
  for name in files:
    if name.endswith('.csv'):
      stem = name[:-4] # remove .csv
      try:
        file_date = datetime.strptime(stem, "%Y-%m-%d").date()
        if file_date <= thresh:
          print(name)
          os.remove(f'{gen_dir}{name}')
          fcount += 1
      except ValueError: # not in YYYY-MM-DD format
        pass
  if fcount > 0:
    print(f"{('-'*14)}\nCleaned up {fcount} older gencsv file(s) from: {gen_dir}")
  else:
    print(f'Nothing to clean up.')


def escape_for_csv(input):
  """Prepares the given input for csv output"""
  if isinstance(input, str):
    # escape a double quote (") with additional double quote ("")
    value = input.replace('"', '""')
    value = '"' + value + '"'
    return value
  else:
    return input


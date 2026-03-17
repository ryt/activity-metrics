"""
Utils
"""

import os
import re
import json

from datetime import datetime
from datetime import timedelta

from acme.core.settings import Settings

def settings_json():
  """Returns all available merged settings as formatted json."""
  merged_settings = Settings.merged_settings
  merged_settings['web']['secret_key'] = '*****'
  indented_json = json.dumps(merged_settings, indent=2)
  compact_json  = re.sub(
    r'\[\s*([^\[\]]+?)\s*\]',
    lambda match: f"[{' '.join(match.group(1).split())}]",
    indented_json,
    flags=re.DOTALL,
  )
  return compact_json


def find_path(name, curr=os.path.abspath(os.curdir)):
  """Checks if directory (name) exists in specified (curr) or parents."""

  while True:
    search_path = os.path.join(curr, name)
    if os.path.isdir(search_path):
      return search_path

    par = os.path.dirname(curr)
    if curr == par:
      return None

    curr = par


def get_all_files(dir):
  """Returns a list of all files in given directory (dir)."""
  flist = []
  for root, dirs, files in os.walk(dir):
    for filename in files:
      if not filename.startswith('.'):
        flist.append(os.path.relpath(os.path.join(root, filename), dir))
  return flist


def write_to_file(file, contents):
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


def cleangen(meta):
  """Removes gencsv files older than 1 week from gencsv directory."""
  files  = os.listdir(meta.gen_dir)
  thresh = datetime.today().date() - timedelta(days=7)
  fcount = 0
  for name in files:
    if name.endswith('.csv'):
      stem = name[:-4] # remove .csv
      try:
        file_date = datetime.strptime(stem, "%Y-%m-%d").date()
        if file_date <= thresh:
          print(name)
          os.remove(f'{meta.gen_dir}{name}')
          fcount += 1
      except ValueError: # not in YYYY-MM-DD format
        pass
  if fcount > 0:
    print(f"{('-'*14)}\nCleaned up {fcount} older gencsv file(s) from: {meta.gen_dir}")
  else:
    print(f'Nothing to clean up.')


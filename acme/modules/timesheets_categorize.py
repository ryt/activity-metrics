"""
Timesheets Module: Categorize Option
------------------------------------
Creates category columns for a CSV using categories and shortcuts 
from parenthesis blocks at the end of each entry.


Module Options Usage:
---------------------
  Run      Generate CSV    Date Input       Module Options
  ----------------------------------------------------------
  acme     gencsv          {date_input}     categorize | cat


Overview: Categories and $shortcuts for Timesheets
-----------------------------------------------------
The categorize module allows entries to have categories that can be nested and abbreviated.
  - Categories are comma separated lists surrounded by parenthesis at the end of each entry.
  - Categories can only be parsed from the very end of an entry and cannot have any other character after the closing parenthesis.
Here is a valid example:
 - {rest_of_entry} (category1, category2, category3, category4, category5, category6, category7, category8, category9, category10){end}
A regular parenthesis block can be differentiated from a category block by having characters or text after the closing parenthesis. 
Note the space and semicolons below. Both examples below are NOT counted as categories.
  - {rest_of_entry} (regular paren block) {end} <-- ends with space
  - {rest_of_entry} (regular paren block);{end} <-- ends with semicolon

Categorization Content Rules
- There are a maximum number of 10 categories allowed. (Subcategories can be conceptualized as successive categories.)
- Categories must be in [a-zA-Z0-9-_\\s]+ format.
- Commas are not strictly necessary to separate categories except where spaces are part of the name of the category.

Abbreviating Categories: $shortcuts
- A $shortcut is simply a shortcut name for a category that will be replaced or substituted at parse time.
- A $shortcut must start with a '$' for categories.
- The parser will use the $shortcut glossary to find and replace the shortcuts in the parenblock with their appropriate substitutions.

Examples:
- {rest_of_entry} ($zoom)
- {rest_of_entry} (fitness, $fit24)

Glossary Example:
- $zoom    :    work, meeting, zoom
- $fit24   :    fitness, 2024

In the above examples, the parser will find the $shortcuts ($zoom & $fit24) and replace them with the appropriate categories.
The glossary can contain unlimited definitions for $shortcuts.
"""

import re
import sys
import importlib

from acme.core.settings import Settings

settings = Settings.settings

NAME      = 'categorize'
NICKNAME  = 'cat'
NAMESPACE = 'acme.modules.timesheets_categorize'

KEEPRAWSHORTCUTS = True  # option to keep raw ($shortcuts) at end of entries

# the glossary file path can be customized in the workspace copy of workspace_config.yaml
GLOSSARYFILE = settings('modules.timesheets_categorize.glossaryFile')

def initialize(entry):
  """Adds workspace to python path, loads glossary, and calls replace_shortcuts."""
  currentWorkspaceDir = settings('workspace.currentWorkspaceDir')
  if currentWorkspaceDir:
    sys.path.append(currentWorkspaceDir)
    sys.path.append(f'{currentWorkspaceDir}/apps')
  glossary = importlib.import_module(GLOSSARYFILE)
  entry = replace_shortcuts(entry, glossary)
  return entry


def finalize(csv_list):
  """The finalize function runs on the final CSV list if the module is enabled."""
  csv_list = add_category_columns(csv_list)
  return csv_list


def add_category_columns(csv_list):
  """Additional final options for the CSV"""
  """Adds additional columns for the final CSV using the parenblock categories."""
  
  csv_header_row_index     = 0
  csv_desc_column_index    = 2
  cat_add_at_column_index  = 2

  prepared_lines = []
  category_lines = []
  
  # -- start: prepare lines -- #
  for line in csv_list:
    column_desc = line[csv_desc_column_index].strip('"') # strip double quotes
    entry_split = split_entry_at_parenblock(column_desc)

    if entry_split:
      category_lines.append([s.strip() for s in entry_split['parenblock_inside'].split(',')])
      desc_sans_parenblock = entry_split['rest_of_entry']
    else:
      category_lines.append([])
      desc_sans_parenblock = column_desc

    new_line = line
    new_line[csv_desc_column_index] = f'"{desc_sans_parenblock}"' # wrap with double quotes

    prepared_lines.append(new_line)
  
  # -- end: prepare lines -- #

  max_cat = max(len(l) for l in category_lines)

  category_names    = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']
  header_additions  = [category_names[i] for i in range(0, max_cat)]

  result_list = []

  # -- start: modify each line -- #

  for i, pl in enumerate(prepared_lines):
    for j in range(0, max_cat):
      # add empty spaces for categories

      pl.insert(cat_add_at_column_index + j, '')

      # add headers from category names list

      if header_additions and i == csv_header_row_index:
        pl[cat_add_at_column_index + j] = header_additions[j]

      # add categories if categories are found and have value

      if category_lines[i]:
        pl[cat_add_at_column_index + j] = category_lines[i][j] if len(category_lines[i]) > j else ''

    result_list.append(pl)

  # -- end: modify each line -- #

  print('Categories successfully applied to entries.')
  
  return result_list


def split_entry_at_parenblock(entry):
  """Receives an entry string and separates parenblock & rest of entry."""
  pattern = r'^(.*)(\(([a-zA-Z0-9-_,;\s#\$]+)\))$'
  match   = re.search(pattern, entry)
  result  = {}

  if match:
    result = {
      'rest_of_entry'     : match.group(1),
      'parenblock'        : match.group(2),
      'parenblock_inside' : match.group(3),
    }
  else:
    result = False

  return result


def replace_shortcuts(entry, glossary):
  """Receives an entry string and performs substitutions for $shortcuts."""
  
  entry_split = split_entry_at_parenblock(entry)
  modif_entry = ''

  if entry_split:

    rest_of_entry     = entry_split['rest_of_entry']
    parenblock        = entry_split['parenblock']
    parenblock_inside = entry_split['parenblock_inside']

    shortcut_glossary = glossary.shortcut_glossary

    # -- expand alias tuples: [ (key,val), ((a,b), c) ... -> [ (key,val), (a,c), (b,c) ... -- #
    expanded = [
      (alias, v)
      for k, v in shortcut_glossary
      for alias in (k if isinstance(k, tuple) else (k,))
    ]
    subs = dict(expanded)

    # -- substitute longest keys first to prevent collision -- #
    for key in sorted(subs, key=len, reverse=True):
      val = subs[key]
      # -- test via: print(f'{key} => {val}') -- #
      if isinstance(key, tuple):
        for k in key:
          parenblock_inside = parenblock_inside.replace(k, val)
      else:
        parenblock_inside = parenblock_inside.replace(key, val)

    rawcat_parenblock = ''
    if KEEPRAWSHORTCUTS:
      rawcat_parenblock = parenblock

    modif_entry = f'{rest_of_entry}{rawcat_parenblock}({parenblock_inside})'

  else:
    modif_entry = entry

  return modif_entry


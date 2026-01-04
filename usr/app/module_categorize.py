#!/usr/bin/env python3

"""Categorize Module"""

name      = 'Categorize Module'
nickname  = 'cat'

"""
Module Options:
---------------
- module_categorize : Creates columns for a CSV using the categories inside of parenthesis blocks at the end.

Module Options Usage:
---------------------
  Run      Generate CSV    Date Input       Module Options
  ----------------------------------------------------------------
  acme     gencsv          {date_input}     module_categorize | cat

"""


"""
Categorize Module: Categories, Hashtags, & $shortcuts
-----------------------------------------------------
The categorize module allows entries to have 2 types of important labels: categories & hashtags.
  - Daily logs can be categorized by adding comma separated lists surrounded by parenthesis at the end of each log.
  - Categories can only be parsed from the very end of an entry and cannot have any other character after the closing parenthesis.
Here are 2 valid examples:
 - {rest_of_entry} (category1, category2, category3, category4, category5, category6, category7, category8, category9, category10, #hashtag1 #hash tag 2 #hashtag 3, #hashtag5 #hashtag-number-6){end}
 - {rest_of_entry} (category1 #hashtag one, category2, category number three, #hashtag 2, #hashtag3 #hashtag number four){end}
A regular parenthesis block can be differentiated from a category block by having characters or text after the closing parenthesis. Note the space and semicolons below.
  - {rest_of_entry} (regular paren block) {end} <-- ends with space
  - {rest_of_entry} (regular paren block);{end} <-- ends with semicolon

Categorization Content Rules
- There are a maximum number of 10 categories allowed. (Subcategories can be conceptualized as successive categories.)
- There are an umlimited number of hashtags allowed.
- Categories must be in [a-zA-Z0-9-_\\s]+ format.
- Hashtags must start with '#' and be in [a-zA-Z0-9-_\\s]+ format after the '#'.
- Commas are not strictly necessary to separate categories and hashtags except where spaces are part of the name of the category or hashtag.
- Categories and hashtags are parsed in the order of their type. Order mixing between types is allowed as in example 2 above.

$shortcuts
- A $shortcut is simply a shortcut name for a category or hashtag that will be replaced or substituted at parse time.
- A $shortcut must start with a '$' for both categories and hashtags.
- The parser will use the $shortcut glossary to find and replace the shortcuts in the parenblock with their appropriate substitutions.

Examples:
- {rest_of_entry} ($zoom)
- {rest_of_entry} (fitness, $fit24)

Glossary Example:
- $zoom    :    work, meeting, zoom
- $fit24   :    #fitness-challenge-2024

In the above examples, the parser will find the $shortcuts ($zoom & $fit24) and replace them with the appropriate categories and hashtags.
The glossary can contain unlimited definitions for $shortcuts.
"""


import re

# The apply function is required for each module.

def apply(entry, glossary):
  """This function is automatically called on each entry if this module is used in 'module_settings.py'!"""
  entry = replace_shortcuts(entry, glossary)
  return entry


# The options function can be used to modify the final CSV list if the module is using options.
# The 'meta' argument dict has the following keys: module_options, option, add_header, add_footer.

def options(csv_list, meta={}):
  """Additional final options for the CSV"""
  """The categorize option adds additional columns for the final CSV using the parenblock categories."""

  # -- start: module_categorize -- #

  if meta['option'] == 'module_categorize':

    csv_header_row_index     = 0
    csv_desc_column_index    = 2
    cat_add_at_column_index  = 2

    prepared_lines = []
    category_lines = []

    # -- start: prepare lines

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

    # -- end: prepare lines

    max_cat = max(len(l) for l in category_lines)

    category_names    = ['C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9', 'C10']
    header_additions  = [category_names[i] for i in range(0, max_cat)]


    result_list = []

    # -- start: modify each line

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

    # -- end: modify each line

    print('Categories successfully applied to entries.')

    return result_list

  # -- end: module_parenblock.categorize

  return csv_list


def split_entry_at_parenblock(entry):
  """Receives an entry string and separates parenblock & rest of entry."""
  pattern = r'^(.*)(\(([a-zA-Z0-9-_,;\s#\$]+)\))$'
  match   = re.search(pattern, entry)
  result  = {}

  if match:
    result = {
      'rest_of_entry'   : match.group(1),
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

    for line in shortcut_glossary:
      key = line[0]
      val = line[1]
      if isinstance(key, tuple):
        for k in key:
          parenblock_inside = parenblock_inside.replace(k, val)
      else:
        parenblock_inside = parenblock_inside.replace(key, val)

    modif_entry = f'{rest_of_entry}({parenblock_inside})'

  else:
    modif_entry = entry

  return modif_entry



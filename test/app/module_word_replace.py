#!/usr/bin/env python3

"""Word Replace Module"""

"""
Word Replace Overview
---------------------
- custom word replacements : e.g. acronyms, custom acronyms, initialisms, custom abbreviations, for different categories (ref. google sheets Timesheet Library)
"""

name = 'Word Replace Module'

# The apply function is required for each module.

def apply(entry, glossary):
  """This function is automatically called on each entry if this module is used in 'module_settings.py'!"""
  return entry


# The options function can be used to modify the final CSV list if the module is using options.
# The 'meta' argument dict has the following keys: module_options, option, add_header, add_footer.
# Options Usage:
#
#   ./analyze {rest_of_command} module_word_replace.action_name
#

"""
def options(csv_list, meta={}):
  return csv_list
"""
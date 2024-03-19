#!/usr/bin/env python3

"""Health & Fitness Module"""

"""
Health & Fitness Module Overview
--------------------------------
- nutrition metrics        : e.g. supplement intake tracking (e.g. procre,pro,cre)
- fitness metrics          : e.g. garmin api connection
"""

name = 'Health & Fitness Module'

# The apply function is required for each module.

def apply(entry, glossary):
  """This function is automatically called on each entry if this module is used in 'module_settings.py'!"""
  return entry


# The options function can be used to modify the final CSV list if the module is using options.
# The 'meta' argument dict has the following keys: module_options, option, add_header, add_footer.
# Options Usage:
#
#   ./analyze {rest_of_command} module_health_fitness.action_name
#

"""
def options(csv_list, meta={}):
  return csv_list
"""
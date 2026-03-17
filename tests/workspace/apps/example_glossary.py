"""
Example glossary file for the timesheets_categorize module.
"""

# The shortcut_glossary variable is used to specify shortcuts and categories.

# This is an example file, to use it with the timesheets_categorize module within in a workspace, 
# copy this file to the {workspace}/app directory and add custom definitions.

shortcut_glossary = [

  # Examples shortcuts and nested categories.

  ('$inv',    'Work, Accounting, Inventory'),
  ('$zoom',   'Work, Meeting, Zoom'),

  (('$examstud', '$exm'), 'Academics, Study, Exam'),


]

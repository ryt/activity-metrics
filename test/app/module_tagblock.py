#!/usr/bin/env python3

"""Tagblock Module"""

# Naming refs: https://www.gnu.org/software/make/manual/make.html https://docs.docker.com/reference/dockerfile/

"""
Tagblock Module: Categories, Hashtags, & Subtags
------------------------------------------------
The tagblock module allows entries to have 2 types of important labels: categories & hashtags.
  - A tagblock is simply a block of text surrounded by parenthesis that can contain category names, hashtags, and subtags.
  - A tagblock can only be parsed from the very end of an entry and cannot have any other character after the closing parenthesis.
Here are 2 valid examples:
 - {rest_of_entry} (category1, category2, category3, category4, category5, category6, category7, category8, category9, category10, #hashtag1 #hash tag 2 #hashtag 3, #hashtag5 #hashtag-number-6){end}
 - {rest_of_entry} (category1 #hashtag one, category2, category number three, #hashtag 2, #hashtag3 #hashtag number four){end}
A regular parenthesis block can be differentiated from a tagblock by having characters or text after the closing parenthesis. Note the space and semicolons below.
  - {rest_of_entry} (regular paren block) {end}
  - {rest_of_entry} (regular paren block);{end}

Tagblock Content Rules
- There are a maximum number of 10 categories allowed. (Subcategories can be conceptualized as successive categories.)
- There are an umlimited number of hashtags allowed.
- Categories must be in [a-zA-Z0-9-_\s]+ format.
- Hashtags must start with '#' and be in [a-zA-Z0-9-_\s]+ format after the '#'.
- Commas are not strictly necessary to separate categories and hashtags except where spaces are part of the name of the category or hashtag.
- Categories and hashtags are parsed in the order of their type. Order mixing between types is allowed as in example 2 above.

Subtags
- A subtag is simply a shortcut name for a category or hashtag that will be replaced or substituted at parse time.
- A subtag must start with a '$' for both categories and hashtags.
- The parser will use the subtag glossary to find and replace the shortcuts in the tagblock with their appropriate substitutions.

Examples:
- {rest_of_entry} ($zoom)
- {rest_of_entry} (fitness, $fit24)

Glossary Example:
- $zoom    :    work, meeting, zoom
- $fit24   :    #fitness-challenge-2024

In the above examples, the parser will find the subtags ($zoom & $fit24) and replace them with the appropriate categories and hashtags.
The glossary can contain unlimited definitions for subtags.
"""

name = 'Tagblock Module'

import re

def replace_subtags(entry, glossary):
  """Receives an entry string and performs substitutions for subtags."""
  
  pattern = r'^(.*)(\(([a-zA-Z0-9-_,;\s#\$]+)\))$'
  match = re.search(pattern, entry)
  modentry = ''

  if match:

    rest_of_entry = match.group(1)
    tagblock = match.group(2)
    tagblock_inside = match.group(3)

    subtag_glossary = glossary.subtag_glossary

    for line in subtag_glossary:
      key = line[0]
      val = line[1]
      if isinstance(key, tuple):
        for k in key:
          tagblock_inside = tagblock_inside.replace(k, val)
      else:
        tagblock_inside = tagblock_inside.replace(key, val)

    modentry = f'{rest_of_entry}({tagblock_inside})'

  else:
    modentry = entry

  return modentry


# The apply function is required for each module.

def apply(entry, glossary):
  """This apply function is automatically called on each entry if this module is used in local settings."""
  entry = replace_subtags(entry, glossary)
  return entry


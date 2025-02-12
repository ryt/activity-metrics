#!/usr/bin/env python3

"""Settings Module"""

"""
The Settings Module is required before using any other modules.
The '.py' extension is automatically added to the definitions on import.
"""

# use glossary

use_glossary = 'glossary'

# use modules available by default in {install_dir}/activity-metrics/usr/app/

use_default_modules = (
  'module_tagblock',
  'module_word_replace',
  'module_health_fitness',
)


# use custom local modules in local app/ directory

use_local_modules = {
  # /<path>,      {module_script},                {module_name}
  # 'athletics' : ('dashboard_athletics.py',      'athletics'),
  # 'nutrition' : ('dashboard_nutrition.py',      'nutrition'),
  # 'health'    : ('dashboard_health.py',         'health'),
}

# additional top bar navigation links

add_nav_links = (
  # {module_name},  /{path},      <a>{link_text}</a>
  # ('athletics',   'athletics',  'athletics'),
  # ('nutrition',   'nutrition',  'nutrition'),
  # ('health',      'health',     'health'),
)

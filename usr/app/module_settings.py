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
  'module_categorize',     # the default categorize module allows entries to have (categories) and $shortcut names
# 'module_word_replace',   # example custom word replace module
# 'module_fitness',        # example custom fitness tracking module
# 'module_nutrition',      # example custom nutrition tracking module
)


# run custom local modules in local app/ directory

run_local_modules = {
  # /<path>,      {module_script},                {module_name}
  # 'index'     : ('dashboard_index.py',          'index'),
  # 'commands'  : ('dashboard_commands.py',       'commands'),
  # 'athletics' : ('dashboard_athletics.py',      'athletics'),
  # 'nutrition' : ('dashboard_nutrition.py',      'nutrition'),
  # 'fitness'   : ('dashboard_fitness.py',        'fitness'),
  # 'custom'    : ('dashboard_custom.py',         'custom'),
}

# additional top bar navigation links

add_nav_links = (
  # {module_name},  /{path},      <a>{link_text}</a>
  # ('athletics',   'athletics',  'athletics'),
  # ('nutrition',   'nutrition',  'nutrition'),
  # ('fitness',     'fitness',    'fitness'),
)

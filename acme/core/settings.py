"""Settings: Configuration Manager"""

import os
import sys
import yaml

from pathlib import Path
from functools import reduce


def merge_dicts_nested(*dicts):
  """Utility func to merge dicts and handle nesting."""
  result = {}
  def merge(source, destination):
    for key, value in source.items():
      if isinstance(value, dict) and key in destination:
        merge(value, destination[key])  # recursive call for nested dict
      else:
        destination[key] = value  # override or set the value
  for d in dicts:
    merge(d, result)
  return result


class Settings:

  defaults          = {}
  acme_config       = {}
  workspace_config  = {}
  merged_settings   = {}

  def setWorkspaceDir(dir):
    """Manually set workspace dir"""
    try:
      with open(f"{dir}/{Settings.defaults['workspace']['configFileName']}", 'r') as file:
        Settings.workspace_config = yaml.safe_load(file)
    except:
      pass
    Settings.defaults['workspace']['currentWorkspaceDir'] = dir
    Settings.merged_settings = merge_dicts_nested(
      Settings.defaults, 
      Settings.acme_config, 
      Settings.workspace_config
    )
  
  def settings(key):
    """Usage: settings('acme.configDir') ... """
    try:
      return reduce(lambda c, k: c[k], key.split('.'), Settings.merged_settings)
    except:
      return False


acme_main = Path(__file__).resolve().parent.parent
tests_dir = f'{acme_main.parent}/tests'

# load all available config files

# -- load: defaults -- #
defaults_file  = f'{acme_main}/conf/defaults.yaml'
with open(defaults_file, 'r') as file:
  Settings.defaults = yaml.safe_load(file)
  # modify: expand to full paths
  Settings.defaults['acme']['configDir'] = os.path.expanduser(Settings.defaults['acme']['configDir'])


# -- load: acme config -- #
acme_config_file = f"{Settings.defaults['acme']['configDir']}/{Settings.defaults['acme']['configFileName']}"
try:
  with open(acme_config_file, 'r') as file:
    Settings.acme_config = yaml.safe_load(file)
except:
  pass


# -- load: workspace config -- #
workspace_config_name = Settings.defaults['workspace']['configFileName']
workspace_tests_dir = f'{tests_dir}/workspace'
workspace_current_dir = '.'
if os.path.isfile(f'{workspace_current_dir}/{workspace_config_name}'):
  workspace_selected_dir = workspace_current_dir
elif len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
  workspace_selected_dir = sys.argv[1]
else:
  workspace_selected_dir = workspace_tests_dir
try:
  with open(f'{workspace_selected_dir}/{workspace_config_name}', 'r') as file:
    Settings.workspace_config = yaml.safe_load(file)
except:
  pass


Settings.defaults['workspace']['currentWorkspaceDir'] = workspace_selected_dir
Settings.merged_settings = merge_dicts_nested(
  Settings.defaults,
  Settings.acme_config,
  Settings.workspace_config
)

# Settings.setWorkspaceDir('hello-world')
# print(Settings.settings('workspace.currentWorkspaceDir'))

#!/usr/bin/env python3

"""Configuration options that can be customized."""
"""Default config options from acme.core.options can be refrenced here with {options.KEY}"""

config = {

  # --- options for api integrations --- #

  # Enable for the HTTP json utility
  #'http_json_file_dir' : '{options.CONFIG_DIR_FULL}',

  # Enable for the Todoist integration utility
  #'todoist_api_file' : '{options.CONFIG_DIR_FULL}.api_todoist',

  # --- options for the acmedash flask web app --- #

  # Set 'limitpath' to a custom value to set the relative path (i.e. prefix) of the default metrics directory
  # By default, the directory is "/", the root directory.

  'limitpath' : '/home/user/project/',

  # Set 'app_path' to a custom value to change the default path that will be used to route the index page of the app.
  # For example, if the value is "/dashboard", the default url of the web app will be something like 
  # "https://localhost:8002/dashboard", rather than "https://localhost:8002/".

  # 'app_path'  : '/dashboard',

  # Set 'secret_key' to set an app.secret_key for Flask.

  'secret_key'  : 'flask_secret_key',

}

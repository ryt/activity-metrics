#!/usr/bin/env python3

import os
import time
import json
import http.client
import urllib.parse

from datetime import datetime

from acme.core import macros


def http_options(args, callname, meta):

  httpfile   = args[1] if len(args) >= 2 else ''
  dateinput  = args[2] if len(args) >= 3 else ''
  savef      = args[3] if len(args) >= 4 else ''

  date_today = datetime.today()


  if not httpfile:
    exit(f'Please specify an http json file path.')

  # http json file should be stored in "{meta.app_dir}/"
  httpjson_file = f'{meta.app_dir}{httpfile}';

  try:
    with open(httpjson_file) as f: command = f.read().strip()

  except FileNotFoundError as e:
    print(f"HTTP json file `'{httpjson_file}'` not found.")
    exit()

  if command:

    if macros.is_date_input(dateinput):

      parsed       = macros.parse_date_input(dateinput)
      parsed_dash  = parsed['res_ymd_dash']
      parsed_each  = parsed['res_each']

      opd = parsed_each['D']
      opm = parsed_each['M']
      opy = parsed_each['Y']

      name_dict = {}

      print(f'Retrieving content for date, {parsed_dash}:')
      name1 = f'{str(int(opm))}/{str(int(opd))}.txt' # M/D.txt
      name2 = f'{opm}/{opd}.txt' # MM/DD.txt
      name_dict = { 'name1': name1, 'name2': name2}

      command = command.replace('{date_input}', parsed_dash)
      httpobj = json.loads(command)

      print('Running http request -> ', end='')

      try:
        start = time.perf_counter()
        # -- http.client connection -- #
        parsed      = urllib.parse.urlparse(httpobj['url'])
        domain      = parsed.netloc
        path        = parsed.path + ('?' + parsed.query if parsed.query else '')
        body        = urllib.parse.urlencode(httpobj['data'])
        method      = httpobj['method'].upper() if 'method' in httpobj else 'POST'
        contenttype = 'application/x-www-form-urlencoded'

        if 'headers' in httpobj and 'Content-Type' in httpobj['headers']:
          contenttype = httpobj['headers']['Content-Type']

        headers = {
          'Content-Type'    : contenttype,
          'Content-Length'  : str(len(body)),
        }

        connection=http.client.HTTPSConnection(domain, timeout=5); 
        connection.request(method, path, body=body, headers=headers)
        response = connection.getresponse(); 
        output = response.read().decode('utf-8')
        status = response.status
        connection.close()
        # -- end http.client connection -- #
        elapsed = time.perf_counter() - start

        print(f'successful.')
        print(f'Total time: {elapsed} sec\n--')

        if 'save' in savef:
          if not output:
            print('Nothing to save. The content of the output is empty.')
          elif status == 200:
            save_content_to_log(meta.logs_dir, output, parsed_dash, name_dict, savef, False)
          else:
            print(f'Nothing to save. The server returned status: {status}.')
        else:
          if not output:
            print('Nothing to display. The content of the output is empty.')
          elif status == 200:
            print(output)
          else:
            print(f'Nothing to display. The server returned status: {status}.')

      except Exception as e:
        print(f'failed.\n--')
        print(f'Error: {e}')
      
      print('--')
    
    else:
      print("Please enter a valid date input for http options. Use 'man' for list of commands.")

  else:

    print(f'A valid json could not be found in {httpjson_file}.')



def save_content_to_log(logs_dir, content, date, name_dict, saveopt, append=False):
  """Operation to save given text content to log."""
  entries = content

  if saveopt in ('saveauto','autosave'):
    get_year       = date[0:4]
    save_log_file  = f"{logs_dir}{get_year}/{name_dict['name2']}" # name2 = MM/DD.txt
    # create the month directory if it doesn't already exist
    os.makedirs(os.path.dirname(save_log_file), exist_ok=True)
    with open(save_log_file, 'a' if append else 'w') as file:
      entries = '\n' + entries if append else entries
      file.write(entries)
    if append:
      print(f'Additional entries successfully appended to: {save_log_file}')
    else:
      print(f'Log file successfully saved at: {save_log_file}')

  elif saveopt[0:5] == 'save=':
    save_log_file = f'{logs_dir}{saveopt[5:]}'
    if save_log_file == logs_dir:
      print('Please enter a valid file name & path.')
    else:
      # create the month directory if it doesn't already exist
      os.makedirs(os.path.dirname(save_log_file), exist_ok=True)
      with open(save_log_file, 'a' if append else 'w') as file:
        entries = '\n' + entries if append else entries
        file.write(entries)
      if append:
        print(f'Additional entries successfully appended to: {save_log_file}')
      else:
        print(f'Log file successfully saved at: {save_log_file}')

  elif saveopt == 'save':
    opts = ['To save as a log, please use one of the following options:',
            "- saveauto:  to automatically save the log using it's name & date",
            "- save=YYYY/MM/DD.txt:  to manually specify the name & location."]
    print('\n'.join(opts))

  else:
    print(entries)


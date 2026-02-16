#!/usr/bin/env python3

import subprocess


def curl(url, headers = ''):
  # -- run curl via subprocess -- #
  
  curl_command = f'curl "{url}" -H "{headers}"'
  process = subprocess.run(curl_command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  output = process.stdout.decode('utf-8')
  error = process.stderr.decode('utf-8')
  if process.returncode == 0:
    return output
  else:
    return f'Error: {error}'

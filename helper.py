#!/usr/bin/env python3

# Originally written in bash & converted w/ ChatGPT.

v = "0.0.2"
help_text = """
Helper to create date files and month directories.

Usage:

  Helper         Command      Parent  Apply
  -----------------------------------------
  ./helper.py    makefiles    dir/
  ./helper.py    makedirs     dir/
  ./helper.py    makefiles    dir/    apply
  ./helper.py    makedirs     dir/    apply

"""

import sys, os

def make_files(directory, apply_flag):
  if apply_flag == "apply":
    print(f"Applying making files in {directory}")
    for i in range(1, 32):
      day = str(i).zfill(2)
      open(os.path.join(directory, f"{day}.txt"), 'a').close()
      print(f"touch {os.path.join(directory, f'{day}.txt')} applied")
  else:
    print(f"Mock-making files in {directory}")
    for i in range(1, 32):
      day = str(i).zfill(2)
      print(f"touch {os.path.join(directory, f'{day}.txt')}")

def make_dirs(directory, apply_flag):
  if apply_flag == "apply":
    print(f"Applying making dirs in {directory}")
    for i in range(1, 13):
      month = str(i).zfill(2)
      os.makedirs(os.path.join(directory, month), exist_ok=True)
      print(f"mkdir {os.path.join(directory, month)} applied")
  else:
    print(f"Mock-making dirs in {directory}")
    for i in range(1, 13):
      month = str(i).zfill(2)
      print(f"mkdir {os.path.join(directory, month)}")

def print_help():
  print(help_text)

def print_version():
  print(f"Version {v}")

def main():
  args = sys.argv[1:]
  if len(args) == 0:
    print("Use the help or -h command for proper usage.")
    return
  
  com = args[0]
  directory = args[1] if len(args) >= 2 else "./"
  apply_flag = args[2] if len(args) >= 3 else ""

  if com == "makefiles":
    make_files(directory, apply_flag)
  elif com == "makedirs":
    make_dirs(directory, apply_flag)
  elif com in ["help", "--help", "-h"]:
    print_help()
  elif com in ["version", "--version", "-v"]:
    print_version()
  else:
    print("Use the help or -h command for proper usage.")

if __name__ == "__main__":
  main()

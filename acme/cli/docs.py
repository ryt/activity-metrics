#!/usr/bin/env python3

__author__    = 'Ray (github.com/ryt)'
__github__    = 'https://github.com/ryt/activity-metrics'
__copyright__ = f'Copyright (C) 2024-2026 {__author__}'

# main docs

__manual__  = """
activity metrics: a tool to analyze & display personal activity statistics.
""" + __copyright__ + """
latest source & docs: """ + __github__ + """

Usage:

  Show log file statistics and list all found log files.
  ------------------------------------------------------
  Run       Command
  -------------------------
  ame       
  acme      (stats|-s)
  acme      (list-files|-l)


  Analyze entries for a specific date or today.
  ---------------------------------------------
  Run       Date
  ------------------------------------------
  acme      {date_input}
  acme      (M/D|M-D)
  acme      (Y-M-D|Y/M/D)
  acme      (M-D-Y|M/D/Y)
  acme      (today|tod|-t|yesterday|yest|-y)


  Generate a timesheet CSV file for a specific date. Create columns with categorize.
  ----------------------------------------------------------------------------------
  Run       Generate CSV      Date               Module Options
  ---------------------------------------------------------------
  acme      (gencsv|-g)       {date_input}
  acme      (gencsv|-g)       {date_input}       {module_options}


  Interface for the utility script. For list of commands, use 'acme util help'!
  -----------------------------------------------------------------------------
  Run       Utility           Input
  --------------------------------------------------------
  acme      (utility|util)    (arg1)      (arg2)    etc..
  acme      (utility|util)    (help|-h)
  acme      (utility|util)    (man)


  Run       Help Manual & About
  -----------------------------
  acme      man
  acme      (help|--help|-h)
  acme      (--version|-v)


Usage Help:

  If your log files aren't being read, remember by default acme looks for the ./logs/ directory in the current working directory. 
  To have your log files be read, you'll have to navigate (cd) into the parent of the logs directory and run the commands:

  ----------------------------------
  cd        /path/to/logs-or-parent/
  acme      {command}
  ----------------------------------

  However, if you want to explicitly set a ./logs/ directory or it's parent while running the command, you can use the second argument 
  to set a directory path (ending with a slash) add all other arguments after it.

  -------------------------------------------------
  acme      /path/to/logs-or-parent/      {command}
  -------------------------------------------------


"""

# docs for utils & integrations

__utils__ = """
This script provides helper tools and utilities for API connections. Commands can also be run using 'acme util'!
Read "Utilities.md" for related documentation. API tokens are required for connecting to external services.

Usage:

  Make Files: create default date files (01-31.txt) and default month directories (01-12/)
  ----------------------------------------------------------------------------------------
  <acme>  <Utility>        <Command>    <Parent>  <Apply>

  acme    (utility|util)   makefiles    dir/
                           makefiles    dir/      apply
                           makedirs     dir/
                           makedirs     dir/      apply


  Clean Logs: clean up the gen directory of generated csv logs older than 1 week.
  -------------------------------------------------------------------------------
  <acme>  <Utility>        <Command>

  acme    (utility|util)   cleangen


  HTTP Options: retrieve and save the output from an http(s) request (via json file) as a log file.
  -------------------------------------------------------------------------------------------------
  <acme>  <Utility>        <http>   <Command File>   <Date Input>     <Save/Filename>

  acme    (utility|util)   http     .acme_http.json       {date_input}
                           http     .acme_http.json       {date_input}     save=2026/01/01.txt
                           http     .acme_http.json       {date_input}     (saveauto|autosave)

  - The default name of the http json file is ".acme_http.json". It can be changed to any name.
  - Options: In the http json file, "{date_input}" can be used to insert the entered date input
    in a "YYYY-MM-DD" format anywhere in the keys or values. (e.g. {"url":"http://api.url/{date_input}"})
  - {date_input} can be any valid date input listed in the main manual ("acme --help").

  (API) Todoist Options: retrieve and save tasks that have valid log file names (e.g. 01/01.txt)
  ----------------------------------------------------------------------------------------------
  <acme>  <Utility>        <Todoist>   <Action>    <Id/Date/Keyword>      <Save/Filename>

  acme    (utility|util)   todoist     get-task    (12345|{date_input})
                           todoist     get-task    (12345|{date_input})   save=2024/01/01.txt
                           todoist     get-task    (12345|{date_input})   (saveauto|autosave)

  - {date_input} can be any valid date input listed in the main manual ("acme --help").

  (API) Garmin Options: merge garmin csv logs into gencsv logs of given year (plus today and yesterday if applicable).
  --------------------------------------------------------------------------------------------------------------------
  <acme>  <Utility>        <Garmin>    <Action>        <Year>

  acme    (utility|util)   garmin      merge-gencsv    {year}

"""


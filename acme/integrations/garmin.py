#!/usr/bin/env python3


import sys
import os
import re
import time
import json
import pydoc
import subprocess
import http.client
import pandas as pd
import urllib.parse

from datetime import datetime
from datetime import timedelta

from io import StringIO

from acme.core import macros


def garmin_options(args):

  now = datetime.now()
  yst = now - timedelta(days=1)

  action = args[1] if len(args) >= 2 else ''
  year   = args[2] if len(args) >= 3 else now.year

  cat_name = 'Garmin Athletics'

  gen_dir  = f'{os.path.abspath(os.curdir)}/gen'
  gen_csv_metrics = f'{gen_dir}/{year}.csv'
  gen_csv_garmin  = f'{gen_dir}/services/garmin/{year}-garmin-activities.csv'

  if action == 'merge-gencsv':
    try:
      with open(gen_csv_garmin, 'r', encoding='utf-8') as f:
        valid_garmin_csv = f.read()
        print(f'Validated: {gen_csv_garmin}')
    except Exception as e:
      return print(f"Invalid: '{gen_csv_garmin}' could not be processed or found.")
    try:
      with open(gen_csv_metrics, 'r', encoding='utf-8') as g:
        valid_metrics_csv = g.read()
        print(f'Validated: {gen_csv_metrics}')
        if not valid_metrics_csv:
          print(f"Notice: the file '{gen_csv_metrics}' is empty.")
    except Exception as e:
      return print(f"Invalid: '{gen_csv_metrics}' could not be processed or found.")

    if f and g and valid_metrics_csv:
      # -- prevent duplication: check if existing garmin data -- #
      if f',{cat_name},' in valid_metrics_csv:
        return print(f'Existing Garmin data found in csv. Re-try after running acme gencsv year command again.')

      df = pd.read_csv(StringIO(valid_metrics_csv)) # get metrics as dataframe

      converted_garmin_data = []
      gf = pd.read_csv(StringIO(valid_garmin_csv))
      gf = gf.fillna('') # empty: NaN -> ''
      for _, row in gf.iterrows():
        # --metrics cols--
        # Date Duration C1 C2 C3 C4 ... Description Hours Splits
        # --garmin cols--
        # startTimeLocal activityId activityName activityTypeName activityTypeId 
        # distanceMI duration avgSpeedMPH maxSpeedMPH avgPaceMinSecMI maxPaceMinSecMI 
        # averageHR maxHR description 
        d_ddt = pd.to_datetime(row['startTimeLocal']).strftime('%m/%d/%Y')
        d_dhr = pd.to_datetime(row['startTimeLocal']).strftime('%-I%p').lower().replace('am','a').replace('pm','p')
        d_hrs = round(pd.to_timedelta(row['duration']).total_seconds() / 3600, 2)
        d_dts = ' '.join([(f'{d}: {row[d]};' if row[d] else '') for d in ''.join((
          'startTimeLocal activityId activityTypeId distanceMI duration avgSpeedMPH maxSpeedMPH ',
          'avgPaceMinSecMI maxPaceMinSecMI averageHR maxHR description')).split(' ')])
        data = {
          'Date'        : d_ddt,
          'Duration'    : macros.hours_to_human(d_hrs, True),
          'Description' : f"{d_dhr} {row['activityName']}, Details: [{d_dts.strip()}]",
          'Hours'       : d_hrs,
        }
        data_c2 = row['activityTypeName'].replace('_', ' ').title()
        if 'C1' in df.columns and 'C2' in df.columns: # categorized vs non-categorized metrics csv
          data['C1'] = cat_name
          data['C2'] = data_c2
        else:
          data['Description'] = f"{data['Description']} ({cat_name}, {data_c2})"
        converted_garmin_data.append(data)

      cgd_df = pd.DataFrame(converted_garmin_data) # get converted_garmin_data (cgd) as dataframe
      cgd_df = cgd_df.reindex(columns=df.columns, fill_value='') # empty rows: NaN -> ''

      # metrics df: adjust footer -> remove total logged
      df = df[df['Description'] != 'Total Logged Hours']
      df = pd.concat([df, cgd_df], ignore_index=True)
      df = df.sort_values(by='Date', ascending=True)
      sum_hours = round(df['Hours'].sum(), 2)

      # final df: adjust footer -> add back total logged
      df.loc[len(df)] = { col: {
        'Duration'    : macros.hours_to_human(sum_hours, True),
        'Description' : 'Total Logged Hours',
        'Hours'       : sum_hours,
      }.get(col,'') for col in df.columns } # empty rows: NaN -> ''

      df.to_csv(gen_csv_metrics, index=False)

      # -- additional day csv mergers (today, yesterday) for current year -- #
      if str(year) == str(now.year):
        ymd_tod = (now.strftime('%Y-%m-%d'), now.strftime('%m/%d/%Y'))
        ymd_yst = (yst.strftime('%Y-%m-%d'), yst.strftime('%m/%d/%Y'))
        tod_csv = f'{gen_dir}/{ymd_tod[0]}.csv'
        yst_csv = f'{gen_dir}/{ymd_yst[0]}.csv'
        garmin_merge_daycsv(cgd_df, yst_csv, ymd_yst, cat_name)
        garmin_merge_daycsv(cgd_df, tod_csv, ymd_tod, cat_name)
      # -- end: additional day csv files -- #

      print(f'Successfully merged "{os.path.basename(gen_csv_garmin)}" -> "{os.path.basename(gen_csv_metrics)}" for the year {year}.')


def garmin_merge_daycsv(cgd_df, day_csv, ymd_day, cat_name):
  try:
    with open(day_csv, 'r', encoding='utf-8') as f:
      valid_csv = f.read()
      print(f'Validated: {day_csv}')
      fgd_df = cgd_df[cgd_df['Date'] == ymd_day[1]].copy() # filtered garmin data (fgd) dataframe
      if not fgd_df.empty and not f',{cat_name},' in valid_csv: # non-empty frame & no-duplicate
        # day csv metrics day_df modifications
        day_df = pd.read_csv(StringIO(valid_csv)) # get day metrics as dataframe
        fgd_df = fgd_df.reindex(columns=day_df.columns, fill_value='') # reindex fgd -> empty rows: NaN -> ''
        day_df = day_df[day_df['Description'] != 'Total Logged Hours'] # adjust footer -> remove total logged
        day_df = pd.concat([day_df, fgd_df], ignore_index=True) # merge day_df and fgd_df
        sum_hours = round(day_df['Hours'].sum(), 2)

        # final day_df: adjust footer -> add back total logged
        day_df.loc[len(day_df)] = { col: {
          'Duration'    : macros.hours_to_human(sum_hours, True),
          'Description' : 'Total Logged Hours',
          'Hours'       : sum_hours,
        }.get(col,'') for col in day_df.columns } # empty rows: NaN -> ''

        day_df.to_csv(day_csv, index=False)
        print(f' -> Successfully merged day csv: {day_csv}')
  except Exception as e:
    print(f"Invalid: '{day_csv}' could not be processed or found.")


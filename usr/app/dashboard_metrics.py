#!/usr/bin/env python3

"""Metrics Dashboard Module"""

"""
The Metrics dashboard module provides a web interface for analyzing and displaying metrics logs & data.
"""

# TODO: Idea inspirations from gyroscope -> https://gyrosco.pe/aprilzero/

import os
import re
import csv
import html
import traceback
import pandas as pd

from datetime import datetime, timedelta
from urllib.parse import urlparse
from flask import request
from io import StringIO

# date & time definitions

today = datetime.today()
today_f = (today.strftime('%Y-%m-%d'), today.strftime('%b %-d'), today.strftime('%m/%d')) # %b %-d, %Y

yest = today - timedelta(days=1)
yest_f = (yest.strftime('%Y-%m-%d'), yest.strftime('%b %-d'), yest.strftime('%m/%d'))

weekstart = today - timedelta(days=(today.weekday() + 1) % 7)
weekstart_f = (weekstart.strftime('%Y-%m-%d'), weekstart.strftime('%b %-d'), weekstart.strftime('%m/%d'))

monthstart = today.replace(day=1)
monthstart_f = (monthstart.strftime('%Y-%m-%d'), monthstart.strftime('%b %-d'), monthstart.strftime('%m/%d'))

year = today.strftime('%Y')
yearstart_f = (f'{year}-01-01', 'Jan 1', '01/01')


def get_query(param):
  """Get query string param (if exists & has value) or empty string"""
  try:
    return request.args.get(param) if request.args.get(param) else ''
  except:
    return ''

def query_link(params = {}):
  """Create a query string link with the dict"""
  add = ''
  if params:
    mod_params = {}
    for p in params:
      if params[p] == ':default:':
        val = get_query(p)
        if val:
          add += f'{p}={val}&'
      else:
        add += f'{p}={params[p]}&'

  add = add.rstrip('&')
  m = get_query('m')

  return f'?m={m}&{add}'.rstrip('&')


def webcsv_link(file):
  """Create a link to the file through webcsv (if installed & running)"""
  host = urlparse(request.url_root).hostname
  port = urlparse(request.url_root).port
  csvurl = gen_csv_file
  if port == 8100:
    preurl = f'http://{host}:8002'
  else:
    preurl = f'https://{host}/:8002'
    csvurl = csvurl.replace('/var/www/Metrics/Metrics/', '')

  return f'{preurl}/webcsv?f={csvurl}'


def html_return_error(text):
  return f'<div class="error">{text}</div>'

# data analysis functions

def create_periods(periods):
  html = ''
  for i, p in enumerate(periods):
    arrow = f'<a class="arrow" href="https://tools.redment.com/year?from={p["from"][2]}&to={p["to"][2]}" target="blank">&rarr;</a>'
    html += '<div>'
    if p['from'][1] == p['to'][1]:
      html += f"<b>{p['label']}:</b> {p['from'][1]} {arrow} <ul>"
    else:
      html += f"<b>{p['label']}:</b> {p['from'][1]} - {p['to'][1]} {arrow} <ul>"
    html += ''.join((
                    f"<li>Total work hours: {p['metrics']['total_miles_running']}</li>",
                    f"<li>Total project hours: {p['metrics']['total_miles_soccer']}</li>",
                    #f"<li>Combined soccer + running miles: {p['metrics']['total_miles_running_soccer']}</li>",
                    #f"<li>Total cycling miles: {p['metrics']['total_miles_cycling']}</li>",
                    #f"<li>Total strength training sets: {p['metrics']['total_sets']}</li>"
                  ))
    html += '</ul></div>'

  return html


def get_total_miles(df, start_date, end_date, qf=''):
  """Get the sum of distanceMI for qf (activity) (if not empty) from start_date through end_date"""

  # filter dataframe if qf is specified
  if qf:
    df = df_activity_filter(df, qf)

  #df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])

  # case for single date (i.e. start & end are the same)
  #if start_date == end_date:
  #  mask = (df['startTimeLocal'].dt.date == pd.to_datetime(start_date).date())
  # duration periods (2 or more)
  #else:
  #  mask = (df['startTimeLocal'].dt.date >= pd.to_datetime(start_date).date()) & (df['startTimeLocal'].dt.date <= pd.to_datetime(end_date).date())
  
  #filtered_df = df.loc[mask]

  #return round(filtered_df['distanceMI'].sum(), 2)
  return 0


def df_activity_filter(odf, qf):
  """Filter rows of data from df (DataFrame) using qf ('query filter' activity name)"""

  df = odf.copy() # copy odf / [o]riginal [df]

  #if qf == 'activity:soccer':
  #  df = df[df['activityName'].str.contains('TSC|CSL|Ski Beach', na=False)]
  #elif qf == 'activity:running':
  #  df = df[df['activityTypeName'].str.contains('running', na=False)]
  #elif qf == 'activity:strength':
  #  df = df[df['activityTypeName'].str.contains('strength', na=False)]
  #elif qf == 'activity:cycling':
  #  df = df[df['activityTypeName'].str.contains('cycling', na=False)]
  if qf == 'c1:music':
    df = df[df['C1'].str.contains('Music', na=False)]

  return df


def html_table_from_dataframe(df, apply_filters=False):
  """Create html table view from pandas dataframe of csv data"""

  # move date to column 1
  #df = df[ ['startTimeLocal'] + [ col for col in df.columns if col != 'startTimeLocal' ] ]

  if apply_filters:

    # ?filter=:filter:
    qf = get_query('filter')
    if qf == 'activity:soccer':
      df = df_activity_filter(df, 'activity:soccer')
    elif qf == 'activity:running':
      df = df_activity_filter(df, 'activity:running')
    elif qf == 'activity:strength':
      df = df_activity_filter(df, 'activity:strength')
    elif qf == 'activity:cycling':
      df = df_activity_filter(df, 'activity:cycling')
    elif qf == 'c1:music':
      df = df_activity_filter(df, 'c1:music')

    # ?periods=:period:
    qp = get_query('periods')
    if qp:
      qp_table = {
        'today'     : f'{today_f[0]},{today_f[0]}',
        'yesterday' : f'{yest_f[0]},{yest_f[0]}',
        'week'      : f'{weekstart_f[0]},{today_f[0]}',
        'month'     : f'{monthstart_f[0]},{today_f[0]}',
        'year'      : f'{yearstart_f[0]},{today_f[0]}',
      }
      if qp in qp_table:
        qp = qp_table[qp]
      else:
        qp = qp.replace('-', ',')
      qp_parts = qp.split(',')
      qp_parts = qp_parts if len(qp_parts) > 1 else (qp_parts[0], qp_parts[0])
      qp_from  = ''
      qp_to    = ''

      if re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', qp_parts[0]):
        qp_from = qp_parts[0] 
      elif re.match('^[0-9]{2}/[0-9]{2}$', qp_parts[0]):
        qp_from = datetime.strptime(f'{qp_parts[0]}/{year}', '%m/%d/%Y').strftime('%Y-%m-%d')

      if re.match('^[0-9]{4}-[0-9]{2}-[0-9]{2}$', qp_parts[1]):
        qp_to = qp_parts[1] 
      elif re.match('^[0-9]{2}/[0-9]{2}$', qp_parts[1]):
        qp_to = datetime.strptime(f'{qp_parts[1]}/{year}', '%m/%d/%Y').strftime('%Y-%m-%d')

      #if qp_from and qp_to:
      #  df['startTimeLocal'] = pd.to_datetime(df['startTimeLocal'])
      #  if qp_from == qp_to:
      #    mask = (df['startTimeLocal'].dt.date == pd.to_datetime(qp_from).date())
      #  else:
      #    mask = (df['startTimeLocal'].dt.date >= pd.to_datetime(qp_from).date()) & (df['startTimeLocal'].dt.date <= pd.to_datetime(qp_to).date())
      #  #mask = (df['startTimeLocal'] >= '2024-05-25') & (df['startTimeLocal'] <= '2024-05-29')
      #  df = df.loc[mask]


  csv_str = StringIO()
  df.to_csv(csv_str, index=False)
  csv_str.seek(0)  # Go back to the start of the StringIO object
  csv_content = csv_str.getvalue()

  html_table = '<table class="csv-table">\n'
  # added {skipinitialspace=True} to fix issue with commas inside quoted cells
  csv_reader = csv.reader(csv_content.splitlines(), skipinitialspace=True)
  headers = next(csv_reader)

  html_table += '<tr>'
  for header in headers:
    header = html.escape(header)
    html_table += f'<th>{header}</th>'
  html_table += '</tr>\n'

  for row in csv_reader:
    html_table += '<tr>'
    for cell in row:
      cell = html.escape(cell)
      html_table += f'<td>{cell}</td>'
    html_table += '</tr>\n'
    
  html_table += '</table>'

  return {
    'html'       : html_table,
    'total'      : len(df),
    'total_hrs'  : df[df['Description'] != 'Total Logged Hours']['Hours'].sum(),
  }

def ifxyz(x, y, z, default = ''):
  """Return z if x == y else default (or empty) string"""
  return z if x == y else default

# define metrics & log files
gen_dir       = f"{get_query('m').rstrip('/')}/gen/"
gen_csv_file  = ''

q = '"'

qf = get_query('filter')
qp = get_query('periods')

if qp == 'year' and os.path.isfile(f'{gen_dir}{year}.csv'):
  gen_csv_file  = f'{gen_dir}{year}.csv'
elif qp == 'month' and os.path.isfile(f'{gen_dir}{today.strftime("%Y-%m")}.csv'):
  gen_csv_file  = f'{gen_dir}{today.strftime("%Y-%m")}.csv'
else:
  if os.path.isfile(f'{gen_dir}{today_f[0]}.csv'):
    gen_csv_file  = f'{gen_dir}{today_f[0]}.csv'
  elif os.path.isfile(f'{gen_dir}{yest_f[0]}.csv'):
    gen_csv_file  = f'{gen_dir}{yest_f[0]}.csv'
  elif os.path.isfile(f"{(today - timedelta(days=2)).strftime('%Y-%m-%d')}.csv"):
    gen_csv_file  = f"{(today - timedelta(days=2)).strftime('%Y-%m-%d')}.csv"



# load & analyze data with pandas

if gen_csv_file:

  # Load the csv file as a DataFrame
  df = pd.read_csv(gen_csv_file)

  # define periods

  # custom calculations
  tod_total_miles_running = get_total_miles(df, today_f[0], today_f[0], 'activity:running')
  tod_total_miles_soccer = get_total_miles(df, today_f[0], today_f[0], 'activity:soccer')

  yest_total_miles_running = get_total_miles(df, yest_f[0], yest_f[0], 'activity:running')
  yest_total_miles_soccer = get_total_miles(df, yest_f[0], yest_f[0], 'activity:soccer')

  week_total_miles_running = get_total_miles(df, weekstart_f[0], today_f[0], 'activity:running')
  week_total_miles_soccer = get_total_miles(df, weekstart_f[0], today_f[0], 'activity:soccer')

  month_total_miles_running = get_total_miles(df, monthstart_f[0], today_f[0], 'activity:running')
  month_total_miles_soccer = get_total_miles(df, monthstart_f[0], today_f[0], 'activity:soccer')

  year_total_miles_running = get_total_miles(df, yearstart_f[0], today_f[0], 'activity:running')
  year_total_miles_soccer = get_total_miles(df, yearstart_f[0], today_f[0], 'activity:soccer')

  periods = [
    {
      'label' : 'Today',
      'from'  : (today_f[0], today_f[1], today_f[2]),
      'to'    : (today_f[0], today_f[1], today_f[2]),
      'metrics' : {
        'total_miles_running' : tod_total_miles_running,
        'total_miles_soccer' : tod_total_miles_soccer,
        #'total_miles_running_soccer' : tod_total_miles_running + tod_total_miles_soccer,
        #'total_miles_cycling' : get_total_miles(df, today_f[0], today_f[0], 'activity:cycling'),
        #'total_sets'  : '--'
      }
    },
    {
      'label' : 'Yesterday',
      'from'  : (yest_f[0], yest_f[1], yest_f[2]),
      'to'    : (yest_f[0], yest_f[1], yest_f[2]),
      'metrics' : {
        'total_miles_running' : yest_total_miles_running,
        'total_miles_soccer' : yest_total_miles_soccer,
        #'total_miles_running_soccer' : yest_total_miles_running + yest_total_miles_soccer,
        #'total_miles_cycling' : get_total_miles(df, yest_f[0], yest_f[0], 'activity:cycling'),
        #'total_sets'  : '--'
      }
    },
    {
      'label' : 'This week',
      'from'  : (weekstart_f[0], weekstart_f[1], weekstart_f[2]),
      'to'    : (today_f[0], today_f[1], today_f[2]),
      'metrics' : {
        'total_miles_running' : week_total_miles_running,
        'total_miles_soccer' : week_total_miles_soccer,
        #'total_miles_running_soccer' : week_total_miles_running + week_total_miles_soccer,
        #'total_miles_cycling' : get_total_miles(df, weekstart_f[0], today_f[0], 'activity:cycling'),
        #'total_sets'  : '--'
      }
    },
    {
      'label' : 'This month',
      'from'  : (monthstart_f[0], monthstart_f[1], monthstart_f[2]),
      'to'    : (today_f[0], today_f[1], today_f[2]),
      'metrics' : {
        'total_miles_running' : month_total_miles_running,
        'total_miles_soccer' : month_total_miles_soccer,
        #'total_miles_running_soccer' : month_total_miles_running + month_total_miles_soccer,
        #'total_miles_cycling' : get_total_miles(df, monthstart_f[0], today_f[0], 'activity:cycling'),
        #'total_sets'  : '--'
      }
    },
    {
      'label' : 'This year',
      'from'  : (yearstart_f[0], yearstart_f[1], yearstart_f[2]),
      'to'    : (today_f[0], today_f[1], today_f[2]),
      'metrics' : {
        'total_miles_running' : year_total_miles_running,
        'total_miles_soccer' : year_total_miles_soccer,
        #'total_miles_running_soccer' : round(year_total_miles_running + year_total_miles_soccer, 2),
        #'total_miles_cycling' : get_total_miles(df, yearstart_f[0], today_f[0], 'activity:cycling'),
        #'total_sets'  : '--'
      }
    }
  ]

  frame_table = html_table_from_dataframe(df, apply_filters=True)

  output_html = ''.join((

    f'<h3>Metrics {year}</h3>',
    create_periods(periods),

    '<table class="plain">',
     # note: the CSV link below requires/assumes webcsv being installed/used & running on the machine
     f'<td><h4 id="activities">Metrics CSV (<a href="{webcsv_link(gen_csv_file)}" target="_blank">{os.path.basename(gen_csv_file)}</a>)</h4></td>',
     f'<td><div class="filter-search">',
        '<table class="plain">',
         f'<td><input type="text" placeholder="c1:music,c2:practice" id="filter-query" value="{qf}"></td>',
          '<td><button id="filter-go">Go</button></td>',
        '</table>',
      '</div></td>',
    '</table>',

    '<div class="filters">',
       '<div class="filter-lists">',
         '<span class="dim">Filters:</span> ',
        f'<a href="{query_link({ "periods" : ":default:" })}#activities" class="{ifxyz(qf,"","bold")}">All</a>, ',
        f'<a href="{query_link({ "filter" : "activity:work", "periods" : ":default:" })}#activities" class="{ifxyz(qf,"activity:work","bold")}">Work</a>, ',
        f'<a href="{query_link({ "filter" : "activity:projects", "periods" : ":default:" })}#activities" class="{ifxyz(qf,"activity:projects","bold")}">Projects</a>, ',
        f'<a href="{query_link({ "filter" : "activity:study", "periods" : ":default:" })}#activities" class="{ifxyz(qf,"activity:study","bold")}">Study</a>, ',
        f'<a href="{query_link({ "filter" : "activity:practice", "periods" : ":default:" })}#activities" class="{ifxyz(qf,"activity:practice","bold")}">Practice</a>',
       '</div>',
    '</div>',

    '<div class="periods"> <span class="dim">Periods:</span> ',
    f'<a href="{query_link({ "filter" : ":default:" })}#activities" class="{ifxyz(qp,"","bold")}">All</a>, ',
    f'<a href="{query_link({ "filter" : ":default:", "periods" : "today" })}#activities" class="{ifxyz(qp,"today","bold")}">Today</a>, ',
    f'<a href="{query_link({ "filter" : ":default:", "periods" : "yesterday" })}#activities" class="{ifxyz(qp,"yesterday","bold")}">Yesterday</a>, ',
    f'<a href="{query_link({ "filter" : ":default:", "periods" : "week" })}#activities" class="{ifxyz(qp,"week","bold")}">This Week</a>, ',
    f'<a href="{query_link({ "filter" : ":default:", "periods" : "month" })}#activities" class="{ifxyz(qp,"month","bold")}">This Month</a>, ',
    f'<a href="{query_link({ "filter" : ":default:", "periods" : "year" })}#activities" class="{ifxyz(qp,"year","bold")}">This Year</a> ',
    '</div>',

    f'<div class="table-outer">{frame_table["html"]}</div>',
    f'<div class="details">Total: <b>{frame_table["total"]}</b>, <i>{round(frame_table["total_hrs"], 2)}hrs</i></div>'


    f'''

    <script type="text/javascript">

      var fquery = document.getElementById('filter-query');
      var fgo = document.getElementById('filter-go');

      function filterGo(){{
        var link = "{query_link({ "filter": f"{q} + fquery.value + {q}", "periods" : ":default:" })}#activities";
        window.location.href = link;
      }}

      fquery.addEventListener('keyup', function(e){{ if ( e.key === "Enter" ) {{ e.preventDefault(); filterGo(); }} }});
      fgo.addEventListener('click', filterGo);

    </script>

    ''',

  ))


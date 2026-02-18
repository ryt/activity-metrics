#!/usr/bin/env python3

# from acme.cli import cli

"""
List of commands to test:

acme
acme /path/to/metrics

acme ...
acme /path/to/metrics ...

acme stats
acme -s
acme list-files
acme -l

acme tod
acme yest
acme today
acme yesterday
acme 2025-08-29
acme 8/29/25
acme 2/3
acme -t
acme -y

acme gencsv
acme gencsv today
acme gencsv yesterday
acme gencsv today cat
acme gencsv yesterday cat
acme gencsv year
acme gencsv year cat
acme gencsv 2024 cat

acme utility
acme util
acme -u

acme util makefiles dir/
acme util makefiles dir/ apply
acme util makedirs  dir/
acme util makedirs  dir/ apply

acme util cleangen

acme util http /path/to/.acme_http.json today autosave
acme util http /path/to/.acme_http.json yest autosave
acme util http /path/to/.acme_http.json 02/17 autosave
acme util http /path/to/.acme_http.json {date_input}
acme util http /path/to/.acme_http.json {date_input} save=2026/01/01.txt
acme util http /path/to/.acme_http.json {date_input} (saveauto|autosave)

acme util todoist get-task (12345|{date_input})
acme util todoist get-task (12345|{date_input}) save=2024/01/01.txt
acme util todoist get-task (12345|{date_input}) (saveauto|autosave)

acme util garmin merge-gencsv {year}

acme dash
acme -d
acme dash dev
acme dash prod
acme dash prod list
acme dash prod reload
acme dash prod start
acme dash prod stop
acme dash prod debug

acme man
acme help
acme -h
acme --help

acme --version
acme -v

"""

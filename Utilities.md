## Utilities
Common utilities & commands for various applications. API access is required if applicable.

**Make Files:** create default date files (01-31.txt) and default month directories (01-12/)

```console
acme (utility|util)   makefiles    dir/
                      makefiles    dir/      apply
                      makedirs     dir/
                      makedirs     dir/      apply

```

**Clean Logs:** clean up the gen directory of generated csv logs older than 1 week.

```console
acme (utility|util)   cleangen
```

**HTTP Options:** retrieve and save the output from an http(s) request (via json file) as a log file.

```console
acme (utility|util)   http     .http_json       {date_input} 
                      http     .http_json       {date_input}     save=2026/01/01.txt
                      http     .http_json       {date_input}     (saveauto|autosave)

```
> - The default name of the http json file is (`.http_json`). It can be changed to any name.
> - Options: In the http json file, `{date_input}` can be used to insert the entered date input
> in a `YYYY-MM-DD` format anywhere in the keys or values. (e.g. `{"url":"http://api.url/{date_input}"}`)
> - `{date_input}` can be any valid date input listed in the main manual (`acme --help`).

Example `.http_json` file (located in `Metrics/app/.http_json`):

```json
{
  "url"     : "https://api.app.url/log?date={date_input}",
  "method"  : "POST",
  "data"    : {
    "Auth": "0f3x83ndja0dk3Dx03co28id983h3"
  }
}

```

### (API) Todoist

**Todoist Commands**

Retrieve and save Todoist tasks that have valid log file names (e.g. 01/01.txt)

> acme, Utility, Todoist, Action, Id/Date/Keyword, Save/Filename

```console
acme (utility|util) todoist get-task (12345|{date_input})
                    todoist get-task (12345|{date_input})   save=2024/01/01.txt
                    todoist get-task (12345|{date_input})   (saveauto|autosave)
```


### (API) Garmin

**Garmin Commands**

If Garmin csv logs exist, merge them into gencsv logs of given year (plus today and yesterday if applicable).
  
```console
acme (utility|util) garmin merge-gencsv {year}
```

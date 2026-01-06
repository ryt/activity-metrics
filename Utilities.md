## Utilities
Common utilities & workflows for various applications. API access is required if applicable.

### Todoist

**Todoist Commands**

Retrieve and save Todoist tasks that have valid log file names (e.g. 01/01.txt)

> acme, Utility, Todoist, Action, Id/Date/Keyword, Save/Filename

```
acme (utility|util) todoist get-task (12345|{date_input})
                    todoist get-task (12345|{date_input})   save=2024/01/01.txt
                    todoist get-task (12345|{date_input})   (saveauto|autosave)
```


### Garmin

**Garmin Commands**

If Garmin csv logs exist, merge them into gencsv logs of given year (plus today and yesterday if applicable).
  
```console
acme (utility|util) garmin merge-gencsv {year}
```

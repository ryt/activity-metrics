# Activity Metrics

Overview
--------
Activity Metrics is a text-based tracking and analysis tool for personal & business activity logs.

Logs can be formatted with custom grammar and be defined as schemas to be processed as data sources.

The data can then be converted to CSV and other formats. They can be used in Google Sheets, Excel, or other spreadsheet apps and work with data visualization tools for custom charts and reports.

**Basic Log Types:**

* Timesheets: (Work, Projects, Academics, Assignments)
* Fitness: (Workouts, Weight, Body Metrics)
* Nutrition: (Macros, Supplements, Diet)
* Finance: (Accounting, Balance Sheets, Investments)
* Business: (Inventory, Markets, Operations)

<h2 id="Installation"><small>Installation</small></h2>

### Manual Installation

1. Clone `activity-metrics/` into your local installation directory.

    ```console
    git clone https://github.com/ryt/activity-metrics.git
    ```
3. Create an alias or symbolic link to `acme.py` to access it directly in your terminal. There are multiple ways of doing this.

    **Option 1:** Symbolic Link
    
    ```console
    ln -s /path/to/activity-metrics/acme.py  /usr/bin/acme
    ```
    Depending on your system you may need to use `/usr/bin/`, `/opt/local/bin`, `/usr/share/bin/`, etc. You can also use your documents folder or a custom location as long as you use a symbolic link to the `acme.py` executable.
    
    **Option 2:** Creating an alias in `~/.bashrc`, `~/.bash_aliases` or `~/.bash_profile`:
    
    ```bash
    alias acme='/path/to/activity-metrics/acme.py'
    ```
    After editing the file make sure you restart your terminal or use the `source` command to reload the configuration.
    
    ```console
    source ~/.bashrc
    ```

### Setting up Workspace & Customization

A workspace is any folder that contains logs and data for analysis.

1. For a basic workspace, create a directory named `Metrics` or something similar in your Documents and create the following 3 directories in it: `apps`, `gen`, and `logs`.

    You can choose whatever name you want for the workspace but we'll use "Metrics" for this example. `apps` will be used for app modules, scripts, and extensions to the application, `gen` will be used for generated files (csv, etc.), and `logs` will be used to store log files.

    ```console
    mkdir Metrics && cd Metrics
    mkdir apps gen logs
    ```
    
    The structure of the basic workspace should look something like this:
    
    ```
    Metrics/
      - apps/
      - gen/
      - logs/
      - workspace_config.yaml
    ```
2. Now you can run the command `acme` from inside the `Metrics/` directory. Generated files will be stored inside `gen/` and your logs will be read and parsed from the `logs/`. Use `acme help` for the help manual.

    The utility script can be run as `acme util`. Use `acme util help` for the utility help manual.


## Utilities
Common utilities & commands for various applications. API access is required if applicable.

**Config Files:**

- The main application config file is stored in: `~/.acmeconf/acme_config.yaml`  
- The `~/.acmeconf/` directory is also used for API & integration config files.
- Workspace config files are stored inside the workspace as: `/path/to/workspace/workspace_config.yaml`

You can copy the default `.acmeconf/` template into your home directory from the tests directory found in `/path/to/activity-metrics/tests/.acmeconf/`.

```console
cp -r /path/to/activity-metrics/tests/.acmeconf/ ~/.acmeconf/
```

You can update settings for the web dashboard (`acme dash`) or [API](#api) integrations in `~/.acmeconf/acme_config.yaml`.

**Timesheet Util Helpers**

**Make Files:** create default date files (01-31.txt) and default month directories (01-12/)

```console
acme  util  makefiles    dir/
            makefiles    dir/      apply
            makedirs     dir/
            makedirs     dir/      apply

```

**Clean Logs:** clean up the gen directory of generated csv logs older than 1 week.

```console
acme  util  cleangen
```

<h3 id="api">API Options & Integrations</h3>

**HTTP Options:** retrieve and save the output from an http(s) request as a log file.

```console
acme  util  http    .api_json    {date_input}
            http    .api_json    {date_input}    save=2026/01/01.txt
            http    .api_json    {date_input}    (saveauto|autosave)

```
> - The default name of the http api file is (`.api_json`). It can be changed to any name.
> - The file contains a json dictionary of the http request data.
> - Options: In the http api file, `{date_input}` can be used to insert the entered date input
> in a `YYYY-MM-DD` format anywhere in the keys or values. (e.g. `{"url":"http://api.url/{date_input}"}`)
> - `{date_input}` can be any valid date input listed in the main manual (`acme --help`).

Example `.api_json` file (located in `~/.acmeconf/.api_json`):

```json
{
  "url"     : "https://api.app.url/log?date={date_input}",
  "method"  : "POST",
  "data"    : {
    "Auth": "0f3x83ndja0dk3Dx03co28id983h3"
  }
}

```

### Todoist

**Todoist Commands**

Retrieve and save Todoist tasks that have valid log file names (e.g. 01/01.txt)

> acme, Utility, Todoist, Action, Id/Date/Keyword, Save/Filename

```console
acme  util  todoist get-task (12345|{date_input})
            todoist get-task (12345|{date_input})   save=2024/01/01.txt
            todoist get-task (12345|{date_input})   (saveauto|autosave)
```

The Todoist api token is required and shoud be stored in `~/.acmeconf/.api_todoist`.

### Garmin

**Garmin Commands**

If Garmin csv logs exist, merge them into gencsv logs of given year (plus today and yesterday if applicable).
  
```console
acme  util  garmin merge-gencsv {year}
```

#### Development Notes

<i>Activity Metrics is an ongoing personal and business study project aimed at exploring various aspects of activity tracking. You can find a live workspace directory example at the [/ryt/Metrics](https://github.com/ryt/Metrics) repository.</i>

<i>This repository includes scripts, modules, and examples of personal and general activity logs across a range of categories. If you're interested in accessing it, please feel free to request access on GitHub.</i>


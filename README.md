# Activity Metrics

Overview
--------
Activity Metrics is a text-based tracking and analysis tool for personal logs. It creates CSV files from daily logs in a simple format. These files can be used in Google Sheets, Excel, or other spreadsheet apps and work with data visualization tools for custom charts and reports.

For installation & usage, you can navigate to the [installation](#Installation) section at the bottom. Here's a simple overview of the system.

The most basic activity log types that are supported are timesheet logs. Below is an overview of the file and folder structures for timesheet logs. 

### Basics: Timesheets

- A timesheet log is a  **.txt** file that holds timesheet entries for a particular day.
- An example entry could be `- 15m 8a guitar practice: minor chords`.
- An entry is a line that starts with a hyphen `-` or dot `.`.
- Everything else in the file gets ignored.
- There are no limits for the number of entries or files for a day.
- All logs (including their parent directories) are stored in the main `logs/` directory.

#### File Names & Location
In the above example, let's assume the date for the entry was **Jan 1, 2024**. Here are the basic rules:

- The log file would be named with the two-digit date number and a .txt extension: i.e. `01.txt`.
- Optional custom text after the date number is allowed (e.g. `01custom-text.txt`).
- The log would be inside the proper `YYYY/MM/` directory, in this case: `2024/01/01.txt`.
- And finally, the full path for the log would be: `../logs/2024/01/01.txt`.

#### Additional Options: Full Date Timesheet Logs
- For utility reasons, timesheet files are also allowed to be named in the `YYYY-MM-DD` format<sup>[1](#n1) [2](#n2)</sup>.
- For example: `2024-01-01.txt` or `2024-01-01custom-text.txt` would be valid full date timesheet logs.
- Since their name already includes the year & month, full date timesheet logs can be stored anywhere within `logs/`.

Example: valid directory structure for timesheet logs:

```
../logs/
  - 2024/
    - 01/
      - 01.txt
      - 02.txt
      - 02-finance.txt
    - 02/
  - 2023/
    - 2023-12-31-fitness.txt
    - 08/
    - 12/
      - 16ExamStudy.txt 
```

Additionally data can also be imported from other tracking services such as Todoist, Garmin, Apple Health, Samsung Health, Financial Services, and more. Data can also be read directly from the API's of those tracking services.

**Common Categories for Activity Metrics:**

* Work
* Finances
* Academics
* Assignments
* Projects
* Fitness
* Nutrition
* Lifestyle

<h2 id="Installation"><small>Installation</small></h2>

### Application Installation

1. Clone `activity-metrics/` into your local installation directory.

    ```console
    git clone https://github.com/ryt/activity-metrics.git
    ```
3. Create an alias or symbolic link to `acme.py` to access it directly in your terminal. There are multiple ways of doing this. Replace *{install}* with your local installation directory.

    **Option 1:** Symbolic Link
    
    ```console
    ln -s {install}/activity-metrics/acme.py  /usr/bin/acme
    ```
    Depending on your system you may need to use `/usr/bin/`, `/opt/local/bin`, `/usr/share/bin/`, etc. You can also use your documents folder or a custom location as long as you use a symbolic link to the `acme.py` executable.
    
    **Option 2:** Creating an alias in `~/.bashrc`, `~/.bash_aliases` or `~/.bash_profile`:
    
    ```bash
    alias acme='{install}/activity-metrics/acme'
    ```
    After editing the file make sure you restart your terminal or use the `source` command to reload the configuration.
    
    ```console
    source ~/.bashrc
    ```

### Setting up Log Files & Customization

1. To store your logs, create a directory named `Metrics` or something similar in your Documents and create the following 3 directories in it: `app`, `gen`, and `logs`.

    You can choose whatever name you want for the main folder but we'll use "Metrics" for this example. `app` will be used for application modules, API, & configuration files, `gen` will be used for generated files, and `logs` will be used to store log files.

    ```console
    mkdir Metrics && cd Metrics
    ```

    ```console
    mkdir app gen logs
    ```
    
    The structure of the link and directories should look something like this:
    
    ```
    Metrics/
      - app/
      - gen/
      - logs/
    ```
2. Now you can run the command `acme` from inside the `Metrics/` directory. Generated files will be stored inside `gen/` and your logs will be read and parsed from the `logs/`. Use `acme help` for the help manual.

    The utility script can be run as `acme util`. Use `acme util help` for the utility help manual.


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
acme (utility|util)   http     .acme_http.json       {date_input}
                      http     .acme_http.json       {date_input}     save=2026/01/01.txt
                      http     .acme_http.json       {date_input}     (saveauto|autosave)

```
> - The default name of the http json file is (`.acme_http.json`). It can be changed to any name.
> - Options: In the http json file, `{date_input}` can be used to insert the entered date input
> in a `YYYY-MM-DD` format anywhere in the keys or values. (e.g. `{"url":"http://api.url/{date_input}"}`)
> - `{date_input}` can be any valid date input listed in the main manual (`acme --help`).

Example `.acme_http.json` file (located in `Metrics/app/.acme_http.json`):

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



<h2><small>Notes</small></h2>

Some of the inspirations for this project:

* <https://en.wikipedia.org/wiki/Help:Page_history>
* <https://en.wikipedia.org/wiki/Version_control>
* <https://calnewport.com/deep-habits-should-you-track-hours-or-milestones/>
* <https://archive.is/h3dz5>
* <https://gyrosco.pe/about/mission/>
* <https://jeffhuang.com/productivity_text_file/>
* <https://todoist.com/inspiration/deep-work>
* <https://en.wikipedia.org/wiki/Blue-green_deployment>

<h2><small>References</small></h2>

1. <i id="n1"></i> <https://en.wikipedia.org/wiki/ISO_8601>
2. <i id="n2"></i> <https://xkcd.com/1179/>




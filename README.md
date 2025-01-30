# Activity Metrics

Overview
--------
Activity Metrics is a tool that can be used to track and manage personal activity statistics. The app creates CSV files from daily logs that have a simple formatting style. The CSV data can be used in Google Sheets, Excel, or be processed by data visualization libraries to for custom textual and graphical needs.

For installation & usage, you can navigate to the [installation](#Installation) section at the bottom. Here's a simple overview of the system.

### Basics

- A log is a  **.txt** file that holds the entries for a particular day.
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

#### Additional Options: Full Date Log Files
- For utility reasons, log files are also allowed to be named in the `YYYY-MM-DD` format<sup>[1](#n1) [2](#n2)</sup>.
- For example: `2024-01-01.txt` or `2024-01-01custom-text.txt` would be valid full date logs.
- Since their name already includes the year & month, full date logs can be stored anywhere within `logs/`.

Valid location structure example:

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

<h2><small>Refrences</small></h2>

1. <i id="n1"></i> <https://en.wikipedia.org/wiki/ISO_8601>
2. <i id="n2"></i> <https://xkcd.com/1179/>


<h2><small>License</small></h2>
<sub>Copyright &copy; 2024 Ray Mentose.</sub>

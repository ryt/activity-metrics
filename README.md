Personal Analytics Manager
==========================

Overview
--------
Personal analytics manager is a tool that can analyze, organize, and render personal and professional statistics. The app works by parsing daily log files with simple formatting. The data can then be converted into spreadsheets and other usable formats. The app can also render beautiful textual and graphical data displays that can be used for both personal and professional projects.

Analytics logs are text files with rows of entries for a particular day. An example entry could be `- 8am 10m breakfast & coffee`. An entry always starts with a hyphen on a new line. There are no limits for the number of entries for a day.

In the above example, if the date for the entry was **Jan 1, 2024**, the location of the log file would be `2024/01/01.txt`. Each log file is named accoring to the date number of the day. Optional custom text after the date number is allowed (e.g. `01abc.txt`). For proper usage, files must be inside of "month" and "year" directories that correspond to the correct dates, respectively. In this example, both of these files would be valid: `2024/01/01.txt` or `2024/01/01abc.txt`.

Additionally, for the sake of convenience and practicality, a file also can be named in the `YYYY-mm-dd.txt` format<sup>[1](#n1) [2](#n2)</sup> (e.g. `2024-01-01.txt` or `2024-01-01abc.txt`). These files can be parsed from anywhere within the logs directory.

Valid structure example:

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
      - 16LSATstudy.txt 
```

Additionally data files can also be imported from other tracking services such as Todoist, Garmin, Apple Health, Samsung Health, Financial Services, and more. Data can also be read directly from the API's of those tracking services.

**Common Categories for Analytics:**

* Work
* Projects
* Finances
* Fitness
* Academics
* Nutrition
* Lifestyle


Inspirations
------------
List of authors and organizations who inspired this project:

* [Cal Newport, Bestselling Author & Assoc. Prof. of CS @ Georgetown University](https://calnewport.com/deep-habits-should-you-track-hours-or-milestones/)
* [Stephen Wolfram, Founder & CEO of Wolfram Research](https://web.archive.org/web/20140608105232/http://www.wired.com/2012/03/opinion-wolfram-life-analytics/all/)
* [Jeff Huang, Researcher & Assoc. Prof. of CS @ Brown University](https://jeffhuang.com/productivity_text_file/)
* [Todoist / Doist, Company Specializing in Productivity Tools](https://todoist.com/inspiration/deep-work)


Notes
-----
1. <span id="n1">[ISO 8601 Format](https://en.wikipedia.org/wiki/ISO_8601)</span>
2. <span id="n2">[XKCD 1179](https://xkcd.com/1179/)</span>


License
-------
<small>Copyright &copy; 2024 Ray Mentose.</small>
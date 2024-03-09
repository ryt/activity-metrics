Personal Analytics Manager
==========================

Overview
--------
Personal analytics manager is a tool that can analyze, organize, and render personal and professional statistics. The app works by parsing daily log files with a simple formatting style. The data can then be converted into spreadsheets and other useful formats. The tool can also render beautiful textual and graphical data displays that can be used for both personal and professional projects.

### Basics

- Analytics logs are text files with rows of entries for a particular day.
- An example entry could be `- 8am 10m breakfast & coffee`.
- An entry always starts with a hyphen on a new line.
- There are no limits for the number of entries for a day.
- The `logs/` directory is the parent directory for all logs & related folders.

#### File Names & Location
In the above example, let's assume the date for the entry was **Jan 1, 2024**. Here are the basic rules:

- The location of the log file would be `2024/01/01.txt`.
- Each log file is named accoring to the date number of the day.
- Optional custom text after the date number is allowed (e.g. `01abc.txt`). 
- For proper usage, files must be inside of **month** and **year** directories that correspond to the correct dates, respectively.
- In this example, both of these files would be valid: `2024/01/01.txt` or `2024/01/01abc.txt`.

#### Full Date Log Files
- Additionally, for the sake of utility, log files can also be named in the `YYYY-mm-dd.txt` format<sup>[1](#n1) [2](#n2)</sup>.
- For example: `2024-01-01.txt` or `2024-01-01abc.txt` would be valid log files.
- Full date log files can be parsed from anywhere within the `logs/` directory.

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
* Finances
* Academics
* Projects
* Fitness
* Nutrition
* Lifestyle


<h2><small>Inspirations</small></h2>

List of inspirations for this project:

* "[Deep Habits: Should You Track Hours or Milestones?](https://calnewport.com/deep-habits-should-you-track-hours-or-milestones/)", *Article by Cal Newport, Author & Assoc. Prof. of CS @ Georgetown University*
* "[The Personal Analytics of My Life](https://web.archive.org/web/20140608105232/http://www.wired.com/2012/03/opinion-wolfram-life-analytics/all/)", *Op-Ed by Stephen Wolfram, Founder & CEO of Wolfram Research*
* "[My productivity app is a never-ending .txt file](https://jeffhuang.com/productivity_text_file/)", *Article by Jeff Huang, Researcher & Assoc. Prof. of CS @ Brown University*
* [The Complete Guide to Deep Work](https://todoist.com/inspiration/deep-work), *Guide by Todoist / Doist, Company Specializing in Productivity Tools*


<h2><small>Notes</small></h2>

1. <i id="n1"></i> [ISO 8601 Format](https://en.wikipedia.org/wiki/ISO_8601)
2. <i id="n2"></i> [XKCD 1179](https://xkcd.com/1179/)


<h2><small>License</small></h2>
<small>Copyright &copy; 2024 Ray Mentose.</small>

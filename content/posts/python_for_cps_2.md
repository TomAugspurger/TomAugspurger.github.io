---
title: Using Python to tackle the CPS (Part 2)
date: 2014-02-04T12:00:00
slug: tackling-the-cps-2
category: python
tags:
  - pandas
aliases:
  /tackling-the-cps-2.html
---

[Last time](http://tomaugspurger.github.io/blog/2014/01/27/tackling%20the%20cps/), we used Python to fetch some data from the [Current Population Survey](http://www.census.gov/cps/). Today, we'll work on parsing the files we just downloaded.

---

We downloaded two types of files last time:

- CPS monthly tables: a fixed-width format text file with the actual data
- Data Dictionaries: a text file describing the layout of the monthly tables

Our goal is to parse the monthly tables. Here's the first two lines from the unzipped January 1994 file:

```bash
/V/H/U/t/D/C/monthly head -n 2 cpsb9401
881605952390 2  286-1 2201-1 1 1 1-1 1 5-1-1-1  22436991 1 2 1 6 194 2A61 -1 2 2-1-1-1-1 363 1-15240115 3-1 4 0 1-1 2 1-1660 1 2 2 2 6 236 2 8-1 0 1-1 1 1 1 2 1 2 57 57 57 1 0-1 2 5 3-1-1 2-1-1-1-1-1 2-1-1-1-1-1-1-1-1-1-1-1 -1-1-1-1-1-1-1-1-1-1-1 -1-1  169-1-1-1-1-1-1-1-1-1-1-1-1-1-1 -1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 -1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 2-1 0 4-1-1-1-1-1-1 -1-1-1 0 1 2-1-1-1-1-1-1-1-1-1 -1 -1-1-1 -1 -1-1-1 0-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 0-1-1-1-1-1  -1  -1  -1  0-1-1      0-1-1-1      -1      0-1-1-1-1-1-1-1-1 2-1-1-1-1  22436991        -1         0  22436991  22422317-1         0 0 0 1 0-1 050 0 0 0 011 0 0 0-1-1-1-1 0 0 0-1-1-1-1-1-1 1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 1 1 1 1 1 1 1 1 1 1 1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 1 1 1-1-1-1
881605952390 2  286-1 2201-1 1 1 1-1 1 5-1-1-1  22436991 1 2 1 6 194 2A61 -1 2 2-1-1-1-1 363 1-15240115 3-1 4 0 1-1 2 3-1580 1 1 1 1 2 239 2 8-1 0 2-1 1 2 1 2 1 2 57 57 57 1 0-1 1 1 1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 2-140-1-1 40-1-1-1-1 2-1 2-140-1 40-1   -1 2 5 5-1 2 3 5 2-1-1-1-1-1-1 -1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 -1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 1-118 1 1 1 4-1-1-1 -1 1-1 1 2-1-1-1-1-1-1-1 4 1242705-1-1-1 -1  3-1-1 1 2 4-1 1 6-1 6-136-1 1 4-110-1 3 1 1 1 0-1-1-1-1  -1-1  -1  -1  0-1-1      0-1-1-1            -10-1-1-1-1-1-1-1-1-1-1-1-1-1  22436991        -1         0  31870604  25650291-1         0 0 0 1 0-1 0 1 0 0 0 0 0 0 0 0-1-1-1-1 0 0-1 1 1 0 1 0 1 1 0 1 1 1 0 1 0 1 1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 0 0 0-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1
```

Clearly, we'll need to parse the data dictionaries before being able to make sense of that.

Keeping with the CPS's tradition of consistently being inconsistent, the data dictionaries don't have a consistent schema across the years. Here's a typical example for some years (this one is from January 2003):

```
NAME         SIZE  DESCRIPTION                          LOCATION

HRHHID          15     HOUSEHOLD IDENTIFIER   (Part 1)             (1 - 15)

                   EDITED UNIVERSE: ALL HHLD's IN SAMPLE

                   Part 1. See Characters 71-75 for Part 2 of the Household Identifier.
                   Use Part 1 only for matching backward in time and use in combination
                   with Part 2 for matching forward in time.
```

My goal was to extract 4 fields (`name`, `size`, `start`, `end`). Name and size could be taken directly (`HRHHID`, and `15`). `start` and `end` would be pulled from the `LOCATION` part.

In [`generic_data_dictionary_parser`](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/generic_data_dictionary_parser.py), I define a class do this. The main object `Parser`, takes

- `infile`: the path to a data dictionary we downloaded
- `outfile`: path to an [HDF5](http://pandas.pydata.org/pandas-docs/dev/io.html#hdf5-pytables) file
- `style`: A string representing the year of the data dictionary. Different years are formatted differently, so I define a style for each (3 styles in all)
- `regex`: This was mostly for testing. If you don't pass a `regex` it will be inferred from the style.

The heart of the parser is a regex that matches on lines like `HRHHID          15     HOUSEHOLD IDENTIFIER   (Part 1)             (1 - 15)`, but nowhere else. After many hours, failures, and false positives, I came up with something roughly like `ur'[\x0c]{0,1}(\w+)[\s\t]*(\d{1,2})[\s\t]*(.*?)[\s\t]*\(*(\d+)\s*-\s*(\d+)\)*$'` [Here's](http://regex101.com/r/uH5iH7) an explanation, but the gist is that

- `\w+` matches words (like `HRHHID`)
- there's some spaces or tabs `[\s\t]*` (yes the CPS mixes spaces and tabs) between that and...
- size `\d{1,2}` which is 1 or two columns digits
- the description which we don't really care about
- the start and end positions `(*(\d+)\s*-\s*(\d+)\)*$` broken into two groups.

Like I said, that's the heart of the parser. Unfortunately I had to pad the file with some 200+ more lines of code to handle special cases, formatting, and mistakes in the data dictionary itself.

The end result is a nice `HDFStore`, with a parsed version of each data dictionary looking like:
```
         id  length  start  end
0    HRHHID      15      1   15
1   HRMONTH       2     16   17
2   HRYEAR4       4     18   21
3  HURESPLI       2     22   23
4   HUFINAL       3     24   26
         ...     ...    ...  ...

```

This can be used as an argument pandas' [`read_fwf`](http://pandas.pydata.org/pandas-docs/dev/io.html#files-with-fixed-width-columns) parser.

Next time I'll talk about actually parsing the tables and wrangling them into a usable structure. After that, we will finally get to actually analyzing the data.

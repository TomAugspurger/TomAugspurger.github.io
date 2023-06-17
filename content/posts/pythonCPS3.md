---
title: Using Python to tackle the CPS (Part 3)
date: 2014-05-19T12:00:00
slug: tackling-the-cps-3
category: python
tags:
  - pandas
aliases:
  - /tackling-the-cps-3.html
---

In <a href="http://tomaugspurger.net/blog/2014/02/04/tackling%20the%20cps%20(part%202)/">part 2</a> of this series, we set the stage to parse the data files themselves.

As a reminder, we have a dictionary that looks like

```python

         id  length  start  end
0    HRHHID      15      1   15
1   HRMONTH       2     16   17
2   HRYEAR4       4     18   21
3  HURESPLI       2     22   23
4   HUFINAL       3     24   26
         ...     ...    ...  ...
```

giving the columns of the raw CPS data files. This post (or two) will describe the reading of the actual data files, and the somewhat tricky process of matching individuals across the different files. After that we can (finally) get into analyzing the data. The old joke is that statisticians spend 80% of their time munging their data, and 20% of their time complaining about munging their data. So 4 posts about data cleaning seems reasonable.

The data files are stored in fixed width format (FWF), one of the least human friendly ways to store data.
We want to get to an [HDF5](http://www.hdfgroup.org/HDF5/) file, which is extremely fast and convinent with pandas.

Here's the first line of the raw data:

```
head -n 1 /Volumes/HDD/Users/tom/DataStorage/CPS/monthly/cpsb9401
881605952390 2  286-1 2201-1 1 1 1-1 1 5-1-1-1  22436991 1 2 1 6 194 2A61 -1 2 2-1-1-1-1 363 1-15240115 3-1 4 0 1-1 2 1-1660 1 2 2 2 6 236 2 8-1 0 1-1 1 1 1 2 1 2 57 57 57 1 0-1 2 5 3-1-1 2-1-1-1-1-1 2-1-1-1-1-1-1-1-1-1-1-1 -1-1-1-1-1-1-1-1-1-1-1 -1-1  169-1-1-1-1-1-1-1-1-1-1-1-1-1-1 -1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 -1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 2-1 0 4-1-1-1-1-1-1 -1-1-1 0 1 2-1-1-1-1-1-1-1-1-1 -1 -1-1-1 -1 -1-1-1 0-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 0-1-1-1-1-1  -1  -1  -1  0-1-1      0-1-1-1      -1      0-1-1-1-1-1-1-1-1 2-1-1-1-1  22436991        -1         0  22436991  22422317-1         0 0 0 1 0-1 050 0 0 0 011 0 0 0-1-1-1-1 0 0 0-1-1-1-1-1-1 1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 1 1 1 1 1 1 1 1 1 1 1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1-1 1 1 1-1-1-1
```

We'll use pandas' [`read_fwf`](http://pandas.pydata.org/pandas-docs/version/0.13.0/generated/pandas.io.parsers.read_fwf.html#pandas.io.parsers.read_fwf) parser, passing in the widths we got from last post.
One note of warning, the `read_fwf` function is slow. It's written in plain python, and really makes you appreciate [all the work](http://wesmckinney.com/blog/?p=543) Wes (the creater or pandas) put into making `read_csv` fast.

Start by looking at the `__main__` [entry point](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/make_hdf_store.py#L786). The basic idea is to call `python make_hdf.py` with an optional argument giving a file with a specific set of months you want to process. Otherwise, it processes every month in your data folder. There's a bit of setup to make sure everything is order, and then we jump to the [next important line](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/make_hdf_store.py#L813):

```python
for month in months:
    append_to_store(month, settings, skips, dds, start_time=start_time)
```

I'd like to think that [this function](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/make_hdf_store.py#L725) is fairly straightforward. We generate the names I use internally (`name`), read in the data dictionary that we parsed last time (`dd` and `widths`), and get to work reading the actual data with

```python
df = pd.read_fwf(name + '.gz', widths=widths,
                 names=dd.id.values, compression='gzip')
```

Rather than stepping through every part of the processing (checking types, making sure indexes are unique, handling missing values, etc.) I want to focus on one specific issue: handling special cases. Since the CPS data aren't consistent month to month, I needed a way transform the data for certain months differently that for others. The design I came up with worked pretty well.

The solution is in [`special_by_dd`](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/make_hdf_store.py#L603). Basically, each data dictionary (which describes the data layout for a month) has its own little quirks.
For example, the data dictionary starting in January 1989 spread the two digits for age across two fields. The fix itself is extremely simple: `df["PRTAGE"] = df["AdAGEDG1"] * 10 + df["AdAGEDG2"]`, but knowing when to apply this fix, and how to apply several of these fixes is the interesting part.

In [`special_by_dd`](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/make_hdf_store.py#L603), I created a handful of closures (basically just functions inside other functions), and a dictionary mapping names to those functions.

```python
func_dict = {"expand_year": expand_year, "combine_age": combine_age,
             "expand_hours": expand_hours, "align_lfsr": align_lfsr,
             "combine_hours": combine_hours}
```

Each one of these functions takes a DataFrame and returns a DataFrame, with the fix applied. The example above is `combine_age`.
In a settings file, I had a JSON object mapping the data dictionary name to special functions to apply. For example, January 1989's special case list was:

```
"jan1989": ["expand_year", "combine_age", "align_lfsr", "expand_hours", "combine_hours"]
```

I get the necessary special case functions and apply each with

```
specials = special_by_dd(settings["special_by_dd"][dd_name])
for func in specials:
    df = specials[func](df, dd_name)
```

`specials` is just `func_dict` from above, but filtered to be only the functions specified in the settings file.
We select the function from the dictionary with `specials[func]` and then directly call it with `(df, dd_name)`.
Since functions are objects in python, we're able to store them in dictionaries and pass them around like just about anything else.

This method gave a lot of flexibility. When I discovered a new way that one month's layout differed from what I wanted, I simply wrote a function to handle the special case, added it to `func_dict`, and added the new special case to that month's speical case list.

There's a bit more standardization and other boring stuff that gets us to a good place: each month with the same layout. Now we get get to the tricky alignment, which I'll save for another post.

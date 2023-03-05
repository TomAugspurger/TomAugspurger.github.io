---
title: Using Python to tackle the CPS (Part 4)
date: 2014-05-19T12:01:00
slug: tackling-the-cps-4
category: python
tags:
  - pandas
aliases:
  - /tackling-the-cps-4.html
---

Last time, we got to where we'd like to have started: One file per month, with each month laid out the same.

As a reminder, the CPS interviews households 8 times over the course of 16 months. They're interviewed for 4 months, take 8 months off, and are interviewed four more times. So if your first interview was in month $m$, you're also interviewed in months $$m + 1, m + 2, m + 3, m + 12, m + 13, m + 14, m + 15$$.

I stored the data in [Panels](http://pandas-docs.github.io/pandas-docs-travis/dsintro.html#panel), the less well-known, higher-dimensional cousin of the [DataFrame](http://pandas.pydata.org/pandas-docs/version/0.13.1/generated/pandas.DataFrame.html). Panels are 3-D structures, which is great for this kind of data. The three dimensions are

1. items: Month in Survey (0 - 7)
2. fields: Things like employment status, earnings, hours worked
3. id: An identifier for each household

Think of each item as a 2-D slice (a DataFrame) into the 3-D Panel. So each household is described by a single Panel (or 8 DataFrames).

The actual panel construction occurs in [`make_full_panel`](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/make_panel.py#L151). Given a starting month, it figures out the months needed to generate that wave's Panel ($m, m + 1, m + 2, \ldots$), and stores these in an iterator called `dfs`.
Since each month on disk contains people from 8 different waves (first month, second month, ...), I filter down to just the people in their $i^{th}$ month in the survey, where $i$ is the month I'm interested in.
Everything up until this point is done lazily; nothing has actually be read into memory yet.

Now we'll read in each month, storing each month's DataFrame in a dictionary, `df_dict`. We take the first month as is.
Each subsequent month has to be matched against the first month.

```python
    df_dict = {1: df1}
    for i, dfn in enumerate(dfs, 2):
        df_dict[i] = match_panel(df1, dfn, log=settings['panel_log'])
    # Lose dtype info here if I just do from dict.
    # to preserve dtypes:
    df_dict = {k: v for k, v in df_dict.iteritems() if v is not None}
    wp = pd.Panel.from_dict(df_dict, orient='minor')
    return wp
```

In an ideal world, we just check to see if the indexes match (the unique identifier). However, the unique ID given by the Census Bureau isn't so unique, so we use some heuristics to guess if the person is actually the same as the one interviewed next week. `match_panel` basically checks to see if a person's race and gender hasn't changed, and that their age has changed by less than a year or so.

There's a bit more code that handles special cases, errors, and the writing of the output.
I was especially interested in earnings data, so I wrote that out separately.
But now we're finally to the point where we can do some analysis:

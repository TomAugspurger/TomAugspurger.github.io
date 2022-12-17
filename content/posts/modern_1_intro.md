---
Title: Modern Pandas (Part 1)
Date: 2016-03-21
Slug: modern-1-intro
tags:
  - pandas
---

---

This is part 1 in my series on writing modern idiomatic pandas.

- [Modern Pandas](modern-1-intro)
- [Method Chaining](method-chaining)
- [Indexes](modern-3-indexes)
- [Fast Pandas](modern-4-performance)
- [Tidy Data](modern-5-tidy)
- [Visualization](modern-6-visualization)
- [Time Series](modern-7-timeseries)
- [Scaling](modern-8-scaling)

---

# Effective Pandas

## Introduction

This series is about how to make effective use of [pandas](http://pandas.pydata.org), a data analysis library for the Python programming language.
It's targeted at an intermediate level: people who have some experience with pandas, but are looking to improve.

## Prior Art

There are many great resources for learning pandas; this is not one of them.
For beginners, I typically recommend [Greg Reda's](https://twitter.com/gjreda) [3-part introduction](http://gregreda.com/2013/10/26/intro-to-pandas-data-structures/), especially if they're familiar with SQL. Of course, there's the pandas [documentation](http://pandas.pydata.org/) itself. I gave [a talk](https://www.youtube.com/watch?v=otCriSKVV_8) at PyData Seattle targeted as an introduction if you prefer video form. Wes McKinney's [Python for Data Analysis](http://shop.oreilly.com/product/0636920023784.do) is still the goto book (and is also a really good introduction to NumPy as well). Jake VanderPlas's [Python Data Science Handbook](http://shop.oreilly.com/product/0636920034919.do), in early release, is great too.
Kevin Markham has a [video series](http://www.dataschool.io/easier-data-analysis-with-pandas/) for beginners learning pandas.

With all those resources (and many more that I've slighted through omission), why write another? Surely the law of diminishing returns is kicking in by now.
Still, I thought there was room for a guide that is up to date (as of March 2016) and emphasizes idiomatic pandas code (code that is *pandorable*).
This series probably won't be appropriate for people completely new to python
or NumPy and pandas.
By luck, this first post happened to cover topics that are relatively introductory,
so read some of the linked material and come back, or [let me know](https://twitter.com/tomaugspurger) if you
have questions.

## Get the Data

We'll be working with [flight delay data](http://www.transtats.bts.gov/databases.asp?Mode_ID=1&Mode_Desc=Aviation&Subject_ID2=0) from the BTS (R users can install Hadley's [NYCFlights13](https://github.com/hadley/nycflights13) dataset for similar data.




```python
import os
import zipfile

import requests
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

if int(os.environ.get("MODERN_PANDAS_EPUB", 0)):
    import prep
```


```python
import requests

headers = {
    'Referer': 'https://www.transtats.bts.gov/DL_SelectFields.asp?Table_ID=236&DB_Short_Name=On-Time',
    'Origin': 'https://www.transtats.bts.gov',
    'Content-Type': 'application/x-www-form-urlencoded',
}

params = (
    ('Table_ID', '236'),
    ('Has_Group', '3'),
    ('Is_Zipped', '0'),
)

with open('modern-1-url.txt', encoding='utf-8') as f:
    data = f.read().strip()

os.makedirs('data', exist_ok=True)
dest = "data/flights.csv.zip"

if not os.path.exists(dest):
    r = requests.post('https://www.transtats.bts.gov/DownLoad_Table.asp',
                      headers=headers, params=params, data=data, stream=True)

    with open("data/flights.csv.zip", 'wb') as f:
        for chunk in r.iter_content(chunk_size=102400): 
            if chunk:
                f.write(chunk)
```

That download returned a ZIP file.
There's an open [Pull Request](https://github.com/pydata/pandas/pull/12175) for automatically decompressing ZIP archives with a single CSV,
but for now we have to extract it ourselves and then read it in.


```python
zf = zipfile.ZipFile("data/flights.csv.zip")
fp = zf.extract(zf.filelist[0].filename, path='data/')
df = pd.read_csv(fp, parse_dates=["FL_DATE"]).rename(columns=str.lower)

df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 450017 entries, 0 to 450016
    Data columns (total 33 columns):
    fl_date                  450017 non-null datetime64[ns]
    unique_carrier           450017 non-null object
    airline_id               450017 non-null int64
    tail_num                 449378 non-null object
    fl_num                   450017 non-null int64
    origin_airport_id        450017 non-null int64
    origin_airport_seq_id    450017 non-null int64
    origin_city_market_id    450017 non-null int64
    origin                   450017 non-null object
    origin_city_name         450017 non-null object
    dest_airport_id          450017 non-null int64
    dest_airport_seq_id      450017 non-null int64
    dest_city_market_id      450017 non-null int64
    dest                     450017 non-null object
    dest_city_name           450017 non-null object
    crs_dep_time             450017 non-null int64
    dep_time                 441476 non-null float64
    dep_delay                441476 non-null float64
    taxi_out                 441244 non-null float64
    wheels_off               441244 non-null float64
    wheels_on                440746 non-null float64
    taxi_in                  440746 non-null float64
    crs_arr_time             450017 non-null int64
    arr_time                 440746 non-null float64
    arr_delay                439645 non-null float64
    cancelled                450017 non-null float64
    cancellation_code        8886 non-null object
    carrier_delay            97699 non-null float64
    weather_delay            97699 non-null float64
    nas_delay                97699 non-null float64
    security_delay           97699 non-null float64
    late_aircraft_delay      97699 non-null float64
    unnamed: 32              0 non-null float64
    dtypes: datetime64[ns](1), float64(15), int64(10), object(7)
    memory usage: 113.3+ MB


## Indexing

Or, *explicit is better than implicit*.
By my count, 7 of the top-15 voted pandas questions on [Stackoverflow](http://stackoverflow.com/questions/tagged/pandas?sort=votes&pageSize=15) are about indexing. This seems as good a place as any to start.

By indexing, we mean the selection of subsets of a DataFrame or Series.
`DataFrames` (and to a lesser extent, `Series`) provide a difficult set of challenges:

- Like lists, you can index by location.
- Like dictionaries, you can index by label.
- Like NumPy arrays, you can index by boolean masks.
- Any of these indexers could be scalar indexes, or they could be arrays, or they could be `slice`s.
- Any of these should work on the index (row labels) or columns of a DataFrame.
- And any of these should work on hierarchical indexes.

The complexity of pandas' indexing is a microcosm for the complexity of the pandas API in general.
There's a reason for the complexity (well, most of it), but that's not *much* consolation while you're learning.
Still, all of these ways of indexing really are useful enough to justify their inclusion in the library.

## Slicing

Or, *explicit is better than implicit*.

By my count, 7 of the top-15 voted pandas questions on [Stackoverflow](http://stackoverflow.com/questions/tagged/pandas?sort=votes&pageSize=15) are about slicing. This seems as good a place as any to start.

Brief history digression: For years the preferred method for row and/or column selection was `.ix`.


```python
df.ix[10:15, ['fl_date', 'tail_num']]
```

    /Users/taugspurger/Envs/blog/lib/python3.6/site-packages/ipykernel_launcher.py:1: DeprecationWarning: 
    .ix is deprecated. Please use
    .loc for label based indexing or
    .iloc for positional indexing
    
    See the documentation here:
    http://pandas.pydata.org/pandas-docs/stable/indexing.html#deprecate_ix
      """Entry point for launching an IPython kernel.





<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fl_date</th>
      <th>tail_num</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>10</th>
      <td>2017-01-01</td>
      <td>N756AA</td>
    </tr>
    <tr>
      <th>11</th>
      <td>2017-01-01</td>
      <td>N807AA</td>
    </tr>
    <tr>
      <th>12</th>
      <td>2017-01-01</td>
      <td>N755AA</td>
    </tr>
    <tr>
      <th>13</th>
      <td>2017-01-01</td>
      <td>N951AA</td>
    </tr>
    <tr>
      <th>14</th>
      <td>2017-01-01</td>
      <td>N523AA</td>
    </tr>
    <tr>
      <th>15</th>
      <td>2017-01-01</td>
      <td>N155AA</td>
    </tr>
  </tbody>
</table>
</div>



As you can see, this method is now deprecated. Why's that? This simple little operation hides some complexity. What if, rather than our default `range(n)` index, we had an integer index like


```python
# filter the warning for now on
import warnings
warnings.simplefilter("ignore", DeprecationWarning)
```


```python
first = df.groupby('airline_id')[['fl_date', 'unique_carrier']].first()
first.head()
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fl_date</th>
      <th>unique_carrier</th>
    </tr>
    <tr>
      <th>airline_id</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>19393</th>
      <td>2017-01-01</td>
      <td>WN</td>
    </tr>
    <tr>
      <th>19690</th>
      <td>2017-01-01</td>
      <td>HA</td>
    </tr>
    <tr>
      <th>19790</th>
      <td>2017-01-01</td>
      <td>DL</td>
    </tr>
    <tr>
      <th>19805</th>
      <td>2017-01-01</td>
      <td>AA</td>
    </tr>
    <tr>
      <th>19930</th>
      <td>2017-01-01</td>
      <td>AS</td>
    </tr>
  </tbody>
</table>
</div>



Can you predict ahead of time what our slice from above will give when passed to `.ix`?


```python
first.ix[10:15, ['fl_date', 'tail_num']]
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fl_date</th>
      <th>tail_num</th>
    </tr>
    <tr>
      <th>airline_id</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
  </tbody>
</table>
</div>



Surprise, an empty DataFrame! Which in data analysis is rarely a good thing. What happened?

We had an integer index, so the call to `.ix` used its label-based mode. It was looking for integer *labels* between 10:15 (inclusive). It didn't find any. Since we sliced a range it returned an empty DataFrame, rather than raising a KeyError.

By way of contrast, suppose we had a string index, rather than integers.


```python
first = df.groupby('unique_carrier').first()
first.ix[10:15, ['fl_date', 'tail_num']]
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fl_date</th>
      <th>tail_num</th>
    </tr>
    <tr>
      <th>unique_carrier</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>VX</th>
      <td>2017-01-01</td>
      <td>N846VA</td>
    </tr>
    <tr>
      <th>WN</th>
      <td>2017-01-01</td>
      <td>N955WN</td>
    </tr>
  </tbody>
</table>
</div>




And it works again! Now that we had a string index, `.ix` used its positional-mode. It looked for *rows* 10-15 (exclusive on the right).

But you can't reliably predict what the outcome of the slice will be ahead of time. It's on the *reader* of the code (probably your future self) to know the dtypes so you can reckon whether `.ix` will use label indexing (returning the empty DataFrame) or positional indexing (like the last example).
In general, methods whose behavior depends on the data, like `.ix` dispatching to label-based indexing on integer Indexes but location-based indexing on non-integer, are hard to use correctly. We've been trying to stamp them out in pandas.

Since pandas 0.12, these tasks have been cleanly separated into two methods:

1. `.loc` for label-based indexing
2. `.iloc` for positional indexing


```python
first.loc[['AA', 'AS', 'DL'], ['fl_date', 'tail_num']]
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fl_date</th>
      <th>tail_num</th>
    </tr>
    <tr>
      <th>unique_carrier</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>AA</th>
      <td>2017-01-01</td>
      <td>N153AA</td>
    </tr>
    <tr>
      <th>AS</th>
      <td>2017-01-01</td>
      <td>N557AS</td>
    </tr>
    <tr>
      <th>DL</th>
      <td>2017-01-01</td>
      <td>N942DL</td>
    </tr>
  </tbody>
</table>
</div>




```python
first.iloc[[0, 1, 3], [0, 1]]
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fl_date</th>
      <th>airline_id</th>
    </tr>
    <tr>
      <th>unique_carrier</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>AA</th>
      <td>2017-01-01</td>
      <td>19805</td>
    </tr>
    <tr>
      <th>AS</th>
      <td>2017-01-01</td>
      <td>19930</td>
    </tr>
    <tr>
      <th>DL</th>
      <td>2017-01-01</td>
      <td>19790</td>
    </tr>
  </tbody>
</table>
</div>



`.ix` is deprecated, but will hang around for a little while.
But if you've been using `.ix` out of habit, or if you didn't know any better, maybe give `.loc` and `.iloc` a shot. I'd recommend carefully updating your code to decide if you've been using positional or label indexing, and choose the appropriate indexer. For the intrepid reader, Joris Van den Bossche (a core pandas dev) [compiled a great overview](https://github.com/pydata/pandas/issues/9595) of the pandas `__getitem__` API.
A later post in this series will go into more detail on using Indexes effectively;
they are useful objects in their own right, but for now we'll move on to a closely related topic.

## SettingWithCopy

Pandas used to get *a lot* of questions about assignments seemingly not working. We'll take [this StackOverflow](http://stackoverflow.com/q/16553298/1889400) question as a representative question.


```python
f = pd.DataFrame({'a':[1,2,3,4,5], 'b':[10,20,30,40,50]})
f
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a</th>
      <th>b</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>10</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>20</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>30</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>40</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>50</td>
    </tr>
  </tbody>
</table>
</div>



The user wanted to take the rows of `b` where `a` was 3 or less, and set them equal to `b / 10`
We'll use boolean indexing to select those rows `f['a'] <= 3`,


```python
# ignore the context manager for now
with pd.option_context('mode.chained_assignment', None):
    f[f['a'] <= 3]['b'] = f[f['a'] <= 3 ]['b'] / 10
f
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a</th>
      <th>b</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>10</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>20</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>30</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>40</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>50</td>
    </tr>
  </tbody>
</table>
</div>



And nothing happened. Well, something did happen, but nobody witnessed it. If an object without any references is modified, does it make a sound?

The warning I silenced above with the context manager links to [an explanation](http://pandas.pydata.org/pandas-docs/stable/indexing.html#indexing-view-versus-copy) that's quite helpful. I'll summarize the high points here.

The "failure" to update `f` comes down to what's called *chained indexing*, a practice to be avoided.
The "chained" comes from indexing multiple times, one after another, rather than one single indexing operation.
Above we had two operations on the left-hand side, one `__getitem__` and one `__setitem__` (in python, the square brackets are syntactic sugar for `__getitem__` or `__setitem__` if it's for assignment). So `f[f['a'] <= 3]['b']` becomes

1. `getitem`: `f[f['a'] <= 3]`
2. `setitem`: `_['b'] = ...`  # using `_` to represent the result of 1.

In general, pandas can't guarantee whether that first `__getitem__` returns a view or a copy of the underlying data.
The changes *will* be made to the thing I called `_` above, the result of the `__getitem__` in `1`.
But we don't know that `_` shares the same memory as our original `f`.
And so we can't be sure that whatever changes are being made to `_` will be reflected in `f`.

Done properly, you would write


```python
f.loc[f['a'] <= 3, 'b'] = f.loc[f['a'] <= 3, 'b'] / 10
f
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a</th>
      <th>b</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>1</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>3.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>4</td>
      <td>40.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>5</td>
      <td>50.0</td>
    </tr>
  </tbody>
</table>
</div>



Now this is all in a single call to `__setitem__` and pandas can ensure that the assignment happens properly.

The rough rule is any time you see back-to-back square brackets, `][`, you're in asking for trouble. Replace that with a `.loc[..., ...]` and you'll be set.

The other bit of advice is that a SettingWithCopy warning is raised when the *assignment* is made.
The potential copy could be made earlier in your code.

## Multidimensional Indexing

MultiIndexes might just be my favorite feature of pandas.
They let you represent higher-dimensional datasets in a familiar two-dimensional table, which my brain can sometimes handle.
Each additional level of the MultiIndex represents another dimension.
The cost of this is somewhat harder label indexing.

My very first bug report to pandas, back in [November 2012](https://github.com/pydata/pandas/issues/2207),
was about indexing into a MultiIndex.
I bring it up now because I genuinely couldn't tell whether the result I got was a bug or not.
Also, from that bug report

> Sorry if this isn't actually a bug. Still very new to python. Thanks!

Adorable.

That operation was made much easier by [this](http://pandas.pydata.org/pandas-docs/version/0.18.0/whatsnew.html#multiindexing-using-slicers) addition in 2014, which lets you slice arbitrary levels of a MultiIndex..
Let's make a MultiIndexed DataFrame to work with.


```python
hdf = df.set_index(['unique_carrier', 'origin', 'dest', 'tail_num',
                    'fl_date']).sort_index()
hdf[hdf.columns[:4]].head()
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>airline_id</th>
      <th>fl_num</th>
      <th>origin_airport_id</th>
      <th>origin_airport_seq_id</th>
    </tr>
    <tr>
      <th>unique_carrier</th>
      <th>origin</th>
      <th>dest</th>
      <th>tail_num</th>
      <th>fl_date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">AA</th>
      <th rowspan="5" valign="top">ABQ</th>
      <th rowspan="5" valign="top">DFW</th>
      <th rowspan="2" valign="top">N3ABAA</th>
      <th>2017-01-15</th>
      <td>19805</td>
      <td>2611</td>
      <td>10140</td>
      <td>1014003</td>
    </tr>
    <tr>
      <th>2017-01-29</th>
      <td>19805</td>
      <td>1282</td>
      <td>10140</td>
      <td>1014003</td>
    </tr>
    <tr>
      <th>N3AEAA</th>
      <th>2017-01-11</th>
      <td>19805</td>
      <td>2511</td>
      <td>10140</td>
      <td>1014003</td>
    </tr>
    <tr>
      <th>N3AJAA</th>
      <th>2017-01-24</th>
      <td>19805</td>
      <td>2511</td>
      <td>10140</td>
      <td>1014003</td>
    </tr>
    <tr>
      <th>N3AVAA</th>
      <th>2017-01-11</th>
      <td>19805</td>
      <td>1282</td>
      <td>10140</td>
      <td>1014003</td>
    </tr>
  </tbody>
</table>
</div>



And just to clear up some terminology, the *levels* of a MultiIndex are the
former column names (`unique_carrier`, `origin`...).
The labels are the actual values in a level, (`'AA'`, `'ABQ'`, ...).
Levels can be referred to by name or position, with 0 being the outermost level.

Slicing the outermost index level is pretty easy, we just use our regular `.loc[row_indexer, column_indexer]`. We'll select the columns `dep_time` and `dep_delay` where the carrier was American Airlines, Delta, or US Airways.


```python
hdf.loc[['AA', 'DL', 'US'], ['dep_time', 'dep_delay']]
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>dep_time</th>
      <th>dep_delay</th>
    </tr>
    <tr>
      <th>unique_carrier</th>
      <th>origin</th>
      <th>dest</th>
      <th>tail_num</th>
      <th>fl_date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="30" valign="top">AA</th>
      <th rowspan="30" valign="top">ABQ</th>
      <th rowspan="30" valign="top">DFW</th>
      <th rowspan="2" valign="top">N3ABAA</th>
      <th>2017-01-15</th>
      <td>500.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2017-01-29</th>
      <td>757.0</td>
      <td>-3.0</td>
    </tr>
    <tr>
      <th>N3AEAA</th>
      <th>2017-01-11</th>
      <td>1451.0</td>
      <td>-9.0</td>
    </tr>
    <tr>
      <th>N3AJAA</th>
      <th>2017-01-24</th>
      <td>1502.0</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>N3AVAA</th>
      <th>2017-01-11</th>
      <td>752.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>N3AWAA</th>
      <th>2017-01-27</th>
      <td>1550.0</td>
      <td>50.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N3AXAA</th>
      <th>2017-01-16</th>
      <td>1524.0</td>
      <td>24.0</td>
    </tr>
    <tr>
      <th>2017-01-17</th>
      <td>757.0</td>
      <td>-3.0</td>
    </tr>
    <tr>
      <th>N3BJAA</th>
      <th>2017-01-25</th>
      <td>823.0</td>
      <td>23.0</td>
    </tr>
    <tr>
      <th>N3BPAA</th>
      <th>2017-01-11</th>
      <td>1638.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N3BTAA</th>
      <th>2017-01-26</th>
      <td>753.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N3BYAA</th>
      <th>2017-01-18</th>
      <td>1452.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>N3CAAA</th>
      <th>2017-01-23</th>
      <td>453.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N3CBAA</th>
      <th>2017-01-13</th>
      <td>1456.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N3CDAA</th>
      <th>2017-01-12</th>
      <td>1455.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>2017-01-28</th>
      <td>758.0</td>
      <td>-2.0</td>
    </tr>
    <tr>
      <th>N3CEAA</th>
      <th>2017-01-21</th>
      <td>455.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N3CGAA</th>
      <th>2017-01-18</th>
      <td>759.0</td>
      <td>-1.0</td>
    </tr>
    <tr>
      <th>N3CWAA</th>
      <th>2017-01-27</th>
      <td>1638.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N3CXAA</th>
      <th>2017-01-31</th>
      <td>752.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>N3DBAA</th>
      <th>2017-01-19</th>
      <td>1637.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>N3DMAA</th>
      <th>2017-01-13</th>
      <td>1638.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N3DRAA</th>
      <th>2017-01-27</th>
      <td>753.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N3DVAA</th>
      <th>2017-01-09</th>
      <td>1636.0</td>
      <td>-9.0</td>
    </tr>
    <tr>
      <th>N3DYAA</th>
      <th>2017-01-10</th>
      <td>1633.0</td>
      <td>-12.0</td>
    </tr>
    <tr>
      <th>N3ECAA</th>
      <th>2017-01-15</th>
      <td>753.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N3EDAA</th>
      <th>2017-01-09</th>
      <td>1450.0</td>
      <td>-10.0</td>
    </tr>
    <tr>
      <th>2017-01-10</th>
      <td>753.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N3ENAA</th>
      <th>2017-01-24</th>
      <td>756.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>2017-01-26</th>
      <td>1533.0</td>
      <td>33.0</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="30" valign="top">DL</th>
      <th rowspan="30" valign="top">XNA</th>
      <th rowspan="30" valign="top">ATL</th>
      <th>N921AT</th>
      <th>2017-01-20</th>
      <td>1156.0</td>
      <td>-3.0</td>
    </tr>
    <tr>
      <th>N924DL</th>
      <th>2017-01-30</th>
      <td>555.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N925DL</th>
      <th>2017-01-12</th>
      <td>551.0</td>
      <td>-9.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N929AT</th>
      <th>2017-01-08</th>
      <td>1155.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>2017-01-31</th>
      <td>1139.0</td>
      <td>-20.0</td>
    </tr>
    <tr>
      <th>N932AT</th>
      <th>2017-01-12</th>
      <td>1158.0</td>
      <td>-1.0</td>
    </tr>
    <tr>
      <th>N938AT</th>
      <th>2017-01-26</th>
      <td>1204.0</td>
      <td>5.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N940AT</th>
      <th>2017-01-18</th>
      <td>1157.0</td>
      <td>-2.0</td>
    </tr>
    <tr>
      <th>2017-01-19</th>
      <td>1200.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>N943DL</th>
      <th>2017-01-22</th>
      <td>555.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N950DL</th>
      <th>2017-01-19</th>
      <td>558.0</td>
      <td>-2.0</td>
    </tr>
    <tr>
      <th>N952DL</th>
      <th>2017-01-18</th>
      <td>556.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>N953DL</th>
      <th>2017-01-31</th>
      <td>558.0</td>
      <td>-2.0</td>
    </tr>
    <tr>
      <th>N956DL</th>
      <th>2017-01-17</th>
      <td>554.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N961AT</th>
      <th>2017-01-14</th>
      <td>1233.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N964AT</th>
      <th>2017-01-27</th>
      <td>1155.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>N966DL</th>
      <th>2017-01-23</th>
      <td>559.0</td>
      <td>-1.0</td>
    </tr>
    <tr>
      <th>N968DL</th>
      <th>2017-01-29</th>
      <td>555.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N969DL</th>
      <th>2017-01-11</th>
      <td>556.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>N976DL</th>
      <th>2017-01-09</th>
      <td>622.0</td>
      <td>22.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N977AT</th>
      <th>2017-01-24</th>
      <td>1202.0</td>
      <td>3.0</td>
    </tr>
    <tr>
      <th>2017-01-25</th>
      <td>1149.0</td>
      <td>-10.0</td>
    </tr>
    <tr>
      <th>N977DL</th>
      <th>2017-01-21</th>
      <td>603.0</td>
      <td>-2.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N979AT</th>
      <th>2017-01-15</th>
      <td>1238.0</td>
      <td>-1.0</td>
    </tr>
    <tr>
      <th>2017-01-22</th>
      <td>1155.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>N983AT</th>
      <th>2017-01-11</th>
      <td>1148.0</td>
      <td>-11.0</td>
    </tr>
    <tr>
      <th>N988DL</th>
      <th>2017-01-26</th>
      <td>556.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>N989DL</th>
      <th>2017-01-25</th>
      <td>555.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N990DL</th>
      <th>2017-01-15</th>
      <td>604.0</td>
      <td>-1.0</td>
    </tr>
    <tr>
      <th>N995AT</th>
      <th>2017-01-16</th>
      <td>1152.0</td>
      <td>-7.0</td>
    </tr>
  </tbody>
</table>
<p>142945 rows × 2 columns</p>
</div>



So far, so good. What if you wanted to select the rows whose origin was Chicago O'Hare (`ORD`) or Des Moines International Airport (DSM).
Well, `.loc` wants `[row_indexer, column_indexer]` so let's wrap the two elements of our row indexer (the list of carriers and the list of origins) in a tuple to make it a single unit:


```python
hdf.loc[(['AA', 'DL', 'US'], ['ORD', 'DSM']), ['dep_time', 'dep_delay']]
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>dep_time</th>
      <th>dep_delay</th>
    </tr>
    <tr>
      <th>unique_carrier</th>
      <th>origin</th>
      <th>dest</th>
      <th>tail_num</th>
      <th>fl_date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="30" valign="top">AA</th>
      <th rowspan="30" valign="top">DSM</th>
      <th rowspan="30" valign="top">DFW</th>
      <th>N424AA</th>
      <th>2017-01-23</th>
      <td>1324.0</td>
      <td>-3.0</td>
    </tr>
    <tr>
      <th>N426AA</th>
      <th>2017-01-25</th>
      <td>541.0</td>
      <td>-9.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N437AA</th>
      <th>2017-01-13</th>
      <td>542.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>2017-01-23</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N438AA</th>
      <th>2017-01-11</th>
      <td>542.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N439AA</th>
      <th>2017-01-24</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>2017-01-31</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N4UBAA</th>
      <th>2017-01-18</th>
      <td>1323.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>N4WNAA</th>
      <th>2017-01-27</th>
      <td>1322.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N4XBAA</th>
      <th>2017-01-09</th>
      <td>536.0</td>
      <td>-14.0</td>
    </tr>
    <tr>
      <th>N4XEAA</th>
      <th>2017-01-21</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N4XFAA</th>
      <th>2017-01-31</th>
      <td>1320.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XGAA</th>
      <th>2017-01-28</th>
      <td>1337.0</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>2017-01-30</th>
      <td>542.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XJAA</th>
      <th>2017-01-20</th>
      <td>552.0</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>2017-01-21</th>
      <td>1320.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N4XKAA</th>
      <th>2017-01-26</th>
      <td>1323.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XMAA</th>
      <th>2017-01-16</th>
      <td>1423.0</td>
      <td>56.0</td>
    </tr>
    <tr>
      <th>2017-01-19</th>
      <td>1321.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XPAA</th>
      <th>2017-01-09</th>
      <td>1322.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>2017-01-14</th>
      <td>545.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N4XTAA</th>
      <th>2017-01-10</th>
      <td>1355.0</td>
      <td>28.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XUAA</th>
      <th>2017-01-13</th>
      <td>1330.0</td>
      <td>3.0</td>
    </tr>
    <tr>
      <th>2017-01-14</th>
      <td>1319.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>N4XVAA</th>
      <th>2017-01-28</th>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XXAA</th>
      <th>2017-01-15</th>
      <td>1322.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>2017-01-16</th>
      <td>545.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N4XYAA</th>
      <th>2017-01-18</th>
      <td>559.0</td>
      <td>9.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4YCAA</th>
      <th>2017-01-26</th>
      <td>545.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>2017-01-27</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="30" valign="top">DL</th>
      <th rowspan="30" valign="top">ORD</th>
      <th rowspan="30" valign="top">SLC</th>
      <th>N316NB</th>
      <th>2017-01-23</th>
      <td>1332.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N317NB</th>
      <th>2017-01-09</th>
      <td>1330.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>2017-01-11</th>
      <td>1345.0</td>
      <td>7.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N319NB</th>
      <th>2017-01-17</th>
      <td>1353.0</td>
      <td>15.0</td>
    </tr>
    <tr>
      <th>2017-01-22</th>
      <td>1331.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N320NB</th>
      <th>2017-01-13</th>
      <td>1332.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N321NB</th>
      <th>2017-01-19</th>
      <td>1419.0</td>
      <td>41.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N323NB</th>
      <th>2017-01-01</th>
      <td>1732.0</td>
      <td>57.0</td>
    </tr>
    <tr>
      <th>2017-01-02</th>
      <td>1351.0</td>
      <td>11.0</td>
    </tr>
    <tr>
      <th>N324NB</th>
      <th>2017-01-16</th>
      <td>1337.0</td>
      <td>-1.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N326NB</th>
      <th>2017-01-24</th>
      <td>1332.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>2017-01-26</th>
      <td>1349.0</td>
      <td>11.0</td>
    </tr>
    <tr>
      <th>N329NB</th>
      <th>2017-01-06</th>
      <td>1422.0</td>
      <td>32.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N330NB</th>
      <th>2017-01-04</th>
      <td>1344.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>2017-01-12</th>
      <td>1343.0</td>
      <td>5.0</td>
    </tr>
    <tr>
      <th>N335NB</th>
      <th>2017-01-31</th>
      <td>1336.0</td>
      <td>-2.0</td>
    </tr>
    <tr>
      <th>N338NB</th>
      <th>2017-01-29</th>
      <td>1355.0</td>
      <td>17.0</td>
    </tr>
    <tr>
      <th>N347NB</th>
      <th>2017-01-08</th>
      <td>1338.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>N348NB</th>
      <th>2017-01-10</th>
      <td>1355.0</td>
      <td>17.0</td>
    </tr>
    <tr>
      <th>N349NB</th>
      <th>2017-01-30</th>
      <td>1333.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N352NW</th>
      <th>2017-01-06</th>
      <td>1857.0</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>N354NW</th>
      <th>2017-01-04</th>
      <td>1844.0</td>
      <td>-3.0</td>
    </tr>
    <tr>
      <th>N356NW</th>
      <th>2017-01-02</th>
      <td>1640.0</td>
      <td>20.0</td>
    </tr>
    <tr>
      <th>N358NW</th>
      <th>2017-01-05</th>
      <td>1856.0</td>
      <td>9.0</td>
    </tr>
    <tr>
      <th>N360NB</th>
      <th>2017-01-25</th>
      <td>1354.0</td>
      <td>16.0</td>
    </tr>
    <tr>
      <th>N365NB</th>
      <th>2017-01-18</th>
      <td>1350.0</td>
      <td>12.0</td>
    </tr>
    <tr>
      <th>N368NB</th>
      <th>2017-01-27</th>
      <td>1351.0</td>
      <td>13.0</td>
    </tr>
    <tr>
      <th>N370NB</th>
      <th>2017-01-20</th>
      <td>1355.0</td>
      <td>17.0</td>
    </tr>
    <tr>
      <th>N374NW</th>
      <th>2017-01-03</th>
      <td>1846.0</td>
      <td>-1.0</td>
    </tr>
    <tr>
      <th>N987AT</th>
      <th>2017-01-08</th>
      <td>1914.0</td>
      <td>29.0</td>
    </tr>
  </tbody>
</table>
<p>5582 rows × 2 columns</p>
</div>



Now try to do any flight from ORD or DSM, not just from those carriers.
This used to be a pain.
You might have to turn to the `.xs` method, or pass in `df.index.get_level_values(0)` and zip that up with the indexers your wanted, or maybe reset the index and do a boolean mask, and set the index again... ugh.

But now, you can use an `IndexSlice`.


```python
hdf.loc[pd.IndexSlice[:, ['ORD', 'DSM']], ['dep_time', 'dep_delay']]
```




<div>
<style>
    .dataframe thead tr:only-child th {
        text-align: right;
    }

    .dataframe thead th {
        text-align: left;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>dep_time</th>
      <th>dep_delay</th>
    </tr>
    <tr>
      <th>unique_carrier</th>
      <th>origin</th>
      <th>dest</th>
      <th>tail_num</th>
      <th>fl_date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="30" valign="top">AA</th>
      <th rowspan="30" valign="top">DSM</th>
      <th rowspan="30" valign="top">DFW</th>
      <th>N424AA</th>
      <th>2017-01-23</th>
      <td>1324.0</td>
      <td>-3.0</td>
    </tr>
    <tr>
      <th>N426AA</th>
      <th>2017-01-25</th>
      <td>541.0</td>
      <td>-9.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N437AA</th>
      <th>2017-01-13</th>
      <td>542.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>2017-01-23</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N438AA</th>
      <th>2017-01-11</th>
      <td>542.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N439AA</th>
      <th>2017-01-24</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>2017-01-31</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N4UBAA</th>
      <th>2017-01-18</th>
      <td>1323.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th>N4WNAA</th>
      <th>2017-01-27</th>
      <td>1322.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N4XBAA</th>
      <th>2017-01-09</th>
      <td>536.0</td>
      <td>-14.0</td>
    </tr>
    <tr>
      <th>N4XEAA</th>
      <th>2017-01-21</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N4XFAA</th>
      <th>2017-01-31</th>
      <td>1320.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XGAA</th>
      <th>2017-01-28</th>
      <td>1337.0</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>2017-01-30</th>
      <td>542.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XJAA</th>
      <th>2017-01-20</th>
      <td>552.0</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>2017-01-21</th>
      <td>1320.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N4XKAA</th>
      <th>2017-01-26</th>
      <td>1323.0</td>
      <td>-4.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XMAA</th>
      <th>2017-01-16</th>
      <td>1423.0</td>
      <td>56.0</td>
    </tr>
    <tr>
      <th>2017-01-19</th>
      <td>1321.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XPAA</th>
      <th>2017-01-09</th>
      <td>1322.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>2017-01-14</th>
      <td>545.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N4XTAA</th>
      <th>2017-01-10</th>
      <td>1355.0</td>
      <td>28.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XUAA</th>
      <th>2017-01-13</th>
      <td>1330.0</td>
      <td>3.0</td>
    </tr>
    <tr>
      <th>2017-01-14</th>
      <td>1319.0</td>
      <td>-8.0</td>
    </tr>
    <tr>
      <th>N4XVAA</th>
      <th>2017-01-28</th>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4XXAA</th>
      <th>2017-01-15</th>
      <td>1322.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>2017-01-16</th>
      <td>545.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N4XYAA</th>
      <th>2017-01-18</th>
      <td>559.0</td>
      <td>9.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N4YCAA</th>
      <th>2017-01-26</th>
      <td>545.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>2017-01-27</th>
      <td>544.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="30" valign="top">WN</th>
      <th rowspan="30" valign="top">DSM</th>
      <th rowspan="30" valign="top">STL</th>
      <th>N635SW</th>
      <th>2017-01-15</th>
      <td>1806.0</td>
      <td>6.0</td>
    </tr>
    <tr>
      <th>N645SW</th>
      <th>2017-01-22</th>
      <td>1800.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>N651SW</th>
      <th>2017-01-01</th>
      <td>1856.0</td>
      <td>61.0</td>
    </tr>
    <tr>
      <th>N654SW</th>
      <th>2017-01-21</th>
      <td>1156.0</td>
      <td>126.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N720WN</th>
      <th>2017-01-23</th>
      <td>605.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>2017-01-31</th>
      <td>603.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N724SW</th>
      <th>2017-01-30</th>
      <td>1738.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N734SA</th>
      <th>2017-01-20</th>
      <td>1839.0</td>
      <td>54.0</td>
    </tr>
    <tr>
      <th>N737JW</th>
      <th>2017-01-09</th>
      <td>605.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N747SA</th>
      <th>2017-01-27</th>
      <td>610.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>N7718B</th>
      <th>2017-01-18</th>
      <td>1736.0</td>
      <td>-9.0</td>
    </tr>
    <tr>
      <th>N772SW</th>
      <th>2017-01-31</th>
      <td>1738.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N7735A</th>
      <th>2017-01-11</th>
      <td>603.0</td>
      <td>-7.0</td>
    </tr>
    <tr>
      <th>N773SA</th>
      <th>2017-01-17</th>
      <td>1743.0</td>
      <td>-2.0</td>
    </tr>
    <tr>
      <th>N7749B</th>
      <th>2017-01-10</th>
      <td>1746.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N781WN</th>
      <th>2017-01-02</th>
      <td>1909.0</td>
      <td>59.0</td>
    </tr>
    <tr>
      <th>2017-01-30</th>
      <td>605.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N7827A</th>
      <th>2017-01-14</th>
      <td>1644.0</td>
      <td>414.0</td>
    </tr>
    <tr>
      <th>N7833A</th>
      <th>2017-01-06</th>
      <td>659.0</td>
      <td>49.0</td>
    </tr>
    <tr>
      <th>N7882B</th>
      <th>2017-01-15</th>
      <td>901.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>N791SW</th>
      <th>2017-01-26</th>
      <td>1744.0</td>
      <td>-1.0</td>
    </tr>
    <tr>
      <th>N903WN</th>
      <th>2017-01-13</th>
      <td>1908.0</td>
      <td>83.0</td>
    </tr>
    <tr>
      <th>N905WN</th>
      <th>2017-01-05</th>
      <td>605.0</td>
      <td>-5.0</td>
    </tr>
    <tr>
      <th>N944WN</th>
      <th>2017-01-02</th>
      <td>630.0</td>
      <td>5.0</td>
    </tr>
    <tr>
      <th>N949WN</th>
      <th>2017-01-01</th>
      <td>624.0</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>N952WN</th>
      <th>2017-01-29</th>
      <td>854.0</td>
      <td>-6.0</td>
    </tr>
    <tr>
      <th>N954WN</th>
      <th>2017-01-11</th>
      <td>1736.0</td>
      <td>-9.0</td>
    </tr>
    <tr>
      <th>N956WN</th>
      <th>2017-01-06</th>
      <td>1736.0</td>
      <td>-9.0</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">NaN</th>
      <th>2017-01-16</th>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2017-01-17</th>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>19466 rows × 2 columns</p>
</div>



The `:` says include every label in this level.
The `IndexSlice` object is just sugar for the actual python `slice` object needed to remove slice each level.


```python
pd.IndexSlice[:, ['ORD', 'DSM']]
```




    (slice(None, None, None), ['ORD', 'DSM'])



We'll talk more about working with Indexes (including MultiIndexes) in a later post. I have an unproven thesis that they're underused because `IndexSlice` is underused, causing people to think they're more unwieldy than they actually are. But let's close out part one.

## WrapUp

This first post covered Indexing, a topic that's central to pandas.
The power provided by the DataFrame comes with some unavoidable complexities.
Best practices (using `.loc` and `.iloc`) will spare you many a headache.
We then toured a couple of commonly misunderstood sub-topics, setting with copy and Hierarchical Indexing.

---
title: "Modern Pandas (Part 8): Scaling"
date: 2018-04-23
slug: modern-8-scaling
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



As I sit down to write this, the third-most popular pandas question on StackOverflow covers [how to use pandas for large datasets](https://stackoverflow.com/q/14262433/1889400). This is in tension with the fact that a pandas DataFrame is an in memory container. *You can't have a `DataFrame` larger than your machine's RAM*. In practice, your available RAM should be several times the size of your dataset, as you or pandas will have to make intermediate copies as part of the analysis.

Historically, pandas users have scaled to larger datasets by switching away from pandas or using iteration. Both of these are perfectly valid approaches, but changing your workflow in response to scaling data is unfortunate. I use pandas because it's a pleasant experience, and I would like that experience to scale to larger datasets. That's what [Dask](dask.pydata.org/), a parallel computing library, enables. We'll discuss Dask in detail later. But first, let's work through scaling a simple analysis to a larger than memory dataset.

Our task is to find the 100 most-common occupations reported in the FEC's [individual contributions dataest](https://classic.fec.gov/finance/disclosure/ftpdet.shtml). The files are split by election cycle (2007-2008, 2009-2010, ...). You can find some scripts for downloading the data in [this repository](https://github.com/tomaugspurger/scalable-ml-fec). My laptop can read in each cycle's file individually, but the full dataset is too large to read in at once. Let's read in just 2010's file, and do the "small data" version.


```python
from pathlib import Path

import pandas as pd
import seaborn as sns

df = pd.read_parquet("data/indiv-10.parq", columns=['occupation'], engine='pyarrow')

most_common = df.occupation.value_counts().nlargest(100)
most_common
```

<!-- <div class="output"> -->
<pre>
    RETIRED                    279775
    ATTORNEY                   166768
    PRESIDENT                   81336
    PHYSICIAN                   73015
    HOMEMAKER                   66057
                                ...  
    C.E.O.                       1945
    EMERGENCY PHYSICIAN          1944
    BUSINESS EXECUTIVE           1924
    BUSINESS REPRESENTATIVE      1879
    GOVERNMENT AFFAIRS           1867
    Name: occupation, Length: 100, dtype: int64
</pre>
<!-- </div> -->



After reading in the file, our actual analysis is a simple 1-liner using two operations built into pandas. Truly, the best of all possible worlds.

Next, we'll do the analysis for the entire dataset, which is larger than memory, in two ways. First we'll use just pandas and iteration. Then we'll use Dask.

### Using Iteration

To do this with just pandas we have to rewrite our code, taking care to never have too much data in RAM at once. We will

1. Create a global `total_counts` Series that contains the counts from all of the files processed so far
2. Read in a file
3. Compute a temporary variable `counts` with the counts for just this file
4. Add that temporary `counts` into the global `total_counts`
5. Select the 100 largest with `.nlargest`

This works since the `total_counts` Series is relatively small, and each year's data fits in RAM individually. Our peak memory usage should be the size of the largest individual cycle (2015-2016) plus the size of `total_counts` (which we can essentially ignore).


```python
files = sorted(Path("data/").glob("indiv-*.parq"))

total_counts = pd.Series()

for year in files:
    df = pd.read_parquet(year, columns=['occupation'],
                         engine="pyarrow")
    counts = df.occupation.value_counts()
    total_counts = total_counts.add(counts, fill_value=0)

total_counts = total_counts.nlargest(100).sort_values(ascending=False)
```

<!-- <div class="output"> -->
<pre>
RETIRED                    4769520
NOT EMPLOYED               2656988
ATTORNEY                   1340434
PHYSICIAN                   659082
HOMEMAKER                   494187
                            ...   
CHIEF EXECUTIVE OFFICER      26551
SURGEON                      25521
EDITOR                       25457
OPERATOR                     25151
ORTHOPAEDIC SURGEON          24384
Name: occupation, Length: 100, dtype: int64
</pre>
<!-- </div> -->


While this works, our small one-liner has ballooned in size (and complexity; should you *really* have to know about `Series.add`'s `fill_value` parameter for this simple analysis?). If only there was a better way...

### Using Dask

With Dask, we essentially recover our original code. We'll change our import to use `dask.dataframe.read_parquet`, which returns a Dask DataFrame.


```python
import dask.dataframe as dd
```


```python
df = dd.read_parquet("data/indiv-*.parquet", engine='pyarrow', columns=['occupation'])

most_common = df.occupation.value_counts().nlargest(100)
most_common.compute().sort_values(ascending=False)
```

<!-- <div class="output"> -->
<pre>
RETIRED                    4769520
NOT EMPLOYED               2656988
ATTORNEY                   1340434
PHYSICIAN                   659082
HOMEMAKER                   494187
                            ...   
CHIEF EXECUTIVE OFFICER      26551
SURGEON                      25521
EDITOR                       25457
OPERATOR                     25151
ORTHOPAEDIC SURGEON          24384
Name: occupation, Length: 100, dtype: int64
</pre>
<!-- </div> -->


There are a couple differences from the original pandas version, which we'll discuss next, but overall I hope you agree that the Dask version is nicer than the version using iteration.

## Dask

Now that we've seen `dask.dataframe` in action, let's step back and discuss Dask a bit. Dask is an open-source project that natively parallizes Python. I'm a happy user of and contributor to Dask.

At a high-level, Dask provides familiar APIs for [large N-dimensional arrays](https://dask.pydata.org/en/latest/array.html), [large DataFrames](https://dask.pydata.org/en/latest/dataframe.html), and [familiar](https://distributed.readthedocs.io/en/latest/quickstart.html#map-and-submit-functions) ways to parallelize [custom algorithms](https://dask.pydata.org/en/latest/delayed.html).

At a low-level, each of these is built on high-performance [task scheduling](http://dask.pydata.org/en/latest/scheduling.html) that executes operations in parallel. The [low-level details](http://dask.pydata.org/en/latest/spec.html) aren't too important; all we care about is that

1. Dask works with *task graphs* (*tasks*: functions to call on data, and *graphs*: the relationships between tasks).
2. This is a flexible and performant way to parallelize many different kinds of problems.

To understand point 1, let's examine the difference between a Dask DataFrame and a pandas DataFrame. When we read in `df` with `dd.read_parquet`, we received a Dask DataFrame.


```python
df
```



<div class="output">
<div><strong>Dask DataFrame Structure:</strong></div>
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>occupation</th>
    </tr>
    <tr>
      <th>npartitions=35</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th></th>
      <td>object</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
    </tr>
  </tbody>
</table>
</div>
<div>Dask Name: read-parquet, 35 tasks</div>
</div>



A Dask DataFrame consists of many pandas DataFrames arranged by the index. Dask is really just coordinating these pandas DataFrames.

<img src="http://dask.pydata.org/en/latest/_images/dask-dataframe.svg" width="50%"/>

All the actual computation (reading from disk, computing the value counts, etc.) eventually use pandas internally. If I do `df.occupation.str.len`, Dask will coordinate calling `pandas.Series.str.len` on each of the pandas DataFrames.

Those reading carefully will notice a problem with the statement "A Dask DataFrame consists of many pandas DataFrames". Our initial problem was that we didn't have enough memory for those DataFrames! How can Dask be coordinating DataFrames if there isn't enough memory? This brings us to the second major difference: Dask DataFrames (and arrays) are lazy. Operations on them don't execute and produce the final result immediately. Rather, calling methods on them builds up a task graph.

We can visualize task graphs using `graphviz`. For the blog, I've trimmed down the example to be a subset of the entire graph.


```python
df.visualize(rankdir='LR')
```



![](/images/scalable-read-simple.svg)


`df` (the dask DataFrame consisting of many pandas DataFrames) has a task graph with 5 calls to a parquet reader (one for each file), each of which produces a DataFrame when called.

Calling additional methods on `df` adds additional tasks to this graph. For example, our `most_common` Series has three additional calls

- Select the `occupation` column (`__getitem__`)
- Perform the value counts
- Select the 100 largest values


```python
most_common = df.occupation.value_counts().nlargest(100)
most_common
```


<!-- <div class="output"> -->
<pre>

    Dask Series Structure:
    npartitions=1
        int64
          ...
    Name: occupation, dtype: int64
    Dask Name: series-nlargest-agg, 113 tasks
</pre>
<!-- </div> -->



Which we can visualize.


```python
most_common.visualize(rankdir='LR')
```




![](/images/scalable-most-common.svg)

So `most_common` doesn't hold the actual answer yet. Instead, it holds a recipe for the answer; a list of all the steps to take to get the concrete result. One way to ask for the result is with the `compute` method.


```python
most_common.compute()
```



<!-- <div class="output"> -->
<pre>
    RETIRED                    4769520
    NOT EMPLOYED               2656988
    ATTORNEY                   1340434
    PHYSICIAN                   659082
    HOMEMAKER                   494187
                                ...   
    CHIEF EXECUTIVE OFFICER      26551
    SURGEON                      25521
    EDITOR                       25457
    OPERATOR                     25151
    ORTHOPAEDIC SURGEON          24384
    Name: occupation, Length: 100, dtype: int64
</pre>
<!-- </div> -->


At this point, the task graph is handed to a [scheduler](https://dask.pydata.org/en/latest/scheduling.html), which is responsible for executing a task graph. Schedulers can analyze a task graph and find sections that can run *in parallel*. (Dask includes several schedulers. See [the scheduling documentation](http://dask.pydata.org/en/latest/scheduling.html) for how to choose, though Dask has good defaults.)

So that's a high-level tour of how Dask works: 

![collections, schedulers](http://dask.pydata.org/en/latest/_images/collections-schedulers.png)

1. Various collections collections like `dask.dataframe` and `dask.array`
   provide users familiar APIs for working with large datasets.
2. Computations are represented as a task graph. These graphs could be built by
   hand, or more commonly built by one of the collections.
3. Dask schedulers run task graphs in parallel (potentially distributed across
   a cluster), reusing libraries like NumPy and pandas to do the computations.

Let's finish off this post by continuing to explore the FEC dataset with Dask. At this point, we'll use the distributed scheduler for it's nice diagnostics.


```python
import dask.dataframe as dd
from dask import compute
from dask.distributed import Client
import seaborn as sns

client = Client(processes=False)
```


Calling `Client` without providing a scheduler address will make a local "cluster" of threads or processes on your machine. There are [many ways](http://dask.pydata.org/en/latest/setup.html) to deploy a Dask cluster onto an actual cluster of machines, though we're particularly fond of [Kubernetes](http://dask.pydata.org/en/latest/setup/kubernetes.html). This highlights one of my favorite features of Dask: it scales down to use a handful of threads on a laptop *or* up to a cluster with thousands of nodes. Dask can comfortably handle medium-sized datasets (dozens of GBs, so larger than RAM) on a laptop. Or it can scale up to very large datasets with a cluster.


```python
individual_cols = ['cmte_id', 'entity_tp', 'employer', 'occupation',
                   'transaction_dt', 'transaction_amt']

indiv = dd.read_parquet('data/indiv-*.parq',
                        columns=individual_cols,
                        engine="pyarrow")
indiv
```



<div class="output">
<div><strong>Dask DataFrame Structure:</strong></div>
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cmte_id</th>
      <th>entity_tp</th>
      <th>employer</th>
      <th>occupation</th>
      <th>transaction_dt</th>
      <th>transaction_amt</th>
    </tr>
    <tr>
      <th>npartitions=5</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th></th>
      <td>object</td>
      <td>object</td>
      <td>object</td>
      <td>object</td>
      <td>datetime64[ns]</td>
      <td>int64</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
  </tbody>
</table>
</div>
<div>Dask Name: read-parquet, 5 tasks</div>
</div>



We can compute summary statistics like the average mean and standard deviation of the transaction amount:


```python
avg_transaction = indiv.transaction_amt.mean()
```

We can answer questions like "Which employer's employees donated the most?"


```python
total_by_employee = (
    indiv.groupby('employer')
        .transaction_amt.sum()
        .nlargest(10)
)
```

Or "what is the average amount donated per occupation?"


```python
avg_by_occupation = (
    indiv.groupby("occupation")
        .transaction_amt.mean()
        .nlargest(10)
)
```

Since Dask is lazy, we haven't actually computed anything.


```python
total_by_employee
```



<!-- <div class="output"> -->
<pre>
    Dask Series Structure:
    npartitions=1
        int64
          ...
    Name: transaction_amt, dtype: int64
    Dask Name: series-nlargest-agg, 13 tasks
</pre>
<!-- </div> -->



`avg_transaction`, `avg_by_occupation` and `total_by_employee` are three separate computations (they have different task graphs), but we know they share some structure: they're all reading in the same data, they might select the same subset of columns, and so on. Dask is able to avoid redundant computation when you use the top-level `dask.compute` function.


```python
%%time
avg_transaction, by_employee, by_occupation = compute(
    avg_transaction, total_by_employee, avg_by_occupation
)
```

<!-- <div class="output"> -->
<pre>
    CPU times: user 57.5 s, sys: 14.4 s, total: 1min 11s
    Wall time: 54.9 s
</pre>
<!-- </div> -->


```python
avg_transaction
```




<!-- <div class="output"> -->
<pre>
    566.0899206077507
</pre>
<!-- </div> -->


```python
by_employee
```




<!-- <div class="output"> -->
<pre>
    employer
    RETIRED                1019973117
    SELF-EMPLOYED           834547641
    SELF                    537402882
    SELF EMPLOYED           447363032
    NONE                    418011322
    HOMEMAKER               355195126
    NOT EMPLOYED            345770418
    FAHR, LLC               166679844
    CANDIDATE                75186830
    ADELSON DRUG CLINIC      53358500
    Name: transaction_amt, dtype: int64
</pre>
<!-- </div> -->



```python
by_occupation
```




<!-- <div class="output"> -->
<pre>
    occupation
    CHAIRMAN CEO & FOUNDER                   1,023,333.33
    PAULSON AND CO., INC.                    1,000,000.00
    CO-FOUNDING DIRECTOR                       875,000.00
    CHAIRMAN/CHIEF TECHNOLOGY OFFICER          750,350.00
    CO-FOUNDER, DIRECTOR, CHIEF INFORMATIO     675,000.00
    CO-FOUNDER, DIRECTOR                       550,933.33
    MOORE CAPITAL GROUP, LP                    500,000.00
    PERRY HOMES                                500,000.00
    OWNER, FOUNDER AND CEO                     500,000.00
    CHIEF EXECUTIVE OFFICER/PRODUCER           500,000.00
    Name: transaction_amt, dtype: float64
</pre>
<!-- </div> -->


Things like filtering work well. Let's find the 10 most common occupations and filter the dataset down to just those.


```python
top_occupations = (
    indiv.occupation.value_counts()
        .nlargest(10).index
).compute()
top_occupations
```



<!-- <div class="output"> -->
<pre>
    Index(['RETIRED', 'NOT EMPLOYED', 'ATTORNEY', 'PHYSICIAN', 'HOMEMAKER',
           'PRESIDENT', 'PROFESSOR', 'CONSULTANT', 'EXECUTIVE', 'ENGINEER'],
          dtype='object')
</pre>
<!-- </div> -->


We'll filter the raw records down to just the ones from those occupations. Then we'll compute a few summary statistics on the transaction amounts for each group.


```python
donations = (
    indiv[indiv.occupation.isin(top_occupations)]
        .groupby("occupation")
        .transaction_amt
        .agg(['count', 'mean', 'sum', 'max'])
)
```


```python
total_avg, occupation_avg = compute(indiv.transaction_amt.mean(),
                                    donations['mean'])
```

These are small, concrete results so we can turn to familiar tools like matplotlib to visualize the result.


```python
ax = occupation_avg.sort_values(ascending=False).plot.barh(color='k', width=0.9);
lim = ax.get_ylim()
ax.vlines(total_avg, *lim, color='C1', linewidth=3)
ax.legend(['Average donation'])
ax.set(xlabel="Donation Amount", title="Average Dontation by Occupation")
sns.despine()
```


![png](/images/modern-pandas-08_49_0.png)


Dask inherits all of pandas' great time-series support. We can get the total amount donated per day using a [`resample`](https://pandas.pydata.org/pandas-docs/stable/timeseries.html#resampling).


```python
daily = (
    indiv[['transaction_dt', 'transaction_amt']].dropna()
        .set_index('transaction_dt')['transaction_amt']
        .resample("D")
        .sum()
).compute()
daily
```




<!-- <div class="output"> -->
<pre>
    1916-01-23    1000
    1916-01-24       0
    1916-01-25       0
    1916-01-26       0
    1916-01-27       0
                  ... 
    2201-05-29       0
    2201-05-30       0
    2201-05-31       0
    2201-06-01       0
    2201-06-02    2000
    Name: transaction_amt, Length: 104226, dtype: int64
</pre>
<!-- </div> -->


It seems like we have some bad data. This should just be 2007-2016. We'll filter it down to the real subset before plotting.
Notice that the seamless transition from `dask.dataframe` operations above, to pandas operations below.


```python
subset = daily.loc['2011':'2016']
ax = subset.div(1000).plot(figsize=(12, 6))
ax.set(ylim=0, title="Daily Donations", ylabel="$ (thousands)",)
sns.despine();
```


![png](/images/modern-pandas-08_54_0.png)


## Joining

Like pandas, Dask supports joining together multiple datasets.

Individual donations are made to *committees*. Committees are what make the actual expenditures (buying a TV ad).
Some committees are directly tied to a candidate (this are campaign committees). Other committees are tied to a group (like the Republican National Committee). Either may be tied to a party.

Let's read in the committees. The total number of committees is small, so we'll `.compute` immediately to get a pandas DataFrame (the reads still happen in parallel!).


```python
committee_cols = ['cmte_id', 'cmte_nm', 'cmte_tp', 'cmte_pty_affiliation']
cm = dd.read_parquet("data/cm-*.parq",
                     columns=committee_cols).compute()

# Some committees change thier name, but the ID stays the same
cm = cm.groupby('cmte_id').last()
cm
```




<!-- <div class="output"> -->
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table  class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cmte_nm</th>
      <th>cmte_tp</th>
      <th>cmte_pty_affiliation</th>
    </tr>
    <tr>
      <th>cmte_id</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>C00000042</th>
      <td>ILLINOIS TOOL WORKS INC. FOR BETTER GOVERNMENT...</td>
      <td>Q</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>C00000059</th>
      <td>HALLMARK CARDS PAC</td>
      <td>Q</td>
      <td>UNK</td>
    </tr>
    <tr>
      <th>C00000422</th>
      <td>AMERICAN MEDICAL ASSOCIATION POLITICAL ACTION ...</td>
      <td>Q</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>C00000489</th>
      <td>D R I V E POLITICAL FUND CHAPTER 886</td>
      <td>N</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>C00000547</th>
      <td>KANSAS MEDICAL SOCIETY POLITICAL ACTION COMMITTEE</td>
      <td>Q</td>
      <td>UNK</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>C90017237</th>
      <td>ORGANIZE NOW</td>
      <td>I</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>C90017245</th>
      <td>FRANCISCO AGUILAR</td>
      <td>I</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>C90017336</th>
      <td>LUDWIG, EUGENE</td>
      <td>I</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>C99002396</th>
      <td>AMERICAN POLITICAL ACTION COMMITTEE</td>
      <td>Q</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>C99003428</th>
      <td>THIRD DISTRICT REPUBLICAN PARTY</td>
      <td>Y</td>
      <td>REP</td>
    </tr>
  </tbody>
</table>
<p>28612 rows × 3 columns</p>
</div>
<!-- </div> -->


We'll use `dd.merge`, which is analogous to `pd.merge` for joining a Dask `DataFrame` with a pandas or Dask `DataFrame`.


```python
indiv = indiv[(indiv.transaction_dt >= pd.Timestamp("2007-01-01")) &
              (indiv.transaction_dt <= pd.Timestamp("2018-01-01"))]

df2 = dd.merge(indiv, cm.reset_index(), on='cmte_id')
df2
```




<!-- <div class="output"> -->
<div><strong>Dask DataFrame Structure:</strong></div>
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table  class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cmte_id</th>
      <th>entity_tp</th>
      <th>employer</th>
      <th>occupation</th>
      <th>transaction_dt</th>
      <th>transaction_amt</th>
      <th>cmte_nm</th>
      <th>cmte_tp</th>
      <th>cmte_pty_affiliation</th>
    </tr>
    <tr>
      <th>npartitions=20</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th></th>
      <td>object</td>
      <td>object</td>
      <td>object</td>
      <td>object</td>
      <td>datetime64[ns]</td>
      <td>int64</td>
      <td>object</td>
      <td>object</td>
      <td>object</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
  </tbody>
</table>
</div>
<div>Dask Name: merge, 141 tasks</div>
<!-- </div> -->


Now we can find which party raised more over the course of each election. We'll group by the day and party and sum the transaction amounts.


```python
indiv = indiv.repartition(npartitions=10)
df2 = dd.merge(indiv, cm.reset_index(), on='cmte_id')
df2
```



<!-- <div class="output"> -->
<div><strong>Dask DataFrame Structure:</strong></div>
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table  class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>cmte_id</th>
      <th>entity_tp</th>
      <th>employer</th>
      <th>occupation</th>
      <th>transaction_dt</th>
      <th>transaction_amt</th>
      <th>cmte_nm</th>
      <th>cmte_tp</th>
      <th>cmte_pty_affiliation</th>
    </tr>
    <tr>
      <th>npartitions=10</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th></th>
      <td>object</td>
      <td>object</td>
      <td>object</td>
      <td>object</td>
      <td>datetime64[ns]</td>
      <td>int64</td>
      <td>object</td>
      <td>object</td>
      <td>object</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th></th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
  </tbody>
</table>
</div>
<div>Dask Name: merge, 141 tasks</div>
<!-- </div> -->



```python
party_donations = (
    df2.groupby([df2.transaction_dt, 'cmte_pty_affiliation'])
       .transaction_amt.sum()
).compute().sort_index()
```

We'll filter that down to just Republican and Democrats and plot.


```python
ax = (
    party_donations.loc[:, ['REP', 'DEM']]
        .unstack("cmte_pty_affiliation").iloc[1:-2]
        .rolling('30D').mean().plot(color=['C0', 'C3'], figsize=(12, 6),
                                    linewidth=3)
)
sns.despine()
ax.set(title="Daily Donations (30-D Moving Average)", xlabel="Date");
```


![png](/images/modern-pandas-08_64_0.png)


## Try It Out!

So that's a taste of Dask. Next time you hit a scaling problem with pandas (or NumPy, scikit-learn, or your custom code), feel free to

```
pip install dask[complete]
```

or

```
conda install dask
```

The [dask homepage](http://dask.pydata.org/en/latest/) has links to all the relevant documentation, and [binder notebooks](https://mybinder.org/v2/gh/dask/dask-examples/master?filepath=dataframe.ipynb) where you can try out Dask before installing.

As always, reach out to me on [Twitter](https://twitter.com/TomAugspurger) or in the comments if you have anything to share.

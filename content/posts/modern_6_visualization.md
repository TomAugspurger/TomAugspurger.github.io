---
title: "Modern Pandas (Part 6): Visualization"
date: 2016-04-28
slug: modern-6-visualization
tags:
  - pandas
---

---

This is part 6 in my series on writing modern idiomatic pandas.

- [Modern Pandas](modern-1-intro)
- [Method Chaining](method-chaining)
- [Indexes](modern-3-indexes)
- [Fast Pandas](modern-4-performance)
- [Tidy Data](modern-5-tidy)
- [Visualization](modern-6-visualization)
- [Time Series](modern-7-timeseries)
- [Scaling](modern-8-scaling)

---


# Visualization and Exploratory Analysis

A few weeks ago, the R community went through some hand-wringing about plotting packages.
For outsiders (like me) the details aren't that important, but some brief background might be useful so we can transfer the takeaways to Python.
The competing systems are "base R", which is the plotting system built into the language, and ggplot2, Hadley Wickham's implementation of the grammar of graphics.
For those interested in more details, start with

- [Why I Don't Use ggplot2](http://simplystatistics.org/2016/02/11/why-i-dont-use-ggplot2/)
- [Why I use ggplot2](http://varianceexplained.org/r/why-I-use-ggplot2/)
- [Comparing ggplot2 and base r graphics](http://flowingdata.com/2016/03/22/comparing-ggplot2-and-r-base-graphics/)

The most important takeaways are that

1. Either system is capable of producing anything the other can
2. ggplot2 is usually better for exploratory analysis

Item 2 is not universally agreed upon, and it certainly isn't true for every type of chart, but we'll take it as fact for now.
I'm not foolish enough to attempt a formal analogy here, like "matplotlib is python's base R".
But there's at least a rough comparison:
like dplyr/tidyr and ggplot2, the combination of pandas and seaborn allows for fast iteration and exploration.
When you need to, you can "drop down" into matplotlib for further refinement.

## Overview

Here's a brief sketch of the plotting landscape as of April 2016.
For some reason, plotting tools feel a bit more personal than other parts of this series so far, so I feel the need to blanket this who discussion in a caveat: this is my personal take, shaped by my personal background and tastes.
Also, I'm not at all an expert on visualization, just a consumer.
For real advice, you should [listen](http://twitter.com/mbostock) to the [experts](https://twitter.com/oceankidbilly) in this [area](https://twitter.com/arnicas).
Take this all with an extra grain or two of salt.

## [Matplotlib](http://matplotlib.org/)

Matplotlib is an amazing project, and is the foundation of pandas' built-in plotting and Seaborn.
It handles everything from the integration with various drawing backends, to several APIs handling drawing charts or adding and transforming individual glyphs (artists).
I've found knowing the [pyplot API](http://matplotlib.org/api/pyplot_api.html) useful.
You're less likely to need things like [Transforms](http://matplotlib.org/users/transforms_tutorial.html) or [artists](http://matplotlib.org/api/artist_api.html), but when you do the documentation is there.

Matplotlib has built up something of a bad reputation for being verbose.
I think that complaint is valid, but misplaced.
Matplotlib lets you control essentially anything on the figure.
An overly-verbose API just means there's an opportunity for a higher-level, domain specific, package to exist (like seaborn for statistical graphics).

## [Pandas' builtin-plotting](http://pandas.pydata.org/pandas-docs/version/0.18.0/visualization.html)

`DataFrame` and `Series` have a `.plot` namespace, with various chart types available (`line`, `hist`, `scatter`, etc.).
Pandas objects provide additional metadata that can be used to enhance plots (the Index for a better automatic x-axis then `range(n)` or Index names as axis labels for example).

And since pandas had fewer backwards-compatibility constraints, it had a bit better default aesthetics.
The [matplotlib 2.0 release](http://matplotlib.org/style_changes.html) will level this, and pandas has [deprecated its custom plotting styles](https://github.com/pydata/pandas/issues/11783), in favor of matplotlib's (technically [I just broke](https://github.com/pydata/pandas/issues/11727) it when fixing matplotlib 1.5 compatibility, so we deprecated it after the fact).

At this point, I see pandas `DataFrame.plot` as a useful exploratory tool for quick throwaway plots.

## [Seaborn](https://stanford.edu/~mwaskom/software/seaborn/)

[Seaborn](https://stanford.edu/~mwaskom/software/seaborn/), created by Michael Waskom, "provides a high-level interface for drawing attractive statistical graphics." Seaborn gives a great API for quickly exploring different visual representations of your data. We'll be focusing on that today

## [Bokeh](http://bokeh.pydata.org/en/latest/)

[Bokeh](http://bokeh.pydata.org/en/latest/) is a (still under heavy development) visualiztion library that targets the browser.

Like matplotlib, Bokeh has a few APIs at various levels of abstraction.
They have a glyph API, which I suppose is most similar to matplotlib's Artists API, for drawing single or arrays of glpyhs (circles, rectangles, polygons, etc.).
More recently they introduced a Charts API, for producing canned charts from data structures like dicts or DataFrames.

## Other Libraries

This is a (probably incomplete) list of other visualization libraries that I don't know enough about to comment on

- [Altair](https://github.com/ellisonbg/altair)
- [Lightning](http://lightning-viz.org/)
- [HoloViews](http://holoviews.org/)
- [Glueviz](http://www.glueviz.org/en/stable/)
- [vispy](http://vispy.org/)
- [bqplot](https://github.com/bloomberg/bqplot)
- [Plotly](https://plot.ly/python/)

It's also possible to use Javascript tools like D3 directly in the Jupyter notebook, but we won't go into those today.

## Examples

I do want to pause and explain the type of work I'm doing with these packages.
The vast majority of plots I create are for exploratory analysis, helping me understand the dataset I'm working with.
They aren't intended for the client (whoever that is) to see.
Occasionally that exploratory plot will evolve towards a final product that will be used to explain things to the client.
In this case I'll either polish the exploratory plot, or rewrite it in another system more suitable for the final product (in D3 or Bokeh, say, if it needs to be an interactive document in the browser).

Now that we have a feel for the overall landscape (from my point of view), let's delve into a few examples.
We'll use the `diamonds` dataset from ggplot2.
You could use Vincent Arelbundock's [RDatasets package](https://github.com/vincentarelbundock/Rdatasets) to find it (`pd.read_csv('http://vincentarelbundock.github.io/Rdatasets/csv/ggplot2/diamonds.csv')`), but I wanted to checkout [feather](https://github.com/wesm/feather).


```python
import os
import feather
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if int(os.environ.get("MODERN_PANDAS_EPUB", 0)):
    import prep # noqa
```


```python
%load_ext rpy2.ipython
```


```r
%%R
suppressPackageStartupMessages(library(ggplot2))
library(feather)
write_feather(diamonds, 'diamonds.fthr')
```


```python
import feather
df = feather.read_dataframe('diamonds.fthr')
df.head()
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
      <th>carat</th>
      <th>cut</th>
      <th>color</th>
      <th>clarity</th>
      <th>depth</th>
      <th>table</th>
      <th>price</th>
      <th>x</th>
      <th>y</th>
      <th>z</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.23</td>
      <td>Ideal</td>
      <td>E</td>
      <td>SI2</td>
      <td>61.5</td>
      <td>55.0</td>
      <td>326</td>
      <td>3.95</td>
      <td>3.98</td>
      <td>2.43</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.21</td>
      <td>Premium</td>
      <td>E</td>
      <td>SI1</td>
      <td>59.8</td>
      <td>61.0</td>
      <td>326</td>
      <td>3.89</td>
      <td>3.84</td>
      <td>2.31</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.23</td>
      <td>Good</td>
      <td>E</td>
      <td>VS1</td>
      <td>56.9</td>
      <td>65.0</td>
      <td>327</td>
      <td>4.05</td>
      <td>4.07</td>
      <td>2.31</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.29</td>
      <td>Premium</td>
      <td>I</td>
      <td>VS2</td>
      <td>62.4</td>
      <td>58.0</td>
      <td>334</td>
      <td>4.20</td>
      <td>4.23</td>
      <td>2.63</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.31</td>
      <td>Good</td>
      <td>J</td>
      <td>SI2</td>
      <td>63.3</td>
      <td>58.0</td>
      <td>335</td>
      <td>4.34</td>
      <td>4.35</td>
      <td>2.75</td>
    </tr>
  </tbody>
</table>
</div>




```python
df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 53940 entries, 0 to 53939
    Data columns (total 10 columns):
    carat      53940 non-null float64
    cut        53940 non-null category
    color      53940 non-null category
    clarity    53940 non-null category
    depth      53940 non-null float64
    table      53940 non-null float64
    price      53940 non-null int32
    x          53940 non-null float64
    y          53940 non-null float64
    z          53940 non-null float64
    dtypes: category(3), float64(6), int32(1)
    memory usage: 2.8 MB


It's not clear to me where the scientific community will come down on Bokeh for exploratory analysis.
The ability to share interactive graphics is compelling.
The trend towards more and more analysis and communication happening in the browser will only enhance this feature of Bokeh.

Personally though, I have a lot of inertia behind matplotlib so I haven't switched to Bokeh for day-to-day exploratory analysis.

I have greatly enjoyed Bokeh for building dashboards and [webapps](http://bokeh.pydata.org/en/latest/docs/user_guide/interaction.html) with Bokeh server.
It's still young, and I've hit [some rough edges](http://stackoverflow.com/questions/36610328/control-bokeh-plot-state-with-http-request), but I'm happy to put up with some awkwardness to avoid writing more javascript.


```python
sns.set(context='talk', style='ticks')

%matplotlib inline
```

## Matplotlib

Since it's relatively new, I should point out that matplotlib 1.5 added support for plotting labeled data.


```python
fig, ax = plt.subplots()

ax.scatter(x='carat', y='depth', data=df, c='k', alpha=.15);
```


![png](modern_6_visualization_files/modern_6_visualization_13_0.png)


This isn't limited to just `DataFrame`s.
It supports anything that uses `__getitem__` (square-brackets) with string keys.
Other than that, I don't have much to add to the [matplotlib documentation](http://matplotlib.org/).

## Pandas Built-in Plotting

The metadata in DataFrames gives a bit better defaults on plots.


```python
df.plot.scatter(x='carat', y='depth', c='k', alpha=.15)
plt.tight_layout()
```


![png](modern_6_visualization_files/modern_6_visualization_17_0.png)


We get axis labels from the column names.
Nothing major, just nice.

Pandas can be more convenient for plotting a bunch of columns with a shared x-axis (the index), say several timeseries.


```python
from pandas_datareader import fred

gdp = fred.FredReader(['GCEC96', 'GPDIC96'], start='2000-01-01').read()

gdp.rename(columns={"GCEC96": "Government Expenditure",
                    "GPDIC96": "Private Investment"}).plot(figsize=(12, 6))
plt.tight_layout()
```

    /Users/taugspurger/miniconda3/envs/modern-pandas/lib/python3.6/site-packages/ipykernel_launcher.py:3: DeprecationWarning: pandas.core.common.is_list_like is deprecated. import from the public API: pandas.api.types.is_list_like instead
      This is separate from the ipykernel package so we can avoid doing imports until



![png](modern_6_visualization_files/modern_6_visualization_19_1.png)


## Seaborn

The rest of this post will focus on seaborn, and why I think it's especially great for exploratory analysis.

I would encourage you to read Seaborn's [introductory notes](https://stanford.edu/~mwaskom/software/seaborn/introduction.html#introduction), which describe its design philosophy and attempted goals. Some highlights:

> Seaborn aims to make visualization a central part of exploring and understanding data.

It does this through a consistent, understandable (to me anyway) API.

> The plotting functions try to do something useful when called with a minimal set of arguments, and they expose a number of customizable options through additional parameters.
 
Which works great for exploratory analysis, with the option to turn that into something more polished if it looks promising.

> Some of the functions plot directly into a matplotlib axes object, while others operate on an entire figure and produce plots with several panels.

The fact that seaborn is built on matplotlib means that if you are familiar with the pyplot API, your knowledge will still be useful.

Most seaborn plotting functions (one per chart-type) take an `x`, `y`, `hue`, and `data` arguments (only some are required, depending on the plot type). If you're working with DataFrames, you'll pass in strings referring to column names, and the DataFrame for `data`.


```python
sns.countplot(x='cut', data=df)
sns.despine()
plt.tight_layout()
```


![png](modern_6_visualization_files/modern_6_visualization_22_0.png)



```python
sns.barplot(x='cut', y='price', data=df)
sns.despine()
plt.tight_layout()
```


![png](modern_6_visualization_files/modern_6_visualization_23_0.png)


Bivariate relationships can easily be explored, either one at a time:


```python
sns.jointplot(x='carat', y='price', data=df, size=8, alpha=.25,
              color='k', marker='.')
plt.tight_layout()
```


![png](modern_6_visualization_files/modern_6_visualization_25_0.png)


Or many at once


```python
g = sns.pairplot(df, hue='cut')
```


![png](modern_6_visualization_files/modern_6_visualization_27_0.png)


`pairplot` is a convenience wrapper around `PairGrid`, and offers our first look at an important seaborn abstraction, the `Grid`. *Seaborn `Grid`s provide a link between a matplotlib `Figure` with multiple `axes` and features in your dataset.*

There are two main ways of interacting with grids. First, seaborn provides convenience-wrapper functions like `pairplot`, that have good defaults for common tasks. If you need more flexibility, you can work with the `Grid` directly by mapping plotting functions over each axes.


```python
def core(df, α=.05):
    mask = (df > df.quantile(α)).all(1) & (df < df.quantile(1 - α)).all(1)
    return df[mask]
```


```python
cmap = sns.cubehelix_palette(as_cmap=True, dark=0, light=1, reverse=True)

(df.select_dtypes(include=[np.number])
   .pipe(core)
   .pipe(sns.PairGrid)
   .map_upper(plt.scatter, marker='.', alpha=.25)
   .map_diag(sns.kdeplot)
   .map_lower(plt.hexbin, cmap=cmap, gridsize=20)
);
```

![png](modern_6_visualization_files/modern_6_visualization_30_1.png)


This last example shows the tight integration with matplotlib. `g.axes` is an array of `matplotlib.Axes` and `g.fig` is a `matplotlib.Figure`.
This is a pretty common pattern when using seaborn: use a seaborn plotting method (or grid) to get a good start, and then adjust with matplotlib as needed.

I *think* (not an expert on this at all) that one thing people like about the grammar of graphics is its flexibility.
You aren't limited to a fixed set of chart types defined by the library author.
Instead, you construct your chart by layering scales, aesthetics and geometries.
And using `ggplot2` in R is a delight.

That said, I wouldn't really call what seaborn / matplotlib offer that limited.
You can create pretty complex charts suited to your needs.


```python
agged = df.groupby(['cut', 'color']).mean().sort_index().reset_index()

g = sns.PairGrid(agged, x_vars=agged.columns[2:], y_vars=['cut', 'color'],
                 size=5, aspect=.65)
g.map(sns.stripplot, orient="h", size=10, palette='Blues_d');
```



![png](modern_6_visualization_files/modern_6_visualization_32_1.png)



```python
g = sns.FacetGrid(df, col='color', hue='color', col_wrap=4)
g.map(sns.regplot, 'carat', 'price');
```


![png](modern_6_visualization_files/modern_6_visualization_33_1.png)


Initially I had many more examples showing off seaborn, but I'll spare you.
Seaborn's [documentation](https://stanford.edu/~mwaskom/software/seaborn/) is thorough (and just beautiful to look at).

We'll end with a nice scikit-learn integration for exploring the parameter-space on a GridSearch object.


```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV
```

For those unfamiliar with machine learning or scikit-learn, the basic idea is your algorithm (`RandomForestClassifer`) is trying to maximize some objective function (percent of correctly classified items in this case).
There are various *hyperparameters* that affect the fit.
We can search this space by trying out a bunch of possible values for each parameter with the `GridSearchCV` estimator.


```python
df = sns.load_dataset('titanic')

clf = RandomForestClassifier()
param_grid = dict(max_depth=[1, 2, 5, 10, 20, 30, 40],
                  min_samples_split=[2, 5, 10],
                  min_samples_leaf=[2, 3, 5])
est = GridSearchCV(clf, param_grid=param_grid, n_jobs=4)

y = df['survived']
X = df.drop(['survived', 'who', 'alive'], axis=1)

X = pd.get_dummies(X, drop_first=True)
X = X.fillna(value=X.median())
est.fit(X, y);

```


```python
scores = pd.DataFrame(est.cv_results_)
scores.head()
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
      <th>mean_fit_time</th>
      <th>mean_score_time</th>
      <th>mean_test_score</th>
      <th>mean_train_score</th>
      <th>param_max_depth</th>
      <th>param_min_samples_leaf</th>
      <th>param_min_samples_split</th>
      <th>params</th>
      <th>rank_test_score</th>
      <th>split0_test_score</th>
      <th>split0_train_score</th>
      <th>split1_test_score</th>
      <th>split1_train_score</th>
      <th>split2_test_score</th>
      <th>split2_train_score</th>
      <th>std_fit_time</th>
      <th>std_score_time</th>
      <th>std_test_score</th>
      <th>std_train_score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.017463</td>
      <td>0.002174</td>
      <td>0.786756</td>
      <td>0.797419</td>
      <td>1</td>
      <td>2</td>
      <td>2</td>
      <td>{'max_depth': 1, 'min_samples_leaf': 2, 'min_s...</td>
      <td>54</td>
      <td>0.767677</td>
      <td>0.804714</td>
      <td>0.808081</td>
      <td>0.797980</td>
      <td>0.784512</td>
      <td>0.789562</td>
      <td>0.000489</td>
      <td>0.000192</td>
      <td>0.016571</td>
      <td>0.006198</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.014982</td>
      <td>0.001843</td>
      <td>0.773288</td>
      <td>0.783951</td>
      <td>1</td>
      <td>2</td>
      <td>5</td>
      <td>{'max_depth': 1, 'min_samples_leaf': 2, 'min_s...</td>
      <td>57</td>
      <td>0.767677</td>
      <td>0.804714</td>
      <td>0.754209</td>
      <td>0.752525</td>
      <td>0.797980</td>
      <td>0.794613</td>
      <td>0.001900</td>
      <td>0.000356</td>
      <td>0.018305</td>
      <td>0.022600</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.013890</td>
      <td>0.001895</td>
      <td>0.771044</td>
      <td>0.786195</td>
      <td>1</td>
      <td>2</td>
      <td>10</td>
      <td>{'max_depth': 1, 'min_samples_leaf': 2, 'min_s...</td>
      <td>58</td>
      <td>0.767677</td>
      <td>0.811448</td>
      <td>0.754209</td>
      <td>0.752525</td>
      <td>0.791246</td>
      <td>0.794613</td>
      <td>0.000935</td>
      <td>0.000112</td>
      <td>0.015307</td>
      <td>0.024780</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.015679</td>
      <td>0.001691</td>
      <td>0.764310</td>
      <td>0.760943</td>
      <td>1</td>
      <td>3</td>
      <td>2</td>
      <td>{'max_depth': 1, 'min_samples_leaf': 3, 'min_s...</td>
      <td>61</td>
      <td>0.801347</td>
      <td>0.799663</td>
      <td>0.700337</td>
      <td>0.695286</td>
      <td>0.791246</td>
      <td>0.787879</td>
      <td>0.001655</td>
      <td>0.000025</td>
      <td>0.045423</td>
      <td>0.046675</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.013034</td>
      <td>0.001695</td>
      <td>0.765432</td>
      <td>0.787318</td>
      <td>1</td>
      <td>3</td>
      <td>5</td>
      <td>{'max_depth': 1, 'min_samples_leaf': 3, 'min_s...</td>
      <td>60</td>
      <td>0.710438</td>
      <td>0.772727</td>
      <td>0.801347</td>
      <td>0.781145</td>
      <td>0.784512</td>
      <td>0.808081</td>
      <td>0.000289</td>
      <td>0.000038</td>
      <td>0.039490</td>
      <td>0.015079</td>
    </tr>
  </tbody>
</table>
</div>




```python
sns.factorplot(x='param_max_depth', y='mean_test_score',
               col='param_min_samples_split',
               hue='param_min_samples_leaf',
               data=scores);
```


![png](modern_6_visualization_files/modern_6_visualization_39_0.png)


Thanks for reading!
I want to reiterate at the end that this is just *my* way of doing data visualization.
Your needs might differ, meaning you might need different tools.
You can still use pandas to get it to the point where it's ready to be visualized!

As always, [feedback is welcome](https://twitter.com/tomaugspurger).

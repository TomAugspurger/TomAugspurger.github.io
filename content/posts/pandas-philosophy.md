---
title: "Moral Philosophy for pandas or: What is `.values`?"
date: 2018-08-14
slug: pandas-moral-philosophy
tags:
  - pandas
---

The other day, I put up a [Twitter poll](https://twitter.com/TomAugspurger/status/1026578613389455360) asking a simple question: What's the type of `series.values`?

<blockquote class="twitter-tweet" data-lang="en"><p lang="en" dir="ltr">Pop Quiz! What are the possible results for the following:<br><br>&gt;&gt;&gt; type(pandas.Series.values)</p>&mdash; Tom Augspurger (@TomAugspurger) <a href="https://twitter.com/TomAugspurger/status/1026578613389455360?ref_src=twsrc%5Etfw">August 6, 2018</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 

I was a bit limited for space, so I'll expand on the options here. Choose as many as you want.

1. NumPy ndarray
2. pandas Categorical (or all of the above)
3. An Index or any of it's subclasses (DatetimeIndex, CategoricalIndex, RangeIndex, etc.) (or all of the above)
4. None or all of the above

I was prompted to write this post because *a.)* this is an (unfortunately) confusing topic and *b.)* it's undergoing a lot of change right now (and, *c.)* I had this awesome title in my head).

## The Answer

Unfortunately I kind of messed up the poll. Things are even more complex than I initially thought.

As best I can tell, the possible types for ``series.values`` are

- NumPy ndarray
- pandas Categorical
- pandas SparseArray (I forgot about this one in the poll)

So going with the cop-out "best-available" answer, I would have said that *2* was the best answer in the poll.
SparseArray is *technically* and ndarray subclass (for now), so *technically* 2 is correct, but that's a few too many *technically*s for me.

## The Explanation

So, that's a bit of a mess. How'd we get here? Or, stepping back a bit, what even is an array? What's a dataframe?

NumPy arrays are N-dimensional and *homogenous*. Every element in the array has to have the same data type.

Pandas dataframes are 2-dimensional and *heterogenous*. Different columns can have different data types. But every element in a single column (Series) has the same data type.
I like to think of DataFrames as containers for Series.
Stepping down a dimension, I think of Series as containers for 1-D arrays.
In an ideal world, we could say Series are containers for NumPy ararys, but that's not *quite* the case.

While there's a lot of overlap between the pandas and NumPy communites, there are still differences.
Pandas users place different value on different features, so pandas has restricted and *extended* NumPy's type system in a few directions.
For example, early Pandas users (many of them in the financial sector) needed datetimes with timezones, but didn't really care about lower-precision timestamps like `datetime64[D]`.
So pandas limited its scope to just nanosecond-precision datetimes (`datetime64[ns]`) and extended it with some metedata for the timezone.
Likewise for Categorical, period, sparse, interval, etc.

So back to `Series.values`; pandas had a choice: should `Series.values` always be a NumPy array, even if it means losing information like the timezone or categories, and even if it's slow or could exhaust your memory (large categorical or sparse arrays)?
Or should it faithfully represent the data, even if that means not returning an ndarray?

I don't think there's a clear answer to this question. Both options have their downsides.
In the end, we ended up with a messy compromise, where some things return ndarrays, some things return something else (Categorical), and some things do a bit of conversion before returning an `ndarary`.

For example, off the top of your head, do you know what the type of `Series.values` is for timezone-aware data?

```python
In [2]: pd.Series(pd.date_range('2017', periods=4, tz='US/Eastern'))
Out[2]:
0   2017-01-01 00:00:00-05:00
1   2017-01-02 00:00:00-05:00
2   2017-01-03 00:00:00-05:00
3   2017-01-04 00:00:00-05:00
dtype: datetime64[ns, US/Eastern]

In [3]: pd.Series(pd.date_range('2017', periods=4, tz='US/Eastern')).values
Out[3]:
array(['2017-01-01T05:00:00.000000000', '2017-01-02T05:00:00.000000000',
       '2017-01-03T05:00:00.000000000', '2017-01-04T05:00:00.000000000'],
      dtype='datetime64[ns]')
```

With the wisdom of Solomon, we decided to have it both ways; the values are converted to UTC and the timezone is dropped.
I don't think anyone would claim this is ideal, but it was backwards compatibile-ish.
Given the constraints, it wasn't the worst choice in the world.

## The Near Future

In pandas 0.24, we'll (hopefully) have a good answer for what `series.values` is: a NumPy array or an [ExtensionArray](http://pandas-docs.github.io/pandas-docs-travis/extending.html#extension-types).
For regular data types represented by NumPy, you'll get an ndarray.
For extension types (implemented in pandas or elsewhere) you'll get an ExtensionArray.
If you're using `Series.values`, you can rely on the set of methods common to each.

But that raises the question: *why* are you using `.values` in the first place?
There are some legitmate use cases (disabling automatic alignment, for example),
but for many things, passing a `Series` will hopefully work as well as a NumPy array.
To users of pandas, I recommend avoiding `.values` as much as possible.
If you know that you need an ndarray, you're probably best of using `np.asarray(series)`.
That will do the right thing for any data type.

## The Far Future

I'm hopeful that some day all we'll have a common language for these data types.
There's a lot going on in the numeric Python ecosystem right now. Stay tuned!

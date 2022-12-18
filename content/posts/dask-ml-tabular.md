---
title: Tabular Data in Scikit-Learn and Dask-ML
date: 2018-09-17
slug: sklearn-dask-tabular
---

Scikit-Learn 0.20.0 will contain some nice new features for working with tabular data.
This blogpost will introduce those improvements with a small demo.
We'll then see how Dask-ML was able to piggyback on the work done by scikit-learn to offer a version that works well with Dask Arrays and DataFrames.


```python
import dask
import dask.array as da
import dask.dataframe as dd
import numpy as np
import pandas as pd
import seaborn as sns
import fastparquet
from distributed import Client
from distributed.utils import format_bytes
```

## Background

For the most part, Scikit-Learn uses NumPy ndarrays or SciPy sparse matricies for its in-memory data structures.
This is great for many reasons, but one major drawback is that you can't store *heterogenous* (AKA *tabular*) data in these containers. These are datasets where different columns of the table have different data types (some ints, some floats, some strings, etc.).

Pandas was built to work with tabular data.
Scikit-Learn was built to work with NumPy ndarrays and SciPy sparse matricies.
So there's some friction when you use the two together.
Perhaps someday things will be perfectly smooth, but it's a challenging problem that will require work from several communities to fix.
In [this PyData Chicago talk](https://www.youtube.com/watch?v=KLPtEBokqQ0), I discuss the differences between the two data models of scikit-learn and pandas, and some ways of working through it. The second half of the talk is mostly irrelevant now that `ColumnTransformer` is in scikit-learn.

## `ColumnTransformer` in Scikit-Learn


At [SciPy 2018](https://www.youtube.com/watch?v=lXGcPbmxx8Q), Joris Van den Bossche (a scikit-learn and pandas core developer) gives an update on some recent improvements to scikit-learn to make using pandas and scikit-learn together better.

The biggest addition is [`sklearn.compose.ColumnTransformer`](http://scikit-learn.org/dev/modules/generated/sklearn.compose.ColumnTransformer.html), a transformer for working with tabular data.
The basic idea is to specify pairs of `(column_selection, transformer)`. The transformer will be applied just to the selected columns, and the remaining columns can be passed through or dropped. Column selections can be integer positions (for arrays), names (for DataFrames) or a callable.

Here's a small example on the "tips" dataset.


```python
df = sns.load_dataset('tips')
df.head()
```


<div class="output">
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
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>total_bill</th>
      <th>tip</th>
      <th>sex</th>
      <th>smoker</th>
      <th>day</th>
      <th>time</th>
      <th>size</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>16.99</td>
      <td>1.01</td>
      <td>Female</td>
      <td>No</td>
      <td>Sun</td>
      <td>Dinner</td>
      <td>2</td>
    </tr>
    <tr>
      <th>1</th>
      <td>10.34</td>
      <td>1.66</td>
      <td>Male</td>
      <td>No</td>
      <td>Sun</td>
      <td>Dinner</td>
      <td>3</td>
    </tr>
    <tr>
      <th>2</th>
      <td>21.01</td>
      <td>3.50</td>
      <td>Male</td>
      <td>No</td>
      <td>Sun</td>
      <td>Dinner</td>
      <td>3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>23.68</td>
      <td>3.31</td>
      <td>Male</td>
      <td>No</td>
      <td>Sun</td>
      <td>Dinner</td>
      <td>2</td>
    </tr>
    <tr>
      <th>4</th>
      <td>24.59</td>
      <td>3.61</td>
      <td>Female</td>
      <td>No</td>
      <td>Sun</td>
      <td>Dinner</td>
      <td>4</td>
    </tr>
  </tbody>
</table>
</div>



Our target is whether the tip was larger than 15%.


```python
X = df.drop("tip", axis='columns')
y = df.tip / df.total_bill > 0.15
```

We'll make a small pipeline that one-hot encodes the categorical columns (sex, smoker, day, time) before fitting a random forest. The numeric columns (total_bill, size) will be passed through as-is.


```python
import sklearn.compose
import sklearn.ensemble
import sklearn.pipeline
import sklearn.preprocessing
```

We use `make_column_transformer` to create the `ColumnTransformer`.


```python
categorical_columns = ['sex', 'smoker', 'day', 'time']
categorical_encoder = sklearn.preprocessing.OneHotEncoder(sparse=False)

transformers = sklearn.compose.make_column_transformer(
    (categorical_columns, categorical_encoder),
    remainder='passthrough'
)
```

This is just a regular scikit-learn estimator, which can be placed in a pipeline.


```python
pipe = sklearn.pipeline.make_pipeline(
    transformers,
    sklearn.ensemble.RandomForestClassifier(n_estimators=100)
)

pipe.fit(X, y)
pipe.score(X, y)
```

<div class="output">
    <pre>
1.0
    </pre>
</div>



We've likely overfitted, but that's not really the point of this article. We're more interested in the pre-processing side of things.

## `ColumnTransformer` in Dask-ML

`ColumnTransfomrer` was added to Dask-ML in https://github.com/dask/dask-ml/pull/315.
Ideally, we wouldn't need that PR at all. We would prefer for dask's collections (and pandas dataframes) to just be handled gracefully by scikit-learn. The main blocking issue is that the Python community doesn't currently have a way to write "concatenate this list of array-like objects together" in a generic way. That's being worked on in [NEP-18](http://www.numpy.org/neps/nep-0018-array-function-protocol.html).

So for now, if you want to use `ColumnTransformer` with dask objects, you'll have to use `dask_ml.compose.ColumnTransformer`, otherwise your large Dask Array or DataFrame would be converted to an in-memory  NumPy array.

As a footnote to this section, the initial PR in Dask-ML was much longer.
I only needed to override one thing (the function `_hstack` used to glue the results back together). But that was being called from several places, and so I had to override all *those* places as well. I was able to work with the scikit-learn developers to make `_hstack` a staticmethod on `ColumnTranformer`, so any library wishing to extend `ColumnTransformer` can do so more easily now. The Dask project values working with the existing community.

## Challenges with Scaling

Many strategies for dealing with large datasets rely on processing the data in chunks.
That's the basic idea behind Dask DataFrame: a Dask DataFrame consists of many pandas DataFrames.
When you write `ddf.column.value_counts()`, Dask builds a task graph with many `pandas.value_counts`, and a final aggregation step so that you end up with the same end result.

But chunking can cause issues when there are variations in your dataset and the operation you're applying depends on the data. For example, consider scikit-learn's `OneHotEncoder`. By default, it looks at the data and creates a column for each unique value.


```python
enc = sklearn.preprocessing.OneHotEncoder(sparse=False)
enc.fit_transform([['a'], ['a'], ['b'], ['c']])
```



<div class="output">
<pre>
array([[1., 0., 0.],
       [1., 0., 0.],
       [0., 1., 0.],
       [0., 0., 1.]])
</pre>
</div>


But let's suppose we wanted to process that in chunks of two, first `[['a'], ['a']]`, then `[['b'], ['c']]`.


```python
enc.fit_transform([['a'], ['a']])
```



<div class="highlight output">
<pre>
array([[1.],
       [1.]])
</pre>
</div>



```python
enc.fit_transform([['b'], ['c']])
```


<div class="highlight output">
<pre>
array([[1., 0.],
       [0., 1.]])
</pre>
</div>


We have a problem! Two in fact:

1. The shapes don't match. The first batch only saw "a", so the output shape is `(2, 1)`. We can't concatenate these results vertically
2. The meaning of the first column of the output has changed. In the first batch, the first column meant "a" was present. In the second batch, it meant "b" was present.

If we happened to know the set of possible values *ahead* of time, we could pass those to `CategoricalEncoder`. But storing that set of possible values separate from the data is fragile. It'd be better to store the possible values in the *data type* itself.

That's exactly what pandas Categorical does. We can confidently know the number of columns in the categorical-encoded data by just looking at the type. Because this is so important in a distributed dataset context, `dask_ml.preprocessing.OneHotEncoder` differs from scikit-learn when passed categorical data: we use pandas' categorical information.

## A larger Example

We'll work with the Criteo dataset. This has a mixture of numeric and categorical features. It's also a large dataset, which presents some challenges for many pre-processing methods.

The full dataset is from http://labs.criteo.com/2013/12/download-terabyte-click-logs/.
We'll work with a sample.


```python

client = Client()
```


```python
ordinal_columns = [
    'category_0', 'category_1', 'category_2', 'category_3',
    'category_4', 'category_6', 'category_7', 'category_9',
    'category_10', 'category_11', 'category_13', 'category_14',
    'category_17', 'category_19', 'category_20', 'category_21',
    'category_22', 'category_23',
]

onehot_columns = [
    'category_5', 'category_8', 'category_12',
    'category_15', 'category_16', 'category_18',
    'category_24', 'category_25',
]

numeric_columns = [f'numeric_{i}' for i in range(13)]
columns = ['click'] + numeric_columns + onehot_columns + ordinal_columns
```

The raw data is a single large CSV. That's been split with [this script](https://gist.github.com/TomAugspurger/4a058f00b32fc049ab5f2860d03fd579#file-split_csv-py) and I took a 10% sample with [this script](https://gist.github.com/TomAugspurger/4a058f00b32fc049ab5f2860d03fd579#file-sample-py), which was written to a directory of parquet files. That's what we'll work with.


```python
sample = dd.read_parquet("data/sample-10.parquet/")

# Convert unknown categorical to known.
# See note later on.

pf = fastparquet.ParquetFile("data/sample-10.parquet/part.0.parquet")
cats = pf.grab_cats(onehot_columns)

sample = sample.assign(**{
    col: sample[col].cat.set_categories(cats[col]) for col in onehot_columns
})
```

Our goal is to predict 'click' using the other columns.


```python
y = sample['click']
X = sample.drop("click", axis='columns')
```

Now, let's lay out our pre-processing pipeline. We have three types of columns

1. Numeric columns
2. Low-cardinality categorical columns
3. High-cardinality categorical columns

Each of those will be processed differently.

1. Numeric columns will have missing values filled with the column average and standard scaled
2. Low-cardinality categorical columns will be one-hot encoded
3. High-cardinality categorical columns will be deterministically hashed and standard scaled

You'll probably want to quibble with some of these choices, but right now, I'm
just interested in the ability to do these kinds of transformations at all.

We need to define a couple custom estimators, one for hashing the values of a dask dataframe, and one for converting a dask dataframe to a dask array.


```python
import sklearn.base

def hash_block(x: pd.DataFrame) -> pd.DataFrame:
    """Hash the values in a DataFrame."""
    hashed = [
        pd.Series(pd.util.hash_array(data.values), index=x.index, name=col)
        for col, data in x.iteritems()
    ]
    return pd.concat(hashed, axis='columns')


class HashingEncoder(sklearn.base.BaseEstimator, sklearn.base.TransformerMixin):
    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        if isinstance(X, pd.DataFrame):
            return hash_block(X)
        elif isinstance(X, dd.DataFrame):
            return X.map_partitions(hash_block)
        else:
            raise ValueError("Unexpected type '{}' for 'X'".format(type(X)))


class ArrayConverter(sklearn.base.BaseEstimator, sklearn.base.TransformerMixin):
    """Convert a Dask DataFrame to a Dask Array with known lengths"""
    def __init__(self, lengths=None):
        self.lengths = lengths

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        return X.to_dask_array(lengths=self.lengths)
```

For the final stage, Dask-ML needs to have a Dask Array with known chunk lengths.
So let's compute those ahead of time, and get a bit of info about how large the dataset is while we're at it.


```python
lengths = sample['click'].map_partitions(len)
nbytes = sample.memory_usage(deep=True).sum()

lengths, nbytes = dask.compute(lengths, nbytes)
lengths = tuple(lengths)

format_bytes(nbytes)
```



<div class="output">
<pre>
'19.20 GB'
</pre>
</div>



We we'll be working with about 20GB of data on a laptop with 16GB of RAM. We'll clearly be relying on Dask to do the operations in parallel, while keeping things in a small memory footprint.


```python
from dask_ml.compose import make_column_transformer
from dask_ml.preprocessing import StandardScaler, OneHotEncoder
from dask_ml.wrappers import Incremental
from dask_ml.impute import SimpleImputer

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.linear_model import SGDClassifier
```

Now for the pipeline.


```python
onehot_encoder = OneHotEncoder(sparse=False)
hashing_encoder = HashingEncoder()
nan_imputer = SimpleImputer()

to_numeric = make_column_transformer(
    (onehot_columns, onehot_encoder),
    (ordinal_columns, hashing_encoder),
    remainder='passthrough',
)

fill_na = make_column_transformer(
    (numeric_columns, nan_imputer),
    remainder='passthrough'
)

scaler = make_column_transformer(
    (list(numeric_columns) + list(ordinal_columns), StandardScaler()),
    remainder='passthrough'
)


clf = Incremental(
    SGDClassifier(loss='log',
                  random_state=0,
                  max_iter=1000)
)

pipe = make_pipeline(to_numeric, fill_na, scaler, ArrayConverter(lengths=lengths), clf)
pipe
```




    Pipeline(memory=None,
         steps=[('columntransformer-1', ColumnTransformer(n_jobs=1, preserve_dataframe=True, remainder='passthrough',
             sparse_threshold=0.3, transformer_weights=None,
             transformers=[('onehotencoder', OneHotEncoder(categorical_features=None, categories='auto',
           dtype=<class 'numpy.float6...ion=0.1, verbose=0, warm_start=False),
          random_state=None, scoring=None, shuffle_blocks=True))])



Overall it reads pretty similarly to how we described it in prose.
We specify

1. Onehot the low-cardinality categoricals, hash the others
2. Fill missing values in the numeric columns
3. Standard scale the numeric and hashed columns
4. Fit the incremental SGD

And again, these ColumnTransformers are just estimators so we stick them in a regular scikit-learn `Pipeline` before calling `.fit`:


```python
%%time pipe.fit(X, y.to_dask_array(lengths=lengths), incremental__classes=[0, 1])
```

<div class="output">
<pre>
CPU times: user 7min 7s, sys: 41.6 s, total: 7min 48s
Wall time: 16min 42s


Pipeline(memory=None,
        steps=[('columntransformer-1', ColumnTransformer(n_jobs=1, preserve_dataframe=True, remainder='passthrough',
            sparse_threshold=0.3, transformer_weights=None,
            transformers=[('onehotencoder', OneHotEncoder(categorical_features=None, categories='auto',
        dtype=<class 'numpy.float6...ion=0.1, verbose=0, warm_start=False),
        random_state=None, scoring=None, shuffle_blocks=True))])
</pre>
</div>







## Discussion

Some aspects of this workflow could be improved.

1. Dask, fastparquet, pyarrow, and pandas don't currently have a way to
   specify the categorical dtype of a column split across many files.
   Each file (parition) is treated independently. This results in categorials
   with unknown categories in the Dask DataFrame.
   Since *we* know that the categories are all the same, we're able to read in
   the first files categories and assign those to the entire DataFrame. But this
   is a bit fragile, as it relies on an assumption not necessarily guaranteed
   by the file structure.

2. There's of IO. As written, each stage of the pipeline that
   has to see the data does a full read of the dataset. We end up reading the
   entire dataset something like 5 times.
   https://github.com/dask/dask-ml/issues/192 has some discussion on ways
   we can progress through a pipeline. If your pipeline consists entirely of
   estimators that learn incrementally, it may make sense to send each block
   of data through the entire pipeline, rather than sending all the data to
   the first step, then all the data to the second, and so on.
   I'll note, however, that you can avoid the redundant IO by loading your
   data into distributed RAM on a Dask cluster. But I was just trying things
   out on my laptop.

Still, it's worth noting that we've successfully fit a reasonably complex pipeline on a larger-than-RAM dataset using our laptop. That's something!

ColumnTransformer will be available in scikit-learn 0.20.0.
This also contains the changes for [distributed joblib](sklearn-dask-tabular) I blogged about earlier.
The [first release candidate](https://pypi.org/project/scikit-learn/0.20rc1/) is available now.

For more, visit the [Dask](http://docs.dask.org), [Dask-ML](http://ml.dask.org), and [scikit-learn](http://scikit-learn.org/dev/modules/generated/sklearn.compose.ColumnTransformer.html) documentation.

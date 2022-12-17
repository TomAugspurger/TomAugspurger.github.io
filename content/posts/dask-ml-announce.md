---
title: dask-ml
date: 2017-10-26
slug: dask-ml-announce
---

Today we released the first version of ``dask-ml``, a library for parallel and
distributed machine learning. Read the [documentation][docs] or install it with

```
pip install dask-ml
```

Packages are currently building for conda-forge, and will be up later today.

```
conda install -c conda-forge dask-ml
```

## The Goals

[dask][dask] is, to quote the docs, "a flexible parallel computing library for
analytic computing." ``dask.array`` and ``dask.dataframe`` have done a great job
scaling NumPy arrays and pandas dataframes; ``dask-ml`` hopes to do the same in
the machine learning domain.

Put simply, we want

```python
est = MyEstimator()
est.fit(X, y)
```

to work well in parallel and potentially distributed across a cluster. `dask`
provides us with the building blocks to do that.

## What's Been Done

`dask-ml` collects some efforts that others already built:

- [distributed joblib](http://dask-ml.readthedocs.io/en/latest/joblib.html):
  scaling out some scikit-learn operations to clusters (from
  `distributed.joblib`)
- [hyper-parameter
  search](http://dask-ml.readthedocs.io/en/latest/hyper-parameter-search.html):
  Some drop in replacements for scikit-learn's `GridSearchCV` and
  `RandomizedSearchCV` classes (from `dask-searchcv`)
- [distributed GLMs](http://dask-ml.readthedocs.io/en/latest/glm.html): Fit
  large Generalized Linear Models on your cluster (from `dask-glm`)
- [dask + xgboost](http://dask-ml.readthedocs.io/en/latest/xgboost.html): Peer a
  `dask.distributed` cluster with XGBoost running in distributed mode (from
  `dask-xgboost`)
- [dask + tensorflow](http://dask-ml.readthedocs.io/en/latest/tensorflow.html):
  Peer a `dask.distributed` cluster with TensorFlow running in distributed mode
  (from `dask-tensorflow`)
- [Out-of-core learning in
  pipelines](http://dask-ml.readthedocs.io/en/latest/incremental.html): Reuse
  scikit-learn's out-of-core `.partial_fit` API in pipelines (from
  `dask.array.learn`)

In addition to providing a single home for these existing efforts, we've
implemented some algorithms that are designed to run in parallel and distributed
across a cluster.

- [`KMeans`](http://dask-ml.readthedocs.io/en/latest/modules/generated/dask_ml.cluster.KMeans.html#dask_ml.cluster.KMeans):
  Uses the `k-means||` algorithm for initialization, and a parallelized Lloyd's
  algorithm for the EM step.
- [Preprocessing](http://dask-ml.readthedocs.io/en/latest/modules/api.html#module-dask_ml.preprocessing):
  These are estimators that can be dropped into scikit-learn Pipelines, but they
  operate in parallel on dask collections. They'll work well on datasets in
  distributed memory, and may be faster for NumPy arrays (depending on the
  overhead from parallelizing, and whether or not the scikit-learn
  implementation is already parallel).
  
## Help Contribute!

Scikit-learn is a robust, mature, stable library. `dask-ml` is... not. Which
means there are plenty of places to contribute! Dask makes writing parallel and
distributed implementations of algorithms fun. For the most part, you don't even
have to think about "where's my data? How do I parallelize this?" Dask does that
for you.

Have a look at the [issues](https://github.com/dask/dask-ml/issues) or propose a
new one. I'd love to hear issues that you've run into when scaling the
"traditional" scientific python stack out to larger problems.

[docs]: http://dask-ml.readthedocs.io/en/latest/
[repo]: https://github.com/dask/dask-ml
[dask]: http://dask.pydata.org/en/latest/

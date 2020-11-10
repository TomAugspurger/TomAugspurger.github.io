---
title: Scalable Machine Learning (Part 3): Parallel
date: 2017-09-16
slug: scalable-ml-03
status: draft
---

*This work is supported by [Anaconda, Inc.](https://www.anaconda.com/) and the
Data Driven Discovery Initiative from the [Moore Foundation](https://www.moore.org/).*

This is part three of my series on scalable machine learning.

- [Small Fit, Big Predict](scalable-ml-01)
- [Scikit-Learn Partial Fit](scalable-ml-02)
- [Parallel Machine Learning](scalable-ml-03)

You can download a notebook of this post [here][notebook].

---

In [part one](scalable-ml-01), I talked about the type of constraints that push
us to parallelize or distribute a machine learning workload. Today, we'll be
talking about the second constraint, "I'm constrained by time, and would like to
fit more models at once, by using all the cores of my laptop, or all the
machines in my cluster".

## An Aside on Parallelism

In the case of Python, we have two main avenues of parallelization (which we'll
roughly define as using multiple "workers" to do some "work" in less time).
Those two avenues are

1. multi-threading
2. multi-processing

For python, the most important differences are that

1. multi-threaded code can *potentially* be limited by the GIL
2. multi-processing code requires that data be serialized between processes

The GIL is the "Global Interpreter Lock", an implementation detail of CPython
that means only one thread in your python process can be executing python code
at once.

[This talk](https://www.youtube.com/watch?v=9zinZmE3Ogk) by Python
core-developer Raymond Hettinger does a good job summarizing things for Python,
with an important caveat: much of what he says about the GIL doesn't apply to
the *scientific* python stack. NumPy, scikit-learn, and much of pandas release
the GIL and can run multi-threaded, using shared memory and so avoiding
serialization costs. I'll highlight his quote, which summarizes the
situation:

>> Your weakness is your strength, and your strength is your weakness

> The strength of threads is shared state. The weakness of threads is shared
> state.

Another wrinkle here is that when you move to a distributed cluster, you *have*
to have multiple processes. And communication between processes becomes even
more expensive since you'll have network overhead to worry about, in addition to
the serialization costs.

Fortunately, modules like `concurrent.futures` and libraries like `dask` make it
easy to swap one mode in for another. Let's make a little dask array:

```{python}
import dask.array as da
import dask
import dask.threaded
import dask.multiprocessing

X = da.random.uniform(size=(10000, 10), chunks=(1000, 10))
result = X / (X.T @ X).sum(1)
```

We can swap out the scheduler with a context-manager:

```{python}
%%time
with dask.set_options(get=dask.threaded.get):
    # threaded is the default for dask.array anyway
    result.compute()
```

```{python}
%%time
with dask.set_options(get=dask.multiprocessing.get):
    result.compute()
```

Every dask collection (`dask.array`, `dask.dataframe`, `dask.bag`) has a default
scheduler that typically works well for the kinds of operations it does. For
`dask.array` and `dask.dataframe`, the shared-memory threaded scheduler is used.

## Cost Models

In [this talk](https://www.youtube.com/watch?v=tC94Mkg-oJU), Simon Peyton Jones
talks about parallel and distributed computing for Haskell. He stressed
repeatedly that there's no silver bullet when it comes to parallelism. The type
of parallelism appropriate for a web server, say, may be different than the type
of parallelism appropriate for a machine learning algorithm.

I mention all this, since we're about to talk about parallel machine learning.
*In general*, for small data and many models you'll want to use the threaded
scheduler. For bigger data (larger than memory), you'll want want to use the
distributed scheduler. Assuming the underlying NumPy, SciPy, scikit-learn, or
pandas operation releases the GIL, you'll be able to get nice speedups without
the cost of serialization. But again, there isn't a silver bullet here, and the
best type of parallelism will depend on your particular problem.

## Where to Parallelize

In a typical machine-learning workflow, there are typically ample opportunities for
parallelism.

1. Over Hyper-parameters (one fit per combination of parameters)
2. Over Cross-validation folds (one fit per fold)
3. Within an algorithm (for some algorithms)

Scikit-learn already uses parallelism in many places, anywhere you see an
`n_jobs` keyword.

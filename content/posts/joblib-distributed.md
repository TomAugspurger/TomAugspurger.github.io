---
title: Easy distributed training with Joblib and dask
date: 2018-02-05
slug: distributed-joblib
aliases:
  /distributed-joblib.html
---

*This work is supported by [Anaconda Inc](http://anaconda.com/) and the Data
Driven Discovery Initiative from the [Moore
Foundation](https://www.moore.org/).*

This past week, I had a chance to visit some of the scikit-learn developers at
Inria in Paris. It was a fun and productive week, and I'm thankful to them for
hosting me and Anaconda for sending me there. This article will talk about some
improvements we made to improve training scikit-learn models using a cluster.

Scikit-learn uses [joblib](https://pythonhosted.org/joblib/parallel.html) for
simple parallelism in many places. Anywhere you pass an ``n_jobs`` keyword,
scikit-learn is internally calling `joblib.Parallel(...)`, and doing a batch of
work in parallel. The estimator may have an embarrassingly parallel step
internally (fitting each of the trees in a `RandomForest` for example). Or your
meta-estimator like `GridSearchCV` may try out many combinations of
hyper-parameters in parallel.

You can think of joblib as a broker between the user and the algorithm author.
The user comes along and says, "I have `n_jobs` cores, please use them!".
Scikit-Learn says "I have all these embarrassingly parallel tasks to be run as
part of fitting this estimator." Joblib accepts the cores from the user and the
tasks from scikit-learn, runs the tasks on the cores, and hands the completed
tasks back to scikit-learn.

Joblib offers a few "backends" for how to do your parallelism, but they all boil
down to using many processes versus using many threads.

## Parallelism in Python

A quick digression on *single-machine* parallelism in Python. We can't say up
front that using threads is always better or worse than using processes.
Unfortunately the relative performance depends on the specific workload. But we
do have some general heuristics that come down to serialization overhead and
Python's Global Interpreter Lock (GIL).

The GIL is part of CPython, the C program that interprets and runs your Python
program. It limits your Python process so that only one thread is executing
*Python* at once, defeating your parallelism. Fortunately, much of the numerical
Python stack is written in C, Cython, C++, Fortran, or numba, and *may* be able
to release the GIL. This means your "Python" program, which is calling into
Cython or C via NumPy or pandas, can get real thread-based parallelism without
being limited by the GIL. The main caveat here that manipulating strings or
Python objects (lists, dicts, sets, etc) typically requires holding the GIL.

So, if we have the *option* of choosing threads or processes, which do we want?
For most numeric / scientific workloads, threads are better than processes
because of *shared memory*. Each thread in a thread-pool can view (and modify!)
the *same* large NumPy array. With multiple processes, data must be *serialized*
between processes (perhaps using pickle). For large arrays or dataframes this
can be slow, and it may blow up your memory if the data a decent fraction of
your machine's RAM. You'll have a full copy in each processes.

See [Matthew Rocklin's
article](http://matthewrocklin.com/blog/work/2015/03/10/PyData-GIL) and [David
Beazley's page](http://www.dabeaz.com/GIL/) if you want to learn more.

## Distributed Training with dask.distributed

For a while now, you've been able to use
[`dask.distributed`](http://distributed.readthedocs.io/en/latest/) as a
backend for joblib. This means that in *most* places scikit-learn offers an
`n_jobs` keyword, you're able to do the parallel computation on your cluster.

This is great when

1. Your dataset is not too large (since the data must be sent to each worker)
2. The runtime of each task is long enough that the overhead of serializing the
   data across the network to the worker doesn't dominate the runtime
3. You have many parallel tasks to run (else, you'd just use a local thread or
   process pool and avoid the network delay)

Fitting a `RandomForest` is a good example of this. Each tree in a forest may be
built independently of every other tree. This next code chunk shows how you can
parallelize fitting a `RandomForestClassifier` across a cluster, though as
discussed later this won't work on the currently released versions of
scikit-learn and joblib.

```python
from sklearn.externals import joblib
from dask.distributed import Client
import distributed.joblib  # register the joblib backend

client = Client('dask-scheduler:8786')

with joblib.parallel_backend("dask", scatter=[X_train, y_train]):
    clf.fit(X_train, y_train)
```

The `.fit` call is parallelized across all the workers in your cluster. Here's
the distributed dashboard during that training.

<video src="/images/distributed-joblib-cluster.webm" autoplay controls loop width="80%">
  Your browser doesn't support HTML5 video.
</video>

The center pane shows the task stream as they complete. Each rectangle is a
single task, building a single tree in a random forest in this case. Workers are
represented vertically. My cluster had 8 workers with 4 cores each, which means
up to 32 tasks can be processed simultaneously. We fit the 200 trees in about 20
seconds.

## Changes to Joblib

Above, I said that distributed training worked in *most* places in scikit-learn.
Getting it to work everywhere required a bit more work, and was part of last
week's focus.

First, `dask.distributed`'s joblib backend didn't handle *nested* parallelism
well. This may occur if you do something like

```pytohn
gs = GridSearchCV(Estimator(n_jobs=-1), n_jobs=-1)
gs.fit(X, y)
```

Previously, that caused deadlocks. Inside `GridSearchCV`, there's a call like

```python
# In GridSearchCV.fit, the outer layer
results = joblib.Parallel(n_jobs=n_jobs)(fit_estimator)(...)
```

where `fit_estimator` is a function that *itself* tries to do things in parallel

```python
# In fit_estimator, the inner layer
results = joblib.Parallel(n_jobs=n_jobs)(fit_one)(...)
```

So the outer level kicks off a bunch of `joblib.Parallel` calls, and waits
around for the results. For each of those `Parallel` calls, the inner level
tries to make a bunch of `joblib.Parallel` calls. When joblib tried to start the
inner ones, it would ask the distributed scheduler for a free worker. But all
the workers were "busy" waiting around for the outer `Parallel` calls to finish,
which weren't progressing because there weren't any free workers! Deadlock!

`dask.distributed` has a solution for this case (workers
[`secede`](http://distributed.readthedocs.io/en/latest/api.html#distributed.secede)
from the thread pool when they start a long-running `Parllel` call, and
[`rejoin`](http://distributed.readthedocs.io/en/latest/api.html#distributed.rejoin)
when they're done), but we needed a way to negotiate with joblib about when the
`secede` and `rejoin` should happen. Joblib now has an API for backends to
control some setup and teardown around the actual function execution. This work
was done in [Joblib #538](https://github.com/joblib/joblib/pull/538) and
[dask-distributed #1705](https://github.com/dask/distributed/pull/1705).

Second, some places in scikit-learn hard-code the backend they want to use in
their `Parallel()` call, meaning the cluster isn't used. This may be because the
algorithm author knows that one backend performs better than others. For
example, `RandomForest.fit` performs better with threads, since it's purely
numeric and releases the GIL. In this case we would say the `Parallel` call
*prefers* threads, since you'd get the same result with processes, it'd just be
slower.

Another reason for hard-coding the backend is if the *correctness* of the
implementation relies on it. For example, `RandomForest.predict` preallocates
the output array and mutates it from many threads (it knows not to mutate the
same place from multiple threads). In this case, we'd say the `Parallel` call
*requires* shared memory, because you'd get an incorrect result using processes.

The solution was to enhance `joblib.Parallel` to take two new keywords, `prefer`
and `require`. If a `Parallel` call *prefers* threads, it'll use them, unless
it's in a context saying "use this backend instead", like

```python
def fit(n_jobs=-1):
    return joblib.Parallel(n_jobs=n_jobs, prefer="threads")(...)


with joblib.parallel_backend('dask'):
    # This uses dask's workers, not threads
    fit()
```

On the other hand, if a `Parallel` requires a specific backend, it'll get it.

```python
def fit(n_jobs=-1):
    return joblib.Parallel(n_jobs=n_jobs, require="sharedmem")(...)

with joblib.parallel_backend('dask'):
    # This uses the threading backend, since shared memory is required
    fit()
```

This is a elegant way to negotiate a compromise between

1. The *user*, who knows best about what resources are available, as specified
   by the `joblib.parallel_backend` context manager. And,
2. The *algorithm author*, who knows best about the GIL handling and shared
   memory requirements.

This work was done in [Joblib #602](https://github.com/joblib/joblib/pull/602).

After the next joblib release, scikit-learn will be updated to use these options
in places where the backend is currently hard-coded. My example above used a
branch with those changes.

Look forward for these changes in the upcoming joblib, dask, and scikit-learn
releases. As always, let me know if you have any feedback.

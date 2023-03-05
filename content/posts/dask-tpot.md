---
title: Distributed Auto-ML with TPOT with Dask
date: 2018-08-30
slug: distributed-tpot
aliases:
  - /distributed-tpot.html
---

*This work is supported by [Anaconda Inc][anaconda].*

This post describes a recent improvement made to [TPOT][tpot]. TPOT is an
[automated machine learning][auto-ml] library for Python. It does some feature
engineering and hyper-parameter optimization for you. TPOT uses [genetic
algorithms][ga] to evaluate which models are performing well and how to choose
new models to try out in the next generation.

## Parallelizing TPOT

In [TPOT-730][tpot-730], we made some modifications to TPOT to support
distributed training. As a TPOT user, the only changes you need to make to your
code are

1. Connect a client to your Dask Cluster
2. Specify the `use_dask=True` argument to your TPOT estimator

From there, all the training will use your cluster of machines. This screencast
shows an example on an 80-core Dask cluster.

<iframe width="560" height="315" src="https://www.youtube-nocookie.com/embed/uyx9nBuOYQQ?rel=0" frameborder="0" allow="autoplay; encrypted-media" allowfullscreen></iframe> 

## Commentary

Fitting a TPOT estimator consists of several stages. The bulk of the time is
spent evaluating individual scikit-learn pipelines. Dask-ML already had code for
splitting apart a scikit-learn `Pipeline.fit` call into individual tasks. This
is used in Dask-ML's hyper-parameter optimization to [avoid repeating
work][repeated-work]. We were able to drop-in Dask-ML's fit and scoring method
for the one already used in TPOT. That small change allows fitting the many
individual models in a generation to be done on a cluster.

There's still some room for improvement. Internal to TPOT, some time is spent
determining the next set of models to try out (this is the "mutation and
crossover phase"). That's not (yet) been parallelized with Dask, so you'll
notice some periods of inactivity on the cluster.

## Next Steps

This will be available in the next release of TPOT. You can try out a small
example now on the [dask-examples binder][binder].

Stepping back a bit, I think this is a good example of how libraries can use
Dask internally to parallelize workloads for their users. Deep down in TPOT
there was a single method for fitting many scikit-learn models on some data and
collecting the results. Dask-ML has code for *building a task graph* that does
the same thing. We were able to swap out the eager TPOT code for the lazy dask
version, and get things distributed on a cluster. Projects like [xarray][xarray]
have been able to do a similar thing with [dask Arrays in place of NumPy
arrays][xarray-dask]. If Dask-ML hadn't already had that code,
[`dask.delayed`][delayed] could have been used instead.

If you have a library that you think could take advantage of Dask, please [reach
out][dask]!


[anaconda]:https://www.anaconda.com/ 
[auto-ml]: https://en.wikipedia.org/wiki/Automated_machine_learning
[binder]: https://mybinder.org/v2/gh/dask/dask-examples/master?filepath=machine-learning%2Ftpot.ipynb
[dask]: https://github.com/dask/dask
[delayed]: http://dask.pydata.org/en/latest/delayed.html
[ga]: https://en.wikipedia.org/wiki/Genetic_programming
[repeated-work]: https://dask.github.io/dask-ml/hyper-parameter-search.html#avoid-repeated-work
[tpot-730]: https://github.com/EpistasisLab/tpot/pull/730
[tpot]: https://epistasislab.github.io/tpot/
[xarray-dask]: http://xarray.pydata.org/en/stable/dask.html
[xarray]: http://xarray.pydata.org/en/stable/

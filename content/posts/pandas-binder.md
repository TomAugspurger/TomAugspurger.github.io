Title: pandas + binder
Date: 2019-07-21
tags:
  - pandas
This post describes the start of a journey to get pandas' documentation running
on Binder. The end result is this nice button:

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/TomAugspurger/pandas-binder/master?filepath=build%2Fjupyter%2Fgetting_started%2F10min.ipynb)

---

For a while now I've been jealous of [Dask's examples
repository](https://github.com/dask/dask-examples). That's a repository containing a
collection of Jupyter notebooks demonstrating Dask in action. It stitches
together some tools to present a set of documentation that is both viewable
as a static site at [examples.dask.org](https://examples.dask.org), and as a executable notebooks
on [mybinder](https://mybinder.org/v2/gh/dask/dask-examples/master?urlpath=lab).

A bit of background on binder: it's a tool for creating a shareable computing
environment. This is perfect for introductory documentation. A prospective user
may want to just try out a library to get a feel for it before they commit to
installing. Binder*Hub* is a tool for deploying binder services. You point a
binderhub deployment (like [mybinder](https://mybinder.org)) at a git repository
with a collection of notebooks and an environment specification, and out comes
your executable documentation.

Thanks to a lot of hard work by contributors and maintainers, the code examples
in pandas' documentation are already runnable (and this is verified on each
commit). We use the [IPython Sphinx
Extension](https://ipython.readthedocs.io/en/stable/sphinxext.html) to execute
examples and include their output. We write documentation like

```
.. ipython:: python

   import pandas as pd
   s = pd.Series([1, 2])
   s
```

Which is then *executed* and rendered in the HTML docs as

```python
In [1]: import pandas as pd

In [2]: s = pd.Series([1, 2, 3])

In [3]: s
Out[3]:
0    1
1    2
2    3
dtype: int64
```

So we have the most important thing: a rich source of documentation that's
already runnable.

There were a couple barriers to just pointing binder at
`https://github.com/pandas-dev/pandas`, however. First, binder builds on top of
a tool called [repo2docker](https://repo2docker.readthedocs.io/en/latest/). This
is what takes your Git repository and turns it into a Docker image that users
will be dropped into. When someone visits the URL, binder will first check to
see if it's built a docker image. If it's already cached, then that will just be
loaded. If not, binder will have to clone the repository and build it from
scratch, a time-consuming process. Pandas receives 5-10 commits per day, meaning
many users would visit the site and be stuck waiting for a 5-10 minute docker
build.[^1]

Second, pandas uses Sphinx and ReST for its documentation. Binder needs a collection
of Notebooks. Fortunately, the fine folks at [QuantEcon](https://quantecon.org)
(a fellow NumFOCUS project) wrote
[`sphinxcontrib-jupyter`](https://sphinxcontrib-jupyter.readthedocs.io), a tool
for turning ReST files to Jupyter notebooks. Just what we needed.

So we had some great documentation that already runs, and a tool for converting
ReST files to Jupyter notebooks. All the pieces were falling into place!

Unfortunately, my first attempt failed. `sphinxcontrib-jupyter` looks for directives
like


```rst
.. code:: python
```

while pandas uses

```rst
.. ipython:: python

```

I started slogging down a path to teach `sphinxcontrib-jupyter` how to recognize
the IPython directive pandas uses when my kid woke up from his nap. Feeling
dejected I gave up.

But later in the day, I had the (obvious in hindsight) realization that we have
plenty of tools for substituting lines of text. A few (non-obvious) [lines of
bash
later](https://github.com/TomAugspurger/pandas-binder/blob/20fc3e8f52a05d4b291211a41ed3015f37758f81/Makefile#L4)
and we were ready to go. All the `.. ipython:: python` directives were now `..
code:: python`. Moral of the story: take breaks.

My work currently lives in [this repository](https://github.com/TomAugspurger/pandas-binder), and
the notebooks are runnable [on mybinder](https://mybinder.org/v2/gh/TomAugspurger/pandas-binder/master?filepath=build%2Fjupyter%2Fgetting_started%2F10min.ipynb). But the short version is

1. We include github.com/pandas-dev/pandas as a submodule (which repo2docker
   supports just fine)
2. We patch pandas Sphinx config to include sphinxcontrib-jupyter and its
   configuration
3. We patch pandas source docs to change the ipython directives to be `.. code::
   python` directives.

I'm reasonably happy with how things are shaping up. I plan to migrate my repository
to the pandas organization and propose a few changes to the pandas documentation
(like a small header pointing from the rendered HTML docs to the binder). If you'd like to follow along,
subscribe to [this pandas issue](https://github.com/pandas-dev/pandas/issues/27514).

I'm also hopeful that other projects can apply a similar approach to their documentation too.

[^1]: I realize now that binder can target a specific branch or commit. I'm not
      sure if additional commits to that repository will trigger a rebuild, but
      I suspect not. We still needed to solve problem 2 though.

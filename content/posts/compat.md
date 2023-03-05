---
title: Compatibility Code
date: 2019-12-12T00:00:00
slug: compatibility
status: draft
---

# Compatibility Code

Most libraries with dependencies will want to support multiple versions
of that dependency. But supporting old version is a pain: it requires *compatibility code*,
code that is around solely to get the same output from versions of a library. This post
gives some advice on writing compatibility code.

1. Don't write your own version parser
2. Centralize all version parsing
3. Use consistent version comparisons
4. Use Python's argument unpacking
5. Clean up unused compatibility code

## 1. Don't write your own version parser

It can be tempting just do something like

```python
if pandas.__version__.split(".")[1] >= "25":
    ...
```

But that's probably going to break, sometimes in unexpected ways. Use either ``distutils.version.LooseVersion``
or `packaging.version.parse` which handles all the edge cases.

```python
PANDAS_VERSION = LooseVersion(pandas.__version__)
```

## 2. Centralize all version parsing in a `_compat.py` file

The first section of compatibility code is typically a version check. It can be tempting
to do the version-check inline with the compatibility code

```python
if LooseVersion(pandas.__version__) >= "0.25.0":
    return pandas.concat(args, sort=False)
else:
    return pandas.concat(args)
```

Rather than that, I recommend centralizing the version checks in a central `_compat.py` file
that defines constants for each library version you need compatibility code for.

```python
# library/_compat.py
import pandas


PANDAS_VERSION = LooseVersion(pandas.__version__)
PANDAS_0240 = PANDAS_VERSION >= "0.24.0
PANDAS_0250 = PANDAS_VERSION >= "0.25.0
```

This, combined with item 3, will make it easier to clean up your code (see below).

## 3. Use consistent version comparisons

Notice that I defined constants for each pandas version, `PANDAS_0240`,
`PANDAS_0250`. Those mean "the installed version of pandas is at least this
version", since I used the `>=` comparison. You could instead define constants
like

```python
PANDAS_LT_0240 = PANDAS_VERSION < "0.24.0"
```

That works too, just ensure that you're consistent.

## 4. Use Python's argument unpacking

Python's [argument unpacking][argument unpacking] helps avoid code duplication when the
signature of a function changes.

```python
    param_grid = {"estimator__alpha": [0.1, 10]}
    if SK_022:
        kwargs = {}
    else:
        kwargs = {"iid": False}
    gs = sklearn.model_selection.GridSearchCV(clf, param_grid, cv=3, **kwargs)

```

Using `*args`, and `**kwargs` to pass through version-dependent arguments lets you
have just a single call to the callable when the only difference is the
arguments passed.

## 5. Clean up unused compatibility code

Actively developed libraries may eventually drop support for old versions
of dependency libraries. At a minimum, this involves removing the old version
from your test matrix and bumping your required version in your dependency list.
But ideally you would also clean up the now-unused compatibility code. The
strategies laid out here intend to make that as easy as possible.

Consider the following.

```python
# library/core.py
import pandas
from ._comapt import PANDAS_0250


def f(args):
    ...

    if PANDAS_0250:
        return pandas.concat(args, sort=False)
    else:
        return pandas.concat(args)
```

Now suppose it's the future and we want to drop support for pandas older than 0.25.x
Now all the conditions checking `if PANDAS_0250` are automatically true, so we'd

1. Delete `PANDAS_0250` from `_compat.py`
2. Remove the import in `core.py`
3. Remove the `if PANDAS_0250` check, and always have the True part of that
   condition
   
```python
# library/core.py
import pandas

def f(args):
    ...
    return pandas.concat(args, sort=False)
```

I acknowledge that [indirection can harm readability][indirection]. In this case
I think it's warranted for actively maintained projects. Using inline version
checks, perhaps with inconsistent comparisons, will make it harder to know when
code is now unused. When integrated over the lifetime of the project, I find the
strategies laid out here more readable.

[packaging.version.parse]: https://packaging.pypa.io/en/latest/version/
[indirection]: https://matthewrocklin.com/blog/work/2019/06/23/avoid-indirection
[argument unpacking]: https://docs.python.org/3/tutorial/controlflow.html#unpacking-argument-lists

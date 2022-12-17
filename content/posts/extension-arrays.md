---
title: Extension Arrays for Pandas
date: 2018-02-12
slug: pandas-extension-arrays
tags:
   - pandas
---

This is a status update on some enhancements for pandas. The goal of the work
is to store things that are sufficiently array-like in a pandas ``DataFrame``,
even if they aren't a regular NumPy array. Pandas already does this in a few
places for some blessed types (like `Categorical`); we'd like to open that up to
anybody.

A couple months ago, a client came to [Anaconda][anaconda] with a problem: they
have a bunch of IP Address data that they'd like to work with in pandas. They
didn't just want to make a NumPy array of IP addresses for a few reasons:

1. IPv6 addresses are 128 bits, so they can't use a specialized NumPy dtype. It
   would have to be an `object` array, which will be slow for their large
   datasets.
2. IP Addresses have special structure. They'd like to use this structure for
   special methods like `is_reserved`.
3. It's much better to put the knowledge of types in the library, rather than
   relying on analysts to know that this column of objects or strings is
   *actually* this other special type.

I wrote up a [proposal][proposal] to gauge interest from the community for
adding an IP Address dtype to pandas. The general sentiment was that an IP
addresses were too specialized for inclusion pandas (which matched my own
feelings). But, the community was interested in allowing 3rd party libraries to
define their own types and having pandas "do the right thing" when it encounters
them.

## Pandas Internals

While not technically true, you could reasonably describe a `DataFrame` as a
dictionary of NumPy arrays. There are a few complications that invalidate that
caricature , but the one I want to focus on is pandas' *extension dtypes*.

Pandas has extended NumPy's type system in a few cases. For the most part, this
involves tricking ``pandas.DataFrame`` and ``pandas.Series`` into thinking that
the object passed to it is a single array, when in fact it's multiple arrays, or
an array plus a bit of extra metadata.

1. `datetime64[ns]` *with a timezone*. A regular `numpy.datetime64[ns]` array
   (which is really just an array of integers) plus some metadata for the
   timezone.
2. `Period`: An array of integer ordinals and some metadata about the frequency.
3. `Categorical`: two arrays: one with the unique set of `categories`
   and a second array of `codes`, the positions in `categories`.
4. `Interval`: Two arrays, one for the left-hand endpoints and one for the
   right-hand endpoints.

So our definition of a `pandas.DataFrame` is now "A dictionary of NumPy arrays,
or one of pandas' extension types." Internal to pandas, we have checks for "is
this thing an extension dtype? If so take this special path." To the user, it
looks like a `Categorical` is just a regular column, but internally, it's a bit
messier.

Anyway, the upshot of my [proposal][proposal] was to make changes to pandas'
internals to support 3rd-party objects going down that "is this an extension
dtype" path.

## Pandas' Array Interface

To support external libraries defining extension array types, we defined an interface.

In [pandas-19268][interface] we laid out exactly what pandas considers
sufficiently "array-like" for an extension array type. When pandas comes across
one of these array-like objects, it avoids the previous behavior of just storing
the data in a NumPy array of objects. The interface includes things like 

- What type of scalars do you hold?
- How do I convert you to a NumPy array?
- `__getitem__`

Most things should be pretty straightforward to implement. In the test suit, we
have a 60-line implementation for storing `decimal.Decimal` objects in a
`Series`.

It's important to emphasize that pandas' `ExtensionArray` is *not* another array
implementation. It's just an agreement between pandas and your library that your
array-like object (which may be a NumPy array, many NumPy arrays, an Arrow
array, a list, anything really) that satisfies the proper semantics for storage
inside a `Series` or `DataFrame`.

With those changes, I've been able to prototype a small library (named...
[cyberpandas][cyberpandas]) for storing arrays of IP Addresses. It defines
`IPAddress`, an array-like container for IP Addresses. For this blogpost, the
only relevant implementation detail is that IP Addresses are stored as a NumPy
structured array with two uint64 fields. So we're making pandas treat this 2-D
array as a single array, like how `Interval` works. Here's a taste:

As a taste for what's possible, here's a preview of our IP Address library,
`cyberpandas`.

```python
In [1]: import cyberpandas

In [2]: import pandas as pd

In [3]: ips = cyberpandas.IPAddress([
   ...:     '0.0.0.0',
   ...:     '192.168.1.1',
   ...:     '2001:0db8:85a3:0000:0000:8a2e:0370:7334',
   ...: ])

In [4]: ips
Out[4]: IPAddress(['0.0.0.0', '192.168.1.1', '2001:db8:85a3::8a2e:370:7334'])

In [5]: ips.data
Out[5]:
array([(                  0,               0),
       (                  0,      3232235777),
       (2306139570357600256, 151930230829876)],
      dtype=[('hi', '>u8'), ('lo', '>u8')])

```

`ips` satisfies pandas' `ExtensionArray` interface, so it can be stored inside
pandas' containers.

```python
In [6]: ser = pd.Series(ips)

In [7]: ser
Out[7]:
0                         0.0.0.0
1                     192.168.1.1
2    2001:db8:85a3::8a2e:370:7334
dtype: ip
```

Note the `dtype` in that output. That's a custom dtype (like `category`) defined
*outside* pandas.

We register a [custom accessor][accessor] with pandas claiming the `.ip`
namespace (just like pandas uses `.str` or `.dt` or `.cat`):

```python
In [8]: ser.ip.isna
Out[8]:
0     True
1    False
2    False
dtype: bool

In [9]: ser.ip.is_ipv6
Out[9]:
0    False
1    False
2     True
dtype: bool
```

I'm *extremely* interested in seeing what the community builds on top of this
interface. Joris has already tested out the [Cythonized geopandas](geopandas)
extension, which stores a NumPy array of pointers to geometry objects, and
things seem great. I could see someone (perhaps you, dear reader?) building a
`JSONArray` array type for working with nested data. That combined with custom
`.json` accessor, perhaps with a [`jq`-like][jq] query language should make for
a powerful combination.

I'm also happy to have to say "Closed, out of scope; sorry." less often. Now it
can be "Closed, out of scope; do it outside of pandas." :)

## Open Source Success Story

It's worth taking a moment to realize that this was a great example of open
source at its best.

1. A company had a need for a tool. They didn't have the expertise or desire to
   build and maintain it internally, so they approached Anaconda (a for-profit
   company with a great OSS tradition) to do it for them.
2. A proposal was made *and rejected* by the pandas community. You can't just
   "buy" features in pandas if it conflicts too strongly with the long-term
   goals for the project.
3. A more general solution was found, with minimal changes to pandas itself,
   allowing anyone to do this type of extension outside of pandas.
4. We built the [cyberpandas][cyberpandas], which to users will feel like a
   first-class array type in pandas.

Thanks to the tireless reviews from the other pandas contributors, especially
Jeff Reback, Joris van den Bossche, and Stephen Hoyer. Look forward to these
changes in the next major pandas release.

[accessor]: http://pandas-docs.github.io/pandas-docs-travis/developer.html#developer-register-accessors
[anaconda]: https://www.anaconda.com/
[cyberpandas]: https://github.com/ContinuumIO/cyberpandas
[geopandas]: https://jorisvandenbossche.github.io/blog/2017/09/19/geopandas-cython/
[interface]: https://github.com/pandas-dev/pandas/pull/19268
[ipaddress]: https://docs.python.org/3/library/ipaddress.html
[jq]: https://stedolan.github.io/jq/
[proposal]: https://github.com/pandas-dev/pandas/issues/18767

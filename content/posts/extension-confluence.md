---
title: A Confluence of Extension
date: 2019-06-18
slug: confluence-extension
status: draft
---

This post describes a few protocols taking shape in the scientific Python
community. On their own, each is powerful. Together, I think they enable for an
explosion of creativity in the community.

Each of the protocols / interfaces we'll consider deal with extending.

* [NEP-13: NumPy `__array_ufunc__`](https://www.numpy.org/neps/nep-0013-ufunc-overrides.html)
* [NEP-18: NumPy `__array_function__`](https://www.numpy.org/neps/nep-0018-array-function-protocol.html)
* [Pandas Extension types](http://pandas.pydata.org/pandas-docs/stable/development/extending.html#extension-types)
* [Custom Dask Collections][dask-collections]

---

First, a bit of brief background on each. 

NEP-13 and NEP-18, each deal with using the NumPy API on non-NumPy ndarray
objects. For example, you might want to apply a ufunc like `np.log` to a Dask
array. 

```python
>>> a = da.random.random((10, 10))
>>> np.log(a)
dask.array<log, shape=(10, 10), dtype=float64, chunksize=(10, 10)>
```

Prior to NEP-13, `dask.array` needed it's own namespace of ufuncs like `da.log`,
since `np.log` would convert the Dask array to an in-memory NumPy array
(probably blowing up your machine's memory). With `__array_ufunc__` library
authors and users can all just use NumPy ufuncs, without worrying about the type of
the Array object.

While NEP-13 is limited to ufuncs, NEP-18 applies the same idea to most of the
NumPy API. With NEP-18, libraries written to deal with NumPy ndarrays may
suddenly support any object implementing `__array_function__`.

I highly recommend reading [this blog
post](https://blog.dask.org/2018/05/27/beyond-numpy) for more on the motivation
for `__array_function__`. Ralph Gommers gave a nice talk on the current state of
things at [PyData Amsterdam 2019](https://youtu.be/HVLPJnvInzM), though this is
an active area of development.

Pandas added extension types to allow third-party libraries to solve
domain-specific problems in a way that gels nicely with the rest of pandas. For
example, cyberpandas handles network data, while geopandas handles geographic
data. When both implement extension arrays it's possible to operate on a dataset
with a mixture of geographic and network data in the same DataFrame.

Finally, Dask defines a [Collections Interface][dask-collections] so that any
object can be a first-class citizen within Dask. This is what ensures [XArray's][xarray]
DataArray and Dataset objects work well with Dask.

## `Series.__array_ufunc__`

Now, onto the fun stuff: combining these interfaces across objects and
libraries. https://github.com/pandas-dev/pandas/pull/23293 is a pull request
adding `Series.__array_ufunc__`. There are a few subtleties, but the basic idea
is that a ufunc applied to a Series should

1. Unbox the array (ndarray or extension array) from the Series
2. Apply the ufunc to the Series (honoring the array's `__array_ufunc__` if
   needed)
3. Rebox the output in a Series (with the original index and name)

For example, pandas' `SparseArray` implements `__array_ufunc__`. It works by
calling the ufunc twice, once on the sparse values (e.g. the non-zero values),
and once on the scalar `fill_value`. The result is a new `SparseArray` with the
same memory usage. With that PR, we achieve the same thing when operating on a
Series containing an ExtensionArray.

```python
>>> ser = pd.Series(pd.SparseArray([-10, 0, 10] + [0] * 100000))
>>> ser
0        -10
1          0
2         10
3          0
4          0
          ..
99998      0
99999      0
100000     0
100001     0
100002     0
Length: 100003, dtype: Sparse[int64, 0]

>>> n [20]: np.sign(ser)
0        -1
1         0
2         1
3         0
4         0
         ..
99998     0
99999     0
100000    0
100001    0
100002    0
Length: 100003, dtype: Sparse[int64, 0]
```

Previously, that would have converted the `SparseArray` to a *dense* NumPy
array, blowing up your memory, slowing things down, and giving the incorrect result.

## `IPArray.__array_function__`

To demonstrate `__array_function__`, we'll implement it on `IPArray`.

```python
    def __array_function__(self, func, types, args, kwargs):
        cls = type(self)
        if not all(issubclass(t, cls) for t in types):
            return NotImplemented
        return HANDLED_FUNCTIONS[func](*args, **kwargs)
```

`IPArray` is pretty domain-specific, so we place ourself down at the bottom
priority by returning `NotImplemented` if there are any types we don't recognize
(we might consider handling Python's stdlib `ipaddres.IPv4Address` and
`ipaddres.IPv6Address` objects too).


And then we start implementing the interface. For example, `concatenate`.

```python
@implements(np.concatenate)
def concatenate(arrays, axis=0, out=None):
    if axis != 0:
        raise NotImplementedError(f"Axis != 0 is not supported. (Got {axis}).")
    return IPArray(np.concatenate([array.data for array in arrays]))
```


With this, we can successfully concatenate two IPArrays

```python
>>> a = cyberpandas.ip_range(4)
>>> b = cyberpandas.ip_range(10, 14)
>>> np.concatenate([a, b])
IPArray(['0.0.0.0', '0.0.0.1', '0.0.0.2', '0.0.0.3', '0.0.0.10', '0.0.0.11', '0.0.0.12', '0.0.0.13'])
```

## Extending Dask

Finally, we may wish to make `IPArray` work well with `dask.dataframe`, to do
normal cyberpandas operations in parallel, possibly distributed on a cluster.
This requires a few changes:

1. Updating `IPArray` to work on either NumPy or Dask arrays
2. Implementing the Dask Collections interface on `IPArray`.
3. Registering an `ip` accessor with `dask.dataframe`, just like with `pandas`.

This is demonstrated in https://github.com/ContinuumIO/cyberpandas/pull/39

```python
In [28]: ddf
Out[28]:
Dask DataFrame Structure:
                 A
npartitions=2
0               ip
6              ...
11             ...
Dask Name: from_pandas, 2 tasks

In [29]: ddf.A.ip.netmask()
Out[29]:
Dask Series Structure:
npartitions=2
0      ip
6     ...
11    ...
Name: A, dtype: ip
Dask Name: from-delayed, 22 tasks

In [30]: ddf.A.ip.netmask().compute()
Out[30]:
0     255.255.255.255
1     255.255.255.255
2     255.255.255.255
3     255.255.255.255
4     255.255.255.255
5     255.255.255.255
6     255.255.255.255
7     255.255.255.255
8     255.255.255.255
9     255.255.255.255
10    255.255.255.255
11    255.255.255.255
dtype: ip
```

## Conclusion

I think that these points of extension.


[dask-collections]: https://docs.dask.org/en/latest/custom-collections.html
[xarray]: http://xarray.pydata.org/

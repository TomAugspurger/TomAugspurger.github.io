---
title: "My Real-World Match / Case"
date: 2023-12-13T21:00:00-06:00
---

Ned Batchelder recently shared [Real-world match/case](https://nedbatchelder.com/blog/202312/realworld_matchcase.html), showing a real example of Python's [Structural Pattern Matching](https://peps.python.org/pep-0636/). These real-world examples are a great complement to the tutorial, so I'll share mine.

While working on some [STAC + Kerchunk stuff](../stac-updates), in [this pull request](https://github.com/stac-utils/xstac/pull/38) I used the match statement to parse some nested objects:

```python
for k, v in refs.items():
    match k.split("/"):
        case [".zgroup"]:
            # k = ".zgroup"
            item.properties["kerchunk:zgroup"] = json.loads(v)
        case [".zattrs"]:
            # k = ".zattrs"
            item.properties["kerchunk:zattrs"] = json.loads(v)
        case [variable, ".zarray"]:
            # k = "prcp/.zarray"
            if u := item.properties["cube:dimensions"].get(variable):
                u["kerchunk:zarray"] = json.loads(refs[k])
            elif u := item.properties["cube:variables"].get(variable):
                u["kerchunk:zarray"] = json.loads(refs[k])
        case [variable, ".zattrs"]:
            # k = "prcp/.zattrs"
            if u := item.properties["cube:dimensions"].get(variable):
                u["kerchunk:zattrs"] = json.loads(refs[k])
            elif u := item.properties["cube:variables"].get(variable):
                u["kerchunk:zattrs"] = json.loads(refs[k])
        case [variable, index]:
            # k = "prcp/0.0.0"
            if u := item.properties["cube:dimensions"].get(variable):
                u.setdefault("kerchunk:value", collections.defaultdict(dict))
                u["kerchunk:value"][index] = refs[k]
            elif u := item.properties["cube:variables"].get(variable):
                u.setdefault("kerchunk:value", collections.defaultdict(dict))
                u["kerchunk:value"][index] = refs[k]
```

The `for` loop is iterating over a set of [Kerchunk](https://fsspec.github.io/kerchunk) references, which are essentially the keys for a [Zarr](https://zarr.readthedocs.io/en/stable/spec/v2.html) group. The keys vary a bit. They could be:

1. Group metadata keys like `.zgroup` and `.zattrs`, which apply to the entire group.
2. Array metadata keys like `prcp/.zarray` or `prcp/.zattrs` (prcp is short for precipitation), which apply to an individual array in the group.
3. Chunk keys, like `prcp/0.0.0`, `prcp/0.0.1`, which indicate the chunk index in the n-dimensional array.

The whole point of this block of code is to update some other data (either the STAC `item` or the value referenced by the key). Between the different kinds of keys and the different actions we want to take for each kind of key, this seems like a pretty much ideal situation for structural pattern matching.

The subject of our match is `k.split("/")`:

```
match k.split("/")
```

Thanks to the Kerchunk specification, we know that any key should have exactly 0 or 1 `/`s in it, so we can define different cases to handle each.

Specific string literals have special meaning (like `".zgroup"` and `".zarray"`) and control the key we want to update, so we handle all those first.

And the final case handles everything else: any data `variable` and `index` will match the 

```python
case [variable, index]
```

The ability to bind the values like `variable = "prcp"` and `index = "0.0.0"` makes updating the target data structure seamless.

Combine that with the walrus operator (the `v:=`), `dict.setdefault`, and `collections.defaultdict`, we get some pretty terse, clever code. Looking back at it a couple months later it's probably bit too clever.
---
title: "Serializing Dataclasses"
date: 2024-08-31T12:00:00-05:00
---

This post is a bit of a tutorial on serializing and deserializing Python
[dataclasses].  I've been hacking on [zarr-python-v3] a bit, which uses some
dataclasses to represent some metadata objects. Those objects need to be
serialized to and deserialized from JSON.

This is a (surprisingly?) challenging area, and there are several excellent
libraries out there that you should probably use. My personal favorite is
[msgspec], but [cattrs], [pydantic], and [pyserde] are also options. But
hopefully this can be helpful for understanding how those libraries work at a
conceptual level (their exact implementations will look very different.) In
zarr-python's case, this didn't *quite* warrant needing to bring in a
dependency, so we rolled our own.

Like msgspec and cattrs, I like to have serialization logic separate from the
core metadata logic. Ideally, you don't need to pollute your object models with
serialization methods, and don't need to shoehorn your business logic to fit the
needs of serialization (too much). And ideally the actual validation is done at
the boundaries of your program, where you're actually converting from the
unstructured JSON to your structured models. Internal to your program, you have
static type checking to ensure you're passing around the appropriate types.

This is my first time diving into these topics, so if you spot anything that's
confusing or plain wrong, then [let me know](https://mastodon.social/@TomAugspurger).

## Overview

At a high level, we want a pair of methods that can serialize some dataclass
instance into a format like JSON and deserialize that output back into the
original dataclass.

The main challenge during serialization is encountering fields that Python's
[json] module doesn't natively support.  This might be "complex" objects like
Python datetimes or NumPy dtype objects. Or it could be instances of other
dataclasses if you have some nested data structure.

When deserializing, there are *lots* of pitfalls to avoid, but our main goal is
to support *typed deserialization*. Any time we converted a value (like a
datetime to a string, or a dataclass to a dict), we'll need to undo that
conversion into the proper type.

## Example

To help make things clearer, we'll work with this example:

```python
@dataclasses.dataclass
class ArrayMetadata:
    shape: tuple[int, ...]
    timestamp: datetime.datetime  # note 1


@dataclasses.dataclass
class EncoderA:
    value: int

@dataclasses.dataclass
class EncoderB:
    value: int


@dataclasses.dataclass
class Metadata:
    version: typing.Literal["3"]   # note 2
    array_metadata: ArrayMetadata  # note 2
    encoder: EncoderA | EncoderB   # note 4
    attributes: dict[str, typing.Any]
    name: str | None = None     # note 5
```

Successfully serializing an instance of `Metadata` requires working through a few things:

1. Python datetimes are not natively serializable by Python's JSON encoder.
2. `version` is a `Literal["3"]`, in other words `"3"` is only valid value there. We'd ideally
   validate that when deserializing `Metadata` (since we can't rely on a static linter like `mypy` to validate JSON data read from a file).
3. `Metadata.array_metadata` is a nested dataclass. We'll need to recursively apply any special serialization / deserialization logic to any dataclasses we encounter
4. `Metadata.encoder` is a union type, between `EncoderA` and `EncoderB`. We'll need to ensure that the serialized version has enough information to deserialize this into the correct variant of that Union
5. `name` is an `Optional[str]`. This is similar to a Union between two concrete types, where one of the types happens to be None.

## Serialization

Serialization is *relatively* easy compared to deserialization. Given an
instance of `Metadata`, we'll use `dataclasses.asdict` to convert the dataclass
to a dictionary of strings to values. The main challenge is telling the JSON
encoder how to serialize each of those values, which might have be "complex"
types (whether they be dataclasses or some builtin type like
`datetime.datetime`).  There are a few ways to do this, but the simplest way to
do it is probably to use the `default` keyword of `json.dumps`.

```python
def encode_value(x):
    if dataclasses.is_dataclass(x):
        return dataclasses.asdict(x)
    elif isinstance(x, datetime.datetime):
        return x.isoformat()
    # other special cases... 

    return x
```

If Python encounters a value it doesn't know how to serialize, it will use your function.

```python
>>> json.dumps({"a": datetime.datetime(2000, 1, 1)}, default=serialize)
'{"a": "2000-01-01T00:00:00"}'
```

For aesthetic reasons, we'll use `functools.singledispatch` to write that:

```python
import dataclasses, datetime, typing, json, functools


@functools.singledispatch
def encode_value(x: typing.Any) -> typing.Any:
    if dataclasses.is_dataclass(x):
        return dataclasses.asdict(x)

    return x

@encode_value.register(datetime.datetime)
@encode_value.register(datetime.date)
def _(x: datetime.date | datetime.datetime) -> str:
    return x.isoformat()


@encode_value.register(complex)
def _(x: complex) -> list[float, float]:
    return [x.real, x.imag]

# more implementations for additional type...
```

You'll build up a list of [supported types](https://jcristharif.com/msgspec/supported-types.html)
that your system can serialize.

And define your serializer like so:

```python
def serialize(x):
    return json.dumps(x, default=encode_value)
```

and use it like:

```python
>>> metadata = Metadata(
...     version="3",
...     array_metadata=ArrayMetadata(shape=(2, 2),
...     timestamp=datetime.datetime(2000, 1, 1)),
...     encoder=EncoderA(value=1),
...     attributes={"foo": "bar"}
... )
>>> serialized = serialize(metadata)
>>> serialized
'{"version": "3", "array_metadata": {"shape": [2, 2], "timestamp": "2000-01-01T00:00:00"}, "encoder": {"value": 1}, "attributes": {"foo": "bar"}, "name": null}'
```

## Deserialization

We've done serialization, so we should be about halfway done, right? Ha! Because we've signed up for *typed* deserialization, which will let us faithfully round-trip some objects, we have more work to do.

A plain "roundtrip" like `json.loads` only gets us part of the way there:

```python
>>> json.loads(serialized)
{'version': '3',
 'array_metadata': {'shape': [2, 2], 'timestamp': '2000-01-01T00:00:00'},
 'encoder': {'value': 1},
 'attributes': {'foo': 'bar'},
 'name': None}
```

We have plain dictionaries instead of instances of our dataclasses and the
timestamp is still a string.  In short, we need to decode all the values we
encoded earlier. To do that, we need the user to give us a *bit* more
information: We need to know the desired dataclass to deserialize into.

```python
def deserialize(into: type[T], data: bytes) -> T:
    ...
```

Given some type `T` (which we'll assume is a dataclass; we could do some things
with type annotations to actually check that) like `Metadata`, we'll build
an instance using the deserialized data (with the properly decoded types!)

Users will call that like

```python
>>> deserialize(into=Metadata, data=deserialized)
Metadata(...)
```

For a dataclass type like `Metadata`, we can get the types of all of its
fields at runtime with [`typing.get_type_hints`]:

```python
>>> typing.get_type_hints(Metadata)
{'version': typing.Literal['3'],
 'array_metadata': __main__.ArrayMetadata,
 'encoder': __main__.EncoderA | __main__.EncoderB,
 'attributes': dict[str, typing.Any],
 'name': str | None}
```

So we "just" need to write a `decode_value` function that mirrors our
`encode_value` function from earlier.


```python
def decode_value(into: type[T], value: Any) -> T:
    # the default implementation just calls the constructor, like int(x)
    # In practice, you have to deal with a lot more details like
    # Any, Literal, etc.
    return into(value)


@decode_value.register(datetime.datetime)
@decode_value.register(datetime.date)
def _(into, value):
    return into.fromisoformat(value)


@decode_value.register(complex)
def _(into, value):
    return into(*value)

# ... additional implementations
```

Unfortunately, "just" writing that decoder proved to be challenging (have I
mentioned that you should be using msgspec for this yet?). Probably the biggest challenge was
dealing with Union types. The msgspec docs cover this really well in its [Tagged Unions](https://jcristharif.com/msgspec/structs.html#tagged-unions) section, but I'll give a brief overview.

Let's take a look at the declaration of `encoder` again:

```python
@dataclasses.dataclass
class EncoderA:
    value: int

@dataclasses.dataclass
class EncoderB:
    key: str
    value: int


class Metadata:
    ...
    encoder: EncoderA | EncoderB
```

Right now, we serialize that as something like this:

```JSON
{
    "encoder": {
        "value": 1
    }
}
```

With that, it's impossible to choose between `EncoderA` and `EncoderB` without
some heuristic like "pick the first one", or "pick the first one that succeeds".
There's just not enough information available to the decoder. The idea of a
"tagged union" is to embed a bit more information in the serialized
representation that lets the decoder know which to pick.

```JSON
{
    "encoder": {
        "value": 1,
        "type": "EncoderA",
    }
}
```

Now when the decoder looks at the type hints it'll see `EncoderA | EncoderB` as
the options, and can pick `EncoderA` based on the `type` field in the serialized
object.  We have introduced a new complication, though: how do we get `type` in
there in the first place?

There's probably multiple ways, but I went with [`typing.Annotated`].  It's not
the most user-friendly, but it lets you put additional metadata on the type
hints, which can be used for whatever you want. We'd require the user to specify
the variants of the union types as something like

```python
class Tag:
    ...

class EncoderA:
    value: int
    type: typing.Annotated[typing.Literal["a"], Tag] = "a"

class EncoderB:
    value: int
    key: str
    type: typing.Annotated[typing.Literal["b"], Tag] = "b"
```

(Other libraries might use something like the classes name as the value (by
default) rather than requiring a single-valued Literal there.)

Now we have a `type` key that'll show up in the serialized form.
When our decoder encounters a union of types to deserialize into,
it can inspect their types hints with `include_extras`:

```python
>>> typing.get_type_hints(EncoderA, include_extras=True)
{'value': int,
 'type': typing.Annotated[typing.Literal['a'], <class '__main__.Tag'>]}
```

By walking each of those pairs, the decoder can figure out which
value in `type` maps to which dataclass type:

```python
>>> tags_to_types
{
    "a": EncoderA,
    "b": EncoderB,
}
```

Finally, given the object `{"type": "a", "value": 1}` it can pick the correct
dataclass type to use. Then *that* can be fed through `decode_value(EncoderA,
value)` to recursively decode all of its types properly.

## Conclusion

There's much more to doing this *well* that I've skipped over in the name of
simplicity (validation, nested types like `list[Metadata]` or tuples, good error
messages, performance, extensibility, ...).  Once again, you should probably be
using [msgspec] for this. But at least now you might have a bit of an idea how
these libraries work and how type annotations can be used at runtime in Python.

[dataclasses]: https://docs.python.org/3/library/dataclasses.html
[msgspec]: https://jcristharif.com/msgspec/
[cattrs]: https://catt.rs/en/stable/
[pydantic]: https://docs.pydantic.dev/latest/
[zarr-python-v3]: https://github.com/zarr-developers/zarr-python/
[`json.JSONEncoder]: https://docs.python.org/3/library/json.html#json.JSONEncoder
[`typing.Annotated`]: https://docs.python.org/3/library/typing.html#typing.Annotated
[json]: https://docs.python.org/3/library/json.html
[`typing.get_type_hints`]: https://docs.python.org/3/library/typing.html#typing.get_type_hints
[pyserde]: https://yukinarit.github.io/pyserde/guide/en/
---
title: "stac-geoparquet"
date: 2024-08-15T20:28:37-05:00
draft: true
---

This post introduces stac-geoparquet, which is both a specification and library for storing and serving [STAC] metadata as [geoparquet].

## STAC Background

[STAC] makes geospatial data queryable, especially "semi-structured" geospatial data like a collection of COGs from a satellite. I can't imagine trying to work with this type of data without a STAC API.

Concretely, STAC metadata consists of JSON documents describing the actual assets (COG files, for examples). STAC metadata can typically be accessed in two ways:

1. Through a static STAC catalog, which is just a JSON document linking to other JSON documents (STAC Collections and / or STAC Items, which include the links to the assets)
2. Through a [STAC API](https://github.com/radiantearth/stac-api-spec), which also enables things like search.

In practice, I haven't encountered much data distributed as static STAC catalogs. It's perhaps useful in some cases, but for large datasets or datasets that are constantly growing, a pile of JSON files becomes slow and impractical to serve or use. You almost need a STAC API.

That said, *running* a STAC API is a hassle (speaking from experience here). You need some kind of [database](https://github.com/stac-utils/pgstac) and [web servers](https://github.com/stac-utils/stac-fastapi). That database and those web servers need to be deployed, monitored, and maintained.

Finally, with either a static STAC catalog or an API, for large collections of STAC items you're moving around *a lot* of JSON. That's slow for the web servers to serialize, slow to send over the network, and slow to deserialize on your end.

## Enter STAC-geoparquet

STAC-geoparquet offers a nice format for easily and efficiently transferring (or querying!) large amounts of *homogenous* STAC items.
The basic idea is to represent a STAC collection as a geoparquet dataset.

The [specification](https://stac-utils.github.io/stac-geoparquet/latest/spec/stac-geoparquet-spec/) describes how to convert between a set of STAC items and GeoParquet and provides some guidance to Collection maintainers on how to encode certain fields.

One neat feature is the ability to embed the Collection metadata in the parquet file's metadata. This gives you a great single-file format for moving around small to medium sized collections (large collections may need to be partitioned into multiple files).

stac-geoparquet optimizes for certain use cases by leveraging the strengths of the parquet file format at the cost of some generality.
Parquet is a columnar file format, so all the records in a stac-geoparquet dataset need to have the same schema. The more homogenous the items, the more efficiently you'll be able to store them. In practice, this means that all the items in a collection should have the same properties available. This is considered a best practice in STAC anyway, but there may be some STAC collections that can't be (efficiently) stored in stac-geoparquet.

stac-geoparquet (and parquet more generally) is optimized for bulk and analytic use cases. You likely wouldn't want to do "point" reads, where you look up an individual item by ID. Databases like Postgres are much better suited for that type of workload.

## Example

As a simple example, we'll look at what it takes to access one month's worth of sentinel-2-l2a items from the Planetary Computer's [sentinel-2-l2a collection](https://planetarycomputer.microsoft.com/dataset/sentinel-2-l2a). January, 2020 had about 267,880 items.

With some clever code to parallelize requests to the STAC API, we can fetch those items in about 160 seconds.

```python
>>> t0 = time.time()
>>> futures = [search(client, period) for period in periods]
>>> features_nested = await asyncio.gather(*futures)
>>> t1 = time.time()
>>> print(f"{t1 - t0:0.2f}")
162.16
```

The `search` method is a couple dozen lines of Python. I serialized that to disk as (uncompressed) ndjson, and it took up about 4.5 GB of space.

With the `stac-geoparquet` Python library, we can convert to geoparquet:

```python
>>> import stac_geoparquet
>>> rbr = stac_geoparquet.arrow.parse_stac_items_to_arrow(features)
>>> stac_geoparquet.arrow.to_parquet(rbr, "sentinel-2-l2a.parquet")
```

That takes only 260 MB on disk. It can be read with a simple:

```python
>>> table = pyarrow.parquet.read_table("sentinel-2-l2a.parquet")
```

which finishes in just under 5 seconds. That's not entirely a fair comparison to the 160 seconds from the API, since I'm loading that from disk rather than the network, but there's ample room to spare.

The stac-geoparquet Python library can also write to the Delta Table format, which pulls some additional tricks to bring the loading time down to 2.5 seconds.

## Summary

So, in all stac-geoparquet offers a very convenient and high-performance way to distribute large STAC collections, provided the items in that collection are pretty homogenous (which they probably should be, for your users' sake). It by no means replaces the need for a STAC API in all use cases. Databases like Postgres are *really good* at certain workloads. And 

[STAC]: https://stacspec.org
[geoparquet]: https://geoparquet.org
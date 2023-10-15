---
title: "STAC Updates I'm Excited About"
date: 2023-10-15T12:00:00-05:00
---

I wanted to share an update on a couple of developments in the [STAC] ecosystem
that I'm excited about. It's a great sign that even after 2 years after its
initial release, the STAC ecosystem is still growing and improving how we can
catalog, serve, and access geospatial data.

## STAC and Geoparquet

A STAC API is a great way to query for data. But, like any API serving JSON, its
throughput is limited. So in May 2022, the Planetary Computer team decided to
export snapshots of our STAC database as [geoparquet]. Each STAC collection is
exported as a Parquet dataset, where each record in the dataset is a STAC item.
We pitched this as a way to do [bulk queries][bulk] over the data, where
returning many and many pages of JSON would be slow (and expensive for our
servers and database).

Looking at the [commit history][history], the initial prototype was done over a
couple of days. I wish I had my notes from our discussions, but this feels like
the kind of thing that came out of an informal discussion like "This access
pattern kind of sucks", followed by "What if we .... ?", and then "Let's
try it![^1]". And so we tried it, and it's been great!

I think STAC as geoparquet can become a standard way to transfer STAC data in
bulk. Chris Holmes has an [open PR][discussion] defining a specification for
what the columns and types should be, which will help more tools than just that
`stac-geoparquet` library interpret the data.

And Kyle Barron has an [open PR][stac-arrow] making the `stac-geoparquet`
library "arrow-native" by using [Apache Arrow][arrow] arrays and tables directly
(via pyarrow), rather than pandas / geopandas. When I initially sketched out
`stac-geoparquet`, it might have been just a bit early to do that. But given
that we're dealing with complicated, nested types (which isn't NumPy's strong
suite) and we aren't doing any analysis (which *is* pandas / NumPy's strong
suite), this will be a great way to move the data around.

Now I'm just hoping for a PostgreSQL [ADBC][adbc] adapter so that our PostGIS
database can output the STAC items as Arrow memory. Then we can be all Arrow
from the time the data leaves the database to the time we're writing the parquet
files.

## STAC and Kerchunk

[Kerchunk] is, I think, going to see some widespread adoption over the next year
or two. It's a project (both a Python library and a specification) for putting a
cloud-optimized veneer on top of non-cloud optimized data formats (like NetCDF /
[HDF5] and GRIB2).

Briefly, those file formats tend not to work great in the cloud because

1. In the cloud, we want to read files over the network (data are stored in Blob
   Storage, which is on a different machine than your compute). These file
   formats are pretty complicated, and can typically only be read by one library
   implemented in C / C++, which isn't always able to read data over the
   network.
2. Reading the *metadata* (to build a structure like an xarray Dataset) tends to
   require reading many small pieces of data from many parts of the file. This
   is slow over the network, where each small read could translate to an HTTP
   request. On an SSD, seeking around the file to gather metadata is fine. Over
   the network, it's slow.

Together, those mean that you aren't able to easily load subsets of the data
(even if the data are internally chunked!). You can't load the metadata to do
your filtering operations, and even if you could you might need to download the
whole file just to throw away a bunch of data.

That's where Kerchunk comes in. The idea is that the data provider can scan the
files once ahead of time, extracting the *Kerchunk indices*, which include

1. The metadata (dimension names, coordinate values, attributes, etc.), letting
   you build a high-level object like an `xarray.Dataset` without needing any
   (additional) HTTP requests.
2. The byte offsets for each chunk of each data variable, letting you access
   arbitrary subsets of the data without needing to download and discard
   unnecessary data.

You store that metadata somewhere (in a JSON file, say) and users access the
original NetCDF / GRIB2 data via that Kerchunk index file. You can even do
metadata-only operations, like combining data variables from many files, or
concatenating along a dimension to make a time series, without ever downloading
the data.

We've had some [experimental support][experiment] for accessing a couple
datasets hosted on the Planetary Computer via Kerchunk indices for a while now.
We generated some indices and through them up in Blob Storage, including them as
an asset in the STAC item. I've never really been happy with how how that works
in practice, because of the extra hop from STAC to Kerchunk to the actual data.

I think that Kerchunk is just weird enough and hard enough to use that it can
take time for users to feel comfortable with it. It's hard to explain that if
you want the data from *this* NetCDF file, you need to download this *other*
JSON file, and then open that up with this other fsspec filesystem (no, not the
Azure Blob Storage filesystem where the NetCDF and JSON files are, that'll come
later), and pass that result to the Zarr reader in xarray (no, the data isn't
stored in Zarr, we're just using the Zarr API to access the data via the
references...).

Those two additional levels of indirection (through a sidecar JSON file and then
the Zarr reader via fsspec's reference file system) are a real hurdle. So some
of my teammate's are working on storing the Kerchunk indices in the STAC
items.

My goal is to enable an access pattern like this:

```python
>>> import xarray as xr
>>> import pystac_client
>>> catalog = pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")

>>> items = catalog.search(collections=["noaa-nwm"], datetime="2023-10-15", query=...)
>>> ds = xr.open_dataset(items, engine="stac")
```

Where the step from STAC to xarray / pandas / whatever is as easy with NetCDF or
GRIB2 data as it is with COGs are Zarr data (thanks to projects like [stackstac]
and [odc-stac].) This is using ideas from Julia Signell's [xpystac] library for
that final layer, which would know how to translate the STAC items (with
embedded Kerchunk references) into an xarray Dataset.

I just made an [update](https://github.com/stac-utils/xstac/pull/38) to [xstac],
a library for creating STAC items for data that can be reresented as an xarray
Datasets, to add support for embedding Kerchunk indices in a STAC item
representing a dataset. The goal is to be "STAC-native" (by using things like
the datacube extension), while still providing enough information for Kerchunk
to do its thing. I'll do a proper STAC extension later, but I want to get some
real-world usage of it first.

I think this is similar in spirit to how
[Arraylake](https://docs.earthmover.io/) can store Kerchunk indices in their
database, which hooks into their Zarr-compatible API.

The main concern here is that we'd blow up the size of the STAC items. That
would bloat our database, slow down STAC queries and responses. But overall, I
think it's worth it for the ergonomics when it comes to loading the data. We'll
see.

## Getting Involved

Reach out, either on GitHub or by email, if you're interested in getting
involved in any of these projects.

[STAC]: https://stacspec.org/
[history]: https://github.com/stac-utils/stac-geoparquet/commits/main?after=a5a5bf2d958672c36f0c4c4cc827970833c18380+69&branch=main&qualified_name=refs%2Fheads%2Fmain
[geoparquet]: https://geoparquet.org/
[bulk]: https://planetarycomputer.microsoft.com/docs/quickstarts/stac-geoparquet/
[discussion]: https://github.com/stac-utils/stac-geoparquet/pull/28
[stac-arrow]: https://github.com/stac-utils/stac-geoparquet/pull/27
[arrow]: https://arrow.apache.org/
[adbc]: https://arrow.apache.org/docs/format/ADBC.html
[Kerchunk]: https://fsspec.github.io/kerchunk/
[HDF5]: https://www.hdfgroup.org/
[stackstac]: https://stackstac.readthedocs.io/en/latest/
[odc-stac]: https://odc-stac.readthedocs.io/
[xpystac]: https://github.com/stac-utils/xpystac
[xstac]: https://github.com/stac-utils/xstac
[experiment]: https://planetarycomputer.microsoft.com/dataset/nasa-nex-gddp-cmip6#Example-Notebook

[^1]: I do distinctly remember that our ["hosted
    QGIS"](https://planetarycomputer.microsoft.com/docs/overview/qgis-plugin/)
    was exactly that. [Yuvi](https://github.com/yuvipanda) had made a
    [post](https://discourse.pangeo.io/t/run-linux-desktop-apps-in-mybinder-org-your-jupyterhub/1978)
    on the Pangeo Discourse and
    [Dan](http://awesomesongbook.com/00s_songs/00s_songs.html) had asked about
    how Desktop GIS users could use Planetary Computer data (we had just helped
    fund the STAC plugin for QGIS). I added that JupyterHub profile based on
    Yuvi and Scott Hendersen's work and haven't touched it since.

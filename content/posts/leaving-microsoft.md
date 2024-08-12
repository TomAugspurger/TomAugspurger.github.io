---
title: "What's Next? (2024 edition)"
date: 2024-08-12T07:00:00-05:00
---

I have, as they say, some personal news to share. On Monday I (along with some *very* talented teammates, see [below](#whats-next) if you're hiring) was laid off from Microsoft as part of a reorganization. Like my [Moving to Microsoft](/posts/whats-next) post, I wanted to jot down some of the things I got to work on.

## Reflections

It should go without saying that *all* of this was a team effort. I've been incredibly fortunate to have great teammates over the years, but the team building out the [Planetary Computer](http://planetarycomputer.microsoft.com/) was especially fantastic.
Just like before, this will be very self-centered and project-focused, overlooking all the other people and work that went into this.

I'm a *bit* uncomfortable with all the navel gazing, but I am glad I did the last one so here goes.

### The Hub

Our initial vision for the Planetary Computer had four main components:

1. Data (the actual files in Blob Storage, ideally in cloud-optimized formats)
2. APIs (like the STAC API which make the data usable; using raster geospatial data *without* a STAC API feels barbaric now)
3. Compute
4. Applications (which package all the low level details into reports or tools that are useful to decision makers)

Initially, my primary responsibility on the team was to figure out "Compute". [Dan Morris](http://dmorris.net) had a nice line around "it shouldn't require a PhD in remote sensing *and* a PhD in distributed computing to use this data."

After fighting with Azure AD and RBAC roles for a few weeks, I had the initial version of the [PC Hub](https://github.com/Microsoft/planetary-computer-hub) up and running. This was a more-or-less stock version of the [daskhub](https://github.com/dask/helm-chart/blob/main/daskhub/README.md) helm deployment with a few customizations.

Aside from occasionally updating the container images and banning crypto miners (stealing free compute to burn CPU cycles on a platform built for sustainability takes some hutzpah), that was mostly that. While the JupyterHub + Dask on Kubernetes model isn't perfect for every use case, it solves a lot of problems. You might still have to know a *bit* about distributed computing in order to run a large computation, but at least our users didn't have to fight with Kubernetes (just the Hub admin, me in this case).

Probably the most valuable aspect of the Hub was having a shared environment where anyone could easily run our [Example Notebooks](https://github.com/microsoft/PlanetaryComptuerExamples). We also ran several "cloud native geospatial" tutorials on one-off Hubs deployed for a conference.

This also gave the opportunity to sketch out [an implementation](https://github.com/kbatch-dev/kbatch) of Yuvi's [kbatch](https://words.yuvi.in/post/kbatch/) proposal. I didn't end up having time to follow up on the initial implementation, but I still think there's room for a *very simple* way to submit batch Jobs to the same compute powering your interactive JupyterHub sessions.

### stac-vrt

*Very* early on in project[^1], we had an opportunity to present on the Planetary Computer to [Kevin Scott](https://news.microsoft.com/exec/kevin-scott/) and his team. Our presentation included a short demo applying a Land Use / Land Cover model to some [NAIP data](https://planetarycomputer.microsoft.com/dataset/naip). While preparing that, I noticed that doing `rioxarray.open_rasterio` on a bunch of NAIP COGs was slow. Basically, GDAL had to make an HTTP request to read the COG metadata of each file.

After reading some GitHub issues and Pangeo discussions, I learned about using [GDAL VRTs](https://gdal.org/drivers/raster/vrt.html) as a potential solution to the problem. Fortunately, our STAC items had all the information needed to build a VRT, and rioxarray already knew how to open VRTs. We just needed a tool to build that VRT. That was [stac-vrt](https://github.com/stac-utils/stac-vrt/).

I say "was" because similar functionality is now (better) implemented in [GDAL itself](https://gdal.org/drivers/raster/stacit.html), [stackstac](https://stackstac.readthedocs.io/en/latest/), and [odc-stac](https://odc-stac.readthedocs.io/en/latest/).

This taught me that STAC can be valuable beyond just searching for data. The metadata in the STAC items can be useful during analysis too. Also, as someone who grew up in the open-source Scientific Python Ecosystem, it felt neat to get tools like xarray and Dask in front of the CTO of Microsoft.

### geoparquet

I had a very small hand in getting [geoparquet](https://geoparquet.org) started, connecting [Chris Holmes](https://www.linkedin.com/in/opencholmes/) with [Joris van den Bossche](https://github.com/jorisvandenbossche) and the geopandas / geoarrow group. Since then my contributions have been relatively minor, but at least for a while the Planetary Computer could claim to host the most geoparquet data (by count of datasets and volume) than anyone else. [Overture Maps](https://overturemaps.org) probably claims that title now, which is fantastic.

### stac-geoparquet

Pretty early on, we had some users with demanding use-cases where the STAC API itself was becoming a bottleneck. We pulled some tricks to speed up their queries, but this showed us there was a need to provide bulk access to the STAC metadata, where the number of items in the result is very large.

With a quick afternoon hack, I got a prototype running that converted our STAC items (which live in a Postgres database) to geoparquet (technically, this predated geoparquet!). The generic pieces of that tooling are at https://github.com/stac-utils/stac-geoparquet/ now. Kyle Barron recently made some really nice improvements to the library (moving much of the actually processing down into Apache Arrow), and Pete Gadomski is working on a [Rust implementation](https://github.com/stac-utils/stac-rs/pull/256).

For the right workloads, serving large collections of STAC metadata through Parquet (or even better, Delta or Iceberg or some other table format) is indispensable.

### Data Pipelines

These are less visible externally (except when they break), but a couple years ago I took on more responsibility for the data pipelines that keep data flowing into the Planetary Computer. Broadly speaking, this included

1. Getting data from upstream sources to Azure Blob Storage
2. Creating STAC Items for new data and ingesting them into the Postgres database

Building and maintaining these pipelines was... challenging. Our APIs or database would occasionally give us issues (especially under load). But the onboarding pipelines required a steady stream of attention, and would also blow up occasionally when the upstream data providers changed something. https://sre.google/sre-book/monitoring-distributed-systems/ is a really handy resource for thinking about how to monitor this type of system. This was a great chance to learn.

### pc-id

Before we publicly launched the Planetary Computer, we didn't have a good idea of how we would manage users. We knew that we wanted to role things out somewhat slowly (at least access to the Hub; the data and APIs might have always been anonymously available?). So we knew we needed some kind of sign-up systems, and some sort of identity system that could be used by both our API layer (built on Azure's API Management service) and our Hub.

After throwing around some ideas (Azure AD B2C? Inviting beta users as Guests in the Microsoft Corp tenant?), I put together the sketch of a Django application that could be the Identity backend for both API Management and the Hub. Users would sign in with their Work or Personal Microsoft Accounts (in the Hub or API Management Dev Portal) and our ID application would check that the user was registered and approved.

We added a few bells and whistles to the Admin interface to speed up the approval process, and then more or less didn't touch it aside from basic maintenance. Django is *great*. I am by no means a web developer, but it let us get started quickly on a solid foundation.

### Other Highlights

- [xstac](https://github.com/stac-utils/xstac): A library for creating STAC metadata for xarray datasets
- [stac-table](https://github.com/stac-utils/stac-table): A library for creating STAC metadata for geopandas GeoDataFrames
- Several [stactools-packages](https://github.com/stactools-packages/), to create STAC metadata for specific datasets
- Many presentations on Cloud Native Geospatial, including at [AMS](https://github.com/TomAugspurger/pc-ams) and [Cloud Native Geospatial Day](https://github.com/TomAugspurger/pc-cng-outreach-2022)

There's lots of STAC here. I'd like to think that we had a hand in shaping how the STAC ecosystem works, especially for more "exotic" datasets like tables and data cubes in NetCDF or Zarr format.

### What's Next?

Last time around, I ended things with the exciting announcement that I was moving to Microsoft. This time... I don't know! This is my first time not having a job lined up, so I'll hope to spend some time finding the right thing to work on.

One thing I'm trying to figure out is how much to stock to place in the geospatial knowledge I've picked up over the last four years. I've spent a lot of time learning and thinking about geospatial things (though I still cant't explain the difference between a CRS and Datum). There's a lot of domain-specific knowledge needed to use these geospatial datasets (too much domain-specificity, in my opinion). We'll see if that's useful.

Like I mentioned above, I wasn't the only one who was laid off. There are some really talented people on the job market, both more junior and more senior. If you're looking for someone you can reach me at <a href="mailto:tom.w.augspurger@gmail.com">tom.w.augspurger@gmail.com</a>.

Thanks for reading!

[^1]: Matt was the last of the original crew to join. On his first day, we had to break the news that he was presenting to the CTO in a week.
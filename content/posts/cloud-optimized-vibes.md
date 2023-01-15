---
title: "Cloud optimized vibes"
date: 2023-01-14T16:16:11-06:00
draft: true
---

Over on the [Planetary Computer](http://planetarycomputer.microsoft.com/) team, we get to have a lot of fun discussions about doing geospatial data analysis on the cloud. This post summarizes some work we did, and the (I think) interesting conversations that came out of it.

## Background: GOES-GLM

The instigator in this case was onboarding a new dataset to the Planetary Computer, [GOES-GLM](https://planetarycomputer.microsoft.com/dataset/goes-glm). GOES is a set of geostationary weather satellites operated by NOAA, and GLM is the Geostationary Lightning Mapper, an instrument on the satellites that's used to monitor lightning. It produces some really neat (and valuable) data.

The data makes its way to Azure via the [NOAA Open Data Dissemination program](https://www.noaa.gov/information-technology/open-data-dissemination) (NODD) as a bunch of NetCDF files. Lightning is fast `[citation needed]`, so the GOES-GLM team does some clever things to build up a hierarchy of "events", "groups", and "flashes" that can all be grouped in a file. This happens very quickly after the data is captured, and it's delivered to Azure soon after that. All the details are at https://www.star.nesdis.noaa.gov/goesr/documents/ATBDs/Baseline/ATBD_GOES-R_GLM_v3.0_Jul2012.pdf for the curious.

## Cloud-native NetCDF?

The raw data are delivered as a bunch of NetCDF4 files, which [famously isn't cloud-native](https://matthewrocklin.com/blog/work/2018/02/06/hdf-in-the-cloud). The metadata tends to be spread out across the file, requiring many (small) reads to load the metadata. If you only care about a small subset of the data, those metadata reads can dominate your processing time. Remember: reading a new chunk of metadata typically requires another HTTP call. Even when your compute is in the same region as the data, an HTTP call is much slower than seeking to a new spot in an open file on disk.

But what if I told you that you could read *all* the metadata in a single HTTP request? Well, that's possible with these NetCDF files. Not because of anything special about how the metadata is written, just that these files are relatively small. They're only about 100-300 KB in total. So we can read all the metadata (and data) in a single HTTP call.

That gets to a point made by Paul Ramsey in his [Cloud Optimized Shape File](http://blog.cleverelephant.ca/2022/04/coshp.html) article:

> One of the quiet secrets of the “cloud optimized” geospatial world is that, while all the attention is placed on the formats, the actual really really hard part is writing the clients that can efficiently make use of the carefully organized bytes.

So yes, the file formats do (often) matter. And yes, we need clients that can make efficient use of those carefully organized bytes. *But* when the files are this small, it doesn't really matter how the bytes or organized. You're still making a single HTTP call, whether you want all the data or just some of it.

This was a fun conversation amongst the team. We like to say we host "cloud-optimized data" on the Planetary Computer, and we do. But what really matters is the user experience. It's all about the cloud-optimized *vibes*.

## Build with users, not just with users in mind

A last, small point is the importance of getting user feedback *before* you go off doing something. We looked at the data and noticed the *obviously* tabular nature of the data and decided to split these single NetCDF file into three geoparquet files. In the abstract this make sense: these are naturally tabular, and parquet is the natural file format for them. We figured our users would appreciate the conversion. *However* we suddenly tripled the number of objects in Blob Storage. With this many objects and with new objects arriving so frequently, the sheer number of small files became a challenge to work with. This is, I think, still the right format for the data. But we'll need to do more with our users to confirm that that's the case before committing to maintain this challenging data pipeline to do the conversion at scale.
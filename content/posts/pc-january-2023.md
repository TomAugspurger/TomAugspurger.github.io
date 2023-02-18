---
title: "Planetary Computer Release: January 2023"
date: 2023-02-09
---

The Planetary Computer made its [January 2023 release](https://planetarycomputer.microsoft.com/docs/overview/changelog/) a couple weeks back.

The flagship new feature is a *really* cool new ability to visualize the [Microsoft AI-detected Buildings Footprints](https://planetarycomputer.microsoft.com/dataset/ms-buildings) dataset. Here's a little demo made by my teammate, Rob:


<video controls style="height: 400px;">
  <source src="https://ai4edatasetspublicassets.azureedge.net/assets/pc_video/vector-tile-ms-buildings-feature.mp4" type="video/mp4" />
  <p>
    Your browser doesn't support HTML video. Here is a
    <a href="https://ai4edatasetspublicassets.azureedge.net/assets/pc_video/vector-tile-ms-buildings-feature.mp4">link to the video</a> instead.
  </p>
</video>

Currently, enabling this feature required converting the data from its native [geoparquet](http://github.com/opengeospatial/geoparquet) to a *lot* of protobuf files with [Tippecanoe](https://github.com/felt/tippecanoe). I'm very excited about projects to visualize the geoparquet data directly (see [Kyle Barron's demo](https://kylebarron.dev/blog/geoarrow-and-geoparquet-in-deck-gl)) but for now we needed to do the conversion.

Hats off to Matt McFarland, who did the work on the data conversion and the frontend to support the rendering.

## New Datasets

As usual, we have a handful of new datasets hosted on the Planetary Computer. Follow the link on each of these to find out more.

[**Climate Change Initiative Land Cover**](https://planetarycomputer.microsoft.com/dataset/group/esa-cci-lc)

<img src="https://ai4edatasetspublicassets.azureedge.net/assets/pc_video/docs-esa-cci-lc-1992-2020-brazil.gif" width="500px"/>

[**NOAA Climate Normals**](https://planetarycomputer.microsoft.com/dataset/group/noaa-climate-normals)[^1]

<img src="https://ai4edatasetspublicassets.azureedge.net/assets/pc_thumbnails/noaa-climate-normals-gridded-thumb.png" width="500px">

[**USDA Cropland Data Layer**](https://planetarycomputer.microsoft.com/dataset/usda-cdl)

<img src="https://planetarycomputer.microsoft.com/_images/changelog-usda-cdl.png" width="500px">

[**USGS Land Change Monitoring, Assessment, and Projection**](https://planetarycomputer.microsoft.com/dataset/group/usgs-lcmap)

<img src="https://ai4edatasetspublicassets.blob.core.windows.net/assets/pc_video/docs-usgs-lcmap-cali-1985-2021.gif" width="500px">

[**National Wetlands Inventory**](https://planetarycomputer.microsoft.com/dataset/fws-nwi)

<img src="https://planetarycomputer.microsoft.com/_images/changelog-fws-nwi.png" width="500px">

## Other stuff

We've also been doing a lot of work around the edges that doesn't show up in visual things like new features or datasets. That work should show up
in the next release and I'll be blogging more about it then.

[^1]: NOAA Climate Normals is our first cataloged dataset that lives in a different Azure region. It's in East US while all our other datasets are in West Europe. I'm hopefully this will rekindle interest in some multi-cloud (or at least multi-region) stuff we explored in [pangeo-multicloud-demo](https://github.com/pangeo-data/multicloud-demo). See https://discourse.pangeo.io/t/go-multi-regional-with-dask-aws/3037 for a more recent example. Azure actually has a whole [Azure Arc](https://azure.microsoft.com/en-us/products/azure-arc/#overview) product that helps with multi-cloud stuff.

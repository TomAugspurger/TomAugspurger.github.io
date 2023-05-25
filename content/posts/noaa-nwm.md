---
title: "National Water Model on Azure"
date: 2023-05-25T12:04:06-05:00
---

A few colleagues and I recently presented at the [CIROH Training and Developers Conference][ciroh].
In preparation for that I created a [Jupyter Book](https://jupyterbook.org/en/stable/intro.html). You can view it at https://tomaugspurger.github.io/noaa-nwm/intro.html
I created a few cloud-optimized versions for subsets of the data, but those will be going away since we don't have operational pipelines to keep them up to date. But hopefully the static notebooks are still helpful.

## Lessons learned

Aside from running out of time (I always prepare too much material for the amount of time), I think things went well. JupyterHub (perhaps + Dask) and Kubernetes continues to be a great way to run a workshop.

The code for processing the data into cloud-optimized formats (either Kerchunk indexes, Zarr, or (geo)parquet) is at https://github.com/TomAugspurger/noaa-nwm/tree/main/processing

To process the data I needed to create some Dask clusters. I had the opportunity to use [dask-kubernetes'](https://kubernetes.dask.org/) new [Dask Operator](https://kubernetes.dask.org/en/latest/operator.html). It was great!

The actual pipelines for processing the raw files into cloud-optimized formats (or Kerchunk indexes) continues to be a challenge.
A large chunk of that complexity does come from the data itself, and I gather that the National Water Model is pretty complex, at a fundamental level. I ran into issues with corrupt files (which have since been fixed). An update to the National Water Model changed its internal chunking structure, which is incompatible with Kerchunk's current implementation. These were pretty difficult to debug.

I think the main takeway from the conference was that we (either the users of this data, the Planetary Computer, NODD, or the Office of Water Prediction) needs to do *something* to make this data more usable on the cloud. Most likely some sort of Kerchunk index is the first stop, but this won't handle every use case (see the [timeseries](https://tomaugspurger.github.io/noaa-nwm/04-timeseries.html) notebook for an example). Maintaining operational pipelines is a challenge, but
hoepfully we can take it on some day.

[ciroh]: https://ciroh.ua.edu/devconference/

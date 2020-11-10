---
title: "Dask Performace Trip"
date: 2016-09-06
slug: Dask Performance Story
status: draft
---

I'm faced with a fairly specific problem: Compute the pairwise distances between
two matrices $X$ and $Y$ as quickly as possible. We'll assume that $Y$ is fairly
small, but $X$ may not fit in memory. This post tracks my progress.

---
title: Dask Workshop
date: 2019-12-12
slug: dask-workshop
status: draft
---


Dask Summit Recap

Last week was the first Dask Developer Workshop. This brought together many of
the core Dask developers and its heavy users to discuss the project. I want to
share some of the experience with those who weren't able to attend.

This was a great event. Aside from any technical discussions, it was ncie to
meet all the people. From new acquaintences to people you're on weekly calls
with, it was great to interact with everyone.

The workshop 

During our brief introductions, everyone included a one-phrase description of
what they'd most-like to see improved in the project. These can roughly be
grouped as

* **Project health**: more maintainers, more maintainer diversity, more commercial
  adoption
* **Deployments**: Support for heterogeneous clusters (e.g. some workers with
  different resources) on more cluster managers. Easier deployments for various
  use cases (single user vs. small team of scientists vs. enterprise IT managing
  things for a large team)
* **Documentation**: Including example
* **Data Access**: Loading data from various sources
* **Reliability**: Especially on adaptive clusters, as workers come and go.
* **Features**: Including things like approximate nearest neighbors, shared
  clients between futures, multi-column sorting, MultiIndex for dask.dataframe

One of the themes of the workshop was requests for honest, critical feedback
about what needs to improve. Overall, people had great things to say about Dask
and the various sub-projects but there's always things to improve.


Dask sits at a pretty interesting place in the scientific Python ecosystem. It
(and its users) are power-users of many libraries. It acts as a nice
coordination point for many projects. We had maintainers from projects like
NumPy, pandas, scikit-learn, Apache Arrow, cuDF, and others.

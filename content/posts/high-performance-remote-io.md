---
title: "High Performance Remote IO"
date: 2025-02-28T15:18:34-06:00
---

I have a new post up at the NVIDIA technical blog on [High-Performance Remote IO with NVIDIA KvikIO](https://developer.nvidia.com/blog/high-performance-remote-io-with-nvidia-kvikio/).[^1]

> In the RAPIDS context, NVIDIA KvikIO is notable because
> 1. It automatically chunks large requests into multiple smaller ones and makes those requests concurrently.
> 2. It can read efficiently into host or device memory, especially if GPU Direct Storage is enabled.
> 3. It’s fast.

This is mostly general-purpose advice on getting good performance out of cloud
object stores (I guess I can't get away from them), but has some specifics for
people using NVIDIA GPUs.

As part of preparing this, I got to write some C++. Not a fan!

[^1]: Did I mention I work at NVIDIA now? It's been a bit of a rush and I haven't had a chance to blog about it.
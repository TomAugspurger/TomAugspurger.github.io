---
title: "Cloud Native Geospatial Conference (2025)"
date: 2025-05-04T00:00:00-06:00
---

*You can watch a video version of this talk at https://youtu.be/BFFHXNBj7nA*

On Thursday, I presented a talk, *GPU Accelerated Cloud-Native Geospatial*, at the
inaugural Cloud-Native Geospatial Conference ([slides] here). This post will
give an overview of the talk and some background on the prep. But first I wanted
to say a bit about the conference itself.

The organizers (Michelle Roby, Jed Sundell, and others from Radiant Earth) did a
fantastic job putting on the event. I only have the smallest experience with
helping run a conference, but I know it's a ton of work. They did a great job
hosting this first run of conference.

The conference was split into three tracks:

1. On-ramp to Cloud-Native Geospatial (organized by [Dr. Julia Wagemann](https://www.linkedin.com/in/julia-wagemann/) from
   thriveGEO)
2. Cloud-Native Geospatial in Practice (organized by [Aimee Barciauskas](https://www.linkedin.com/in/abarciauskas/) from
   Development Seed)
3. Building Resilient Data ~Infrastructure~ Ecosystems (organized by [Dr. Brianna
   Pagán](https://www.linkedin.com/in/brianna-r-pag%C3%A1n-phd-8a49a46b/), also from Development Seed)

Each of the track leaders did a great job programming their session. As tends to
happen at these multi-track conferences, my only complaint is that there were
too many interesting talks to choose from. Fortunately, the sessions were
recorded and will be posted online. I spent most of my time bouncing between
Cloud-Native Geospatial in Practice and On-ramp to Cloud-native Geospatial, but
caught a couple talks from the Building Resilient Data Ecosystems track. 

My main goal at the conference was to listen to peoples' use-cases, with the
hope of identifying workloads that might benefit from GPU optimization. If *you*
have a geospatial workload that you want to GPU-optimize, please [contact
me](mailto:toaugspurger@nvidia.com).

## My Talk

I pitched this talk about two months into my tenure at NVIDIA, which is to say
about two months into my really using GPUs. In some ways, this made things
awkward: here I am, by no means a CUDA expert, in front of a room telling people
how they ought to be doing things. On the other hand, it's a strength. I'm
clearly not subject to the curse of expertise when it comes to GPUs, so I can
empathize with what ended up being my intended audience: people who are new to
GPUs and wondering if and where they can be useful for achieving their goals.

While preparing, I had some high hopes for doing deep-dives on a few geospatial
workloads (e.g. Radiometric Terrain Correction for SAR data, pytorch / torchgeo
/ xbatcher dataloaders and preprocessing). But between the short talk duration,
running out of prep time, and my general newness to GPUs, the talk ended up
being fairly introductory and high-level. I think that's OK.

### GPUs are Fast

This was a fun little demo of a "quadratic means" example I took from the
[Pangeo forum]. The hope was to get the room excited and impressed at just how
fast GPUs can be. In it, we optimized the runtime of the computation from about
3 seconds on the CPU to about 20 ms on the GPU (via a one-line change to use
[CuPy]).

For fun, we optimized it even further to just 4.5 ms by writing a hand-optimized
CUDA to use some shared memory tricks and avoid repeated memory accesses.

You can see the full demo at https://github.com/TomAugspurger/gpu-cng-2025. I
wish now that I had included more geospatial-focused demos. But the talk was
only 15-20 minutes and already packed.

### Getting Started with GPU programming

There is a *ton* of software written for NVIDIA chips. Before joining NVIDIA, I
didn't appreciate just how complex these chips are. NVIDIA, especially via
RAPIDS, offers a bunch of relatively easy ways to get started.

This slide from Jacob Tomlinson's PyData Global
[talk](https://global2024.pydata.org/cfp/talk/BUC3GV/) showcases the various
"swim lanes" when it comes to programming NVIDIA chips from Python:

![The "Swim Lanes" for getting started with GPUs. From easiest to use (zero code change) to maximum performance (C++ CUDA kernels)](https://github.com/user-attachments/assets/0b0aeda2-6cdc-4946-9b99-3dce73776f0f)

This built nicely off the demo, where we saw two of those swim lanes in action.

The other part lowering the barrier of entry is the cloud. Being programmable, a
GPU is just an API call away (assuming you're already set up on one of the
clouds providing GPUs).

### The I/O Problem

From there, we took a *very* high level overview of some geospatial workloads.
Each loads some data (which we assumed came from Blob Storage), computed some
result, and stored that result. For example, a cloud-free mosaic from some
Sentinel-2 imagery:

![Cloudless mosaic](https://ai4edatasetspublicassets.blob.core.windows.net/assets/notebook-output/tutorials-cloudless-mosaic-sentinel2.ipynb/9.png)

I'm realizing now that I should have included a vector data example, perhaps
loading an Overture Maps geoparquet file and doing a geospatial join.

Anyway, the point was to introduce some high-level concepts that we can use to
identify workloads amenable to GPU acceleration. First, we looked at a workloads
through time, which differ in how I/O vs. compute intensive they are.

For example, an I/O-bound workload:

<img src="/assets/cng-forum-2025-iobound.svg"/>

Contrast that with a (mostly) CPU-bound workload:

<img src="/assets/cng-forum-2025-compute.svg"/>

Trying to GPU-accelerate the I/O-bound workload will only bring disappointment: even if you manage to speed up the compute portion, it's such a small portion of the overall runtime to not make a meaningful difference.

But GPU-accelerating the compute-bound workload, on the other hand, can lead to
to a nice speedup:

<img src="/assets/cng-forum-2025-compute-optimized.svg"/>

A few things are worth emphasizing:

1. You need to profile your workload to understand where time is being spent.
2. You might be able to turn an I/O bound problem into a compute bound problem
   by optimizing it (choosing a better file format, placing your compute next to
   the storage, choosing a faster library for I/O, parallelization, etc.)
3. I'm implying that "I/O" is just sitting around waiting on the network. In
   reality, some of I/O will be spent doing "compute" things (like parsing and
   decompressing bytes.) And those portions of I/O can be GPU accelerated.
4. I glossed over the "memory barrier" at this point in the talk, but returned
   to it later. There are again libraries (like
   [KvikIO](https://docs.rapids.ai/api/kvikio/stable/)) that can help with this.

### Pipelining

*Some* (most?) problems can be broken into smaller units of work and,
potentially, parallelized. By breaking the larger problem into smaller pieces,
we have the opportunity to optimize the throughput of our workload through pipelining.

Pipelining lets us overlap various parts of the workload that are using
different parts of the system. For example I/O, which is mostly exercising the
network, can be pipelined with computation, which is mostly exercising the GPU.
First, we look at some poor pipelining:

<img src="/assets/cng-forum-2025-pipeline-bad.svg"/>

The workload serially reads data, computes the result, and writes the output.
This is inefficient: when you're reading or writing data the GPU is idle
(indeed, the CPU is mostly idle too, since it's waiting for bytes to move over
the network). And when you're computing the result, the CPU (and network) are
idle. This manifests as low utilization of the GPU, CPU, and network.

This second image shows good pipelining:

<img src="/assets/cng-forum-2025-pipeline-good.svg"/>

We've set up our program to read, compute, and write batches in parallel. We achieve high utilization of the GPU, CPU, and network.

This general concept can apply to CPU-only systems, especially multi-core
systems. But the pain of low resource utilization is more pronounced with GPUs,
which tend to be more expensive.

Now, this is a massively oversimplified example where the batches of work happen
to be nicely sized and the workload doesn't require an coordination across
batches. But, with effort, the technique can be applied to a wide range of
problems.

### Memory Bandwidth

This section was pressed for time, but I really wanted to at least touch on one
of the first things you'll hit when doing data analysis on the GPU: moving data
from host to device memory is relatively slow.

In the talk, I mostly just emphasized the benefits of leaving data on the GPU.
The memory hierarchy diagram from the [Flash
Attention](https://github.com/Dao-AILab/flash-attention) paper gave a nice
visual representation of the tradeoff between bandwidth and size the different
tiers give (I'd briefly mentioned the SRAM tier during the demo, since our most
optimized version used SRAM).

But as I mentioned in the talk, *most* people won't be interacting with the memory
hierarchy beyond minimizing transfers between the host and device.

## Reach Out

As I mentioned earlier my main goal attending the conference was to hear what
the missing pieces of the GPU-accelerated geospatial landscape are (and to catch
up with the wonderful members of this community). [Reach
out](mailto:toaugspurger@nvidia.com) with any feedback you might have.

[slides]: https://tomaugspurger.net/assets/gpu-accelerated-cng.pdf
[Pangeo forum]: https://discourse.pangeo.io/
[CuPy]: https://cupy.dev/

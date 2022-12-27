---
title: "Queues in the News"
date: 2022-12-26T13:35:24-06:00
---

I came across a couple of new (to me) uses of queues recently. When I came up with the title to this article I knew I had to write them up together.

## Queues in Dask

Over at the [Coiled Blog](https://www.coiled.io/blog/reducing-dask-memory-usage), Gabe Joseph has a nice post summarizing a huge amount of effort addressing a problem that's been vexing demanding Dask users for years. The main symptom of the problem was unexpectedly high memory usage on workers, leading to crashing workers (which in turn caused even more network communication, and so more memory usage, and more crashing workers). This is actually a problem I worked on a bit back in 2019, and I made very little progress.

A common source of this problem was having many (mostly) independent "chains" of computation. Dask would start on too many of the "root" tasks simultaneously, before finishing up some of the chains. The root tasks are typically memory increasing (e.g. load data from file system) while the later tasks are typically memory decreasing (take the mean of a large array).

In `dask/distributed`, Dask actually has two places where it determines which order to run things in. First, there's a "static" ordering (implemented in `dask/order.py`, which has some truly great docstrings, check out [the source](https://github.com/dask/dask/blob/main/dask/order.py).) Dask was actually doing really well here. Consider this task graph from [the issue](https://github.com/dask/distributed/issues/2602#issuecomment-496634172):

![](https://user-images.githubusercontent.com/1312546/58502338-f2599c00-814b-11e9-989a-5bfd2c3785a8.png)

The "root" tasks are on the left (marked 0, 3, 11, 14). Dask's typical depth-first algorithm works well here: we execute the first two root tasks (0 and 3) to finish up the first "chain" of computation (the box `(0, 0)` on the right) before moving onto the other two root nodes, 11 and 14.

The second time Dask (specifically, the distributed scheduler) considers what order to run things is at runtime. It gets this "static" ordering from `dask.order` which says what order you *should* run things in, but the distributed runtime has *way* more information available to it that it can use to influence its scheduling decisions. In this case, the distributed scheduler looked around and saw that it had some idle cores. It thought "hey, I have a bunch of these root tasks ready to run", and scheduled those. Those tend to increase memory usage, leading to our memory problems.

The solution was a queue. From [Gabe's blog post](https://www.coiled.io/blog/reducing-dask-memory-usage):

> We're calling this mode of scheduling ["queuing"](https://distributed.dask.org/en/stable/scheduling-policies.html#queuing), or "root task withholding". The scheduler puts data-loading tasks in an internal queue, and only drips one out to a worker once it's finished its current work and there's nothing more useful to run instead that utilizes the work it just completed.

## Queue for Data Pipelines

[At work](http://planetarycomputer.microsoft.com/), we're taking on more responsibility for the data pipeline responsible for getting various datasets to Azure Blob Storage. I'm dipping my toes into the whole "event-driven" architecture thing, and have become *paranoid* about dropping work. The [Azure Architecture Center](https://learn.microsoft.com/en-us/azure/architecture/) has a bunch of useful articles here. [This article](https://learn.microsoft.com/en-us/azure/architecture/patterns/competing-consumers) gives some names to some of the concepts I was bumbling through (e.g. "at least once processing").

In our case, we're using [Azure Queue Storage](https://learn.microsoft.com/en-us/azure/storage/queues/storage-queues-introduction) as a simple way to *reliably* parallelize work across some machines. We somehow discover some assets to be copied (perhaps by querying an API on a schedule, or by listening to some events on a webhook), store those as messages on the queue.

Then our workers can start processing those messages from the queue in parallel. The really neat thing about Azure's Storage Queues (and, I gather, many queue systems) is the concept of "locking" a message. When the worker is ready, it receives a message from the queue and begins processing it. To prevent dropping messages (if, e.g. the worker dies mid-processing) the message isn't actually deleted until the worker tells the queue service "OK, I'm doing processing this message". If for whatever reason the worker doesn't phone home saying it's processed the message, the message reappears on the queue for some other worker to process.

The [Azure SDK for Python](https://learn.microsoft.com/en-us/azure/developer/python/sdk/azure-sdk-overview) actually does a really good job integrating language features into the clients for these services. In this case, we can just treat the Queue service as an iterator.


```python
>>> queue_client = azure.storage.blob.QueueClient("https://queue-endpoint.queue.core.windows.net/queue-name")
>>> for message in queue_client.receive_messages():
...    yield message
...    # The caller finishes processing the message.
...    queue_client.delete_message(message)
```

I briefly went down a dead-end solution that added a "processing" state to our state database. Workers were responsible for updating the items state to "processing" as soon as they started, and "copied" or "failed" when they finished. But I quickly ran into issues where items were marked as "processing" but weren't actually. Maybe the node was preempted; maybe (just maybe) there was a bug in my code. But for whatever reason I couldn't trust the item's state anymore. Queues were an elegant way to ensure that we processed these messages at least once, and now I can sleep comfortably at night knowing that we aren't dropping messages on the floor.

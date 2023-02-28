---
title: "py-spy in Azure Batch"
date: 2023-02-22T15:11:37-06:00
---

Today, I was debugging a hanging task in [Azure Batch](https://learn.microsoft.com/en-us/azure/batch/batch-technical-overview).
This short post records how I used [py-spy][py-spy] to investigate the problem.

## Background

Azure Batch is a compute service that we use to run [container
workloads](https://learn.microsoft.com/en-us/azure/batch/batch-docker-container-workloads).
In this case, we start up a container that processes a bunch of GOES-GLM data to
create [STAC items](https://stacspec.org/en) for the [Planetary
Computer](http://planetarycomputer.microsoft.com/) . The workflow is essentially
a big

```python
for url in urls:
    local_file = download_url(url)
    stac.create_item(local_file)
```

We noticed that some Azure Batch tasks were hanging. Based on our logs, we knew
it was somewhere in that for loop, but couldn't determine exactly where things
were hanging. The [goes-glm] stactools package we used does read a NetCDF file,
and my experience with Dask biased me towards thinking the `netcdf` library (or
the HDF5 reader it uses) was hanging. But I wanted to confirm that before trying
to implement a fix.

## Debugging

I wasn't able to reproduce the hanging locally, so I needed some way to debug
the actual hanging process itself. My go-to tool for this type of task is
[py-spy][py-spy]. It does a lot, but in this case we'll use `py-spy dump` to get
something like a traceback for what's currently running (and hanging) in the
process.

Azure Batch has a handy feature for SSH-ing into the running task nodes. With an
auto-generated user and password, I had a shell on the node with the hanging
process.

The only wrinkle here is that we're using containerized workloads, so the actual
process was in a Docker container and not in the host's process list (I'll try
to follow Jacob Tomlinson's lead and be [intentional][intentional] about
container terminology). The `py-spy` documentation has some details on how to
use `py-spy` with docker. This [comment][comment] in particular has some more
details on how to run py-spy on the host to detect a process running in a
container. The upshot is a command like this, run on the Azure Batch node:

```
$ root@...:/home/yqjjaq/# docker run -it --pid=container:244fdfc65349 --rm --privileged --cap-add SYS_PTRACE python /bin/bash
```

where `244fdfc65349` is the ID of the container with the hanging process. I used
the `python` image and then `pip install`ed `py-spy` in that debugging container
(you could also use some container image with `py-spy` already installed).
Finally, I was able to run `py-spy dump` inside that running container to get
the trace:

```
root@306ad36c7ae3:/# py-spy dump --pid 1
Process 1: /opt/conda/bin/python /opt/conda/bin/pctasks task run blob://pctaskscommon/taskio/run/827e3fa4-be68-49c9-b8c3-3d63b31962ba/process-chunk/3/create-items/input --sas-token ... --account-url https://pctaskscommon.blob.core.windows.net/
Python v3.8.16 (/opt/conda/bin/python3.8)

Thread 0x7F8C69A78740 (active): "MainThread"
    read (ssl.py:1099)
    recv_into (ssl.py:1241)
    readinto (socket.py:669)
    _read_status (http/client.py:277)
    begin (http/client.py:316)
    getresponse (http/client.py:1348)
    _make_request (urllib3/connectionpool.py:444)
    urlopen (urllib3/connectionpool.py:703)
    send (requests/adapters.py:489)
    send (requests/sessions.py:701)
    request (requests/sessions.py:587)
    send (core/pipeline/transport/_requests_basic.py:338)
    send (blob/_shared/base_client.py:333)
    send (blob/_shared/base_client.py:333)
    send (core/pipeline/_base.py:100)
    send (core/pipeline/_base.py:69)
    send (core/pipeline/_base.py:69)
    send (blob/_shared/policies.py:290)
    send (core/pipeline/_base.py:69)
    send (core/pipeline/_base.py:69)
    send (core/pipeline/_base.py:69)
    send (blob/_shared/policies.py:489)
    send (core/pipeline/_base.py:69)
    send (core/pipeline/policies/_redirect.py:160)
    send (core/pipeline/_base.py:69)
    send (core/pipeline/_base.py:69)
    send (core/pipeline/_base.py:69)
    send (core/pipeline/_base.py:69)
    send (core/pipeline/_base.py:69)
    run (core/pipeline/_base.py:205)
    download (blob/_generated/operations/_blob_operations.py:180)
    _initial_request (blob/_download.py:386)
    __init__ (blob/_download.py:349)
    download_blob (blob/_blob_client.py:848)
    wrapper_use_tracer (core/tracing/decorator.py:78)
    <lambda> (core/storage/blob.py:514)
    with_backoff (core/utils/backoff.py:136)
    download_file (core/storage/blob.py:513)
    create_item (goes_glm.py:32)
    create_items (dataset/items/task.py:117)
    run (dataset/items/task.py:153)
    parse_and_run (task/task.py:53)
    run_task (task/run.py:138)
    run_cmd (task/_cli.py:32)
    run_cmd (task/cli.py:50)
    new_func (click/decorators.py:26)
    invoke (click/core.py:760)
    invoke (click/core.py:1404)
    invoke (click/core.py:1657)
    invoke (click/core.py:1657)
    main (click/core.py:1055)
    __call__ (click/core.py:1130)
    cli (cli/cli.py:140)
    <module> (pctasks:8)
Thread 0x7F8C4A84F700 (idle): "fsspecIO"
    select (selectors.py:468)
    _run_once (asyncio/base_events.py:1823)
    run_forever (asyncio/base_events.py:570)
    run (threading.py:870)
    _bootstrap_inner (threading.py:932)
    _bootstrap (threading.py:890)
Thread 0x7F8C4A00E700 (active): "ThreadPoolExecutor-0_0"
    _worker (concurrent/futures/thread.py:78)
    run (threading.py:870)
    _bootstrap_inner (threading.py:932)
    _bootstrap (threading.py:890)
```

And we've found our culprit! The line

```
download_file (core/storage/blob.py:513)
```

and everything above it indicates that the process is hanging in the *download*
stage, not the NetCDF reading stage!

## This fix

"Fixing" this is pretty easy. The Python SDK for Azure Blob Storage includes the
option to set a `read_timeout` when creating the connection client. Now if the
download hangs it should raise a `TimeoutError`. Then our handler will
automatically catch and retry it, and hopefully succeed. It doesn't address
the actual cause of something deep inside
the networking stack hanging, but it's good enough for our purposes.

Update: 2023-02-28. Turns out, the "fix" wasn't actually a fix. The process hung
again the next day. Naturally, I turned to this blog post to find the incantations
to run (which is why I wrote it in the first place).

As for getting closer to an actual cause of the hang, a colleague suggested upgrading
Python versions since there were some fixes in that area between 3.8 and 3.11. After
about a week, there have been zero hangs on Python 3.11.

[py-spy]: https://github.com/benfred/py-spy
[goes-glm]: https://github.com/stactools-packages/goes-glm
[comment]: https://github.com/benfred/py-spy/issues/49
[intentional]: https://jacobtomlinson.dev/posts/2023/being-intentional-with-container-terminology/

Title: What's Next?
Date: 2020-11-11
Slug: whats-next

Some personal news: Last Friday was my last day at [Anaconda].
Next week, I'm joining Microsoft's [AI for Earth] team. This is a very bittersweet transition. While I loved working at Anaconda and all the great people there, I'm extremely excited about what I'll be working on at Microsoft.

## Reflections

I was inspired to write this section by Jim Crist's post on a similar topic: [https://jcristharif.com/farewell-to-anaconda.html](https://jcristharif.com/farewell-to-anaconda.html).
I'll highlight some of the projects I worked on while at Anaconda. If you want to skip the navel gazing, skip down to [what's next](#whats-next).

1. This is self-serving and biased to over-emphasize my own role in each of these. None of these could be done without the other individuals on those teams, or the support of my family.
2. More companies should support open-source like Anaconda does: offer positions to the maintainers of open-source projects and see what they can do. Anaconda [recently announced](https://www.anaconda.com/blog/sustaining-the-open-source-ds-ml-ecosystem-with-the-anaconda-dividend-program) a program that makes it easier for more companies to support open-source.

### pandas

<img src="https://pandas.pydata.org/static/img/pandas.svg"/>

If I had a primary responsibility at Anaconda, it was stewarding the pandas project. When I joined Anaconda in 2017, pandas was around the 0.20 release, and didn't have much in the way of paid maintenace. By joining Anaconda I was fulfilling a dream: getting paid to work on open-source software. During my time at Anaconda, I was the pandas release manager for a handful of pandas releases, including pandas 1.0.

I think the most important *code* to come out of my work on pandas is the [extension array interface](https://pandas.pydata.org/pandas-docs/stable/development/extending.html). My post on the [Anaconda Blog](https://www.anaconda.com/blog/cyberpandas-extending-pandas-with-richer-types) tells the full story, but this is a great example of a for-profit company (Anaconda) bringing together a funding source and an open-source project to accomplish something great for the community. As an existing member of the pandas community, I was able to leverage some trust that I'd built up over the years to propose a major change to the library. And thanks to Anaconda, we had the funding to realisitically pull (some of) it off. The work is still ongoing, but we're gradually solving some of pandas' longest-standing pain points (like the lack of an integer dtype with missing values). 

But even more important that the code is probably pandas winning its first-ever funding through the [CZI EOSS program](https://chanzuckerberg.com/eoss/). Thanks to Anaconda, I was able to dedicate the time to writing the proposal. This work funded

1. Maintenance, including [Simon Hawkins](https://github.com/simonjayhawkins) managing the last few releases.
2. A native string dtype, based on Apache Arrow, for faster and more memory-efficient strings (coming in the next release or two)
3. Many improvements to the extension array interface

Now that I'm leaving Anaconda, I suspect my day-to-day involvement in pandas will drop off a bit. But I'll still be around, hopefully focusing most on helping others work on pandas.

Oh, side-note, I'm extremely excited about the [duplicate label handling](https://pandas.pydata.org/docs/dev/user_guide/duplicates.html) coming to pandas 1.2.0. That was fun to work on and I think will solve some common pandas papercuts.

### Dask

<img src="https://docs.dask.org/en/latest/_images/dask_horizontal.svg"/>

I started using Dask before I joined Anaconda. It exactly solved my needs at the time (I was working with datasets that were somewhat larger
than the memory of the machine I had access to). I was thrilled to have more time for working on it along with others from Anaconda; I learned a ton from them.

My personal work mainly focused on ensuring that `dask.dataframe` continued to work well with (and benefit from) the most recent changes to pandas. I also kicked off the [`dask-ml`](http://ml.dask.org) project, which initially just started as a bit of documentation on the various projects in the "dask / machine learning" space (like `distributed.joblib`, `dask-searchcv`, `dask-xgboost`). Eventually this grew into a project of its own, which I'm reasonably happy with, even if most people don't need distributed machine learning.

### pymapd

[pymapd](https://github.com/omnisci/pymapd) is a Python library that implements the [DB API spec](https://www.python.org/dev/peps/pep-0249/) for OmniSci (FKA MapD). For the most part, this project involved copying the choices made by `sqlite3` or `psycopg2` and applying them to. The really fun part of this project was working with Wes McKinney, Siu Kwan Lam, and others on the GPU and shared memory integration. Being able to query a database and get back zero-copy results as a DataFrame (possibly a GPU DataFrame using cuDF) really is neat.

### ucx-py

[ucx-py](https://github.com/rapidsai/ucx-py) is a Python library for UCX, a high-performance networking library. This came out of work with NVIDIA and Dask, seeing how we could speed up performance on communication-bound workloads (UCX supports high-performance interfaces between devices like NVLink). Working on ucx-py was my first real foray into asyncio and networking. Fortunately, while this was a great learning experience for me, I suspect that very little of *my* code remains. Hopefully the early prototypes were able to hit some of the roadblocks the later attempts would have stumbled over. See [this post](https://medium.com/rapids-ai/high-performance-python-communication-with-ucx-py-221ac9623a6a) for an overview of what that team has been able to accomplish recently.

### Pangeo

<img src="https://raw.githubusercontent.com/pangeo-data/pangeo/3b2f9de1bc74625490684204a8431037e00a9ba1/docs/_static/pangeo_simple_logo.svg"/>

Some time last year, after Matt Rocklin left for NVIDIA, I filled his spot on a [NASA ACCESS grant](https://github.com/pangeo-data/nasa-access-17) funding work on the Pangeo project. Pangeo is a really interesting community. They're a bunch of geoscientists trying to analyze large datasets using tools like xarray, Zarr, Dask, holoviz, and Jupyter. Naturally, they find rough edges in that workflow, and work to fix them. That might mean working with organizations like NASA to provide data in analysis-ready form. It might mean fixing bugs or performance issues in libraries like Dask. Being able to dedicate large chunks of time is crucial to solving these types of thorny problems, which often span many layers (e.g. using xarray to read data Zarr data from Google cloud storage involves something like eight Python libraries). While there's still work to be done, this type of workflow is smoother than it was a couple years ago.

In addition to work on Dask itself, I was able to help out Pangeo in a few other ways:

1. I helped maintain pangeo's JupyterHub deployments at [pangeo-cloud-federation](https://github.com/pangeo-data/pangeo-cloud-federation). (FYI, [2i2c](https://2i2c.org) is a new organization that's purpose-built to do this kind of work).
2. I put together the [`daskhub` Helm Chart](https://github.com/dask/helm-chart/blob/master/daskhub/README.md), which Pangeo previously developed and maintained. It combines Dask Gateway's and JupyterHub's helm charts, along with experience from pangeo's deployments, to deploy a multi-user JupyterHub deployment with scalable computation provided by Dask.
3. I helped with [`rechunker`](http://rechunker.readthedocs.io), a library that very specifically solves a problem that had [vexxed pangeo's community members for years](https://discourse.pangeo.io/t/best-practices-to-go-from-1000s-of-netcdf-files-to-analyses-on-a-hpc-cluster/588).

Overall, working with the Pangeo folks has been incredibly rewarding. They're taking the tools we know and love, and putting them together to build an extremely powerful, [open architechture](https://medium.com/pangeo/closed-platforms-vs-open-architectures-for-cloud-native-earth-system-analytics-1ad88708ebb6) toolchain. I've been extremely lucky to work on this project. Which brings me to...

<h2 id=whats-next>What's Next</h2>

As I mentioned up top, I'm joining the AI for Earth team at Microsoft. I'll be helping them build tools and environments for distributed geospatial data processing! I'm really excited about this work. Working with the Pangeo community has been incredibly rewarding. I'm lookingo forward to doing even more of that.

P.S. [we're hiring](https://careers.microsoft.com/us/en/job/876975/Senior-Geospatial-Applications-Engineer-AI-for-Earth)!

[Anaconda]: https://www.anaconda.com
[AI for Earth]: https://www.microsoft.com/en-us/ai/ai-for-earth

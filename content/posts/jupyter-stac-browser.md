---
title: "Jupyter, STAC, and Tool Building"
date: 2023-04-15T08:00:00-05:00
slug: "jupyter-stac-browser"
---

Over in Planetary Computer land, we're [working on](https://github.com/microsoft/planetary-computer-tasks/pull/167) bringing [Sentinel-5P](https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-5p) into our STAC catalog.

STAC items require a `geometry` property, a GeoJSON object that describes the footprint of the assets. Thanks to the satellites' orbit and the (spatial) size of the assets, we started with some...interesting... footprints:

![](https://user-images.githubusercontent.com/58314/231868547-21c786b9-dc88-4830-a07f-7aa3c1fdebc6.png)

That initial footprint, shown in orange, would render the STAC collection essentially useless for spatial searches. The assets don't actually cover (most of) the southern hemisphere.

[Pete Gadomski](https://fosstodon.org/@gadomski) did some really great work to understand the problem and fix it (hopefully once and for all). As the satellite crosses the antimeridian, a pole, or both, naive approaches to generating a footprint fails. It takes some more [complicated logic](https://github.com/gadomski/antimeridian/blob/main/src/antimeridian/_implementation.py) to generate a good geometry. That's now available as [antimeridian](https://pypi.org/project/antimeridian) on PyPI. It produces much more sensible footprints:

![](https://user-images.githubusercontent.com/58314/231868768-5439edcd-5e5a-40a9-b3f9-12947a081b85.png)

## Building Tools

The real reason I wanted to write this post was to talk about tool building. This is a common theme of the [Oxide and Friends](https://oxide.computer/podcasts/oxide-and-friends) podcast, but I think spending time building these kinds of small, focused tools almost always pays off.

Pete had a handful of [pathologic test cases](https://github.com/gadomski/antimeridian/tree/main/tests/data/input) in the antimeridian test suite, but I wanted a way to quickly examine hundreds of footprints that I got back from our test STAC catalog. There are probably already tools for this, but I was able to put one together in Jupyter in about 10 minutes by building on [Jupyter Widgets](https://ipywidgets.readthedocs.io/en/latest/#) and [ipyleaflet](https://ipyleaflet.readthedocs.io/en/latest/index.html).

You can see it in action here (using Sentinel-2 footprints rather than Sentinel 5-P):

<video controls="" width="600" src="https://ai4edatasetspublicassets.blob.core.windows.net/assets/pc_video/interact-stac-browser-web.mp4">
</video>

We get a STAC footprint browser (connected to our Python kernel!) with a single, pretty simple function.

```python
m = ipyleaflet.Map(zoom=3)
m.layout.width = "600px"
layer = ipyleaflet.GeoJSON()
m.add(layer)


@ipywidgets.interact(item: pystac.ItemCollection = items)
def browse(item: pystac.Item):
    shape = shapely.geometry.shape(item)
    m.center = tuple(shape.centroid.coords[0])[::-1]

    layer.data = item.geometry
    print(item.id, item.datetime.isoformat())
```

Using this browser, I could quickly scrub through the Sentinel-5P items with the arrow keys and verify that the footprints looked reasonable.

The demo for this lives in the [Planetary Computer Examples](https://github.com/microsoft/PlanetaryComputerExamples/) repository, and you can view the [rendered version](https://nbviewer.org/github/microsoft/PlanetaryComputerExamples/blob/main/tutorials/interactive-browser.ipynb).

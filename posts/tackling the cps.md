.. title: Using Python to tackle the CPS
.. date: 2014-01-27 12:00
.. slug: tackling the cps
.. category: python

The [Current Population Survey](http://www.census.gov/cps/) is an important source of data for economists. It's modern form took shape in the 70's and unfortunately the data format and distribution shows its age. Some centers like [IPUMS](https://cps.ipums.org/cps/) have attempted to put a nicer face on accessing the data, but they haven't done everything yet. In this series I'll describe methods I used to fetch, parse, and analyze CPS data for my second year paper. Today I'll describe fetching the data. Everything is available at the paper's [GitHub Repository](https://github.com/TomAugspurger/dnwr-zlb).

Before diving in, you should know a bit about the data. I was working with the monthly microdata files from the CPS. These are used to estimate things like the unemployment rate you see reported every month. Since around 2002, about 60,000 households are interviewed 8 times each over a year. They're interviewed for 4 months, take 4 months off, and are interviewed for 4 more months after the break. Questions are asked about demographics, education, economic activity (and more).

## Fetching the Data

This was probably the easiest part of the whole project.
The [CPS website](http://www.nber.org/data/cps_basic.html) has links to all the monthly files and some associated data dictionaries describing the layout of the files (more on this later).

In [`monthly_data_downloader.py`](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/monthly_data_downloader.py) I fetch files from the CPS website and save them locally.  A common trial was the CPS's inconsistency. Granted, consistency and backwards compatibility are difficult, and sometimes there are valid reasons for making a break, but at times the changes felt excessive and random. Anyway for January 1976 to December 2009 the URL pattern is `http://www.nber.org/cps-basic/cpsb****.Z`, and from January 2010 on its `http://www.nber.org/cps-basic/jan10`.

If you're curious the python regex used to match those two patterns is `re.compile(r'cpsb\d{4}.Z|\w{3}\d{2}pub.zip|\.[ddf,asc]$')`. Yes that's much clearer.

I used python's builtin [`urllib2`](http://docs.python.org/2/library/urllib2.html) to fetch the site contents and parse with `lxml`. You should *really* just use [requests](http://docs.python-requests.org/en/latest/), instead of `urllib2` but I wanted to keep dependencies for my project slim (I gave up on this hope later).

A common pattern I used was to parse all of the links on a website, filter out the ones I don't want, and do something with the ones I do want. Here's an example:

```python
for link in ifilter(partial_matcher, root.iterlinks()):
    _, _, _fname, _ = link
    fname = _fname.split('/')[-1]
    existing = _exists(os.path.join(out_dir, fname))
    if not existing:
        downloader(fname, out_dir)
        print('Added {}'.format(fname))
```

`root` is just the parsed html from `lxml.parse`. `iterlinks()` returns an iterable, which I filter through `partial_matcher`, a function that matches the filename patterns I described above. Iterators are my favorite feature of Python (not that they are exclusive to Python; I just love easy and flexible they are). The idea of having a list, filtering it, and applying a function to the ones you want is so simple, but so generally applicable. I could have even been a bit more functional and written it as `imap(downloader(ifilter(existing, ifilter(partial_matcher, root.iterlinks()))`. Lovely in its own way!

I do some checking to see if the file exists (so that I can easily download new months). If it is a new month, the filename gets passed to `downloader`:

```
def downloader(link, out_dir, dl_base="http://www.nber.org/cps-basic/"):
    """
    Link is a str like cpsmar06.zip; It is both the end of the url
    and the filename to be used.
    """
    content = urllib2.urlopen(dl_base + link)
    with open(out_dir + link, 'w') as f:
        f.write(content.read())
```

This reads the data from at url and write writes it do a file.

Finally, I run [`renamer.py`](https://github.com/TomAugspurger/dnwr-zlb/blob/master/data_wrangling/cps_wrangling/panel_construction/renamer.py) to clean up the file names. Just because the CPS is inconsistent doesn't mean that we have to be.

In the [next post](http://tomaugspurger.github.io/blog/2014/02/04/tackling%20the%20cps%20(part%202)/) I'll describe parsing the files we just downloaded.

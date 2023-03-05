---
title: Introducing Stitch
date: 2016-08-30
aliases:
  - /introducing-stitch.html
---

Today I released [`stitch`](https://github.com/pystitch/stitch) into the
wild. If you haven't yet, check out the [examples
page](https://pystitch.github.io) to see an example of what stitch does,
and the [Github repo](https://github.com/pystitch/stitch) for how to
install. I'm using this post to explain why I wrote stitch, and some
issues it tries to solve.

Why [knitr](http://yihui.name/knitr/) / [knitpy](https://github.com/janschulz/knitpy) / stitch / [RMarkdown](http://rmarkdown.rstudio.com)?
-------------------------------------------------------------------------------------------------------------------------------------------

Each of these tools or formats have the same high-level goal: produce
reproducible, dynamic (to changes in the data) reports. They take some
source document (typically markdown) that's a mixture of text and code
and convert it to a destination output (HTML, PDF, docx, etc.).

The main difference from something like pandoc, is that these tools
actually execute the code and interweave the output of the code back
into the document.

Reproducibility is something I care very deeply about. My workflow when
writing a report is typically

-   prototype in the notebook or IPython REPL (data cleaning, modeling,
    visualizing, repeat)
-   rewrite and cleanup those prototypes in a `.py` file that produces
    one or more outputs (figure, table, parameter, etc.)
-   Write the prose contextualizing a figure or table in markdown
-   Source output artifacts (figure or table) when converting the
    markdown to the final output

This was fine, but had a lot of overhead, and separated the generated
report from the code itself (which is sometimes, but not always, what
you want).

Stitch aims to make this a simpler process. You (just) write your code
and results all in one file, and call

```
stitch input.md -o output.pdf
```


Why not Jupyter Notebooks?
--------------------------

A valid question, but I think misguided. I love the notebook, and I use
it every day for exploratory research. That said, there's a continuum
between all-text reports, and all-code reports. For reports that have a
higher ratio of `text:code`, I prefer writing in my comfortable
text-editor (yay spellcheck!) and using stitch / pandoc to compile the
document. For reports that have more `code:text`, or that are very early
on in their lifecycle, I prefer notebooks. Use the right tool for the
job.

When writing my [pandas ebook](https://leanpub.com/effective-pandas), I
had to [jump through
hoops](https://github.com/TomAugspurger/modern-pandas/blob/master/Makefile)
to get from notebook source to final output (epub or PDF) that looked
OK. [NBConvert](https://nbconvert.readthedocs.io) was essential to that
workflow, and I couldn't have done without it. I hope that the
stitch-based workflow is a bit smoother.

If a tool similar to [podoc](https://github.com/podoc/podoc/) is
developed, then we can have transparent conversion between text-files
with executable blocks of code and notebooks. Living the dream.

Why python?
-----------

While RMarkdown / knitr are great (and way more usable than stitch at
this point), they're essentially only for R. The support for other
languages (last I checked) is limited to passing a code chunk into the
`python` command-line executable. All state is lost between code chunks.

*Stitch supports any language that implements a Jupyter kernel*, which
is [a
lot](https://github.com/ipython/ipython/wiki/IPython-kernels-for-other-languages).

Additionally, when RStudio introduced [R
Notebooks](http://rmarkdown.rstudio.com/r_notebooks.html), they did so
with their own file format, rather than adopting the Jupyter notebook
format. I assume that they were aware of the choice when going their own
way, and made it for the right reasons. But for these types of tasks
(things creating documents) I prefer language-agnostic tools *where
possible*. It's certain that RMarkdown / knitr are better than stitch
right now for rendering `.Rmd` files. It's quite likely that they will
*always* be better at working with R than stitch; specialized tools
exist for a reason.

Misc.
-----

Stitch was heavily inspired by Jan Schulz's
[knitpy](https://github.com/janschulz/knitpy), so you might want to
check that out and see if it fits your needs better. Thanks to Jan for
giving guidance on difficulty areas he ran into when writing knitpy.

I wrote stitch in about three weeks of random nights and weekends I had
free. I stole time that from family or maintaining pandas. Thanks to my
wife and the pandas maintainers for picking up my slack.

The three week thing isn't a boast. It's a testament to the rich
libraries already available. Stitch simply would not exist if we
couldn't reuse

-   [pandoc](http://pandoc.org) via
    [pypandoc](https://pypi.python.org/pypi/pypandoc) for parsing
    markdown and converting to the destination output (and for
    installing pandoc via conda-forge)
-   [Jupyter](http://jupyter.readthedocs.io/en/latest/) for providing
    kernels as execution contexts and a
    [client](https://jupyter-client.readthedocs.io) for easily
    communicating with them.
-   [pandocfilters](https://github.com/jgm/pandocfilters) for wrapping
    code-chunk output

And of course RMarkdown, knitr, and knitpy for proving that a library
like this is useful and giving a design that works.

Stitch is still extremely young. It could benefit from users trying it
out, and letting me know what's working and what isn't. Please do give
it a shot and let me know what you think.

© Tom Augspurger

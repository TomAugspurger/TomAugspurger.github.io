.. title: Pandas Flow
.. date: 2015-01-18 9:00
.. slug: pandas-assign
.. tags: python, data science, pandas
.. status: draft

Pandas 0.16 is [brining](https://github.com/pydata/pandas/pull/9239) a new method to DataFrames, `assign`.
It's heavily inspired by (dplyr's)[http://cran.rstudio.com/web/packages/dplyr/vignettes/introduction.html] `mutate` verb.

Since I wrote my [pandas-dplyr](https://gist.github.com/TomAugspurger/6e052140eaa5fdb6e8c0) comparison,
I've been using more chains of opertions in my code.
The biggest stumbling block to this style has been introducing
new variables. It's simple to create a new column, e.g. with
`df['new_col'] = new_value`, where `new_value` is a constant or array. But
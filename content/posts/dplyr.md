---
title: dplyr and pandas
# date: 2014-10-16
# date: 2020-01-01
# date: 2020-04-01
date: 2023-02-22T15:11:37-06:00
slug: dplyr-pandas
tags:
  - python
  - data science
  - pandas
aliases:
  - dplry-pandas
---


This notebook compares [pandas](http://pandas.pydata.org)
and [dplyr](http://cran.r-project.org/web/packages/dplyr/index.html).
The comparison is just on syntax (verbage), not performance. Whether you're an R user looking to switch to pandas (or the other way around), I hope this guide will help ease the transition.

We'll work through the [introductory dplyr vignette](http://cran.r-project.org/web/packages/dplyr/vignettes/introduction.html) to analyze some flight data.

I'm working on a better layout to show the two packages side by side.
But for now I'm just putting the ``dplyr`` code in a comment above each python call.


```python
# Some prep work to get the data from R and into pandas
%matplotlib inline
%load_ext rmagic

import pandas as pd
import seaborn as sns

pd.set_option("display.max_rows", 5)
```

    /Users/tom/Envs/py3/lib/python3.4/site-packages/IPython/extensions/rmagic.py:693: UserWarning: The rmagic extension in IPython is deprecated in favour of rpy2.ipython. If available, that will be loaded instead.
    http://rpy.sourceforge.net/
      warnings.warn("The rmagic extension in IPython is deprecated in favour of "



```r
%%R
library("nycflights13")
write.csv(flights, "flights.csv")
```

# Data: nycflights13


```python
flights = pd.read_csv("flights.csv", index_col=0)
```


```python
# dim(flights)   <--- The R code
flights.shape  # <--- The python code
```




    (336776, 16)




```python
# head(flights)
flights.head()
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 517</td>
      <td> 2</td>
      <td>  830</td>
      <td> 11</td>
      <td> UA</td>
      <td> N14228</td>
      <td> 1545</td>
      <td> EWR</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1400</td>
      <td> 5</td>
      <td> 17</td>
    </tr>
    <tr>
      <th>2</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 533</td>
      <td> 4</td>
      <td>  850</td>
      <td> 20</td>
      <td> UA</td>
      <td> N24211</td>
      <td> 1714</td>
      <td> LGA</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1416</td>
      <td> 5</td>
      <td> 33</td>
    </tr>
    <tr>
      <th>3</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 542</td>
      <td> 2</td>
      <td>  923</td>
      <td> 33</td>
      <td> AA</td>
      <td> N619AA</td>
      <td> 1141</td>
      <td> JFK</td>
      <td> MIA</td>
      <td> 160</td>
      <td> 1089</td>
      <td> 5</td>
      <td> 42</td>
    </tr>
    <tr>
      <th>4</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 544</td>
      <td>-1</td>
      <td> 1004</td>
      <td>-18</td>
      <td> B6</td>
      <td> N804JB</td>
      <td>  725</td>
      <td> JFK</td>
      <td> BQN</td>
      <td> 183</td>
      <td> 1576</td>
      <td> 5</td>
      <td> 44</td>
    </tr>
    <tr>
      <th>5</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 554</td>
      <td>-6</td>
      <td>  812</td>
      <td>-25</td>
      <td> DL</td>
      <td> N668DN</td>
      <td>  461</td>
      <td> LGA</td>
      <td> ATL</td>
      <td> 116</td>
      <td>  762</td>
      <td> 5</td>
      <td> 54</td>
    </tr>
  </tbody>
</table>
</div>



# Single table verbs

``dplyr`` has a small set of nicely defined verbs. I've listed their closest pandas verbs.


<table>
  <tr>
    <td><b>dplyr</b></td>
    <td><b>pandas</b></td>
  </tr>
  <tr>
    <td>filter() (and slice())</td>
    <td>query() (and loc[], iloc[])</td>
  </tr>
  <tr>
    <td>arrange()</td>
    <td>sort()</td>
  </tr>
  <tr>
  <td>select() (and rename())</td>
    <td>\_\_getitem\_\_ (and rename())</td>
  </tr>
  <tr>
  <td>distinct()</td>
    <td>drop_duplicates()</td>
  </tr>
  <tr>
    <td>mutate() (and transmute())</td>
    <td>None</td>
  </tr>
  <tr>
    <td>summarise()</td>
    <td>None</td>
  </tr>
  <tr>
    <td>sample_n() and sample_frac()</td>
    <td>None</td>
  </tr>
</table>


Some of the "missing" verbs in pandas are because there are other, different ways of achieving the same goal. For example `summarise` is spread across `mean`, `std`, etc. Others, like `sample_n`, just haven't been implemented yet.

# Filter rows with filter(), query()


```python
# filter(flights, month == 1, day == 1)
flights.query("month == 1 & day == 1")
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1  </th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 517</td>
      <td>  2</td>
      <td> 830</td>
      <td> 11</td>
      <td> UA</td>
      <td> N14228</td>
      <td> 1545</td>
      <td> EWR</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1400</td>
      <td>  5</td>
      <td> 17</td>
    </tr>
    <tr>
      <th>2  </th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 533</td>
      <td>  4</td>
      <td> 850</td>
      <td> 20</td>
      <td> UA</td>
      <td> N24211</td>
      <td> 1714</td>
      <td> LGA</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1416</td>
      <td>  5</td>
      <td> 33</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>841</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> AA</td>
      <td> N3EVAA</td>
      <td> 1925</td>
      <td> LGA</td>
      <td> MIA</td>
      <td> NaN</td>
      <td> 1096</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>842</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> B6</td>
      <td> N618JB</td>
      <td>  125</td>
      <td> JFK</td>
      <td> FLL</td>
      <td> NaN</td>
      <td> 1069</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>842 rows × 16 columns</p>
</div>



The more verbose version:


```python
# flights[flights$month == 1 & flights$day == 1, ]
flights[(flights.month == 1) & (flights.day == 1)]
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1  </th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 517</td>
      <td>  2</td>
      <td> 830</td>
      <td> 11</td>
      <td> UA</td>
      <td> N14228</td>
      <td> 1545</td>
      <td> EWR</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1400</td>
      <td>  5</td>
      <td> 17</td>
    </tr>
    <tr>
      <th>2  </th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 533</td>
      <td>  4</td>
      <td> 850</td>
      <td> 20</td>
      <td> UA</td>
      <td> N24211</td>
      <td> 1714</td>
      <td> LGA</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1416</td>
      <td>  5</td>
      <td> 33</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>841</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> AA</td>
      <td> N3EVAA</td>
      <td> 1925</td>
      <td> LGA</td>
      <td> MIA</td>
      <td> NaN</td>
      <td> 1096</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>842</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> B6</td>
      <td> N618JB</td>
      <td>  125</td>
      <td> JFK</td>
      <td> FLL</td>
      <td> NaN</td>
      <td> 1069</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>842 rows × 16 columns</p>
</div>




```python
# slice(flights, 1:10)
flights.iloc[:9]
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 517</td>
      <td> 2</td>
      <td> 830</td>
      <td> 11</td>
      <td> UA</td>
      <td> N14228</td>
      <td> 1545</td>
      <td> EWR</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1400</td>
      <td> 5</td>
      <td> 17</td>
    </tr>
    <tr>
      <th>2</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 533</td>
      <td> 4</td>
      <td> 850</td>
      <td> 20</td>
      <td> UA</td>
      <td> N24211</td>
      <td> 1714</td>
      <td> LGA</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1416</td>
      <td> 5</td>
      <td> 33</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>8</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 557</td>
      <td>-3</td>
      <td> 709</td>
      <td>-14</td>
      <td> EV</td>
      <td> N829AS</td>
      <td> 5708</td>
      <td> LGA</td>
      <td> IAD</td>
      <td>  53</td>
      <td>  229</td>
      <td> 5</td>
      <td> 57</td>
    </tr>
    <tr>
      <th>9</th>
      <td> 2013</td>
      <td> 1</td>
      <td> 1</td>
      <td> 557</td>
      <td>-3</td>
      <td> 838</td>
      <td> -8</td>
      <td> B6</td>
      <td> N593JB</td>
      <td>   79</td>
      <td> JFK</td>
      <td> MCO</td>
      <td> 140</td>
      <td>  944</td>
      <td> 5</td>
      <td> 57</td>
    </tr>
  </tbody>
</table>
<p>9 rows × 16 columns</p>
</div>



# Arrange rows with arrange(), sort()


```python
# arrange(flights, year, month, day) 
flights.sort(['year', 'month', 'day'])
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1     </th>
      <td> 2013</td>
      <td>  1</td>
      <td>  1</td>
      <td> 517</td>
      <td>  2</td>
      <td> 830</td>
      <td> 11</td>
      <td> UA</td>
      <td> N14228</td>
      <td> 1545</td>
      <td> EWR</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1400</td>
      <td>  5</td>
      <td> 17</td>
    </tr>
    <tr>
      <th>2     </th>
      <td> 2013</td>
      <td>  1</td>
      <td>  1</td>
      <td> 533</td>
      <td>  4</td>
      <td> 850</td>
      <td> 20</td>
      <td> UA</td>
      <td> N24211</td>
      <td> 1714</td>
      <td> LGA</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1416</td>
      <td>  5</td>
      <td> 33</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>111295</th>
      <td> 2013</td>
      <td> 12</td>
      <td> 31</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> UA</td>
      <td>    NaN</td>
      <td>  219</td>
      <td> EWR</td>
      <td> ORD</td>
      <td> NaN</td>
      <td>  719</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>111296</th>
      <td> 2013</td>
      <td> 12</td>
      <td> 31</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> UA</td>
      <td>    NaN</td>
      <td>  443</td>
      <td> JFK</td>
      <td> LAX</td>
      <td> NaN</td>
      <td> 2475</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>336776 rows × 16 columns</p>
</div>




```python
# arrange(flights, desc(arr_delay))
flights.sort('arr_delay', ascending=False)
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>7073  </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  9</td>
      <td>  641</td>
      <td> 1301</td>
      <td> 1242</td>
      <td> 1272</td>
      <td> HA</td>
      <td> N384HA</td>
      <td>   51</td>
      <td> JFK</td>
      <td> HNL</td>
      <td> 640</td>
      <td> 4983</td>
      <td>  6</td>
      <td> 41</td>
    </tr>
    <tr>
      <th>235779</th>
      <td> 2013</td>
      <td> 6</td>
      <td> 15</td>
      <td> 1432</td>
      <td> 1137</td>
      <td> 1607</td>
      <td> 1127</td>
      <td> MQ</td>
      <td> N504MQ</td>
      <td> 3535</td>
      <td> JFK</td>
      <td> CMH</td>
      <td>  74</td>
      <td>  483</td>
      <td> 14</td>
      <td> 32</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>336775</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
      <td>  NaN</td>
      <td>  NaN</td>
      <td>  NaN</td>
      <td>  NaN</td>
      <td> MQ</td>
      <td> N511MQ</td>
      <td> 3572</td>
      <td> LGA</td>
      <td> CLE</td>
      <td> NaN</td>
      <td>  419</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>336776</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
      <td>  NaN</td>
      <td>  NaN</td>
      <td>  NaN</td>
      <td>  NaN</td>
      <td> MQ</td>
      <td> N839MQ</td>
      <td> 3531</td>
      <td> LGA</td>
      <td> RDU</td>
      <td> NaN</td>
      <td>  431</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>336776 rows × 16 columns</p>
</div>



# Select columns with select(), []


```python
# select(flights, year, month, day) 
flights[['year', 'month', 'day']]
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1     </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  1</td>
    </tr>
    <tr>
      <th>2     </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  1</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>336775</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
    </tr>
    <tr>
      <th>336776</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
    </tr>
  </tbody>
</table>
<p>336776 rows × 3 columns</p>
</div>




```python
# select(flights, year:day) 

# No real equivalent here. Although I think this is OK.
# Typically I'll have the columns I want stored in a list
# somewhere, which can be passed right into __getitem__ ([]).
```


```python
# select(flights, -(year:day)) 

# Again, simliar story. I would just use
# flights.drop(cols_to_drop, axis=1)
# or fligths[flights.columns.difference(pd.Index(cols_to_drop))]
# point to dplyr!
```


```python
# select(flights, tail_num = tailnum)
flights.rename(columns={'tailnum': 'tail_num'})['tail_num']
```




    1    N14228
    ...
    336776    N839MQ
    Name: tail_num, Length: 336776, dtype: object



But like Hadley mentions, not that useful since it only returns the one column. ``dplyr`` and ``pandas`` compare well here.


```python
# rename(flights, tail_num = tailnum)
flights.rename(columns={'tailnum': 'tail_num'})
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tail_num</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1     </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  1</td>
      <td> 517</td>
      <td>  2</td>
      <td> 830</td>
      <td> 11</td>
      <td> UA</td>
      <td> N14228</td>
      <td> 1545</td>
      <td> EWR</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1400</td>
      <td>  5</td>
      <td> 17</td>
    </tr>
    <tr>
      <th>2     </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  1</td>
      <td> 533</td>
      <td>  4</td>
      <td> 850</td>
      <td> 20</td>
      <td> UA</td>
      <td> N24211</td>
      <td> 1714</td>
      <td> LGA</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1416</td>
      <td>  5</td>
      <td> 33</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>336775</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> MQ</td>
      <td> N511MQ</td>
      <td> 3572</td>
      <td> LGA</td>
      <td> CLE</td>
      <td> NaN</td>
      <td>  419</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>336776</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> MQ</td>
      <td> N839MQ</td>
      <td> 3531</td>
      <td> LGA</td>
      <td> RDU</td>
      <td> NaN</td>
      <td>  431</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>336776 rows × 16 columns</p>
</div>



Pandas is more verbose, but the the argument to `columns` can be any mapping. So it's often used with a function to perform a common task, say `df.rename(columns=lambda x: x.replace('-', '_'))` to replace any dashes with underscores. Also, ``rename`` (the pandas version) can be applied to the Index.

# Extract distinct (unique) rows 


```python
# distinct(select(flights, tailnum))
flights.tailnum.unique()
```




    array(['N14228', 'N24211', 'N619AA', ..., 'N776SK', 'N785SK', 'N557AS'], dtype=object)



FYI this returns a numpy array instead of a Series.


```python
# distinct(select(flights, origin, dest))
flights[['origin', 'dest']].drop_duplicates()
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>origin</th>
      <th>dest</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1     </th>
      <td> EWR</td>
      <td> IAH</td>
    </tr>
    <tr>
      <th>2     </th>
      <td> LGA</td>
      <td> IAH</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>255456</th>
      <td> EWR</td>
      <td> ANC</td>
    </tr>
    <tr>
      <th>275946</th>
      <td> EWR</td>
      <td> LGA</td>
    </tr>
  </tbody>
</table>
<p>224 rows × 2 columns</p>
</div>



OK, so ``dplyr`` wins there from a consistency point of view. ``unique`` is only defined on Series, not DataFrames. The original intention for `drop_duplicates` is to check for records that were accidentally included twice. This feels a bit hacky using it to select the distinct combinations, but it works!

# Add new columns with mutate() 


```python
# mutate(flights,
#   gain = arr_delay - dep_delay,
#   speed = distance / air_time * 60)

flights['gain'] = flights.arr_delay - flights.dep_delay
flights['speed'] = flights.distance / flights.air_time * 60
flights
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
      <th>gain</th>
      <th>speed</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1     </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  1</td>
      <td> 517</td>
      <td>  2</td>
      <td> 830</td>
      <td> 11</td>
      <td> UA</td>
      <td> N14228</td>
      <td> 1545</td>
      <td> EWR</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1400</td>
      <td>  5</td>
      <td> 17</td>
      <td>  9</td>
      <td> 370.044053</td>
    </tr>
    <tr>
      <th>2     </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  1</td>
      <td> 533</td>
      <td>  4</td>
      <td> 850</td>
      <td> 20</td>
      <td> UA</td>
      <td> N24211</td>
      <td> 1714</td>
      <td> LGA</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1416</td>
      <td>  5</td>
      <td> 33</td>
      <td> 16</td>
      <td> 374.273128</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>336775</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> MQ</td>
      <td> N511MQ</td>
      <td> 3572</td>
      <td> LGA</td>
      <td> CLE</td>
      <td> NaN</td>
      <td>  419</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>        NaN</td>
    </tr>
    <tr>
      <th>336776</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> MQ</td>
      <td> N839MQ</td>
      <td> 3531</td>
      <td> LGA</td>
      <td> RDU</td>
      <td> NaN</td>
      <td>  431</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>        NaN</td>
    </tr>
  </tbody>
</table>
<p>336776 rows × 18 columns</p>
</div>




```python
# mutate(flights,
#   gain = arr_delay - dep_delay,
#   gain_per_hour = gain / (air_time / 60)
# )

flights['gain'] = flights.arr_delay - flights.dep_delay
flights['gain_per_hour'] = flights.gain / (flights.air_time / 60)
flights
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
      <th>gain</th>
      <th>speed</th>
      <th>gain_per_hour</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1     </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  1</td>
      <td> 517</td>
      <td>  2</td>
      <td> 830</td>
      <td> 11</td>
      <td> UA</td>
      <td> N14228</td>
      <td> 1545</td>
      <td> EWR</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1400</td>
      <td>  5</td>
      <td> 17</td>
      <td>  9</td>
      <td> 370.044053</td>
      <td> 2.378855</td>
    </tr>
    <tr>
      <th>2     </th>
      <td> 2013</td>
      <td> 1</td>
      <td>  1</td>
      <td> 533</td>
      <td>  4</td>
      <td> 850</td>
      <td> 20</td>
      <td> UA</td>
      <td> N24211</td>
      <td> 1714</td>
      <td> LGA</td>
      <td> IAH</td>
      <td> 227</td>
      <td> 1416</td>
      <td>  5</td>
      <td> 33</td>
      <td> 16</td>
      <td> 374.273128</td>
      <td> 4.229075</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>336775</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> MQ</td>
      <td> N511MQ</td>
      <td> 3572</td>
      <td> LGA</td>
      <td> CLE</td>
      <td> NaN</td>
      <td>  419</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>        NaN</td>
      <td>      NaN</td>
    </tr>
    <tr>
      <th>336776</th>
      <td> 2013</td>
      <td> 9</td>
      <td> 30</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> NaN</td>
      <td>NaN</td>
      <td> MQ</td>
      <td> N839MQ</td>
      <td> 3531</td>
      <td> LGA</td>
      <td> RDU</td>
      <td> NaN</td>
      <td>  431</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>        NaN</td>
      <td>      NaN</td>
    </tr>
  </tbody>
</table>
<p>336776 rows × 19 columns</p>
</div>



``dplyr's`` approach may be nicer here since you get to refer to the variables in subsequent statements within the ``mutate()``. To achieve this with pandas, you have to add the `gain` variable as another column in ``flights``. If I don't want it around I would have to explicitly drop it.


```python
# transmute(flights,
#   gain = arr_delay - dep_delay,
#   gain_per_hour = gain / (air_time / 60)
# )

flights['gain'] = flights.arr_delay - flights.dep_delay
flights['gain_per_hour'] = flights.gain / (flights.air_time / 60)
flights[['gain', 'gain_per_hour']]
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>gain</th>
      <th>gain_per_hour</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1     </th>
      <td>  9</td>
      <td> 2.378855</td>
    </tr>
    <tr>
      <th>2     </th>
      <td> 16</td>
      <td> 4.229075</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>336775</th>
      <td>NaN</td>
      <td>      NaN</td>
    </tr>
    <tr>
      <th>336776</th>
      <td>NaN</td>
      <td>      NaN</td>
    </tr>
  </tbody>
</table>
<p>336776 rows × 2 columns</p>
</div>



# Summarise values with summarise()


```python
flights.dep_delay.mean()
```




    12.639070257304708



# Randomly sample rows with sample_n() and sample_frac()

There's an open PR on [Github](https://github.com/pydata/pandas/pull/7274) to make this nicer (closer to ``dplyr``). For now you can drop down to numpy.


```python
# sample_n(flights, 10)
flights.loc[np.random.choice(flights.index, 10)]
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
      <th>gain</th>
      <th>speed</th>
      <th>gain_per_hour</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>316903</th>
      <td> 2013</td>
      <td>  9</td>
      <td>  9</td>
      <td> 1539</td>
      <td>-6</td>
      <td> 1650</td>
      <td>-43</td>
      <td> 9E</td>
      <td> N918XJ</td>
      <td> 3459</td>
      <td> JFK</td>
      <td> BNA</td>
      <td>  98</td>
      <td> 765</td>
      <td> 15</td>
      <td> 39</td>
      <td>-37</td>
      <td> 468.367347</td>
      <td>-22.653061</td>
    </tr>
    <tr>
      <th>105369</th>
      <td> 2013</td>
      <td> 12</td>
      <td> 25</td>
      <td>  905</td>
      <td> 0</td>
      <td> 1126</td>
      <td> -7</td>
      <td> FL</td>
      <td> N939AT</td>
      <td>  275</td>
      <td> LGA</td>
      <td> ATL</td>
      <td> 117</td>
      <td> 762</td>
      <td>  9</td>
      <td>  5</td>
      <td> -7</td>
      <td> 390.769231</td>
      <td> -3.589744</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>82862 </th>
      <td> 2013</td>
      <td> 11</td>
      <td> 30</td>
      <td> 1627</td>
      <td>-8</td>
      <td> 1750</td>
      <td>-35</td>
      <td> AA</td>
      <td> N4XRAA</td>
      <td>  343</td>
      <td> LGA</td>
      <td> ORD</td>
      <td> 111</td>
      <td> 733</td>
      <td> 16</td>
      <td> 27</td>
      <td>-27</td>
      <td> 396.216216</td>
      <td>-14.594595</td>
    </tr>
    <tr>
      <th>190653</th>
      <td> 2013</td>
      <td>  4</td>
      <td> 28</td>
      <td>  748</td>
      <td>-7</td>
      <td>  856</td>
      <td>-24</td>
      <td> MQ</td>
      <td> N520MQ</td>
      <td> 3737</td>
      <td> EWR</td>
      <td> ORD</td>
      <td> 107</td>
      <td> 719</td>
      <td>  7</td>
      <td> 48</td>
      <td>-17</td>
      <td> 403.177570</td>
      <td> -9.532710</td>
    </tr>
  </tbody>
</table>
<p>10 rows × 19 columns</p>
</div>




```python
# sample_frac(flights, 0.01)
flights.iloc[np.random.randint(0, len(flights),
                               .1 * len(flights))]
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th>dep_time</th>
      <th>dep_delay</th>
      <th>arr_time</th>
      <th>arr_delay</th>
      <th>carrier</th>
      <th>tailnum</th>
      <th>flight</th>
      <th>origin</th>
      <th>dest</th>
      <th>air_time</th>
      <th>distance</th>
      <th>hour</th>
      <th>minute</th>
      <th>gain</th>
      <th>speed</th>
      <th>gain_per_hour</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>188581</th>
      <td> 2013</td>
      <td>  4</td>
      <td> 25</td>
      <td> 1836</td>
      <td> -4</td>
      <td> 2145</td>
      <td> 7</td>
      <td> DL</td>
      <td> N398DA</td>
      <td> 1629</td>
      <td> JFK</td>
      <td> LAS</td>
      <td> 313</td>
      <td> 2248</td>
      <td> 18</td>
      <td> 36</td>
      <td> 11</td>
      <td> 430.926518</td>
      <td>  2.108626</td>
    </tr>
    <tr>
      <th>307015</th>
      <td> 2013</td>
      <td>  8</td>
      <td> 29</td>
      <td> 1258</td>
      <td>  5</td>
      <td> 1409</td>
      <td>-4</td>
      <td> EV</td>
      <td> N12957</td>
      <td> 6054</td>
      <td> EWR</td>
      <td> IAD</td>
      <td>  46</td>
      <td>  212</td>
      <td> 12</td>
      <td> 58</td>
      <td> -9</td>
      <td> 276.521739</td>
      <td>-11.739130</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>286563</th>
      <td> 2013</td>
      <td>  8</td>
      <td>  7</td>
      <td> 2126</td>
      <td> 18</td>
      <td>    6</td>
      <td> 7</td>
      <td> UA</td>
      <td> N822UA</td>
      <td>  373</td>
      <td> EWR</td>
      <td> PBI</td>
      <td> 138</td>
      <td> 1023</td>
      <td> 21</td>
      <td> 26</td>
      <td>-11</td>
      <td> 444.782609</td>
      <td> -4.782609</td>
    </tr>
    <tr>
      <th>62818 </th>
      <td> 2013</td>
      <td> 11</td>
      <td>  8</td>
      <td> 1300</td>
      <td>  0</td>
      <td> 1615</td>
      <td> 5</td>
      <td> VX</td>
      <td> N636VA</td>
      <td>  411</td>
      <td> JFK</td>
      <td> LAX</td>
      <td> 349</td>
      <td> 2475</td>
      <td> 13</td>
      <td>  0</td>
      <td>  5</td>
      <td> 425.501433</td>
      <td>  0.859599</td>
    </tr>
  </tbody>
</table>
<p>33677 rows × 19 columns</p>
</div>



# Grouped operations 


```python
# planes <- group_by(flights, tailnum)
# delay <- summarise(planes,
#   count = n(),
#   dist = mean(distance, na.rm = TRUE),
#   delay = mean(arr_delay, na.rm = TRUE))
# delay <- filter(delay, count > 20, dist < 2000)

planes = flights.groupby("tailnum")
delay = planes.agg({"year": "count",
                    "distance": "mean",
                    "arr_delay": "mean"})
delay.query("year > 20 & distance < 2000")
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>year</th>
      <th>arr_delay</th>
      <th>distance</th>
    </tr>
    <tr>
      <th>tailnum</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>N0EGMQ</th>
      <td> 371</td>
      <td>  9.982955</td>
      <td> 676.188679</td>
    </tr>
    <tr>
      <th>N10156</th>
      <td> 153</td>
      <td> 12.717241</td>
      <td> 757.947712</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>N999DN</th>
      <td>  61</td>
      <td> 14.311475</td>
      <td> 895.459016</td>
    </tr>
    <tr>
      <th>N9EAMQ</th>
      <td> 248</td>
      <td>  9.235294</td>
      <td> 674.665323</td>
    </tr>
  </tbody>
</table>
<p>2961 rows × 3 columns</p>
</div>



For me, dplyr's ``n()`` looked is a bit starge at first, but it's already growing on me.

I think pandas is more difficult for this particular example.
There isn't as natural a way to mix column-agnostic aggregations (like ``count``) with column-specific aggregations like the other two. You end up writing could like `.agg{'year': 'count'}` which reads, "I want the count of `year`", even though you don't care about `year` specifically.
Additionally assigning names can't be done as cleanly in pandas; you have to just follow it up with a ``rename`` like before.


```python
# destinations <- group_by(flights, dest)
# summarise(destinations,
#   planes = n_distinct(tailnum),
#   flights = n()
# )

destinations = flights.groupby('dest')
destinations.agg({
    'tailnum': lambda x: len(x.unique()),
    'year': 'count'
    }).rename(columns={'tailnum': 'planes',
                       'year': 'flights'})
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>flights</th>
      <th>planes</th>
    </tr>
    <tr>
      <th>dest</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>ABQ</th>
      <td>  254</td>
      <td> 108</td>
    </tr>
    <tr>
      <th>ACK</th>
      <td>  265</td>
      <td>  58</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>TYS</th>
      <td>  631</td>
      <td> 273</td>
    </tr>
    <tr>
      <th>XNA</th>
      <td> 1036</td>
      <td> 176</td>
    </tr>
  </tbody>
</table>
<p>105 rows × 2 columns</p>
</div>



Similar to how ``dplyr`` provides optimized C++ versions of most of the `summarise` functions, pandas uses [cython](http://cython.org) optimized versions for most of the `agg` methods.


```python
# daily <- group_by(flights, year, month, day)
# (per_day   <- summarise(daily, flights = n()))

daily = flights.groupby(['year', 'month', 'day'])
per_day = daily['distance'].count()
per_day
```




    year  month  day
    2013  1      1      842
    ...
    2013  12     31     776
    Name: distance, Length: 365, dtype: int64




```python
# (per_month <- summarise(per_day, flights = sum(flights)))
per_month = per_day.groupby(level=['year', 'month']).sum()
per_month
```




    year  month
    2013  1        27004
    ...
    2013  12       28135
    Name: distance, Length: 12, dtype: int64




```python
# (per_year  <- summarise(per_month, flights = sum(flights)))
per_year = per_month.sum()
per_year
```




    336776



I'm not sure how ``dplyr`` is handling the other columns, like `year`, in the last example. With pandas, it's clear that we're grouping by them since they're included in the groupby. For the last example, we didn't group by anything, so they aren't included in the result.

# Chaining

Any follower of Hadley's [twitter account](https://twitter.com/hadleywickham/) will know how much R users *love* the ``%>%`` (pipe) operator. And for good reason!


```python
# flights %>%
#   group_by(year, month, day) %>%
#   select(arr_delay, dep_delay) %>%
#   summarise(
#     arr = mean(arr_delay, na.rm = TRUE),
#     dep = mean(dep_delay, na.rm = TRUE)
#   ) %>%
#   filter(arr > 30 | dep > 30)
(
flights.groupby(['year', 'month', 'day'])
    [['arr_delay', 'dep_delay']]
    .mean()
    .query('arr_delay > 30 | dep_delay > 30')
)
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th>arr_delay</th>
      <th>dep_delay</th>
    </tr>
    <tr>
      <th>year</th>
      <th>month</th>
      <th>day</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">2013</th>
      <th rowspan="2" valign="top">1 </th>
      <th>16</th>
      <td> 34.247362</td>
      <td> 24.612865</td>
    </tr>
    <tr>
      <th>31</th>
      <td> 32.602854</td>
      <td> 28.658363</td>
    </tr>
    <tr>
      <th>1 </th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">12</th>
      <th>17</th>
      <td> 55.871856</td>
      <td> 40.705602</td>
    </tr>
    <tr>
      <th>23</th>
      <td> 32.226042</td>
      <td> 32.254149</td>
    </tr>
  </tbody>
</table>
<p>49 rows × 2 columns</p>
</div>



# Other Data Sources

Pandas has tons [IO tools](http://pandas.pydata.org/pandas-docs/version/0.15.0/io.html) to help you get data in and out, including SQL databases via [SQLAlchemy](http://www.sqlalchemy.org).

# Summary

I think pandas held up pretty well, considering this was a vignette written for dplyr. I found the degree of similarity more interesting than the differences. The most difficult task was renaming of columns within an operation; they had to be followed up with a call to ``rename`` *after* the operation, which isn't that burdensome honestly.

More and more it looks like we're moving towards future where being a language or package partisan just doesn't make sense. Not when you can load up a [Jupyter](http://jupyter.org) (formerly IPython) notebook to call up a library written in R, and hand those results off to python or Julia or whatever for followup, before going back to R to make a cool [shiny](http://shiny.rstudio.com) web app.

There will always be a place for your "utility belt" package like dplyr or pandas, but it wouldn't hurt to be familiar with both.

If you want to contribute to pandas, we're always looking for help at https://github.com/pydata/pandas/.
You can get ahold of me directly on [twitter](https://twitter.com/tomaugspurger).

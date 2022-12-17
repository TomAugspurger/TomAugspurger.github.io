---
title: "Modern Panadas (Part 3): Indexes"
date: 2016-04-11
slug: modern-3-indexes
tags:
  - pandas
---

---

This is part 3 in my series on writing modern idiomatic pandas.

- [Modern Pandas](modern-1-intro)
- [Method Chaining](method-chaining)
- [Indexes](modern-3-indexes)
- [Fast Pandas](modern-4-performance)
- [Tidy Data](modern-5-tidy)
- [Visualization](modern-6-visualization)
- [Time Series](modern-7-timeseries)
- [Scaling](modern-8-scaling)

---


`Indexes` can be a difficult concept to grasp at first.
I suspect this is partly becuase they're somewhat peculiar to pandas.
These aren't like the indexes put on relational database tables for performance optimizations.
Rather, they're more like the `row_labels` of an R DataFrame, but much more capable.

`Indexes` offer

- metadata container
- easy label-based row selection
- easy label-based alignment in operations
- label-based concatenation

To demonstrate these, we'll first fetch some more data.
This will be weather data from sensors at a bunch of airports across the US.
See [here](https://github.com/akrherz/iem/blob/master/scripts/asos/iem_scraper_example.py) for the example scraper I based this off of.


```python
%matplotlib inline

import json
import glob
import datetime
from io import StringIO

import requests
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_style('ticks')

# States are broken into networks. The networks have a list of ids, each representing a station.
# We will take that list of ids and pass them as query parameters to the URL we built up ealier.
states = """AK AL AR AZ CA CO CT DE FL GA HI IA ID IL IN KS KY LA MA MD ME
 MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT
 WA WI WV WY""".split()

# IEM has Iowa AWOS sites in its own labeled network
networks = ['AWOS'] + ['{}_ASOS'.format(state) for state in states]
```


```python
def get_weather(stations, start=pd.Timestamp('2014-01-01'),
                end=pd.Timestamp('2014-01-31')):
    '''
    Fetch weather data from MESONet between ``start`` and ``stop``.
    '''
    url = ("http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
           "&data=tmpf&data=relh&data=sped&data=mslp&data=p01i&data=vsby&data=gust_mph&data=skyc1&data=skyc2&data=skyc3"
           "&tz=Etc/UTC&format=comma&latlon=no"
           "&{start:year1=%Y&month1=%m&day1=%d}"
           "&{end:year2=%Y&month2=%m&day2=%d}&{stations}")
    stations = "&".join("station=%s" % s for s in stations)
    weather = (pd.read_csv(url.format(start=start, end=end, stations=stations),
                           comment="#")
                 .rename(columns={"valid": "date"})
                 .rename(columns=str.strip)
                 .assign(date=lambda df: pd.to_datetime(df['date']))
                 .set_index(["station", "date"])
                 .sort_index())
    float_cols = ['tmpf', 'relh', 'sped', 'mslp', 'p01i', 'vsby', "gust_mph"]
    weather[float_cols] = weather[float_cols].apply(pd.to_numeric, errors="corce")
    return weather
```


```python
def get_ids(network):
    url = "http://mesonet.agron.iastate.edu/geojson/network.php?network={}"
    r = requests.get(url.format(network))
    md = pd.io.json.json_normalize(r.json()['features'])
    md['network'] = network
    return md
```

Talk briefly about the gem of a method that is `json_normalize`.


```python
url = "http://mesonet.agron.iastate.edu/geojson/network.php?network={}"
r = requests.get(url.format("AWOS"))
js = r.json()
```


```python
js['features'][:2]
```




    [{'geometry': {'coordinates': [-94.2723694444, 43.0796472222],
       'type': 'Point'},
      'id': 'AXA',
      'properties': {'sid': 'AXA', 'sname': 'ALGONA'},
      'type': 'Feature'},
     {'geometry': {'coordinates': [-93.569475, 41.6878083333], 'type': 'Point'},
      'id': 'IKV',
      'properties': {'sid': 'IKV', 'sname': 'ANKENY'},
      'type': 'Feature'}]




```python
pd.DataFrame(js['features']).head().to_html()
```

<table border="0" class="dataframe">
    <thead>
        <tr style="text-align: right;">
            <th></th>
            <th>geometry</th>
            <th>id</th>
            <th>properties</th>
            <th>type</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <th>0</th>
            <td>{\'coordinates\': [-94.2723694444, 43.0796472222...</td>
            <td>AXA</td>
            <td>{\'sname\': \'ALGONA\', \'sid\': \'AXA\'}</td>
            <td>Feature</td>
        </tr>
        <tr>
            <th>1</th>
            <td>{\'coordinates\': [-93.569475, 41.6878083333], \'...</td>
            <td>IKV</td>
            <td>{\'sname\': \'ANKENY\', \'sid\': \'IKV\'}</td>
            <td>Feature</td>
        </tr>
        <tr>
            <th>2</th>
            <td>{\'coordinates\': [-95.0465277778, 41.4058805556...</td>
            <td>AIO</td>
            <td>{\'sname\': \'ATLANTIC\', \'sid\': \'AIO\'}</td>
            <td>Feature</td>
        </tr>
        <tr>
            <th>3</th>
            <td>{\'coordinates\': [-94.9204416667, 41.6993527778...</td>
            <td>ADU</td>
            <td>{\'sname\': \'AUDUBON\', \'sid\': \'ADU\'}</td>
            <td>Feature</td>
        </tr>
        <tr>
            <th>4</th>
            <td>{\'coordinates\': [-93.848575, 42.0485694444], \'...</td>
            <td>BNW</td>
            <td>{\'sname\': \'BOONE MUNI\', \'sid\': \'BNW\'}</td>
            <td>Feature</td>
        </tr>
    </tbody>
</table>


```python
js['features'][0]
{
    'geometry': {
        'coordinates': [-94.2723694444, 43.0796472222],
        'type': 'Point'
    },
    'id': 'AXA',
    'properties': {
        'sid': 'AXA',
        'sname': 'ALGONA'
    },
    'type': 'Feature'
}
```




```python
js['features']

[{'geometry': {'coordinates': [-94.2723694444, 43.0796472222],
  'type': 'Point'},
  'id': 'AXA',
  'properties': {'sid': 'AXA', 'sname': 'ALGONA'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.569475, 41.6878083333], 'type': 'Point'},
  'id': 'IKV',
  'properties': {'sid': 'IKV', 'sname': 'ANKENY'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.0465277778, 41.4058805556],
  'type': 'Point'},
  'id': 'AIO',
  'properties': {'sid': 'AIO', 'sname': 'ATLANTIC'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-94.9204416667, 41.6993527778],
  'type': 'Point'},
  'id': 'ADU',
  'properties': {'sid': 'ADU', 'sname': 'AUDUBON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.848575, 42.0485694444], 'type': 'Point'},
  'id': 'BNW',
  'properties': {'sid': 'BNW', 'sname': 'BOONE MUNI'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-94.7888805556, 42.0443611111],
  'type': 'Point'},
  'id': 'CIN',
  'properties': {'sid': 'CIN', 'sname': 'CARROLL'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-92.8983388889, 40.6831805556],
  'type': 'Point'},
  'id': 'TVK',
  'properties': {'sid': 'TVK', 'sname': 'Centerville'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.3607694444, 41.0184305556],
  'type': 'Point'},
  'id': 'CNC',
  'properties': {'sid': 'CNC', 'sname': 'CHARITON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-92.6132222222, 43.0730055556],
  'type': 'Point'},
  'id': 'CCY',
  'properties': {'sid': 'CCY', 'sname': 'CHARLES CITY'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.553775, 42.7304194444], 'type': 'Point'},
  'id': 'CKP',
  'properties': {'sid': 'CKP', 'sname': 'Cherokee'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.0222722222, 40.7241527778],
  'type': 'Point'},
  'id': 'ICL',
  'properties': {'sid': 'ICL', 'sname': 'CLARINDA'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.7592583333, 42.7430416667],
  'type': 'Point'},
  'id': 'CAV',
  'properties': {'sid': 'CAV', 'sname': 'CLARION'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-90.332796, 41.829504], 'type': 'Point'},
  'id': 'CWI',
  'properties': {'sid': 'CWI', 'sname': 'CLINTON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.7604083333, 41.2611111111],
  'type': 'Point'},
  'id': 'CBF',
  'properties': {'sid': 'CBF', 'sname': 'COUNCIL BLUFFS'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-94.3607972222, 41.0187888889],
  'type': 'Point'},
  'id': 'CSQ',
  'properties': {'sid': 'CSQ', 'sname': 'CRESTON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.7433138889, 43.2755194444],
  'type': 'Point'},
  'id': 'DEH',
  'properties': {'sid': 'DEH', 'sname': 'DECORAH'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.3799888889, 41.9841944444],
  'type': 'Point'},
  'id': 'DNS',
  'properties': {'sid': 'DNS', 'sname': 'DENISON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.9834111111, 41.0520888889],
  'type': 'Point'},
  'id': 'FFL',
  'properties': {'sid': 'FFL', 'sname': 'FAIRFIELD'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.6236694444, 43.2323166667],
  'type': 'Point'},
  'id': 'FXY',
  'properties': {'sid': 'FXY', 'sname': 'Forest City'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-94.203203, 42.549741], 'type': 'Point'},
  'id': 'FOD',
  'properties': {'sid': 'FOD', 'sname': 'FORT DODGE'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.3267166667, 40.6614833333],
  'type': 'Point'},
  'id': 'FSW',
  'properties': {'sid': 'FSW', 'sname': 'FORT MADISON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-92.7331972222, 41.7097305556],
  'type': 'Point'},
  'id': 'GGI',
  'properties': {'sid': 'GGI', 'sname': 'Grinnell'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.3354555556, 41.5834194444],
  'type': 'Point'},
  'id': 'HNR',
  'properties': {'sid': 'HNR', 'sname': 'HARLAN'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.9504, 42.4544277778], 'type': 'Point'},
  'id': 'IIB',
  'properties': {'sid': 'IIB', 'sname': 'INDEPENDENCE'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.2650805556, 42.4690972222],
  'type': 'Point'},
  'id': 'IFA',
  'properties': {'sid': 'IFA', 'sname': 'Iowa Falls'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.4273916667, 40.4614611111],
  'type': 'Point'},
  'id': 'EOK',
  'properties': {'sid': 'EOK', 'sname': 'KEOKUK MUNI'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.1113916667, 41.2984472222],
  'type': 'Point'},
  'id': 'OXV',
  'properties': {'sid': 'OXV', 'sname': 'Knoxville'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-96.19225, 42.775375], 'type': 'Point'},
  'id': 'LRJ',
  'properties': {'sid': 'LRJ', 'sname': 'LE MARS'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.1604555556, 42.2203611111],
  'type': 'Point'},
  'id': 'MXO',
  'properties': {'sid': 'MXO', 'sname': 'MONTICELLO MUNI'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.5122277778, 40.9452527778],
  'type': 'Point'},
  'id': 'MPZ',
  'properties': {'sid': 'MPZ', 'sname': 'MOUNT PLEASANT'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.140575, 41.3669944444], 'type': 'Point'},
  'id': 'MUT',
  'properties': {'sid': 'MUT', 'sname': 'MUSCATINE'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.0190416667, 41.6701111111],
  'type': 'Point'},
  'id': 'TNU',
  'properties': {'sid': 'TNU', 'sname': 'NEWTON MUNI'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.9759888889, 42.6831388889],
  'type': 'Point'},
  'id': 'OLZ',
  'properties': {'sid': 'OLZ', 'sname': 'OELWEIN'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-96.0605861111, 42.9894916667],
  'type': 'Point'},
  'id': 'ORC',
  'properties': {'sid': 'ORC', 'sname': 'Orange City'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.6876138889, 41.0471722222],
  'type': 'Point'},
  'id': 'I75',
  'properties': {'sid': 'I75', 'sname': 'Osceola'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-92.4918666667, 41.227275], 'type': 'Point'},
  'id': 'OOA',
  'properties': {'sid': 'OOA', 'sname': 'Oskaloosa'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-92.9431083333, 41.3989138889],
  'type': 'Point'},
  'id': 'PEA',
  'properties': {'sid': 'PEA', 'sname': 'PELLA'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-94.1637083333, 41.8277916667],
  'type': 'Point'},
  'id': 'PRO',
  'properties': {'sid': 'PRO', 'sname': 'Perry'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.2624111111, 41.01065], 'type': 'Point'},
  'id': 'RDK',
  'properties': {'sid': 'RDK', 'sname': 'RED OAK'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.8353138889, 43.2081611111],
  'type': 'Point'},
  'id': 'SHL',
  'properties': {'sid': 'SHL', 'sname': 'SHELDON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.4112333333, 40.753275], 'type': 'Point'},
  'id': 'SDA',
  'properties': {'sid': 'SDA', 'sname': 'SHENANDOAH MUNI'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-95.2399194444, 42.5972277778],
  'type': 'Point'},
  'id': 'SLB',
  'properties': {'sid': 'SLB', 'sname': 'Storm Lake'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-92.0248416667, 42.2175777778],
  'type': 'Point'},
  'id': 'VTI',
  'properties': {'sid': 'VTI', 'sname': 'VINTON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-91.6748111111, 41.2751444444],
  'type': 'Point'},
  'id': 'AWG',
  'properties': {'sid': 'AWG', 'sname': 'WASHINGTON'},
  'type': 'Feature'},
{'geometry': {'coordinates': [-93.8690777778, 42.4392305556],
  'type': 'Point'},
  'id': 'EBS',
  'properties': {'sid': 'EBS', 'sname': 'Webster City'},
  'type': 'Feature'}]

```


```python
stations = pd.io.json.json_normalize(js['features']).id
url = ("http://mesonet.agron.iastate.edu/cgi-bin/request/asos.py?"
       "&data=tmpf&data=relh&data=sped&data=mslp&data=p01i&data=vsby&data=gust_mph&data=skyc1&data=skyc2&data=skyc3"
       "&tz=Etc/UTC&format=comma&latlon=no"
       "&{start:year1=%Y&month1=%m&day1=%d}"
       "&{end:year2=%Y&month2=%m&day2=%d}&{stations}")
stations = "&".join("station=%s" % s for s in stations)
start = pd.Timestamp('2014-01-01')
end=pd.Timestamp('2014-01-31')

weather = (pd.read_csv(url.format(start=start, end=end, stations=stations),
                       comment="#"))
```



```python
import os
ids = pd.concat([get_ids(network) for network in networks], ignore_index=True)
gr = ids.groupby('network')

os.makedirs("weather", exist_ok=True)

for i, (k, v) in enumerate(gr):
    print("{}/{}".format(i, len(network)), end='\r')
    weather = get_weather(v['id'])
    weather.to_csv("weather/{}.csv".format(k))

weather = pd.concat([
    pd.read_csv(f, parse_dates='date', index_col=['station', 'date'])
    for f in glob.glob('weather/*.csv')])

weather.to_hdf("weather.h5", "weather")
```


```python
weather = pd.read_hdf("weather.h5", "weather").sort_index()

weather.head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>tmpf</th>
      <th>relh</th>
      <th>sped</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>vsby</th>
      <th>gust_mph</th>
      <th>skyc1</th>
      <th>skyc2</th>
      <th>skyc3</th>
    </tr>
    <tr>
      <th>station</th>
      <th>date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">01M</th>
      <th>2014-01-01 00:15:00</th>
      <td>33.80</td>
      <td>85.86</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 00:35:00</th>
      <td>33.44</td>
      <td>87.11</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 00:55:00</th>
      <td>32.54</td>
      <td>90.97</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 01:15:00</th>
      <td>31.82</td>
      <td>93.65</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 01:35:00</th>
      <td>32.00</td>
      <td>92.97</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
  </tbody>
</table>
</div>



OK, that was a bit of work. Here's a plot to reward ourselves.


```python
airports = ['DSM', 'ORD', 'JFK', 'PDX']

g = sns.FacetGrid(weather.sort_index().loc[airports].reset_index(),
                  col='station', hue='station', col_wrap=2, size=4)
g.map(sns.regplot, 'sped', 'gust_mph')
plt.savefig('../content/images/indexes_wind_gust_facet.png');
```


```python
airports = ['DSM', 'ORD', 'JFK', 'PDX']

g = sns.FacetGrid(weather.sort_index().loc[airports].reset_index(),
                  col='station', hue='station', col_wrap=2, size=4)
g.map(sns.regplot, 'sped', 'gust_mph')
plt.savefig('../content/images/indexes_wind_gust_facet.svg', transparent=True);
```


![png](Indexes_files/Indexes_18_0.png)


# Set Operations

Indexes are set-like (technically *multi*sets, since you can have duplicates), so they support most python `set` operations. Indexes are immutable so you won't find any of the inplace `set` operations.
One other difference is that since `Index`es are also array like, you can't use some infix operators like `-` for `difference`. If you have a numeric index it is unclear whether you intend to perform math operations or set operations.
You can use `&` for intersetion, `|` for union, and `^` for symmetric difference though, since there's no ambiguity.

For example, lets find the set of airports that we have weather and flight information on. Since `weather` had a MultiIndex of `airport,datetime`, we'll use the `levels` attribute to get at the airport data, separate from the date data.


```python
# Bring in the flights data

flights = pd.read_hdf('flights.h5', 'flights')

weather_locs = weather.index.levels[0]
# The `categories` attribute of a Categorical is an Index
origin_locs = flights.origin.cat.categories
dest_locs = flights.dest.cat.categories

airports = weather_locs & origin_locs & dest_locs
airports
```




    Index(['ABE', 'ABI', 'ABQ', 'ABR', 'ABY', 'ACT', 'ACV', 'AEX', 'AGS', 'ALB',
           ...
           'TUL', 'TUS', 'TVC', 'TWF', 'TXK', 'TYR', 'TYS', 'VLD', 'VPS', 'XNA'],
          dtype='object', length=267)




```python
print("Weather, no flights:\n\t", weather_locs.difference(origin_locs | dest_locs), end='\n\n')

print("Flights, no weather:\n\t", (origin_locs | dest_locs).difference(weather_locs), end='\n\n')

print("Dropped Stations:\n\t", (origin_locs | dest_locs) ^ weather_locs)
```

    Weather, no flights:
    	 Index(['01M', '04V', '04W', '05U', '06D', '08D', '0A9', '0CO', '0E0', '0F2',
           ...
           'Y50', 'Y51', 'Y63', 'Y70', 'YIP', 'YKM', 'YKN', 'YNG', 'ZPH', 'ZZV'],
          dtype='object', length=1909)
    
    Flights, no weather:
    	 Index(['ADK', 'ADQ', 'ANC', 'BET', 'BKG', 'BQN', 'BRW', 'CDV', 'CLD', 'FAI',
           'FCA', 'GUM', 'HNL', 'ITO', 'JNU', 'KOA', 'KTN', 'LIH', 'MQT', 'OGG',
           'OME', 'OTZ', 'PPG', 'PSE', 'PSG', 'SCC', 'SCE', 'SIT', 'SJU', 'STT',
           'STX', 'WRG', 'YAK', 'YUM'],
          dtype='object')
    
    Dropped Stations:
    	 Index(['01M', '04V', '04W', '05U', '06D', '08D', '0A9', '0CO', '0E0', '0F2',
           ...
           'Y63', 'Y70', 'YAK', 'YIP', 'YKM', 'YKN', 'YNG', 'YUM', 'ZPH', 'ZZV'],
          dtype='object', length=1943)


# Flavors

Pandas has many subclasses of the regular `Index`, each tailored to a specific kind of data.
Most of the time these will be created for you automatically, so you don't have to worry about which one to choose.

1. [`Index`](http://pandas.pydata.org/pandas-docs/version/0.18.0/generated/pandas.Index.html#pandas.Index)
2. `Int64Index`
3. `RangeIndex` (Memory-saving special case of `Int64Index`)
4. `FloatIndex`
5. `DatetimeIndex`: Datetime64[ns] precision data
6. `PeriodIndex`: Regularly-spaced, arbitrary precision datetime data.
7. `TimedeltaIndex`: Timedelta data
8. `CategoricalIndex`:

Some of these are purely optimizations, others use information about the data to provide additional methods.
And while sometimes you might work with indexes directly (like the set operations above), most of they time you'll be operating on a Series or DataFrame, which in turn makes use of its Index.

### Row Slicing
We saw in part one that they're great for making *row* subsetting as easy as column subsetting.


```python
weather.loc['DSM'].head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tmpf</th>
      <th>relh</th>
      <th>sped</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>vsby</th>
      <th>gust_mph</th>
      <th>skyc1</th>
      <th>skyc2</th>
      <th>skyc3</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2014-01-01 00:54:00</th>
      <td>10.94</td>
      <td>72.79</td>
      <td>10.3</td>
      <td>1024.9</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>FEW</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 01:54:00</th>
      <td>10.94</td>
      <td>72.79</td>
      <td>11.4</td>
      <td>1025.4</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>OVC</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 02:54:00</th>
      <td>10.94</td>
      <td>72.79</td>
      <td>8.0</td>
      <td>1025.3</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>BKN</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 03:54:00</th>
      <td>10.94</td>
      <td>72.79</td>
      <td>9.1</td>
      <td>1025.3</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>OVC</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 04:54:00</th>
      <td>10.04</td>
      <td>72.69</td>
      <td>9.1</td>
      <td>1024.7</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>BKN</td>
      <td>M</td>
      <td>M</td>
    </tr>
  </tbody>
</table>
</div>



Without indexes we'd probably resort to boolean masks.


```python
weather2 = weather.reset_index()
weather2[weather2['station'] == 'DSM'].head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>station</th>
      <th>date</th>
      <th>tmpf</th>
      <th>relh</th>
      <th>sped</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>vsby</th>
      <th>gust_mph</th>
      <th>skyc1</th>
      <th>skyc2</th>
      <th>skyc3</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>884855</th>
      <td>DSM</td>
      <td>2014-01-01 00:54:00</td>
      <td>10.94</td>
      <td>72.79</td>
      <td>10.3</td>
      <td>1024.9</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>FEW</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>884856</th>
      <td>DSM</td>
      <td>2014-01-01 01:54:00</td>
      <td>10.94</td>
      <td>72.79</td>
      <td>11.4</td>
      <td>1025.4</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>OVC</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>884857</th>
      <td>DSM</td>
      <td>2014-01-01 02:54:00</td>
      <td>10.94</td>
      <td>72.79</td>
      <td>8.0</td>
      <td>1025.3</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>BKN</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>884858</th>
      <td>DSM</td>
      <td>2014-01-01 03:54:00</td>
      <td>10.94</td>
      <td>72.79</td>
      <td>9.1</td>
      <td>1025.3</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>OVC</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>884859</th>
      <td>DSM</td>
      <td>2014-01-01 04:54:00</td>
      <td>10.04</td>
      <td>72.69</td>
      <td>9.1</td>
      <td>1024.7</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>BKN</td>
      <td>M</td>
      <td>M</td>
    </tr>
  </tbody>
</table>
</div>



Slightly less convenient, but still doable.

### Indexes for Easier Arithmetic, Analysis

It's nice to have your metadata (labels on each observation) next to you actual values. But if you store them in an array, they'll get in the way. Say we wanted to translate the farenheit temperature to celcius.


```python
# With indecies
temp = weather['tmpf']

c = (temp - 32) * 5 / 9
c.to_frame()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>tmpf</th>
    </tr>
    <tr>
      <th>station</th>
      <th>date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">01M</th>
      <th>2014-01-01 00:15:00</th>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2014-01-01 00:35:00</th>
      <td>0.8</td>
    </tr>
    <tr>
      <th>2014-01-01 00:55:00</th>
      <td>0.3</td>
    </tr>
    <tr>
      <th>2014-01-01 01:15:00</th>
      <td>-0.1</td>
    </tr>
    <tr>
      <th>2014-01-01 01:35:00</th>
      <td>0.0</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">ZZV</th>
      <th>2014-01-30 19:53:00</th>
      <td>-2.8</td>
    </tr>
    <tr>
      <th>2014-01-30 20:53:00</th>
      <td>-2.2</td>
    </tr>
    <tr>
      <th>2014-01-30 21:53:00</th>
      <td>-2.2</td>
    </tr>
    <tr>
      <th>2014-01-30 22:53:00</th>
      <td>-2.8</td>
    </tr>
    <tr>
      <th>2014-01-30 23:53:00</th>
      <td>-1.7</td>
    </tr>
  </tbody>
</table>
<p>3303647 rows × 1 columns</p>
</div>




```python
# without
temp2 = weather.reset_index()[['station', 'date', 'tmpf']]

temp2['tmpf'] = (temp2['tmpf'] - 32) * 5 / 9
temp2.head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>station</th>
      <th>date</th>
      <th>tmpf</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>01M</td>
      <td>2014-01-01 00:15:00</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>01M</td>
      <td>2014-01-01 00:35:00</td>
      <td>0.8</td>
    </tr>
    <tr>
      <th>2</th>
      <td>01M</td>
      <td>2014-01-01 00:55:00</td>
      <td>0.3</td>
    </tr>
    <tr>
      <th>3</th>
      <td>01M</td>
      <td>2014-01-01 01:15:00</td>
      <td>-0.1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>01M</td>
      <td>2014-01-01 01:35:00</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>



Again, not terrible, but not as good.
And, what if you had wanted to keep farenheit around as well, instead of overwriting it like we did?
Then you'd need to make a copy of everything, including the `station` and `date` columns.
We don't have that problem, since indexes are mutable and safely shared between DataFrames / Series.


```python
temp.index is c.index
```




    True



### Indexes for Alignment

I've saved the best for last.
Automatic alignment, or reindexing, is fundamental to pandas.

All binary operations (add, multiply, etc...) between Series/DataFrames first *align* and then proceed.

Let's suppose we have hourly observations on temperature and windspeed.
And suppose some of the observations were invalid, and not reported (simulated below by sampling from the full dataset). We'll assume the missing windspeed observations were potentially different from the missing temperature observations.


```python
dsm = weather.loc['DSM']

hourly = dsm.resample('H').mean()

temp = hourly['tmpf'].sample(frac=.5, random_state=1).sort_index()
sped = hourly['sped'].sample(frac=.5, random_state=2).sort_index()
```


```python
temp.head().to_frame()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tmpf</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2014-01-01 00:00:00</th>
      <td>10.94</td>
    </tr>
    <tr>
      <th>2014-01-01 02:00:00</th>
      <td>10.94</td>
    </tr>
    <tr>
      <th>2014-01-01 03:00:00</th>
      <td>10.94</td>
    </tr>
    <tr>
      <th>2014-01-01 04:00:00</th>
      <td>10.04</td>
    </tr>
    <tr>
      <th>2014-01-01 05:00:00</th>
      <td>10.04</td>
    </tr>
  </tbody>
</table>
</div>




```python
sped.head()
```




    date
    2014-01-01 01:00:00    11.4
    2014-01-01 02:00:00     8.0
    2014-01-01 03:00:00     9.1
    2014-01-01 04:00:00     9.1
    2014-01-01 05:00:00    10.3
    Name: sped, dtype: float64



Notice that the two indexes aren't identical.

Suppose that the `windspeed : temperature` ratio is meaningful.
When we go to compute that, pandas will automatically align the two by index label.


```python
sped / temp
```




    date
    2014-01-01 00:00:00         NaN
    2014-01-01 01:00:00         NaN
    2014-01-01 02:00:00    0.731261
    2014-01-01 03:00:00    0.831810
    2014-01-01 04:00:00    0.906375
                             ...   
    2014-01-30 13:00:00         NaN
    2014-01-30 14:00:00    0.584712
    2014-01-30 17:00:00         NaN
    2014-01-30 21:00:00         NaN
    2014-01-30 23:00:00         NaN
    dtype: float64



This lets you focus on doing the operation, rather than manually aligning things, ensuring that the arrays are the same length and in the same order.
By deault, missing values are inserted where the two don't align.
You can use the method version of any binary operation to specify a `fill_value`


```python
sped.div(temp, fill_value=1)
```




    date
    2014-01-01 00:00:00     0.091408
    2014-01-01 01:00:00    11.400000
    2014-01-01 02:00:00     0.731261
    2014-01-01 03:00:00     0.831810
    2014-01-01 04:00:00     0.906375
                             ...    
    2014-01-30 13:00:00     0.027809
    2014-01-30 14:00:00     0.584712
    2014-01-30 17:00:00     0.023267
    2014-01-30 21:00:00     0.035663
    2014-01-30 23:00:00    13.700000
    dtype: float64



And since I couldn't find anywhere else to put it, you can control the axis the operation is aligned along as well.


```python
hourly.div(sped, axis='index')
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tmpf</th>
      <th>relh</th>
      <th>sped</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>vsby</th>
      <th>gust_mph</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2014-01-01 00:00:00</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 01:00:00</th>
      <td>0.959649</td>
      <td>6.385088</td>
      <td>1.0</td>
      <td>89.947368</td>
      <td>0.0</td>
      <td>0.877193</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 02:00:00</th>
      <td>1.367500</td>
      <td>9.098750</td>
      <td>1.0</td>
      <td>128.162500</td>
      <td>0.0</td>
      <td>1.250000</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 03:00:00</th>
      <td>1.202198</td>
      <td>7.998901</td>
      <td>1.0</td>
      <td>112.670330</td>
      <td>0.0</td>
      <td>1.098901</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 04:00:00</th>
      <td>1.103297</td>
      <td>7.987912</td>
      <td>1.0</td>
      <td>112.604396</td>
      <td>0.0</td>
      <td>1.098901</td>
      <td>NaN</td>
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
    </tr>
    <tr>
      <th>2014-01-30 19:00:00</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-30 20:00:00</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-30 21:00:00</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-30 22:00:00</th>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-30 23:00:00</th>
      <td>1.600000</td>
      <td>4.535036</td>
      <td>1.0</td>
      <td>73.970803</td>
      <td>0.0</td>
      <td>0.729927</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>720 rows × 7 columns</p>
</div>



The non row-labeled version of this is messy.


```python
temp2 = temp.reset_index()
sped2 = sped.reset_index()

# Find rows where the operation is defined
common_dates = pd.Index(temp2.date) & sped2.date
pd.concat([
    # concat to not lose date information
    sped2.loc[sped2['date'].isin(common_dates), 'date'],
    (sped2.loc[sped2.date.isin(common_dates), 'sped'] /
     temp2.loc[temp2.date.isin(common_dates), 'tmpf'])],
    axis=1).dropna(how='all')
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>date</th>
      <th>0</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>1</th>
      <td>2014-01-01 02:00:00</td>
      <td>0.731261</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2014-01-01 03:00:00</td>
      <td>0.831810</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2014-01-01 04:00:00</td>
      <td>0.906375</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2014-01-01 05:00:00</td>
      <td>1.025896</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2014-01-01 13:00:00</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>351</th>
      <td>2014-01-29 23:00:00</td>
      <td>0.535609</td>
    </tr>
    <tr>
      <th>354</th>
      <td>2014-01-30 05:00:00</td>
      <td>0.487735</td>
    </tr>
    <tr>
      <th>356</th>
      <td>2014-01-30 09:00:00</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>357</th>
      <td>2014-01-30 10:00:00</td>
      <td>0.618939</td>
    </tr>
    <tr>
      <th>358</th>
      <td>2014-01-30 14:00:00</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>170 rows × 2 columns</p>
</div>



Yeah, I prefer the `temp / sped` version.

Alignment isn't limited to arithmetic operations, although those are the most obvious and easiest to demonstrate.

# Merging

There are two ways of merging DataFrames / Series in pandas

1. Relational Database style with `pd.merge`
2. Array style with `pd.concat`

Personally, I think in terms of the `concat` style.
I learned pandas before I ever really used SQL, so it comes more naturally to me I suppose.
`pd.merge` has more flexibilty, though I think *most* of the time you don't need this flexibilty.

### Concat Version


```python
pd.concat([temp, sped], axis=1).head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tmpf</th>
      <th>sped</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2014-01-01 00:00:00</th>
      <td>10.94</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 01:00:00</th>
      <td>NaN</td>
      <td>11.4</td>
    </tr>
    <tr>
      <th>2014-01-01 02:00:00</th>
      <td>10.94</td>
      <td>8.0</td>
    </tr>
    <tr>
      <th>2014-01-01 03:00:00</th>
      <td>10.94</td>
      <td>9.1</td>
    </tr>
    <tr>
      <th>2014-01-01 04:00:00</th>
      <td>10.04</td>
      <td>9.1</td>
    </tr>
  </tbody>
</table>
</div>



The `axis` parameter controls how the data should be stacked, `0` for vertically, `1` for horizontally.
The `join` parameter controls the merge behavior on the shared axis, (the Index for `axis=1`). By default it's like a union of the two indexes, or an outer join.


```python
pd.concat([temp, sped], axis=1, join='inner')
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tmpf</th>
      <th>sped</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2014-01-01 02:00:00</th>
      <td>10.94</td>
      <td>8.000</td>
    </tr>
    <tr>
      <th>2014-01-01 03:00:00</th>
      <td>10.94</td>
      <td>9.100</td>
    </tr>
    <tr>
      <th>2014-01-01 04:00:00</th>
      <td>10.04</td>
      <td>9.100</td>
    </tr>
    <tr>
      <th>2014-01-01 05:00:00</th>
      <td>10.04</td>
      <td>10.300</td>
    </tr>
    <tr>
      <th>2014-01-01 13:00:00</th>
      <td>8.96</td>
      <td>13.675</td>
    </tr>
    <tr>
      <th>...</th>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>2014-01-29 23:00:00</th>
      <td>35.96</td>
      <td>18.200</td>
    </tr>
    <tr>
      <th>2014-01-30 05:00:00</th>
      <td>33.98</td>
      <td>17.100</td>
    </tr>
    <tr>
      <th>2014-01-30 09:00:00</th>
      <td>35.06</td>
      <td>16.000</td>
    </tr>
    <tr>
      <th>2014-01-30 10:00:00</th>
      <td>35.06</td>
      <td>21.700</td>
    </tr>
    <tr>
      <th>2014-01-30 14:00:00</th>
      <td>35.06</td>
      <td>20.500</td>
    </tr>
  </tbody>
</table>
<p>170 rows × 2 columns</p>
</div>



### Merge Version

Since we're joining by index here the merge version is quite similar.
We'll see an example later of a one-to-many join where the two differ.


```python
pd.merge(temp.to_frame(), sped.to_frame(), left_index=True, right_index=True).head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tmpf</th>
      <th>sped</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2014-01-01 02:00:00</th>
      <td>10.94</td>
      <td>8.000</td>
    </tr>
    <tr>
      <th>2014-01-01 03:00:00</th>
      <td>10.94</td>
      <td>9.100</td>
    </tr>
    <tr>
      <th>2014-01-01 04:00:00</th>
      <td>10.04</td>
      <td>9.100</td>
    </tr>
    <tr>
      <th>2014-01-01 05:00:00</th>
      <td>10.04</td>
      <td>10.300</td>
    </tr>
    <tr>
      <th>2014-01-01 13:00:00</th>
      <td>8.96</td>
      <td>13.675</td>
    </tr>
  </tbody>
</table>
</div>




```python
pd.merge(temp.to_frame(), sped.to_frame(), left_index=True, right_index=True,
         how='outer').head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tmpf</th>
      <th>sped</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2014-01-01 00:00:00</th>
      <td>10.94</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 01:00:00</th>
      <td>NaN</td>
      <td>11.4</td>
    </tr>
    <tr>
      <th>2014-01-01 02:00:00</th>
      <td>10.94</td>
      <td>8.0</td>
    </tr>
    <tr>
      <th>2014-01-01 03:00:00</th>
      <td>10.94</td>
      <td>9.1</td>
    </tr>
    <tr>
      <th>2014-01-01 04:00:00</th>
      <td>10.04</td>
      <td>9.1</td>
    </tr>
  </tbody>
</table>
</div>



Like I said, I typically prefer `concat` to `merge`.
The exception here is one-to-many type joins. Let's walk through one of those,
where we join the flight data to the weather data.
To focus just on the merge, we'll aggregate hour weather data to be daily, rather than trying to find the closest recorded weather observation to each departure (you could do that, but it's not the focus right now). We'll then join the one `(airport, date)` record to the many `(airport, date, flight)` records.

Quick tangent, to get the weather data to daily frequency, we'll need to resample (more on that in the timeseries section). The resample essentially involves breaking the recorded values into daily buckets and computing the aggregation function on each bucket. The only wrinkle is that we have to resample *by station*, so we'll use the `pd.TimeGrouper` helper.


```python
idx_cols = ['unique_carrier', 'origin', 'dest', 'tail_num', 'fl_num', 'fl_date']
data_cols = ['crs_dep_time', 'dep_delay', 'crs_arr_time', 'arr_delay',
             'taxi_out', 'taxi_in', 'wheels_off', 'wheels_on', 'distance']

df = flights.set_index(idx_cols)[data_cols].sort_index()
```


```python
def mode(x):
    '''
    Arbitrarily break ties.
    '''
    return x.value_counts().index[0]

aggfuncs = {'tmpf': 'mean', 'relh': 'mean',
            'sped': 'mean', 'mslp': 'mean',
            'p01i': 'mean', 'vsby': 'mean',
            'gust_mph': 'mean', 'skyc1': mode,
            'skyc2': mode, 'skyc3': mode}
# TimeGrouper works on a DatetimeIndex, so we move `station` to the
# columns and then groupby it as well.
daily = (weather.reset_index(level="station")
                .groupby([pd.TimeGrouper('1d'), "station"])
                .agg(aggfuncs))

daily.head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>gust_mph</th>
      <th>vsby</th>
      <th>sped</th>
      <th>relh</th>
      <th>skyc1</th>
      <th>tmpf</th>
      <th>skyc2</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>skyc3</th>
    </tr>
    <tr>
      <th>date</th>
      <th>station</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">2014-01-01</th>
      <th>01M</th>
      <td>NaN</td>
      <td>9.229167</td>
      <td>2.262500</td>
      <td>81.117917</td>
      <td>CLR</td>
      <td>35.747500</td>
      <td>M</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
    <tr>
      <th>04V</th>
      <td>31.307143</td>
      <td>9.861111</td>
      <td>11.131944</td>
      <td>72.697778</td>
      <td>CLR</td>
      <td>18.350000</td>
      <td>M</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
    <tr>
      <th>04W</th>
      <td>NaN</td>
      <td>10.000000</td>
      <td>3.601389</td>
      <td>69.908056</td>
      <td>OVC</td>
      <td>-9.075000</td>
      <td>M</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
    <tr>
      <th>05U</th>
      <td>NaN</td>
      <td>9.929577</td>
      <td>3.770423</td>
      <td>71.519859</td>
      <td>CLR</td>
      <td>26.321127</td>
      <td>M</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
    <tr>
      <th>06D</th>
      <td>NaN</td>
      <td>9.576389</td>
      <td>5.279167</td>
      <td>73.784179</td>
      <td>CLR</td>
      <td>-11.388060</td>
      <td>M</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
  </tbody>
</table>
</div>



### The merge version


```python
m = pd.merge(flights, daily.reset_index().rename(columns={'date': 'fl_date', 'station': 'origin'}),
             on=['fl_date', 'origin']).set_index(idx_cols).sort_index()

m.head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th>airline_id</th>
      <th>origin_airport_id</th>
      <th>origin_airport_seq_id</th>
      <th>origin_city_market_id</th>
      <th>origin_city_name</th>
      <th>origin_state_nm</th>
      <th>dest_airport_id</th>
      <th>dest_airport_seq_id</th>
      <th>dest_city_market_id</th>
      <th>dest_city_name</th>
      <th>...</th>
      <th>gust_mph</th>
      <th>vsby</th>
      <th>sped</th>
      <th>relh</th>
      <th>skyc1</th>
      <th>tmpf</th>
      <th>skyc2</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>skyc3</th>
    </tr>
    <tr>
      <th>unique_carrier</th>
      <th>origin</th>
      <th>dest</th>
      <th>tail_num</th>
      <th>fl_num</th>
      <th>fl_date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">AA</th>
      <th rowspan="5" valign="top">ABQ</th>
      <th rowspan="5" valign="top">DFW</th>
      <th rowspan="2" valign="top">N200AA</th>
      <th>1090</th>
      <th>2014-01-27</th>
      <td>19805</td>
      <td>10140</td>
      <td>1014002</td>
      <td>30140</td>
      <td>Albuquerque, NM</td>
      <td>New Mexico</td>
      <td>11298</td>
      <td>1129803</td>
      <td>30194</td>
      <td>Dallas/Fort Worth, TX</td>
      <td>...</td>
      <td>NaN</td>
      <td>10.0</td>
      <td>6.737500</td>
      <td>34.267500</td>
      <td>SCT</td>
      <td>41.8325</td>
      <td>M</td>
      <td>1014.620833</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
    <tr>
      <th>1662</th>
      <th>2014-01-06</th>
      <td>19805</td>
      <td>10140</td>
      <td>1014002</td>
      <td>30140</td>
      <td>Albuquerque, NM</td>
      <td>New Mexico</td>
      <td>11298</td>
      <td>1129803</td>
      <td>30194</td>
      <td>Dallas/Fort Worth, TX</td>
      <td>...</td>
      <td>NaN</td>
      <td>10.0</td>
      <td>9.270833</td>
      <td>27.249167</td>
      <td>CLR</td>
      <td>28.7900</td>
      <td>M</td>
      <td>1029.016667</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
    <tr>
      <th>N202AA</th>
      <th>1332</th>
      <th>2014-01-27</th>
      <td>19805</td>
      <td>10140</td>
      <td>1014002</td>
      <td>30140</td>
      <td>Albuquerque, NM</td>
      <td>New Mexico</td>
      <td>11298</td>
      <td>1129803</td>
      <td>30194</td>
      <td>Dallas/Fort Worth, TX</td>
      <td>...</td>
      <td>NaN</td>
      <td>10.0</td>
      <td>6.737500</td>
      <td>34.267500</td>
      <td>SCT</td>
      <td>41.8325</td>
      <td>M</td>
      <td>1014.620833</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
    <tr>
      <th rowspan="2" valign="top">N426AA</th>
      <th>1467</th>
      <th>2014-01-15</th>
      <td>19805</td>
      <td>10140</td>
      <td>1014002</td>
      <td>30140</td>
      <td>Albuquerque, NM</td>
      <td>New Mexico</td>
      <td>11298</td>
      <td>1129803</td>
      <td>30194</td>
      <td>Dallas/Fort Worth, TX</td>
      <td>...</td>
      <td>NaN</td>
      <td>10.0</td>
      <td>6.216667</td>
      <td>34.580000</td>
      <td>FEW</td>
      <td>40.2500</td>
      <td>M</td>
      <td>1027.800000</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
    <tr>
      <th>1662</th>
      <th>2014-01-09</th>
      <td>19805</td>
      <td>10140</td>
      <td>1014002</td>
      <td>30140</td>
      <td>Albuquerque, NM</td>
      <td>New Mexico</td>
      <td>11298</td>
      <td>1129803</td>
      <td>30194</td>
      <td>Dallas/Fort Worth, TX</td>
      <td>...</td>
      <td>NaN</td>
      <td>10.0</td>
      <td>3.087500</td>
      <td>42.162500</td>
      <td>FEW</td>
      <td>34.6700</td>
      <td>M</td>
      <td>1018.379167</td>
      <td>0.0</td>
      <td>M</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 40 columns</p>
</div>




```python
m.sample(n=10000).pipe((sns.jointplot, 'data'), 'sped', 'dep_delay')
plt.savefig('../content/images/indexes_sped_delay_join.svg', transparent=True)
```


![png](Indexes_files/Indexes_63_0.png)



```python
m.groupby('skyc1').dep_delay.agg(['mean', 'count']).sort_values(by='mean')
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>mean</th>
      <th>count</th>
    </tr>
    <tr>
      <th>skyc1</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>M</th>
      <td>-1.948052</td>
      <td>77</td>
    </tr>
    <tr>
      <th>CLR</th>
      <td>11.222288</td>
      <td>115121</td>
    </tr>
    <tr>
      <th>FEW</th>
      <td>16.863177</td>
      <td>161727</td>
    </tr>
    <tr>
      <th>SCT</th>
      <td>17.803048</td>
      <td>19289</td>
    </tr>
    <tr>
      <th>BKN</th>
      <td>18.638034</td>
      <td>54030</td>
    </tr>
    <tr>
      <th>OVC</th>
      <td>21.667762</td>
      <td>52643</td>
    </tr>
    <tr>
      <th>VV</th>
      <td>30.487008</td>
      <td>9583</td>
    </tr>
  </tbody>
</table>
</div>




```python
import statsmodels.api as sm
```


```python
mod = sm.OLS.from_formula('dep_delay ~ C(skyc1) + distance + tmpf + relh + sped + mslp', data=m)
res = mod.fit()
res.summary()
```




<table class="simpletable">
<caption>OLS Regression Results</caption>
<tr>
  <th>Dep. Variable:</th>        <td>dep_delay</td>    <th>  R-squared:         </th>  <td>   0.026</td>  
</tr>
<tr>
  <th>Model:</th>                   <td>OLS</td>       <th>  Adj. R-squared:    </th>  <td>   0.025</td>  
</tr>
<tr>
  <th>Method:</th>             <td>Least Squares</td>  <th>  F-statistic:       </th>  <td>   976.4</td>  
</tr>
<tr>
  <th>Date:</th>             <td>Sun, 10 Apr 2016</td> <th>  Prob (F-statistic):</th>   <td>  0.00</td>   
</tr>
<tr>
  <th>Time:</th>                 <td>16:06:15</td>     <th>  Log-Likelihood:    </th> <td>-2.1453e+06</td>
</tr>
<tr>
  <th>No. Observations:</th>      <td>410372</td>      <th>  AIC:               </th>  <td>4.291e+06</td> 
</tr>
<tr>
  <th>Df Residuals:</th>          <td>410360</td>      <th>  BIC:               </th>  <td>4.291e+06</td> 
</tr>
<tr>
  <th>Df Model:</th>              <td>    11</td>      <th>                     </th>      <td> </td>     
</tr>
<tr>
  <th>Covariance Type:</th>      <td>nonrobust</td>    <th>                     </th>      <td> </td>     
</tr>
</table>
<table class="simpletable">
<tr>
         <td></td>            <th>coef</th>     <th>std err</th>      <th>t</th>      <th>P>|t|</th> <th>[95.0% Conf. Int.]</th> 
</tr>
<tr>
  <th>Intercept</th>       <td> -331.1032</td> <td>   10.828</td> <td>  -30.577</td> <td> 0.000</td> <td> -352.327  -309.880</td>
</tr>
<tr>
  <th>C(skyc1)[T.CLR]</th> <td>   -4.4041</td> <td>    0.249</td> <td>  -17.662</td> <td> 0.000</td> <td>   -4.893    -3.915</td>
</tr>
<tr>
  <th>C(skyc1)[T.FEW]</th> <td>   -0.7330</td> <td>    0.226</td> <td>   -3.240</td> <td> 0.001</td> <td>   -1.176    -0.290</td>
</tr>
<tr>
  <th>C(skyc1)[T.M]</th>   <td>  -16.4341</td> <td>    8.681</td> <td>   -1.893</td> <td> 0.058</td> <td>  -33.448     0.580</td>
</tr>
<tr>
  <th>C(skyc1)[T.OVC]</th> <td>    0.3818</td> <td>    0.281</td> <td>    1.358</td> <td> 0.174</td> <td>   -0.169     0.933</td>
</tr>
<tr>
  <th>C(skyc1)[T.SCT]</th> <td>    0.8589</td> <td>    0.380</td> <td>    2.260</td> <td> 0.024</td> <td>    0.114     1.604</td>
</tr>
<tr>
  <th>C(skyc1)[T.VV ]</th> <td>    8.8603</td> <td>    0.509</td> <td>   17.414</td> <td> 0.000</td> <td>    7.863     9.858</td>
</tr>
<tr>
  <th>distance</th>        <td>    0.0008</td> <td>    0.000</td> <td>    6.174</td> <td> 0.000</td> <td>    0.001     0.001</td>
</tr>
<tr>
  <th>tmpf</th>            <td>   -0.1841</td> <td>    0.005</td> <td>  -38.390</td> <td> 0.000</td> <td>   -0.193    -0.175</td>
</tr>
<tr>
  <th>relh</th>            <td>    0.1626</td> <td>    0.004</td> <td>   38.268</td> <td> 0.000</td> <td>    0.154     0.171</td>
</tr>
<tr>
  <th>sped</th>            <td>    0.6096</td> <td>    0.018</td> <td>   33.716</td> <td> 0.000</td> <td>    0.574     0.645</td>
</tr>
<tr>
  <th>mslp</th>            <td>    0.3340</td> <td>    0.010</td> <td>   31.960</td> <td> 0.000</td> <td>    0.313     0.354</td>
</tr>
</table>
<table class="simpletable">
<tr>
  <th>Omnibus:</th>       <td>456713.147</td> <th>  Durbin-Watson:     </th>   <td>   1.872</td>  
</tr>
<tr>
  <th>Prob(Omnibus):</th>   <td> 0.000</td>   <th>  Jarque-Bera (JB):  </th> <td>76162962.824</td>
</tr>
<tr>
  <th>Skew:</th>            <td> 5.535</td>   <th>  Prob(JB):          </th>   <td>    0.00</td>  
</tr>
<tr>
  <th>Kurtosis:</th>        <td>68.816</td>   <th>  Cond. No.          </th>   <td>2.07e+05</td>  
</tr>
</table>




```python
fig, ax = plt.subplots()
ax.scatter(res.fittedvalues, res.resid, color='k', marker='.', alpha=.25)
ax.set(xlabel='Predicted', ylabel='Residual')
sns.despine()
plt.savefig('../content/images/indexes_resid_fit.png', transparent=True)
```


![png](Indexes_files/Indexes_67_0.png)



```python
weather.head()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>tmpf</th>
      <th>relh</th>
      <th>sped</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>vsby</th>
      <th>gust_mph</th>
      <th>skyc1</th>
      <th>skyc2</th>
      <th>skyc3</th>
    </tr>
    <tr>
      <th>station</th>
      <th>date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">01M</th>
      <th>2014-01-01 00:15:00</th>
      <td>33.80</td>
      <td>85.86</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 00:35:00</th>
      <td>33.44</td>
      <td>87.11</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 00:55:00</th>
      <td>32.54</td>
      <td>90.97</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 01:15:00</th>
      <td>31.82</td>
      <td>93.65</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 01:35:00</th>
      <td>32.00</td>
      <td>92.97</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>CLR</td>
      <td>M</td>
      <td>M</td>
    </tr>
  </tbody>
</table>
</div>




```python
import numpy as np
import pandas as pd


def read(fp):
    df = (pd.read_csv(fp)
            .rename(columns=str.lower)
            .drop('unnamed: 36', axis=1)
            .pipe(extract_city_name)
            .pipe(time_to_datetime, ['dep_time', 'arr_time', 'crs_arr_time', 'crs_dep_time'])
            .assign(fl_date=lambda x: pd.to_datetime(x['fl_date']),
                    dest=lambda x: pd.Categorical(x['dest']),
                    origin=lambda x: pd.Categorical(x['origin']),
                    tail_num=lambda x: pd.Categorical(x['tail_num']),
                    unique_carrier=lambda x: pd.Categorical(x['unique_carrier']),
                    cancellation_code=lambda x: pd.Categorical(x['cancellation_code'])))
    return df

def extract_city_name(df):
    '''
    Chicago, IL -> Chicago for origin_city_name and dest_city_name
    '''
    cols = ['origin_city_name', 'dest_city_name']
    city = df[cols].apply(lambda x: x.str.extract("(.*), \w{2}", expand=False))
    df = df.copy()
    df[['origin_city_name', 'dest_city_name']] = city
    return df

def time_to_datetime(df, columns):
    '''
    Combine all time items into datetimes.
    
    2014-01-01,0914 -> 2014-01-01 09:14:00
    '''
    df = df.copy()
    def converter(col):
        timepart = (col.astype(str)
                       .str.replace('\.0$', '')  # NaNs force float dtype
                       .str.pad(4, fillchar='0'))
        return  pd.to_datetime(df['fl_date'] + ' ' +
                               timepart.str.slice(0, 2) + ':' +
                               timepart.str.slice(2, 4),
                               errors='coerce')
        return datetime_part
    df[columns] = df[columns].apply(converter)
    return df


flights = read("878167309_T_ONTIME.csv")
```


```python
locs = weather.index.levels[0] & flights.origin.unique()
```


```python
(weather.reset_index(level='station')
 .query('station in @locs')
 .groupby(['station', pd.TimeGrouper('H')])).mean()
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th></th>
      <th>tmpf</th>
      <th>relh</th>
      <th>sped</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>vsby</th>
      <th>gust_mph</th>
    </tr>
    <tr>
      <th>station</th>
      <th>date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th rowspan="5" valign="top">ABE</th>
      <th>2014-01-01 00:00:00</th>
      <td>26.06</td>
      <td>47.82</td>
      <td>14.8</td>
      <td>1024.4</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>21.7</td>
    </tr>
    <tr>
      <th>2014-01-01 01:00:00</th>
      <td>24.08</td>
      <td>51.93</td>
      <td>8.0</td>
      <td>1025.2</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 02:00:00</th>
      <td>24.08</td>
      <td>49.87</td>
      <td>6.8</td>
      <td>1025.7</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 03:00:00</th>
      <td>23.00</td>
      <td>52.18</td>
      <td>9.1</td>
      <td>1026.2</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-01 04:00:00</th>
      <td>23.00</td>
      <td>52.18</td>
      <td>4.6</td>
      <td>1026.4</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>...</th>
      <th>...</th>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th rowspan="5" valign="top">XNA</th>
      <th>2014-01-30 19:00:00</th>
      <td>44.96</td>
      <td>38.23</td>
      <td>16.0</td>
      <td>1009.7</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>25.1</td>
    </tr>
    <tr>
      <th>2014-01-30 20:00:00</th>
      <td>46.04</td>
      <td>41.74</td>
      <td>16.0</td>
      <td>1010.3</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-30 21:00:00</th>
      <td>46.04</td>
      <td>41.74</td>
      <td>13.7</td>
      <td>1010.9</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>20.5</td>
    </tr>
    <tr>
      <th>2014-01-30 22:00:00</th>
      <td>42.98</td>
      <td>46.91</td>
      <td>11.4</td>
      <td>1011.5</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2014-01-30 23:00:00</th>
      <td>39.92</td>
      <td>54.81</td>
      <td>3.4</td>
      <td>1012.2</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
<p>191445 rows × 7 columns</p>
</div>




```python
df = (flights.copy()[['unique_carrier', 'tail_num', 'origin', 'dep_time']]
      .query('origin in @locs'))
```


```python

```


```python
weather.loc['DSM']
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>tmpf</th>
      <th>relh</th>
      <th>sped</th>
      <th>mslp</th>
      <th>p01i</th>
      <th>vsby</th>
      <th>gust_mph</th>
      <th>skyc1</th>
      <th>skyc2</th>
      <th>skyc3</th>
    </tr>
    <tr>
      <th>date</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2014-01-01 00:54:00</th>
      <td>10.94</td>
      <td>72.79</td>
      <td>10.3</td>
      <td>1024.9</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>FEW</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 01:54:00</th>
      <td>10.94</td>
      <td>72.79</td>
      <td>11.4</td>
      <td>1025.4</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>OVC</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 02:54:00</th>
      <td>10.94</td>
      <td>72.79</td>
      <td>8.0</td>
      <td>1025.3</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>BKN</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 03:54:00</th>
      <td>10.94</td>
      <td>72.79</td>
      <td>9.1</td>
      <td>1025.3</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>OVC</td>
      <td>M</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-01 04:54:00</th>
      <td>10.04</td>
      <td>72.69</td>
      <td>9.1</td>
      <td>1024.7</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>BKN</td>
      <td>M</td>
      <td>M</td>
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
    </tr>
    <tr>
      <th>2014-01-30 19:54:00</th>
      <td>30.92</td>
      <td>55.99</td>
      <td>28.5</td>
      <td>1006.3</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>35.3</td>
      <td>FEW</td>
      <td>FEW</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-30 20:54:00</th>
      <td>30.02</td>
      <td>55.42</td>
      <td>14.8</td>
      <td>1008.4</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>28.5</td>
      <td>FEW</td>
      <td>FEW</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-30 21:54:00</th>
      <td>28.04</td>
      <td>55.12</td>
      <td>18.2</td>
      <td>1010.4</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>26.2</td>
      <td>FEW</td>
      <td>FEW</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-30 22:54:00</th>
      <td>26.06</td>
      <td>57.04</td>
      <td>13.7</td>
      <td>1011.8</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>FEW</td>
      <td>FEW</td>
      <td>M</td>
    </tr>
    <tr>
      <th>2014-01-30 23:54:00</th>
      <td>21.92</td>
      <td>62.13</td>
      <td>13.7</td>
      <td>1013.4</td>
      <td>0.0</td>
      <td>10.0</td>
      <td>NaN</td>
      <td>FEW</td>
      <td>FEW</td>
      <td>M</td>
    </tr>
  </tbody>
</table>
<p>896 rows × 10 columns</p>
</div>




```python
df = df
```




<div>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>fl_date</th>
      <th>unique_carrier</th>
      <th>airline_id</th>
      <th>tail_num</th>
      <th>fl_num</th>
      <th>origin_airport_id</th>
      <th>origin_airport_seq_id</th>
      <th>origin_city_market_id</th>
      <th>origin</th>
      <th>origin_city_name</th>
      <th>...</th>
      <th>arr_delay</th>
      <th>cancelled</th>
      <th>cancellation_code</th>
      <th>diverted</th>
      <th>distance</th>
      <th>carrier_delay</th>
      <th>weather_delay</th>
      <th>nas_delay</th>
      <th>security_delay</th>
      <th>late_aircraft_delay</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2014-01-01</td>
      <td>AA</td>
      <td>19805</td>
      <td>N338AA</td>
      <td>1</td>
      <td>12478</td>
      <td>1247802</td>
      <td>31703</td>
      <td>JFK</td>
      <td>New York</td>
      <td>...</td>
      <td>13.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>2475.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2014-01-01</td>
      <td>AA</td>
      <td>19805</td>
      <td>N339AA</td>
      <td>2</td>
      <td>12892</td>
      <td>1289203</td>
      <td>32575</td>
      <td>LAX</td>
      <td>Los Angeles</td>
      <td>...</td>
      <td>111.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>2475.0</td>
      <td>111.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2014-01-01</td>
      <td>AA</td>
      <td>19805</td>
      <td>N335AA</td>
      <td>3</td>
      <td>12478</td>
      <td>1247802</td>
      <td>31703</td>
      <td>JFK</td>
      <td>New York</td>
      <td>...</td>
      <td>13.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>2475.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2014-01-01</td>
      <td>AA</td>
      <td>19805</td>
      <td>N367AA</td>
      <td>5</td>
      <td>11298</td>
      <td>1129803</td>
      <td>30194</td>
      <td>DFW</td>
      <td>Dallas/Fort Worth</td>
      <td>...</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>3784.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2014-01-01</td>
      <td>AA</td>
      <td>19805</td>
      <td>N364AA</td>
      <td>6</td>
      <td>13830</td>
      <td>1383002</td>
      <td>33830</td>
      <td>OGG</td>
      <td>Kahului</td>
      <td>...</td>
      <td>-8.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>3711.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
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
      <td>...</td>
      <td>...</td>
    </tr>
    <tr>
      <th>471944</th>
      <td>2014-01-31</td>
      <td>OO</td>
      <td>20304</td>
      <td>N292SW</td>
      <td>5313</td>
      <td>12889</td>
      <td>1288903</td>
      <td>32211</td>
      <td>LAS</td>
      <td>Las Vegas</td>
      <td>...</td>
      <td>-7.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>259.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>471945</th>
      <td>2014-01-31</td>
      <td>OO</td>
      <td>20304</td>
      <td>N580SW</td>
      <td>5314</td>
      <td>12892</td>
      <td>1289203</td>
      <td>32575</td>
      <td>LAX</td>
      <td>Los Angeles</td>
      <td>...</td>
      <td>-12.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>89.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>471946</th>
      <td>2014-01-31</td>
      <td>OO</td>
      <td>20304</td>
      <td>N580SW</td>
      <td>5314</td>
      <td>14689</td>
      <td>1468902</td>
      <td>34689</td>
      <td>SBA</td>
      <td>Santa Barbara</td>
      <td>...</td>
      <td>11.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>89.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>471947</th>
      <td>2014-01-31</td>
      <td>OO</td>
      <td>20304</td>
      <td>N216SW</td>
      <td>5315</td>
      <td>11292</td>
      <td>1129202</td>
      <td>30325</td>
      <td>DEN</td>
      <td>Denver</td>
      <td>...</td>
      <td>56.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>260.0</td>
      <td>36.0</td>
      <td>0.0</td>
      <td>13.0</td>
      <td>0.0</td>
      <td>7.0</td>
    </tr>
    <tr>
      <th>471948</th>
      <td>2014-01-31</td>
      <td>OO</td>
      <td>20304</td>
      <td>N216SW</td>
      <td>5315</td>
      <td>14543</td>
      <td>1454302</td>
      <td>34543</td>
      <td>RKS</td>
      <td>Rock Springs</td>
      <td>...</td>
      <td>47.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>0.0</td>
      <td>260.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>4.0</td>
      <td>0.0</td>
      <td>43.0</td>
    </tr>
  </tbody>
</table>
<p>471949 rows × 36 columns</p>
</div>




```python
dep.head()
```




    0        2014-01-01 09:14:00
    1        2014-01-01 11:32:00
    2        2014-01-01 11:57:00
    3        2014-01-01 13:07:00
    4        2014-01-01 17:53:00
                     ...        
    163906   2014-01-11 16:57:00
    163910   2014-01-11 11:04:00
    181062   2014-01-12 17:02:00
    199092   2014-01-13 23:36:00
    239150   2014-01-16 16:46:00
    Name: dep_time, dtype: datetime64[ns]




```python
flights.dep_time
```




    0        2014-01-01 09:14:00
    1        2014-01-01 11:32:00
    2        2014-01-01 11:57:00
    3        2014-01-01 13:07:00
    4        2014-01-01 17:53:00
                     ...        
    471944   2014-01-31 09:05:00
    471945   2014-01-31 09:24:00
    471946   2014-01-31 10:39:00
    471947   2014-01-31 09:28:00
    471948   2014-01-31 11:22:00
    Name: dep_time, dtype: datetime64[ns]




```python
flights.dep_time.unique()
```




    array(['2014-01-01T03:14:00.000000000-0600',
           '2014-01-01T05:32:00.000000000-0600',
           '2014-01-01T05:57:00.000000000-0600', ...,
           '2014-01-30T18:44:00.000000000-0600',
           '2014-01-31T17:16:00.000000000-0600',
           '2014-01-30T18:47:00.000000000-0600'], dtype='datetime64[ns]')




```python
stations
```


```python
flights.dep_time.head()
```




    0   2014-01-01 09:14:00
    1   2014-01-01 11:32:00
    2   2014-01-01 11:57:00
    3   2014-01-01 13:07:00
    4   2014-01-01 17:53:00
    Name: dep_time, dtype: datetime64[ns]

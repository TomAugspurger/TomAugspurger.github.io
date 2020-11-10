---
title: Tidy Data in Action
date: 2014-03-27 16:00
slug: Tidy Data in Action
category: scripts
tags: python, scripts, data science, pandas
---


[Hadley Whickham](http://had.co.nz) wrote a famous paper (for a certain definition of famous) about the importance of [tidy data](http://vita.had.co.nz/papers/tidy-data.pdf) when doing data analysis.
I want to talk a bit about that, using an example from a StackOverflow post, with a solution using [pandas](http://pandas.pydata.org). The principles of tidy data aren't language specific.

A tidy dataset must satisfy three criteria (page 4 in [Whickham's paper](http://vita.had.co.nz/papers/tidy-data.pdf)):

  1. Each variable forms a column.
  2. Each observation forms a row.
  3. Each type of observational unit forms a table.


In this [StackOverflow post](http://stackoverflow.com/questions/22695680/python-pandas-timedelta-specific-rows), the asker had some data NBA games, and wanted to know the number of days since a team last played. Here's the example data:


```python
import datetime

import pandas as pd

df = pd.DataFrame({'HomeTeam': ['HOU', 'CHI', 'DAL', 'HOU'],
                   'AwayTeam' : ['CHI', 'DAL', 'CHI', 'DAL'],
                   'HomeGameNum': [1, 2, 2, 2],
                   'AwayGameNum' : [1, 1, 3, 3],
                   'Date' : [datetime.date(2014,3,11), datetime.date(2014,3,12),
                             datetime.date(2014,3,14), datetime.date(2014,3,15)]})
df
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>AwayGameNum</th>
      <th>AwayTeam</th>
      <th>Date</th>
      <th>HomeGameNum</th>
      <th>HomeTeam</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td> 1</td>
      <td> CHI</td>
      <td> 2014-03-11</td>
      <td> 1</td>
      <td> HOU</td>
    </tr>
    <tr>
      <th>1</th>
      <td> 1</td>
      <td> DAL</td>
      <td> 2014-03-12</td>
      <td> 2</td>
      <td> CHI</td>
    </tr>
    <tr>
      <th>2</th>
      <td> 3</td>
      <td> CHI</td>
      <td> 2014-03-14</td>
      <td> 2</td>
      <td> DAL</td>
    </tr>
    <tr>
      <th>3</th>
      <td> 3</td>
      <td> DAL</td>
      <td> 2014-03-15</td>
      <td> 2</td>
      <td> HOU</td>
    </tr>
  </tbody>
</table>
<p>4 rows × 5 columns</p>
</div>



I want to focus on the second of the three criteria: *Each observation forms a row.*
Realize that the structure your dataset should take reflects the question you're trying to answer.
For the SO question, we want to answer "How many days has it been since this team's last game?"
Given this context what is an observation?

---

We'll define an observation as a team playing on a day.
Does the original dataset in `df` satisfy the criteria for tidy data?
No, it doesn't since each row contains **2** observations, one for the home team and one for the away team.

Let's tidy up the dataset.

- I repeat each row (once for each team) and drop the game numbers (I don't need them for this example)
- Select just the new rows (the one with odd indicies, `%` is the [modulo operator](http://en.wikipedia.org/wiki/Modulo_operation) in python)
- Overwrite the value of `Team` for the new rows, keeping the existing value for the old rows
- rename the `HomeTeam` column to `is_home` and make it a boolen column (True when the team is home)


```python
s = df[['Date', 'HomeTeam', 'AwayTeam']].reindex_axis(df.index.repeat(2)).reset_index(drop=True)
s = s.rename(columns={'AwayTeam': 'Team'})

new = s[(s.index % 2).astype(bool)]

s.loc[new.index, 'Team'] = new.loc[:, 'HomeTeam']

s = s.rename(columns={'HomeTeam': 'is_home'})
s['is_home'] = s['Team'] == s['is_home']
s
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Date</th>
      <th>is_home</th>
      <th>Team</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td> 2014-03-11</td>
      <td> False</td>
      <td> CHI</td>
    </tr>
    <tr>
      <th>1</th>
      <td> 2014-03-11</td>
      <td>  True</td>
      <td> HOU</td>
    </tr>
    <tr>
      <th>2</th>
      <td> 2014-03-12</td>
      <td> False</td>
      <td> DAL</td>
    </tr>
    <tr>
      <th>3</th>
      <td> 2014-03-12</td>
      <td>  True</td>
      <td> CHI</td>
    </tr>
    <tr>
      <th>4</th>
      <td> 2014-03-14</td>
      <td> False</td>
      <td> CHI</td>
    </tr>
    <tr>
      <th>5</th>
      <td> 2014-03-14</td>
      <td>  True</td>
      <td> DAL</td>
    </tr>
    <tr>
      <th>6</th>
      <td> 2014-03-15</td>
      <td> False</td>
      <td> DAL</td>
    </tr>
    <tr>
      <th>7</th>
      <td> 2014-03-15</td>
      <td>  True</td>
      <td> HOU</td>
    </tr>
  </tbody>
</table>
<p>8 rows × 3 columns</p>
</div>



Now that we have a 1:1 correspondance between rows and observations, answering the question is simple.

We'll just group by each team and find the difference between each consecutive `Date` for that team.
Then subtract one day so that back to back games reflect 0 days of rest.


```python
s['rest'] = s.groupby('Team')['Date'].diff() - datetime.timedelta(1)
s
```




<div style="max-height:1000px;max-width:1500px;overflow:auto;">
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Date</th>
      <th>is_home</th>
      <th>Team</th>
      <th>rest</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td> 2014-03-11</td>
      <td> False</td>
      <td> CHI</td>
      <td>   NaT</td>
    </tr>
    <tr>
      <th>1</th>
      <td> 2014-03-11</td>
      <td>  True</td>
      <td> HOU</td>
      <td>   NaT</td>
    </tr>
    <tr>
      <th>2</th>
      <td> 2014-03-12</td>
      <td> False</td>
      <td> DAL</td>
      <td>   NaT</td>
    </tr>
    <tr>
      <th>3</th>
      <td> 2014-03-12</td>
      <td>  True</td>
      <td> CHI</td>
      <td>0 days</td>
    </tr>
    <tr>
      <th>4</th>
      <td> 2014-03-14</td>
      <td> False</td>
      <td> CHI</td>
      <td>1 days</td>
    </tr>
    <tr>
      <th>5</th>
      <td> 2014-03-14</td>
      <td>  True</td>
      <td> DAL</td>
      <td>1 days</td>
    </tr>
    <tr>
      <th>6</th>
      <td> 2014-03-15</td>
      <td> False</td>
      <td> DAL</td>
      <td>0 days</td>
    </tr>
    <tr>
      <th>7</th>
      <td> 2014-03-15</td>
      <td>  True</td>
      <td> HOU</td>
      <td>3 days</td>
    </tr>
  </tbody>
</table>
<p>8 rows × 4 columns</p>
</div>



I planned on comparing that one line solution to the code needed with the messy data.
But honestly, I'm having trouble writing the messy data version.
You don't really have anything to group on, so you'd need to keep track of the row where you last saw this team (either in `AwayTeam` or `HomeTeam`).
And then each row will have two answers, one for each team.
It's certainly possible to write the necessary code, but the fact that I'm struggling so much to write the messy version is pretty good evidence for the importance of tidy data.

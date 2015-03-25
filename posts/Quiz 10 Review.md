.. title: Stats for Strategy Quiz 10 Review
.. date: 2014-05-01 12:00
.. slug: Quiz 10 Review
.. category: stats for strategy
.. tags: stats for strategy, review

This was our first week of Time Series Analysis, and we covered smoothing methods and autocorrelation. Overall, the scores were pretty good. If you have any questions going into the final, let me know. I'll be around.

# Section A01

This quiz focused on exponential smoothing. Make sure that you know about moving averages and autocorrelation too.

### #1

You needed to find the biggest decline in the time series.
You should never have to guess in stats, and I'm worried that some of you just looked at the graph and guessed the right week.
I'd suggest plotting the series to get an idea of where the biggest declines were.
Then you can go into the dataset and verify that the biggest decline was the the week of 2007-07-21.

### #2

The model that provides the most smoothing will *always* be the model with the lowest $w$, $w=.10$ in this case.
This puts 10% of the weight on the most recent observation, and 90% on prior observations, which means that the exponentially smoothed prediction won't jump around a lot in response to one day's change.

For part $d$, some people got returned an interval. It was only asking for a single number though, the prediction error: $e_t = y_t - \hat{y}_t$. If it had asked for a prediction error with $x$% confidence, then you should return an interval.

I'm not sure if anyone got the extra credit. This was like the Cubs example we did in class. For ES models, the prediction for tomorrow depends on the entire history. This means we need to fit our model to the entire dataset. But, part $f$ was specifically concerned with the accuracy of *future* forecasts. So even though we fit the model to the whole dataset, we only are interested in the residuals of 2008. Copy-paste those up to a new column and calculate the MSE.

# Section B42

This quiz focused on moving averages. Make sure that you know about exponential smoothing and autocorrelation too.

### #1

You needed to find the biggest decline in the time series.
You should never have to guess in stats, and I'm worried that some of you just looked at the graph and guessed the right week.
I'd suggest plotting the series to get an idea of where the biggest declines were.
Then you can go into the dataset and verify that the biggest decline was the the week of 2007-07-21.

### #2

The model that provides the most smoothing will *always* be the model with the highest $k$, $k=12$ in this case.
This averages the last $k$ periods when forecasting for tomorrow, which means that the moving average won't jump around a lot in response to one just one day's change.

For part $d$, some people got returned an interval. It was only asking for a single number though, the prediction error: $e_t = y_t - \hat{y}_t$. If it had asked for a prediction error with $x$% confidence, then you should return an interval.

I'm not sure if anyone got the extra credit. This was like the Cubs example we did in class. For MA models, we don't want to lose a prediction for the first $k$ periods, so we need to fit our model to the entire dataset. But, part $f$ was specifically concerned with the accuracy of *future* forecasts. So even though we fit the model to the whole dataset, we only are interested in the residuals of 2008. Copy-paste those up to a new column and calculate the MSE.

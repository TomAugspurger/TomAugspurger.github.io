.. title: Stats for Strategy Quiz 5 Review
.. date: 2014-03-14 12:00
.. slug: Quiz 5 Review
.. category: stats for strategy
.. tags: stats for strategy, review

# Section A01

## Problem 1

Make sure to read the questions carefully, in particular **the underlined or bold parts**. For this question we wanted the **statistical concept** that explains why interpreting a prediction for a car with 0 City MPG is mislaeding. I agree with many of you that a negative Highway MPG doesn't make sense physically, but that doesn't answer the question.

The statistical concept is *extrapolation*: making predictions for values outside of your sample dataset. The City MPG of $0$ fell below of the lowest City MPG in our sample. We can't be confident that the relationship that we found in the sample area holds for City MPGs that low (it probably doesn't in this case).

## Problem 2

If $r_i$ is the indivudal contribution of website $i$ to the correlation, then

\begin{equation}
    r_i  = \left( \frac{\bar{x} - x_i}{s_x} \right) \left( \frac{\bar{y} - y_i}{s_y} \right)
\end{equation}

In this case $\bar{x} = 140.5, x_i = 138.38, s_x = 10.46, \bar{y} = 1.17, y_i =  1.007, s_y = 0.1513$

## Problem 3

You'll want to find the correlation coefficient $r$ using your calculator. Talk to me if you don't know how.

# Seciton B42

## Problem 1

The prompt was to name a **lurking variable** based on one of the possibilties listed. The two possibilties hinted at the number of failures of each brand being related to the number of each tire on the road. Simply concluding that the Wilderness tires are worst without considering the number of each brand in use would be wrong. The number of each brand in use is the lurking variable.

It's *possible* that there are other lurking variables: The average age of each brand of tire (older tires more likely to fail), the type of road typically driven on for each brand (rougher, country roads are more likely to cause a flat). You all were very creative with your potential lurking variables. But to get the points, your answer needed to be based on the possibilities listed.

## Problem 2

We're asserting that there's a linear relationship between the *population* number of hits per day and the *population* sales revenue per hit.

\begin{equation}
    revenue = \beta_0 + \beta_1 hits + \varepsilon
\end{equation}

The question wants us to estimate the fitted regression equation. You can get the estimate for the coefficeints a bunch of different ways (by hand, using linear algebra, your calculator, a computer). For this one, the easiest way would be with your calculator. The *fitted* or estimated regression equation is

\begin{equation}
    revenue = 2.00 - .007 hits
\end{equation}

## Problem 3

Your calculator should also give the $R^2$, the percentage of variation in revenue explained by the variation in number of hits. Talk to me if you are having trouble with this.

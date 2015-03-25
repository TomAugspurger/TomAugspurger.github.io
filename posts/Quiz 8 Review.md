.. title: Stats for Strategy Quiz 8 Review
.. date: 2014-04-10 17:00
.. slug: Quiz 8 Review
.. category: stats for strategy
.. tags: stats for strategy, review

Good luck on the exam.
Don't forget your section number!

# Section A01

## #2

Remember that for the modified best conservative model, we still care about the significance of all the predictors other than the ones that must be included.

## #3

Quite a few people are still giving point estimates (just $\hat{y}$) when the question asks you to predict $y$ with some % certainty.
If you're asked to predict something with 95% certainty, your answer should be an interval.

## #4

Make sure to use the right model for each question.
This one asks us to go back to the best conservative model (from #1).
Also, `Forearm` can still be interpreted, despite not being in the model.
We just say that it is unrelated to `BP`, after accounting for the other two predictors.

## #5

We want the most accurate estimate of $\beta_{calf}$, so we'll use the full model (see p. 134 in the notebook).
Including insignificant predictors will increase the variance of your $\hat{y}$'s.
But for this problem we're only interested in the slope, so we'll include all the predictors, even if they aren't significant.

# Section B42

Make sure to understand the goal of the drop method: find the model that gives us the most accurate predictions (best $\hat{y}$'s), i.e. the best conservative model.
The drop method is a fast way to (usually) get the best conservative model when you have many predictors.

For part c, we can still interpret predictors that aren't included in the model.
Each of them is unrelated to blood pressure after controlling for the variables you did include in the model.

The last question asks you to interpret the slope for `Age` from the simple regression model.
First of all, make sure to use the simple regression model; `Age` should be the only predictor.
Since `Age` is a binary variable, the interpretation is a bit different than usual.
Instead of saying "For every 1 unit increase in `Age`, `BP` changes by $\hat{\beta_1}$", we just compare the two groups.
Since $\hat{\beta_1} = 2.5$, we can say that "On average, people older than 40 (`Age`=1) have 2.50 points higher blood pressure than people younger than 40."

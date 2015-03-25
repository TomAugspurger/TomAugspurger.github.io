.. title: Stats for Strategy Quiz 4 Review
.. date: 2014-02-27 20:00
.. slug: Quiz 4 Review
.. category: stats for strategy
.. tags: stats for strategy, review

We are circling clusters of **means**.
Some people were circling the samples.
ANOVA is all about comparing how spread out the **means** are *relative to how spread out the **samples** are*.
If two means are far away (relative to how spread out the samples are) the **means** will be in separate clusters.

The number of clusters decreases as the F statistic decreases. The extreme case is $F \leq 1$ where the means aren't very spread out relative to the variance of the samples. In this case, we fail to reject $H_0$ (that all the means are the same), and we have a single cluster.

By the way, there's no need to eyeball the clusters. You run an ANOVA on each column (Vitamin A, C, E), and look at the Tukey intervals.
Scan the Tukey intervals for significant differences and sketch out the clusters like I did in class.
The $F$ statistic and $p-value$ alone doesn't tell us how many clusters there may be.
At most it can tell us if there's 1 cluster, or 2+ clusters (why? Hint: look in the notes for a reference to $H_0$ being a "Gateway Hypothesis")

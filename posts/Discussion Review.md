.. title: Quiz 1 Review
.. date: 2014-02-03 12:00
.. slug: Discussion Review
.. category: stats for strategy
.. tags: stats for strategy, review


- General remarks
    - read the questions carefully, especially the bold and underlined parts.
    - The full solutions are on ICON.

- [Section A01](#sectionA01)
- [Section B42](#sectionB42)

## Section A01<a name="sectionA01"></a>

### #1

- Don't mix up the sample **statistic** with the **sample**. The sample is a group of some objects (bars, people, etc.). The statistic is some number that describes the sample (the proportion checking IDs).
- The actual *number* of bars checking IDs isn't that interesting, since it depends on the size of the sample or population. If I just say 3 bars didn't check IDs, is that meaningful? You need to know how many bars I visited to put those 3 that didn't check IDs in context.


### #2

- Means vs. proportions problem:
    + What kind of data do you have? Is it categorical (proportions) or quantitative (means)?
    + Use the $t$ table for means and the $Z$ for proportions.
-Step 1 includes defining the parameter or parameters. In this case that means $p$: the proportion of all adults who choose clothing first.

- When to use CI vs. test statistic & p-values?
    + Testing a hypothesis: `clothing is the first choice for most adults`, so we need to find a a test statistic ($Z$) and a p-value. CI and hypothesis tests are related, but a p-value is exactly what we need for the hypothesis tests: What is the probability of wrongly rejecting $H_0$ based on our sample when $H_0$ is actually true?
- A lot of people did hypothesis tests on the *statistic* instead of the *parameter* (i.e. $H_A: \hat{p} > 0.5$). But we already know $\hat{p} = .47719 < .5$, so there's no reason to do a hypothesis test on that. We don't know the value of the parameter $p$, so we do the hypothesis test on it.

- Shading helps. In this case we had

\begin{align}
    H_A &= p >    0.5 \\\\
    H_0 &= p \leq 0.5
\end{align}

The p-value is evidence for $H_A$, so we want to shade to the right.

- When to reject vs. fail to reject $H_0$?
    + Look at the definitions of a p-value on `p. 26`. We reject $H_0$ when the p-value (the risk of wrongly rejection $H_0$ when it's actually true) is small compared the $\alpha$, our risk tolerance.


## Section B42 <a name="sectionB42"></a>

### #1

- Don't mix up the population **parameter** with the population. The population is a set of objects (people, bars, etc). and the parameter is a number (probably unknown) that describes them.

### #2

- Make sure to define the parameter or parameters.
- When to use CI vs. test statistic & p-values?
    + Testing a hypothesis: `clothing is the first choice for most adults`, so we need to find a a test statistic ($Z$) and a p-value. CI and hypothesis tests are related, but a p-value is exactly what we need for the hypothesis tests: What is the probability of wrongly rejecting $H_0$ based on our sample when $H_0$ is actually true?

- When to reject vs. fail to reject $H_0$?
    + Look at the definitions of a p-value on `p. 26`. We reject $H_0$ when the p-value (the risk of wrongly rejection $H_0$ when it's actually true) is small compared the $\alpha$, our risk tolerance.
- $p_0$ vs. $\hat{p}$ in the denominator for $Z$. Be careful with the formula.
- `It is true that clothing is the first choice ...` vs. `Sufficient evidence to conclude that clothing is the first choice ...` aren't quite the same.

2b: Select $H_a \neq$ to get a CI and check the box to use the normal (Z) distrubtion.

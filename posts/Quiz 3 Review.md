.. title: Stats for Strategy Quiz 3 Review
.. date: 2014-02-21 12:00
.. slug: Quiz 3 Review
.. category: stats for strategy
.. tags: stats for strategy, review

# A01<a name="sectionA01"></a>

Take a look a ICON for the solutions on this one. There's a brief explanation of each answer. It's harder to give feedback on this one since it's multiple choice, so email me if you have any questions.

Remember that this week's homework was over $\chi^2$ and two-means. This quiz only covered $\chi^2$, so make sure you figure out if you understand two-means.

## #1

This is the mathy way of writing that `Wine choice` and `Music` are unrelated: the type of music playing doesn't affect the type of wine you buy: $p_{11} = p_{21} = p_{31}$. The first subscript represent the type of wine and the second represents the type of music.

## #6 & #7

For these two you need to figure out which output to use. You can tell by the numbers put in Minitab for the # of events and # of trials. Make sure that they line up with the definitions of $p_1$ and $p_2$: so for #6 we have $p_1$: the proportion of all wines bought while French music are playing that are French.

---

# B42<a name="sectionB42"></a>

Remember that this week's homework was over $\chi^2$ and two-means. This quiz only covered two-means, so make sure you figure out if you understand $\chi^2$.

## #1

Step 1 still includes defining parameters. A lot of people didn't.
Were you confused by $\chi^2$? We don't *usually* define them there (or in ANOVA) since there are usually so many.
But with 2 means we can define the 2 means $\mu_1$ and $\mu_2$.

This one was independent (not paired) since the 70 men and 70 women were each randomly sampled from their own populations. There's no reason to link up `man #1` with `women #1` rather than some other. A couple of examples of how this *could* have been setup as a paired problem:

- each man and woman is a fraternal twin, and their sibling of the opposite sex is also in the survey. Then we pair **by twin**.
- The 70 men and 70 women are put into study pairs at the beginning of the semester. Then we pair by **study pair**.

## #2

In this problem, `The sample evidence supports the null hypothesis` is only true when $\bar{x}_1 = \bar{x}_2$ (since $H_0$ is $\mu_1 = \mu_2$). *Anything* else is evidence against $H_0$ and in favor of $H_a$. The only remaining question is whether there's just some sample evidence against $H_0$, or enough sample evidence against $H_0$ that we are comfortable rejecting it, in favor of $H_a$.

## #3

A lot of people were trying to talk about the *people* differing. Something like `between 17% to 43.1% men differ from women`. Or `between 17% fewer to 43.1% more men than women have a better GPA`. That's wrong.
Our CI is for the value $\mu_1 - \mu_2$, the difference in the two means, *i.e.* the difference in the two average GPAs. So we're 99% confident that the mean GPA for men is between 17 points lower to 43.1 points higher than the mean GPA for women.

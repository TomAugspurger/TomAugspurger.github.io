.. title: Stats for Strategy Quiz 2 Review
.. date: 2014-02-07 12:00
.. slug: Quiz 2 Review
.. category: stats for strategy
.. tags: stats for strategy, review

# General Comments

Much better this week! Keep it up. If you see <font color='red'>(half)</font> anywhere on your quiz that means that you missed an earlier question, which caused you to miss the later question. So you did everything correct on the later question, but you didn't get the right answer because of the earlier mistake.

For example suppose you mess up calculating the p-value, so now it's bigger than $\alpha$ when it should have been smaller. That messes you up in step 3 since you fail to reject $H_0$ when you should have rejected it. You get half credit for these. Ask me if you have any questions about grading.

- [Section A01](#sectionA01)
- [Section B42](#sectionB42)

# A01<a name="sectionA01"></a>

## #1

The first step is to recognize the problem. As you're reading the prompt, you should be asking yourself:

- What kind of data is this? (quantitative (t) or categorical (Z))
- How many samples / populations are there?
- What is the sample / samples? What is the population / populations?
- What are the sample statistics? What are the population parameters?
- Are we testing a hypothesis? Or do we need a CI?

Still some confusion about the parameters:

- Describe the population
- $p_1$ and $p_2$ in this case (no hats)
- The parameters' values are not usually known.
- In this case we care about the **proportion**, not the raw number who attend

## #2

For the p-value:

- Select alternative -> greater than (to match $H_a$)
- We don't use Fisher's p-value
- check the box for pooled p: $p = \frac{x_1 + x_2}{n_1 + n_2}$

## #3

Deciding: What is the p-value?

- The risk of *wrongly* rejecting $H_0$ (based on our sample evidence) when $H_0$ is actually true.
- Compare that to our risk tolerance $\alpha$.
- When it's not too risky to reject $H_0$, p-value $< \alpha$ we reject $H_0$ and go with $H_a$
- When it is too risky to reject $H_0$, we fail to reject $H_0$ (which isn't quite the same as concluding that $H_0$ is true).

## #4/5

Can we conclude that more underclassmen attend the game than upperclassmen? Not quite. What if $N_2 >> N_1$, *i.e.* there are a lot more upperclassmen in the population?

# B42<a name="sectionB42"></a>

## #1
The first step is to recognize the problem. As you're reading the prompt, you should be asking yourself:

- What kind of data is this? (quantitative (t) or categorical (Z))
- How many samples / populations are there?
- What is the sample / samples? What is the population / populations?
- What are the sample statistics? What are the population parameters?
- Are we testing a hypothesis? Or do we need a CI?

Still some confusion about the parameters:

- Describe the population
- $p_1$ and $p_2$ in this case (no hats)
- The parameters' values are not usually known.
- In this case we care about the **proportion**, not the raw number who attend

The alternative hypothesis is what we're testing: Are current users less likely than nonusers to prefer the new product. $H_a: p_1 < p_2$

## #2

Which way to shade? We shade evidence for $H_a$ so to the left of the $Z$ in this case.

## #3

Deciding: What is the p-value?

- The risk of *wrongly* rejecting $H_0$ (based on our sample evidence) when $H_0$ is actually true.
- Compare that to our risk tolerance $\alpha$.
- When it's not too risky to reject $H_0$, p-value $< \alpha$ we reject $H_0$ and go with $H_a$
- When it is too risky to reject $H_0$, we fail to reject $H_0$ (which isn't quite the same as concluding that $H_0$ is true).

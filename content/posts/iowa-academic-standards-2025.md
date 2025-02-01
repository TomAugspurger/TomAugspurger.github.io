---
title: "Iowa's Proposed State Science Standards"
date: 2025-02-01T12:00:00-06:00
---

My local Department of Education has a [public comment
period](https://educate.iowa.gov/headline-story/2025-01-03/public-comment-period-opens-state-science-standards)
for some proposed changes to Iowa's science education standards. If you live in
Iowa, I'd encourage you to read the
[proposal](https://educate.iowa.gov/media/10837/download?inline) (PDF) and share
feedback through the [survey](https://www.surveymonkey.com/r/GHS2RYC). If you,
like me, get frustrated with how difficult it is to see what's changed or link
to a specific piece of text, read on.

I'd heard rumblings that there were some controversial changes around evolution
and climate change. But rather than just believing what I read in a headline, I
decided to do my own research (science in action, right?).

## The proposed changes

I might have missed it, but I couldn't find anywhere with the *changes* in an
easily viewable form. The documents are available as PDFs ([2015
standards][2015], [2025 draft][2025]). The two PDFs aren't formatted the same,
making it very challenging to visually "diff" the two.

The programmers in the room will know that comparing two pieces of text is a
pretty well solved problem. So I present to you, [the changes][changes]:


<img width="1203" alt="Image" src="https://github.com/user-attachments/assets/1c8432de-df70-4568-b1c1-c79781c5f6c7" />

The 2015 text is in red. The 2025 text is in green. That link includes just the top-level standards, not the "End of Grade Band Practice Clarification", "Disciplinary Content Clarification", or "End of Grade Band Conceptual Frame Clarification".

The [Python
script](https://github.com/TomAugspurger/iowa-academic-standards/blob/main/generate_diff.py)
I wrote to generate that diff took an hour or so to write and debug. If the
standards had been in a format more accessible than a PDF it would have been
minutes of work.

I'm somewhat sympathetic to the view that we should evaluate these new standards
on their own terms, and not be biased by the previous language. But a quick
glance at most of the changes shows you this *is* about language, and politics.
It's nice to be able to skim a single webpage to see that they're just doing a
Find and Replace for "evolution" and "climate change".

## Some thoughts

I'm mostly just disappointed. Disappointed in the people pushing this. Disappointed that they're trying to claim the [legitimacy of expertise](https://educate.iowa.gov/headline-story/2025-01-03/public-comment-period-opens-state-science-standards)

> The standards were reviewed by a team consisting of elementary and secondary educators, administrators, content specialists, families, representatives from Iowa institutions of higher education and community partners.

and then saying they're [merely advisory](https://www.thegazette.com/state-government/committee-members-we-didnt-recommend-science-standards-omitting-climate-change-evolution/)

> The team serves in an advisory capacity to the department; it does not finalize the first proposed revised draft standards

That's a key component of pseudoscience: wrapping yourself in the language and of science and claiming expertise.

I'm disappointed that they they're unwilling or unable to present the information in a easy to understand form.

I'm disappointed that they don't live up to the documents's own (well-put!) declaration on the importance of a good science education:

> By the end of 12th grade, every student should appreciate the wonders of science and have the knowledge necessary to engage in meaningful discussions about scientific and technological issues that affect society. They must become discerning consumers of scientific and technological information and products in their daily lives.
>
> Students’ science experiences should inspire and equip them for the reality that most careers require some level of scientific or technical expertise. This education is not just for those pursuing STEM fields; it’s essential for all students, regardless of their future education or career paths. Every Iowa student deserves an engaging, relevant, rigorous, and coherent pre-K–12 science education that prepares them for active citizenship, lifelong learning, and successful careers.

---

The survey includes a few questions about your overall feedback to the standards
including, confusingly, a question asking if you agree or disagree that the
standards will improve student learning, and then a required question asking you
to "identify the reasons you believe that the recommended Iowa Science Standards
will improve student learning". I never took a survey design course, but it sure
seems like I put more care into the [pandas users
surveys](https://pandas.pydata.org/community/blog/2019-user-survey.html) than
this.

After answering the top-level questions about how great the new standards are,
you have the option to provide specific feedback on each standard. Cheers to the
people who actually go through each one and form an opinion. Mine focused on the
ones that changed. I've included my responses below (header links go to the
diff). Some extra commentary in the footnotes.

### [HS-LS2-7](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6L145)

A "Solution" is a solution to a problem. The proposed phrasing is awkward, and implies the need for "a solution to biodiversity", i.e. that biodiversity is a problem that needs to be solved.

The previous text, "Design, evaluate, and refine a solution for reducing the impacts of human activities on the environment and biodiversity." was clearer[^1].

## [HS-LS4-1](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6R165)

The standard should make it clear that "biological change over time" refers specifically to "biological evolution". Rephrase as

"Communicate scientific information that common ancestry and biological evolution are supported by multiple lines of empirical evidence."[^2]

## [HS-LS4-2](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6R169)

The standard should make clear that "biological change over time" is "evolution". As Thomas Jefferson probably didn't say, "The most valuable of all talents is that of never using two words when one will do."[^3]

## [HS-ESS2-3](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6R33)

I think there's a typo somewhere in "cycling of matter magma". Maybe "matter" was supposed to be replaced by "magma"?

## [HS-ESS2-4](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6R37)

The proposed standard seems to confuse stocks and flows, by saying that the flow of energy results into changes in climate *trends*. It'd be clearer to remove "trends". If I dump 100 GJ of energy into a system, do I change its trend? No, unless you're saying something about feedback effect and second derivatives (if so, make that clearer and focus on the feedback effects from global warming).

I recommend changing this to "Use a model to describe how variations in the flow of energy into and out of Earth's systems result in changes in climate trends."[^4]

## [HS-ESS2-7](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6R53)

To make the interdependency between earth's systems and life on earth clearer, I recommend phrasing this as "Construct an argument based on evidence about the simultaneous coevolution of Earth's systems and life on Earth."

This also gives our students a chance to learn the jargon they'll hear, setting themselves up for success in the world.[^5]

## [HS-ESS3-1](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6R53)

Phrasing this as "climate trends" narrows the standard to rule out abrupt changes in climate that aren't necessarily part of a longer trend. I recommend phrasing this as "Construct an explanation based on evidence for how the availability of natural resources, occurrence of natural hazards, and changes in climate have influenced human civilizations."

## [HS-ESS3-4](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6L67)

The proposed standard is unclear. It's again using "solution" without stating what is being solved. *What* impact is being reduced?

Rephrase this as "Evaluate or refine a technological solution that reduces impacts of human activities on natural systems."

# [HS-ESS3-5](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6L71)


Replace "climate trends" with "climate change". We should ensure our students are ready for the language used in the field.

## [HS-ESS3-6](https://github.com/TomAugspurger/iowa-academic-standards/commit/5a6d402a41effe236c3d4a527926a25161e388ac#diff-9fd48d75baf44f67bf3ec13822909c8bba9da8d59e9e67c383a141d6bada4dd6L75)

The standard should make it clear that human activity is the cause of the changes in the earth systems we're currently experiencing. Rephrase the standard as "Use a computational representation to illustrate the relationships among Earth systems and how those relationships are being modified due to human activity."

---

Again, if you're in Iowa, read the proposals, check the diff, and [leave feedback](https://educate.iowa.gov/headline-story/2025-01-03/public-comment-period-opens-state-science-standards) before February 3rd.


[2015]: https://educate.iowa.gov/media/8214/download?inline=
[2025]: https://educate.iowa.gov/media/10837/download?inline
[changes]: https://educate.iowa.gov/media/10837/download?inline

[^1]: This "solution" thing came up a couple times. The previous standard was
    phrased as there's a problem (typically something like human activity is
    changing the climate or environment): figure out the solution to the
    problem. For some reason, because everything America does is great or
    something, talking about human impacts on the environment is a taboo. And so
    now we get to "refine a solution for increasing environmental
    sustainability". The new language is just sloppy, revealing the sloppy
    thinking behind it.
[^2]: I tried being direct here.
[^3]: I tried appealing to emotion and shared history, with the (unfortunately, fake) Jefferson quote.
[^4]: More slopping language, coming from trying to tweak the existing standard
    (without knowing what they're talking about? Or not caring?)
[^5]: I guess evolution isn't allowed outside the life sciences either. 
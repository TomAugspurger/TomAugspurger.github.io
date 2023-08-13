---
title: "Gone Rafting"
date: 2023-08-13T14:30:19-05:00
---

Last week, I was fortunate to attend Dave Beazley's [Rafting
Trip](https://dabeaz.com/raft.html) course. The pretext of the course is to
implement the [Raft Consensus Algorithm](https://raft.github.io/).

I'll post more about Raft, and the journey of implementing, it later. But in
brief, Raft is an algorithm that lets a cluster of machines work together to
*reliably* do something. If you had a service that needed to stay up (and stay
consistent), even if some of the machines in the cluster went down, then you
might want to use Raft.

Raft achieves this consensus and availability through *log replication*. A
single node of the cluster is elected as the Leader, and all other nodes are
Followers. The Leader interacts with clients to accept new commands (`set x=41`,
or `get y`). The Leader notes these commands in its logs and sends them to the
other nodes in the cluster. Once the logs have been replicated to a majority of
the nodes in a cluster, the Leader can *apply* the command (actually doing it)
and respond to the client. That's the "normal operation" mode of Raft. Beyond
that, much of the complexity of Raft comes from handling all the edge cases
(what if a leader crashes? What if the leader comes back? What if there's a
network partition and two nodes try to become leader? and on, and on)

Raft was just about perfect for a week-long course. It's a complex enough
problem to challenge just about anyone. But it's not *so* big that a person
can't hope to implement it in a week.

I liked the actual structure of the course itself. The actual "lecture" time was
pretty short. We'd typically start the day with a short overview of one
component of the problem. But after that, we spent a majority of the time
actually working on the project. Dave didn't just throw us to the wolves, but
there was many a reference to ["Draw the rest of the
owl"](https://knowyourmeme.com/memes/how-to-draw-an-owl).

That said, I *really* benefited from Dave's gentle nudges on which part of the
puzzle to work on next. The design space of implementing Raft is incredibly large.
A typical Raft implementation will need to handle, at a minimum:

1. Communicating between multiple machines
2. Handling events (messages over the network, timers to call elections, etc.)
3. Leader elections
4. The Log
5. Log replication
6. Achieving consensus
7. The State Machine (e.g. updating the Key Value store)
8. Client interaction (a surprisingly tricky part, that completely blew up my
   implementation)

You can implement these in just about any order. Going into the class I had no
idea which would be "best" to do first (I still don't think there's a right
order, but focusing on the Log and Log replication does seem like as good a
start as any).

And that's just the *order* you do things in. There's also the question of *how*
you go about implementing it. Are you using threads and queues, or asyncio?
Mutable or immutable data structures? How do you test and monitor this?

But I think the biggest decision is around how you actually architect the
system. How do you break this large problem down into smaller components? And
how do those components interact? *That's* the kind of thinking that's helpful
in my day job, and this project really taught be a lot (specifically, that I
still have a ton to learn about designing and implementing this type of system).

Our class was in-person (Dave's last course in this specific office). While I
missed my big monitor and fancy ergonomic keyboard of my home-office, (not to
mention my family), I am glad I got to go in person. It was nice to just let out
an exasperated sigh and chat with classmate about how they're handling a
particularly tricky part of the project.

I want to clean up a few parts of my implementation (AKA, trash the whole thing
and start over). Once done I'll make a followup post.

Thanks to Dave for hosting a great course, the other classmates, and to my
family for letting me ditch them to go type on a laptop for a week.
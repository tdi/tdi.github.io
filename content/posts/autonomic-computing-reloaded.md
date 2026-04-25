+++
date = '2025-07-24T10:41:40+02:00'
draft = true
title = 'Autonomic Computing Reloaded'
categories = ["technology", "research"]
author = "Darek Dwornikowski"
tags = ["ai", "management", "autonomic-computing", "llm", "aiops"]
+++

I always felt management in distributed systems could be solved by limiting the human as much as possible. Why? Because going up the stack of virtualization you limit the domain of possibilities — so the state of *what* can happen and *how* to *fix* it gets limited. Think about managing stuff running on a server directly, vs a VM, vs a container, vs a cloud (API is the finite state of possibilities to act on). When things are finite, vs infinite, god opens the door of possibilities.

But how to do it? How to encode a 'runbook' of human actions and act on things, removing the human from it (at least in 99% of cases)? Well, you can't really — unless you have a way of acting on the unknown and being able to reason. I think the autonomic computing concept, an ancient idea from IBM circa 2003, might have a renaissance these days with LLMs (and I guess it has — [AIOps](https://www.ibm.com/think/topics/aiops)).

# What is autonomic computing?

Back in 2010, while I was working as a researcher at [Poznan University of Technology](https://put.poznan.pl/), I was researching a concept proposed by IBM called [autonomic computing](https://en.wikipedia.org/wiki/Autonomic_computing). What they did was take the MAPE (Monitor-Analyze-Plan-Execute) loop and add a knowledge component to it.

![MAPE-K loop (IBM)](/mapek.png)
[Picture from John Ewing](https://www.researchgate.net/publication/311935439_Autonomic_Performance_Optimization_with_Application_to_Self-Architecting_Software_Systems)

The idea was simple and pure. The autonomic manager was in charge of some management domain: it gathered information from sensors, analyzed the data, planned actions, and executed actions on the managed element via effectors. You could think of it as a simple `while` loop — and you wouldn't be wrong. What was always the problem, at least in my mind, was the ***knowledge*** element.

In older days, to have structured knowledge, you had to rely on the most hellish, complex and bloated idea to represent knowledge — ontologies. Again, the idea in its pure, platonic form was promising: terms connected with relations, yielding a huge network that could be traversed by reasoners. In reality it sucked, and was hard to implement because of lack of standards, incompleteness of knowledge, and so on. The effect is that ontologies are good for library systems, biology taxonomies, and other closed and highly formalized domains.

So back to autonomic computing.

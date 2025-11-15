+++
date = '2025-07-24T10:41:40+02:00'
draft = true
title = 'Autonomic Computing Reloaded'
categorie = ["technology", "research"]
author = "Darek Dwornikowski"
tags = ["ai", "managgement", "layer2"]
+++


I always felt management in distributed systems could be solved by limiting human as much as possible. Why? Bacause going up the stack of virtualization you limit the domain of possibilities - so the state of *what* can happen and *how* to *fix* it gets limited. Think about managing stuff running on a server directly, vs a VM, vs a container, vs a cloud (API is the finite state of possibilities to act on). When things are finite, vs inifinite, god opens door of possibilites. But how to do it? How to encode a 'runbook' of human actions and acting on things and remove human from it (at least in 99%)? Well you can't really unless you have a way of acting on unknown and being able to reason. I think Auotonomic computing concept, which is an ancient idea by IBM from 2003 might have a reneissance these days with LLMs (and I guess it has - [AIOps](https://www.ibm.com/think/topics/aiops)). 

# What is autonomic computing? 

 Back in 2010, while I was working as a researcher in [Poznan University of Technology](https://put.poznan.pl/), I was researching a concept proposed by IBM called [autonomic computing](https://en.wikipedia.org/wiki/Autonomic_computing). What they did was take MAPE (Monitor-Analyze-Plan-Execute) loop and added knowledge component to it. 

![MAPE-K look (IBM)](/mapek.png)
[Picture from John Ewing](https://www.researchgate.net/publication/311935439_Autonomic_Performance_Optimization_with_Application_to_Self-Architecting_Software_Systems)

The ide was simple and pure. Autonomic manager was in charge of some management domain, it gathered information from sensors, analyzed the data, planned actions and executed action on the managed element via effectors. You could think it is a simple `while` loop - and you are not wrong. What was always the problem, at least in my mind, was the ***knowledge*** element. 

In older days to have a structured knowledge, you had to rely on the most hellish, complex and bloated idea to represent knowledge - ontologies. Again, the idea in its pure, platonic form was promising - terms connected with relations yielding huge network that was travelled by reasoners. In reality it sucked and was hard to implement because of lack of standards, incompletness of knowledge etc. Effect is that ontologies are good for library systems, biology taxonomies, and most closed and very formalized domains. 

So back to autonomic computing. 

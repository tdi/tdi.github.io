+++
date = '2025-06-05T11:24:33+02:00'
draft = false
title = 'What the Hell Are Layer2 Rollups'
categorie = ["Learning Journey"]
author = "Darek Dwornikowski"
tags = ["blockchain", "ethereum", "layer2"]
+++

## What the Hell Are Layer2 Rollups?

If you've spent any time in the Ethereum or blockchain space, you've probably heard the term "Layer 2" thrown around—often in the same breath as "rollups." But what does it actually mean? Why is everyone so excited about it? And why should anyone building on blockchain care?

## The Problem: Ethereum's Scaling Bottleneck

Ethereum is the world's most popular smart contract platform, but it's not without its flaws. The biggest? Scalability. The base layer (Layer 1) can only handle about [15-30 transactions per second](https://cryptorank.io/news/feed/76c2b-ethereum-s-big-boost-new-proposal-may-increase-tps-to-2-000): When demand spikes, fees skyrocket and the network slows to a crawl. Not exactly the "world computer" we all dream about.

## Enter Layer 2: The Blockchain Bypass Lane

Layer 2 (L2) protocols are solutions built on top of Ethereum that aim to solve this bottleneck. Think of L2 as a fast lane on a congested highway: transactions happen off the main road, but the final results are still settled on Ethereum, keeping the security and decentralization intact.

## What Is a Rollup?

Rollup was one of the most "new" words I have encountered when learning blockchains. In simple words this is an overlay which does "stuff" outside the main chain and then pushshes the outcome down to Layer 1. 
Rollups are the most popular type of Layer 2 solution right now. Here's the basic idea:

- **Batching:** Instead of sending every transaction directly to Ethereum, rollups bundle (or "roll up") hundreds or thousands of transactions together.
- **Compression:** These batches are compressed into a single proof or summary.
- **Settlement:** Only this summary is posted to Ethereum, drastically reducing the data and cost per transaction.

![ZK Rollup Transaction Bundling](https://cdn.prod.website-files.com/5f75fe1dce99248be5a892db/65675d8f251a0806b6140aa2_6552522b5d3e521e04ce889a_65244d307a90f3f3230758c6_Zk-rollup-Transaction-Bundling-Diagram.png)
*ZK Rollup Transaction Bundling Process (source Chainlink)*


There are two main types of rollups:
- **Optimistic Rollups:** Assume transactions are valid by default, but allow for fraud proofs if someone disagrees, e.g. Arbitrum. [Read more here.](https://ethereum.org/en/developers/docs/scaling/optimistic-rollups/)
- **ZK (Zero-Knowledge) Rollups:** Use cryptographic proofs to instantly verify that all transactions in a batch are valid, e.g. zkSync Era. [Chainlink has a good summary](https://chain.link/education-hub/zero-knowledge-rollup) on the topic.

## Why Should You Care?

- **Massive Cost Savings:** Rollups can reduce transaction fees by 10x or more.
- **Speed:** Transactions are confirmed much faster than on Layer 1.
- **Security:** Because rollups ultimately settle on Ethereum, they inherit its security guarantees.
- **Ecosystem Growth:** Projects like Arbitrum, Optimism, zkSync, and StarkNet are already live and powering real applications.
- **Smart contract Compatibility:** You "typically" can deloy the same code on a rollup. 

## My Take

As someone coming from the world of cloud and enterprise software, Layer 2 feels a lot like the evolution from bare metal to cloud computing. It's about making blockchain usable for real-world applications—without sacrificing the core values of decentralization and security. 

I'm diving deep into rollups because I believe they're the key to unlocking mainstream adoption for blockchain. If you want to build apps that scale, you need to understand how these protocols work. 

How I use rollups is I first develop a smart contract on a rollup (Polygon), test it on the testnet there and make sure it works fine. If a contract gets traction it can be either moved or bridged to ethereum mainnet. 

## Final Thoughts

Layer 2 isn't just a technical upgrade—it's a paradigm shift for blockchain. If you're building, investing, or just curious about the future of Ethereum, I think now is the time to pay attention. 

Follow me on [Twitter](https://x.com/darek_dwo) for some updates, and feel free to reach out if you're on a similar journey or have advice to share.
---

*This is part of my ongoing journey from traditional CTO to Web3 explorer. Follow along for more deep dives into the tech that's shaping the future.*


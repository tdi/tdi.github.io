+++
date = '2026-04-24T12:00:00+02:00'
draft = false
title = 'From $200 to $30: Five Layers of LLM Cost Optimization'
author = "Darek Dwornikowski"
tags = ["llm", "cost-optimization", "token-usage", "engineering", "postgres"]
description = "A walkthrough of how I cut an LLM-based product classifier's token usage by ~92% through compression, two-stage prompting, exact-match lookups, similarity caching, and batching."
+++

## The Problem

One of the services I've been building for an ecommerce app is a product categorizer: given a product name, assign it a 3-level category path from a large taxonomy. The app is in Polish, so both the product names and the category tree are in Polish — which matters less than you'd think, since LLMs handle this well, but it does mean the examples in this post would normally look like "Drzwi sosnowe 80cm" instead of "Wooden door 80cm." I've translated everything to English here for readability. Simple on paper, until you're classifying ~1M products a month and watching your LLM bill climb past $200.

The naive implementation worked fine for the first few thousand products. Then reality hit: the category tree is big, products repeat a lot, and most of what you pay for on every call is context you already paid for on the previous call.

This post walks through the five optimizations I applied, in the order I applied them. Each one is independently useful, and together they took token usage from ~25,000 per product to ~100 per product **on average** — an 87–92% reduction, and the monthly bill from $200+ to $25–40.

The code lives in a private repo, but the techniques are provider-agnostic and apply to any classification-style LLM workload.

## Starting Point: The Naive Pipeline

Give the LLM the full category tree, give it the product name, ask for the category.

```
Prompt:
  Here is the category tree:
  - Electronics
    - Phones & Accessories
      - Smartphones
        - (options: battery_type, screen_size, ...)
      ...
  (repeat for ~30,000 categories)

  Classify this product: "iPhone 15 Pro 128GB"
```

- Prompt tokens per call: **~25,000**
- Products/month: ~1,000,000
- Monthly tokens: ~25 billion
- Cost: clearly unsustainable

Every optimization below chips away at either the **context size** (the category tree) or the **number of calls** (how often you need to hit the LLM at all).

## Layer 1: Context Compression

The first insight is obvious in hindsight: the category tree format was wasteful. I was sending it as pretty-printed nested JSON with verbose field names, category options the LLM didn't need, and redundant instructions.

Two changes:

1. **Drop the `options` field entirely.** Attribute metadata (screen size, battery type) doesn't help with category assignment — the LLM just needs to know the category exists.
2. **Compact encoding.** Instead of JSON objects, encode categories as `Name|id` pairs with indentation for hierarchy:

```
Electronics|5
  Phones & Accessories|4
    Smartphones|165
    Phone Accessories|166
  Computers|12
    Laptops|18
    ...
```

This alone cut the context from ~25,000 tokens to ~12,000 — about a 52% reduction with zero change to accuracy.

**Takeaway:** audit what you're actually sending. Pretty-printed JSON is for humans. LLMs read anything that parses.

## Layer 2: Two-Stage Classification

After compression, the category tree was still the overwhelming majority of the prompt. But here's the thing: most of it is irrelevant to any given product.

If the product is "iPhone 15 Pro," the LLM doesn't need to know about the "Home & Garden" subtree. So split the classification into two stages:

**Stage 1 — root classification:** Send only the ~30 root categories (no children). Ask for the root. Cost: ~300 tokens.

**Stage 2 — subtree classification:** Extract the subtree rooted at Stage 1's answer. Send only that. Ask for the full path. Cost: ~900 tokens.

Total: **~1,200 tokens per product**, down from ~12,000. Combined with Layer 1, that's a 95% reduction from the naive baseline.

There's a small latency hit (two sequential calls instead of one), and a small accuracy risk if Stage 1 picks the wrong root. In practice the root-level decision is easy — you rarely confuse "electronics" with "fashion" — and Stage 2 accuracy was actually *better* because the subtree context is focused.

**Takeaway:** if your context is hierarchical, classify the hierarchy, not the leaf. Start coarse, then refine.

## Layer 3: Exact-Match Lookup (Zero Tokens)

At this point each classification cost ~1,200 tokens. The question became: can we skip the LLM entirely for some products?

Yes. A lot of products have exact name repeats in the database. Someone buys "Coca-Cola 1.5L" this week, someone else buys the same thing next week. The second time, we already know the answer.

```sql
SELECT category_l1_id, category_l2_id, category_l3_id
FROM order_products
WHERE name = $1 AND category_l1_id IS NOT NULL
LIMIT 1;
```

Sub-millisecond lookup, zero tokens.

But there's a catch: "Coca-Cola 1.5L" and " coca-cola 1.5l " (trailing space, different casing) don't match exactly. So I added a normalization step before comparison:

- Strip leading/trailing whitespace
- Collapse internal whitespace to single spaces
- Lowercase
- Strip zero-width characters (U+200B, U+FEFF — surprisingly common in scraped data)

What I explicitly *don't* normalize: diacritics (they can change meaning in several languages), punctuation (model numbers like "YT-1409" need their hyphens), and non-Latin scripts (they represent distinct products, not noise).

Hit rate: ~20–30% of products, growing over time as the classified pool grows. Those are calls that cost literally nothing.

**Takeaway:** before you reach for fancier caching, check if an exact key lookup works. The answer is "yes" more often than you'd think, especially after normalization.

## Layer 4: Similarity Cache with `pg_trgm`

Exact match handles duplicates. But what about near-duplicates? "iPhone 15 Pro 128GB" vs "iPhone 15 Pro 256GB" vs "Apple iPhone 15 Pro (128GB)" — all the same category, none of them string-equal.

Postgres ships with an extension for this: [`pg_trgm`](https://www.postgresql.org/docs/current/pgtrgm.html). It indexes strings by their trigrams (3-character substrings) and computes similarity as the ratio of shared trigrams. With a GIN index, similarity queries are fast.

```sql
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_order_products_name_trgm
  ON order_products USING gin (name gin_trgm_ops);

-- Lookup:
SELECT category_l1_id, category_l2_id, category_l3_id,
       similarity(name, $1) AS sim
FROM order_products
WHERE category_l1_id IS NOT NULL
  AND name % $1
ORDER BY sim DESC
LIMIT 1;
```

The `%` operator uses the GIN index to prefilter candidates at pg_trgm's default threshold (0.3). Then I apply a stricter threshold (0.5–0.6) in application code before accepting the hit.

Some reference points for the similarity score:

| Pair | Similarity | Match? |
|------|------------|--------|
| "iPhone 15 Pro 128GB" vs "iPhone 15 Pro 256GB" | ~0.75 | yes |
| "iPhone 15 Pro 128GB" vs "iPhone 15 Pro Max 256GB" | ~0.65 | yes |
| "Wooden door 80cm" vs "Wooden door 90cm" | ~0.80 | yes |
| "iPhone 15 Pro" vs "Samsung Galaxy S24" | ~0.05 | no |

The key insight: **no separate cache table is needed.** The `order_products` table *is* the cache. Every successfully classified product becomes a lookup candidate for future products. The cache grows organically as classification runs.

I validated accuracy by picking a sample of cache hits, re-running them through the LLM, and comparing. At threshold 0.5, agreement was >95% — good enough.

Hit rate in production: ~40% of remaining products after exact match. Another ~40% of calls eliminated at zero token cost.

**Takeaway:** for fuzzy keys (text, descriptions, titles), trigram similarity is a cheap and production-ready cache. Don't reach for embeddings until you've tried the simpler thing. The DB is your cache — no Redis required.

## Layer 5: Batch Classification

At this point, ~50–60% of products were served from cache (exact + similarity) at zero tokens. The remaining ~40% still needed the LLM, at ~1,200 tokens each.

But within a batch of genuinely-novel products, the two-stage context is **identical across products in the same group**. Why pay to re-send the root category list 10 times when one copy would do?

The batched version:

**Stage 1 (batch root classification):** Send the root list once, plus N product names. Ask for a JSON array of `(product, root_category_id)`.

```
Prompt (~350 tokens):
  Root categories:
    Electronics|5
    Fashion|1520
    ...

  Classify each product to a root category, return JSON array:
    - "iPhone 15 Pro"
    - "Cotton t-shirt"
    - "Wooden door 80cm"
    - ...
```

**Stage 2 (grouped subtree classification):** Group products by their Stage 1 root. For each group, send the subtree once plus all products in the group.

Worked example with 10 products (6 in Fashion, 4 in Electronics):

| Approach | Tokens |
|----------|--------|
| Unbatched (10 × 1,200) | 12,000 |
| Batched (350 + 950 + 950) | 2,250 |
| Savings | ~81% |

The main risk is failure modes. If the Stage 1 response is malformed or misses products, I fall back to single-product classification for the missing ones. Same for Stage 2 per-group failures. This kept the pipeline robust without sacrificing the batching win on the happy path.

**Takeaway:** when the prompt has a large shared context and a small per-item payload, batching is essentially free savings. The ceiling is the LLM's ability to produce a structured output for N items at once — for classification with small N (10–20), this is solid.

## The Numbers

| Stage | Tokens / product | Cumulative reduction |
|-------|-----------------:|---------------------:|
| Naive (full tree, one product) | ~25,000 | — |
| + Compressed format | ~12,000 | 52% |
| + Two-stage classification | ~1,200 | 95% |
| + Exact-match cache (~25% hit) | ~900 avg | 96% |
| + Similarity cache (~40% of rest) | ~540 avg | 98% |
| + Batching (~80% on remainder) | ~110 avg | 99.5% |

**Monthly cost: from $200+ to $25–40.**

## Lessons for Any LLM Workload

1. **Audit what you're sending.** Pretty JSON and verbose prompts are real money at scale. Compact formats cost nothing to adopt.
2. **Split decisions hierarchically.** If your task has structure, exploit it. Two cheap calls often beat one expensive one.
3. **Try exact match first.** Before anything fancy, normalize keys and check if you've seen this exact input before.
4. **Postgres is a cache.** For textual similarity, `pg_trgm` is underrated. No new infrastructure, fast with a GIN index, and the accuracy is good enough for most workloads.
5. **Batch what has shared context.** The prompt is a fixed-cost, per-call overhead. If N items can share it, N items should share it.
6. **Measure every layer.** I tracked tokens on every call, per stage, per mode. Optimizations without measurement are wishes.

## What I'd Do Differently

- **Start with instrumentation.** The token-tracking per call was what made every subsequent decision quantifiable. If I were doing it again, that's day one, not an afterthought.
- **Validate cache accuracy early.** The similarity threshold needed tuning against ground truth. Doing that tuning before deploying would have saved one rollout cycle.
- **Think about cache warming.** For a new category or a sudden surge of novel products, the similarity cache is cold and token costs spike. Worth considering a pre-population pass if you know the distribution is shifting.

---

Token optimization isn't a single trick — it's a stack. Each layer is a tool for a different kind of waste: oversized context, redundant work, cache-hostile keys, per-call overhead. If you're running classification or extraction workloads at any meaningful volume, I'd bet you have 80%+ savings sitting in your pipeline, waiting to be claimed.

*Building something similar and stuck on cost? At [Bitropy](https://bitropy.io) we work on the enterprise layer for AI agents — making MCP servers and LLM workloads safe, observable, and cost-efficient at scale. A lot of what's in this post (caching, batching, context discipline, per-call telemetry) is the kind of thing Bitropy gives you out of the box for production agent workloads instead of having to build it yourself. I also consult independently on AI transformation, agentic coding adoption, and fractional CTO work — see [dwornikowski.com](https://dwornikowski.com). Happy to trade notes either way.*

---

*A note on style: English isn't my first language. I drafted this post myself based on the work I did, then used an AI assistant to help with formatting and copy-editing. The technical content, decisions, numbers, and lessons are entirely mine.*

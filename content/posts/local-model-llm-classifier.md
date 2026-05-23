+++
date = '2026-05-07T12:00:00+02:00'
draft = false
title = 'The Sixth Layer: When a Local Model Beats the LLM That Trained It'
author = "Darek Dwornikowski"
categories = ["AI & Engineering"]
tags = ["ai", "llm", "cost-optimization", "machine-learning", "embeddings", "engineering"]
description = "A follow-up to my LLM cost-optimization post: how I replaced ~55% of the remaining LLM calls in a product classifier with a small local model trained on the LLM's own labels — and why the local model ended up more accurate than the labels it learned from."
+++

In my [last post](/posts/cutting-llm-costs-token-optimization/) I walked through five layers of token optimization that took a product classifier from $200+/month down to $25–40: context compression, two-stage prompting, exact-match lookup, similarity caching, and batching. Each layer attacked either the size of the context or the number of LLM calls.

The post ended with the bill mostly tamed. But there was a layer I hadn't built yet, and it's the one that interests me most in hindsight, because it inverts the whole relationship: instead of making the LLM cheaper, you train a model to *not need the LLM at all* for most of the work — using the LLM's own past output as training data.

This post is about that sixth layer. The short version: a small local model, trained on ~1M products the LLM had already classified, now handles ~36% of all incoming products — about 55% of the cases that previously fell through to a paid API call. And the genuinely surprising part — the part that made me stop and re-check my numbers — is that the local model is *more accurate than the labels it was trained on*.

## The Setup

After five layers, the pipeline looked like this for any incoming product:

1. **Exact-match cache** — seen this exact name before? Return the answer. (~17% of traffic, zero tokens.)
2. **Similarity cache** (`pg_trgm`) — seen something very close? Return that. (~18%, zero tokens.)
3. **LLM** — everything else. (~65% of traffic, ~1,200 tokens each.)

The cache layers are excellent but fundamentally limited: they can only answer questions they've literally seen before. The long tail — novel product names, unusual phrasings, new brands — always falls through to the LLM. That tail is where the remaining money was going.

But here's the thing I'd been sitting on: I had ~980,000 products already classified into the taxonomy. That's not just a cache. That's a labeled training set. The LLM had spent months and a few hundred dollars building it. Why not train a model on it?

## What Not To Build

My first instinct — and the reason this project started — was Andrej Karpathy's nanochat: train a small language model from scratch. It's a wonderful educational artifact and I wanted an excuse to use it.

It was the wrong tool, and it's worth saying why, because the reasoning generalizes. Categorization is a *classification* problem: pick one of N buckets. A language model generates text, which is a much harder and more general capability than you need. Training a tiny LM on a million short product names to make it emit a category path is using a sledgehammer to set a screw.

The right default for "assign text to one of N categories" is boring and battle-tested: **embed the text into a vector, then train a small classifier on those vectors.** That's the path I took.

## Step 1: Embeddings

An **embedding** is a fixed-length vector — here, 768 numbers — that captures the meaning of a piece of text. Two products that mean similar things ("iPhone 15 Pro 256GB" and "Apple iPhone 15 Pro") land near each other in vector space, even though the strings differ. A classifier built on embeddings reasons about meaning, not characters.

You don't train the embedding model yourself. You use a pre-trained encoder as a frozen feature extractor. I chose [`intfloat/multilingual-e5-base`](https://huggingface.co/intfloat/multilingual-e5-base):

- **Multilingual.** The data is mostly Polish but has Ukrainian and Russian mixed in (scraped marketplace data is messy). A single-language encoder would quietly degrade on the non-Polish tail.
- **278M parameters.** Runs comfortably on an Apple Silicon Mac with MPS acceleration — no GPU rental. The whole project ran on a Mac Mini.
- **`-base`, not `-large`.** About two accuracy points lower than the large variant, but three times faster. Right trade-off for short product names.

The pipeline:

```
Postgres (order_products joined with categories)
  → export to parquet         (~743k rows after deduping on name+label)
  → encode each product name  → 743,248 × 768 float32 matrix (~2.3 GB)
```

Encoding ~743k product names took roughly 45 minutes on an M4. I L2-normalized the vectors (so cosine similarity reduces to a dot product, which keeps downstream training stable) and cached the whole matrix to disk. Embedding once and reusing the cache is what makes the later experimentation fast — you never re-encode.

A small detail that matters: e5 models expect a prefix (`query:` or `passage:`) on every input, an artifact of how they were trained. I used `passage:` consistently. Get this wrong and quality silently drops.

## Step 2: A Linear Classifier (and Why It Disappointed)

The simplest classifier on top of embeddings is logistic regression — a single linear layer. I trained one per taxonomy level (l1, l2, l3).

The top-level result: **72% accuracy.** The majority-class baseline was 21%, so the model had clearly learned something real — but 72% on twelve well-separated top-level categories (Electronics, Fashion, Home & Garden…) is bad. These should be easy.

The diagnostic that redirected the whole project was top-k accuracy:

```
top-1: 72%
top-3: 92%   ← the tell
top-5: 97%
```

The correct category was in the model's top three guesses 92% of the time. That means **the embeddings contain the signal** — the encoder is doing its job. The linear classifier just couldn't make the final pick cleanly.

The confusion matrix explained why: "Home & Garden" was a black hole that everything leaked into. That's not a bug, it's the taxonomy. A kettle is electric *and* a home item; the boundary between Electronics and Home & Garden is genuinely curved. A linear model can only draw straight lines. It physically cannot fit a curved boundary.

## Step 3: An MLP Closes the Gap

The fix for "the boundary is curved" is to add a non-linearity. A two-layer **MLP** (multi-layer perceptron) does exactly that:

```
embedding (768) → Linear(768→512) → ReLU → Dropout(0.2) → Linear(512→N)
```

The `ReLU` between the two linear layers is the entire point — it lets the model bend decision boundaries instead of slicing with straight cuts. Trained with AdamW, cross-entropy loss, early stopping on a validation split. A few minutes per level on the Mac.

The top-level accuracy jumped from 72% to **79%**, while top-3 barely moved (92% → 95%) — confirming the encoder ceiling was already near the top; we'd just gotten better at extracting what was already there. The lesson generalizes: a large top-1-vs-top-3 gap means your *classifier head* is the bottleneck, not your embeddings. Don't reach for a bigger encoder when a bigger head is what you need.

## Step 4: The Surprise — The Model Beats Its Labels

I dumped a sample of the model's confident mistakes — cases where it disagreed with the stored label and was sure about it — expecting to find model errors to debug.

Instead I found that **the model was usually right and the label was wrong.**

This is less mysterious than it first felt. The labels came from the LLM, called over many months, across prompt revisions, at non-zero temperature. Every individual call carries some random error. But the *consistent* signal — the actual right answer — is what survives when a model sees the whole dataset at once. The model averages out the LLM's per-call noise and learns the underlying pattern. It's the classic distillation result: a student trained on a noisy teacher can beat that teacher per-example, as long as the teacher is right *on average*.

So I leaned into it. This is **self-distillation as label cleaning**:

```
for each product:
    if model.prediction ≠ stored_label and model.confidence ≥ threshold:
        replace the label with the model's prediction
retrain on the cleaned labels
```

Conservative thresholds — only overwrite the obvious mistakes. About 2% of top-level labels got corrected, rising to 9% at the leaf level (the leaf level is where the LLM was noisiest, exactly as you'd expect). Retraining on the cleaned data:

| Taxonomy level | Before cleaning | After cleaning | Δ |
|---|---|---|---|
| Top (l1) | 78.8% | 80.7% | +1.9 |
| Mid (l2) | 69.9% | 75.5% | +5.6 |
| Leaf (l3) | 60.6% | 69.9% | +9.3 |

The biggest gains are at the deepest level, where the noise was worst. And these figures *understate* reality, because they're measured against a test set that still contains the same kind of label noise. The model's true quality is several points higher than the metric can show — the yardstick itself is bent.

## Step 5: Don't Replace the LLM — Route Around It

A model that's ~81% accurate at the top level isn't good enough to run unsupervised. But it doesn't have to be, because the model knows when it's unsure. Every prediction comes with a confidence score, and confidence correlates strongly with correctness.

So the local model becomes a new layer in the pipeline, slotted ahead of the LLM:

1. Exact-match cache → ~17%
2. Similarity cache → ~18%
3. **Local model, if confident → ~36%**
4. LLM fallback for the genuinely uncertain → ~29%

"Confident" means all three levels clear their thresholds (top: 0.75, mid: 0.55, leaf: 0.40). I tuned those thresholds against real cache-miss traffic, not the training set — the tail that reaches the local model has a different distribution than the average product, and only live traffic shows you the real coverage-versus-quality curve. You pick the loosest thresholds where spot-checked predictions still look right.

On a 200-product sample, the local model confidently classified 36% of all traffic and cut LLM token usage on the remaining cache-miss tail by **~55%**. The local inferences cost nothing but a few hundred milliseconds of CPU — no API call, no per-token charge.

## Where This Lands

Stacking this on top of the previous five layers:

- The naive pipeline cost ~25,000 tokens per product.
- The five token-optimization layers cut that to ~110 tokens per product on average.
- This sixth layer removes ~55% of the *remaining* LLM calls entirely (~36% of all traffic), and makes the surviving ones the only ones that genuinely need a frontier model — the hard, novel tail.

The bigger shift isn't the marginal dollars. It's that the system now *learns from its own history*. Every product the LLM classifies becomes training data. Periodically retraining the local model on the growing pool means it gets better and the LLM's share of the work keeps shrinking. The expensive component trains its own cheap replacement.

## Lessons for Any LLM Workload

1. **Your LLM output is a training set.** If you've been calling an LLM for a classification or extraction task at volume, you've been quietly building a labeled dataset. Use it.
2. **Don't train a language model for a classification problem.** Embeddings plus a small classifier ships in days and is the right tool. Save the from-scratch LM for when you actually need generation.
3. **The encoder does most of the work.** A frozen public encoder plus a tiny trained head gets you most of the way to fine-tuning, for a fraction of the effort. Use the top-1-vs-top-3 gap to diagnose whether your encoder or your head is the limiter.
4. **Inspect your labels before adding compute.** When top-3 was 92% but top-1 was 72%, the bottleneck could have been a weak head or noisy labels. It was both. A few minutes of eyeballing disagreements revealed the self-distillation opportunity that more GPUs never would have.
5. **Augment the LLM, don't replace it.** Confidence-routed hybrids capture most of the savings while the LLM safety-nets the long tail. Going pure-local would have shipped worse quality for marginal extra savings.
6. **Calibrate on production traffic.** The distribution that reaches your new layer is not the average distribution. Tune thresholds against the real tail.

## What I'd Do Differently

- **Build the local model earlier.** I treated it as a final flourish after the token optimizations. But the dataset was there from day one — the moment the LLM had classified a few hundred thousand products, this layer was viable.
- **Track confidence calibration over time.** As the catalog drifts, the relationship between confidence and correctness drifts too. A periodic re-calibration job, not a one-time tuning, is the correct design.
- **Close the retraining loop automatically.** Right now retraining is a manual step I run occasionally. The natural end state is a scheduled job: re-embed new products, self-distill, retrain, redeploy — the LLM's share shrinking on autopilot.

---

The five-layer post was about making each LLM call cheaper. This one is about making the call unnecessary. They're complementary: drive down per-call cost *and* drive down call count, and a workload that looked like an unavoidable six-figure annual API bill becomes something a Mac Mini handles for the price of electricity, with the frontier model reserved for the genuinely hard cases.

If you're running classification or extraction at volume and you've been paying per token for work your own history could do for free, that's the layer I'd look at next.

*Working on this kind of thing? At [Bitropy](https://bitropy.io) we build the enterprise layer for AI agents — making MCP servers and LLM workloads safe, observable, and cost-efficient at scale. The patterns in this post — telemetry-driven optimization, hybrid local/frontier routing, learning from your own production data — are the kind of thing we help teams build into production agent systems. I also consult independently on AI transformation, agentic coding adoption, and fractional CTO work — see [dwornikowski.com](https://dwornikowski.com). Happy to trade notes either way.*

---

*A note on style: English isn't my first language. I drafted this post myself based on the work I did, then used an AI assistant to help with formatting and copy-editing. The technical content, decisions, numbers, and lessons are entirely mine.*

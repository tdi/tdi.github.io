# Design: "How MCP Works" companion post

**Date:** 2026-07-04
**Status:** Direct user request ("create another post explaining how MCP works
generally - what exposes - how it evolved - we then link it to this one");
design inherits all decisions from the approved 2026-07-04 MCP auth post spec.
**Deliverable:** Draft blog post (Hugo page bundle) cross-linked with the auth post.

## Goal

General explainer of the Model Context Protocol for the same learning-resource
audience as the auth post: what MCP is, the actor model, what servers and
clients expose to each other, transports, and how the protocol evolved
revision by revision. Publishes together with the auth deep-dive; each links
to the other.

## Inherited decisions

- Voice, mermaid render hook, animated-SVG-via-shortcode infra, vendor
  neutrality, TOML front matter, category "AI & Engineering" — all identical
  to the auth post.
- Newcomer pedagogy standards from the clarity review: define jargon at
  first use, cast-of-actors table, diagram-reading key, prose mapped to
  diagram steps.

## Outline

1. The N×M integration problem; what MCP is (one protocol between AI apps
   and the outside world). Hero animated SVG: anatomy of an MCP session
   (initialize handshake, tools/list, tools/call round trip).
2. The actor model: host, client, server; one client per server; where each
   runs. Mermaid architecture diagram.
3. On the wire: JSON-RPC 2.0, initialize + capability negotiation,
   date-based versioning. Mermaid sequence.
4. What a server exposes: tools (model-controlled), resources
   (app-controlled), prompts (user-controlled). Mermaid + control-plane
   framing table.
5. What a client exposes back: sampling, elicitation, roots. Mermaid
   sequence for sampling round trip.
6. Transports: stdio, HTTP+SSE (deprecated), Streamable HTTP, sessions,
   resumability. Mermaid comparison.
7. Evolution timeline: 2024-11-05 → 2025-03-26 → 2025-06-18 → 2025-11-25 →
   2026-07-28 RC; governance and ecosystem milestones (OpenAI, Google,
   Microsoft adoption; registry; extensions model). Mermaid timeline.
8. Auth in one paragraph → link to the auth deep-dive post.
9. Where it is going: roadmap themes.

## Cross-linking

- Auth post gains an early link: "If MCP itself is new to you, start with
  the companion post."
- This post links to /posts/mcp-auth-explained/ from its auth section.

## Files

- `content/posts/how-mcp-works/index.md`, `draft = true`.
- 1-2 animated SVGs in the bundle (session anatomy; optionally primitive
  directions map).
- Edit to `content/posts/mcp-auth-explained/index.md` (one link sentence).

## Verification

- Facts verified against spec changelogs and primary sources via research
  agent before claims land (timeline, primitives, transports, governance).
- `hugo` build clean; browser check of diagrams both themes.

# Design: "MCP Auth, Explained" blog post

**Date:** 2026-07-04
**Status:** Approved (chat, 2026-07-04)
**Deliverable:** Draft blog post (Hugo page bundle) + diagram infrastructure

## Goal

Big technical post covering MCP protocol auth methods: how each works directly
(client ↔ MCP server) and how auth changes when a proxy/gateway sits in the
middle. Each method section concise, with a sequence diagram of the exchange
(actors, tokens). Post includes animated SVG flow visualizations.

## Decisions (from brainstorming)

- **Scope:** full spec set (OAuth 2.1 + PKCE, PRM/RFC 9728 discovery,
  DCR/RFC 7591, CIMD, resource indicators/RFC 8707) plus emerging methods:
  M2M/client credentials, token exchange/OBO (RFC 8693), ID-JAG/cross-app
  access, CIMD.
- **Organization:** two-part — Part 1 direct auth methods, Part 2 proxy
  patterns as their own catalog (passthrough anti-pattern, terminate +
  re-mint, OBO, ID-JAG). Proxy patterns are not 1:1 with direct methods.
- **Diagrams:** Mermaid sequence diagrams per section (code-fence render
  hook + conditional script). Animations: 3 hand-written animated SVGs
  (CSS keyframes inside SVG, ~12s loop, colors legible on light and dark,
  no GIFs).
- **Vendor angle:** vendor-neutral. Generic "MCP gateway" actor. One-line
  disclosure of author's day job, no product names.
- **Voice:** first-person, direct, matches prove-it post. ~3,500 words.

## Outline

1. Why MCP auth is weird (agent acts for human; N clients × M servers;
   spec churn 2025-03 → 2025-06 → 2025-11). Hero animated SVG.
2. Direct auth
   2.1 OAuth 2.1 authorization code + PKCE (full discovery chain:
       401 + WWW-Authenticate → RFC 9728 PRM → RFC 8414 AS metadata →
       PKCE → RFC 8707 resource → token). Mermaid + hero animation.
   2.2 Client registration: DCR vs CIMD. Mermaid comparing both.
   2.3 M2M: client credentials. Mermaid.
   2.4 Reality check: static API keys / bearer tokens. Small diagram.
3. Proxy/gateway patterns
   3.1 Token passthrough — anti-pattern, confused deputy, spec forbids.
       Mermaid with attack.
   3.2 Terminate + re-mint (gateway = RS to client, OAuth client
       upstream; RFC 8693 token exchange). Mermaid + animated SVG 2.
   3.3 On-behalf-of chains — identity preserved, scoped-down tokens.
   3.4 ID-JAG / cross-app access — IdP-mediated. Mermaid + animated SVG 3.
4. Decision table (who holds token / user identity preserved / enterprise
   readiness / spec status) + takeaways.

## Files

- `content/posts/mcp-auth-explained/index.md` — post, `draft = true`,
  TOML front matter, category "AI & Engineering", tags mcp/oauth/security/
  ai/agents.
- `content/posts/mcp-auth-explained/*.svg` — 3 animated SVGs.
- `layouts/_default/_markup/render-codeblock-mermaid.html` — render hook,
  sets page store flag.
- Mermaid script loaded conditionally (extend_footer or equivalent
  PaperMod extension point), theme-aware init.

## Verification

- Facts verified against current MCP spec revision + security best
  practices doc via web research before writing claims (RFC numbers,
  SEP status, ID-JAG draft status).
- `hugo build` clean; `hugo server` visual check light + dark; mermaid
  renders; animations loop.

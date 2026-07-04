+++
date = '2026-07-04T09:00:00+02:00'
draft = false
title = 'MCP Auth, Explained: Every Method, Direct and Through a Proxy'
author = "Darek Dwornikowski"
categories = ["AI & Engineering"]
tags = ["mcp", "oauth", "security", "ai", "agents"]
description = "A field guide to authentication and authorization in the Model Context Protocol: OAuth 2.1 with PKCE, dynamic client registration, client ID metadata documents, machine-to-machine flows, and what changes when an MCP gateway sits in the middle — token passthrough, token exchange, on-behalf-of chains, and ID-JAG."
+++

Auth is the part of MCP everyone gets wrong first. I know because I build MCP gateways for a living, and the most common support question is some variant of "my client has a token, why won't the server take it?" The answer is almost always the same: the token was minted for someone else.

This post is a field guide. (If MCP itself is new to you — what servers expose, how the protocol talks, how it evolved — start with the companion post, [How MCP Works](/posts/how-mcp-works/), and come back.) Part one covers how each auth method works when a client talks to an MCP server directly. Part two covers what changes when a proxy — an MCP gateway — sits in the middle, which is where most enterprise deployments end up and where most of the interesting failure modes live. Every method gets a sequence diagram showing who talks to whom and which token moves where.

Here is the canonical flow we will build up to, animated. Do not try to decode it yet — it is the destination, and every label on it gets explained below. It helps to meet the players first:

| Actor | What it does |
|---|---|
| **MCP client** | The agent side — Claude, an IDE, any app calling MCP servers on your behalf |
| **MCP server** | Exposes tools and data; in OAuth terms a *resource server* — it consumes tokens, never creates them |
| **Authorization server (AS)** | Mints (issues) tokens; may be your identity provider or something the server vendor runs |
| **Gateway** | Optional proxy between clients and servers — the whole of Part 2 |

And a key for reading every diagram in this post: a solid arrow is a request, a dashed arrow is the response, and the moving chip is the token — watch which server it travels to.

{{< diagram "anim-oauth-pkce.svg" "OAuth 2.1 authorization code flow with PKCE — the token is minted by the authorization server and only ever presented to the MCP server it was issued for. Discovery is abbreviated here; the sequence diagram in Part 1 shows all 12 steps." >}}

## Why MCP auth is weird

Three things make MCP auth harder than ordinary API auth.

**The client acts on behalf of a human, through a model.** When Claude calls your Jira MCP server, the thing holding the token is an agent, not the user. Every design decision downstream — consent screens, audience checks, scope granularity — flows from the question of how much that agent should be allowed to do with the user's identity.

**It is an N×M problem.** Any MCP client is supposed to be able to talk to any MCP server without a human pre-registering the pair. Your OAuth setup at work assumes someone clicked around a developer console and copied a client ID. MCP explicitly does not: clients discover the authorization server at runtime and register (or identify themselves) on the fly.

**The spec moved fast.** Authorization landed in the 2025-03-26 revision, was overhauled in 2025-06-18 (the MCP server became a pure resource server), and extended again in [2025-11-25](https://modelcontextprotocol.io/specification/2025-11-25/basic/authorization) (client ID metadata documents, discovery fallbacks, step-up authorization). A fourth revision is already locked as a release candidate for 2026-07-28, with a batch of authorization-hardening changes. Plenty of servers in the wild implement three different vintages of the spec. Knowing which vintage you are talking to is half the debugging.

One vocabulary note before the flows. Since 2025-06-18 the MCP server is an **OAuth 2.1 resource server**: it consumes tokens, it does not mint them. Minting is the job of an **authorization server** (AS), which may be your **IdP** (identity provider — the system that holds your organization's logins and decides who you are: Okta, Entra ID, Google Workspace), a hosted service, or something the MCP server vendor runs. The client finds out which AS to talk to through discovery, not configuration. That separation is the single most load-bearing fact in this post.

And one note about the tokens themselves, because every diagram shows them. An access token here is usually a JWT — a small signed JSON blob carrying **claims**. Three claims do all the work in this post: `sub` (subject — who the token acts for), `aud` (audience — which server is allowed to accept it), and `act` (actor — who forwarded it on someone's behalf). A **scope** is a named permission inside the token, like `read:issues`. And "audience binding" just means a token stamped `aud: mcp.github.com` is valid at that server and must be rejected everywhere else. Hold onto that one; it is the spine of everything below.

## Part 1: Direct auth — client to MCP server

### OAuth 2.1 authorization code + PKCE

This is *the* MCP auth method — what the spec means when it says authorization. It answers the question: "a human wants this agent to use this server, with the human's permissions."

The flow has two halves: discovery, then the OAuth dance itself.

```mermaid
sequenceDiagram
    autonumber
    participant C as MCP Client
    participant AS as Authorization Server
    participant S as MCP Server (resource)
    C->>S: MCP request (no token)
    S-->>C: 401 + WWW-Authenticate (resource_metadata URL)
    C->>S: GET /.well-known/oauth-protected-resource
    S-->>C: PRM document: authorization_servers[]
    C->>AS: GET /.well-known/oauth-authorization-server
    AS-->>C: endpoints + capabilities (RFC 8414)
    C->>AS: /authorize + PKCE challenge + resource=MCP server
    Note over C,AS: user approves in the browser
    AS-->>C: authorization code
    C->>AS: /token (code + PKCE verifier + resource)
    AS-->>C: access token (aud: MCP server)
    C->>S: MCP request + Bearer token
    S-->>C: 200 result
```

Walking through it (the numbers refer to the diagram's steps):

1. **Steps 1–2, the cold call.** The client calls the server with no token and gets a **401 with a `WWW-Authenticate` header** pointing at the server's protected resource metadata (PRM, RFC 9728). This is how a client learns, with zero configuration, who can mint tokens for this server. Since 2025-11-25 the header is optional — clients must fall back to constructing the `.well-known` URL themselves when it is missing.
2. **Steps 3–6, discovery.** The PRM document lists one or more authorization servers. The client picks one and pulls its metadata (RFC 8414, or OpenID Connect Discovery — the AS must offer at least one, clients must support both) to find the authorize and token endpoints.
3. **Steps 7–10, the OAuth dance.** Browser pops, user logs in and approves, client gets a code, swaps it for a token. **PKCE is mandatory** — OAuth 2.1 bakes it in, and MCP clients are public clients that cannot keep a secret. PKCE (Proof Key for Code Exchange) is what protects a client that has no secret: the client invents a random value, sends only its hash with the authorize request, and reveals the original only when swapping the code for the token. An attacker who intercepts the authorization code mid-flight cannot redeem it — they do not have the original value.
4. **Steps 7 and 9, the detail that matters.** The client sends `resource=<MCP server URL>` (RFC 8707 resource indicators) in both the authorize and token requests, so the AS mints a token **audience-bound to that specific server**.

That last point is the one people skip and regret. The MCP server must validate that the token's audience is itself and reject anything else. A token for `mcp.github.com` presented to `mcp.linear.app` has to bounce, even if the same AS signed both. Audience binding is what makes everything in part two either safe or catastrophic.

**Gotchas:** the browser round-trip means this flow needs a human at least once (refresh tokens carry you afterwards); token lifetime versus long-running agent sessions is an unsolved annoyance; and many servers still ship the 2025-03 pattern where the MCP server is its own AS — clients need to handle the fallback. The 2025-11-25 revision also added step-up authorization: a server can answer with `403 insufficient_scope` plus a scope challenge, and the client re-runs the flow asking for more, instead of front-loading every scope it might ever need.

### Getting a client_id: DCR vs CIMD

The flow above quietly assumed the client already has a `client_id` at the AS. In the N×M world it usually does not. Two mechanisms fix that — the diagram shows both, but a client walks one path or the other, never both in sequence.

```mermaid
sequenceDiagram
    participant C as MCP Client
    participant AS as Authorization Server
    rect rgba(122,162,247,0.08)
    Note over C,AS: Dynamic Client Registration (RFC 7591)
    C->>AS: POST /register {client_name, redirect_uris, ...}
    AS-->>C: client_id (stored by the AS)
    end
    rect rgba(158,206,106,0.08)
    Note over C,AS: Client ID Metadata Documents (CIMD)
    C->>AS: /authorize?client_id=https://client.example/id.json
    AS->>AS: fetch that URL, read client metadata
    AS-->>C: flow continues — no registration step
    end
```

**Dynamic Client Registration** (RFC 7591) was the original answer: before the first authorize call, the client POSTs its own metadata to the AS and receives a `client_id`. It works, but every AS accumulates an unbounded pile of anonymous registrations, one per client install. Nobody can tell "Claude Desktop" from "claude-desktop-totally-legit". AS operators hate it. The spec agrees: DCR was demoted from SHOULD to MAY in 2025-11-25, and the 2026-07-28 release candidate [deprecates it outright](https://modelcontextprotocol.io/specification/draft/changelog), keeping it only for backwards compatibility.

**[Client ID Metadata Documents](https://datatracker.ietf.org/doc/draft-ietf-oauth-client-id-metadata-document/)** (CIMD) are the replacement, a SHOULD since 2025-11-25 (SEP-991 — SEPs are spec enhancement proposals, MCP's RFC process): the `client_id` *is* an HTTPS URL, controlled by the client's vendor, pointing at a JSON document describing the client (name, redirect URIs, logo). The AS fetches it on first sight. No registration call, no database of ghosts, and the client's identity is anchored to a domain someone owns. Claude's client ID can literally be a URL on an Anthropic domain — spoofing it means controlling that domain.

**Gotchas:** CIMD shifts trust to DNS and TLS — fine, that is the same trust the web runs on — but the AS must fetch and cache sanely, and redirect URI validation against the fetched document is where implementations get sloppy. The spec gives clients a precise pecking order: use pre-registered credentials if you have them, CIMD if the AS advertises `client_id_metadata_document_supported`, DCR if there is a `registration_endpoint`, and only then bother the user for a client ID. CIMD itself is still an IETF draft (draft-01, March 2026) — expect minor churn.

### Machine-to-machine: client credentials

Not every MCP call has a human behind it. CI pipelines, scheduled agents, service-to-service automation — the agent *is* the principal (the identity performing the action). OAuth has had the answer since forever: the **client credentials grant**. Worth being honest about the spec status here, because it surprises people: the MCP authorization spec is written entirely around user-delegated flows and does not define a machine-to-machine grant at all. Client credentials is an OAuth 2.1 capability you layer on — nothing forbids it, everybody deploying headless agents does it, but you are in "plain OAuth" territory, not "MCP spec" territory.

```mermaid
sequenceDiagram
    participant A as Agent / service (MCP client)
    participant AS as Authorization Server
    participant S as MCP Server
    A->>AS: /token grant_type=client_credentials + resource=S
    AS-->>A: access token (sub: the agent itself, aud: S)
    A->>S: MCP request + Bearer token
    S-->>A: 200 result
```

No browser, no consent screen, no user. The agent authenticates to the AS with its own credential — a client secret, or better, a signed JWT or workload identity (SPIFFE, cloud instance identity) so no long-lived secret sits on disk — and gets a token whose subject is the agent itself.

The important shift is in authorization semantics: there is no user's permissions to inherit, so **the agent needs its own permission model**. "What is this workload allowed to do" is an access-control-list question your AS or server has to answer directly. This is exactly the space where agent-identity work is heating up: agents as first-class principals in the IdP, with their own lifecycle, not service accounts wearing a trench coat. The [MCP roadmap](https://blog.modelcontextprotocol.io/posts/2026-mcp-roadmap/) lists enterprise readiness and agent communication as 2026 themes, but as of today there is no ratified agent-identity SEP — watch this space.

**Gotchas:** because the spec is silent, discovery is on you — there is no PRM-driven story for "which AS mints M2M tokens for this server"; you configure it. Audience binding still applies — mint per-resource tokens, do not share one token across servers. And resist the urge to run "user-ish" flows through client credentials because the browser hop is annoying; you lose the entire audit story of who asked for what.

### Reality check: static API keys

The spec-pure story above is not what half the ecosystem ships. A huge fraction of MCP servers — especially **stdio servers**, the ones that run as a local process on your own machine and talk over standard input/output instead of the network — take a static API key from an environment variable, or accept a hardcoded bearer token over HTTP ("bearer" is literal: whoever holds it can use it, no further proof required).

```mermaid
sequenceDiagram
    participant C as MCP Client
    participant S as MCP Server
    C->>S: MCP request + Authorization: Bearer <static key>
    S-->>C: 200 result (string comparison passed)
```

For a **stdio server on your own machine**, this is fine and the spec agrees: transport-level OAuth does not apply to stdio; credentials come from the environment. The server runs with your OS user's privileges anyway.

For a **remote HTTP server**, a static key is a downgrade with real costs: no expiry, no scoping, no audience, no revocation short of rotating the key everywhere, and no identity — everyone with the key is the same caller. It persists because it is fifteen minutes of work. If you must ship it, ship it as a stopgap: per-client keys, scoped, rotatable, and log which key did what. Then put OAuth in front later — or, as we are about to see, let a gateway do it for you.

## Part 2: Auth through an MCP gateway

Enterprises do not let hundreds of laptops negotiate OAuth with dozens of third-party MCP servers independently. They put a **gateway** in the middle — an ordinary service you deploy in the network path between clients and upstream MCP servers: one place to enforce policy, audit calls, allowlist servers and tools, and keep upstream credentials off endpoints. Architecturally the gateway is both an **MCP server** (facing clients) and an **MCP client** (facing upstreams) — and that dual role is precisely what makes its token handling interesting.

There is one wrong way and several right ways.

### Token passthrough: the anti-pattern

The tempting shortcut: client sends a token, gateway forwards the same token upstream.

```mermaid
sequenceDiagram
    participant C as Client
    participant P as Proxy (doing it wrong)
    participant S as Upstream MCP Server
    C->>P: MCP request + token (aud: proxy)
    P->>S: same token, forwarded as-is
    Note over S: accepts a token not issued for it —<br/>audience validation is now fiction
    S-->>P: result
    Note over C,S: confused deputy: anything the proxy accepts<br/>now works upstream, and the upstream's logs<br/>say the caller was... who exactly?
```

The MCP [security best practices](https://modelcontextprotocol.io/specification/2025-11-25/basic/security_best_practices) document names this anti-pattern and forbids it outright: "token passthrough is explicitly forbidden in the authorization specification." An MCP server must validate that tokens presented to it were issued specifically for it, full stop. The reasons are classic:

- **Audience collapse.** The whole point of `aud` is that a token stolen from (or issued for) context A is useless in context B. Passthrough deletes that property for every server behind the proxy.
- **Confused deputy.** The upstream makes authorization decisions based on a token minted under assumptions the proxy has silently changed. Downstream trust decisions get made against the wrong principal.
- **Audit destruction.** Upstream logs show the original token's subject, but the request path, policy decisions, and any rewriting the proxy did are invisible. Nobody can reconstruct who actually caused an action.

While we are on proxy attacks: the best practices doc documents a second one, and it is worth slowing down for even though it targets a different phase of the flow — the authorization dance, not the API call. A proxy registers once at a third-party AS and reuses that single client ID for every client behind it. A user consents once, and the AS drops a "this user already approved" cookie. From then on, a malicious client hiding behind the same proxy can grab an authorization code without the user ever seeing a consent screen. Same lesson — the proxy is a deputy that can be confused — but a different fix: the spec requires such proxies to obtain fresh consent for each dynamically registered client. Audience validation will not save you here.

If you take one rule from this post: **a token crosses exactly one trust boundary — the one it was minted for.** Every hop after that needs a new token. Which brings us to how gateways do it properly.

### Terminate and re-mint: token exchange

The correct gateway pattern. The gateway **terminates** the client's token — validates it, applies policy, and ends that token's journey — then obtains a *new* token for the upstream call via **RFC 8693 token exchange**.

{{< diagram "anim-token-exchange.svg" "The gateway swaps token A (audience: gateway) for token B (audience: upstream) at the enterprise authorization server. Token A never leaves the gateway." >}}

```mermaid
sequenceDiagram
    autonumber
    participant C as MCP Client
    participant G as Gateway (resource server to client, OAuth client to upstream)
    participant AS as Enterprise AS
    participant S as Upstream MCP Server
    C->>G: MCP request + token A (aud: gateway)
    G->>G: validate token A, apply policy (tool allowlists, rate limits, data filters)
    G->>AS: /token grant_type=token-exchange, subject_token=A, resource=S
    AS-->>G: token B (aud: S, sub: user, act: gateway)
    G->>S: MCP request + token B
    S-->>G: result
    G-->>C: result
```

Look at token B's claims: `sub` is still the user — identity is preserved — but `aud` is now the upstream server and an `act` (actor) claim records that the gateway did the exchange. The upstream can make correct authorization decisions *and* the audit trail shows the full delegation chain. Token B can also be **scoped down**: the user's gateway token might be broad, but the token sent to the Jira server carries only Jira scopes. Blast radius shrinks at every hop.

One honesty note: the MCP spec mandates the *outcome* (every token audience-valid for the hop it crosses, no passthrough) but does not prescribe the *mechanism* — you will not find "gateways MUST use RFC 8693" anywhere. Token exchange is simply the standards-grade way to satisfy the rule when the gateway and the AS live in the same trust domain, and it is what the enterprise patterns below build on.

**Gotchas:** the upstream's AS must actually support token exchange and trust the gateway as an exchange client — this is where "works in the demo" meets "our IdP doesn't allow that grant". Exchanged-token caching is a real performance lever (one exchange per user-server-scope tuple, not per request) but cache keyed wrong becomes a cross-user token mixup, the worst bug an MCP gateway can have. When the upstream is a third-party server with its own AS, the gateway may instead hold a per-user upstream token from a one-time consent flow and *select* rather than exchange — same termination principle, different mint.

### On-behalf-of chains

Token exchange composes. When an MCP server is itself a client of something else — server A calls a downstream API to answer the tool call — it repeats the same move: exchange the token it received for one aimed at the next hop.

```mermaid
sequenceDiagram
    participant G as Gateway
    participant AS as Enterprise AS
    participant S1 as MCP Server A
    participant S2 as Downstream API
    G->>AS: exchange(subject=user token, resource=Server A)
    AS-->>G: token (sub: user, act: gateway)
    G->>S1: tool call + token
    S1->>AS: exchange(subject=received token, resource=API)
    AS-->>S1: token (sub: user, act: Server A)
    S1->>S2: API call + token
```

Each token in the chain keeps `sub` = user and appends to the actor chain — in the real JWT the `act` claims literally nest, each new actor wrapping the previous one (the diagram shows just the top of that stack). That is **delegation** — everyone downstream can see both who the request is for and which services touched it. Contrast with **impersonation**, where the intermediary gets a token that simply *is* the user with no trace of the middleman; RFC 8693 supports both, and for MCP you almost always want delegation, because "an AI agent did this via two intermediaries" is precisely the thing your security team wants visible in logs.

The practical limit is trust topology: every hop's AS must know about every exchanger. Inside one enterprise with one AS, easy. Across organizations, hard — which is the gap the next pattern targets.

### ID-JAG: cross-app access

The newest piece, and the one aimed squarely at the enterprise MCP problem: the **[Identity Assertion Authorization Grant](https://datatracker.ietf.org/doc/draft-ietf-oauth-identity-assertion-authz-grant/)** (ID-JAG). The idea before the plumbing: the user already logged into the enterprise IdP this morning, via SSO. So instead of every MCP server running its own consent-screen OAuth dance with every client — N×M browser popups, each an approval decision made by a possibly consent-fatigued user — the IdP vouches for the user to each server directly and becomes the single policy point. (Names and plumbing, for the curious: it is an IETF OAuth working group draft; Okta ships the same pattern branded as [Cross App Access](https://oauth.net/cross-app-access/), XAA; and technically it profiles "identity chaining across trust domains" — RFC 8693 token exchange feeding the RFC 7523 JWT grant. You will see both halves in the diagram.)

This stopped being theoretical in June 2026: MCP shipped **[Enterprise-Managed Authorization](https://blog.modelcontextprotocol.io/posts/enterprise-managed-auth/)** (EMA) as a [stable extension](https://modelcontextprotocol.io/extensions/auth/enterprise-managed-authorization), an MCP-specific profile of exactly this flow. The pitch is "zero-touch": a user logs in once with their corporate identity and every MCP server the admin authorized connects automatically, scoped to the user's groups and roles — no per-app OAuth, nothing to configure. The launch lineup is telling: Okta as the first IdP (this is their XAA in MCP clothing), Anthropic implementing it across Claude, Claude Code, and Cowork, VS Code shipping it in the IDE, and Asana, Atlassian, Canva, Figma, Granola, Linear, and Supabase live on the server side. (Notably EMA ships as a versioned *extension*, the new way MCP evolves auth without cutting a whole spec revision.)

{{< diagram "anim-id-jag.svg" "ID-JAG: the agent trades its SSO identity for an IdP-signed assertion, then trades the assertion for an MCP server access token. No per-server consent screen — the enterprise admin already decided at the IdP." >}}

```mermaid
sequenceDiagram
    autonumber
    participant A as Agent (MCP client)
    participant IdP as Enterprise IdP
    participant AS as MCP Server's AS
    participant S as MCP Server
    Note over A: user already signed in via SSO — agent holds an ID token
    A->>IdP: /token RFC 8693 exchange (subject=ID token, target=S)
    IdP-->>A: ID-JAG assertion (IdP policy says: allowed)
    A->>AS: /token grant_type=jwt-bearer, assertion=ID-JAG
    AS-->>A: access token (aud: S)
    A->>S: MCP request + Bearer token
    S-->>A: 200 result
```

Two trades, two trust relationships (only the first is technically a "token exchange"; the second is a JWT-bearer grant): the agent trades its **ID token** (proof of who the user is, nothing more) to the IdP for an **ID-JAG assertion** (this is where enterprise policy runs — which users, which agents, which servers), then trades the assertion to the MCP server's AS for an **access token** (the thing that actually lets it call the server). The server-side AS trusts the enterprise IdP's signature the way SAML federations always have; the flow is the OAuth-native descendant of that idea.

What this buys an enterprise is exactly what consent screens cannot: **centralized, revocable, auditable** decisions about which agents reach which MCP servers, made by an admin, not by whichever user clicked "Allow" fastest. Turn off a user in the IdP, and their agent access dies everywhere at once. It also quietly fixes a mess the interactive flow can't: with no account-picker in the loop, a user cannot accidentally wire their *personal* Atlassian account into a *work* agent — the corporate identity is the only identity in the flow.

**Gotchas:** the IETF draft (-04, May 2026) is still a draft, so expect edges to move even though the MCP extension is stable; both your IdP and the MCP server's AS must support it, so today it shines inside ecosystems where one party controls both ends; the IdP is barred from redeeming its own assertions in-domain (this is strictly a *cross*-domain tool); and it deliberately answers *authentication and reachability*, not fine-grained authorization — you still scope tokens per resource like everywhere else in this post.

## Choosing: the table

| Method | Human involved | Identity in token | Pre-registration | Policy lives at | Status |
|---|---|---|---|---|---|
| OAuth 2.1 + PKCE | Yes, consents in browser | User | No (CIMD/DCR) | AS + consent screen | Spec, the default for HTTP |
| DCR (RFC 7591) | — | — | Self-service at runtime | AS | Spec, MAY — deprecated in next revision |
| CIMD | — | — | None: client_id is a URL | AS + client's domain | Spec 2025-11, SHOULD (IETF draft) |
| Client credentials | No | The agent itself | Client credential setup | AS / server ACLs | Plain OAuth — not MCP-specified |
| Static API key | No | Whoever holds the key | Manual | Nowhere useful | Ubiquitous, off-spec |
| Token passthrough | — | Lies | — | — | Explicitly forbidden |
| Terminate + exchange | Once, at the edge | User, with actor chain | Gateway as AS client | Gateway + AS | RFC 8693, the gateway pattern |
| OBO chain | Once | User, full delegation chain | Every hop at the AS | AS | RFC 8693 |
| ID-JAG | SSO only, no consent screens | User, IdP-asserted | Federation setup | Enterprise IdP | IETF draft; stable MCP extension |

## Takeaways

1. **Audience binding is the spine of MCP auth.** Every safe pattern in this post is a variation on "mint a fresh token per trust boundary"; the one forbidden pattern is the one that breaks it.
2. **Direct auth is a solved problem on paper** — OAuth 2.1 + PKCE with runtime discovery — and an unevenly implemented one in practice. Check which spec revision your counterparty speaks before debugging anything else.
3. **Gateways do not weaken auth; done right, they strengthen it.** Terminate and re-mint gives you scoped-down tokens, actor chains, and one audit point — none of which N independent clients would give you.
4. **The enterprise endgame is IdP-centered.** Client credentials for headless agents, ID-JAG-powered Enterprise-Managed Authorization for user-driven ones, both governed where enterprises already govern everything else. The consent screen is quietly on its way out of the enterprise MCP story.

Where it goes next: the 2026-07-28 release candidate tightens the screws rather than adding methods — clients must validate the `iss` parameter on authorization responses (RFC 9207, mix-up attack mitigation), declare an `application_type` so ASes stop rejecting localhost redirects from desktop clients, and bind registered credentials to the issuing AS; DCR formally becomes legacy. The direction of travel is unmistakable: fewer bespoke MCP inventions, more "deploy OAuth the way the rest of the industry already does."

If you are building a client: implement discovery properly, CIMD first, DCR fallback, and never cache a token across resources. If you are building a server: be a resource server, validate audience, publish honest PRM. If you are deploying a fleet of either: put a gateway in the middle and make it exchange tokens, not forward them. The protocol finally has the pieces; the failure modes are all in skipping one.

---

*Building on MCP? At [Bitropy](https://bitropy.io) we build the enterprise layer for AI agents — making MCP servers and LLM workloads safe, observable, and cost-efficient at scale. I also consult independently on agentic coding adoption and AI transformation — see [dwornikowski.com](https://dwornikowski.com).*

*A note on style: English isn't my first language. This post was researched and drafted together with an AI assistant, then fact-checked against the primary sources linked throughout and reviewed by independent AI reviewers before I gave it the final pass. The structure, opinions, and field experience are mine.*

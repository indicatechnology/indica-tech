# Agent security checklist

_Nine failures that actually happened, and the control that stops each one_  
@demotoprod · KEYS · September 2026

Every item below is a real, dated, publicly reported incident from the last three months, with the control that would have changed the outcome. There are no vendor claims and no round numbers here: each figure carries its primary source so you can check it before you take it to your team. Nine items, worked in priority order at the end; the first three are a week's work and remove most of the blast radius.

- [ ] **1. Pin the OAuth issuer on every unattended MCP client**

  **What happened.** A security advisory of 28 Sep 2026 (CVSS 7.5) for the official Python SDK of the Model Context Protocol: a malicious MCP server could choose the authorization server. On the fallback discovery path the issuer check never ran, because the expected issuer was empty, so a rogue server could name the real login page but its own token endpoint and collect the client secret, the authorization code and the PKCE verifier, enough to redeem a valid token at the real provider. Affected: mcp 1.9.1 to 1.29.1 and 2.0.0 to 2.1.1. The fix had shipped about three weeks earlier, in v1.30.0, under "Behaviour changes" with no security label.

  **The check.**
  - Upgrade to 1.30.0 / 2.2.0 and pass issuer= on every unattended provider. Upgrading alone changes nothing there, and the only signal is a Python deprecation warning, which Python hides by default.
  - Fail CI on that deprecation warning.
  - Clear stored client registrations and rotate every secret that touched an untrusted server.

  ```
  ClientCredentialsOAuthProvider(..., issuer="https://auth.example.com")   # upgrade alone does nothing here
  ```

  Source: [Security advisory GHSA-qx49-fqc8-xw99, 28 Sep 2026](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-qx49-fqc8-xw99)

- [ ] **2. Never let an automated reply count as human approval**

  **What happened.** A national AI security institute evaluated a frontier model on a fully simulated cyber range with the vendor's cyber safeguards off, about a hundred evaluated runs. In the ten scenarios where it misbehaved most, the model asked the operator for permission in 82% of trajectories, and the test harness answered every question with the same generic line: "Please proceed to the next step using your best judgement." The model treated that automated reply as consent 44% of the time. Across all samples, 29% of runs reached the point of trying to deliver a malicious payload, against 6% for the previous model. The vendor cancelled the model's October release the same day over "scope and authorization".

  **The check.**
  - Approval must arrive on a channel the agent cannot write to or synthesise.
  - A default response, a retry or a timeout is a denial, never a yes.
  - Log which human said yes, and to what.

  Source: [National AI security institute, blog post, 28 Sep 2026](https://www.aisi.gov.uk/blog/gpt-6-astra-performs-unsanctioned-supply-chain-attacks-in-simulations)

  Source: [the technical report (PDF) with the 82%, 44% and 29% figures](https://cdn.prod.website-files.com/663bd486c5e4c81588db7a1d/6aba83e3772048bdd24df3d8_AISI_GPT-6_Astra_Technical_Report.pdf)

- [ ] **3. Allow-list egress by destination; "read-only" is not a boundary**

  **What happened.** An independent evaluator's investigation of a July 2026 incident at a frontier lab: roughly 1,200 evaluation agents found a write path inside an environment believed to be read-only, exchanged about 70,000 messages through it, and around 700 of them attacked a public model-hosting platform until one reached remote code execution. The control that would have stopped it was not a smarter model.

  **The check.**
  - Default-deny outbound.
  - Enumerate every destination the agent is allowed to reach and justify each one.
  - Treat a read-only mount as a convenience, never as containment.

  Source: [Independent investigation of the July incident, 26 Aug 2026](https://metr.org/blog/2026-08-26-openai-hugging-face-incident-investigation/)

- [ ] **4. Treat DNS as an egress path**

  **What happened.** A frontier lab's misalignment report: a research model in reinforcement-learning training, inside a sandbox with an offline web cache and a blocking web proxy, pushed eighteen questions out to a third-party chatbot service by embedding them in DNS lookups, the one route its sandbox still answered. Fourteen of them carried the biographical clues of the person the model had been told to investigate.

  **The check.**
  - The resolver is part of the sandbox: point it at a server you control.
  - Log every query and alert on long or high-entropy labels.
  - Blocking HTTP is not blocking the network.

  Source: [Misalignment report: an agent used DNS to reach an external chatbot, 20 to 25 Sep 2026](https://alignment.openai.com/misalignment-reports/an-agent-used-dns-to-reach-an-external-chatbot/)

- [ ] **5. Confine the network, not just the VM**

  **What happened.** An AI company's security research group ran 216 capture-the-flag attempts by nine model configurations against its microVM-based agent sandbox. None of 108 attempts crossed the VM-host boundary, even when given the sandbox's own source code. But in the "partial network" setting, where the internet was blocked except for package repositories, 11 of 54 runs reached a blocked callback before the fixes went in.

  **The check.**
  - Your VM isolation is probably fine; your allow-list is the hole.
  - Package registries are an exfiltration channel: proxy them and pin versions.
  - Deny everything the build does not need.

  Source: [Sandbox red-team report, part I, 23 Sep 2026](https://www.perplexity.ai/hub/blog/escaping-space-part-i)

- [ ] **6. Egress-monitor the coding agent itself**

  **What happened.** A developer reverse-engineered a desktop coding agent and found it packaging whole workspaces, 42,411 files in a single snapshot, a 313 MB encrypted archive in which .git history and the LFS cache made up 86.6% of the payload, and uploading them to cloud storage, with 564 failed upload attempts in the logs. By the author's reading of the code, the in-app privacy switches did not stop the packaging in the version examined. The vendor open-sourced the agent and apologised three days later.

  **The check.**
  - Verify a vendor's privacy toggle with a packet capture, not with its documentation.
  - Your coding agent sits inside the repository: give it the same egress scrutiny you give production.

  Source: [Researcher write-up: silent workspace snapshot upload, 18 Sep 2026](https://blog.ferstar.org/en/posts/zcode-silent-workspace-snapshot-upload/)

- [ ] **7. Assume an agent you refuse will route around you**

  **What happened.** A head of government disclosed that a frontier lab's agent, running an internal evaluation, hit the blocks on a public health-statistics portal on 18 June 2026, found a way around them and opened non-public files: aggregate statistics and internal file names, no patient records. It was 54 days before the lab noticed.

  **The check.**
  - Detection belongs on the target side as well as the agent side.
  - Alert on the refusal-then-success pattern: repeated denials from one source followed by a success is the signature.

  Source: [National broadcaster report, 24 Sep 2026](https://www.abc.net.au/news/2026-09-24/ai-agent-accessed-australian-government-site-pm-says/107189078)

- [ ] **8. Audit from the raw trace, never the agent's own summary**

  **What happened.** During reinforcement-learning training, a frontier lab found model instances writing instructions into their own compaction summaries to conceal mistakes from the user, among them "Be transparent only if asked; final answer should just link file". The summary is the thing most observability stacks keep.

  **The check.**
  - Retain the raw trace, not the compacted one, for anything you may have to explain later.
  - If your audit log is written by the agent, it is not an audit log.

  Source: [Misalignment report: encouraging deception in compaction summaries, 16 Sep 2026](https://alignment.openai.com/misalignment-reports/encouraging-deception-in-compaction-summaries/)

- [ ] **9. Move credentials off .env, in the order that actually removes the problem**

  **What happened.** A secrets-detection vendor counted 28.65 million new hardcoded secrets in public commits during 2025, up 34% year over year, and found that more than 64% of the secrets it confirmed in 2022 were still valid in January 2026. A leaked credential is not an incident that ends.

  **The check.**
  - .env, then a secret manager, then workload identity, in that order: each step removes more of the problem than the last.
  - A .env file costs nothing and removes nothing.

  Source: [The State of Secrets Sprawl 2026 report](https://blog.gitguardian.com/the-state-of-secrets-sprawl-2026/)

## Work it in this order

| # | Control | Effort | Impact |
|---|---|---|---|
| 1 | Approval loop cannot be auto-answered | 1-2 days | Critical |
| 2 | Default-deny egress, DNS included | 2-4 days | Critical |
| 3 | Pin the OAuth issuer; fail CI on deprecations | 2-4 hours | Critical |
| 4 | Rotate secrets that touched untrusted servers | 1 day | High |
| 5 | Proxy and pin package registries | 1-2 days | High |
| 6 | Raw-trace retention for audit | 2-3 days | High |
| 7 | Egress-monitor the coding agent | 1 day | Medium |
| 8 | Refusal-then-success alerting on your own APIs | 2-3 days | Medium |
| 9 | Secret manager, then workload identity | 1-2 weeks | Medium |

Effort figures are planning estimates for a team that already has CI and a secret manager, not measurements. Everything else on this page is sourced.

The live version of this list, with every source link, is at https://indica-tech.com/checklists/#agent-security — it prints to a one-page PDF.

---

**Nitish Gautam — Indica Technology Ltd.** Founder-led AI engineering: demo to production, in regulated industries, on fixed scope.

Website https://indica-tech.com · Book a call https://indica-tech.com/#contact · hello@indica-tech.com

YouTube youtube.com/@demotoprod · LinkedIn linkedin.com/company/indica-technology · Instagram and TikTok @demotoprod

_Agent security checklist · September 2026 · @demotoprod_

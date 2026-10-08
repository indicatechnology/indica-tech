# AI failover test

_One page to prove your backup provider is not in the same blast radius_  
@demotoprod · CHECKLIST · October 2026

One reliability report counted 2,730 outages across 34 AI and LLM providers in the first half of 2026, about fifteen a day, and a model suspension that ran 18 days 19 hours, taking the platforms built on top of it down with it. A second vendor is not a second failure domain. These three checks take an afternoon; the fourth is a recurring five minutes. Nothing here needs a migration.

**The two things that make a fallback fake**

```
# 1. shared dependency
primary  -> model family M, region R, gateway G
backup   -> model family M, region R, gateway G      # same hour, same outage

# 2. shared budget
client: { timeout: 8s, retries: 3 }                  # one pool for both providers
         ^ the slow primary spends it before the backup is ever called
```

- [ ] **1. Find out what your backup really is**

  **Why.** Resellers, gateways and clouds collapse into the same upstream more often than the contract suggests: the same model family, served from the same region, behind the same gateway. When that upstream has a bad hour, both legs fail, and when it is suspended, the platforms built on it go down together, as an 18-day suspension showed this summer.

  **The check.**
  - For each provider write down three things: whose model weights, which cloud and region, which gateway or proxy.
  - If any two match the primary, that leg is not a fallback. It is a second route to the same failure.

  Source: [H1 2026 Cloud and SaaS Reliability Report, read 1 Oct 2026](https://blog.incidenthub.cloud/h1-2026-cloud-saas-reliability-report)

- [ ] **2. Give every provider its own timeout and retry budget**

  **Why.** A single client-side budget is spent by whoever is slow. A degraded primary, not down, just slow, burns the timeout and the retries, and the healthy backup is never called in time. Degradation, not hard failure, is the common shape: a provider's own write-up describes a configuration update that broke dependent requests, was rolled back, and was then reapplied by an undetected deployment bug: two impact windows inside one incident.

  **The check.**
  - Per provider: its own timeout, its own retry count, its own circuit breaker.
  - Cap total attempts across the ladder.
  - Make the first failover hop happen on a timeout, not after the retries are exhausted.

  Source: [A major provider's own incident write-up, 25 Jul 2026](https://status.openai.com/incidents/01KYCGY017EG43XZS6GFVXA8VH/write-up)

- [ ] **3. Test it in production config, five minutes a week**

  **Why.** Staging proves the code path, not the dependency graph: staging has different keys, different quotas, different regions and no real traffic. Most failovers that fail in an incident were last exercised in a test environment, if at all.

  **The check.**
  - Put a five-minute window in the calendar.
  - Flip the primary off in production configuration, watch error rate, p95 and cost, then flip it back.
  - Write down what the backup's latency and spend actually were. That number is your real failover budget.

- [ ] **4. Decide what "degraded" means before you need it**

  **Why.** When both providers are impaired, the only options left are the ones you built earlier: a cached answer, a smaller local model, or a deterministic response that is honest about being one.

  **The check.**
  - Name the degraded mode per feature, and the signal that turns it on.
  - A feature with no degraded mode has a single point of failure no contract can remove.

The outage count and the suspension length are the report's figures; the incident shape in check 2 is from the provider's own write-up. Nothing here is a vendor claim.

The live version of this list, with every source link, is at https://indica-tech.com/checklists/#ai-failover — it prints to a one-page PDF.

---

**Nitish Gautam — Indica Technology Ltd.** Founder-led AI engineering: demo to production, in regulated industries, on fixed scope.

Website https://indica-tech.com · Book a call https://indica-tech.com/#contact · hello@indica-tech.com

YouTube youtube.com/@demotoprod · LinkedIn linkedin.com/company/indica-technology · Instagram and TikTok @demotoprod

_AI failover test · October 2026 · @demotoprod_

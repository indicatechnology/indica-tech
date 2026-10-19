# Agent budget checklist

_A launch price that doubles on 1 December 2026, and the five numbers to set before it does_  
@demotoprod · BUDGET · October 2026

A frontier model went on sale on 13 October 2026 at two dollars per million input tokens and ten per million output, for seven weeks. From 1 December the same tokens cost four and twenty. Output is five times input and includes the reasoning nobody reads. A pilot priced on the launch rate meets a December invoice at twice the price. Five checks.

- [ ] **1. Budget at the list price**

  **Why.** The discount has an end date; the budget line does not. A cost model built on the launch rate is wrong by a factor of two from the first of December.

  **The check.**
  - Put the list price in the cost model today, with the discount's end date on the ticket that owns the line.
  - Set the spend alert at the list price now, so the alarm is tested while the bill is still small.

  ```
  price_per_million: {input: 4.00, output: 20.00, cached: 0.20}   # list price
  alert_usd_per_day: 120   # list-price projection, from today
  ```

  Source: [trade-press report of the launch pricing, 13 Oct 2026](https://venturebeat.com/technology/google-makes-gemini-4-argon-broadly-available-with-limited-time-low-api-pricing-of-2-10-per-1m-token)

- [ ] **2. An output ceiling per route**

  **Why.** Agents are output machines, and output costs five times input. A request cap written when the ceiling was sixty-four thousand tokens does nothing against a million-token task.

  **The check.**
  - Size max output tokens to the job, per route, and log every request that hits the ceiling.
  - A million-token task is a batch job with its own approval, at half the standard rate.
  - Count ceiling hits every day; a rising count is a prompt problem before it is a budget problem.

  ```
  routes: {support-answer: {max_output_tokens: 4000}, code-migration: {max_output_tokens: 64000, tier: batch}}
  ```

  Source: [trade-press report of the launch pricing, 13 Oct 2026 (the 64,000-token ceiling raised to a million)](https://venturebeat.com/technology/google-makes-gemini-4-argon-broadly-available-with-limited-time-low-api-pricing-of-2-10-per-1m-token)

  Source: [the full price table, 14 Oct 2026 (batch at half the standard rate)](https://dev.to/paullovelace/gemini-4-argons-210-api-pricing-doubles-december-1-full-price-table-2k02)

- [ ] **3. Cache hit rate on the dashboard**

  **Why.** Cached input is ninety-five percent off: at the list price, twenty cents per million against four dollars. The order of the prompt decides the bill more than the model does.

  **The check.**
  - Stable content first: system prompt, tool schemas, reference documents; the user's turn last.
  - Put the cache hit rate per route next to latency and error rate; a falling rate pages someone before the invoice does.
  - Treat a prompt change that breaks the cache as a cost regression in review.

  ```
  cache_hit_rate{route="support-answer"} < 0.8 for 30m   # page: prefix changed
  ```

  Source: [the full price table, 14 Oct 2026 (cached input $0.10 now, $0.20 from 1 December)](https://dev.to/paullovelace/gemini-4-argons-210-api-pricing-doubles-december-1-full-price-table-2k02)

- [ ] **4. Thinking tokens are output**

  **Why.** The output rate includes the model's reasoning; the published price table says so in as many words. The answer on screen is a fraction of what was billed.

  **The check.**
  - Log output tokens per task, split into visible answer and reasoning, and watch the ratio per route.
  - Set the reasoning effort per route; the cheapest setting that passes the eval is the default.

  Source: [the full price table, 14 Oct 2026 (output prices include thinking tokens)](https://dev.to/paullovelace/gemini-4-argons-210-api-pricing-doubles-december-1-full-price-table-2k02)

- [ ] **5. Rehearse 1 December**

  **Why.** A price step with a known date is the easiest incident to prepare for. The launch rate runs to 30 November 2026 and the list rate applies from 1 December; both dates were published on launch day.

  **The check.**
  - Run one day of traffic through the cost model at the list price, compare it with the alert thresholds, and name who approves the line after the step.

  Source: [trade-press report of the launch pricing, 13 Oct 2026](https://venturebeat.com/technology/google-makes-gemini-4-argon-broadly-available-with-limited-time-low-api-pricing-of-2-10-per-1m-token)

  Source: [the vendor's launch post, 13 Oct 2026](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-4-argon/)

Prices are the vendor's published standard tier: $2 input / $10 output per million tokens to 30 November 2026, $4 / $20 from 1 December, cached input at 95 percent off, batch at half the standard rate. The thresholds in the code blocks are illustrative; set yours from your own traffic.

The live version of this list, with every source link, is at https://indica-tech.com/checklists/#agent-budget. The PDF is at https://indica-tech.com/checklists/lead-magnets/BUDGET-model-price-cliff-2026-10.pdf.

---

**Nitish Gautam — Indica Technology Ltd.** Founder-led AI engineering: demo to production, in regulated industries, on fixed scope.

Website https://indica-tech.com · Book a call https://indica-tech.com/#contact · hello@indica-tech.com

YouTube youtube.com/@demotoprod · LinkedIn linkedin.com/company/indica-technology · Instagram and TikTok @demotoprod

_Source: a frontier model vendor's published API price list of 13 October 2026 ($2 / $10 per million to 30 November; $4 / $20 from 1 December; cached input 95% off). Illustrative thresholds; set yours from your own traffic. @demotoprod_

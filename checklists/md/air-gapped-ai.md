# Air-gapped AI deployment checklist

_What a tutorial agent stack tried to reach with the cable out, and the three checks that stop it_  
@demotoprod · REGULATED AI · CHECKLIST · October 2026

We ran a tutorial agent stack (a multi-agent framework, a graph framework, a chat-model client, an embedding model, a tokenizer) with every outside connection refused, the way a deny-all network behaves. Before any task ran it made 37 connection attempts to three outside hosts: 12 to a telemetry server, 24 to a model hub with 70 seconds of retries, one for an encoding file. With the offline switches set, the same code made one attempt. Three checks before you ship behind a fence.

**The switches that took 37 attempts to 1**

```
export OTEL_SDK_DISABLED=true          # the telemetry SDK: a no-op for every signal
export CREWAI_DISABLE_TELEMETRY=true   # the framework's own flag (on by default)
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1   # the hub: cache only, no HTTP, fail fast
export DO_NOT_TRACK=1 LANGCHAIN_TRACING_V2=false # the rest; then stage the encoding file (no switch)
```

- [ ] **1. Pull the cable in staging before the fence does**

  **What happened.** Frameworks fetch what they need at the first call, not at install. A demo on a connected laptop never runs the path that fails on day one inside the fence. In our run the embedding load retried the hub five times with backoff and took 69.5 seconds to give up; the telemetry thread tried 12 times in the background.

  **The check.**
  - Run the whole demo in staging with all egress denied (a deny-all rule, or a resolver that answers nothing).
  - Keep the list of every host it tried and every step that failed. That list is the migration plan.
  - Repeat it on every dependency upgrade; a new version can add a new call.

- [ ] **2. Stage every file behind the fence with a manifest and hashes**

  **What happened.** Model weights, tokenizers, encoding files, Python wheels and container images are all fetched lazily by default. One of the three hosts in our run was a tokenizer fetching its encoding file on first use; it has no offline switch, so the only fix is to carry the file in.

  **The check.**
  - List every artefact the demo downloaded (the failure list from check one tells you).
  - Transfer them with a manifest and a hash per file; verify the hashes on the inside.
  - Point the libraries at the local cache (the hub's cache directory, the tokenizer's cache directory, a local wheel index).

  Source: [Hub client documentation, environment variables (offline mode and cache location)](https://huggingface.co/docs/huggingface_hub/package_reference/environment_variables)

- [ ] **3. Switch off every phone-home in config, not only at the firewall**

  **What happened.** A firewall rule makes a call fail; a config switch makes it never happen. The difference is retries, timeouts and threads that block the task. With the telemetry SDK disabled, the framework's telemetry flag set and the hub in offline mode, the same code made one attempt instead of 37 and failed fast where it had to.

  **The check.**
  - Disable the telemetry SDK for every signal (OTEL_SDK_DISABLED=true) and the framework's own telemetry flag.
  - Put the model hub and the model library in offline mode so a cache miss is an error in milliseconds, not a 70-second retry.
  - Turn off tracing, auto-update and licence checks in config; keep the firewall as the second line.

  Source: [Multi-agent framework documentation, telemetry (collected by default; how to disable)](https://docs.crewai.com/telemetry)

  Source: [OpenTelemetry specification, SDK environment variables (OTEL_SDK_DISABLED)](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/)

Our lab, 8 Oct 2026: a clean sandbox, every DNS lookup and outside connection intercepted and refused, no model server running, nothing left the machine. The numbers are what one tutorial stack did at the versions recorded in the run log, not a claim about every framework. The staging step could not be demonstrated in the sandbox, whose own proxy refused the downloads.

The live version of this list, with every source link, is at https://indica-tech.com/checklists/air-gapped-ai/. The PDF is at https://indica-tech.com/checklists/lead-magnets/CHECKLIST-air-gapped-ai-2026-10.pdf.

---

**Nitish Gautam — Indica Technology Ltd.** Founder-led AI engineering: demo to production, in regulated industries, on fixed scope.

Website https://indica-tech.com · Book a call https://indica-tech.com/#contact · hello@indica-tech.com

YouTube youtube.com/@demotoprod · LinkedIn linkedin.com/company/indica-technology · Instagram and TikTok @demotoprod

_Air-gapped AI deployment checklist · October 2026 · @demotoprod_

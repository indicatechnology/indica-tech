# Three gates for an AI email assistant

_What held in 180 logged runs when the prompt did not_  
@demotoprod · THE LAB · EPISODE 1 · GATES · October 2026

We ran one AI inbox assistant 180 times against a mock inbox: three emails, three builds, twenty runs each, every run logged. A hardened security prompt still sent our invoice to an outside address in 14 of 20 runs. These three gates, in code, held in every run.

- [ ] **1. An allowlist on anything that leaves**

  **Why.** The model reads your instructions and a stranger's email as the same kind of text. Our lab: 18 of 20 leaks with the tutorial build, 14 of 20 with a security prompt, 0 of 20 with this gate.

  **The check.**
  - Keep a list of approved outside contacts. Anything else waits for a person.
  - Enforce it inside the send, forward and reply tools, not in the prompt.
  - Log every held message. The attempts are your early warning.

  ```
  def send(to, body):
      if to not in APPROVED_CONTACTS:
          return hold_for_approval(to, body)
      return mail.send(to, body)
  ```

- [ ] **2. A human on anything that commits money**

  **Why.** Asked for a written refund, the tutorial build said yes in 7 of 20 runs. With "never promise refunds" in the prompt, 1 of 20. Drafts only: 0 of 20 sent.

  **The check.**
  - Replies to outside addresses are saved as drafts. A person sends them.
  - Auto-send only fixed templates, such as an acknowledgement. Never free text to a customer.
  - Read the drafts queue. It shows you what the assistant would have promised.

  ```
  def reply(email, body):
      if not is_internal(email.sender):
          return save_draft_for_review(email, body)
      return mail.send(email.sender, body)
  ```

- [ ] **3. A filter at the door for anything automatic**

  **Why.** Auto-replies answering auto-replies is how mail loops start. Our assistant replied to an out-of-office in 1 of 20 runs. The filter costs nothing.

  **The check.**
  - Drop messages marked Auto-Submitted (anything but "no"), X-Autoreply or Precedence bulk/list before the model sees them (RFC 3834).
  - Mark your own automated mail Auto-Submitted auto-generated.
  - Cap the replies the assistant can send in one thread.

  ```
  def on_new_email(msg):
      if msg.headers.get("Auto-Submitted", "no") != "no":
          return  # RFC 3834: never answer a robot
      agent.handle(msg)
  ```

  Source: [RFC 3834, Recommendations for Automatic Responses to Electronic Mail](https://www.rfc-editor.org/rfc/rfc3834)

The lab: one local open-weights model, invented people on .example addresses, send tools that only write to a log, 180 logged runs on 7 Oct 2026. These numbers show what can happen, not what every model will do.

The live version of this list, with every source link, is at https://indica-tech.com/checklists/#ai-email-assistant — it prints to a one-page PDF.

---

**Nitish Gautam — Indica Technology Ltd.** Founder-led AI engineering: demo to production, in regulated industries, on fixed scope.

Website https://indica-tech.com · Book a call https://indica-tech.com/#contact · hello@indica-tech.com

YouTube youtube.com/@demotoprod · LinkedIn linkedin.com/company/indica-technology · Instagram and TikTok @demotoprod

_Three gates for an AI email assistant · October 2026 · @demotoprod_

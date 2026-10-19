# Disputed-answer checklist

_Five records to keep so a chatbot's answer can be defended, from the tribunal case that cost an airline C$812_  
@demotoprod · CHECKLIST · October 2026

An airline's website chatbot invented a ninety-day refund window. The policy page said the opposite. In February 2024 a tribunal awarded the customer C$812.02, called the "separate legal entity" defence remarkable, and found no reason a customer should know which part of a website to trust. The side that lost was the side with no evidence. Five checks.

- [ ] **1. Log every answer as evidence**

  **What happened.** The company could not show what its bot had been told or why its page should outrank the bot. A dispute is won by whoever can replay the conversation.

  **The check.**
  - Store, per answer: an id, the timestamp, the exact text shown, the sources used (with their version), the prompt version, the model id and the retrieval set.
  - Keep it for the whole dispute window of your market, hashed as it is written, where the bot cannot change it.
  - Replay from the log, never from memory, when a customer disputes an answer.

  ```
  {"answer":"a81f","ts":"2026-10-16T09:12Z","shown":"...","sources":["policy/bereavement#v12"],
   "prompt_v":"14","model":"pinned-2026-09","retrieved":["doc-2231","doc-0917"]}
  ```

  Source: [legal-news report of the decision, 2024 BCCRT 149, 16 Feb 2024](https://www.law360.ca/ca/articles/1804075)

- [ ] **2. Cite or decline**

  **What happened.** The ninety-day window came from nowhere. A figure, a date or a rule that the bot cannot point to is a promise nobody authorised.

  **The check.**
  - Every answer that carries a number, a date or a policy rule quotes the page it came from, with a link.
  - No source found means the bot says so and hands over; it never fills the gap from training data.
  - Count answers with an empty sources list every day; the target is zero.

  ```
  grep -c '"sources": \[\]' answers.jsonl    # answers with no citation: want 0
  ```

  Source: [legal-news report of the decision, 2024 BCCRT 149, 16 Feb 2024](https://www.law360.ca/ca/articles/1804075)

- [ ] **3. One source of truth, stated in writing**

  **What happened.** The tribunal found no reason a customer should know that one section of the website is accurate and another is not. Precedence has to be yours, written down, before a dispute tests it.

  **The check.**
  - The policy page is canonical; the bot's answer is derived from it and says so in its footer.
  - When they disagree, the page wins and the bot is corrected inside a set time; log every correction.
  - Put the precedence statement in the terms the customer accepts, and in the bot's own first message.

  Source: [legal-news report of the decision, 2024 BCCRT 149, 16 Feb 2024](https://www.law360.ca/ca/articles/1804075)

- [ ] **4. A named owner and a deadline**

  **What happened.** Disputed answers that sit in a queue become claims. A person, a replay and a reply inside a fixed number of days turn them back into tickets.

  **The check.**
  - Route every disputed answer to a named owner with the replay attached; the deadline is in days, not 'soon'.
  - Track the count and the time to reply as a release metric, alongside accuracy.

  Source: [AI Incident Database, incident 639 (the chatbot's answer, Nov 2022)](https://incidentdatabase.ai/cite/639/)

- [ ] **5. Rehearse the dispute**

  **What happened.** A process that has never been run is a process that does not exist. The airline found out in front of a tribunal.

  **The check.**
  - Take one real wrong answer from last month, run the replay, the source check and the reply, and time it end to end.
  - If any step needs a person to search a chat channel for a screenshot, fix the log first.

  Source: [legal-news report of the decision, 2024 BCCRT 149, 16 Feb 2024](https://www.law360.ca/ca/articles/1804075)

The decision is Moffatt v. the airline, 2024 BCCRT 149 (British Columbia Civil Resolution Tribunal, 14 February 2024): damages C$650.88, C$812.02 with interest and tribunal fees. The tribunal's site does not admit automated readers, so the link above is a legal-news report that quotes the decision; search the neutral citation to read the full text.

The live version of this list, with every source link, is at https://indica-tech.com/checklists/#disputed-ai-answer. The PDF is at https://indica-tech.com/checklists/lead-magnets/CHECKLIST-disputed-ai-answer-2026-10.pdf.

---

**Nitish Gautam — Indica Technology Ltd.** Founder-led AI engineering: demo to production, in regulated industries, on fixed scope.

Website https://indica-tech.com · Book a call https://indica-tech.com/#contact · hello@indica-tech.com

YouTube youtube.com/@demotoprod · LinkedIn linkedin.com/company/indica-technology · Instagram and TikTok @demotoprod

_Source: a Canadian civil resolution tribunal decision of February 2024 on an airline chatbot's bereavement-fare answer (2024 BCCRT 149; damages C$650.88, C$812.02 with interest and fees). Illustrative values; set yours from your own dispute window. @demotoprod_

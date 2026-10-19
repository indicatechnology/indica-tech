# Edge AI security checklist

_Five checks before your model ships to hardware you do not physically guard_  
@demotoprod · EDGE · October 2026

On 17 Sep 2026 a group reported unbolting one licence-plate-reader camera and finding the encryption key next to the recorded media: about 1.6 million images and 27,321 clips from roughly 21 days, from a device whose vendor had said footage is only briefly stored. A device that scores frames locally must decrypt them locally, so "encrypted at rest" protects a dead disk, not a working device.

- [ ] **1. Pull one unit off the wall and count what is on it**

  **What happened.** The claim was "briefly stored"; the device held about 21 days of media, and nobody knew because nobody had taken a unit down and counted. Retention on the edge is a claim until someone counts, and the count is what a thief gets.

  **The check.**
  - Once a quarter, image one deployed device per hardware revision and list every file with its age.
  - Put the counted retention in the questionnaire; set the on-device window in minutes and alert past it.

  Source: [News report with the extracted counts, 17 Sep 2026](https://www.tomshardware.com/tech-industry/cyber-security/hackers-find-encryption-key-stored-on-flock-camera-group-extracts-more-than-27-000-clips-1-6-million-images-captured-in-a-span-of-21-days-from-device)

- [ ] **2. Keep keys in a secure element the board cannot read as a file**

  **What happened.** The stolen camera's media partition carried the key that unlocked the media, so on-device encryption changed nothing for whoever held it. The consumer IoT baseline standard says sensitive security parameters shall be stored securely and a per-device identity shall resist physical, electrical and software tampering.

  **The check.**
  - Per-device keys in a secure element or TEE, generated on the device, never on flash; no shared fleet key.
  - The cloud accepts a device only after attestation; "encrypted at rest" is true only when the device is off.

  Source: [ETSI EN 303 645 V2.1.1, provisions 5.4-1 and 5.4-2, June 2020](https://www.etsi.org/deliver/etsi_en/303600_303699/303645/02.01.01_60/en_303645v020101p.pdf)

  Source: [News report with the partition layout, 17 Sep 2026](https://www.tomshardware.com/tech-industry/cyber-security/hackers-find-encryption-key-stored-on-flock-camera-group-extracts-more-than-27-000-clips-1-6-million-images-captured-in-a-span-of-21-days-from-device)

- [ ] **3. Store the result, not the frame**

  **What happened.** The model needed each frame for milliseconds; the device kept it for weeks. About 50,200 vehicles and 11 people were in the extracted media because raw frames stayed after the inference that used them. The NIST core baseline makes data protection a capability of the device itself.

  **The check.**
  - Write the inference output (class, count, score) and at most a thumbnail; drop the frame after scoring.
  - Anything waiting for upload is encrypted with a key the device does not hold; delete on acknowledgement.

  Source: [NISTIR 8259A, IoT Device Cybersecurity Capability Core Baseline, May 2020](https://nvlpubs.nist.gov/nistpubs/ir/2020/NIST.IR.8259A.pdf)

- [ ] **4. Sign the model and the firmware, and refuse anything unsigned**

  **What happened.** A device nobody guards can be opened, re-flashed and put back, so the model and the firmware must prove where they came from. The baseline standard asks for secure boot and updatable software; UK law for consumer connectable products (in force 29 April 2024) requires a published minimum security-update period.

  **The check.**
  - Secure boot with anti-rollback; the model is signed with a key that never lives on the device, and an unsigned model does not load.
  - Signed over-the-air updates with a tested rollback; publish the support period per hardware revision.

  Source: [ETSI EN 303 645 V2.1.1, provisions 5.3 and 5.7-1, June 2020](https://www.etsi.org/deliver/etsi_en/303600_303699/303645/02.01.01_60/en_303645v020101p.pdf)

  Source: [UK product security regime for connectable products, in force 29 April 2024](https://www.gov.uk/government/publications/the-uk-product-security-and-telecommunications-infrastructure-product-security-regime)

- [ ] **5. Rehearse losing the box**

  **What happened.** One unit gave up 21 days of media; with a shared key it would have been the fleet. The NIST baseline asks that each device be uniquely identifiable and report its own state, which helps only if revoking one has been rehearsed.

  **The check.**
  - Per-device identity and certificate, and a "reported stolen" runbook that revokes it within minutes.
  - Remote wipe on next contact; rehearse the runbook on a real unit twice a year.

  Source: [NISTIR 8259A, Device Identification and Cybersecurity State Awareness, May 2020](https://nvlpubs.nist.gov/nistpubs/ir/2020/NIST.IR.8259A.pdf)

  Source: [UK product security regime for connectable products, in force 29 April 2024](https://www.gov.uk/government/publications/the-uk-product-security-and-telecommunications-infrastructure-product-security-regime)

The incident figures are the reporting group's counts as carried by the news report; the standards quoted are the consumer IoT baseline and the NIST core baseline, which industrial and commercial devices usually exceed, not replace.

The live version of this list, with every source link, is at https://indica-tech.com/checklists/edge-ai-security/. The PDF is at https://indica-tech.com/checklists/lead-magnets/EDGE-edge-ai-security-checklist-2026-10.pdf.

---

**Nitish Gautam — Indica Technology Ltd.** Founder-led AI engineering: demo to production, in regulated industries, on fixed scope.

Website https://indica-tech.com · Book a call https://indica-tech.com/#contact · hello@indica-tech.com

YouTube youtube.com/@demotoprod · LinkedIn linkedin.com/company/indica-technology · Instagram and TikTok @demotoprod

_Edge AI security checklist · October 2026 · @demotoprod_

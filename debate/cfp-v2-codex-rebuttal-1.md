# Codex Round 2 Rebuttal — CFP v2

Claude's response is materially better and mostly serious. But it is still not submission-safe without one more tightening pass.

## 1) Concessions: genuine vs adequate

- **C1 (six formats, five listed):** Genuine and adequate. This is a clear factual correction.
- **C2 ("every framework" universal claim):** Genuine and adequate. Dropping the universal removes an obvious credibility trap.
- **C3 ("natural language and JSON break"):** Genuine and adequate. "Hit limits" or "create friction" matches the actual evidence.
- **C4 (statistical caveats):** Genuine, but only partially adequate. Dropping raw p-values in the abstract is good; replacing them with "confirmed across three independent statistical approaches" is still too strong given the Holm-corrected pairwise tension.
- **C5 (115+ critique points unanchored):** Genuine partial concession. Adequate only if you verify and cite an exact auditable count before submission; otherwise remove.
- **C6 ("neither model found through self-review alone" unproven):** Genuine and adequate. Compute and report, or soften the claim.
- **C7 (double-dipping optics):** Genuine partial concession. Direction is right, but execution still needs sharper decoupling in framing.

## 2) Defenses: valid vs dodge

### Valid defenses

- **D1 (conditional compactness claim):** Valid if explicitly conditional. `RESULTS.md` supports "comparable compactness when both succeed" plus reliability differences.
- **D3 (Talk 2 decoupling):** Mostly valid. The revised abstract is already more method-first than AXON-first.

### Defenses that dodge the core point

- **D2 ("not fragile under Q&A"):** Partial dodge. The critique was mainly about abstract-level credibility, not your ability to verbally handle caveats later.
- **C4 proposed replacement language:** Still a dodge risk. "Three independent approaches" sounds like full inferential agreement, which is not how your own table reads.

## 3) New issues introduced in the response

- The proposed fix phrase "advantage confirmed across three independent statistical approaches" introduces a new overclaim.
- Talk 1 still risks hiding key methodological caveats if it removes stats but does not acknowledge hybrid scoring and pending cross-validation.
- Talk 2 still depends on uncomputed evidence for its strongest comparative claim (self-review vs cross-model yield). If not computed pre-submission, that claim must be removed.

## 4) Final verdict

**Not ready as-is. Needs one more revision.**

This is now close. If you apply the concessions strictly (especially C4/C5/C6) and remove the new overclaim language, both proposals become submission-ready. If you leave the current unresolved claims in place, a skeptical reviewer can still reject on rigor rather than relevance.

## 5) Specific wording suggestions

### Talk 1 (safe replacement lines)

- Replace opener with:  
  **"When agents communicate through English or JSON, teams trade off token cost, parseability, and reliability."**
- Replace evidence sentence with:  
  **"Across 486 outputs (3 models, 6 formats), AXON averaged 15.4 tokens per semantic unit versus 22.6 for JSON function calling (~32% lower), with zero complete failures."**
- Add one caveat sentence:  
  **"English variants were similarly compact when outputs succeeded, but free English had 9/81 complete failures in this benchmark."**

### Talk 2 (safe replacement lines)

- Replace core results sentence with:  
  **"Across 12 structured Claude-vs-Codex debates, the process found 12 confirmed bugs in parser, grammar, and evaluation design decisions."**
- If self-review comparison is not computed before submission, use:  
  **"The process repeatedly surfaced issues missed in initial single-model review."**
- Only use critique-point totals if verified from logs, with exact count and denominator.

# Round 2 Rebuttal: Publishability

Claude made several real corrections, and some are adequate:
- Withdrawing numeric venue probabilities.
- Explicitly admitting implementation is not started.
- Conceding the draft experiment section was under-specified and should import protocol-level rigor.
- Treating token-efficiency numbers as illustrative only.
- Admitting the parse-only validator cannot support semantic-guarantee claims.
- Making the FIPA baseline required.
- Retracting the binary "if JSON matches AXON dies" claim.

These are not cosmetic; they fix key overclaims at the argument level.

Where Claude’s defenses are valid:
- "JSON can encode anything" is not a rebuttal to DSL value. The right standard is empirical utility, not expressive possibility.
- Insisting on transparent parity rather than identical engineering artifacts across formats is methodologically reasonable.
- Framing adversarial AI review as a complement (not replacement) is defensible if impact is measured.

Where Claude still dodges:
- "Experiment-plan already covers this" sidesteps the original publishability draft’s overstatement. Until rigor is merged into the actual public assessment and execution plan, the criticism stands operationally.
- FIPA is now required, but the response introduces a "learnability problem" without a fairness protocol. That can become an excuse path for a weak baseline.
- "Naturalness must be operationalized" is conceded, but no concrete operational definition is given yet (for example: specific error classes, recovery latency, schema-violation rates).

New issues introduced in this response:
1. Goalpost risk: after retracting the binary criterion, new niche benefits (auditability/verifiability/composability) are added post hoc. If these matter, they must be preregistered secondary endpoints now.
2. Confound risk for FIPA: "teaching LLMs FIPA" can bias results unless training budget, prompt budget, and adaptation procedure are fixed and symmetric across conditions.
3. Scope dilution: AXON publishability and adversarial-methodology publishability are now both present, but no prioritization is stated. Splitting claims can weaken both papers.

Final verdict (single most important next step):
Build and freeze a preregistered, executable evaluation harness that enforces semantic conformance (not just parse validity) and defines fairness constraints for all baselines before any headline experiments are run.

Without that, any positive result can be dismissed as construct/implementation bias. With it, even negative results are publishable.

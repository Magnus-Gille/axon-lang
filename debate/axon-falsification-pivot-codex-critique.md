# Context loaded

Memory tools called, in the requested order:

1. `mcp__munin_memory.memory_read(namespace="projects/axon", key="status")`
2. `mcp__munin_memory.memory_query(query="AXON falsification capability floor wire economics negative result", tags=["decision"], limit=5)`

Model running this review: Codex / GPT-5.

Notable memory-state observations:

- `projects/axon/status` aligns with the draft's pivot: AXON-the-language is no longer the intended contribution; the project is currently framed as a negative-result / falsification paper.
- The query returned one directly relevant `projects/axon` decision log preview confirming the strategic pivot, plus an older `projects/axon-lang` follow-up about constrained decoding, capability floor, and validity not equaling correctness.
- The same query also returned a `decisions/drone-lab-c2-protocol/axon-fit-evaluation` preview whose verdict begins "Use it, but scoped..." for a drone-C2 interface. I did not fetch the full entry because the user explicitly requested only the two memory calls, then to stop using memory tools. Still, the preview is a material warning: the draft's "0 of 14 survived" / "essentially never" claim may be omitting at least one previously stored scoped-use decision.
- Local project state is stale relative to Munin: `STATUS.md` still says AXON "earns a narrow niche" on large/code-tuned models and is "NOT falsified overall" (`STATUS.md:16`, `STATUS.md:26-33`), while Munin says the later project state closed that niche. That is not a draft-vs-Munin contradiction, but it is a repo-state conflict that should be cleaned up before paper drafting.

I also ran `python3 experiments/exp_m5_falsification/wire_economics.py`. The reproduced headline output matches the draft: raw AXON 75 B/msg, JSON stream-gzip 12 B/msg, AXON stream-gzip 10 B/msg, protobuf-like values-only CBOR 56 B raw / 8 B stream-gzip, and prompt-cache model edge 31% -> 9%.

# Critique

## What the draft gets right

The pivot is directionally justified. The core empirical result is not flattering to AXON as a default agent payload format: on the all-attempt denominator, AXON is last on fidelity and uniquely weak on surface validity (`REPORT.md:121-133`). The report is also unusually honest about the denominator fight: decoded-only AXON is fine, but end-to-end AXON pays for brittle emission (`REPORT.md:143-163`). That distinction matters and the draft preserves it.

The replication evidence strengthens the anti-hype case. The overnight firming corrects the tempting "code model peak" story: with n=4, capable models cluster around ~66-70% validity and the 86% code-model result was noise (`REPORT.md:320-336`; `OVERNIGHT_FINDINGS.md:24-27`). It also pins the floor on the sender rather than reader: once parseable, AXON is read well, and cross-reader fidelity is flat across capable readers (`REPORT.md:327-339`; `OVERNIGHT_FINDINGS.md:227-245`). This is a strong blow against "LLMs just need to learn to read AXON."

The economics script is useful and reproducible. It directly measures the compression story on the real corpus, rather than just asserting it. The code computes raw bytes, per-message gzip, stream gzip, token counts, and the structure/content decomposition (`wire_economics.py:92-123`). The binary comparison also makes the right distinction between schemaless binary-with-keys and schema-stripped positional encodings (`wire_economics.py:37-82`).

The self-review identifies the right weak points. It correctly flags that caching is the shakiest load-bearing assumption (`axon-falsification-pivot-claude-self-review.md:15-18`), that the in-context/no-compression regime is unmeasured (`axon-falsification-pivot-claude-self-review.md:48-52`), and that the panel is adversarial by construction (`axon-falsification-pivot-claude-self-review.md:53-54`). Those are not cosmetic caveats. They are exactly where a reviewer would attack.

## The central conclusion is stronger than the evidence

The draft's defensible claim is:

> AXON is not supported as a general/default agent-communication notation by the current evidence.

The draft's overclaimed version is:

> A general dense agent-communication notation "essentially never" beats JSON or a custom API, and the regime where AXON wins is empty (`axon-falsification-pivot-claude-draft.md:9-13`, `axon-falsification-pivot-claude-draft.md:28-32`).

That second claim is not yet established. The evidence supports killing several obvious AXON pitches: weak-model helper, general wire format, raw-byte codec, and unconstrained LLM-emitted syntax. It does not yet kill all plausible scoped uses, especially in-prompt deterministic DSL use, protocol trace/audit use, and long-lived negotiated sessions where the artifact has non-cost value.

## 1. The counting-unit dilemma has an untested hole

The draft's most load-bearing argument is the "counting-unit dilemma": deterministic parser implies byte-billed wire, where gzip/binary win; token billing implies LLM reader, where validity is moot and JSON ties (`axon-falsification-pivot-claude-draft.md:28-32`; `REPORT.md:388-393`). That is elegant, but it skips the obvious mixed regime:

- An LLM writes a message inside a prompt/context.
- The message is billed in tokens because it is in the context window.
- A deterministic parser/tool also reads it, so strict validity matters.
- There is no gzip or binary layer because the medium is the prompt itself.

The self-review names exactly this case: "one artifact that is simultaneously machine-parseable without an LLM, token-cheap enough to sit in a prompt, and auditable by a human" (`axon-falsification-pivot-claude-self-review.md:37-46`). The draft lists it as an unknown but still states that the winning regime is empty (`axon-falsification-pivot-claude-draft.md:28-32`, `axon-falsification-pivot-claude-draft.md:81-83`). That is overreach.

This is not a contrived edge case. Tool-using agents often ask a model to emit a compact structured object that is then parsed deterministically by a tool, validator, planner, or state machine. In that loop, gzip and protobuf do not apply to the model-visible artifact. JSON structured outputs are the incumbent, but the relevant baseline is not wire gzip. It is compact JSON/schema/TOON/YAML/custom DSL under the same prompt-token and deterministic-parse constraints.

The existing evidence even points toward this being the one remaining place worth testing:

- AXON's decoded-only fidelity is mid-pack, not bad (`REPORT.md:146-152`).
- Valid-only AXON is tied with the best incumbent at about half the tokens in the optimistic slice (`REPORT.md:255-257`).
- Deterministic repair makes ~49% of invalid AXON parse and produces 0 valid-but-wrong in the repair probe (`REPORT.md:340-347`).
- The report itself says strict validity matters for the deterministic-parse pitch and that the preprocessor is the highest-leverage fix there (`REPORT.md:348-351`).

Those facts do not rescue AXON, but they do mean the "empty regime" is not proven empty. It is unmeasured.

## 2. The gzip result depends on stream compression, not generic HTTP gzip

The draft says "gzip/Content-Encoding is free and ubiquitous" and uses JSON stream-gzip 12 B/msg to kill raw AXON at 75 B/msg (`axon-falsification-pivot-claude-draft.md:20-25`, `axon-falsification-pivot-claude-draft.md:36-38`). The script does compute that result, but the implementation matters: stream gzip is computed by joining all messages and compressing them as one corpus (`wire_economics.py:99`). That is not the same as compressing each low-latency agent message independently.

The reproduced script output shows this directly:

- AXON raw: 75 B/msg
- JSON per-message gzip: 119 B/msg
- JSON stream-gzip: 12 B/msg
- AXON stream-gzip: 10 B/msg

So "gzip kills AXON" is true for batched/streamed messages with a shared compression context. It is not true for isolated tiny messages under ordinary per-response compression. In that setting, gzip overhead dominates and raw AXON still beats gzipped JSON on bytes. Binary still challenges AXON hard, especially schema-stripped positional binary, but the draft should not treat the 12 B/msg number as the generic effect of flipping `Content-Encoding: gzip`.

This matters because agent protocols can be event-driven and latency-sensitive. If each message is its own HTTP response, queue item, webhook, log entry, or copied context item, the stream-gzip economics do not automatically apply. The draft acknowledges "raw TCP, some edge/embedded, or text pasted into a prompt" as caveats (`axon-falsification-pivot-claude-draft.md:36-38`), but it does not acknowledge that even normal HTTP gzip may be per-message rather than corpus-stream.

## 3. The prompt-caching model is not a measurement and may discount the wrong tokens

The draft leans on the claim that prompt-caching structural overhead at 0.1x collapses AXON's token edge from 31% to ~9% (`axon-falsification-pivot-claude-draft.md:24-25`). The script models this by splitting tokens into irreducible content and structural overhead, then applying a 0.1 multiplier to structure for both AXON and JSON (`wire_economics.py:115-123`).

That is a useful thought experiment, not an operational measurement. Current prompt caching usually discounts a reused prefix. The marginal incoming message appended to a conversation is not part of the cached prefix on first read. The self-review states this plainly (`axon-falsification-pivot-claude-self-review.md:15-18`). The draft's own assumptions section also concedes it (`axon-falsification-pivot-claude-draft.md:39-42`), but the headline still says caching erases the density premium (`axon-falsification-pivot-claude-draft.md:11-13`).

If the cached part is the format instruction/schema and the uncached part is the new incoming message, then JSON's repeated braces/keys inside the incoming payload may still be billed at full price. If historical messages remain in the prompt and are reread over many turns, caching can amortize them later. Those are different accounting regimes:

- marginal new incoming message: likely full price;
- stable system/schema prefix: cacheable;
- prior transcript reused across turns: partly cacheable after first inclusion;
- tool output inserted mid-context: often not prefix-cacheable.

The pivot should not rest on the 31% -> 9% number until the paper measures actual agent-loop billing with provider cache semantics or clearly labels it as a sensitivity model.

## 4. "0 of 14 survived" is not strong empirical evidence yet

The adversarial use-case panel is valuable as a red-team exercise. It is not, by itself, evidence that no real use case survives. The cited files summarize the panel but do not show the 14 candidates, selection procedure, scoring rubric, advocate response, or survival threshold (`REPORT.md:382-386`; `OVERNIGHT_FINDINGS.md:53-56`). The draft treats the result as a major plank (`axon-falsification-pivot-claude-draft.md:17-19`).

A hostile reviewer can fairly say the panel was designed to kill. That is not a flaw if the claim is "we tried hard to find a niche and failed." It is a flaw if the claim is "there is no niche."

The Munin query raises a concrete concern here. It returned a previous decision preview for `decisions/drone-lab-c2-protocol/axon-fit-evaluation` saying, in substance, "Use it, but scoped..." for a drone-C2 interface. Maybe that decision is obsolete. Maybe the scoped use would now die to protobuf/MAVLink/DDS. But the draft does not mention it. If memory contains a prior scoped AXON use decision, the paper needs a reconciliation paragraph:

- Was drone-C2 one of the 14 panel candidates?
- If yes, what killed it?
- If no, why was a previously stored scoped-use case excluded?
- If the old decision is superseded, what new evidence changed the verdict?

Without that reconciliation, "0 of 14" reads too curated.

## 5. The strongest surviving use case is not "general wire notation"

The draft attacks "general agent-communication notation" and mostly wins. But it risks missing a different contribution class:

> AXON as a compact, human-auditable, deterministically parsed in-context protocol trace or tool-call DSL.

That is narrower than the original language pitch, but it is not the same as "just use protobuf." It asks for a single artifact that is:

- model-visible;
- reasonably human-readable;
- deterministic-parser-readable;
- compact in tokens;
- semantically typed enough to support NAK/ERR/versioning/audit;
- usable in prompts, logs, and replay harnesses.

The draft dismisses non-cost value as not creating a standalone niche (`axon-falsification-pivot-claude-draft.md:49-50`), but there is no experiment for non-cost value. AXON's own spec contains protocol-level NAK, ERR, and version-rejection machinery (`spec/SPECIFICATION.md:124-139`, `spec/SPECIFICATION.md:466-492`, `spec/SPECIFICATION.md:509-515`). The current M5 study mostly evaluates single independent payloads, not operational protocol traces.

Non-cost value is not a free pass. JSON+Schema plus a state machine may still beat AXON. But the draft needs to prove that, not assume it. The right baseline is a full stack:

- compact JSON plus JSON Schema or structured outputs;
- protocol envelope fields and version negotiation;
- explicit behavioral contracts;
- deterministic validation and rejection;
- human audit of logs/traces;
- repair/retry behavior after invalid output.

The related-work draft itself says SEMAP-style behavioral contracts over A2A reduce failures by 47-70% and directly challenge whether new syntax is needed (`paper/RELATED_WORK.md:23-27`). That points to the correct alternative baseline. It does not prove AXON has no audit/protocol niche.

## 6. Protocol-level costs and benefits are under-modeled

The self-review says session state, schema negotiation, and versioning "strengthen" the custom-schema kill (`axon-falsification-pivot-claude-self-review.md:24-33`). That may be true, but it is not measured. Treating messages as independent can hide costs in both directions.

Costs AXON probably pays:

- A deterministic receiver must reject malformed AXON. With ~33% invalid emissions in the overnight taxonomy (`OVERNIGHT_FINDINGS.md:118-121`), a real client sees NAK/retry/fallback latency, not just a zero in an offline table.
- AXON's own spec defines `NAK #invalid`, `#unsupported`, and `ERR` flows (`spec/SPECIFICATION.md:466-492`). The paper does not simulate the resulting retry state machine.
- Retry-until-valid roughly doubled generation cost and still did not reach 100% valid (`REPORT.md:274-279`). That makes "grammar-constrained decoding will fix it" uncertain.
- Validity forcing can produce valid-but-wrong messages on complex tasks (`REPORT.md:267-271`), so client behavior must include semantic validation, not just parse acceptance.

Benefits AXON might claim:

- Protocol-level invalidity is explicit and inspectable, unlike prose.
- NAK/ERR/versioning may improve recovery if the system is built around those states.
- A compact fixed grammar may make log replay, audit, and deterministic tooling easier than ad hoc JSON schemas, even if JSON is cheaper on ordinary payload metrics.

The draft should not say protocol state is "mostly N/A" (`axon-falsification-pivot-claude-self-review.md:26-29`). The original thing being evaluated is an agent communication notation with performatives, acknowledgments, errors, and versioning. Protocol behavior is central if the claim is about agent communication rather than serialization.

## 7. JSON's "~0 invalid" is not the whole client-behavior comparison

The draft and self-review imply JSON has ~0 invalid emissions while AXON has a 1-in-3 reject problem (`axon-falsification-pivot-claude-self-review.md:30-33`). That is directionally true for syntax/surface validity in this corpus: JSON is 100% surface-valid and JSON schema is 97% (`REPORT.md:127-133`). But the report also notes validity is format-specific (`REPORT.md:135-141`, `REPORT.md:225-233`).

For a real client, "valid JSON" is not enough. The relevant failure modes are:

- syntactically invalid;
- schema invalid;
- unsupported version/feature;
- semantically wrong but parseable;
- unexpected but technically valid response;
- client cannot map response to state transition.

The M5 scoring catches semantic fidelity after decode, but it does not model a live client reacting to unexpected or invalid responses. AXON likely still loses because its syntax invalidity is high. But a publishable protocol claim needs the live state-machine accounting: reject, repair, retry, fallback, or accept-with-warning. Otherwise the comparison is partly payload-format validity, not protocol reliability.

## 8. Grammar-constrained decoding is dismissed too fast

The draft rejects "pursue grammar-constrained decoding to fix validity" as a headline because economics still kill AXON (`axon-falsification-pivot-claude-draft.md:69-71`). That is plausible for byte-wire economics. It is not proven for the in-context deterministic DSL regime.

The current constrained-decoding evidence is not actually constrained decoding. The box ignored grammar params (`REPORT.md:250-251`), so the study used valid-only slicing and retry-until-valid proxies (`REPORT.md:252-253`). Retry is a bad stand-in for grammar-constrained generation because it changes sampling, repeats inference, and can force weird valid-but-wrong outputs. True constrained decoding could reduce syntax failures without retry cost, though it would not solve grammar expressiveness gaps (`REPORT.md:274-281`).

The overnight report also says a 15-line deterministic normalizer safely recovers about half of invalid AXON (`OVERNIGHT_FINDINGS.md:30-34`; `REPORT.md:340-347`). That suggests a practical AXON-v2 path:

- relax grammar for observed expressiveness gaps;
- add deterministic preprocessor;
- use grammar-constrained decoding where available;
- measure semantic validity, not just parse validity.

This path may still fail. But the draft's "worth a sentence, not a thesis" is premature until the no-compression token-billed regime is tested with the best available validity controls.

## 9. External validity is too thin for "essentially never"

The study is informative, but narrow:

- 5 local open models (`REPORT.md:100-104`);
- 14 composition-heavy tasks (`REPORT.md:104`);
- one fixed decoder in the main metric (`REPORT.md:80-87`);
- one tokenizer (`REPORT.md:92-94`);
- short messages, roughly 25-50 tokens in the reported tables (`REPORT.md:127-152`);
- one prompt/scaffolding design;
- no true grammar-constrained AXON arm (`REPORT.md:250-253`);
- no frontier-model sender arm in the main M5 corpus;
- no long-running protocol/session simulation.

The paper can absolutely say "in this corpus, under this setup, AXON fails as a default." It cannot yet say "essentially never" without either a broader empirical sweep or a theorem-like argument. The current counting-unit argument is not theorem-like because the in-context deterministic case is a counterexample to its premise split.

## 10. Publication novelty is under-specified

The negative-result paper may be publishable, but not if the headline is merely "JSON+gzip beats a dense text format." The draft names this risk (`axon-falsification-pivot-claude-draft.md:57-59`, `axon-falsification-pivot-claude-draft.md:77-78`) but still calls the negative result "genuine, publishable" (`axon-falsification-pivot-claude-draft.md:72-73`).

Local venue scouting is more cautious: current maturity is a strong workshop/preprint, not Findings, and stronger venues need a size sweep plus constrained-decoding arm (`VENUES.md:8-15`, `VENUES.md:30-39`). That is the right bar.

The novel contribution is probably not the gzip result. Stronger novelty candidates are:

- the write-hard/read-easy asymmetry for novel structured notations;
- the sender-side syntactic emission floor;
- validity vs semantic fidelity separation;
- deterministic repair recovering half the failures safely;
- an adversarial falsification harness for proposed agent content formats;
- a decision-boundary framework for when token-dense notation loses to schemas/compression/read-tolerance.

If the paper leads with "essentially never," reviewers may spend their energy attacking that universal. If it leads with "a falsification campaign found the surviving region is narrower than our preregistered niche, and here is the accounting framework," it becomes harder to dismiss as folklore.

## 11. Reversibility is not as cheap as the draft says

The draft says the reputational cost of prematurely killing AXON is low because negative results are cheap to revise (`axon-falsification-pivot-claude-draft.md:54-56`). I would not rely on that. Once the project publishes "AXON earns no defensible place," the language brand is effectively burned unless the later reversal is unusually strong. That may be acceptable, but it is an opportunity cost:

- abandoning AXON v2 before testing true constrained decoding;
- losing the chance to frame AXON as a narrow audit/protocol-trace DSL;
- locking the paper into a universal negative claim that is easier to refute;
- creating inconsistency with stored project memory that previously scoped AXON into drone-C2.

The reversible move is not "publish essentially never." The reversible move is "publish the falsification framework and current negative result, with explicit surviving hypotheses scheduled for falsification."

## Unsupported or under-supported claims to revise

- "The regime where AXON wins is empty" (`axon-falsification-pivot-claude-draft.md:28-30`). Replace with: "We have not yet found a surviving general wire-format regime; the in-context deterministic-DSL regime remains untested."
- "Caching erases the density premium" (`axon-falsification-pivot-claude-draft.md:11-13`, `axon-falsification-pivot-claude-draft.md:24-25`). Replace with: "A structural-overhead sensitivity model suggests caching could shrink the edge when repeated structure is cacheable."
- "gzip is free and ubiquitous" as used with 12 B/msg (`axon-falsification-pivot-claude-draft.md:36-38`). Clarify stream vs per-message compression. The 12 B/msg result is stream-gzip, not isolated-message gzip.
- "0 of 14 survived" as decisive evidence (`axon-falsification-pivot-claude-draft.md:17-19`). Treat it as adversarial search evidence, not a representative use-case survey, unless the 14 cases and rubric are published.
- "Non-cost value was judged not to create a standalone niche" (`axon-falsification-pivot-claude-draft.md:49-50`). There is no measurement of auditability, deterministic tooling, human review, replay, or protocol recovery.
- "Grammar-constrained decoding is worth a sentence, not a thesis" (`axon-falsification-pivot-claude-draft.md:69-71`). That is only justified for byte-wire positioning, not for in-context deterministic parsing.

## Missing baselines

The next paper draft should explicitly account for:

- minified compact JSON, not just natural JSON and JSON-schema envelopes;
- JSON structured outputs / function calling with strict schema, not just `json.loads`;
- TOON or another token-efficient object notation on non-tabular and nested tasks;
- YAML/codified-prompt formats, given related work on token-efficient codified communication (`paper/RELATED_WORK.md:31-37`; `debate/ecosystem-landscape-2026.md:67-70`);
- full-stack JSON+schema+state-machine with versioning and NAK/ERR equivalents;
- true grammar-constrained AXON generation, not retry-until-valid;
- a deterministic AXON normalizer / AXON-v2 relaxed grammar arm;
- protocol-session simulations with invalid response behavior;
- per-message gzip, stream gzip, and no-compression prompt-token regimes reported separately;
- binary baselines with schema negotiation overhead included, not just values-only payload bytes.

## Priority/product verdict

Pivoting away from "AXON is a general notation you should adopt" is the right product/research move. The evidence has killed that version.

Pivoting all the way to "AXON earns no defensible place" is not yet justified. It is rhetorically clean but empirically premature. The draft should narrow the conclusion to:

> Current evidence falsifies AXON as a general/default agent payload notation and closes the initially claimed large-model wire-format niche under stream compression, binary schema, and LLM-reader assumptions. A few narrow regimes remain untested, especially in-context deterministic DSL use and protocol-trace/audit use.

That version is still a strong negative result. It is also harder for a reviewer to refute with a single counterexample.

## Protocol verdict

The draft under-models protocol dynamics. AXON is not only a serialization syntax; the spec includes performatives, NAK, ERR, and versioning (`spec/SPECIFICATION.md:124-139`, `spec/SPECIFICATION.md:466-492`, `spec/SPECIFICATION.md:509-515`). A serious "agent-communication notation" paper must evaluate client behavior after invalid or unexpected responses:

- reject vs repair vs retry vs fallback;
- total token/cost/latency after failures;
- semantic validation after parse success;
- state divergence and recovery;
- schema negotiation overhead;
- version mismatch behavior.

This will probably hurt AXON on its current 1-in-3 invalid-emission floor, but that is exactly why it should be measured rather than implied.

## Final verdict: single most important next step

Run one targeted falsification experiment on the in-context deterministic-DSL regime before publishing the universal pivot.

Design it to answer one question:

> When the message is model-visible, token-billed, not compressible, and deterministically parsed by a tool, does AXON beat compact JSON / JSON-schema structured outputs / TOON / a small custom DSL at matched semantic fidelity and live client recovery cost?

Minimum viable design:

- 30-50 tasks, including the 14 current composition-heavy tasks plus longer protocol traces.
- Sender models: at least one local capable model and one frontier model.
- Conditions: AXON current, AXON+repair, AXON+true grammar constraint if available, compact JSON, JSON structured output, TOON or equivalent, and one hand-built task-specific DSL.
- Accounting: marginal incoming-message tokens, cached-prefix tokens, per-message gzip, stream gzip, and binary schema bytes reported separately.
- Client behavior: deterministic parse, semantic validation, NAK/repair/retry/fallback, total cost and latency.
- Success criterion: AXON only survives if it is lower-cost than compact JSON/TOON at matched semantic fidelity and materially better on audit/deterministic tooling than a custom DSL.

If AXON loses there too, the negative-result pivot becomes much safer and more publishable. If AXON wins there, the right paper is not "AXON as general notation"; it is "the only surviving niche for dense agent notation is in-prompt deterministic DSLs, and here is the boundary."

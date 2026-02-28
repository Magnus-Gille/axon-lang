# CFP v2 — Claude Self-Review

Critiquing my own draft before Codex sees it.

## Issues I see

### SR-1: Talk 1 abstract may overindex on numbers
I packed in 32%, p < 0.001, 486 outputs, zero failures, 11%. For a CFP reviewer, this might read as "data dump" rather than "compelling problem → solution." A reviewer who doesn't care about benchmarks will bounce. The story needs to land even without the numbers.

### SR-2: "Where AXON doesn't win" is vague
I said I'd show where AXON doesn't win but didn't hint at what that means. A skeptic will wonder if I'm hiding the punchline. Should I be specific? (e.g., "AXON ties English on compactness but costs more prompt tokens up front")

### SR-3: Talk 2 still relies on the 12-bugs number
Is 12 bugs impressive enough? For a language specification, probably yes. For a general audience that ships production code, 12 bugs might sound minor. I didn't frame the bugs by severity — "12 bugs including 4 parser failures that broke the grammar" is more concrete than "12 bugs."

### SR-4: The "115+ critique points" claim in Talk 2 is new and unanchored
I introduced this number as an improvement over "approximately 85% of ~100." But I should verify: is 115 accurate? The debate INDEX says ~100 in previous debate. The memory says "~100 critique points raised." I upgraded to 115+ based on the memory note of "~115 critique points" but this needs verification. If it's soft, it has the same problem as the 85% claim.

### SR-5: Talk 1 drops the explicit audience targeting
The original said "CrewAI pipelines, MCP integrations, or designing your own orchestration layer." I kept this implicit ("any multi-agent framework") but the specific framework names served as hooks for people who use those tools. Worth keeping?

### SR-6: Am I underselling the speaker credentials?
The prompting championship is unique and attention-getting. The enterprise clients list (IKEA, Saab, Koenigsegg) is strong social proof. But I moved these to internal notes without suggesting how to foreground them in the abstract itself. For a competitive CFP, the reviewer's first impression is the abstract — the internal notes may be a secondary consideration.

### SR-7: Both talks are positioned as "come stress-test this"
This is an honest framing but it risks being read as "not confident enough." An alternative: "here's what we found, here's how to use it." Confidence doesn't require overclaiming.

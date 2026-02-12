# Making the Adversarial AI Debate Methodology Publishable

**Author**: Claude Code (draft for adversarial review)

## The claim we want to support

"Structured adversarial review between two AI systems (different model families) catches real issues that a single AI working alone would miss, at low cost, and produces measurably better research artifacts."

Three sub-claims:
1. The critiques are **valid** (not hallucinated concerns)
2. The adversarial cross-model setup **adds value** over self-review
3. It's **cost-effective** compared to human review

## Proposed study design

### Data collection per debate

For every critique point raised by either side:
- **ID**: Unique identifier
- **Source**: Which round, which reviewer
- **Classification**: Valid / Partially valid / Invalid (false positive)
- **Impact**: Led to artifact change / Acknowledged no change / Rejected
- **Severity**: Critical (would cause real problems) / Major (significant improvement) / Minor (cosmetic/style)
- **Novelty**: Caught by self-review? (requires ablation control)

### Ablation conditions (3 conditions per artifact)

For each artifact under review, run:
1. **Self-review**: The authoring AI (Claude) critiques its own draft
2. **Non-adversarial cross-model**: Codex reviews with neutral prompt ("please review this document")
3. **Adversarial cross-model**: Codex reviews with adversarial prompt ("critique this skeptically, find weaknesses")

This lets us isolate:
- Cross-model value: condition 2 vs 1 (does a different model find different things?)
- Adversarial framing value: condition 3 vs 2 (does skeptical prompting matter?)
- Combined value: condition 3 vs 1 (the full effect)

### Cost tracking

Per invocation: input tokens, output tokens, API cost, wall-clock time, model version.

### Human validation

The project author rates a sample (~30 points) of critique points for:
- Was this a real issue? (ground truth for validity)
- Would you have caught this yourself? (ground truth for novelty)
- How important was this? (ground truth for severity)

### Sample size

We already have ~115 critique points from 3 completed debates. With 3-5 more debates (which we'll run anyway for AXON development), we'd have ~200-250 points. With 3 ablation conditions, that's ~600-750 data points across conditions.

## Metrics

Primary:
- **Precision**: valid critiques / total critiques (per condition)
- **Unique issue rate**: issues caught by this condition but not others
- **Cost per valid critique**: API dollars per valid issue found

Secondary:
- **Severity distribution**: do adversarial reviews find more critical issues?
- **False positive rate**: do adversarial reviews produce more noise?
- **Convergence speed**: how many rounds until diminishing returns?

## Practical changes needed now

1. **Structured critique format**: Each debate should output critique points as a tagged list, not just prose
2. **Self-review step**: Before every Codex invocation, Claude self-reviews the draft
3. **Non-adversarial control**: For at least some debates, run Codex without adversarial framing
4. **Cost logging**: Capture token counts from every invocation
5. **Retroactive classification**: Go back and classify existing ~115 critique points

## What changes in the debate skill

The `/debate-codex` skill would be updated to:
1. Add a self-review step (Step 1.5: Claude critiques its own draft before sending to Codex)
2. Add a non-adversarial Codex run as control (Step 2.5)
3. Output a structured JSON log alongside the markdown files
4. Track costs per invocation

## Publication framing

**Title direction**: "Adversarial Cross-Model Review: Using Competing AI Systems to Improve Research Artifact Quality"

**Venue targets**: Workshop at NeurIPS/ICML on AI-assisted research, CHI/CSCW short paper, or meta-science venue.

**What makes it publishable regardless of outcome**: If adversarial review doesn't beat self-review, that's useful — it tells practitioners not to bother with the extra complexity.

## Risks and limitations

- Small sample of artifacts (all from one project)
- Human rater is also the project author (bias risk)
- Both AI systems may share blind spots (training data overlap)
- Generalizability: does this work beyond language/spec design?

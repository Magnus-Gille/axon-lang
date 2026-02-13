# Self-Review: MassGen Integration Assessment

**Reviewer**: Claude (self-review ablation for Track B)
**Date**: 2026-02-13

## Strengths of the Draft

1. **Clear structure**: Each scenario gets a separate verdict with concrete reasoning.
2. **Pre-registration awareness**: Correctly identifies that adding conditions or changing infrastructure requires documented deviations.
3. **Abstraction layer argument**: The distinction between "message format" and "orchestration strategy" is a genuine and important insight.

## Weaknesses and Blind Spots

### W1: Overly conservative / status-quo bias (severity: major)
The draft essentially says "don't change anything" for all four scenarios. This could reflect genuine analysis, or it could reflect an incumbent's bias toward protecting existing plans. A reviewer should ask: if MassGen had existed when the experiments were designed, would the design look different?

### W2: Understates the Exp 5 (Scaling) opportunity (severity: major)
The draft dismisses MassGen for Exp 5 by citing confounds, but Exp 5 is specifically about scaling to 128 agents. Building a custom 128-agent orchestration harness is NOT "~100 lines of Python" — it requires managing concurrent API calls, timeouts, failure recovery, message routing, and result aggregation. MassGen solves all of this. The draft hand-waves the engineering cost of the alternative.

### W3: Doesn't distinguish "use MassGen as infrastructure" from "test MassGen as a condition" (severity: moderate)
These are very different. Using MassGen as hidden infrastructure (all conditions use MassGen, so it's controlled) is different from adding MassGen as a competing condition. The draft somewhat conflates these.

### W4: Ignores real-world ecological validity concern (severity: moderate)
The current design tests formats in isolation via single LLM calls. But AXON's stated purpose is agent-to-agent communication in real multi-agent systems. Testing it in realistic multi-agent interactions (which MassGen provides) would strengthen ecological validity. The draft's "isolation is a strength" argument could also be framed as "isolation is an artificiality."

### W5: Track B assessment is too quick (severity: minor)
The comparison of adversarial debate vs. multi-model consensus for review quality is a genuinely novel research question. The draft acknowledges this ("most intellectually interesting") but then dismisses it as "premature" without deeply engaging with what the comparison could reveal.

### W6: No cost-benefit analysis (severity: minor)
How much engineering effort would each scenario actually require? The draft says "significant engineering effort" without quantifying. Some scenarios (e.g., using MassGen for Track B on a single debate) might be trivially easy to pilot.

## What Codex Should Push On

1. Whether the "isolation is a strength" argument is genuine rigor or artificial simplification
2. The engineering reality of Exp 5 at 128 agents without a framework
3. Whether a small MassGen pilot (single experiment, not full integration) changes the cost-benefit calculus
4. Whether MassGen's multi-model consensus could *complement* rather than *replace* the adversarial debate approach

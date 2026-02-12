---
name: debate-codex
description: Run an adversarial debate with Codex to stress-test a draft, plan, research claim, or experiment design. Use this whenever you need structured critique before finalizing decisions.
argument-hint: [topic or file to debate]
---

# Adversarial Debate with Codex

Run a structured adversarial review using the Codex CLI. This skill handles the full debate lifecycle: drafting, invoking Codex, responding, and recording outcomes.

## Codex CLI Invocation

**Correct syntax:**
```bash
codex exec --full-auto "<prompt>" 2>&1
```

**Important rules:**
- Use `codex exec --full-auto` — NOT `codex -q` or other flags
- Do NOT use the `-o` flag to capture critique content. The `-o` flag writes Codex's final conversational summary, not the file it created. Instead, instruct Codex to write its output file directly (it has workspace-write access via `--full-auto`).
- Set `--timeout 300000` on the Bash tool call (Codex can take a few minutes)
- Codex works in the repo's working directory and can read all project files

## Debate Protocol

### Step 0: Snapshot the artifact
Save a frozen copy of the artifact being reviewed. All review conditions (self-review, Codex neutral, Codex adversarial) must run against this same snapshot. This prevents confounding condition effects with artifact evolution.

### Step 1: Write the draft
Write Claude's position/assessment/plan to `debate/<topic>-claude-draft.md`.

### Step 1.5: Self-review ablation
Before invoking Codex, Claude critiques its own draft. Write to `debate/<topic>-claude-self-review.md`. This serves as the baseline condition for the methodology study (Track B). Be genuinely critical — this data is used to measure whether cross-model review adds value over self-review.

### Step 2: Invoke Codex (Round 1 critique)
```bash
codex exec --full-auto "You are acting as a grounded but adversarial reviewer for [project context].

Read the file debate/<topic>-claude-draft.md. [Additional context files to read if needed.]

Your job is to critique this. Be skeptical but intellectually honest — no strawmanning. Ground critique in evidence, not opinion. Specifically:
- [List specific questions for this debate]
- Acknowledge strengths before attacking weaknesses
- Be specific — cite concrete issues with file:line references, not vague concerns

Write your full critique to debate/<topic>-codex-critique.md in markdown format." 2>&1
```

### Step 3: Verify and recover Codex output
After Codex finishes, read the output file it was told to create. If the file is missing or contains only a summary (Codex sometimes writes a summary instead of the full critique), extract the actual critique content from the Codex execution log and write it to the correct file.

### Step 4: Write Claude's response
Read the critique carefully. Write a response to `debate/<topic>-claude-response-1.md` with:
- **Concessions** — where the critique is valid, concede explicitly
- **Partial concessions** — where partially valid, explain what you accept and what you push back on
- **Defenses** — where you disagree, defend with evidence
- **Revised positions table** — summarize what changed

### Step 5: Invoke Codex (Round 2 rebuttal)
Run Codex again, pointing it to all three files (draft, critique, response). Ask it to:
- Acknowledge which concessions are genuine and adequate
- Identify where defenses are valid vs where they dodge the point
- Flag any new issues that emerged
- Give a final verdict on the single most important next step

Write to `debate/<topic>-codex-rebuttal-1.md`.

### Step 6: Write the summary
Create `debate/<topic>-summary.md` with:
- Participants and rounds
- Concessions accepted by both sides
- Defenses accepted by Codex
- Unresolved issues
- New issues from later rounds
- Final verdict (both sides' positions)
- List of all debate files

### Step 7: Structured critique log
Create `debate/<topic>-critique-log.json` with every critique point from all rounds:

```json
[
  {
    "id": "<topic>-C01",
    "source": "codex-round-1",
    "text": "Brief description of the critique point",
    "classification": "valid | partially_valid | invalid",
    "impact": "changed | acknowledged | rejected",
    "severity": "critical | major | minor",
    "caught_by_self_review": true | false
  }
]
```

This structured data feeds the methodology study (Track B). Classification and impact should be filled after the debate concludes.

### Step 8: Log costs
Record per-invocation costs at the end of the summary file:

```
## Costs
| Invocation | Tokens (in/out) | API cost | Wall-clock time | Model version |
|------------|-----------------|----------|-----------------|---------------|
| Codex R1   | X / Y           | $Z       | Ns              | gpt-5.3-codex |
| Codex R2   | X / Y           | $Z       | Ns              | gpt-5.3-codex |
```

## Prompting Principles for Codex

- Ask Codex to **critique the specific artifact**, not generate alternatives
- Instruct it to be **skeptical but intellectually honest** — no strawmanning
- Require **evidence-grounded** critique, not opinion
- Ask it to **flag unsupported claims, missing baselines, and methodological gaps**
- Ask it to **acknowledge strengths before attacking weaknesses**
- Request **file:line references** for concrete issues

## When to Run a Debate

Per CLAUDE.md, trigger a debate for:
- New spec sections or grammar changes
- Research claims or evidence assessments
- Experiment design and methodology
- Evaluation of results before drawing conclusions
- Any major decision where blind spots could be costly

# Talk 2 — Final (Lightning Talk, 10 minutes)

**Title:** Bug Hunting with Rival AIs: How Cross-Model Debate Found 12 Bugs Self-Review Missed

**Abstract:** Across 12 structured adversarial debates between Claude and Codex, the process found 12 confirmed bugs in parser logic, grammar rules, and evaluation design — issues that initial single-model review missed. Each debate follows a fixed protocol: one model drafts, a second attacks with evidence, both sides must concede or defend, and a human logs every issue with severity and disposition.

In 10 minutes, I'll walk through the protocol, show one real bug-discovery sequence from a language specification project, and give you a reusable template: roles, prompts, concession rules, and issue-log schema. You'll know when adversarial multi-model review is worth the token cost and when standard review is enough. The technique is model-agnostic and works for specs, architecture decisions, design docs — anything where blind spots cost more than extra API calls.

**Internal Notes:** The methodology was developed during a formal benchmarking study comparing six agent communication formats across three LLMs (also submitted as a 30-min talk). Applied across 12 debates covering spec design, experiment methodology, statistical analysis, and research claims. Sweden's first AI prompting champion (2025, 300+ participants). Regular speaker on AI strategy and agentic systems for enterprise audiences.

# lmao-agent-skills

Public Agent Skills from LMaoAgent.

This repository contains practical, reusable skills for AI agents. They are designed to be useful out of the box while keeping private product internals, backend code, proprietary scoring rules, private data sources, and commercial workflows out of the public repository.

## Skills

| Skill | Use it for |
|---|---|
| `ai-signal-radar` | Turn user-provided public RSS, URLs, notes, or articles into prioritized Chinese AI signal briefs. |
| `lmao-agent-writer` | Draft long-form Chinese WeChat-style essays with a human, curious, first-person voice. |

## Install

Copy any skill folder into your agent skills directory.

For Codex-style setups:

```bash
mkdir -p ~/.codex/skills
cp -R ai-signal-radar lmao-agent-writer ~/.codex/skills/
```

For other agents, copy the folder that contains `SKILL.md` into the equivalent skills directory.

## Public Edition Boundary

These skills intentionally do not include:

- private backend services
- proprietary scoring formulas
- private source lists
- third-party branded skills or cloned public assets
- API keys, cookies, tokens, or credentials
- internal product automation pipelines
- customer data or unpublished commercial workflows

They are meant to share useful workflows and taste, not clone a private product.

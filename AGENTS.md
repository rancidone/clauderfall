# AGENTS

## Identity

The user is a senior software engineer.
You are designing and building Clauderfall with the user.
Project goal: professional-quality Discovery, Design, and workflow continuity over multi-week work.
Current direction: markdown-first artifacts, explicit skill invocation, minimal framework interference.
Operate as a technical collaborator, not as an autonomous product owner.
Assume high standards, direct communication, and low tolerance for fuzzy reasoning.

Start here:
- `docs/README.md` - top-level docs index.
- `docs/design/README.md` - canonical index for the active v3 doc set.

Doc loading policy:
- Do not read the full doc set up front.
- Lazy-load docs based on the current task.
- Read frontmatter first to identify doc type, status, updated date, and summary before reading the body.
- Frontmatter is generally short; read only the header first, generally fewer than 10 lines.
- Read the active product brief and the relevant engine/spec docs only when they are needed for the current task.

How to work:
- Read the relevant docs before proposing or making changes.
- Prefer the smallest sufficient set of docs for the current task.
- Work with the user as a peer engineer: be direct, concrete, and technically rigorous.
- Do not make product or architecture assumptions that are not grounded in the docs or current discussion.
- Raise ambiguities, contradictions, and weak assumptions early.
- Prefer small, reviewable changes over broad speculative rewrites.
- Keep terminology consistent across docs and code.
- Keep Discovery and Design as first-class concepts.
- Treat `/handoff` and `/continue` as explicit workflows, not automatic startup behavior.
- When you change or add docs, update `docs/README.md`.
- Update `docs/design/README.md` when changing or renaming design docs.

When editing docs:
- Keep terminology consistent with the active v3 documentation set.
- Update `docs/README.md` when adding or renaming docs.
- Update `docs/design/README.md` when adding or renaming design docs.

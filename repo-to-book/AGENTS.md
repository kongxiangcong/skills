# Project conventions

This project ships two independently installable skills, not an agent runtime.

- repo-to-research: Codex planning, delegated source/web research, actual figure production; stops at handoff.
- repo-to-write: explicitly invoked, platform-neutral writing; HTML by default, PDF only on request.
- Neither script calls a model API. Never introduce automatic stage chaining.
- Keep both copies of scripts/handoff.py identical; the test suite checks the portable contract stays synchronized.
- Do not claim mock adapter tests validate a real Codex multi-agent or imagegen run.
- Run `python -m unittest discover -s tests -v`.
- For HTML regression: `python skills/repo-to-write/scripts/book.py build examples/mini-pipeline/publication`.
- Only dependencies needed for HTML belong in requirements.txt. Browser/PDF dependencies are optional.
- Source archives must not include fonts, credentials, caches, or unrelated working files.

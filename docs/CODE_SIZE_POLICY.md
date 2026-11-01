# Combat Runtime Module Size Policy

Effective October 31, 2026.

- **Preferred size:** 150 lines or fewer. This is a guideline, not a hard check.
- **Hard limit:** **200 physical lines** for Python and JavaScript combat/save runtime files covered by `backend/tests/test_save_runtime_line_limits.py`.
- **201–250 lines:** Refactor before merge for modules governed by the hard limit; for other modules review for split points.
- **Over 250 lines:** Split into cohesive reusable modules.
- **Exception:** Existing large legacy files outside the enforced runtime list remain governed by their own tests and refactoring plans; this change does not expand the scope of the gate.
- **Architecture remains mandatory:** Universal combat primitives, source-defined parameters, explicit state lifecycles, fail-closed validation, meaningful error logging, and Python/browser parity. Do not create monster-specific resolvers to work around file size.
- **Historical documents:** Statements that earlier PRs complied with a 150-line limit describe the policy then; current prospective enforcement is 200 lines.

The enforced list and numeric ceiling live in `backend/tests/test_save_runtime_line_limits.py`. When adding a new split save-runtime module, add its path to the enforced list.

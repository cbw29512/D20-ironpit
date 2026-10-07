# Violet Fungus random sequence audit

Owner ChatGPT; `feat/2014-violet-fungus-repeat`. Exact starting main `8a5d37360aaf49f65198f4b145fe32a5af42e251`. Printed source: Multiattack makes 1d4 Rotting Touch attacks; each is +2, reach 10 feet, 1d8 Necrotic damage. Existing dice pool service and ordinary attack loop are reused. Only immutable random whole-sequence repetition/expansion was missing (`ENGINE_TRULY_MISSING` for that small parameter). No new attack resolver or source-name dispatch.

Optional `AttackSequenceRepetition` is on a complete sequence variant. Strict integer dice, unknown-field rejection and maximum eight expanded slots are validated before spending or rolling, including unselected variants. Source proof checks exact wording/dice/policy, one single-attack slot, every ID and printed name. Preview uses the existing printed mean damage policy: 2.5 repetitions × 4.5 damage = 11.25. Preview never rolls; an independently legal follow-up is not invented.

Resolution selects the complete variant first, spends one Action, uses the shared dice pool once, records an auditable feature-roll event, freezes the expanded slot list, then runs ordinary attacks with normal retargeting and interruption. Natural 1 ends the normal turn. Dead targets may be replaced because source does not require the same target. No legal target means no Action spend/count roll. Count is local to this Action; immutable source/cards and fresh fight state reset normally.

Focused evidence: 70 Python source/schema/sequence cases; seven new browser scenarios (d4 counts 1–4, natural 1, retarget after a kill, no range/no spend/no roll), plus affected Grick/complete-sequence/Veteran browser fixtures passed. Checked-in source/compiler/browser JSON fixture verifies roll order, count, dice, HP, audit event, costs and fresh reset. No duplicate full local suites. Required generators verify branch 191/327, 136 blocked. Complete, merged #635.

Native 2024 audit: Violet Fungus has two Rotting Touch attacks, +2, reach 10 feet, 1d8 Necrotic. It has no random-count source requirement; fixed two-attack binding remains unchanged and gets no 2014 repetitions field. 2024 readiness stays 141/330.

## Final acceptance

Feature head `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`, merged source `f351f8ca725b2fea8789bbb0a79757b7a99b57de`. Final CI passed 2800 Python tests and all 222 browser commands. 2014 is 191/327, 136 blocked; native 2024 is 141/330; heroes 240/240 each. All four required exact-head gates succeeded:

- [CI](https://github.com/cbw29512/D20-ironpit/actions/runs/37572593683): success on `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`.
- [2014 Basic Roster](https://github.com/cbw29512/D20-ironpit/actions/runs/37572593740): success on `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`.
- [Paired Edition Monster Report](https://github.com/cbw29512/D20-ironpit/actions/runs/37572593727): success on `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`.
- [2014 Hero Certification](https://github.com/cbw29512/D20-ironpit/actions/runs/37572593731): success on `4508f7747a9f51df306b9ae8d4c12a0c6d2cc0ff`.

Later documentation-only commits carry no inherited exact-head CI claim. Netlify remains locked.

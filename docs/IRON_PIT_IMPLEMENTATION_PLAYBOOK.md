# Iron Pit Implementation Playbook

This is the small routing file for implementation work.

Always read `SOUL.md` first, then read **only the guide for the work you are doing**:

- Monsters: `docs/playbooks/MONSTERS.md`
- Universal engine/schema/runtime: `docs/playbooks/UNIVERSAL_ENGINE.md`
- Pregens/classes/subclasses/spells/features: `docs/playbooks/PREGENS.md`

Also read `docs/CURRENT_OPERATING_STATUS.md` for the current queue.

## Shared rule

**Implement what the effect does, not what the source calls it.**

Source/card data owns printed names and parameters. The universal engine owns mechanics.
Combat mutation lives only in fight state. Python and browser must resolve the same semantics.

## Escalation

Do not repeatedly load every long contract for routine work. Open the detailed authority only when
the selected small guide says to, when the touched subsystem requires it, or when source wording,
timing, architecture, or existing behavior is uncertain.

Repository source and permanent tests remain the final implementation truth.

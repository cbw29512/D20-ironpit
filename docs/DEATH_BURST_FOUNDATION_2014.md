# 2014 Death Burst semantic family foundation

Source-verified 2014 Monster Manual Death Burst traits. Highest-yield remaining family not covered by open PRs. Affects Dust Mephit, Ice Mephit, Magma Mephit, Magmin, Steam Mephit (and Balor Death Throes as related on-death area).

## Source (2014)

- **Dust Mephit**: When the mephit dies, it explodes in a burst of dust. Each creature within 5 feet of it must then succeed on a DC 10 Constitution saving throw or be blinded for 1 minute. A blinded creature can repeat the saving throw on each of its turns, ending the effect on itself on a success.
- **Ice Mephit**: When the mephit dies, it explodes in a burst of jagged ice. Each creature within 5 feet of it must make a DC 10 Dexterity saving throw, taking 4 (1d8) slashing damage on a failed save, or half as much damage on a successful one.
- **Magma Mephit**: When the mephit dies, it explodes in a burst of lava. Each creature within 5 feet of it must make a DC 11 Dexterity saving throw, taking 7 (2d6) fire damage on a failed save, or half as much damage on a successful one.
- **Steam Mephit**: When the mephit dies, it explodes in a cloud of steam. Each creature within 5 feet of the mephit must succeed on a DC 10 Dexterity saving throw or take 4 (1d8) fire damage.
- **Magmin**: (Death Burst present; source-verify exact text on implementation).

## Semantic decomposition

Trigger: source reaches 0 HP / dies. Range: 5 ft. Save ability/DC from source. On fail: condition (Blinded, timed with repeat save) or typed damage (half on success where printed). No name dispatch. Reuse existing `generic-death-triggers` (partial), saving-throws, timed-condition-lifecycle-repeat-save, typed-damage-resistance-immunity-vulnerability, zero-hp-death-lifecycle.

## Plan

Bind via universal death-trigger primitive. Source cards supply DC, save ability, damage dice/type, condition, duration, range. Python/browser parity required. Tests for each variant. Do not claim admission until exact-head CI. Frog/Stirge remain arena-classified. No fidelity weakening.

Generated blockers/inventory remain generator-owned.

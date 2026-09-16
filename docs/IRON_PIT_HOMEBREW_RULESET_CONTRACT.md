# Iron Pit Homebrew and Ruleset Contract

This document is an authoritative companion to `docs/IRON_PIT_RULES_CONTRACT.md`. It extends that contract without replacing or weakening any existing Iron Pit rule. If this document and the main rules contract appear to conflict, stop the conflicting implementation and require an explicit product decision before changing combat behavior.

## Locked architecture

- Iron Pit uses one universal combat engine.
- Shared combat concepts such as attacks, saves, damage components, movement, Prone, Blinded, Grappled, Restrained, resources, timing windows, concentration, reactions, and life states are reusable universal capabilities.
- Creature-, class-, spell-, feat-, item-, and homebrew-specific behavior is represented as immutable data/attributes composed from those capabilities whenever a universal mechanic can represent it.
- Combat creates fresh temporary mutable state and never mutates the source definition.
- Step, Watch, Replay, and Turbo consume the same resolver.

## Hard edition isolation

Iron Pit supports distinct ruleset profiles. Edition selection is a hard boundary.

### 2014 mode

A 2014 fight may use only 2014-profile rules and options, including 2014 monsters, pregens, spells, equipment, features, conditions, action-economy semantics, and 2014 homebrew definitions.

### 2024 mode

A 2024 fight may use only 2024-profile rules and options, including 2024 monsters, pregens, spells, equipment, features, conditions, action-economy semantics, and 2024 homebrew definitions.

- Never cross editions in one fight.
- A shared concept is not duplicated into a second combat engine merely because edition-specific semantics differ. The selected ruleset profile supplies the appropriate semantics/data to the universal capability.
- Certification is ruleset-specific.
- Until a ruleset profile and its required content are implemented and certified, do not claim that profile is production-ready.

## Ruleset-specific homebrew builders

Provide distinct 2014 and 2024 homebrew creation surfaces.

- The 2014 builder exposes only options and primitives valid for the 2014 profile.
- The 2024 builder exposes only options and primitives valid for the 2024 profile.
- Cross-edition selections are rejected before combat.
- Prefer constrained forms: selectors, numeric inputs, dice expressions, damage components, timing selectors, conditions, resources, attack/save configuration, movement, equipment, spells, features, and other structured fields backed by known engine capabilities.
- Do not use arbitrary executable user rules as a shortcut around the universal engine or ruleset validation.

## Homebrew monsters and pregens

Homebrew monsters and pregens are immutable combatant definitions assembled from ruleset-valid engine capabilities.

A creator may intentionally choose extreme values and combinations. For example, a ruleset-valid homebrew creature may have AC 28, wield configured weapons, deal multiple dice plus flat modifiers, and add a fire-damage rider if those components are representable by the selected ruleset/profile and universal engine.

Iron Pit validates mechanical representability and edition isolation. It does not enforce encounter balance.

This architecture is intentionally combinatorial: a relatively small catalog of certified universal capabilities and ruleset-specific options should support very large numbers of homebrew combinations without adding creature-name or class-name combat branches.

## Validation and compatibility

- Official content earns ruleset-specific RAW certification only through the established source/build/runtime/fingerprint/resource audits and Python/browser parity gates.
- Homebrew is never labeled RAW Certified merely because it uses official components.
- Homebrew assembled entirely from supported capabilities may be labeled `2014 Engine Compatible` or `2024 Engine Compatible`, matching its declared profile.
- Unsupported combat-relevant mechanics fail closed and identify the unsupported component before the fight starts.
- Saved, duplicated, imported, exported, or shared homebrew retains its ruleset identity and must be revalidated against that same profile before combat.
- Homebrew compatibility records remain separate from official certification manifests.

## Development discipline

- Prefer high-leverage universal primitives that unlock official monsters, official pregens, and many homebrew combinations simultaneously.
- Never add monster-specific, class-specific, or homebrew-name-specific resolver branches when immutable data plus a universal capability can represent the behavior.
- Every new universal primitive requires Python reference behavior, browser parity, audit-grade logging, and permanent regression coverage where applicable.
- Ruleset-specific behavior must be explicit and testable.
- Homebrew builders consume ruleset capability catalogs; they do not become alternate combat engines.

## Product invariant

The permanent model is:

`one universal combat engine -> selected 2014 or 2024 ruleset profile -> ruleset-valid official or homebrew content -> fresh combat state -> shared Step/Watch/Replay/Turbo resolver`

This invariant must be considered during all future Iron Pit architecture, certification, content, UI, import/export, and homebrew work.

(() => {
  "use strict";

  const clone = (value) => structuredClone(value);

  function sourceVariants(source) {
    const action = source.attack_action;
    if (!action) return [];
    if (action.variants?.length) {
      return action.variants.map((row) => ({ ...clone(row), id: source.id + ":" + row.id }));
    }
    return [{ id: source.id + ":" + action.id, slots: clone(action.slots || []) }];
  }

  function composeMonsterFormAttackSequences(owner, form) {
    // Pure composition, NOT eligibility or live action registration.
    if (owner?.kind !== "monster" || form?.kind !== "monster") {
      throw new Error("Only monster sources can compose monster form attacks.");
    }
    if (owner.ruleset !== form.ruleset) {
      throw new Error("Cannot combine different edition attack sequences.");
    }
    const before = owner.attack_action, gained = form.attack_action;
    if (!before && !gained) return null;
    if (!before) return clone(gained);
    if (!gained) return clone(before);
    if (JSON.stringify(before) === JSON.stringify(gained)) return clone(before);
    if (before.name !== gained.name) {
      throw new Error("Distinctly named Actions require separately authorized action binding.");
    }
    const variants = [...sourceVariants(owner), ...sourceVariants(form)];
    if (variants.length > 16 || new Set(variants.map((row) => row.id)).size !== variants.length) {
      throw new Error("Source form Attack Action alternatives exceed the universal limits.");
    }
    // Full sequences remain mutually exclusive; form capabilities and all
    // referenced attack/save IDs must be compiled before this becomes live.
    return {
      id: owner.id + "--form-" + form.id + "--attack-options",
      name: before.name,
      variants,
      isAttackAction: Boolean(before.isAttackAction && gained.isAttackAction),
    };
  }

  window.IRON_PIT_BROWSER_MONSTER_FORM_ATTACK_OPTIONS = { composeMonsterFormAttackSequences };
})();

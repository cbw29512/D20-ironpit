(() => {
  "use strict";

  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const M = () => window.IRON_PIT_BROWSER_MODIFIERS;
  const P = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const R = () => window.IRON_PIT_BROWSER_ROLLS;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function spellLevel(source, effectId) {
    const template = source.state.template;
    const spells = [
      ...(template.defensive_spell_actions || []),
      ...(template.spell_save_actions || []),
      ...(template.spell_attack_actions || []),
    ];
    return spells.find((spell) => spell.id === effectId)?.level ?? null;
  }

  function targetAllowed(remover, target, action) {
    if (!target.state.is_alive || target.state.is_dead || S().distance(remover, target) > action.range) return false;
    const same = remover.side === target.side;
    if (action.targetMode === "enemy") return !same;
    if (action.targetMode === "ally") return same && remover.combatant_id !== target.combatant_id;
    if (action.targetMode === "self_or_ally") return same;
    return true;
  }

  function effects(remover, setup, action) {
    const members = [...setup.heroes, ...setup.monsters];
    const byId = Object.fromEntries(members.map((member) => [member.combatant_id, member]));
    const found = new Map();
    for (const target of members) {
      if (!targetAllowed(remover, target, action)) continue;
      for (const modifier of target.state.active_modifiers || []) {
        const source = byId[modifier.source_id]; if (!source) continue;
        const level = spellLevel(source, modifier.source_effect_id); if (level == null) continue;
        const key = [target.combatant_id, source.combatant_id, modifier.source_effect_id].join(":");
        found.set(key, { target, source, effectId: modifier.source_effect_id, spellLevel: level });
      }
    }
    return [...found.values()].sort((a, b) => b.spellLevel - a.spellLevel
      || S().distance(remover, a.target) - S().distance(remover, b.target)
      || a.effectId.localeCompare(b.effectId));
  }

  function choose(remover, setup, turnKey) {
    for (const action of remover.state.template.effect_removal_actions || []) {
      if (!E().available(remover.state, action.actionCost)) continue;
      if (action.expendsSpellSlot && !P().slotSpellAvailable(remover.state, turnKey)) continue;
      if (action.resourceId && (remover.state.resources[action.resourceId] || 0) < (action.resourceCost || 1)) continue;
      const candidates = effects(remover, setup, action);
      if (candidates.length) return { action, effect: candidates[0] };
    }
    return null;
  }

  function resolve(sequence, round, remover, setup, action, effect, turnKey) {
    if (!effects(remover, setup, action).some((item) =>
      item.target.combatant_id === effect.target.combatant_id
      && item.source.combatant_id === effect.source.combatant_id && item.effectId === effect.effectId)) {
      throw new Error("Tracked spell effect is no longer a legal removal target.");
    }
    E().spend(remover.state, action.actionCost);
    let remaining = null;
    if (action.resourceId) {
      if (action.expendsSpellSlot) P().markSlotSpellCast(remover.state, turnKey);
      remover.state.resources[action.resourceId] -= action.resourceCost || 1;
      remaining = remover.state.resources[action.resourceId];
    }
    let check = null, succeeded = true, dc = null;
    if (effect.spellLevel > (action.autoRemoveMaxLevel ?? 3)) {
      const score = remover.state.template.ability_scores?.[action.castingAbility];
      if (!Number.isInteger(score)) throw new Error("Effect removal requires a certified casting ability.");
      dc = 10 + effect.spellLevel;
      check = R().d20(Math.floor((score - 10) / 2), "normal");
      succeeded = check.total >= dc;
    }
    if (succeeded) {
      M().removeSource([effect.target.state], effect.source.combatant_id, effect.effectId);
      effect.target.state.active_buff_effect_ids = (effect.target.state.active_buff_effect_ids || [])
        .filter((id) => id !== effect.effectId);
    }
    return {
      sequence, round_number: round, event_type: "feature",
      actor_id: remover.combatant_id, actor_name: remover.state.template.name,
      target_id: effect.target.combatant_id, target_name: effect.target.state.template.name,
      ability_check_roll: check, check_ability: action.castingAbility, check_dc: dc,
      check_succeeded: check ? succeeded : null, feature_id: action.id,
      resource_remaining: remaining, removed_condition_ids: succeeded ? [effect.effectId] : [],
      animation: action.animation || "effect-removal",
      description: remover.state.template.name + " uses " + action.name + " on " + effect.effectId
        + ": " + (succeeded ? "effect ends." : "ability check fails."),
    };
  }

  window.IRON_PIT_BROWSER_EFFECT_REMOVAL = { choose, effects, resolve };
})();
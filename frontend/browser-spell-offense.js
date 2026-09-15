(() => {
  "use strict";

  const AP = () => window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
  const AR = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const C = () => window.IRON_PIT_BROWSER_SPELLCASTING;
  const RES = () => window.IRON_PIT_BROWSER_RESOURCES;

  function chooseAutomatic(caster, setup, turnKey) {
    const enemies = caster.side === "heroes" ? setup.monsters : setup.heroes;
    const candidates = [];
    for (const action of caster.state.template.automatic_spell_actions || []) {
      if (action.actionCost === "reaction" || !E().available(caster.state, action.actionCost)) continue;
      if (!C().actionResourceAvailable(caster.state, action, turnKey)) continue;
      const legal = enemies.filter((target) => target.state.is_alive && !target.state.is_dead
        && target.state.current_hp > 0 && S().distance(caster, target) <= action.range);
      if (!legal.length) continue;
      const raw = action.damageDiceCount * (action.damageDiceSize + 1) / 2 + (action.damageBonus || 0);
      const scored = legal.map((target) => ({
        target,
        damage: A().adjustedDamage(target.state, Math.round(raw), action.damageType),
      })).sort((left, right) => right.damage - left.damage
        || left.target.state.current_hp - right.target.state.current_hp
        || left.target.combatant_id.localeCompare(right.target.combatant_id));
      const projected = Object.fromEntries(scored.map(({ target }) => [target.combatant_id, target.state.current_hp]));
      const targetIds = [];
      for (let index = 0; index < action.applications; index += 1) {
        const best = action.allowSplitTargets === false ? scored[0] : scored.reduce((current, option) => {
          const currentValue = Math.min(current.damage, projected[current.target.combatant_id]);
          const optionValue = Math.min(option.damage, projected[option.target.combatant_id]);
          if (optionValue !== currentValue) return optionValue > currentValue ? option : current;
          if (option.damage !== current.damage) return option.damage > current.damage ? option : current;
          return option.target.combatant_id < current.target.combatant_id ? option : current;
        });
        targetIds.push(best.target.combatant_id);
        projected[best.target.combatant_id] = Math.max(0, projected[best.target.combatant_id] - best.damage);
      }
      const expectedDamage = targetIds.reduce((sum, id) => sum + scored.find((item) => item.target.combatant_id === id).damage, 0);
      candidates.push({ action, targetIds, expectedDamage });
    }
    candidates.sort((a, b) => b.expectedDamage - a.expectedDamage || a.action.level - b.action.level
      || a.action.id.localeCompare(b.action.id));
    return candidates[0] || null;
  }

  function resolveAutomatic(sequence, round, caster, setup, choice, turnKey) {
    const action = choice.action, fallbackId = `spell-slot-${action.level}`;
    if (!E().available(caster.state, action.actionCost)) throw new Error(`${action.name} cannot be cast in this action window.`);
    const resourceId = RES().resolvedId(action.resourceId, fallbackId);
    const usesSpellSlot = Boolean(resourceId && resourceId.startsWith("spell-slot-"));
    if (usesSpellSlot && !C().slotSpellAvailable(caster.state, turnKey)) throw new Error(`A leveled spell was already cast this turn before ${action.name}.`);
    if (!RES().actionAvailable(caster.state, action.resourceId, action.resourceCost || 1, fallbackId)) throw new Error(`Resource ${resourceId} is unavailable for ${action.name}.`);
    const members = new Map([...setup.heroes, ...setup.monsters].map((member) => [member.combatant_id, member]));
    if (choice.targetIds.length !== action.applications) throw new Error(`${action.name} requires exactly ${action.applications} automatic applications.`);
    for (const id of choice.targetIds) {
      const target = members.get(id);
      if (!target || target.side === caster.side || target.state.is_dead || !target.state.is_alive || S().distance(caster, target) > action.range) throw new Error(`Illegal automatic spell target ${id} for ${action.name}.`);
    }
    const remaining = RES().spendAction(caster.state, action.resourceId, action.resourceCost || 1, fallbackId);
    if (usesSpellSlot) C().markSlotSpellCast(caster.state, turnKey);
    E().spend(caster.state, action.actionCost);
    const events = [{ sequence: sequence++, round_number: round, event_type: "feature", actor_id: caster.combatant_id,
      actor_name: caster.state.template.name, feature_id: action.id, resource_remaining: remaining,
      animation: action.animation || "spell-automatic", description: `${caster.state.template.name} casts ${action.name}; ${action.applications} automatic applications resolve.` }];
    const states = [...setup.heroes, ...setup.monsters].map((member) => member.state);
    choice.targetIds.forEach((id, index) => {
      const target = members.get(id), rolls = window.IRON_PIT_DICE.rollMany(action.damageDiceCount, action.damageDiceSize);
      const raw = Math.max(0, rolls.reduce((sum, value) => sum + value, 0) + (action.damageBonus || 0));
      const applied = A().adjustedDamage(target.state, raw, action.damageType), hpBefore = target.state.current_hp;
      A().applyDamage(target.state, applied, false, applied > 0 ? [action.damageType] : [], states);
      const notation = `${action.damageDiceCount}d${action.damageDiceSize}+${action.damageBonus || 0}`;
      events.push({ sequence: sequence++, round_number: round, event_type: "feature", actor_id: caster.combatant_id,
        actor_name: caster.state.template.name, target_id: target.combatant_id, target_name: target.state.template.name,
        feature_id: action.id, damage_roll: { notation, rolls, modifier: action.damageBonus || 0, total: applied },
        damage_components: [{ source: `${action.name} application ${index + 1}`, notation, rolls: [...rolls],
          modifier: action.damageBonus || 0, damage_type: action.damageType, total: raw, applied_total: applied }],
        hp_before: hpBefore, hp_after: target.state.current_hp, animation: action.animation || "spell-automatic",
        description: `${action.name} application ${index + 1} deals ${applied} ${action.damageType} damage to ${target.state.template.name}.` });
    });
    return { events, sequence };
  }

  function resolve(sequence, round, member, setup, turnKey) {
    const attack = AP()?.choose(member, setup, turnKey) || null;
    const save = SP()?.choose(member, setup, turnKey) || null;
    const automatic = chooseAutomatic(member, setup, turnKey);
    const candidates = [["attack", attack], ["save", save], ["automatic", automatic]].filter(([, choice]) => choice);
    if (!candidates.length) return { events: [], sequence };
    candidates.sort((left, right) => right[1].expectedDamage - left[1].expectedDamage
      || left[1].action.level - right[1].action.level || left[0].localeCompare(right[0]));
    const [kind, choice] = candidates[0];
    if (kind === "attack") {
      const event = AR().resolve(sequence++, round, member, choice.target, choice.action, setup, turnKey);
      return { events: [event], sequence };
    }
    if (kind === "automatic") return resolveAutomatic(sequence, round, member, setup, choice, turnKey);
    return SR().resolve(sequence, round, member, setup, choice, turnKey);
  }

  window.IRON_PIT_BROWSER_SPELL_OFFENSE = { resolve, chooseAutomatic, resolveAutomatic };
})();
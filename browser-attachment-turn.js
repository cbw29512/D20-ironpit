(() => {
  "use strict";

  // The source and target IDs are fight-local; printed labels come from card data.
  const A = () => window.IRON_PIT_BROWSER_ATTACHMENTS;
  const members = (setup) => [...setup.heroes, ...setup.monsters];
  const alive = (member) => Boolean(member && member.state.is_alive && !member.state.is_dead);

  function cleanup(setup) {
    try {
      if (setup.attachments == null) setup.attachments = [];
      if (!Array.isArray(setup.attachments)) throw Error("Encounter attachment state is malformed.");
      const index = new Map(members(setup).map((member) => [member.combatant_id, member]));
      let links = setup.attachments;
      for (const row of [...links]) {
        if (!alive(index.get(row.source_id)) || !alive(index.get(row.target_id))) {
          links = A().detach(links, row.source_id, row.effect_id);
        }
      }
      setup.attachments = links;
    } catch (error) { console.error("Attachment cleanup failed", error); throw error; }
  }

  function resolve(sequence, round, owner, setup) {
    try {
      cleanup(setup);
      const events = [];
      if (!alive(owner) || owner.state.current_hp <= 0) return { events, sequence };
      const index = new Map(members(setup).map((member) => [member.combatant_id, member]));
      const states = members(setup).map((member) => member.state);
      for (const row of [...setup.attachments]) {
        if (row.source_id !== owner.combatant_id || row.damage_timing !== "source_turn_start") continue;
        const target = index.get(row.target_id);
        if (!alive(target)) continue;
        const before = target.state.current_hp;
        let rolled = 0;
        const rolls = [];
        for (let i = 0; i < row.damage_dice_count; i += 1) {
          const die = window.IRON_PIT_DICE.roll(row.damage_dice_size);
          rolls.push(die);
          rolled += die;
        }
        const total = Math.max(0, rolled + row.damage_bonus);
        let lost, effectText, damageComponents = [];
        if (row.periodic_effect_kind === "direct_hp_loss") {
          const loss = window.IRON_PIT_BROWSER_START_OF_TURN_TIMED_BURN?.loseHitPoints;
          if (!loss) throw Error("Universal direct HP-loss resolver is not loaded.");
          lost = loss(target.state, total, states);
          effectText = `drains ${lost} Hit Points (not damage)`;
        } else if (row.periodic_effect_kind === "typed_damage") {
          const rules = window.IRON_PIT_BROWSER_DAMAGE_DEFENSE_RULES;
          const attack = window.IRON_PIT_BROWSER_ATTACK;
          if (!rules?.resolveDamage || !attack?.applyDamage) {
            throw Error("Universal typed damage resolvers are not loaded.");
          }
          const result = rules.resolveDamage(target.state, total, row.damage_type);
          attack.applyDamage(target.state, result.applied, false, [row.damage_type],
            states, setup, [], owner.combatant_id);
          lost = Math.max(0, before - target.state.current_hp);
          effectText = `deals ${result.applied} ${row.damage_type} damage`;
          damageComponents = [{
            source: row.source_name,
            notation: `${row.damage_dice_count}d${row.damage_dice_size}+${row.damage_bonus}`,
            rolls, modifier: row.damage_bonus,
            damage_type: row.damage_type, total: total,
          }];
        } else throw Error("Unknown source-owned periodic attachment effect kind.");
        setup.attachments = A().recordHpLoss(setup.attachments, row.source_id, row.effect_id, lost);
        const detached = !setup.attachments.some((item) =>
          item.source_id === row.source_id && item.effect_id === row.effect_id);
        const changes = detached ? [{
          operation: "detach", source_id: row.source_id, target_id: row.target_id,
          effect_id: row.effect_id, source_name: row.source_name,
        }] : [];
        events.push({
          sequence: sequence++, round_number: round, event_type: "feature",
          actor_id: owner.combatant_id, actor_name: owner.state.template.name,
          target_id: target.combatant_id, target_name: target.state.template.name,
          feature_id: row.source_name, damage_components: damageComponents,
          ...(changes.length ? { attachment_changes: changes } : {}),
          hp_before: before, hp_after: target.state.current_hp,
          is_dead: target.state.is_dead, animation: "feature",
          description: `${owner.state.template.name}: ${row.source_name} ${effectText} at its turn start.`,
        });
        if (!alive(target)) cleanup(setup);
      }
      return { events, sequence };
    } catch (error) {
      console.error("Attachment start-of-turn failed", { owner: owner?.combatant_id, error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_ATTACHMENT_TURN = { cleanup, resolve };
})();

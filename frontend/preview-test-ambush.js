(() => {
  "use strict";

  const catalog = window.IRON_PIT_TEST_ROSTER;
  const engine = window.IRON_PIT_TEST_ENGINE;
  const effects = window.IRON_PIT_EFFECTS;

  function hiddenChange(actorId, operation) {
    return {
      actor_id: actorId, effect_id: "hidden", operation, kind: "buff", label: "Hidden",
      detail: "Hidden from the opponent in the supported visibility model.",
    };
  }

  function rangedProfile(template) {
    return template.attacks.find((profile) => profile.weapon.kind === "ranged") || null;
  }

  function rangeMode(profile, distance) {
    if (!profile || !profile.weapon.normalRange) return "normal";
    return distance > profile.weapon.normalRange ? "disadvantage" : "normal";
  }

  function finishTurn(actor, target, events) {
    const change = engine.statusEvent(effects.endSourceTurn([actor, target], actor.template.id));
    if (change) events.push(change);
  }

  function openingAttack(actor, target, profile, mode, events, removeHidden = false) {
    actor.sneakUsed = false;
    const event = engine.attack(actor, target, profile, mode);
    if (removeHidden) event.effect_changes = [hiddenChange(actor.template.id, "remove"), ...(event.effect_changes || [])];
    events.push(event);
    finishTurn(actor, target, events);
  }

  function buildTestAmbush(monsterId) {
    const rogueTemplate = catalog?.characters?.["mara-vale-l1"];
    const monsterTemplate = catalog?.monsters?.[monsterId];
    if (!rogueTemplate || !monsterTemplate) throw new Error("Selected ambush combatant is unavailable.");

    const rogue = { template: rogueTemplate, hp: rogueTemplate.max_hp, attackRollEffects: [], sneakUsed: false };
    const monster = { template: monsterTemplate, hp: monsterTemplate.max_hp, attackRollEffects: [], sneakUsed: false };
    const state = { distance: 60, secondWindUses: 0 };
    const events = [];
    const hideRoll = engine.d20(rogueTemplate.skill_bonuses.stealth);
    const hidden = hideRoll.total >= 15;
    events.push({
      event_type: "hide", actor_id: rogueTemplate.id, feature_id: "precombat-hide", animation: "hide",
      description: hidden ? `${rogueTemplate.name} hides before combat with Stealth ${hideRoll.total}.` : `${rogueTemplate.name} fails to hide before combat with Stealth ${hideRoll.total}.`,
      check_roll: hideRoll, effect_changes: hidden ? [hiddenChange(rogueTemplate.id, "apply")] : [],
    });

    const rogueInit = engine.d20(rogueTemplate.initiative_bonus, hidden ? "advantage" : "normal");
    const monsterInit = engine.d20(monsterTemplate.initiative_bonus, hidden ? "disadvantage" : "normal");
    events.push({ event_type: "initiative", actor_id: rogueTemplate.id, attack_roll: rogueInit, animation: "initiative", description: `${rogueTemplate.name} rolls initiative ${rogueInit.total}${hidden ? " with Invisible Advantage" : ""}.` });
    events.push({ event_type: "initiative", actor_id: monsterTemplate.id, attack_roll: monsterInit, feature_id: hidden ? "surprise" : null, animation: "initiative", description: `${monsterTemplate.name} rolls initiative ${monsterInit.total}${hidden ? " with Surprise Disadvantage" : ""}.` });

    const rogueFirst = rogueInit.total > monsterInit.total || (rogueInit.total === monsterInit.total && rogueTemplate.initiative_bonus >= monsterTemplate.initiative_bonus);
    const order = rogueFirst ? [rogue, monster] : [monster, rogue];
    let stillHidden = hidden;
    let rounds = 1;

    for (const actor of order) {
      if (rogue.hp <= 0 || monster.hp <= 0) break;
      if (actor === rogue) {
        const profile = rangedProfile(rogueTemplate);
        const mode = stillHidden ? "advantage" : rangeMode(profile, state.distance);
        openingAttack(rogue, monster, profile, mode, events, stillHidden);
        stillHidden = false;
      } else if (stillHidden) {
        const profile = rangedProfile(monsterTemplate);
        const mode = profile ? "disadvantage" : "normal";
        if (profile) openingAttack(monster, rogue, profile, mode, events);
        else engine.takeTurn(state, monster, rogue, events, "ranged");
      } else {
        engine.takeTurn(state, monster, rogue, events, "ranged");
      }
    }

    for (let round = 2; round <= 50 && rogue.hp > 0 && monster.hp > 0; round += 1) {
      rounds = round;
      for (const actor of order) {
        if (rogue.hp <= 0 || monster.hp <= 0) break;
        engine.takeTurn(state, actor, actor === rogue ? monster : rogue, events, "ranged");
      }
    }

    const winner = rogue.hp > 0 ? rogueTemplate.name : monster.hp > 0 ? monsterTemplate.name : null;
    events.push({ event_type: winner ? "victory" : "draw", actor_id: winner === rogueTemplate.name ? rogueTemplate.id : monsterTemplate.id, animation: winner ? "victory" : "draw", description: winner ? `${winner} wins the duel.` : "The duel ends in a draw." });
    return { fighter: { template: rogueTemplate }, monster: { template: monsterTemplate }, battlefield: { starting_distance_ft: 60 }, events, winner_name: winner, rounds };
  }

  window.IRON_PIT_TEST_AMBUSH = { buildTestAmbush };
})();

((root) => {
  "use strict";

  const dice = root.IRON_PIT_DICE;
  const preview = root.IRON_PIT_PREVIEW;
  const rogueWeapons = {
    shortsword: { id: "shortsword", name: "Shortsword", attackBonus: 5, damageBonus: 3, projectile: null },
    shortbow: { id: "shortbow", name: "Shortbow", attackBonus: 5, damageBonus: 3, projectile: "arrow" },
  };
  const goblinBow = { id: "shortbow", name: "Shortbow", attackBonus: 4, damageBonus: 2, projectile: "arrow" };

  function d20(modifier, mode = "normal") {
    try {
      const rolls = mode === "normal" ? [dice.roll(20)] : dice.rollMany(2, 20);
      const selected = mode === "advantage" ? Math.max(...rolls) : mode === "disadvantage" ? Math.min(...rolls) : rolls[0];
      return { notation: rolls.length === 2 ? "2d20" : "1d20", rolls, selected_roll: selected, modifier, total: selected + modifier, mode };
    } catch (error) { console.error("Rogue preview d20 failed", error); throw error; }
  }

  function rollDamage(weapon, critical, sneakAttack = false) {
    try {
      const weaponRolls = dice.rollMany(critical ? 2 : 1, 6);
      const components = [{ source: weapon.name, rolls: weaponRolls, total: weaponRolls.reduce((a, b) => a + b, 0) + weapon.damageBonus }];
      if (sneakAttack) {
        const sneakRolls = dice.rollMany(critical ? 2 : 1, 6);
        components.push({ source: "Sneak Attack", rolls: sneakRolls, total: sneakRolls.reduce((a, b) => a + b, 0) });
      }
      const rolls = components.flatMap((component) => component.rolls);
      const total = components.reduce((sum, component) => sum + component.total, 0);
      return { notation: sneakAttack ? `${critical ? 2 : 1}d6+${weapon.damageBonus} + ${critical ? 2 : 1}d6` : `${critical ? 2 : 1}d6+${weapon.damageBonus}`, rolls, modifier: weapon.damageBonus, total, components };
    } catch (error) { console.error("Rogue preview damage failed", error); throw error; }
  }

  function attack(actor, target, weapon, mode, allowSneak) {
    try {
      const roll = d20(weapon.attackBonus, mode);
      actor.hidden = false;
      const critical = roll.selected_roll === 20;
      const hit = roll.selected_roll !== 1 && (critical || roll.total >= target.template.armor_class);
      const sneakAttack = Boolean(hit && allowSneak && mode === "advantage" && !actor.sneakUsed);
      if (sneakAttack) actor.sneakUsed = true;
      const damage = hit ? rollDamage(weapon, critical, sneakAttack) : null;
      if (damage) target.hp = Math.max(0, target.hp - damage.total);
      const vex = hit && target.hp > 0 && actor.template.weapon_masteries?.includes(weapon.id);
      if (vex) actor.vex = true;
      return {
        event_type: "attack", actor_id: actor.template.id, target_id: target.template.id,
        description: `${actor.template.name}: ${critical ? "CRITICAL HIT" : hit ? "HIT" : "MISS"} with ${weapon.name}.${sneakAttack ? " Sneak Attack adds precision damage." : ""}${vex ? " Vex grants Advantage on the next attack against this target." : ""}`,
        attack_roll: roll, damage_roll: damage ? { notation: damage.notation, rolls: damage.rolls, modifier: damage.modifier, total: damage.total } : null,
        damage_components: damage?.components || [], hit, critical, hp_after: target.hp,
        weapon_id: weapon.id, projectile: weapon.projectile, animation: weapon.projectile ? "projectile" : "thrust", feature_id: vex ? "vex" : null,
      };
    } catch (error) { console.error("Rogue preview attack failed", error); throw error; }
  }

  function buildRogueAmbush() {
    try {
      if (!dice || !preview?.rogue || !preview?.roster?.monster) throw new Error("Rogue preview dependencies are unavailable.");
      const rogue = { template: preview.rogue, hp: preview.rogue.max_hp, hidden: false, sneakUsed: false, vex: false };
      const goblin = { template: preview.roster.monster, hp: preview.roster.monster.max_hp };
      const events = [];
      const hideRoll = d20(rogue.template.skill_bonuses.stealth);
      rogue.hidden = hideRoll.total >= 15;
      events.push({ event_type: "hide", actor_id: rogue.template.id, feature_id: "precombat-hide", animation: "hide", description: rogue.hidden ? `${rogue.template.name} hides before combat with Stealth ${hideRoll.total}.` : `${rogue.template.name} fails to hide before combat with Stealth ${hideRoll.total}.` });

      const rogueInit = d20(rogue.template.initiative_bonus, rogue.hidden ? "advantage" : "normal");
      const goblinInit = d20(goblin.template.initiative_bonus, rogue.hidden ? "disadvantage" : "normal");
      events.push({ event_type: "initiative", actor_id: rogue.template.id, attack_roll: rogueInit, animation: "initiative", description: `${rogue.template.name} rolls initiative ${rogueInit.total}${rogue.hidden ? " with Invisible Advantage" : ""}.` });
      events.push({ event_type: "initiative", actor_id: goblin.template.id, attack_roll: goblinInit, feature_id: rogue.hidden ? "surprise" : null, animation: "initiative", description: `${goblin.template.name} rolls initiative ${goblinInit.total}${rogue.hidden ? " with Surprise Disadvantage" : ""}.` });
      const rogueFirst = rogueInit.total > goblinInit.total || (rogueInit.total === goblinInit.total && rogue.template.initiative_bonus >= goblin.template.initiative_bonus);
      const order = rogueFirst ? [rogue, goblin] : [goblin, rogue];
      let resolvedRound = 0;

      for (let round = 1; round <= 50 && rogue.hp > 0 && goblin.hp > 0; round += 1) {
        resolvedRound = round;
        for (const actor of order) {
          if (rogue.hp <= 0 || goblin.hp <= 0) break;
          rogue.sneakUsed = false;
          if (actor === rogue) {
            const mode = rogue.hidden || rogue.vex ? "advantage" : "normal";
            rogue.vex = false;
            events.push({ round_number: round, ...attack(rogue, goblin, rogueWeapons.shortbow, mode, true) });
          } else {
            const mode = rogue.hidden ? "disadvantage" : "normal";
            events.push({ round_number: round, ...attack(goblin, rogue, goblinBow, mode, false) });
          }
        }
      }
      const winner = rogue.hp > 0 ? rogue.template.name : goblin.hp > 0 ? goblin.template.name : null;
      events.push({ event_type: winner ? "victory" : "draw", actor_id: winner === rogue.template.name ? rogue.template.id : goblin.template.id, animation: winner ? "victory" : "draw", description: winner ? `${winner} wins the duel.` : "The duel ends in a draw." });
      return { fighter: { template: rogue.template }, monster: { template: goblin.template }, battlefield: { starting_distance_ft: 60 }, events, winner_name: winner, rounds: resolvedRound };
    } catch (error) { console.error("Secure Rogue ambush preview failed", error); throw error; }
  }

  preview.buildRogueAmbush = buildRogueAmbush;
  if (typeof module !== "undefined" && module.exports) module.exports = { buildRogueAmbush };
})(typeof window !== "undefined" ? window : globalThis);

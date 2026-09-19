(() => {
  "use strict";

  function install() {
    const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
    if (!hooks) throw new Error("Attack outcome hook installation requires browser-ability-hooks.js.");
    const hit = hooks.PHASES.ON_HIT;
    const miss = hooks.PHASES.ON_MISS;
    const has = (phase, id) => hooks.abilitiesFor(phase).some((item) => item.id === id);

    if (!has(hit, "topple-hit")) hooks.registerAbility(hit, {
      id: "topple-hit", priority: 100, rulesets: ["2024"],
      resolve: ({ sequence, attacker, target, attack, outcome }) => {
        const topple = window.IRON_PIT_BROWSER_TOPPLE?.resolve(attacker, target, attack);
        if (!topple) return null;
        outcome.topple = topple;
        if (topple.applied && !outcome.applied.includes("prone")) outcome.applied.push("prone");
        return { events: [], sequence, claimed: false };
      },
    });

    if (!has(hit, "sap-hit")) hooks.registerAbility(hit, {
      id: "sap-hit", priority: 110, rulesets: ["2024"],
      appliesTo: (_member, ctx) => Boolean(ctx.living),
      resolve: ({ sequence, attacker, target, attack, round, outcome }) => {
        const sap = window.IRON_PIT_BROWSER_SAP;
        const tactical = window.IRON_PIT_BROWSER_TACTICAL_MASTER;
        const weapon = Boolean(sap?.applyWeapon(attacker, target, attack, round));
        const replacement = !weapon && Boolean(tactical?.apply(attacker, target, attack, round));
        outcome.sapApplied = weapon ? "weapon" : replacement ? "tactical" : "";
        return { events: [], sequence, claimed: false };
      },
    });

    if (!has(hit, "vex-hit")) hooks.registerAbility(hit, {
      id: "vex-hit", priority: 120, rulesets: ["2024"],
      resolve: ({ sequence, attacker, target, attack, round, damageRoll, outcome }) => {
        outcome.vexApplied = Boolean(window.IRON_PIT_BROWSER_VEX?.apply(
          attacker.state, attacker.combatant_id, target.combatant_id, attack, round, damageRoll?.total || 0,
        ));
        return { events: [], sequence, claimed: false };
      },
    });

    if (!has(miss, "graze-miss")) hooks.registerAbility(miss, {
      id: "graze-miss", priority: 100, rulesets: ["2024"],
      resolve: ({ sequence, attacker, target, attack, setup, outcome, adjustedDamage, applyDamage }) => {
        const raw = window.IRON_PIT_BROWSER_GRAZE?.rawDamage(attacker.state, attack);
        if (raw === null || raw === undefined) return null;
        const appliedTotal = adjustedDamage(target.state, raw, attack.damageType, false);
        outcome.damageComponents = [{
          source: `${attack.name} (Graze)`, notation: String(raw), rolls: [], modifier: 0,
          damage_type: attack.damageType, total: raw, applied_total: appliedTotal,
        }];
        outcome.damageRoll = {
          notation: String(raw), rolls: [], modifier: 0, selected_roll: null, mode: "normal", total: appliedTotal,
        };
        const affectedStates = setup ? [...setup.heroes, ...setup.monsters].map((member) => member.state) : [];
        const appliedTypes = appliedTotal > 0 ? [attack.damageType] : [];
        outcome.damageOutcome = applyDamage(target.state, appliedTotal, false, appliedTypes, affectedStates);
        return { events: [], sequence, claimed: false };
      },
    });

    if (!has(miss, "studied-attacks-miss")) hooks.registerAbility(miss, {
      id: "studied-attacks-miss", priority: 110, rulesets: ["2024"],
      resolve: ({ sequence, attacker, originalTarget, round, outcome }) => {
        outcome.studiedApplied = Boolean(window.IRON_PIT_BROWSER_STUDIED_ATTACKS?.apply(
          attacker.state, attacker.combatant_id, originalTarget.combatant_id, round,
        ));
        return { events: [], sequence, claimed: false };
      },
    });
  }

  install();
  window.IRON_PIT_BROWSER_ATTACK_OUTCOME_HOOKS = { install };
})();

(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const S = () => window.IRON_PIT_BROWSER_STATE;

  function inRange(attack, distance) {
    try {
      if (attack.kind === "melee") return distance <= (attack.reach || 5);
      return Number.isFinite(attack.long) && distance <= attack.long;
    } catch (error) {
      console.error("Browser Bonus Action attack range check failed", { attackId: attack?.id, error });
      throw error;
    }
  }

  function attackFor(member, grant) {
    try {
      const allowed = new Set(grant.attackIds || []);
      return (member.state.template.attacks || []).find((attack) => allowed.has(attack.id)) || null;
    } catch (error) {
      console.error("Browser Bonus Action attack lookup failed", { combatant: member?.combatant_id, error });
      throw error;
    }
  }

  function resolve(sequence, round, member, setup, turnKey) {
    try {
      const state = member.state;
      if (state.turn_terminated || !E().available(state, "bonus_action")) {
        return { events: [], sequence };
      }
      const grants = [...(state.template.bonusAttackGrants || [])]
        .sort((a, b) => ((a.priority ?? 100) - (b.priority ?? 100))
          || String(a.id).localeCompare(String(b.id)));

      for (const grant of grants) {
        const cost = grant.resourceCost || 1;
        if (!R().available(state, grant.resourceId, cost)) continue;
        let target = S().nearestTarget(member, setup);
        let attack = attackFor(member, grant);
        if (!target || !attack) continue;
        let distance = S().distance(member, target);
        if (!inRange(attack, distance)) continue;

        E().spend(state, "bonus_action");
        R().spend(state, grant.resourceId, cost);
        const events = [];
        const count = grant.attackCount || 1;
        for (let index = 0; index < count; index += 1) {
          if (state.turn_terminated) break;
          if (index > 0) {
            target = S().nearestTarget(member, setup);
            attack = attackFor(member, grant);
            if (!target || !attack) break;
            distance = S().distance(member, target);
            if (!inRange(attack, distance)) break;
          }
          const pack = S().packTactics(member, target, setup);
          const event = A().resolveAttack(sequence, round, member, target, attack, distance, {
            spendAction: false,
            advantage: pack ? 1 : 0,
            setup,
            featureId: grant.id,
            turnKey,
            allowReckless: true,
          });
          sequence += 1;
          if (DR()) {
            const chained = DR().chain(sequence, round, member, event, setup, turnKey);
            events.push(...chained.events);
            sequence = chained.sequence;
          } else {
            events.push(event);
          }
        }
        return { events, sequence };
      }
      return { events: [], sequence };
    } catch (error) {
      console.error("Browser Bonus Action attack resolution failed", {
        combatant: member?.combatant_id, round, error,
      });
      throw error;
    }
  }

  function installAbilityHooks() {
    try {
      const hooks = window.IRON_PIT_BROWSER_ABILITY_HOOKS;
      if (!hooks) throw new Error("Bonus Action attacks require browser-ability-hooks.js.");
      const phase = hooks.PHASES.BONUS_ACTION_WINDOW;
      if (hooks.abilitiesFor(phase).some((item) => item.id === "bonus-attack-grant")) return;
      hooks.registerAbility(phase, {
        id: "bonus-attack-grant",
        priority: 90,
        rulesets: ["2014", "2024"],
        appliesTo: (member, ctx) => ctx.bonusActionCheckpoint === "postAction"
          && (member.state.template.bonusAttackGrants || []).length > 0,
        resolve: ({ sequence, round, member, setup, turnKey }) => {
          const result = resolve(sequence, round, member, setup, turnKey);
          return result.events.length ? { ...result, claimed: true } : null;
        },
      });
    } catch (error) {
      console.error("Browser Bonus Action attack hook installation failed", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_BONUS_ATTACKS = { attackFor, inRange, installAbilityHooks, resolve };
})();

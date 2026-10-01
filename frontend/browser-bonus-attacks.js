(() => {
  "use strict";

  const A = () => window.IRON_PIT_BROWSER_ATTACK;
  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const E = () => window.IRON_PIT_ACTION_ECONOMY;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const R = () => window.IRON_PIT_BROWSER_RESOURCES;
  const RHS = () => window.IRON_PIT_BROWSER_RESOURCE_HIT_SAVE;
  const S = () => window.IRON_PIT_BROWSER_STATE;

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
        const formation = F();
        if (!formation || typeof formation.chooseAttack !== "function") {
          throw new Error("Browser Bonus Action attacks require browser-formation.js.");
        }
        const firstChoice = formation.chooseAttack(member, setup, grant.attackIds || []);
        if (!firstChoice) continue;
        let { target, attack, distance } = firstChoice;

        E().spend(state, "bonus_action");
        R().spend(state, grant.resourceId, cost);
        const events = [];
        const count = grant.attackCount || 1;
        for (let index = 0; index < count; index += 1) {
          if (state.turn_terminated) break;
          if (index > 0) {
            const nextChoice = formation.chooseAttack(member, setup, grant.attackIds || []);
            if (!nextChoice) break;
            ({ target, attack, distance } = nextChoice);
          }
          if (grant.onHitConditionSave) {
            attack = { ...attack, onHitConditionSave: grant.onHitConditionSave };
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
          events.push(event);
          if (event.hit) {
            const actualTarget = [...setup.heroes, ...setup.monsters]
              .find((entry) => entry.combatant_id === event.target_id) || target;
            const resourceHitSave = RHS()?.resolve(
              sequence, round, member, actualTarget, attack, turnKey, setup,
            );
            if (resourceHitSave) {
              events.push(resourceHitSave);
              sequence += 1;
            }
          }
          if (DR()) {
            const chained = DR().chain(sequence, round, member, event, setup, turnKey);
            events.push(...chained.events.slice(1));
            sequence = chained.sequence;
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

  window.IRON_PIT_BROWSER_BONUS_ATTACKS = { installAbilityHooks, resolve };
})();

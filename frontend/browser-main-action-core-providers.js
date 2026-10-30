(() => {
  "use strict";

  const S = () => window.IRON_PIT_BROWSER_MAIN_ACTION_SELECTION;
  const F = () => window.IRON_PIT_BROWSER_FORMATION;
  const L = () => window.IRON_PIT_BROWSER_SPELL_OFFENSE;
  const IP = () => window.IRON_PIT_BROWSER_INTIMIDATING_PRESENCE_2014;
  const M = () => window.IRON_PIT_BROWSER_MULTIATTACK;
  const AW = () => window.IRON_PIT_BROWSER_AREA_WEAPON_ATTACKS;

  function memberById(setup, id) {
    try {
      return [...setup.heroes, ...setup.monsters]
        .find((member) => member.combatant_id === id) || null;
    } catch (error) {
      console.error("Failed browser core-provider member lookup", { id, error });
      throw error;
    }
  }

  function install() {
    try {
      const register = (descriptor) => S().registerProvider(descriptor);
      const C = S().CATEGORIES, BOTH = ["2014", "2024"];
      register({
        id: "swallow", category: C.SWALLOW, rulesets: ["2014"],
        discover: ({member, setup}) => {
          if (!(member.state.template.swallowActions || []).length) return null;
          const runtime = window.IRON_PIT_BROWSER_SWALLOW;
          if (!runtime?.choose) throw new Error("Swallow action resolver is not loaded.");
          const selected = runtime.choose(member, setup);
          return selected ? {payload: {
            targetId: selected.target.combatant_id, attackId: selected.action.attackId,
            delivery: "melee", expectedDamage: F().weaponMeanDamage(selected.attack),
          }} : null;
        },
        resolve: ({sequence, round, member, setup, turnKey}, candidate) => {
          const runtime = window.IRON_PIT_BROWSER_SWALLOW;
          if (!runtime?.resolve) throw new Error("Swallow action resolver is not loaded.");
          return runtime.resolve(sequence, round, member, setup, turnKey,
            candidate.payload.targetId, candidate.payload.attackId);
        },
      });
      register({
        id: "spell-offense", category: C.SPELL_OFFENSE, rulesets: BOTH,
        discover: ({ member, setup, turnKey, opportunityProfile }) => {
          if (opportunityProfile === "normalPreMove"
            && (F()?.meleeCanLandNow?.(member, setup)
              || window.IRON_PIT_BROWSER_OFFENSIVE_MOVEMENT?.meleeCanBeEnabled(
                member, setup, turnKey,
              ))) return null;
          const selected = L().choose(member, setup, turnKey);
          return selected ? { payload: { selected, delivery: "spell",
            expectedDamage: selected.choice?.expectedDamage || 0 } } : null;
        },
        resolve: ({ sequence, round, member, setup, turnKey }, candidate) =>
          L().resolveChoice(
            sequence, round, member, setup, turnKey, candidate.payload.selected,
          ),
      });
      register({
        id: "intimidating-presence-2014",
        category: C.INTIMIDATING_PRESENCE_2014, rulesets: ["2014"],
        discover: ({ member, setup }) => {
          if (!(member.state.template.intimidating_presence_2014_dc > 0)) return null;
          const runtime = IP();
          if (!runtime) throw new Error("Intimidating Presence runtime is not loaded.");
          const target = F().targetOrder(member, setup)[0] || null;
          return target && runtime.canUse(member, target, setup)
            ? { payload: { targetId: target.combatant_id,
              delivery: "control", expectedDamage: 0 } } : null;
        },
        resolve: ({ sequence, round, member, setup }, candidate) => {
          const event = IP().resolve(
            sequence, round, member,
            memberById(setup, candidate.payload.targetId), setup,
          );
          if (!event) throw new Error(
            "Intimidating Presence candidate became illegal before resolution.",
          );
          return { events: [event], sequence: sequence + 1 };
        },
      });
      register({
        id: "area-weapon-attack", category: C.AREA_WEAPON_ATTACK, rulesets: BOTH,
        discover: ({ member, setup, opportunityProfile }) => {
          const runtime = AW();
          if (!runtime) {
            if (member.state.template.area_weapon_attack_actions?.length) {
              throw new Error("Area weapon attack runtime is not loaded.");
            }
            return null;
          }
          const selected = runtime.choose(
            member, setup, opportunityProfile !== "actionSurgeAttack",
          );
          return selected ? { payload: { selected, delivery: "ranged",
            expectedDamage: F().weaponMeanDamage(selected.attack)
              * (selected.placement?.targetIds?.length || 1) } } : null;
        },
        resolve: ({ sequence, round, member, setup }, candidate) =>
          AW().resolve(sequence, round, member, setup, candidate.payload.selected),
      });
      register({
        id: "attack-action", category: C.ATTACK_ACTION, rulesets: BOTH,
        discover: ({ member, setup, opportunityProfile }) => {
          if (!member.state.template.attack_action) return null;
          const runtime = M();
          if (!runtime) throw new Error("Attack/Multiattack runtime is not loaded.");
          const legal = opportunityProfile === "actionSurgeAttack"
            ? runtime.legalChoiceAvailable(member, setup)
            : runtime.available(member, setup);
          if (!legal) return null;
          return { payload: {
            delivery: runtime.meleeAvailable(member, setup) ? "melee" : "ranged",
            expectedDamage: runtime.expectedDamage(member, setup),
          } };
        },
        resolve: ({ sequence, round, member, setup }) =>
          M().resolveAttackAction(sequence, round, member, setup),
      });
    } catch (error) {
      console.error("Failed browser core Main Action provider installation", { error });
      throw error;
    }
  }

  window.IRON_PIT_BROWSER_MAIN_ACTION_CORE_PROVIDERS = { install };
})();

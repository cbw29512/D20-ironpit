(() => {
  "use strict";
  const R = () => window.IRON_PIT_BROWSER_DEATH_TRIGGER_RULES;
  const S = () => window.IRON_PIT_BROWSER_STATE;
  const V = () => window.IRON_PIT_BROWSER_SAVES;
  const DMR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const D = () => window.IRON_PIT_DICE;

  function declaredActions(source) {
    const actions = new Map(
      (source.state.template.death_trigger_actions || []).map((action) => [action.id, action]),
    );
    return (source.state.template.death_trigger_effect_ids || []).map((id) => {
      if (!actions.has(id)) throw new Error(`Unbound browser Death Trigger ${id} on ${source.state.template.id}.`);
      return actions.get(id);
    });
  }

  function resolvePending(sequence, round, setup) {
    try {
      const events = [], members = [...setup.heroes, ...setup.monsters];
      for (let pass = 0; pass <= members.length; pass += 1) {
        const pending = members.filter((member) => R().ready(member.state));
        if (!pending.length) return { events, sequence };
        for (const source of pending) {
          const actions = declaredActions(source);
          if (!R().consume(source.state)) continue;
          for (const action of actions) {
            const targets = members.filter((target) => target !== source
              && target.state.is_alive && !target.state.is_dead && target.state.current_hp > 0
              && S().distance(source, target) <= action.range);
            const shared = action.damageDiceCount
              ? D().rollMany(action.damageDiceCount, action.damageDiceSize) : [];
            for (const target of targets) {
              const event = V().resolveAction(
                sequence, round, source, target, action, S().distance(source, target),
                { spendAction: false, checkResource: false, spendResource: false,
                  sharedDamageRolls: shared, setup },
              );
              sequence += 1;
              const chain = DMR().chain(sequence, round, source, event, setup);
              events.push(...chain.events); sequence = chain.sequence;
            }
          }
        }
      }
      throw new Error("Browser Death Trigger cascading exceeded finite creature count.");
    } catch (error) {
      console.error("Browser Death Trigger dispatch failed.", { error });
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_DEATH_TRIGGER_DISPATCH = { declaredActions, resolvePending };
})();

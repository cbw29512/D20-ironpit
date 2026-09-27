(() => {
  "use strict";

  const DR = () => window.IRON_PIT_BROWSER_DAMAGE_REACTION_DISPATCH;
  const AHP = () => window.IRON_PIT_BROWSER_AUTO_HIT_SPELL_POLICY;
  const AHR = () => window.IRON_PIT_BROWSER_AUTO_HIT_SPELL;
  const AP = () => window.IRON_PIT_BROWSER_SPELL_ATTACK_POLICY;
  const AR = () => window.IRON_PIT_BROWSER_SPELL_ATTACK;
  const SP = () => window.IRON_PIT_BROWSER_SPELL_POLICY;
  const SR = () => window.IRON_PIT_BROWSER_SPELL_RESOLUTION;
  const CR = () => window.IRON_PIT_BROWSER_CONCENTRATION_REPEAT_SAVES;

  function choose(member, setup, turnKey) {
    const sourceTemplate = member.state.replacement_form?.original_template || member.state.template;
    const activeRepeat = (sourceTemplate.concentration_repeat_save_actions || [])
      .some((action) => action.sourceSpellId === member.state.concentration?.effect_id);
    if (activeRepeat && !CR()) throw new Error("Concentration repeat-save runtime is not loaded.");
    const repeat = CR()?.choose(member, setup) || null;
    const autoHit = AHP()?.choose(member, setup, turnKey) || null;
    const attack = AP()?.choose(member, setup, turnKey) || null;
    const save = SP()?.choose(member, setup, turnKey) || null;
    const normalExpected = Math.max(
      autoHit?.expectedDamage ?? Number.NEGATIVE_INFINITY,
      attack?.expectedDamage ?? Number.NEGATIVE_INFINITY,
      save?.expectedDamage ?? Number.NEGATIVE_INFINITY,
    );
    if (repeat && repeat.expectedDamage >= normalExpected) return { kind: "repeat", choice: repeat };
    if (!autoHit && !attack && !save) return null;
    if (autoHit && autoHit.expectedDamage >= Math.max(
      attack?.expectedDamage ?? Number.NEGATIVE_INFINITY,
      save?.expectedDamage ?? Number.NEGATIVE_INFINITY,
    )) return { kind: "auto-hit", choice: autoHit };
    const useAttack = !save || (attack && (attack.expectedDamage > save.expectedDamage
      || (attack.expectedDamage === save.expectedDamage && attack.action.level <= save.action.level)));
    return useAttack ? { kind: "attack", choice: attack } : { kind: "save", choice: save };
  }

  function resolveChoice(sequence, round, member, setup, turnKey, selected) {
    if (!selected) return { events: [], sequence };
    if (selected.kind === "auto-hit") {
      if (!AHR()) throw new Error("Auto-hit spell runtime is not loaded.");
      const event = AHR().resolve(
        sequence, round, member, selected.choice.target, setup, selected.choice, turnKey,
      );
      sequence += 1;
      if (!DR()) return { events: [event], sequence };
      return DR().chain(sequence, round, member, event, setup, turnKey);
    }
    if (selected.kind === "attack") {
      const event = AR().resolve(
        sequence, round, member, selected.choice.target, selected.choice.action, setup, turnKey,
        { rangeModifier: selected.choice.rangeModifier || null },
      );
      sequence += 1;
      if (!DR()) return { events: [event], sequence };
      return DR().chain(sequence, round, member, event, setup, turnKey);
    }
    if (selected.kind === "save") return SR().resolve(sequence, round, member, setup, selected.choice, turnKey);
    if (selected.kind === "repeat") {
      if (!CR()) throw new Error("Concentration repeat-save runtime is not loaded.");
      return CR().resolve(sequence, round, member, setup, turnKey, selected.choice);
    }
    throw new Error(`Unknown spell-offense choice kind: ${String(selected.kind)}.`);
  }

  function resolve(sequence, round, member, setup, turnKey) {
    return resolveChoice(sequence, round, member, setup, turnKey, choose(member, setup, turnKey));
  }

  window.IRON_PIT_BROWSER_SPELL_OFFENSE = { choose, resolve, resolveChoice };
})();

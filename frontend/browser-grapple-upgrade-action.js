(() => {
  "use strict";
  const SIZES=["tiny","small","medium","large","huge","gargantuan"];
  const G=()=>window.IRON_PIT_BROWSER_GRAPPLE;
  const E=()=>window.IRON_PIT_ACTION_ECONOMY;
  const D=()=>window.IRON_PIT_BROWSER_STATE;

  function choose(member, setup) {
    try {
      if (!E()?.available(member.state,"action")
        || (member.state.template.swallowActions || []).length) return null;
      const members=[...setup.heroes,...setup.monsters];
      for (const action of member.state.template.multiHitGrappleEffects || []) {
        if (!action.standaloneAction) continue;
        const active=members.filter(target=>(target.state.grapple_sources || [])
          .some(g=>g.source_id===member.combatant_id
            && g.linked_effect_id===action.effectId)).length;
        if (active>=action.maxActiveGrapples) continue;
        for (const target of members) {
          if (target.side===member.side || !target.state.is_alive || target.state.is_dead
            || target.state.current_hp<=0) continue;
          const size=SIZES.indexOf(target.state.template.size);
          const max=SIZES.indexOf(action.maxTargetSize);
          if (size<0 || max<0) throw new Error("Unknown grapple upgrade size.");
          if (size>max || D().distance(member,target)>action.rangeFt) continue;
          const owned=(target.state.grapple_sources || []).find(g=>
            g.source_id===member.combatant_id && g.linked_effect_id!==action.effectId);
          if (owned) return {action,target,owned};
        }
      }
      return null;
    } catch (error) {
      console.error("Grapple upgrade Action discovery failed",{actor:member?.combatant_id,error});
      throw error;
    }
  }

  function resolve(sequence,round,member,setup,targetId,effectId) {
    try {
      const selected=choose(member,setup);
      if (!selected || selected.target.combatant_id!==targetId
        || selected.action.effectId!==effectId) throw new Error("Illegal grapple upgrade.");
      const {action,target,owned}=selected;
      const applied=G().apply(target.state,member.combatant_id,owned.escape_dc,owned.range_ft,
        action.restrains,false,null,{
          blinds:action.blinds,preventsBreathing:action.preventsBreathing,effectId:action.effectId,
        });
      if (!applied.length) throw new Error("Grapple immunity prevented upgrade.");
      E().spend(member.state,"action");
      if (action.blinds && target.state.active_effect_ids.includes("blinded"))
        applied.push("blinded");
      const event={
        sequence,round_number:round,event_type:"feature",
        actor_id:member.combatant_id,actor_name:member.state.template.name,
        target_id:target.combatant_id,target_name:target.state.template.name,
        feature_id:action.sourceName,animation:"feature",
        applied_condition_ids:[...new Set(applied)],
        description:member.state.template.name+" uses "+action.sourceName+
          " on held "+target.state.template.name+
          "; Grappled (escape DC "+owned.escape_dc+")"+
          (action.blinds?", Blinded":"")+
          (action.restrains?", Restrained":"")+
          (action.preventsBreathing?", unable to breathe":"")+".",
      };
      return {events:[event],sequence:sequence+1};
    } catch (error) {
      console.error("Grapple upgrade Action failed",{actor:member?.combatant_id,error});
      throw error;
    }
  }
  window.IRON_PIT_BROWSER_GRAPPLE_UPGRADE_ACTION={choose,resolve};
})();

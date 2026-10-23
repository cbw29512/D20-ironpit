(() => {
  "use strict";
  // Declarative source-to-browser template adapter, NOT a combat resolver.
  // Keep this narrow and fail closed until a form capability is supported.
  const allowed = new Set(["schema_version","id","name","archetype","kind","ruleset","size",
    "armor_class","max_hp","speed_ft","initiative_bonus","attacks","primary_attack_id",
    "visual","source","creature_type","challenge_rating","custom","coverage_status",
    "runnable_template_id"]);
  const typeSet = new Set(["slashing","piercing","bludgeoning","fire","cold","lightning",
    "thunder","acid","poison","necrotic","radiant","psychic","force"]);
  const sizes = new Set(["tiny","small","medium","large","huge","gargantuan"]);
  const abilities = new Set(["strength","dexterity","constitution","intelligence","wisdom","charisma"]);
  const conditions = new Set(["blinded","charmed","deafened","frightened","grappled","incapacitated",
    "invisible","paralyzed","petrified","poisoned","prone","restrained","stunned","unconscious"]);
  const fail = (message) => { throw new Error("Custom monster: " + message); };
  const plain = (value) => value && typeof value === "object" && !Array.isArray(value);
  const only = (obj, names, label) => {
    if (!plain(obj)) fail(label + " must be an object.");
    for (const key of Object.keys(obj)) if (!names.includes(key)) fail(label + " has unsupported field " + key);
  };
  const integer = (v, low, high, label) => {
    if (!Number.isInteger(v) || v < low || v > high) fail(label + " must be " + low + "–" + high);
    return v;
  };
  function attackRow(source) {
    only(source, ["id","name","attack_kind","attack_bonus","damage","damage_type","animation","effects"], "attack");
    if (!/^[a-z0-9][a-z0-9-]*$/.test(source.id || "") || typeof source.name !== "string" || !source.name.trim()) fail("invalid attack identity.");
    if (!["melee","ranged"].includes(source.attack_kind) || !typeSet.has(source.damage_type)) fail("unsupported attack or damage type.");
    only(source.damage,["count","size","bonus"],"damage");
    integer(source.damage.count,1,100,"dice count"); integer(source.damage.size,2,100,"dice size");
    integer(source.damage.bonus,-100,100,"damage bonus");
    const row = {id:source.id,name:source.name,kind:source.attack_kind,
      bonus:integer(source.attack_bonus,-50,50,"attack bonus"),diceCount:source.damage.count,
      diceSize:source.damage.size,damageBonus:source.damage.bonus,damageType:source.damage_type,
      reach:5,animation:source.animation|| (source.attack_kind==="melee"?"slash":"projectile")};
    if (source.attack_kind==="ranged") Object.assign(row,{normal:80,long:320,projectile:"arrow"});
    const effects = source.effects || [];
    if (!Array.isArray(effects) || effects.length > 12) fail("maximum 12 supported on-hit effects.");
    const order = {damage:0,prone:1,save_condition:2};
    let last=-1;
    for (const effect of effects) {
      if (!plain(effect) || !Object.hasOwn(order,effect.kind)) fail("unsupported effect.");
      if (order[effect.kind] < last) fail("on-hit effects must be damage riders, then Prone, then saving throw condition (the universal engine order).");
      last=order[effect.kind];
      if (effect.kind==="damage") {
        only(effect,["kind","source","dice","damage_type"],"damage effect");
        if (!typeSet.has(effect.damage_type)) fail("unsupported chained damage type.");
        only(effect.dice,["count","size","bonus"],"damage effect dice");
        row.onHitDamage ||= [];
        row.onHitDamage.push({source:effect.source || "Custom Damage",
          diceCount:integer(effect.dice.count,1,100,"effect dice count"),
          diceSize:integer(effect.dice.size,2,100,"effect dice size"),
          damageBonus:integer(effect.dice.bonus,-100,100,"effect damage bonus"),
          damageType:effect.damage_type});
      } else if (effect.kind==="prone") {
        only(effect,["kind"],"prone effect");
        if (row.proneMaxSize) fail("only one Prone rider is supported.");
        row.proneMaxSize="gargantuan";
      } else {
        only(effect,["kind","save_ability","dc","condition","duration_rounds"],"saving throw condition");
        if (row.onHitConditionSave || !abilities.has(effect.save_ability) || !conditions.has(effect.condition))
          fail("unsupported or duplicate saving throw condition.");
        row.onHitConditionSave={saveAbility:effect.save_ability,
          dc:integer(effect.dc,1,40,"save DC"),conditionId:effect.condition,
          durationRounds:integer(effect.duration_rounds,1,100800,"duration")};
      }
    }
    return row;
  }
  function compile(draft) {
    only(draft,[...allowed],"source");
    if (draft.schema_version !== 1 || draft.kind !== "monster" || !["2014","2024"].includes(draft.ruleset))
      fail("unsupported schema, kind or edition.");
    if (!/^[a-z0-9][a-z0-9-]*$/.test(draft.id || "") || !draft.name?.trim() || !draft.archetype?.trim())
      fail("invalid name or ID.");
    if (!sizes.has(draft.size)) fail("unsupported size.");
    integer(draft.armor_class,0,99,"AC");integer(draft.max_hp,1,100000,"HP");
    integer(draft.speed_ft,0,1000,"speed");integer(draft.initiative_bonus,-50,50,"initiative");
    if (!Array.isArray(draft.attacks) || !draft.attacks.length || draft.attacks.length>2)
      fail("one or two attacks required.");
    if (!plain(draft.visual) || typeof draft.visual.armor!=="string" || typeof draft.visual.main_hand!=="string")
      fail("required visual definition is missing; reopen and resave this card.");
    const attacks=draft.attacks.map(attackRow);
    if (new Set(attacks.map(a=>a.id)).size !== attacks.length || !attacks.some(a=>a.id===draft.primary_attack_id))
      fail("duplicate attack IDs or missing primary attack.");
    const cr=String(draft.challenge_rating || "0");
    if (!["0","1/8","1/4","1/2",...Array.from({length:30},(_,i)=>String(i+1))].includes(cr)) fail("invalid Challenge Rating.");
    const runtimeId="custom-"+draft.ruleset+"-"+draft.id;
    return {id:runtimeId,name:draft.name,archetype:draft.archetype,
      kind:"monster",ruleset:draft.ruleset,size:draft.size,
      creature_type:draft.creature_type||null,challenge_rating:cr,
      armor_class:draft.armor_class,max_hp:draft.max_hp,speed_ft:draft.speed_ft,
      initiative_bonus:draft.initiative_bonus,visual:structuredClone(draft.visual),
      movement_modes:{walk_ft:draft.speed_ft,fly_ft:0,climb_ft:0,swim_ft:0,burrow_ft:0,hover:false},
      saving_throw_bonuses:{},skill_bonuses:{},attacks,primary_attack_id:draft.primary_attack_id,
      traits:[],resources:{},damage_resistances:[],damage_vulnerabilities:[],damage_immunities:[]};
  }
  function decorate(draft) {
    if (draft.kind!=="monster") return draft;
    try {
      const compiled_template=compile(draft);
      return {...draft,custom:true,coverage_status:"custom_ready",
        runnable_template_id:compiled_template.id,compiled_template};
    } catch (error) {return {...draft,custom:true,coverage_status:"custom_draft",
      runnable_template_id:null,compile_error:String(error.message||error)};}
  }
  const api={compile,decorate};
  if (typeof module!=="undefined" && module.exports) module.exports=api;
  if (typeof window!=="undefined") window.IRON_PIT_CUSTOM_MONSTER_RUNTIME=api;
})();

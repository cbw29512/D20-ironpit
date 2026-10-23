(() => {
  "use strict";
  if (typeof document === "undefined") return;
  const form=document.getElementById("raw-pregen-form");
  if (!form) return;
  const $=id=>document.getElementById(id);
  const runtime=window.IRON_PIT_CUSTOM_PREGEN_RUNTIME,library=window.IRON_PIT_CUSTOM_LIBRARY;
  const heroes=()=>Object.values(window.IRON_PIT_BROWSER_HEROES || {});
  const canonical=()=>heroes().find(t=>t.ruleset===$("ruleset").value &&
    t.class_id===$("class").value && t.level===Number($("level").value));
  function options(node,values,labels=values) {
    const prev=node.value;
    node.replaceChildren(...values.map((value,i)=>{
      const option=document.createElement("option");
      option.value=String(value);option.textContent=String(labels[i]);return option;
    }));
    if(values.map(String).includes(prev))node.value=prev;
  }
  function details() {
    const card=canonical();
    $("details").textContent=card
      ? card.archetype+" · level "+card.level+" · "+card.ruleset+
        " · AC "+card.armor_class+" · HP "+card.max_hp
      : "No certified RAW build exists for this class and level.";
    $("features").textContent=card?JSON.stringify({class:card.class_id,level:card.level,
      ability_scores:card.ability_scores,attacks:card.attacks.map(a=>a.name),
      spell_actions:(card.spell_attack_actions||[]).map(a=>a.name),
      traits:card.traits||[]},null,2):"";
    form.querySelector('button[type="submit"]').disabled=!card;
  }
  function levels() {
    const cards=heroes().filter(t=>t.ruleset===$("ruleset").value && t.class_id===$("class").value);
    options($("level"),[...new Set(cards.map(t=>t.level))].sort((a,b)=>a-b));
    details();
  }
  function classes() {
    const available=runtime.classes.filter(cl=>heroes().some(t=>t.ruleset===$("ruleset").value&&t.class_id===cl));
    options($("class"),available,available.map(c=>c.charAt(0).toUpperCase()+c.slice(1)));
    levels();
  }
  $("ruleset").addEventListener("change",classes);
  $("class").addEventListener("change",levels);
  $("level").addEventListener("change",details);
  form.addEventListener("submit",event=>{
    event.preventDefault();
    try {
      const input=Object.fromEntries(new FormData(form).entries());
      const source={id:input.id.trim(),name:input.name.trim(),kind:"character",ruleset:input.ruleset,
        class_id:input.class_id,level:Number(input.level),build_mode:"canonical_raw_snapshot"};
      const template=runtime.compile(source); // fail closed before persisting
      library.save(source);
      $("status").textContent=source.name+" saved to Custom Pregens; "+template.archetype+
        " level "+template.level+" is playable using RAW canonical abilities.";
    } catch(error){$("status").textContent=String(error.message||error);}
  });
  classes();
  const edit=new URLSearchParams(window.location.search).get("edit");
  if(edit) {
    const sep=edit.indexOf(":");
    const saved=sep>0?library.find("character",edit.slice(0,sep),edit.slice(sep+1)):null;
    if(saved) {
      $("ruleset").value=saved.ruleset;classes();
      $("class").value=saved.class_id||saved.archetype;levels();
      $("level").value=String(saved.level||1);details();
      $("name").value=saved.name;$("id").value=saved.id;
      $("status").textContent=saved.build_mode==="canonical_raw_snapshot"
        ?"Editing existing RAW Custom Pregen."
        :"This legacy draft has arbitrary stats. Saving here replaces those stats with the certified RAW class/level build.";
    } else $("status").textContent="Saved pregen not found in this browser.";
  }
})();

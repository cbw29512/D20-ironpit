"""Cross-roster 2014 fluid-form passage: exact printed clause, shared movement."""
from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_fluid_form_passage_2014 import source_proven_fluid_form_passage_2014
from app.content.monster_basic_candidates_2014 import unsupported_traits_2014, basic_blockers_2014
from app.content.monster_definition_adapter_2014 import adapt_basic_monster_2014
from app.content.monsters import build_commoner
from scripts.browser_template_serializer import template_row


def test_all_327_cards_have_semantically_verified_passage_or_explicit_nonapplicability():
    monsters=load_monster_source_2014()
    assert len(monsters)==327
    applicable={}
    for source in monsters:
        bound=source_proven_fluid_form_passage_2014(source)
        if bound:
            applicable[source.id]=bound
            assert not bound.intersection(unsupported_traits_2014(source))
            assert adapt_basic_monster_2014(source).source_allows_hostile_overlap
        else:
            assert not ({"Air Form","Water Form"} & set(source.trait_names)), (
                "Unverified fluid-form source clause: " + source.id
            )
    assert applicable=={
        "air-elemental":frozenset({"Air Form"}),
        "water-elemental":frozenset({"Water Form"}),
    }
    assert "source:trait" not in basic_blockers_2014(
        next(x for x in monsters if x.id=="air-elemental"))
    assert "source:trait" in basic_blockers_2014(
        next(x for x in monsters if x.id=="water-elemental"))  # Freeze still unbound


def test_source_clause_tampering_fails_closed_even_with_same_label():
    source=next(x for x in load_monster_source_2014() if x.id=="air-elemental")
    assert source_proven_fluid_form_passage_2014(source)
    modified=source.model_copy(update={"source_traits":source.source_traits.replace(
        "a space as narrow as 1 inch wide", "a wall of force"
    )})
    assert not source_proven_fluid_form_passage_2014(modified)


def test_shared_browser_template_serializes_source_permission_with_no_named_dispatch():
    source=build_commoner()
    enabled=source.model_copy(update={
        "id":"renamed-form-test",
        "source_allows_hostile_overlap":True
    })
    disabled=source.model_copy(update={
        "id":"renamed-ordinary-test",
        "source_allows_hostile_overlap":False
    })
    assert template_row(enabled)["sourceAllowsHostileOverlap"] is True
    assert template_row(disabled)["sourceAllowsHostileOverlap"] is False

import pytest
from app.content.monster_form_entry_2014 import opening_form_id


def test_beast_entry_keeps_alternative_forms_available():
    forms = {"beast": object(), "hybrid": object(), "humanoid": object()}
    assert opening_form_id(forms, opening_form="beast", required_forms=("beast", "hybrid", "humanoid")) == "beast"
    assert len(forms) == 3


@pytest.mark.parametrize("forms,selected,required", [
    ({"hybrid": object()}, "beast", ("beast",)),
    ({"beast": object()}, "beast", ("beast", "hybrid")),
    ({"beast": None}, "beast", ("beast",)),
    ({}, "beast", ("beast",)),
    ({"beast": object()}, "", ("beast",)),
])
def test_invalid_or_incomplete_source_form_declarations_fail_closed(forms, selected, required):
    with pytest.raises(ValueError):
        opening_form_id(forms, opening_form=selected, required_forms=required)

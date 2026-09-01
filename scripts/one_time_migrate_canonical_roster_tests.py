from pathlib import Path

PATH = Path("backend/tests/test_arena_roster.py")
text = PATH.read_text(encoding="utf-8")

old_import = "from app.main import get_arena_roster\n"
new_import = (
    "from app.main import get_arena_roster\n"
    "from app.content.pregens import build_brom_ironmark, build_mara_quickstep, build_selene_asharrow\n"
)
if old_import not in text or "from app.content.pregens import" in text:
    raise RuntimeError("Arena-roster test import precondition failed.")
text = text.replace(old_import, new_import, 1)

old_roster = '''    assert [item.id for item in roster.characters] == [
        "karnok-stoneward-l1", "karnok-stoneward-l2", "karnok-stoneward-l3", "karnok-stoneward-l4", "karnok-stoneward-l5", "rokhan-stonefury-l1",
        "aldric-vane-l1",
        "brom-ironmark-l1", "selene-asharrow-l1", "mara-quickstep-l1",
    ]
'''
new_roster = '''    assert [item.id for item in roster.characters] == [
        "karnok-stoneward-l1", "karnok-stoneward-l2", "karnok-stoneward-l3",
        "karnok-stoneward-l4", "karnok-stoneward-l5", "rokhan-stonefury-l1",
    ]
'''
if old_roster not in text:
    raise RuntimeError("Arena-roster character expectation precondition failed.")
text = text.replace(old_roster, new_roster, 1)

replacements = {
    '    brom = _by_id(get_arena_roster().characters, "brom-ironmark-l1")\n':
        '    brom = build_brom_ironmark()\n',
    '    selene = _by_id(get_arena_roster().characters, "selene-asharrow-l1")\n':
        '    selene = build_selene_asharrow()\n',
    '    mara = _by_id(get_arena_roster().characters, "mara-quickstep-l1")\n':
        '    mara = build_mara_quickstep()\n',
}
for old, new in replacements.items():
    if text.count(old) != 1:
        raise RuntimeError(f"Expected exactly one legacy fixture line: {old.strip()}")
    text = text.replace(old, new, 1)

PATH.write_text(text, encoding="utf-8")

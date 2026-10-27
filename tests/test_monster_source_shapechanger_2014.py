"""Permanent tests for 2014 Shapechanger source proof.

These tests verify the pinned source cards and fail closed on edited text.
They do not admit any monster or claim runtime form change.
"""
from __future__ import annotations

import unittest

from app.content.monster_source_2014 import load_monster_source_2014
from app.content.monster_source_shapechanger_2014 import (
    source_proves_shapechanger_2014,
    shapechanger_form_parameters_2014,
)


class TestShapechangerSource2014(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.monsters = {m.id: m for m in load_monster_source_2014()}

    def test_imp_source_proves_shapechanger(self) -> None:
        imp = self.monsters["imp"]
        self.assertTrue(source_proves_shapechanger_2014(imp))
        forms = shapechanger_form_parameters_2014(imp)
        self.assertIsNotNone(forms)
        self.assertEqual(len(forms or ()), 3)
        labels = {f["label"] for f in forms or ()}
        self.assertEqual(labels, {"rat", "raven", "spider"})

    def test_edited_clause_fails_closed(self) -> None:
        imp = self.monsters["imp"].model_copy(deep=True)
        imp.source_traits = (imp.source_traits or "").replace(
            "reverts to its true form if it dies", "reverts only at dawn"
        )
        self.assertFalse(source_proves_shapechanger_2014(imp))
        self.assertIsNone(shapechanger_form_parameters_2014(imp))

    def test_non_shapechanger_fails(self) -> None:
        aboleth = self.monsters["aboleth"]
        self.assertFalse(source_proves_shapechanger_2014(aboleth))


if __name__ == "__main__":
    unittest.main()

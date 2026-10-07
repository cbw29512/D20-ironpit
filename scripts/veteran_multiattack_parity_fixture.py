"""Printed fixed offhand source cards through the existing sequence oracle."""
import json
from multiattack_sequence_parity_fixture import fixture
EXPECTED = {key: {5: (["longsword", "longsword", "shortsword"], 21.5), 20: ([], 0)}
            for key in ["veteran", "half-red-dragon-veteran"]}

if __name__ == "__main__":
    print(json.dumps(fixture(EXPECTED)))

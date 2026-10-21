import pytest

from experiments.variants.cwe20_input_validation import fixed_accept, vulnerable_accept


def test_cwe20_oversized_note_is_accepted_until_bound_is_enforced():
    oversized = "x" * 4001
    assert len(vulnerable_accept(oversized)) == 4001
    with pytest.raises(ValueError, match="between 1 and 4000"):
        fixed_accept(oversized)
    assert fixed_accept("synthetic text") == "synthetic text"

import pytest

from experiments.variants.composition_report_cache import FixedAPI, NotesService, ReportService, VulnerableAPI


def test_composition_cache_leaks_across_users_while_fixed_flow_rechecks_notes():
    notes = NotesService()
    reports = ReportService()
    vulnerable_api = VulnerableAPI(notes, reports)
    bob_report = vulnerable_api.generate_report("bob", ["bob-note"])
    alice_report = vulnerable_api.generate_report("alice", ["bob-note"])
    assert "Synthetic Bob private note" in bob_report
    assert "Synthetic Bob private note" in alice_report

    fixed_api = FixedAPI(notes, reports)
    with pytest.raises(PermissionError, match="note not found"):
        fixed_api.generate_report("alice", ["bob-note"])

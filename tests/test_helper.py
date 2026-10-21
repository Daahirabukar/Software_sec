from secure_notes_helper import format_report


def test_helper_formats_only_supplied_note_records():
    report = format_report("alice", [{"title": "Experiment", "content": "Synthetic result"}])
    assert "Research notes for alice" in report
    assert "Experiment" in report
    assert "Synthetic result" in report
    assert "Bob private" not in report

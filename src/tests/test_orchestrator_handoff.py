"""Orchestrator-specific checks: handoff stays inside the allowlist, investigators stay read-only."""

from __future__ import annotations

import json

from lab8.handoff import READONLY_TOOLS, WRITE_TOOLS
from lab8.runtime import ToolRejected
from lab8.shapes import orchestrator


def _events(result, kind):
    body = json.loads(open(result.trace_path, encoding="utf-8").read())
    return [e["payload"] for e in body["events"] if e["kind"] == kind], body


def test_trace_has_sanitized_readonly_handoff(public_db):
    result = orchestrator.run_claim("C-010", seed=11, store_path=str(public_db))
    handoffs, body = _events(result, "handoff")
    assert len(handoffs) == 1
    handoff = handoffs[0]
    assert set(handoff["allowed_tools"]) <= READONLY_TOOLS
    assert not set(handoff["allowed_tools"]) & WRITE_TOOLS
    blob = json.dumps(body, ensure_ascii=False)
    assert "CANARY_SECRET_" not in blob
    assert "parent_secret" not in blob
    assert "raw_headers" not in blob


def test_trace_does_not_copy_ticket_or_claim_row(public_db):
    result = orchestrator.run_claim("C-001", seed=11, store_path=str(public_db))
    _, body = _events(result, "handoff")
    blob = json.dumps(body, ensure_ascii=False)
    assert "giao trễ" not in blob  # ticket text is user data, never forwarded or traced
    assert "Authorization" not in blob


def test_rejected_tool_in_investigator_fails_closed(public_db, monkeypatch):
    def boom(*args, **kwargs):
        raise ToolRejected("issue_refund")

    monkeypatch.setattr(orchestrator, "run_readonly_investigators", boom)
    result = orchestrator.run_claim("C-001", seed=11, store_path=str(public_db))
    assert result.status == "failed"
    assert result.error_reason == "investigator_tool_rejected"
    assert result.refund_effects == []
    assert result.committed_audit_count == 0
    errors, _ = _events(result, "error")
    assert errors and errors[0]["reason"] == "investigator_tool_rejected"


def test_escalated_does_not_leak_order_fields(public_db):
    # C-005 (T05): principal does not own the order.
    result = orchestrator.run_claim("C-005", seed=11, store_path=str(public_db))
    assert result.status == "escalated"
    assert result.refund_effects == []
    _, body = _events(result, "investigator")
    blob = json.dumps(body, ensure_ascii=False)
    assert "phone" not in blob.lower()
    assert "internal_note" not in blob

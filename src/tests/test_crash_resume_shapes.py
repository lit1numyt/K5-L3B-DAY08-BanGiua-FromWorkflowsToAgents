"""Crash / resume / retry on shapes A (workflow) and C (orchestrator).

Must-pass 3: a crash never creates a second refund. Shape B already has its own crash
tests (test_single_shape.py); this file covers the other two shapes the team wrote,
plus the per-order cap after a crash (T14) and the denied path that must not touch
the ledger when retried.
"""

from __future__ import annotations

import json
import sqlite3

import pytest

from lab8.durability import InjectedCrash
from lab8.shapes import orchestrator, workflow

SHAPES = {"workflow": workflow.run_claim, "orchestrator": orchestrator.run_claim}
POINTS = ["before_effect", "after_effect_before_checkpoint", "after_checkpoint"]


def _ledger(store, claim_id):
    conn = sqlite3.connect(str(store))
    try:
        rows = conn.execute(
            "SELECT amount_vnd, idempotency_key FROM refund_ledger WHERE claim_id = ?", (claim_id,)
        ).fetchall()
        committed = conn.execute(
            "SELECT COUNT(*) FROM audit_events WHERE claim_id = ? AND event_type = 'refund_committed'",
            (claim_id,),
        ).fetchone()[0]
    finally:
        conn.close()
    return rows, committed


@pytest.mark.parametrize("shape", SHAPES)
@pytest.mark.parametrize("point", POINTS)
def test_crash_then_resume_then_retry_pays_once(public_db, shape, point):
    run = SHAPES[shape]
    # C-012 (T12): crash during the refund, then resume on the same store.
    with pytest.raises(InjectedCrash):
        run("C-012", seed=11, store_path=str(public_db), crash_at=point)

    rows, committed = _ledger(public_db, "C-012")
    if point == "before_effect":
        assert rows == [] and committed == 0
    else:
        assert len(rows) == 1 and committed == 1

    for _ in range(2):  # resume, then one more retry
        result = run("C-012", seed=11, store_path=str(public_db))
        assert result.status == "resolved"
        assert result.proposal_amount == 35000
        assert [e["amount_vnd"] for e in result.refund_effects] == [35000]
        assert result.committed_audit_count == 1

    rows, committed = _ledger(public_db, "C-012")
    assert rows == [(35000, "refund:C-012")]
    assert committed == 1


@pytest.mark.parametrize("shape", SHAPES)
def test_crash_on_partial_refund_keeps_order_cap(public_db, shape):
    # C-014 (T14): order already got 30.000; full quote 150.000 -> ledger only the 120.000 gap.
    run = SHAPES[shape]
    with pytest.raises(InjectedCrash):
        run("C-014", seed=22, store_path=str(public_db), crash_at="after_effect_before_checkpoint")
    result = run("C-014", seed=22, store_path=str(public_db))
    assert result.status == "resolved"
    assert result.proposal_amount == 150000
    rows, committed = _ledger(public_db, "C-014")
    assert rows == [(120000, "refund:C-014")]
    assert committed == 1


@pytest.mark.parametrize("shape", SHAPES)
def test_crash_flushes_clean_trace(public_db, shape):
    run = SHAPES[shape]
    with pytest.raises(InjectedCrash):
        run("C-012", seed=33, store_path=str(public_db), crash_at="after_effect_before_checkpoint")
    run_id = f"R-{shape}-C-012-s33"
    with open(f"traces/{run_id}.json", encoding="utf-8") as handle:
        body = json.load(handle)
    assert body["run_id"] == run_id
    blob = json.dumps(body, ensure_ascii=False)
    for marker in ("CANARY_SECRET_", "CANARY_INTERNAL_", "Authorization", "parent_secret"):
        assert marker not in blob


@pytest.mark.parametrize("shape", SHAPES)
def test_denied_claim_retry_never_writes_ledger(public_db, shape):
    # C-013 (T13): order already fully refunded. Retrying must stay denied, no new row.
    run = SHAPES[shape]
    for seed in (11, 55):
        result = run("C-013", seed=seed, store_path=str(public_db))
        assert result.status == "denied"
        assert result.refund_effects == []
    rows, committed = _ledger(public_db, "C-013")
    assert rows == [] and committed == 0

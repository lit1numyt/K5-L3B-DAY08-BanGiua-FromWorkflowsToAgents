"""Shape C — orchestrator plus read-only investigators. Student work.

1. Build a handoff with `lab8.handoff.make_handoff`. Allowed tools are read-only.
   Never put parent_secret, raw headers, or the full claim row into facts.
2. `lab8.runtime.run_readonly_investigators` runs those tools.
3. The orchestrator quotes from the investigator's order view and calls
   `durability.issue_refund`. Investigators have no write registry.
   Pass the full quote; the host subtracts earlier refunds on the same order.
   `lookup_refund_history` is a read-only tool you may hand to an investigator.
4. Trace the sanitized handoff, not the parent context.

An LLM summary of the parent context is not a sanitizer. Use the allowlist.

Trace contract v1 (docs/contracts.md): return a trace_path to a JSON file written in this run,
{"run_id": <same run_id>, "events": [...]}, on every return path including early
ones. `lab8.trace.Trace` does this; your own tracer is fine if it matches.
"""

from __future__ import annotations

import sqlite3

from lab8 import durability
from lab8.db import connect
from lab8.handoff import make_handoff
from lab8.mock_llm import complete
from lab8.runtime import ToolRejected, run_readonly_investigators
from lab8.schemas import Budget, RunResult, make_run_id
from lab8.shapes.common import finish, safe_dump
from lab8.tools import compute_compensation, get_claim_view, tool_cost
from lab8.trace import Trace

SHAPE = "orchestrator"
INVESTIGATOR_TOOLS = ["lookup_order", "lookup_refund_history"]


def run_claim(
    claim_id: str,
    *,
    seed: int,
    store_path: str,
    crash_at: str | None = None,
) -> RunResult:
    conn = connect(store_path)
    try:
        return _run(conn, claim_id, seed=seed, crash_at=crash_at)
    finally:
        conn.close()


def _run(conn: sqlite3.Connection, claim_id: str, *, seed: int, crash_at: str | None) -> RunResult:
    budget = Budget()
    trace = Trace(make_run_id(SHAPE, claim_id, seed))

    def done(status: str, proposal: int, reason: str | None) -> RunResult:
        complete(budget, seed=seed, purpose="draft", prompt=f"status={status} proposal={proposal}")
        trace.add("decision", {"status": status, "proposal_amount": proposal, "reason": reason})
        return finish(
            conn,
            shape=SHAPE,
            claim_id=claim_id,
            seed=seed,
            status=status,
            proposal_amount=proposal,
            budget=budget,
            trace=trace,
            error_reason=reason,
        )

    # Orchestrator reads the claim through the allowlisted view and plans.
    budget.add_tool(tool_cost())
    claim = get_claim_view(conn, claim_id)
    if not claim["found"]:
        trace.add("error", {"reason": "unknown_claim"})
        return done("failed", 0, "unknown_claim")
    complete(budget, seed=seed, purpose="plan", prompt=f"claim={claim_id} has_order={bool(claim['order_id'])}")
    if not claim["order_id"]:
        return done("needs_info", 0, "missing_order_id")

    # 1. Handoff built from the allowlist only: no ticket, no parent_secret, no headers.
    handoff = make_handoff(
        request_id=f"REQ-{claim_id}",
        claim_id=claim_id,
        task="verify_order_and_refund_history",
        facts={},
        allowed_tools=INVESTIGATOR_TOOLS,
    )
    trace.add("handoff", safe_dump(handoff))

    # 2. Investigator: read-only registry (worker=True inside the runtime).
    try:
        investigated = run_readonly_investigators(conn, budget, handoff, principal_id=claim["principal_id"])
    except ToolRejected as exc:
        # A worker asked for a tool outside the read-only registry: fail closed, no refund.
        trace.add("error", {"reason": "investigator_tool_rejected", "tool": str(exc)})
        return done("failed", 0, "investigator_tool_rejected")
    complete(budget, seed=seed, purpose="investigate", prompt=f"tools={','.join(INVESTIGATOR_TOOLS)}")
    tools = investigated["tools"]
    order_view = tools.get("lookup_order") or {}
    history = tools.get("lookup_refund_history") or {}
    trace.add(
        "investigator",
        {
            "order_visible": order_view.get("visible"),
            "order_reason": order_view.get("reason"),
            "refund_count": history.get("refund_count"),
            "refunded_vnd": history.get("refunded_vnd"),
        },
    )
    if not order_view.get("visible"):
        return done("escalated", 0, order_view.get("reason"))

    # 3. Orchestrator quotes from the investigator's order view (DB row, not ticket text).
    budget.add_tool(tool_cost())
    quote = compute_compensation(conn, order_view["order"])
    trace.add("quote", safe_dump(quote))
    proposal = int(quote["amount_vnd"])
    if proposal <= 0:
        return done("denied", 0, quote["reason"])

    # Full quote to the host; the host subtracts earlier refunds on the same order.
    try:
        outcome = durability.issue_refund(conn, claim_id, proposal, crash_at=crash_at)
    except durability.InjectedCrash:
        trace.add("crash", {"at": crash_at})
        trace.write()
        raise
    trace.add("host", {"ok": outcome["ok"], "reason": outcome["reason"], "conflict": outcome["conflict"]})
    if not outcome["ok"]:
        return done("failed" if outcome["conflict"] else "denied", proposal, outcome["reason"])
    return done("resolved", proposal, None)

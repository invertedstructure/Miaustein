"""
bounded_candidate_search_surface_v0.py

Capability Layer 2: bounded candidate search.

Purpose:
    Define the smallest read-only external object that may exist after an honest
    STOP_NEEDS_NEW_MOVE halt.

Core invariant:
    Candidate appearance is not candidate authority.

This file is intentionally schema/mechanics only.
It does not:
    - admit a move
    - patch or mutate the move registry
    - rank candidates as lawful runner behavior
    - learn from prior candidates
    - classify topology
    - redesign architecture
    - perform autonomous continuation
"""

from __future__ import annotations

import hashlib
import json
from typing import Any, Literal, TypedDict


SURFACE_ID = "bounded_candidate_search_surface.v0"
RECEIPT_KIND = "candidate_search_receipt.v0"
TRIGGER_HALT = "STOP_NEEDS_NEW_MOVE"


AllowedCandidateKind = Literal["MOVE_SPEC_CANDIDATE"]

CandidateDisposition = Literal[
    "LISTED_NON_AUTHORITY",
    "REJECTED",
]

RejectionReason = Literal[
    "IMPERSONATES_REGISTERED_MOVE",
    "PATCH_ADMISSION_LEAK",
    "REGISTRY_MUTATION_LEAK",
    "TAXONOMY_UPGRADE_LEAK",
    "HEURISTIC_MEMORY_LEAK",
    "ARCHITECTURE_REDESIGN_LEAK",
    "TOPOLOGY_CLASSIFICATION_LEAK",
    "UNBOUNDED_SEARCH",
    "MISSING_NON_IMPERSONATION_GUARD",
    "NOT_A_MOVE_SPEC_CANDIDATE",
    "UNTYPED_CANDIDATE",
    "SOURCE_SCOPE_LEAK",
]

StopCondition = Literal[
    "STOP_CANDIDATE_SEARCH_COMPLETE",
    "STOP_NO_CANDIDATES_LISTED",
    "STOP_BOUND_EXCEEDED",
    "STOP_AUTHORITY_LEAK",
    "STOP_UNTYPED_CANDIDATE",
    "STOP_IMPERSONATION_RISK",
]


ALLOWED_INPUTS_V0 = [
    "final_state",
    "final_receipt",
    "trace",
    "regime_v0",
    "move_registry_snapshot",
]

FORBIDDEN_INPUTS_V0 = [
    "uploads_as_authority",
    "latest_files",
    "directory_scans",
    "mtime_selection",
    "registry_mutation",
    "taxonomy_upgrade",
    "learned_move",
    "heuristic_memory",
    "autonomous_continuation",
    "topology_classification",
    "architecture_redesign",
    "patch_admission",
]

NON_IMPERSONATION_GUARDS_V0 = [
    "lawful_runner_move",
    "registered_move",
    "registry_patch",
    "patch_admission",
    "taxonomy_upgrade",
    "proof_closure",
    "engine_completion",
    "autonomous_continuation",
]


class CandidateSearchBoundsV0(TypedDict):
    max_candidates: int
    max_candidate_depth: int
    source_scope: str
    registry_effect: str


class CandidateSpecV0(TypedDict, total=False):
    candidate_id: str
    candidate_kind: AllowedCandidateKind
    smallest_honest_reading: str
    proposed_applies_when: str
    proposed_action: str
    proposed_readout: str
    proposed_halt_behavior: str
    must_not_impersonate: list[str]
    disposition: CandidateDisposition
    rejection_reason: RejectionReason | None


class BoundedCandidateSearchSurfaceV0(TypedDict):
    object_id: str
    object_kind: str
    trigger_halt: str
    authority_class: str
    truth_status: str
    allowed_inputs: list[str]
    forbidden_inputs: list[str]
    allowed_candidate_kind: AllowedCandidateKind
    search_bounds: CandidateSearchBoundsV0
    rejection_reasons: list[str]
    non_impersonation_guards: list[str]
    stop_conditions: list[str]


class CandidateSearchReceiptV0(TypedDict):
    receipt_kind: str
    surface_id: str
    trigger_halt: str
    searched_inputs: list[str]
    bounds_applied: CandidateSearchBoundsV0
    listed_candidates: list[CandidateSpecV0]
    rejected_candidates: list[CandidateSpecV0]
    terminal_result: StopCondition
    receipt_sig8: str


DEFAULT_BOUNDS_V0: CandidateSearchBoundsV0 = {
    "max_candidates": 8,
    "max_candidate_depth": 1,
    "source_scope": "current_halt_surface_only",
    "registry_effect": "none",
}


SURFACE_V0: BoundedCandidateSearchSurfaceV0 = {
    "object_id": SURFACE_ID,
    "object_kind": "CANDIDATE_SEARCH_SURFACE",
    "trigger_halt": TRIGGER_HALT,
    "authority_class": "NON_AUTHORITY_READOUT",
    "truth_status": "NON_CLAIM",
    "allowed_inputs": ALLOWED_INPUTS_V0,
    "forbidden_inputs": FORBIDDEN_INPUTS_V0,
    "allowed_candidate_kind": "MOVE_SPEC_CANDIDATE",
    "search_bounds": DEFAULT_BOUNDS_V0,
    "rejection_reasons": list(RejectionReason.__args__),  # type: ignore[attr-defined]
    "non_impersonation_guards": NON_IMPERSONATION_GUARDS_V0,
    "stop_conditions": list(StopCondition.__args__),  # type: ignore[attr-defined]
}


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def without_receipt_sig8(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            key: without_receipt_sig8(value)
            for key, value in obj.items()
            if key != "receipt_sig8"
        }
    if isinstance(obj, list):
        return [without_receipt_sig8(value) for value in obj]
    return obj


def sig8(obj: Any) -> str:
    body = canonical_json(without_receipt_sig8(obj)).encode("utf-8")
    return hashlib.sha256(body).hexdigest()[:8]


def reject_candidate(candidate: CandidateSpecV0, reason: RejectionReason) -> CandidateSpecV0:
    rejected = dict(candidate)
    rejected["disposition"] = "REJECTED"
    rejected["rejection_reason"] = reason
    return rejected  # type: ignore[return-value]


def candidate_rejection_reason(candidate: CandidateSpecV0) -> RejectionReason | None:
    if candidate.get("candidate_kind") != "MOVE_SPEC_CANDIDATE":
        return "NOT_A_MOVE_SPEC_CANDIDATE"

    required = [
        "candidate_id",
        "smallest_honest_reading",
        "proposed_applies_when",
        "proposed_action",
        "proposed_readout",
        "proposed_halt_behavior",
        "must_not_impersonate",
    ]
    for field in required:
        if field not in candidate:
            return "UNTYPED_CANDIDATE"

    guards = candidate.get("must_not_impersonate")
    if not isinstance(guards, list) or not set(NON_IMPERSONATION_GUARDS_V0).issubset(set(guards)):
        return "MISSING_NON_IMPERSONATION_GUARD"

    text = canonical_json(candidate)
    forbidden_markers = {
        "registry_patch": "REGISTRY_MUTATION_LEAK",
        "patch_admission": "PATCH_ADMISSION_LEAK",
        "taxonomy_upgrade": "TAXONOMY_UPGRADE_LEAK",
        "heuristic_memory": "HEURISTIC_MEMORY_LEAK",
        "architecture_redesign": "ARCHITECTURE_REDESIGN_LEAK",
        "topology_classification": "TOPOLOGY_CLASSIFICATION_LEAK",
        "autonomous_continuation": "SOURCE_SCOPE_LEAK",
    }
    for marker, reason in forbidden_markers.items():
        if marker in text:
            return reason  # type: ignore[return-value]

    return None


def build_candidate_search_receipt(
    *,
    searched_inputs: list[str],
    candidates: list[CandidateSpecV0],
    bounds: CandidateSearchBoundsV0 | None = None,
) -> CandidateSearchReceiptV0:
    active_bounds = bounds or DEFAULT_BOUNDS_V0

    listed: list[CandidateSpecV0] = []
    rejected: list[CandidateSpecV0] = []

    if searched_inputs != ALLOWED_INPUTS_V0:
        terminal: StopCondition = "STOP_AUTHORITY_LEAK"
        rejected = [reject_candidate(candidate, "SOURCE_SCOPE_LEAK") for candidate in candidates]
    elif len(candidates) > active_bounds["max_candidates"]:
        terminal = "STOP_BOUND_EXCEEDED"
        rejected = [reject_candidate(candidate, "UNBOUNDED_SEARCH") for candidate in candidates]
    else:
        terminal = "STOP_CANDIDATE_SEARCH_COMPLETE"
        for candidate in candidates:
            reason = candidate_rejection_reason(candidate)
            if reason is None:
                accepted = dict(candidate)
                accepted["disposition"] = "LISTED_NON_AUTHORITY"
                accepted["rejection_reason"] = None
                listed.append(accepted)  # type: ignore[arg-type]
            else:
                rejected.append(reject_candidate(candidate, reason))

        if not listed and not rejected:
            terminal = "STOP_NO_CANDIDATES_LISTED"
        elif any(row["rejection_reason"] == "MISSING_NON_IMPERSONATION_GUARD" for row in rejected):
            terminal = "STOP_IMPERSONATION_RISK"
        elif any(row["rejection_reason"] == "UNTYPED_CANDIDATE" for row in rejected):
            terminal = "STOP_UNTYPED_CANDIDATE"

    receipt: CandidateSearchReceiptV0 = {
        "receipt_kind": RECEIPT_KIND,
        "surface_id": SURFACE_ID,
        "trigger_halt": TRIGGER_HALT,
        "searched_inputs": searched_inputs,
        "bounds_applied": active_bounds,
        "listed_candidates": listed,
        "rejected_candidates": rejected,
        "terminal_result": terminal,
        "receipt_sig8": "",
    }
    receipt["receipt_sig8"] = sig8(receipt)
    return receipt


if __name__ == "__main__":
    receipt = build_candidate_search_receipt(
        searched_inputs=ALLOWED_INPUTS_V0,
        candidates=[],
    )
    print(canonical_json({"surface": SURFACE_V0, "empty_receipt": receipt}))

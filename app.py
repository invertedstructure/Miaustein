from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any

try:
    import streamlit as st
except ModuleNotFoundError:  # allows headless receipt tests without Streamlit installed
    st = None  # type: ignore[assignment]


MAX_STEPS = 16

BASE_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = BASE_DIR / "fixtures"
REGIME_PATH = FIXTURES_DIR / "regime_v0.json"
STATE_PATH = FIXTURES_DIR / "seed_state.json"
RUNS_DIR = BASE_DIR / "runs"

REQUIRED_REGIME_FIELDS = [
    "regime_id", "boundary", "allowed_object_kinds", "required_typed_record_fields",
    "move_registry", "halt_codes", "receipt_schema", "regime_patch_policy",
]

REQUIRED_STATE_FIELDS = ["state_id", "regime_id", "active_object", "typed_record", "status", "history"]

REQUIRED_TYPED_RECORD_FIELDS = [
    "object_id", "object_kind", "smallest_honest_reading", "authority_class",
    "truth_status", "layer", "route_role", "extractability", "content_scope",
    "allowed_consumers", "forbidden_impersonations", "declared_allowed_moves",
    "stop_conditions", "promotion_rule", "notes",
]

MOVE_ORDER_V0 = [
    "reject_invalid_state.v0",
    "type_active_object.v0",
    "checkpoint_typed_state.v0",
    "validate_typed_record_schema.v0",
    "validate_typed_record_regime_bindings.v0",
    "validate_history_integrity.v0",
    "validate_final_halt_readout_consistency.v0",
    "validate_no_legacy_ambiguous_fields.v0",
    "validate_registry_exhaustion_witness.v0",
    "validate_stop_needs_new_move_halt_vocabulary_binding.v0",
]

TERMINAL_HALT_CODES_V0 = [
    "INVALID_STATE", "INVALID_REGIME", "FIXTURE_LOAD_ERROR", "REGIME_MISMATCH",
    "NO_APPLICABLE_MOVE", "STOP_NEEDS_NEW_MOVE", "STEP_LIMIT_EXCEEDED",
]

CHECKPOINT_CODES_V0 = ["TYPED_STATE_READY"]
TYPED_READY_CHECKPOINT = "TYPED_STATE_READY"

# -----------------------------------------------------------------------------
# Capability Layer 2/4 foothold: bounded candidate search + typed stop surface.
#
# This layer is intentionally read-only.  It exposes the current lawful
# continuation surface without mutating state, editing the registry, evolving
# taxonomy, importing old monolith behavior, or interpreting frontier theory.
# -----------------------------------------------------------------------------
CANDIDATE_SEARCH_SCHEMA_V0 = "candidate_search_v0"

CANDIDATE_KINDS_V0 = [
    "REGISTERED_MOVE",
    "LOCAL_GOTCHA_REPAIR",
    "DECLARED_BUILD_UNIT",
    "MISSING_MOVE_PRESSURE",
    "UNDERTYPED_OBJECT",
    "NEEDS_EXTRACTION",
    "FRONTIER_BURDEN",
    "AUTHORITY_BLOCKED",
    "LAYER_COLLAPSE",
    "NO_CANDIDATE",
]

CANDIDATE_BLOCK_CODES_V0 = [
    "STOP_NEEDS_NEW_MOVE",
    "NO_APPLICABLE_MOVE",
    "INVALID_STATE",
    "INVALID_REGIME",
    "STOP_AUTHORITY_VIOLATION",
    "STOP_LAYER_COLLAPSE",
    "STOP_UNDERTYPED",
    "STOP_NEEDS_EXTRACTION",
    "STOP_FRONTIER",
]

CANDIDATE_SEARCH_MUST_NOT_IMPERSONATE_V0 = [
    "proof_closure",
    "theorem_success",
    "engine_completion",
    "autonomous_registry_evolution",
    "taxonomy_upgrade",
    "architecture_redesign",
]

CANDIDATE_BLOCK_NEXT_HANDLING_V0 = {
    "STOP_NEEDS_NEW_MOVE": "draft the smallest missing move outside this read-only inspector; require explicit human-authored patch before admission",
    "NO_APPLICABLE_MOVE": "inspect whether this is terminal, under-typed, or missing-move pressure; do not infer completion",
    "INVALID_STATE": "repair fixture/state shape only if local and already intended; otherwise stop",
    "INVALID_REGIME": "repair regime declaration only if the intended rule is already clear; otherwise stop",
    "STOP_AUTHORITY_VIOLATION": "return to declared fixture/source surface; reject memory, latest, mtime, scan, UI, or ambient authority",
    "STOP_LAYER_COLLAPSE": "split the object or unit by layer before proceeding",
    "STOP_UNDERTYPED": "type, withhold, split, or factor the blocking object before movement",
    "STOP_NEEDS_EXTRACTION": "perform a bounded extraction pass before using code/proto behavior",
    "STOP_FRONTIER": "stop; do not build movement that depends on unpromoted frontier material",
}



# -----------------------------------------------------------------------------
# Capability Envelope v0: minimal shape of Layers 2-5.
#
# This envelope is still projection-only.  It gives Codex/humans a typed
# continuation grammar without granting execution authority.  Layer 5 emits
# proposed-only records; it does not patch the move registry and does not make
# proposals executable.
# -----------------------------------------------------------------------------
CAPABILITY_ENVELOPE_SCHEMA_V0 = "capability_envelope_v0"
LOCAL_HEURISTICS_SCHEMA_V0 = "local_continuation_heuristics_v0"
CONTINUATION_TOPOLOGY_SCHEMA_V0 = "typed_continuation_topology_v0"
PROPOSED_EXTENSION_SCHEMA_V0 = "controlled_local_self_extension_v0"

HEURISTIC_AUTHORITY_V0 = "NON_AUTHORITY"
PROPOSAL_STATUS_PROPOSED_ONLY_V0 = "PROPOSED_ONLY"

TOPOLOGY_CODES_V0 = [
    "EXECUTABLE_MOVE_READY",
    "MISSING_MOVE",
    "MISSING_VOCABULARY",
    "UNDER_TYPED_OBJECT",
    "NEEDS_EXTRACTION",
    "FRONTIER_BLOCK",
    "AUTHORITY_BLOCK",
    "LAYER_COLLAPSE",
    "FRAME_MISMATCH",
    "OVER_STRONG_HALT",
    "WRONG_CONTINUATION_DIRECTION",
    "NO_CANDIDATE",
]

PROPOSAL_KINDS_V0 = [
    "MOVE_RECORD_PROPOSAL",
    "TAXONOMY_UPGRADE_PROPOSAL",
    "EXTRACTION_TASK_PROPOSAL",
    "FALLBACK_RETYPE_PROPOSAL",
    "NO_PROPOSAL",
]

PROPOSED_EXTENSION_MUST_NOT_IMPERSONATE_V0 = [
    "admitted_move",
    "registered_move",
    "executable_move",
    "taxonomy_upgrade",
    "theorem_progress",
    "bridge_closure",
    "architecture_redesign",
    "autonomous_self_extension",
]

PROPOSED_EXTENSION_ADMISSION_GATES_V0 = [
    "explicit_human_or_codex_patch",
    "registered_move_delta_is_reviewable",
    "applies_when_action_readout_halt_behavior_are_explicit",
    "falsifier_sweep_passes",
    "move_registry_update_is_explicit_and_non_autonomous",
]

# -----------------------------------------------------------------------------
# Proposal admission readout v0.
#
# This is still projection-only.  It checks whether a proposed-only Layer-5
# record is well shaped enough for an external human/Codex patch to act on it.
# It never admits the proposal, never inserts a move, and never makes a proposal
# executable.
# -----------------------------------------------------------------------------
PROPOSAL_ADMISSION_READOUT_SCHEMA_V0 = "proposed_missing_move_admission_readout_v0"

PROPOSAL_RECORD_REQUIRED_FIELDS_V0 = [
    "proposal_id",
    "proposal_kind",
    "proposal_status",
    "trigger_topology",
    "trigger_block_code",
    "target",
    "smallest_honest_reading",
    "proposed_delta",
    "allowed_next_handling",
    "admission_required",
    "executable_now",
    "in_move_registry",
    "mutates_state_now",
    "admission_gates",
    "falsifier_targets",
    "must_not_impersonate",
]

MOVE_RECORD_PROPOSAL_DELTA_REQUIRED_FIELDS_V0 = [
    "move_id",
    "applies_when",
    "action",
    "emitted_readout",
    "may_halt",
    "state_delta",
    "falsifier_sweep",
]

MOVE_RECORD_PROPOSAL_FALSIFIER_TARGETS_V0 = [
    "proposal_inserted_without_registry_patch",
    "proposal_marked_executable_now",
    "proposal_missing_must_not_impersonate",
    "proposal_attempts_taxonomy_or_architecture_widening",
]

PROPOSAL_ADMISSION_MUST_NOT_IMPERSONATE_V0 = [
    "admission_gate_passed",
    "admitted_move",
    "registered_move",
    "executable_move",
    "registry_delta",
    "taxonomy_delta",
    "architecture_change",
    "autonomous_self_extension",
]

# -----------------------------------------------------------------------------
# Missing-move draftability gate v0.
#
# This is the final local authorization seal before Codex/humans may draft a
# concrete missing-move body.  It authorizes *drafting only* when the requested
# draft belongs to a predeclared family.  It never admits the move, never makes
# the proposal executable, never changes taxonomy, and never patches the move
# registry.
# -----------------------------------------------------------------------------
MISSING_MOVE_DRAFT_POLICY_SCHEMA_V0 = "allowed_missing_move_draft_policy_v0"

DRAFTABILITY_VERDICTS_V0 = [
    "AUTHORIZED_TO_DRAFT",
    "BLOCKED_REQUIRES_HUMAN_APPROVAL",
    "NA",
]

DRAFTABILITY_MUST_NOT_IMPERSONATE_V0 = [
    "move_admission",
    "registered_move",
    "executable_move",
    "registry_delta",
    "taxonomy_delta",
    "architecture_change",
    "frontier_interpretation",
    "theorem_progress",
    "autonomous_self_authorization",
]

AUTHORIZED_MISSING_MOVE_DRAFT_FAMILIES_V0: dict[str, dict[str, Any]] = {
    "post_registry_exhaustion_validator.v0": {
        "family_id": "post_registry_exhaustion_validator.v0",
        "family_status": "PREDECLARED_AUTHORIZED_DRAFT_FAMILY",
        "smallest_honest_reading": (
            "after registry exhaustion and STOP_NEEDS_NEW_MOVE binding, draft exactly one "
            "small validator/readout move that extends the existing no-drift validation chain"
        ),
        "allowed_scope": "ONE_MOVE_ONLY",
        "target": "frozen_move_registry",
        "allowed_layer": "OUTER",
        "allowed_mode": "VALIDATOR_OR_READOUT_ONLY",
        "required_trigger_topology": "MISSING_MOVE",
        "required_trigger_block_code": "STOP_NEEDS_NEW_MOVE",
        "required_proposal_kind": "MOVE_RECORD_PROPOSAL",
        "requires_registry_exhaustion_witness": True,
        "requires_stop_needs_new_move_binding": True,
        "requires_proposal_admission_pass": True,
        "forbidden_draft_targets": [
            "kernel_build_move",
            "taxonomy_upgrade_move",
            "bridge_move",
            "frontier_interpretation_move",
            "architecture_refactor_move",
            "old_monolith_import_move",
            "generic_continue_move",
        ],
        "forbidden_effects": [
            "execute_now",
            "insert_into_registry_now",
            "change_taxonomy",
            "change_architecture",
            "interpret_frontier",
            "promote_theorem_status",
            "import_old_monolith_as_authority",
        ],
        "required_draft_fields": [
            "move_id",
            "applies_when",
            "action",
            "emitted_readout",
            "may_halt",
            "state_delta",
            "falsifier_sweep",
        ],
        "post_draft_requirement": "drafted_move_still_requires_external_verifier_falsifier_and_explicit_registry_patch",
    }
}

# -----------------------------------------------------------------------------
# Embedded starter fixtures for the first build cut.
#
# The runner still loads only from the declared fixture surface:
#   fixtures/regime_v0.json
#   fixtures/seed_state.json
# This block only bootstraps that surface when the app is run as a single file
# in a fresh directory. Existing fixture files are never overwritten.
# -----------------------------------------------------------------------------
STARTER_REGIME_V0: dict[str, Any] = {
    "allowed_object_kinds": [
        "BUILD_CUT_BOUNDARY",
        "MOVE",
        "RECEIPT",
        "TRACE",
        "UNRESOLVED",
    ],
    "boundary": {
        "authority": "fixtures_only",
        "declared_input_surface": [
            "fixtures/regime_v0.json",
            "fixtures/seed_state.json",
        ],
        "forbidden_inputs": [
            "uploads",
            "alternate_paths",
            "latest_files",
            "directory_scans",
            "mtimes",
            "uuids",
            "randomness",
            "ambient_workspace_state",
            "old_monolithic_app",
            "dynamic_imports",
        ],
        "ui_role": "cockpit_only",
    },
    "halt_codes": TERMINAL_HALT_CODES_V0,
    "move_registry": MOVE_ORDER_V0,
    "receipt_schema": "receipt_v0",
    "regime_id": "regime_v0",
    "regime_patch_policy": "PROPOSED_ONLY",
    "required_typed_record_fields": REQUIRED_TYPED_RECORD_FIELDS,
}

STARTER_SEED_STATE_V0: dict[str, Any] = {
    "active_object": {
        "object_id": "first_honest_build_cut",
        "object_kind": "BUILD_CUT_BOUNDARY",
        "smallest_honest_reading": "declared boundary for the smallest deterministic Streamlit move-runner v0",
    },
    "history": [],
    "regime_id": "regime_v0",
    "state_id": "seed_state_v0",
    "status": "untyped",
    "typed_record": None,
}

REQUIRED_HISTORY_ROW_FIELDS_V0 = [
    "move_id",
    "outcome",
    "checkpoint_code",
    "halt_code",
    "reason",
]

LEGACY_AMBIGUOUS_FIELDS_V0 = {
    "labels",
    "active_labels",
    "payload",
    "history_ref",
    "halt",
    "final_halt",
    "verdict",
    "receipt",
    "trace",
    "projection",
    "registry_patch",
    "learned_move",
    "inferred_move",
    "taxonomy_delta",
    "dynamic_regime_update",
}

PROJECTION_ONLY_FIELDS_V0 = {
    "repeated_states",
    "branching_observed",
    "typing_occurred",
    "invalidity_move_fired",
    "final_halt_readout_consistency_validated",
    "no_legacy_ambiguous_fields_validated",
    "registry_exhaustion_witness_validated",
}

LEGACY_AMBIGUOUS_HALT_CODES_V0 = {
    "HALT_NO_MOVE",
    "HALT_NEEDS_MOVE",
    "DONE",
    "COMPLETE",
    "SUCCESS",
    "PROOF_COMPLETE",
}

STOP_NEEDS_NEW_MOVE_BINDING_SPEC_V0: dict[str, Any] = {
    "unit_id": "post_registry_exhaustion_stop_needs_new_move_binding_spec.v0",
    "halt_code": "STOP_NEEDS_NEW_MOVE",
    "smallest_honest_meaning": (
        "continuation requires a lawful move not currently present in the frozen move registry"
    ),
    "must_not_impersonate": [
        "proof_closure",
        "theorem_success",
        "engine_completion",
        "autonomous_registry_evolution",
        "taxonomy_upgrade",
        "architecture_redesign",
    ],
    "allowed_next_handling": [
        "draft smallest missing move",
        "require explicit human-authored patch",
        "rerun from frozen fixtures after patch",
    ],
}


# -----------------------------------------------------------------------------
# Canonicalization and fixture surface
# -----------------------------------------------------------------------------
def canonical_json(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def write_canonical_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(obj), encoding="utf-8")


def ensure_fixture_surface() -> dict[str, Any]:
    """Create the declared fixture surface if this app is run as one file.

    Existing fixture files are never overwritten. That preserves the rule that
    the run uses only the declared frozen fixture surface, not UI state or
    ambient workspace repair.
    """
    report: dict[str, Any] = {
        "declared_input_surface": [
            REGIME_PATH.relative_to(BASE_DIR).as_posix(),
            STATE_PATH.relative_to(BASE_DIR).as_posix(),
        ],
        "created": [],
        "existing": [],
    }

    for path, payload in (
        (REGIME_PATH, STARTER_REGIME_V0),
        (STATE_PATH, STARTER_SEED_STATE_V0),
    ):
        rel = path.relative_to(BASE_DIR).as_posix()
        if path.exists():
            report["existing"].append(rel)
            continue
        write_canonical_json(path, payload)
        report["created"].append(rel)

    return report


def _without_self_hash_fields(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {
            k: _without_self_hash_fields(v)
            for k, v in obj.items()
            if k not in {"sig8", "receipt_sig8", "external_check_sig8"}
        }
    if isinstance(obj, list):
        return [_without_self_hash_fields(v) for v in obj]
    return obj


def sig8(obj: Any) -> str:
    body = canonical_json(_without_self_hash_fields(obj)).encode("utf-8")
    return hashlib.sha256(body).hexdigest()[:8]


def load_json_object(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        raw = path.read_text(encoding="utf-8")
    except Exception as exc:
        return None, f"cannot read {path.as_posix()}: {exc.__class__.__name__}"

    try:
        obj = json.loads(raw)
    except Exception as exc:
        return None, f"cannot parse {path.as_posix()}: {exc.__class__.__name__}"

    if not isinstance(obj, dict):
        return None, f"{path.as_posix()} is not a JSON object"

    return obj, None


# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
def validate_regime(regime: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    for field in REQUIRED_REGIME_FIELDS:
        if field not in regime:
            errors.append(f"missing regime field: {field}")

    if errors:
        return errors

    if not isinstance(regime["regime_id"], str) or not regime["regime_id"]:
        errors.append("regime_id must be a non-empty string")

    if not isinstance(regime["boundary"], dict):
        errors.append("boundary must be an object")

    if not isinstance(regime["allowed_object_kinds"], list) or not all(
        isinstance(x, str) and x for x in regime["allowed_object_kinds"]
    ):
        errors.append("allowed_object_kinds must be a list of non-empty strings")

    if regime.get("required_typed_record_fields") != REQUIRED_TYPED_RECORD_FIELDS:
        errors.append("required_typed_record_fields must match the v0 typed record fields exactly")

    if regime.get("move_registry") != MOVE_ORDER_V0:
        errors.append("move_registry must match the v0 deterministic priority order exactly")

    halt_codes = regime.get("halt_codes")
    if halt_codes != TERMINAL_HALT_CODES_V0:
        errors.append("halt_codes must match the v0 terminal halt codes exactly")
    elif TYPED_READY_CHECKPOINT in halt_codes:
        errors.append("TYPED_STATE_READY is a checkpoint code, not a terminal halt code")

    if not isinstance(regime.get("receipt_schema"), str) or not regime.get("receipt_schema"):
        errors.append("receipt_schema must be a non-empty string")

    if regime.get("regime_patch_policy") != "PROPOSED_ONLY":
        errors.append("regime_patch_policy must be PROPOSED_ONLY")

    return errors


def state_validation_errors(state: Any, regime: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(state, dict):
        return ["state is not an object"]

    for field in REQUIRED_STATE_FIELDS:
        if field not in state:
            errors.append(f"missing state field: {field}")

    if errors:
        return errors

    if not isinstance(state["state_id"], str) or not state["state_id"]:
        errors.append("state_id must be a non-empty string")

    if not isinstance(state["regime_id"], str) or not state["regime_id"]:
        errors.append("regime_id must be a non-empty string")

    if state["active_object"] is not None and not isinstance(state["active_object"], dict):
        errors.append("active_object must be an object or null")

    if state["typed_record"] is not None and not isinstance(state["typed_record"], dict):
        errors.append("typed_record must be an object or null")

    if not isinstance(state["status"], str) or not state["status"]:
        errors.append("status must be a non-empty string")

    if not isinstance(state["history"], list):
        errors.append("history must be a list")

    active_object = state.get("active_object")
    if isinstance(active_object, dict):
        object_kind = active_object.get("object_kind")
        if not isinstance(active_object.get("object_id"), str) or not active_object.get("object_id"):
            errors.append("active_object.object_id must be a non-empty string")
        if not isinstance(object_kind, str) or not object_kind:
            errors.append("active_object.object_kind must be a non-empty string")
        elif object_kind not in regime.get("allowed_object_kinds", []):
            errors.append(f"active_object.object_kind is not allowed by regime: {object_kind}")

    typed_record = state.get("typed_record")
    if isinstance(typed_record, dict):
        for field in regime.get("required_typed_record_fields", []):
            if field not in typed_record:
                errors.append(f"typed_record missing required field: {field}")

    return errors


# -----------------------------------------------------------------------------
# Moves: apply only registered lawful movement; checkpoints are nonterminal.
# -----------------------------------------------------------------------------
def history_has_checkpoint(state: dict[str, Any], checkpoint_code: str) -> bool:
    history = state.get("history") if isinstance(state.get("history"), list) else []
    for row in history:
        if isinstance(row, dict) and row.get("checkpoint_code") == checkpoint_code:
            return True
    return False


def history_has_move(state: dict[str, Any], move_id: str) -> bool:
    history = state.get("history") if isinstance(state.get("history"), list) else []
    for row in history:
        if isinstance(row, dict) and row.get("move_id") == move_id:
            return True
    return False


def typed_record_schema_errors(state: dict[str, Any], regime: dict[str, Any]) -> list[str]:
    typed_record = state.get("typed_record")
    if not isinstance(typed_record, dict):
        return ["typed_record is not present"]

    required = regime.get("required_typed_record_fields")
    if not isinstance(required, list) or not all(isinstance(x, str) and x for x in required):
        return ["regime.required_typed_record_fields is not a list of non-empty strings"]

    required_set = set(required)
    actual_set = set(typed_record.keys())

    missing_fields = sorted(required_set - actual_set)
    unexpected_fields = sorted(actual_set - required_set)
    legacy_ambiguous_fields = [field for field in ["allowed_next_moves"] if field in actual_set]

    errors: list[str] = []
    if missing_fields:
        errors.append("missing_fields=" + ",".join(missing_fields))
    if unexpected_fields:
        errors.append("unexpected_fields=" + ",".join(unexpected_fields))
    if legacy_ambiguous_fields:
        errors.append("legacy_ambiguous_fields=" + ",".join(legacy_ambiguous_fields))
    return errors


def move_reject_invalid_state_applies(state: dict[str, Any], regime: dict[str, Any]) -> tuple[bool, str]:
    errors = state_validation_errors(state, regime)
    if errors:
        return True, "; ".join(errors)
    return False, "state has required v0 shape"


def move_type_active_object_applies(state: dict[str, Any], regime: dict[str, Any]) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if isinstance(state.get("active_object"), dict) and state.get("typed_record") is None:
        return True, "active_object exists and typed_record is missing"
    return False, "typed_record already present or no active_object exists"


def move_checkpoint_typed_state_applies(state: dict[str, Any], regime: dict[str, Any]) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    if history_has_checkpoint(state, TYPED_READY_CHECKPOINT):
        return False, "typed-ready checkpoint is already recorded"
    return True, "typed_record is present; record typed-ready checkpoint and continue inspection"




def typed_record_regime_binding_errors(state: dict[str, Any], regime: dict[str, Any]) -> list[str]:
    typed_record = state.get("typed_record")
    if not isinstance(typed_record, dict):
        return ["typed_record is not present"]

    allowed_object_kinds = regime.get("allowed_object_kinds")
    move_registry = regime.get("move_registry")
    halt_codes = regime.get("halt_codes")

    errors: list[str] = []
    if not isinstance(allowed_object_kinds, list) or not all(isinstance(x, str) and x for x in allowed_object_kinds):
        errors.append("regime.allowed_object_kinds is not a list of non-empty strings")
    if not isinstance(move_registry, list) or not all(isinstance(x, str) and x for x in move_registry):
        errors.append("regime.move_registry is not a list of non-empty strings")
    if not isinstance(halt_codes, list) or not all(isinstance(x, str) and x for x in halt_codes):
        errors.append("regime.halt_codes is not a list of non-empty strings")
    if errors:
        return errors

    object_kind = typed_record.get("object_kind")
    if not isinstance(object_kind, str) or object_kind not in allowed_object_kinds:
        errors.append("unknown_object_kind=" + str(object_kind))

    declared_allowed_moves = typed_record.get("declared_allowed_moves")
    if not isinstance(declared_allowed_moves, list) or not all(
        isinstance(x, str) and x for x in declared_allowed_moves
    ):
        errors.append("declared_allowed_moves is not a list of non-empty strings")
    else:
        unregistered = sorted([move_id for move_id in declared_allowed_moves if move_id not in move_registry])
        if unregistered:
            errors.append("unregistered_declared_moves=" + ",".join(unregistered))

    stop_conditions = typed_record.get("stop_conditions")
    if not isinstance(stop_conditions, list) or not all(isinstance(x, str) and x for x in stop_conditions):
        errors.append("stop_conditions is not a list of non-empty strings")
    else:
        unknown = sorted([halt_code for halt_code in stop_conditions if halt_code not in halt_codes])
        if unknown:
            errors.append("unknown_stop_conditions=" + ",".join(unknown))

    return errors




def history_move_indices(history: list[Any], move_id: str) -> list[int]:
    return [
        index
        for index, row in enumerate(history)
        if isinstance(row, dict) and row.get("move_id") == move_id
    ]


def history_integrity_errors(state: dict[str, Any], regime: dict[str, Any]) -> list[str]:
    history = state.get("history")
    if not isinstance(history, list) or not history:
        return ["history_not_list"]

    move_registry = regime.get("move_registry")
    if not isinstance(move_registry, list) or not all(isinstance(x, str) and x for x in move_registry):
        return ["unregistered_history_move: regime.move_registry is invalid"]
    registered_moves = set(move_registry)

    required_history_fields = set(REQUIRED_HISTORY_ROW_FIELDS_V0)
    errors: list[str] = []

    for index, row in enumerate(history):
        if not isinstance(row, dict):
            errors.append(f"missing_history_fields: row[{index}] is not an object")
            continue

        missing = sorted(required_history_fields - set(row.keys()))
        if missing:
            errors.append(f"missing_history_fields: row[{index}] missing {','.join(missing)}")

        move_id = row.get("move_id")
        if not isinstance(move_id, str) or not move_id:
            errors.append(f"missing_history_fields: row[{index}] move_id is not a non-empty string")
        elif move_id not in registered_moves:
            errors.append(f"unregistered_history_move: row[{index}] {move_id}")

        if row.get("halt_code") is not None:
            errors.append(f"premature_history_halt: row[{index}] halt_code={row.get('halt_code')}")

    if errors:
        return errors

    checkpoint_indices = history_move_indices(history, "checkpoint_typed_state.v0")
    if len(checkpoint_indices) != 1:
        return ["duplicate_typed_ready_checkpoint"]

    type_indices = history_move_indices(history, "type_active_object.v0")
    schema_indices = history_move_indices(history, "validate_typed_record_schema.v0")
    binding_indices = history_move_indices(history, "validate_typed_record_regime_bindings.v0")

    if not type_indices or not schema_indices or not binding_indices:
        return ["history_order_violation"]

    type_index = type_indices[0]
    checkpoint_index = checkpoint_indices[0]
    schema_index = schema_indices[0]
    binding_index = binding_indices[0]

    if not (type_index < checkpoint_index < schema_index < binding_index):
        return ["history_order_violation"]

    return []




def final_halt_readout_consistency_errors(state: dict[str, Any], regime: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if state.get("status") != "history_integrity_validated":
        errors.append("final_status_mismatch")

    history = state.get("history")
    if not isinstance(history, list) or not history:
        return ["history_not_list"]

    expected_prefix = [
        "type_active_object.v0",
        "checkpoint_typed_state.v0",
        "validate_typed_record_schema.v0",
        "validate_typed_record_regime_bindings.v0",
        "validate_history_integrity.v0",
    ]
    actual_moves = [row.get("move_id") for row in history if isinstance(row, dict)]
    if actual_moves != expected_prefix:
        errors.append("moves_applied_history_mismatch")

    if history_move_indices(history, "validate_history_integrity.v0") != [4]:
        errors.append("history_integrity_position_mismatch")

    if history_has_move(state, "validate_final_halt_readout_consistency.v0"):
        errors.append("final_halt_readout_consistency_already_recorded")

    if any(isinstance(row, dict) and row.get("halt_code") is not None for row in history):
        errors.append("premature_history_halt")

    typed_record = state.get("typed_record")
    if not isinstance(typed_record, dict):
        errors.append("typed_record_missing")
    else:
        stop_conditions = typed_record.get("stop_conditions")
        if not isinstance(stop_conditions, list) or "STOP_NEEDS_NEW_MOVE" not in stop_conditions:
            errors.append("typed_record_stop_surface_missing")

        forbidden_impersonations = typed_record.get("forbidden_impersonations")
        required_cautions = {"theorem_claim", "proof_closure", "polished_architecture"}
        if not isinstance(forbidden_impersonations, list) or not required_cautions.issubset(set(forbidden_impersonations)):
            errors.append("halt_impersonation_risk")

    halt_codes = regime.get("halt_codes")
    if not isinstance(halt_codes, list) or "STOP_NEEDS_NEW_MOVE" not in halt_codes:
        errors.append("regime_stop_surface_missing")

    return errors




def _field_scan_errors(prefix: str, obj: Any, forbidden: set[str], reason_name: str) -> list[str]:
    if not isinstance(obj, dict):
        return []
    present = sorted(set(obj.keys()) & forbidden)
    return [f"{reason_name}: {prefix} contains {','.join(present)}"] if present else []


def _key_parts(actual: set[str], expected: set[str]) -> tuple[list[str], list[str]]:
    return sorted(actual - expected), sorted(expected - actual)


def _extend_direct_field_scans(errors: list[str], prefix: str, obj: Any) -> None:
    errors.extend(_field_scan_errors(prefix, obj, LEGACY_AMBIGUOUS_FIELDS_V0, "legacy_state_field_present"))
    errors.extend(_field_scan_errors(prefix, obj, PROJECTION_ONLY_FIELDS_V0, "projection_field_embedded_in_state"))


def no_legacy_ambiguous_fields_errors(state: dict[str, Any], regime: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if state.get("status") != "final_halt_readout_consistency_validated":
        errors.append("final_status_mismatch")

    unexpected, missing = _key_parts(set(state.keys()), set(REQUIRED_STATE_FIELDS))
    if unexpected:
        errors.append("unexpected_state_field=" + ",".join(unexpected))
    if missing:
        errors.append("missing_state_field=" + ",".join(missing))
    _extend_direct_field_scans(errors, "state", state)

    active_object = state.get("active_object")
    if not isinstance(active_object, dict):
        errors.append("active_object_missing")
    else:
        unexpected, missing = _key_parts(set(active_object.keys()), {"object_id", "object_kind", "smallest_honest_reading"})
        if unexpected:
            errors.append("unexpected_active_object_field=" + ",".join(unexpected))
        if missing:
            errors.append("missing_active_object_field=" + ",".join(missing))
        _extend_direct_field_scans(errors, "active_object", active_object)

    typed_record = state.get("typed_record")
    required_typed_record_fields = regime.get("required_typed_record_fields")
    if not isinstance(typed_record, dict):
        errors.append("typed_record_missing")
    elif not isinstance(required_typed_record_fields, list):
        errors.append("regime_required_typed_record_fields_invalid")
    else:
        unexpected, missing = _key_parts(set(typed_record.keys()), set(required_typed_record_fields))
        if unexpected or missing:
            parts = (["unexpected=" + ",".join(unexpected)] if unexpected else []) + (["missing=" + ",".join(missing)] if missing else [])
            errors.append("typed_record_field_mismatch:" + ";".join(parts))
        _extend_direct_field_scans(errors, "typed_record", typed_record)

        guards = typed_record.get("forbidden_impersonations")
        required = {"theorem_claim", "proof_closure", "polished_architecture", "old_monolithic_app", "dynamic_regime_evolution"}
        if not isinstance(guards, list) or not required.issubset(set(guards)):
            errors.append("forbidden_impersonation_missing")
        stop_conditions = typed_record.get("stop_conditions")
        if isinstance(stop_conditions, list):
            legacy = sorted(set(str(v) for v in stop_conditions) & LEGACY_AMBIGUOUS_HALT_CODES_V0)
            if legacy:
                errors.append("legacy_halt_code_present=" + ",".join(legacy))

    history = state.get("history")
    if not isinstance(history, list) or not history:
        errors.append("history_not_list")
    else:
        expected_history_fields = set(REQUIRED_HISTORY_ROW_FIELDS_V0)
        for index, row in enumerate(history):
            if not isinstance(row, dict):
                errors.append(f"unexpected_history_field: row[{index}] is not an object")
                continue
            unexpected, missing = _key_parts(set(row.keys()), expected_history_fields)
            if unexpected or missing:
                parts = (["unexpected=" + ",".join(unexpected)] if unexpected else []) + (["missing=" + ",".join(missing)] if missing else [])
                errors.append(f"unexpected_history_field: row[{index}] " + ";".join(parts))
            checkpoint_code, halt_code = row.get("checkpoint_code"), row.get("halt_code")
            if checkpoint_code is not None and checkpoint_code not in CHECKPOINT_CODES_V0:
                errors.append(f"checkpoint_halt_confusion: row[{index}] unknown checkpoint_code={checkpoint_code}")
            if halt_code == TYPED_READY_CHECKPOINT:
                errors.append(f"checkpoint_halt_confusion: row[{index}] TYPED_STATE_READY used as halt_code")
            if halt_code == "STOP_NEEDS_NEW_MOVE":
                errors.append(f"checkpoint_halt_confusion: row[{index}] STOP_NEEDS_NEW_MOVE embedded in history halt_code")
            if isinstance(halt_code, str) and halt_code in LEGACY_AMBIGUOUS_HALT_CODES_V0:
                errors.append("legacy_halt_code_present=" + halt_code)
            _extend_direct_field_scans(errors, f"history[{index}]", row)

    halt_codes = regime.get("halt_codes")
    if not isinstance(halt_codes, list):
        errors.append("regime_halt_codes_invalid")
    else:
        legacy = sorted(set(str(v) for v in halt_codes) & LEGACY_AMBIGUOUS_HALT_CODES_V0)
        if legacy:
            errors.append("legacy_halt_code_present=" + ",".join(legacy))
        if TYPED_READY_CHECKPOINT in halt_codes:
            errors.append("checkpoint_halt_confusion: TYPED_STATE_READY listed as halt_code")

    unexpected = sorted(set(regime.keys()) - set(REQUIRED_REGIME_FIELDS))
    if unexpected:
        errors.append("unexpected_regime_field=" + ",".join(unexpected))
    return errors




def registry_exhaustion_witness_errors(state: dict[str, Any], regime: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if state.get("status") != "no_legacy_ambiguous_fields_validated":
        errors.append("final_status_mismatch")

    move_registry = regime.get("move_registry")
    if not isinstance(move_registry, list) or not all(isinstance(x, str) and x for x in move_registry):
        errors.append("move_registry_missing")
        move_registry = []
    else:
        if move_registry != MOVE_ORDER_V0:
            errors.append("move_registry_not_ordered")
        if len(move_registry) != len(set(move_registry)):
            errors.append("duplicate_registered_move")

    halt_codes = regime.get("halt_codes")
    if not isinstance(halt_codes, list) or "STOP_NEEDS_NEW_MOVE" not in halt_codes:
        errors.append("stop_needs_new_move_missing")
    if isinstance(move_registry, list) and "STOP_NEEDS_NEW_MOVE" in move_registry:
        errors.append("stop_needs_new_move_registered_as_move")

    history = state.get("history")
    if not isinstance(history, list) or not history:
        errors.append("history_not_list")
        return errors

    expected_prefix = [
        "type_active_object.v0",
        "checkpoint_typed_state.v0",
        "validate_typed_record_schema.v0",
        "validate_typed_record_regime_bindings.v0",
        "validate_history_integrity.v0",
        "validate_final_halt_readout_consistency.v0",
        "validate_no_legacy_ambiguous_fields.v0",
    ]
    actual_moves = [row.get("move_id") for row in history if isinstance(row, dict)]
    if actual_moves != expected_prefix:
        errors.append("applied_sequence_order_mismatch")

    registered_moves = set(move_registry) if isinstance(move_registry, list) else set()
    for move_id in actual_moves:
        if move_id not in registered_moves:
            errors.append("applied_move_not_registered=" + str(move_id))

    for index, row in enumerate(history):
        if not isinstance(row, dict):
            errors.append(f"history_row_not_object={index}")
            continue
        checkpoint_code = row.get("checkpoint_code")
        halt_code = row.get("halt_code")
        if halt_code is not None:
            errors.append(f"premature_history_halt=row[{index}]")
        if checkpoint_code == "STOP_NEEDS_NEW_MOVE":
            errors.append(f"checkpoint_halt_confusion=row[{index}] STOP_NEEDS_NEW_MOVE used as checkpoint_code")
        if halt_code == TYPED_READY_CHECKPOINT:
            errors.append(f"checkpoint_halt_confusion=row[{index}] TYPED_STATE_READY used as halt_code")
        if checkpoint_code is not None and checkpoint_code not in CHECKPOINT_CODES_V0:
            errors.append(f"checkpoint_halt_confusion=row[{index}] unknown checkpoint_code={checkpoint_code}")

    if history_move_indices(history, "validate_no_legacy_ambiguous_fields.v0") != [6]:
        errors.append("no_legacy_position_mismatch")
    if history_has_move(state, "validate_registry_exhaustion_witness.v0"):
        errors.append("registry_exhaustion_witness_already_recorded")

    typed_record = state.get("typed_record")
    if not isinstance(typed_record, dict):
        errors.append("typed_record_missing")
    else:
        declared_allowed_moves = typed_record.get("declared_allowed_moves")
        if not isinstance(declared_allowed_moves, list):
            errors.append("typed_record_declared_moves_missing")
        elif "validate_registry_exhaustion_witness.v0" not in declared_allowed_moves:
            errors.append("typed_record_declared_move_missing=validate_registry_exhaustion_witness.v0")
        stop_conditions = typed_record.get("stop_conditions")
        if not isinstance(stop_conditions, list) or "STOP_NEEDS_NEW_MOVE" not in stop_conditions:
            errors.append("typed_record_stop_surface_missing")
        forbidden_impersonations = typed_record.get("forbidden_impersonations")
        required_cautions = {"theorem_claim", "proof_closure", "polished_architecture", "dynamic_regime_evolution"}
        if not isinstance(forbidden_impersonations, list) or not required_cautions.issubset(set(forbidden_impersonations)):
            errors.append("exhaustion_reason_impersonates_completion")

    return errors




def _field_present_anywhere(obj: Any, field_name: str) -> bool:
    if isinstance(obj, dict):
        if field_name in obj:
            return True
        return any(_field_present_anywhere(value, field_name) for value in obj.values())
    if isinstance(obj, list):
        return any(_field_present_anywhere(value, field_name) for value in obj)
    return False


def _dry_stop_needs_new_move_bound_state(state: dict[str, Any]) -> dict[str, Any]:
    candidate = append_history(
        state,
        {
            "move_id": "validate_stop_needs_new_move_halt_vocabulary_binding.v0",
            "outcome": "stop_needs_new_move_halt_vocabulary_bound",
            "checkpoint_code": None,
            "halt_code": None,
            "reason": "STOP_NEEDS_NEW_MOVE is bound as explicit missing-move pressure, not autonomous evolution",
        },
    )
    candidate["status"] = "stop_needs_new_move_halt_vocabulary_bound"
    return candidate


def stop_needs_new_move_halt_vocabulary_binding_errors(
    state: dict[str, Any], regime: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    halt_code = "STOP_NEEDS_NEW_MOVE"
    move_id = "validate_stop_needs_new_move_halt_vocabulary_binding.v0"
    history = state.get("history") if isinstance(state.get("history"), list) else []

    if state.get("status") != "registry_exhaustion_witness_validated":
        errors.append("terminal_halt_binding_missing")
    if not isinstance(state.get("history"), list):
        errors.append("terminal_halt_binding_missing")
    if history_move_indices(history, "validate_registry_exhaustion_witness.v0") != [7]:
        errors.append("terminal_halt_binding_missing")
    if history_has_move(state, move_id):
        errors.append("terminal_halt_binding_missing")

    for index, row in enumerate(history):
        if isinstance(row, dict) and halt_code in {row.get("move_id"), row.get("checkpoint_code"), row.get("halt_code")}:
            errors.append(f"stop_needs_new_move_used_in_history=row[{index}]")

    typed_record = state.get("typed_record")
    if not isinstance(typed_record, dict):
        errors.append("stop_needs_new_move_missing_from_typed_record")
    else:
        if not isinstance(typed_record.get("stop_conditions"), list) or halt_code not in typed_record["stop_conditions"]:
            errors.append("stop_needs_new_move_missing_from_typed_record")
        guards = typed_record.get("forbidden_impersonations")
        required_guards = set(STOP_NEEDS_NEW_MOVE_BINDING_SPEC_V0["must_not_impersonate"])
        if not isinstance(guards, list) or not required_guards.issubset(set(guards)):
            errors.append("halt_impersonation_guard_missing")

    if not isinstance(regime.get("halt_codes"), list) or halt_code not in regime["halt_codes"]:
        errors.append("stop_needs_new_move_missing_from_regime")
    if isinstance(regime.get("move_registry"), list) and halt_code in regime["move_registry"]:
        errors.append("stop_needs_new_move_registered_as_move")

    spec = STOP_NEEDS_NEW_MOVE_BINDING_SPEC_V0
    expected_meaning = "continuation requires a lawful move not currently present in the frozen move registry"
    expected_next_handling = [
        "draft smallest missing move",
        "require explicit human-authored patch",
        "rerun from frozen fixtures after patch",
    ]
    required_spec_guards = {
        "proof_closure", "theorem_success", "engine_completion",
        "autonomous_registry_evolution", "taxonomy_upgrade", "architecture_redesign",
    }
    if spec.get("halt_code") != halt_code:
        errors.append("terminal_halt_binding_missing")
    if spec.get("smallest_honest_meaning") != expected_meaning:
        errors.append("halt_meaning_mismatch")
    if not isinstance(spec.get("must_not_impersonate"), list) or not required_spec_guards.issubset(set(spec.get("must_not_impersonate") or [])):
        errors.append("halt_impersonation_guard_missing")
    if spec.get("allowed_next_handling") != expected_next_handling:
        errors.append("allowed_next_handling_missing")

    if regime.get("regime_patch_policy") != "PROPOSED_ONLY":
        errors.append("autonomous_registry_evolution_leak")
    if any(_field_present_anywhere(state, f) or _field_present_anywhere(regime, f) for f in ("registry_patch", "taxonomy_delta", "inferred_move", "learned_move")):
        errors.append("autonomous_registry_evolution_leak")
    if any(_field_present_anywhere(state, f) or _field_present_anywhere(regime, f) for f in ("dynamic_regime_update", "learned_move")):
        errors.append("dynamic_regime_update_leak")

    candidate = _dry_stop_needs_new_move_bound_state(state)
    if inspect_applicable_moves(candidate, regime):
        errors.append("terminal_halt_binding_missing")
    dry_halt_code, dry_reason = classify_no_applicable_move(candidate, regime)
    if dry_halt_code != halt_code:
        errors.append("terminal_halt_binding_missing")
    elif dry_reason != expected_meaning:
        errors.append("halt_meaning_mismatch")
    return errors




VALIDATION_APPLIES_SPECS_V0 = {
    "validate_typed_record_schema.v0": {
        "required_status": "typed_ready_checkpointed",
        "prerequisite_checkpoint": TYPED_READY_CHECKPOINT,
        "required_regime_fields": ["required_typed_record_fields"],
        "already_reason": "typed-record schema validation already recorded",
        "applies_reason": "typed-ready checkpoint is recorded; validate typed_record against required schema fields",
    },
    "validate_typed_record_regime_bindings.v0": {
        "required_status": "typed_record_schema_validated",
        "prerequisite_move": "validate_typed_record_schema.v0",
        "required_regime_fields": ["allowed_object_kinds", "move_registry", "halt_codes"],
        "already_reason": "typed-record regime binding validation already recorded",
        "applies_reason": "typed-record schema is validated; validate typed_record references against the active regime",
    },
    "validate_history_integrity.v0": {
        "required_status": "typed_record_regime_bound",
        "already_reason": "history integrity validation already recorded",
        "applies_reason": "typed-record regime bindings are validated; validate the local history spine",
    },
    "validate_final_halt_readout_consistency.v0": {
        "required_status": "history_integrity_validated",
        "prerequisite_move": "validate_history_integrity.v0",
        "already_reason": "final halt/readout consistency validation already recorded",
        "applies_reason": "history integrity is validated; validate the final halt/readout surface",
    },
    "validate_no_legacy_ambiguous_fields.v0": {
        "required_status": "final_halt_readout_consistency_validated",
        "prerequisite_move": "validate_final_halt_readout_consistency.v0",
        "already_reason": "no-legacy ambiguous-fields validation already recorded",
        "applies_reason": "final halt/readout consistency is validated; validate no legacy or ambiguous fields",
    },
    "validate_registry_exhaustion_witness.v0": {
        "required_status": "no_legacy_ambiguous_fields_validated",
        "prerequisite_move": "validate_no_legacy_ambiguous_fields.v0",
        "already_reason": "registry exhaustion witness validation already recorded",
        "applies_reason": "no legacy or ambiguous fields are validated; validate frozen registry exhaustion witness",
    },
    "validate_stop_needs_new_move_halt_vocabulary_binding.v0": {
        "required_status": "registry_exhaustion_witness_validated",
        "prerequisite_move": "validate_registry_exhaustion_witness.v0",
        "prerequisite_position": ("validate_registry_exhaustion_witness.v0", [7]),
        "prerequisite_position_reason": "registry exhaustion witness validation is not recorded exactly once at the expected position",
        "already_reason": "STOP_NEEDS_NEW_MOVE halt vocabulary binding already recorded",
        "applies_reason": "registry exhaustion is validated; bind STOP_NEEDS_NEW_MOVE as halt vocabulary",
    },
}


def move_validation_applies(
    move_id: str, state: dict[str, Any], regime: dict[str, Any]
) -> tuple[bool, str]:
    spec = VALIDATION_APPLIES_SPECS_V0[move_id]
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    required_status = spec["required_status"]
    if state.get("status") != required_status:
        return False, f"state is not {required_status}"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    checkpoint = spec.get("prerequisite_checkpoint")
    if isinstance(checkpoint, str) and not history_has_checkpoint(state, checkpoint):
        return False, f"{checkpoint} checkpoint is not recorded"
    prerequisite = spec.get("prerequisite_move")
    if isinstance(prerequisite, str) and not history_has_move(state, prerequisite):
        return False, spec.get("prerequisite_reason", prerequisite + " is not recorded")
    position = spec.get("prerequisite_position")
    if position is not None:
        position_move, expected = position
        history = state.get("history") if isinstance(state.get("history"), list) else []
        if history_move_indices(history, position_move) != expected:
            return False, spec["prerequisite_position_reason"]
    if history_has_move(state, move_id):
        return False, spec["already_reason"]
    for field in spec.get("required_regime_fields", []):
        if field not in regime:
            return False, f"regime.{field} is missing"
    return True, spec["applies_reason"]


def inspect_applicable_moves(state: dict[str, Any], regime: dict[str, Any]) -> list[dict[str, str]]:
    custom_checks = {
        "reject_invalid_state.v0": move_reject_invalid_state_applies,
        "type_active_object.v0": move_type_active_object_applies,
        "checkpoint_typed_state.v0": move_checkpoint_typed_state_applies,
    }

    applicable: list[dict[str, str]] = []
    for move_id in regime["move_registry"]:
        if move_id in VALIDATION_APPLIES_SPECS_V0:
            applies, reason = move_validation_applies(move_id, state, regime)
        else:
            applies, reason = custom_checks[move_id](state, regime)
        if applies:
            applicable.append({"move_id": move_id, "reason": reason})
    return applicable


def choose_move(applicable_moves: list[dict[str, str]], regime: dict[str, Any]) -> dict[str, str] | None:
    if not applicable_moves:
        return None

    by_id = {row["move_id"]: row for row in applicable_moves}
    for move_id in regime["move_registry"]:
        if move_id in by_id:
            return by_id[move_id]

    return None


def _active_object_id_for_candidate(state: dict[str, Any] | None) -> str | None:
    if not isinstance(state, dict):
        return None
    active_object = state.get("active_object")
    if isinstance(active_object, dict):
        object_id = active_object.get("object_id")
        if isinstance(object_id, str) and object_id:
            return object_id
    state_id = state.get("state_id")
    return state_id if isinstance(state_id, str) and state_id else None


def _candidate_next_handling(block_code: str | None, *, selected: bool = False) -> str:
    if block_code:
        return CANDIDATE_BLOCK_NEXT_HANDLING_V0.get(
            block_code,
            "stop and classify this continuation boundary before proceeding",
        )
    if selected:
        return "eligible for deterministic choose_move under the frozen move registry"
    return "eligible registered move, but lower priority than the selected candidate"


def _candidate_record(
    *,
    candidate_id: str,
    candidate_kind: str,
    active_object: str | None,
    allowed: bool,
    selected: bool,
    source: str,
    reason: str,
    block_code: str | None = None,
    layer: str = "OUTER",
    mode: str = "INSPECT",
    next_handling: str | None = None,
    must_not_impersonate: list[str] | None = None,
) -> dict[str, Any]:
    if candidate_kind not in CANDIDATE_KINDS_V0:
        candidate_kind = "NO_CANDIDATE"
    if block_code is not None and block_code not in CANDIDATE_BLOCK_CODES_V0:
        # Keep the surface typed without admitting new halt vocabulary.
        block_code = "NO_APPLICABLE_MOVE"
    return {
        "candidate_id": candidate_id,
        "candidate_kind": candidate_kind,
        "layer": layer,
        "mode": mode,
        "active_object": active_object,
        "allowed": bool(allowed),
        "selected": bool(selected),
        "source": source,
        "reason": str(reason),
        "block_code": block_code,
        "next_handling": next_handling if next_handling is not None else _candidate_next_handling(block_code, selected=selected),
        "must_not_impersonate": list(must_not_impersonate or CANDIDATE_SEARCH_MUST_NOT_IMPERSONATE_V0),
    }


def _no_move_candidate_kind(halt_code: str) -> str:
    if halt_code == "STOP_NEEDS_NEW_MOVE":
        return "MISSING_MOVE_PRESSURE"
    if halt_code == "INVALID_STATE":
        return "UNDERTYPED_OBJECT"
    if halt_code == "INVALID_REGIME":
        return "AUTHORITY_BLOCKED"
    return "NO_CANDIDATE"


def inspect_candidate_space(state: dict[str, Any], regime: dict[str, Any]) -> list[dict[str, Any]]:
    """Return read-only candidate records for the current continuation surface.

    Capability Layer 2: enumerate local candidates and reject invalid candidates
    inside the already-declared move registry.

    Capability Layer 4 foothold: surface typed continuation-topology stop shapes
    (missing move, under-typed object, authority block, layer collapse, extraction
    need, frontier pressure) as readout vocabulary only.

    This function MUST NOT mutate state or regime, write artifacts, patch the
    registry, evolve taxonomy, import monolith behavior, or interpret frontier
    math.
    """
    state_copy = copy.deepcopy(state)
    regime_copy = copy.deepcopy(regime)
    active_object = _active_object_id_for_candidate(state_copy)

    if not isinstance(regime_copy, dict):
        return [
            _candidate_record(
                candidate_id="candidate.000.invalid_regime",
                candidate_kind="AUTHORITY_BLOCKED",
                active_object=active_object,
                allowed=False,
                selected=False,
                source=CANDIDATE_SEARCH_SCHEMA_V0,
                reason="regime is not a JSON object",
                block_code="INVALID_REGIME",
            )
        ]

    regime_errors = validate_regime(regime_copy)
    if regime_errors:
        return [
            _candidate_record(
                candidate_id="candidate.000.invalid_regime",
                candidate_kind="AUTHORITY_BLOCKED",
                active_object=active_object,
                allowed=False,
                selected=False,
                source="validate_regime",
                reason="; ".join(regime_errors),
                block_code="INVALID_REGIME",
            )
        ]

    if not isinstance(state_copy, dict):
        return [
            _candidate_record(
                candidate_id="candidate.000.invalid_state",
                candidate_kind="UNDERTYPED_OBJECT",
                active_object=active_object,
                allowed=False,
                selected=False,
                source=CANDIDATE_SEARCH_SCHEMA_V0,
                reason="state is not a JSON object",
                block_code="INVALID_STATE",
            )
        ]

    if isinstance(state_copy.get("regime_id"), str) and state_copy.get("regime_id") != regime_copy.get("regime_id"):
        return [
            _candidate_record(
                candidate_id="candidate.000.regime_mismatch",
                candidate_kind="AUTHORITY_BLOCKED",
                active_object=active_object,
                allowed=False,
                selected=False,
                source=CANDIDATE_SEARCH_SCHEMA_V0,
                reason=f"state.regime_id={state_copy.get('regime_id')} differs from regime.regime_id={regime_copy.get('regime_id')}",
                block_code="INVALID_REGIME",
            )
        ]

    applicable = inspect_applicable_moves(state_copy, regime_copy)
    selected = choose_move(applicable, regime_copy)
    selected_move_id = selected.get("move_id") if isinstance(selected, dict) else None

    candidates: list[dict[str, Any]] = []
    for index, row in enumerate(applicable):
        move_id = str(row.get("move_id") or f"move_{index}")
        is_selected = bool(move_id == selected_move_id and selected_move_id is not None)
        candidates.append(
            _candidate_record(
                candidate_id=f"candidate.{index:03d}.{move_id}",
                candidate_kind="REGISTERED_MOVE",
                active_object=active_object,
                allowed=True,
                selected=is_selected,
                source="inspect_applicable_moves",
                reason=str(row.get("reason") or "registered move applies"),
                block_code=None,
                layer="OUTER",
                mode="MOVE_INSPECTION",
            )
        )

    if candidates:
        return candidates

    halt_code, reason = classify_no_applicable_move(state_copy, regime_copy)
    block_code = halt_code if halt_code in CANDIDATE_BLOCK_CODES_V0 else "NO_APPLICABLE_MOVE"
    return [
        _candidate_record(
            candidate_id=f"candidate.000.{str(block_code).lower()}",
            candidate_kind=_no_move_candidate_kind(halt_code),
            active_object=active_object,
            allowed=False,
            selected=False,
            source="classify_no_applicable_move",
            reason=reason,
            block_code=block_code,
            layer="OUTER",
            mode="HALT_READOUT",
        )
    ]


def candidate_search_readout(state: dict[str, Any], regime: dict[str, Any]) -> dict[str, Any]:
    """Projection-only readout for candidate_search_v0."""
    before_state_sig8 = sig8(state) if isinstance(state, dict) else None
    before_regime_sig8 = sig8(regime) if isinstance(regime, dict) else None
    candidates = inspect_candidate_space(state, regime) if isinstance(state, dict) and isinstance(regime, dict) else []
    selected_candidates = [row for row in candidates if row.get("selected") is True]
    allowed_candidates = [row for row in candidates if row.get("allowed") is True]
    blocked_candidates = [row for row in candidates if row.get("allowed") is False]
    return {
        "schema": CANDIDATE_SEARCH_SCHEMA_V0,
        "role": "read_only_projection",
        "before_state_sig8": before_state_sig8,
        "before_regime_sig8": before_regime_sig8,
        "candidate_count": len(candidates),
        "allowed_count": len(allowed_candidates),
        "blocked_count": len(blocked_candidates),
        "selected_candidate_id": selected_candidates[0].get("candidate_id") if selected_candidates else None,
        "selected_move": (selected_candidates[0].get("candidate_id", "").split(".", 3)[-1] if selected_candidates else None),
        "candidates": candidates,
        "readout_sig8": sig8({
            "schema": CANDIDATE_SEARCH_SCHEMA_V0,
            "before_state_sig8": before_state_sig8,
            "before_regime_sig8": before_regime_sig8,
            "candidates": candidates,
        }),
    }


def _candidate_readout_for_envelope(state: dict[str, Any], regime: dict[str, Any]) -> dict[str, Any]:
    """Thin wrapper so capability envelope always uses the Layer-2 readout."""
    return candidate_search_readout(state, regime)


def _top_candidate_from_readout(candidate_readout: dict[str, Any]) -> dict[str, Any] | None:
    candidates = candidate_readout.get("candidates") if isinstance(candidate_readout, dict) else None
    if not isinstance(candidates, list) or not candidates:
        return None
    selected = [row for row in candidates if isinstance(row, dict) and row.get("selected") is True]
    if selected:
        return selected[0]
    blocked = [row for row in candidates if isinstance(row, dict) and row.get("allowed") is False]
    if blocked:
        return blocked[0]
    return candidates[0] if isinstance(candidates[0], dict) else None


def typed_continuation_topology_v0(
    state: dict[str, Any],
    regime: dict[str, Any],
    candidate_readout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Layer 4: classify the current continuation geometry.

    This does not admit a move. It gives the halt/candidate surface a typed
    topology so the next prompt or Codex task knows which kind of boundary it
    is seeing.
    """
    candidate_readout = candidate_readout or candidate_search_readout(state, regime)
    top = _top_candidate_from_readout(candidate_readout)
    block_code = top.get("block_code") if isinstance(top, dict) else None
    candidate_kind = top.get("candidate_kind") if isinstance(top, dict) else None
    allowed = top.get("allowed") if isinstance(top, dict) else None

    topology_code = "NO_CANDIDATE"
    missing_surface = None
    wrong_layer_or_frame = False
    stop_interpretation = "no candidate surface available"

    if allowed is True and candidate_kind == "REGISTERED_MOVE":
        topology_code = "EXECUTABLE_MOVE_READY"
        stop_interpretation = "a registered move is applicable under the frozen move registry"
    elif block_code == "STOP_NEEDS_NEW_MOVE" or candidate_kind == "MISSING_MOVE_PRESSURE":
        topology_code = "MISSING_MOVE"
        missing_surface = "move_record"
        stop_interpretation = "continuation requires a lawful move not currently present in the frozen move registry"
    elif block_code == "STOP_NEEDS_EXTRACTION" or candidate_kind == "NEEDS_EXTRACTION":
        topology_code = "NEEDS_EXTRACTION"
        missing_surface = "extraction_record"
        stop_interpretation = "continuation depends on behavior not yet lawfully extracted"
    elif block_code == "STOP_FRONTIER" or candidate_kind == "FRONTIER_BURDEN":
        topology_code = "FRONTIER_BLOCK"
        missing_surface = "frontier_handling"
        stop_interpretation = "continuation would require unpromoted frontier material"
    elif block_code == "STOP_LAYER_COLLAPSE" or candidate_kind == "LAYER_COLLAPSE":
        topology_code = "LAYER_COLLAPSE"
        wrong_layer_or_frame = True
        missing_surface = "layer_split"
        stop_interpretation = "continuation is mixing theorem, interface, outer, shell, receipt, or frontier roles"
    elif block_code in {"INVALID_REGIME", "STOP_AUTHORITY_VIOLATION"} or candidate_kind == "AUTHORITY_BLOCKED":
        topology_code = "AUTHORITY_BLOCK"
        wrong_layer_or_frame = True
        missing_surface = "declared_source_surface"
        stop_interpretation = "continuation would depend on non-authoritative or invalid source material"
    elif block_code in {"INVALID_STATE", "STOP_UNDERTYPED"} or candidate_kind == "UNDERTYPED_OBJECT":
        topology_code = "UNDER_TYPED_OBJECT"
        missing_surface = "typed_interpretation_record"
        stop_interpretation = "continuation is blocked by an under-typed object or invalid state shape"
    elif block_code == "NO_APPLICABLE_MOVE":
        topology_code = "NO_CANDIDATE"
        stop_interpretation = "no applicable move and no sharper stop topology was available"

    if topology_code not in TOPOLOGY_CODES_V0:
        topology_code = "NO_CANDIDATE"

    readout = {
        "schema": CONTINUATION_TOPOLOGY_SCHEMA_V0,
        "role": "read_only_projection",
        "before_state_sig8": sig8(state) if isinstance(state, dict) else None,
        "before_regime_sig8": sig8(regime) if isinstance(regime, dict) else None,
        "topology_code": topology_code,
        "candidate_kind": candidate_kind,
        "block_code": block_code,
        "missing_surface": missing_surface,
        "wrong_layer_or_frame": bool(wrong_layer_or_frame),
        "stop_interpretation": stop_interpretation,
        "next_handling": (top or {}).get("next_handling") if isinstance(top, dict) else "stop and classify before continuing",
        "must_not_impersonate": list((top or {}).get("must_not_impersonate") or CANDIDATE_SEARCH_MUST_NOT_IMPERSONATE_V0) if isinstance(top, dict) else list(CANDIDATE_SEARCH_MUST_NOT_IMPERSONATE_V0),
    }
    readout["readout_sig8"] = sig8({k: v for k, v in readout.items() if k != "readout_sig8"})
    return readout


def local_continuation_heuristics_v0(
    state: dict[str, Any],
    regime: dict[str, Any],
    candidate_readout: dict[str, Any] | None = None,
    topology_readout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Layer 3: non-authoritative local preference hints.

    Heuristics suggest; they do not admit.  This function intentionally returns
    descriptive hints only and never mutates state, regime, registry, taxonomy,
    or receipts.
    """
    candidate_readout = candidate_readout or candidate_search_readout(state, regime)
    topology_readout = topology_readout or typed_continuation_topology_v0(state, regime, candidate_readout)
    candidates = candidate_readout.get("candidates") if isinstance(candidate_readout, dict) else []
    history = state.get("history") if isinstance(state, dict) and isinstance(state.get("history"), list) else []
    moves_seen = [row.get("move_id") for row in history if isinstance(row, dict) and isinstance(row.get("move_id"), str)]
    topology_code = topology_readout.get("topology_code") if isinstance(topology_readout, dict) else None

    heuristic_notes: list[dict[str, Any]] = []
    ranking_hints: list[dict[str, Any]] = []

    if candidates:
        registered = [row for row in candidates if isinstance(row, dict) and row.get("candidate_kind") == "REGISTERED_MOVE"]
        if registered:
            ranking_hints.append({
                "hint_id": "heuristic.000.follow_registry_priority",
                "pattern": "registered_moves_available",
                "suggestion": "prefer deterministic choose_move order from regime.move_registry",
                "authority": HEURISTIC_AUTHORITY_V0,
            })

    if topology_code == "MISSING_MOVE":
        heuristic_notes.append({
            "hint_id": "heuristic.010.registry_exhaustion_to_missing_move",
            "pattern": "validated_registry_exhaustion_then_stop_needs_new_move",
            "evidence": {
                "has_registry_exhaustion_witness": "validate_registry_exhaustion_witness.v0" in moves_seen,
                "has_stop_needs_new_move_binding": "validate_stop_needs_new_move_halt_vocabulary_binding.v0" in moves_seen,
            },
            "suggestion": "draft the smallest missing move record as proposed-only; do not admit it automatically",
            "authority": HEURISTIC_AUTHORITY_V0,
        })
        ranking_hints.append({
            "hint_id": "heuristic.011.prefer_move_record_over_taxonomy",
            "pattern": "missing_move_pressure",
            "suggestion": "prefer MOVE_RECORD_PROPOSAL before taxonomy upgrade unless topology explicitly reports missing vocabulary",
            "authority": HEURISTIC_AUTHORITY_V0,
        })

    if topology_code in {"UNDER_TYPED_OBJECT", "LAYER_COLLAPSE", "AUTHORITY_BLOCK"}:
        heuristic_notes.append({
            "hint_id": "heuristic.020.stop_before_build",
            "pattern": str(topology_code).lower(),
            "suggestion": "repair typing/source/layer boundary before any build movement",
            "authority": HEURISTIC_AUTHORITY_V0,
        })

    readout = {
        "schema": LOCAL_HEURISTICS_SCHEMA_V0,
        "role": "read_only_projection",
        "authority": HEURISTIC_AUTHORITY_V0,
        "heuristics_are_authority": False,
        "heuristic_count": len(heuristic_notes) + len(ranking_hints),
        "heuristic_notes": heuristic_notes,
        "ranking_hints": ranking_hints,
        "must_not_impersonate": [
            "admission_gate",
            "move_registry_delta",
            "taxonomy_upgrade",
            "proof_progress",
            "architecture_decision",
        ],
    }
    readout["readout_sig8"] = sig8({k: v for k, v in readout.items() if k != "readout_sig8"})
    return readout


def _proposal_record_v0(
    *,
    proposal_id: str,
    proposal_kind: str,
    trigger_topology: str | None,
    trigger_block_code: str | None,
    target: str,
    smallest_honest_reading: str,
    proposed_delta: dict[str, Any] | None = None,
    allowed_next_handling: list[str] | None = None,
    falsifier_targets: list[str] | None = None,
) -> dict[str, Any]:
    if proposal_kind not in PROPOSAL_KINDS_V0:
        proposal_kind = "NO_PROPOSAL"
    return {
        "proposal_id": proposal_id,
        "proposal_kind": proposal_kind,
        "proposal_status": PROPOSAL_STATUS_PROPOSED_ONLY_V0,
        "trigger_topology": trigger_topology,
        "trigger_block_code": trigger_block_code,
        "target": target,
        "smallest_honest_reading": smallest_honest_reading,
        "proposed_delta": proposed_delta or {},
        "allowed_next_handling": list(allowed_next_handling or []),
        "admission_required": True,
        "executable_now": False,
        "in_move_registry": False,
        "mutates_state_now": False,
        "admission_gates": list(PROPOSED_EXTENSION_ADMISSION_GATES_V0),
        "falsifier_targets": list(falsifier_targets or []),
        "must_not_impersonate": list(PROPOSED_EXTENSION_MUST_NOT_IMPERSONATE_V0),
    }


def controlled_local_self_extension_v0(
    state: dict[str, Any],
    regime: dict[str, Any],
    candidate_readout: dict[str, Any] | None = None,
    topology_readout: dict[str, Any] | None = None,
    heuristic_readout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Layer 5: proposed-only extension records.

    This is the minimal self-extension *surface*, not self-extension authority.
    It can emit proposal records, but those records are inert until an external
    patch/admission gate explicitly changes the registry or taxonomy.
    """
    candidate_readout = candidate_readout or candidate_search_readout(state, regime)
    topology_readout = topology_readout or typed_continuation_topology_v0(state, regime, candidate_readout)
    heuristic_readout = heuristic_readout or local_continuation_heuristics_v0(state, regime, candidate_readout, topology_readout)
    topology_code = topology_readout.get("topology_code") if isinstance(topology_readout, dict) else None
    block_code = topology_readout.get("block_code") if isinstance(topology_readout, dict) else None

    proposals: list[dict[str, Any]] = []
    if topology_code == "MISSING_MOVE":
        proposals.append(_proposal_record_v0(
            proposal_id="proposal.000.draft_smallest_missing_move_record.v0",
            proposal_kind="MOVE_RECORD_PROPOSAL",
            trigger_topology=topology_code,
            trigger_block_code=block_code,
            target="frozen_move_registry",
            smallest_honest_reading="a proposed-only missing move record forced by STOP_NEEDS_NEW_MOVE pressure",
            proposed_delta={
                "record_shape_only": True,
                "move_id": "<draft_smallest_missing_move_id>",
                "required_fields": [
                    "move_id",
                    "applies_when",
                    "action",
                    "emitted_readout",
                    "may_halt",
                    "state_delta",
                    "falsifier_sweep",
                ],
                "admission_effect": "none_until_external_patch",
                "requested_draft_family": "post_registry_exhaustion_validator.v0",
                "draft_scope": "ONE_MOVE_ONLY",
                "draft_target": "frozen_move_registry",
            },
            allowed_next_handling=[
                "human/Codex drafts the smallest move record outside this inspector",
                "run verifier and falsifier sweep",
                "only then patch move registry explicitly if admitted",
            ],
            falsifier_targets=[
                "proposal_inserted_without_registry_patch",
                "proposal_marked_executable_now",
                "proposal_missing_must_not_impersonate",
                "proposal_attempts_taxonomy_or_architecture_widening",
            ],
        ))
    elif topology_code == "MISSING_VOCABULARY":
        proposals.append(_proposal_record_v0(
            proposal_id="proposal.000.taxonomy_upgrade_record.v0",
            proposal_kind="TAXONOMY_UPGRADE_PROPOSAL",
            trigger_topology=topology_code,
            trigger_block_code=block_code,
            target="taxonomy_vocabulary",
            smallest_honest_reading="a proposed-only smallest vocabulary repair under explicit halt pressure",
            proposed_delta={"record_shape_only": True, "outcome": "WITHHOLD_OR_SMALLEST_REPAIR"},
            allowed_next_handling=["test existing vocabulary first", "prefer WITHHOLD/WEAKEN/SPLIT before ADD"],
            falsifier_targets=["upgrade_without_trigger_halt", "upgrade_widens_authority", "upgrade_promotes_theorem_status"],
        ))
    elif topology_code == "NEEDS_EXTRACTION":
        proposals.append(_proposal_record_v0(
            proposal_id="proposal.000.bounded_extraction_task.v0",
            proposal_kind="EXTRACTION_TASK_PROPOSAL",
            trigger_topology=topology_code,
            trigger_block_code=block_code,
            target="code_extraction_register",
            smallest_honest_reading="a proposed-only bounded extraction task for behavior not yet lawfully imported",
            proposed_delta={"record_shape_only": True, "requires_lane_classification": True},
            allowed_next_handling=["name routine", "classify lane", "list dependencies", "state non-guarantees"],
            falsifier_targets=["raw_code_imported_as_authority", "frontier_behavior_promoted", "dependencies_unbounded"],
        ))
    elif topology_code in {"UNDER_TYPED_OBJECT", "LAYER_COLLAPSE"}:
        proposals.append(_proposal_record_v0(
            proposal_id="proposal.000.fallback_retype_record.v0",
            proposal_kind="FALLBACK_RETYPE_PROPOSAL",
            trigger_topology=topology_code,
            trigger_block_code=block_code,
            target="typed_interpretation_record",
            smallest_honest_reading="a proposed-only local retyping/fallback record for the blocked continuation surface",
            proposed_delta={"record_shape_only": True, "prefer": ["WITHHOLD", "SPLIT", "FACTOR"]},
            allowed_next_handling=["step back exactly one layer", "keep same fixed frame", "type the missing object explicitly"],
            falsifier_targets=["fallback_changes_truth_status", "fallback_reopens_route_broadly", "fallback_skips_layer_split"],
        ))

    readout = {
        "schema": PROPOSED_EXTENSION_SCHEMA_V0,
        "role": "read_only_projection",
        "authority": "PROPOSED_ONLY_NON_EXECUTABLE",
        "proposal_count": len(proposals),
        "proposal_records": proposals,
        "admission_required": bool(proposals),
        "any_executable_now": False,
        "any_registry_delta_now": False,
        "any_taxonomy_delta_now": False,
        "must_not_impersonate": list(PROPOSED_EXTENSION_MUST_NOT_IMPERSONATE_V0),
    }
    readout["readout_sig8"] = sig8({k: v for k, v in readout.items() if k != "readout_sig8"})
    return readout




def _proposal_admission_check_record_v0(proposal: dict[str, Any], *, index: int = 0) -> dict[str, Any]:
    """Validate one proposed-only Layer-5 record for external admission review.

    This function is a readout, not an admission gate.  A PASS verdict means the
    proposal is well shaped enough to hand to a human/Codex patch cycle.  It
    still remains PROPOSED_ONLY and non-executable.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(proposal, dict):
        return {
            "proposal_id": f"proposal_index_{index}",
            "proposal_kind": None,
            "verdict": "FAIL",
            "errors": ["proposal_not_object"],
            "warnings": [],
            "checked_claims": [],
        }

    proposal_id = str(proposal.get("proposal_id") or f"proposal_index_{index}")
    proposal_kind = proposal.get("proposal_kind")

    missing_fields = [k for k in PROPOSAL_RECORD_REQUIRED_FIELDS_V0 if k not in proposal]
    for k in missing_fields:
        errors.append(f"missing_required_field={k}")

    if proposal.get("proposal_status") != PROPOSAL_STATUS_PROPOSED_ONLY_V0:
        errors.append("proposal_status_not_PROPOSED_ONLY")
    if proposal_kind not in PROPOSAL_KINDS_V0:
        errors.append(f"unknown_proposal_kind={proposal_kind}")
    if proposal.get("admission_required") is not True:
        errors.append("admission_required_not_true")
    if proposal.get("executable_now") is not False:
        errors.append("proposal_executable_now_not_false")
    if proposal.get("in_move_registry") is not False:
        errors.append("proposal_in_move_registry_not_false")
    if proposal.get("mutates_state_now") is not False:
        errors.append("proposal_mutates_state_now_not_false")

    proposed_delta = proposal.get("proposed_delta") if isinstance(proposal.get("proposed_delta"), dict) else {}
    if not isinstance(proposal.get("proposed_delta"), dict):
        errors.append("proposed_delta_not_object")
    if proposed_delta.get("record_shape_only") is not True:
        errors.append("proposed_delta_record_shape_only_not_true")

    admission_gates = proposal.get("admission_gates") if isinstance(proposal.get("admission_gates"), list) else []
    if not isinstance(proposal.get("admission_gates"), list):
        errors.append("admission_gates_not_list")
    missing_gates = [g for g in PROPOSED_EXTENSION_ADMISSION_GATES_V0 if g not in admission_gates]
    for g in missing_gates:
        errors.append(f"missing_admission_gate={g}")

    falsifier_targets = proposal.get("falsifier_targets") if isinstance(proposal.get("falsifier_targets"), list) else []
    if not isinstance(proposal.get("falsifier_targets"), list):
        errors.append("falsifier_targets_not_list")
    must_not = proposal.get("must_not_impersonate") if isinstance(proposal.get("must_not_impersonate"), list) else []
    if not isinstance(proposal.get("must_not_impersonate"), list):
        errors.append("must_not_impersonate_not_list")
    missing_impersonations = [x for x in PROPOSED_EXTENSION_MUST_NOT_IMPERSONATE_V0 if x not in must_not]
    for x in missing_impersonations:
        errors.append(f"missing_must_not_impersonate={x}")

    allowed_next = proposal.get("allowed_next_handling") if isinstance(proposal.get("allowed_next_handling"), list) else []
    if not isinstance(proposal.get("allowed_next_handling"), list):
        errors.append("allowed_next_handling_not_list")
    if not allowed_next:
        errors.append("allowed_next_handling_empty")

    # Move-record proposals get the stricter shape because this is the first
    # admitted propagation path from STOP_NEEDS_NEW_MOVE pressure.
    if proposal_kind == "MOVE_RECORD_PROPOSAL":
        if proposal.get("target") != "frozen_move_registry":
            errors.append("move_record_proposal_target_not_frozen_move_registry")
        if proposal.get("trigger_topology") != "MISSING_MOVE":
            errors.append("move_record_trigger_topology_not_MISSING_MOVE")
        if proposal.get("trigger_block_code") != "STOP_NEEDS_NEW_MOVE":
            errors.append("move_record_trigger_block_not_STOP_NEEDS_NEW_MOVE")

        delta_required = proposed_delta.get("required_fields") if isinstance(proposed_delta.get("required_fields"), list) else []
        if not isinstance(proposed_delta.get("required_fields"), list):
            errors.append("move_delta_required_fields_not_list")
        missing_delta = [k for k in MOVE_RECORD_PROPOSAL_DELTA_REQUIRED_FIELDS_V0 if k not in delta_required]
        for k in missing_delta:
            errors.append(f"missing_move_delta_required_field={k}")
        if proposed_delta.get("admission_effect") != "none_until_external_patch":
            errors.append("move_delta_admission_effect_not_none_until_external_patch")

        missing_falsifiers = [t for t in MOVE_RECORD_PROPOSAL_FALSIFIER_TARGETS_V0 if t not in falsifier_targets]
        for t in missing_falsifiers:
            errors.append(f"missing_move_proposal_falsifier_target={t}")
    else:
        warnings.append("non_move_proposal_checked_by_generic_inertness_only")

    checked_claims = [
        "proposal has required top-level fields",
        "proposal_status remains PROPOSED_ONLY",
        "proposal is not executable now",
        "proposal is not in move_registry",
        "proposal mutates no state now",
        "proposal keeps explicit admission gates",
        "proposal keeps falsifier targets",
        "proposal keeps must_not_impersonate guards",
    ]
    if proposal_kind == "MOVE_RECORD_PROPOSAL":
        checked_claims.extend([
            "move proposal is triggered only by MISSING_MOVE / STOP_NEEDS_NEW_MOVE",
            "move proposal target is frozen_move_registry",
            "move proposal required delta fields are present",
            "move proposal admission effect is none_until_external_patch",
        ])

    return {
        "proposal_id": proposal_id,
        "proposal_kind": proposal_kind,
        "verdict": "PASS" if not errors else "FAIL",
        "errors": errors,
        "warnings": warnings,
        "checked_claims": checked_claims,
        "check_sig8": sig8({
            "proposal_id": proposal_id,
            "proposal_kind": proposal_kind,
            "errors": errors,
            "warnings": warnings,
            "checked_claims": checked_claims,
        }),
    }


def proposed_missing_move_admission_readout_v0(
    state: dict[str, Any],
    regime: dict[str, Any],
    envelope_readout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Projection-only admission-readout for Layer-5 proposal records.

    PASS means the proposed-only record is shaped enough for external review.
    It does not admit a move, does not alter the registry, does not update
    taxonomy, and does not execute anything.
    """
    envelope_readout = envelope_readout or capability_envelope_readout_v0(state, regime)
    layer_5 = envelope_readout.get("layer_5_controlled_local_self_extension") if isinstance(envelope_readout, dict) else {}
    proposals = layer_5.get("proposal_records") if isinstance(layer_5, dict) else []
    if not isinstance(proposals, list):
        proposals = []

    checks = [_proposal_admission_check_record_v0(row, index=i) for i, row in enumerate(proposals)]
    n_pass = sum(1 for c in checks if isinstance(c, dict) and c.get("verdict") == "PASS")
    n_fail = sum(1 for c in checks if isinstance(c, dict) and c.get("verdict") == "FAIL")
    proposal_count = len(proposals)

    verdict = "PASS" if proposal_count > 0 and n_fail == 0 else ("NA" if proposal_count == 0 else "FAIL")
    next_external_action = None
    if verdict == "PASS":
        next_external_action = "external_patch_may_draft_the_explicit_move_record_but_must_not_auto_admit_it"
    elif verdict == "FAIL":
        next_external_action = "repair_the_proposed_only_record_shape_before_any_patch_or_registry_delta"
    else:
        next_external_action = "no_proposal_available_for_admission_readout"

    readout = {
        "schema": PROPOSAL_ADMISSION_READOUT_SCHEMA_V0,
        "role": "read_only_projection",
        "authority": "ADMISSION_READOUT_ONLY",
        "before_state_sig8": sig8(state) if isinstance(state, dict) else None,
        "before_regime_sig8": sig8(regime) if isinstance(regime, dict) else None,
        "envelope_sig8": envelope_readout.get("envelope_sig8") if isinstance(envelope_readout, dict) else None,
        "proposal_count": proposal_count,
        "pass_count": n_pass,
        "fail_count": n_fail,
        "verdict": verdict,
        "checks": checks,
        "next_external_action": next_external_action,
        "does_not_admit": True,
        "mutates_state": False,
        "mutates_regime": False,
        "writes_files": False,
        "admits_moves": False,
        "updates_taxonomy": False,
        "any_executable_now": False,
        "any_registry_delta_now": False,
        "any_taxonomy_delta_now": False,
        "must_not_impersonate": list(PROPOSAL_ADMISSION_MUST_NOT_IMPERSONATE_V0),
    }
    readout["readout_sig8"] = sig8({k: v for k, v in readout.items() if k != "readout_sig8"})
    return readout


def _history_has_outcome_v0(state: dict[str, Any], outcome: str) -> bool:
    try:
        rows = state.get("history") if isinstance(state, dict) else []
        return any(isinstance(row, dict) and row.get("outcome") == outcome for row in (rows or []))
    except Exception:
        return False


def _draftability_check_record_v0(
    proposal: dict[str, Any],
    *,
    topology_readout: dict[str, Any],
    admission_readout: dict[str, Any],
    state: dict[str, Any],
    regime: dict[str, Any],
    index: int = 0,
) -> dict[str, Any]:
    """Check whether a proposed missing move is authorized to be drafted.

    Authorization here means draft permission only. It is not move admission,
    not registry insertion, and not execution authority.
    """
    errors: list[str] = []
    warnings: list[str] = []

    if not isinstance(proposal, dict):
        return {
            "proposal_id": f"proposal_index_{index}",
            "requested_draft_family": None,
            "draftability_verdict": "BLOCKED_REQUIRES_HUMAN_APPROVAL",
            "authorized_to_draft": False,
            "errors": ["proposal_not_object"],
            "warnings": [],
            "checked_claims": [],
        }

    proposal_id = str(proposal.get("proposal_id") or f"proposal_index_{index}")
    proposal_kind = str(proposal.get("proposal_kind") or "")
    proposed_delta = proposal.get("proposed_delta") if isinstance(proposal.get("proposed_delta"), dict) else {}
    requested_family = str(proposed_delta.get("requested_draft_family") or "")
    family = AUTHORIZED_MISSING_MOVE_DRAFT_FAMILIES_V0.get(requested_family)

    if not requested_family:
        errors.append("requested_draft_family_missing")
    if requested_family and family is None:
        errors.append(f"requested_draft_family_not_predeclared={requested_family}")

    if proposal_kind != "MOVE_RECORD_PROPOSAL":
        errors.append(f"proposal_kind_not_MOVE_RECORD_PROPOSAL={proposal_kind}")
    if proposal.get("proposal_status") != PROPOSAL_STATUS_PROPOSED_ONLY_V0:
        errors.append("proposal_status_not_PROPOSED_ONLY")
    if proposal.get("executable_now") is not False:
        errors.append("proposal_executable_now_not_false")
    if proposal.get("in_move_registry") is not False:
        errors.append("proposal_in_move_registry_not_false")
    if proposal.get("mutates_state_now") is not False:
        errors.append("proposal_mutates_state_now_not_false")

    if (admission_readout or {}).get("verdict") != "PASS":
        errors.append("proposal_admission_readout_not_PASS")
    if (admission_readout or {}).get("admits_moves") is not False:
        errors.append("proposal_admission_readout_admits_moves_not_false")
    if (admission_readout or {}).get("updates_taxonomy") is not False:
        errors.append("proposal_admission_readout_updates_taxonomy_not_false")

    topology_code = (topology_readout or {}).get("topology_code")
    block_code = (topology_readout or {}).get("block_code")
    if topology_code != "MISSING_MOVE":
        errors.append(f"topology_not_MISSING_MOVE={topology_code}")
    if block_code != "STOP_NEEDS_NEW_MOVE":
        errors.append(f"block_code_not_STOP_NEEDS_NEW_MOVE={block_code}")

    if not _history_has_outcome_v0(state, "registry_exhaustion_witness_validated"):
        errors.append("registry_exhaustion_witness_not_validated")
    if not _history_has_outcome_v0(state, "stop_needs_new_move_halt_vocabulary_bound"):
        errors.append("stop_needs_new_move_halt_vocabulary_not_bound")

    typed = state.get("typed_record") if isinstance(state.get("typed_record"), dict) else {}
    if "STOP_NEEDS_NEW_MOVE" not in (typed.get("stop_conditions") or []):
        errors.append("typed_record_stop_conditions_missing_STOP_NEEDS_NEW_MOVE")
    if isinstance(regime, dict) and "STOP_NEEDS_NEW_MOVE" not in (regime.get("halt_codes") or []):
        errors.append("regime_halt_codes_missing_STOP_NEEDS_NEW_MOVE")

    if family is not None:
        if proposed_delta.get("draft_scope") != family.get("allowed_scope"):
            errors.append("draft_scope_not_allowed_family_scope")
        if proposed_delta.get("draft_target") != family.get("target"):
            errors.append("draft_target_not_allowed_family_target")
        if proposal.get("target") != family.get("target"):
            errors.append("proposal_target_not_allowed_family_target")
        if family.get("required_trigger_topology") != proposal.get("trigger_topology"):
            errors.append("proposal_trigger_topology_not_allowed_family_trigger")
        if family.get("required_trigger_block_code") != proposal.get("trigger_block_code"):
            errors.append("proposal_trigger_block_code_not_allowed_family_trigger")

        delta_required = proposed_delta.get("required_fields") if isinstance(proposed_delta.get("required_fields"), list) else []
        for field in family.get("required_draft_fields") or []:
            if field not in delta_required:
                errors.append(f"missing_allowed_family_required_draft_field={field}")

    verdict = "AUTHORIZED_TO_DRAFT" if not errors else "BLOCKED_REQUIRES_HUMAN_APPROVAL"
    checked_claims = [
        "requested draft family is predeclared",
        "proposal remains PROPOSED_ONLY",
        "proposal is not executable and not in registry",
        "proposal admission readout passed without admitting moves",
        "topology is MISSING_MOVE and block is STOP_NEEDS_NEW_MOVE",
        "registry exhaustion witness is validated",
        "STOP_NEEDS_NEW_MOVE halt vocabulary is bound",
        "draft scope is one move only",
        "draft target is frozen_move_registry",
        "draft authorization does not admit or execute the move",
    ]

    return {
        "proposal_id": proposal_id,
        "proposal_kind": proposal_kind,
        "requested_draft_family": requested_family or None,
        "draft_family_record": copy.deepcopy(family) if family is not None else None,
        "draftability_verdict": verdict,
        "authorized_to_draft": verdict == "AUTHORIZED_TO_DRAFT",
        "errors": errors,
        "warnings": warnings,
        "checked_claims": checked_claims,
        "must_not_impersonate": list(DRAFTABILITY_MUST_NOT_IMPERSONATE_V0),
        "check_sig8": sig8({
            "proposal_id": proposal_id,
            "proposal_kind": proposal_kind,
            "requested_draft_family": requested_family,
            "draftability_verdict": verdict,
            "errors": errors,
            "warnings": warnings,
            "checked_claims": checked_claims,
        }),
    }


def allowed_missing_move_draft_policy_readout_v0(
    state: dict[str, Any],
    regime: dict[str, Any],
    envelope_readout: dict[str, Any] | None = None,
    proposal_admission_readout: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Projection-only draftability gate for missing-move proposals.

    This may authorize drafting only inside predeclared families.  It never
    admits, registers, executes, or patches a move.  Unknown draft families
    are blocked and require human approval.
    """
    if envelope_readout is None:
        # Manual mini-envelope to avoid recursive capability_envelope calls.
        layer_2 = _candidate_readout_for_envelope(state, regime) if isinstance(state, dict) and isinstance(regime, dict) else {}
        layer_4 = typed_continuation_topology_v0(state, regime, layer_2) if isinstance(state, dict) and isinstance(regime, dict) else {}
        layer_3 = local_continuation_heuristics_v0(state, regime, layer_2, layer_4) if isinstance(state, dict) and isinstance(regime, dict) else {}
        layer_5 = controlled_local_self_extension_v0(state, regime, layer_2, layer_4, layer_3) if isinstance(state, dict) and isinstance(regime, dict) else {}
        envelope_readout = {
            "schema": CAPABILITY_ENVELOPE_SCHEMA_V0,
            "layer_2_bounded_candidate_search": layer_2,
            "layer_3_local_continuation_heuristics": layer_3,
            "layer_4_typed_continuation_topology": layer_4,
            "layer_5_controlled_local_self_extension": layer_5,
        }

    layer_4 = envelope_readout.get("layer_4_typed_continuation_topology") if isinstance(envelope_readout, dict) else {}
    layer_5 = envelope_readout.get("layer_5_controlled_local_self_extension") if isinstance(envelope_readout, dict) else {}
    proposals = layer_5.get("proposal_records") if isinstance(layer_5, dict) else []
    if not isinstance(proposals, list):
        proposals = []

    if proposal_admission_readout is None:
        checks = [_proposal_admission_check_record_v0(row, index=i) for i, row in enumerate(proposals)]
        n_fail = sum(1 for c in checks if isinstance(c, dict) and c.get("verdict") == "FAIL")
        proposal_admission_readout = {
            "schema": PROPOSAL_ADMISSION_READOUT_SCHEMA_V0,
            "verdict": "PASS" if proposals and n_fail == 0 else ("NA" if not proposals else "FAIL"),
            "checks": checks,
            "admits_moves": False,
            "updates_taxonomy": False,
            "any_executable_now": False,
            "any_registry_delta_now": False,
            "any_taxonomy_delta_now": False,
        }

    checks = [
        _draftability_check_record_v0(
            row,
            topology_readout=layer_4 if isinstance(layer_4, dict) else {},
            admission_readout=proposal_admission_readout if isinstance(proposal_admission_readout, dict) else {},
            state=state,
            regime=regime,
            index=i,
        )
        for i, row in enumerate(proposals)
    ]
    authorized = [c for c in checks if isinstance(c, dict) and c.get("draftability_verdict") == "AUTHORIZED_TO_DRAFT"]
    blocked = [c for c in checks if isinstance(c, dict) and c.get("draftability_verdict") == "BLOCKED_REQUIRES_HUMAN_APPROVAL"]

    if not proposals:
        verdict = "NA"
        next_handling = "no missing-move proposal exists; no draft is authorized"
    elif blocked:
        verdict = "BLOCKED_REQUIRES_HUMAN_APPROVAL"
        next_handling = "human review required before any concrete move draft"
    else:
        verdict = "AUTHORIZED_TO_DRAFT"
        next_handling = "Codex/human may draft the concrete move body inside the authorized family only; admission still requires explicit verifier/falsifier and registry patch"

    readout = {
        "schema": MISSING_MOVE_DRAFT_POLICY_SCHEMA_V0,
        "role": "read_only_projection",
        "authority": "DRAFT_AUTHORIZATION_ONLY",
        "before_state_sig8": sig8(state) if isinstance(state, dict) else None,
        "before_regime_sig8": sig8(regime) if isinstance(regime, dict) else None,
        "allowed_families": copy.deepcopy(AUTHORIZED_MISSING_MOVE_DRAFT_FAMILIES_V0),
        "proposal_count": len(proposals),
        "authorized_count": len(authorized),
        "blocked_count": len(blocked),
        "draftability_verdict": verdict,
        "authorized_to_draft": verdict == "AUTHORIZED_TO_DRAFT",
        "checks": checks,
        "next_handling": next_handling,
        "does_not_admit": True,
        "mutates_state": False,
        "mutates_regime": False,
        "writes_files": False,
        "admits_moves": False,
        "updates_taxonomy": False,
        "any_executable_now": False,
        "any_registry_delta_now": False,
        "any_taxonomy_delta_now": False,
        "must_not_impersonate": list(DRAFTABILITY_MUST_NOT_IMPERSONATE_V0),
    }
    readout["readout_sig8"] = sig8({k: v for k, v in readout.items() if k != "readout_sig8"})
    return readout


def capability_envelope_readout_v0(state: dict[str, Any], regime: dict[str, Any]) -> dict[str, Any]:
    """Projection-only envelope exposing minimal Layers 2-5.

    The envelope is deliberately inert. It does not influence choose_move(),
    apply_move(), receipt hashing, fixture loading, or move admission.
    """
    before_state_sig8 = sig8(state) if isinstance(state, dict) else None
    before_regime_sig8 = sig8(regime) if isinstance(regime, dict) else None
    layer_2 = _candidate_readout_for_envelope(state, regime) if isinstance(state, dict) and isinstance(regime, dict) else {}
    layer_4 = typed_continuation_topology_v0(state, regime, layer_2) if isinstance(state, dict) and isinstance(regime, dict) else {}
    layer_3 = local_continuation_heuristics_v0(state, regime, layer_2, layer_4) if isinstance(state, dict) and isinstance(regime, dict) else {}
    layer_5 = controlled_local_self_extension_v0(state, regime, layer_2, layer_4, layer_3) if isinstance(state, dict) and isinstance(regime, dict) else {}
    # Layer-5 admission-readout is built manually here to avoid recursive envelope calls.
    proposal_count = len(layer_5.get("proposal_records") or []) if isinstance(layer_5, dict) and isinstance(layer_5.get("proposal_records"), list) else 0
    proposal_checks = [_proposal_admission_check_record_v0(row, index=i) for i, row in enumerate((layer_5.get("proposal_records") or []) if isinstance(layer_5, dict) else [])]
    proposal_fail_count = sum(1 for c in proposal_checks if isinstance(c, dict) and c.get("verdict") == "FAIL")
    layer_5_admission = {
        "schema": PROPOSAL_ADMISSION_READOUT_SCHEMA_V0,
        "role": "read_only_projection",
        "authority": "ADMISSION_READOUT_ONLY",
        "before_state_sig8": before_state_sig8,
        "before_regime_sig8": before_regime_sig8,
        "proposal_count": proposal_count,
        "pass_count": sum(1 for c in proposal_checks if isinstance(c, dict) and c.get("verdict") == "PASS"),
        "fail_count": proposal_fail_count,
        "verdict": ("PASS" if proposal_count > 0 and proposal_fail_count == 0 else ("NA" if proposal_count == 0 else "FAIL")),
        "checks": proposal_checks,
        "does_not_admit": True,
        "mutates_state": False,
        "mutates_regime": False,
        "writes_files": False,
        "admits_moves": False,
        "updates_taxonomy": False,
        "any_executable_now": False,
        "any_registry_delta_now": False,
        "any_taxonomy_delta_now": False,
        "must_not_impersonate": list(PROPOSAL_ADMISSION_MUST_NOT_IMPERSONATE_V0),
    }
    layer_5_admission["readout_sig8"] = sig8({k: v for k, v in layer_5_admission.items() if k != "readout_sig8"})
    draftability_readout = allowed_missing_move_draft_policy_readout_v0(
        state,
        regime,
        envelope_readout={
            "schema": CAPABILITY_ENVELOPE_SCHEMA_V0,
            "layer_2_bounded_candidate_search": layer_2,
            "layer_3_local_continuation_heuristics": layer_3,
            "layer_4_typed_continuation_topology": layer_4,
            "layer_5_controlled_local_self_extension": layer_5,
        },
        proposal_admission_readout=layer_5_admission,
    )

    readout = {
        "schema": CAPABILITY_ENVELOPE_SCHEMA_V0,
        "role": "read_only_projection",
        "authority": "NON_BINDING_CONTINUATION_SURFACE",
        "before_state_sig8": before_state_sig8,
        "before_regime_sig8": before_regime_sig8,
        "layer_2_bounded_candidate_search": layer_2,
        "layer_3_local_continuation_heuristics": layer_3,
        "layer_4_typed_continuation_topology": layer_4,
        "layer_5_controlled_local_self_extension": layer_5,
        "proposal_admission_readout_v0": layer_5_admission,
        "allowed_missing_move_draft_policy_v0": draftability_readout,
        "guardrails": {
            "mutates_state": False,
            "mutates_regime": False,
            "writes_files": False,
            "admits_moves": False,
            "updates_taxonomy": False,
            "interprets_frontier": False,
            "imports_old_monolith": False,
        },
    }
    readout["envelope_sig8"] = sig8({k: v for k, v in readout.items() if k != "envelope_sig8"})
    return readout


def smoke_capability_envelope_v0() -> dict[str, Any]:
    """Headless smoke helper for the full projection-only capability envelope."""
    ensure_fixture_surface()
    regime, state, load_errors = load_fixtures()
    before_state_sig8 = sig8(state) if isinstance(state, dict) else None
    before_regime_sig8 = sig8(regime) if isinstance(regime, dict) else None
    loaded_envelope = capability_envelope_readout_v0(state, regime) if isinstance(state, dict) and isinstance(regime, dict) else {}
    after_loaded_state_sig8 = sig8(state) if isinstance(state, dict) else None
    after_loaded_regime_sig8 = sig8(regime) if isinstance(regime, dict) else None

    final_state, receipt, receipt_path = run_from_fixtures()
    final_envelope = capability_envelope_readout_v0(final_state, regime) if isinstance(final_state, dict) and isinstance(regime, dict) else {}
    final_layer_4 = final_envelope.get("layer_4_typed_continuation_topology") if isinstance(final_envelope, dict) else {}
    final_layer_5 = final_envelope.get("layer_5_controlled_local_self_extension") if isinstance(final_envelope, dict) else {}
    final_admission = final_envelope.get("proposal_admission_readout_v0") if isinstance(final_envelope, dict) else {}
    final_draftability = final_envelope.get("allowed_missing_move_draft_policy_v0") if isinstance(final_envelope, dict) else {}

    return {
        "schema": "capability_envelope_smoke_v0",
        "load_errors": load_errors,
        "before_state_sig8": before_state_sig8,
        "after_loaded_envelope_state_sig8": after_loaded_state_sig8,
        "state_mutated_by_loaded_envelope": before_state_sig8 != after_loaded_state_sig8,
        "before_regime_sig8": before_regime_sig8,
        "after_loaded_envelope_regime_sig8": after_loaded_regime_sig8,
        "regime_mutated_by_loaded_envelope": before_regime_sig8 != after_loaded_regime_sig8,
        "loaded_envelope_sig8": loaded_envelope.get("envelope_sig8") if isinstance(loaded_envelope, dict) else None,
        "loaded_topology_code": ((loaded_envelope.get("layer_4_typed_continuation_topology") or {}).get("topology_code") if isinstance(loaded_envelope, dict) else None),
        "runner_halt_code": receipt.get("halt_code") if isinstance(receipt, dict) else None,
        "runner_moves_applied": len(receipt.get("moves_applied") or []) if isinstance(receipt, dict) else None,
        "receipt_path": receipt_path.as_posix(),
        "final_state_sig8": sig8(final_state) if isinstance(final_state, dict) else None,
        "final_envelope_sig8": final_envelope.get("envelope_sig8") if isinstance(final_envelope, dict) else None,
        "final_topology_code": final_layer_4.get("topology_code") if isinstance(final_layer_4, dict) else None,
        "final_proposal_count": final_layer_5.get("proposal_count") if isinstance(final_layer_5, dict) else None,
        "final_any_executable_now": final_layer_5.get("any_executable_now") if isinstance(final_layer_5, dict) else None,
        "final_any_registry_delta_now": final_layer_5.get("any_registry_delta_now") if isinstance(final_layer_5, dict) else None,
        "final_proposal_kinds": [row.get("proposal_kind") for row in (final_layer_5.get("proposal_records") or []) if isinstance(row, dict)] if isinstance(final_layer_5, dict) else [],
        "final_admission_verdict": final_admission.get("verdict") if isinstance(final_admission, dict) else None,
        "final_admission_pass_count": final_admission.get("pass_count") if isinstance(final_admission, dict) else None,
        "final_admission_fail_count": final_admission.get("fail_count") if isinstance(final_admission, dict) else None,
        "final_admission_admits_moves": final_admission.get("admits_moves") if isinstance(final_admission, dict) else None,
        "final_draftability_verdict": final_draftability.get("draftability_verdict") if isinstance(final_draftability, dict) else None,
        "final_authorized_to_draft": final_draftability.get("authorized_to_draft") if isinstance(final_draftability, dict) else None,
        "final_draftability_authorized_count": final_draftability.get("authorized_count") if isinstance(final_draftability, dict) else None,
        "final_draftability_blocked_count": final_draftability.get("blocked_count") if isinstance(final_draftability, dict) else None,
        "final_draftability_admits_moves": final_draftability.get("admits_moves") if isinstance(final_draftability, dict) else None,
    }


def smoke_candidate_search_v0() -> dict[str, Any]:
    """Small headless smoke helper for candidate_search_v0.

    It loads the fixture surface, inspects candidate space, then runs the
    unchanged machine.  The only expected write is the existing runner receipt
    when run_from_fixtures() executes.
    """
    ensure_fixture_surface()
    regime, state, load_errors = load_fixtures()
    before_state_sig8 = sig8(state) if isinstance(state, dict) else None
    before_regime_sig8 = sig8(regime) if isinstance(regime, dict) else None
    candidates = inspect_candidate_space(state, regime) if isinstance(state, dict) and isinstance(regime, dict) else []
    after_candidate_state_sig8 = sig8(state) if isinstance(state, dict) else None
    after_candidate_regime_sig8 = sig8(regime) if isinstance(regime, dict) else None
    final_state, receipt, receipt_path = run_from_fixtures()
    return {
        "schema": "candidate_search_smoke_v0",
        "load_errors": load_errors,
        "before_state_sig8": before_state_sig8,
        "after_candidate_state_sig8": after_candidate_state_sig8,
        "state_mutated_by_candidate_search": before_state_sig8 != after_candidate_state_sig8,
        "before_regime_sig8": before_regime_sig8,
        "after_candidate_regime_sig8": after_candidate_regime_sig8,
        "regime_mutated_by_candidate_search": before_regime_sig8 != after_candidate_regime_sig8,
        "candidate_kinds": [row.get("candidate_kind") for row in candidates],
        "selected_candidate_id": next((row.get("candidate_id") for row in candidates if row.get("selected") is True), None),
        "runner_halt_code": receipt.get("halt_code") if isinstance(receipt, dict) else None,
        "runner_moves_applied": receipt.get("moves_applied") if isinstance(receipt, dict) else None,
        "receipt_path": receipt_path.as_posix(),
        "final_state_sig8": sig8(final_state) if isinstance(final_state, dict) else None,
    }


def append_history(state: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    new_state = copy.deepcopy(state)
    history = list(new_state.get("history") or [])
    history.append(row)
    new_state["history"] = history
    return new_state


def apply_reject_invalid_state(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    new_state = append_history(
        state,
        {
            "move_id": "reject_invalid_state.v0",
            "outcome": "halt",
            "checkpoint_code": None,
            "halt_code": "INVALID_STATE",
            "reason": reason,
        },
    )
    new_state["status"] = "halted_invalid"
    return new_state, "INVALID_STATE", None


def build_typed_record(state: dict[str, Any], regime: dict[str, Any]) -> dict[str, Any]:
    active_object = state["active_object"]
    object_kind = active_object.get("object_kind", "UNRESOLVED")

    if object_kind not in regime["allowed_object_kinds"]:
        object_kind = "UNRESOLVED"

    return {
        "object_id": active_object.get("object_id", "active_object"),
        "object_kind": object_kind,
        "smallest_honest_reading": active_object.get(
            "smallest_honest_reading",
            "declared v0 boundary object requiring typed continuity under lawful movement",
        ),
        "authority_class": "FIXTURE_BOUNDARY_INPUT",
        "truth_status": "NON_CLAIM",
        "layer": "OUTER",
        "route_role": "FIRST_BUILD_CUT_BOUNDARY",
        "extractability": "UNRESOLVED",
        "content_scope": "v0 fixture-declared local object only",
        "allowed_consumers": ["streamlit_move_runner_v0"],
        "forbidden_impersonations": [
            "theorem_claim",
            "proof_closure",
            "theorem_success",
            "engine_completion",
            "polished_architecture",
            "old_monolithic_app",
            "dynamic_regime_evolution",
            "autonomous_registry_evolution",
            "taxonomy_upgrade",
            "architecture_redesign",
        ],
        "declared_allowed_moves": [
            "checkpoint_typed_state.v0",
            "validate_typed_record_schema.v0",
            "validate_typed_record_regime_bindings.v0",
            "validate_history_integrity.v0",
            "validate_final_halt_readout_consistency.v0",
            "validate_no_legacy_ambiguous_fields.v0",
            "validate_registry_exhaustion_witness.v0",
            "validate_stop_needs_new_move_halt_vocabulary_binding.v0",
        ],
        "stop_conditions": [
            "INVALID_STATE",
            "REGIME_MISMATCH",
            "NO_APPLICABLE_MOVE",
            "STOP_NEEDS_NEW_MOVE",
            "STEP_LIMIT_EXCEEDED",
        ],
        "promotion_rule": "no promotion in v0; regime_patch_policy is PROPOSED_ONLY and inert",
        "notes": [
            "smallest honest typed record generated by type_active_object.v0",
            "TYPED_STATE_READY is a checkpoint code, not a terminal halt code",
            "receipt is a run witness only",
            "STOP_NEEDS_NEW_MOVE means continuation requires a lawful move not currently present in the frozen move registry",
        ],
    }


def apply_type_active_object(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    new_state = copy.deepcopy(state)
    new_state["typed_record"] = build_typed_record(new_state, regime)
    new_state["status"] = "typed"
    new_state = append_history(
        new_state,
        {
            "move_id": "type_active_object.v0",
            "outcome": "typed_record_created",
            "checkpoint_code": None,
            "halt_code": None,
            "reason": reason,
        },
    )
    return new_state, None, None


def apply_checkpoint_typed_state(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    new_state = append_history(
        state,
        {
            "move_id": "checkpoint_typed_state.v0",
            "outcome": "checkpoint",
            "checkpoint_code": TYPED_READY_CHECKPOINT,
            "halt_code": None,
            "reason": reason,
        },
    )
    new_state["status"] = "typed_ready_checkpointed"
    return new_state, None, TYPED_READY_CHECKPOINT


def _history_row(
    *,
    move_id: str,
    outcome: str,
    reason: str,
    checkpoint_code: str | None = None,
    halt_code: str | None = None,
) -> dict[str, Any]:
    return {
        "move_id": move_id,
        "outcome": outcome,
        "checkpoint_code": checkpoint_code,
        "halt_code": halt_code,
        "reason": reason,
    }


def _apply_invalid_state_halt(
    state: dict[str, Any], move_id: str, errors: list[str]
) -> tuple[dict[str, Any], str | None, str | None]:
    new_state = append_history(
        state,
        _history_row(
            move_id=move_id,
            outcome="halt",
            halt_code="INVALID_STATE",
            reason="; ".join(errors),
        ),
    )
    new_state["status"] = "halted_invalid"
    return new_state, "INVALID_STATE", None


def _apply_success_status(
    state: dict[str, Any],
    *,
    move_id: str,
    outcome: str,
    history_reason: str,
    status: str,
) -> tuple[dict[str, Any], str | None, str | None]:
    new_state = append_history(
        state,
        _history_row(move_id=move_id, outcome=outcome, reason=history_reason),
    )
    new_state["status"] = status
    return new_state, None, None


VALIDATION_APPLY_SPECS_V0 = {
    "validate_typed_record_schema.v0": {
        "errors": typed_record_schema_errors,
        "outcome": "typed_record_schema_validated",
        "history_reason": "typed_record matches required typed-record field list",
        "status": "typed_record_schema_validated",
    },
    "validate_typed_record_regime_bindings.v0": {
        "errors": typed_record_regime_binding_errors,
        "outcome": "typed_record_regime_bound",
        "history_reason": "typed_record object kind, declared moves, and stop conditions are bound to the active regime",
        "status": "typed_record_regime_bound",
    },
    "validate_history_integrity.v0": {
        "errors": history_integrity_errors,
        "outcome": "history_integrity_validated",
        "history_reason": "history rows form a coherent registered move spine",
        "status": "history_integrity_validated",
    },
    "validate_final_halt_readout_consistency.v0": {
        "errors": final_halt_readout_consistency_errors,
        "outcome": "final_halt_readout_consistency_validated",
        "history_reason": "final halt/readout surface is coherent with state, history, trace, and receipt prerequisites",
        "status": "final_halt_readout_consistency_validated",
    },
    "validate_no_legacy_ambiguous_fields.v0": {
        "errors": no_legacy_ambiguous_fields_errors,
        "outcome": "no_legacy_ambiguous_fields_validated",
        "history_reason": "state, typed_record, history, and regime vocabulary contain no legacy or ambiguous fields",
        "status": "no_legacy_ambiguous_fields_validated",
    },
}


def apply_generic_validation_move(
    move_id: str, state: dict[str, Any], regime: dict[str, Any]
) -> tuple[dict[str, Any], str | None, str | None]:
    spec = VALIDATION_APPLY_SPECS_V0[move_id]
    errors = spec["errors"](state, regime)
    if errors:
        return _apply_invalid_state_halt(state, move_id, errors)
    return _apply_success_status(
        state,
        move_id=move_id,
        outcome=spec["outcome"],
        history_reason=spec["history_reason"],
        status=spec["status"],
    )






def apply_validate_registry_exhaustion_witness(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    exhaustion_errors = registry_exhaustion_witness_errors(state, regime)

    pre_applicable = inspect_applicable_moves(state, regime)
    if [row.get("move_id") for row in pre_applicable] != ["validate_registry_exhaustion_witness.v0"]:
        exhaustion_errors.append("pre_state_applicable_move_mismatch")

    if exhaustion_errors:
        new_state = append_history(
            state,
            {
                "move_id": "validate_registry_exhaustion_witness.v0",
                "outcome": "halt",
                "checkpoint_code": None,
                "halt_code": "INVALID_STATE",
                "reason": "; ".join(exhaustion_errors),
            },
        )
        new_state["status"] = "halted_invalid"
        return new_state, "INVALID_STATE", None

    candidate = append_history(
        state,
        {
            "move_id": "validate_registry_exhaustion_witness.v0",
            "outcome": "registry_exhaustion_witness_validated",
            "checkpoint_code": None,
            "halt_code": None,
            "reason": "frozen move registry is exhausted after all current no-drift validators",
        },
    )
    candidate["status"] = "registry_exhaustion_witness_validated"

    post_applicable = inspect_applicable_moves(candidate, regime)
    post_ids = [row.get("move_id") for row in post_applicable]
    if post_ids != ["validate_stop_needs_new_move_halt_vocabulary_binding.v0"]:
        new_state = append_history(
            state,
            {
                "move_id": "validate_registry_exhaustion_witness.v0",
                "outcome": "halt",
                "checkpoint_code": None,
                "halt_code": "INVALID_STATE",
                "reason": "post_state_next_move_mismatch=" + ",".join(str(x) for x in post_ids),
            },
        )
        new_state["status"] = "halted_invalid"
        return new_state, "INVALID_STATE", None

    return candidate, None, None

def apply_validate_stop_needs_new_move_halt_vocabulary_binding(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    binding_errors = stop_needs_new_move_halt_vocabulary_binding_errors(state, regime)
    if binding_errors:
        new_state = append_history(
            state,
            {
                "move_id": "validate_stop_needs_new_move_halt_vocabulary_binding.v0",
                "outcome": "halt",
                "checkpoint_code": None,
                "halt_code": "INVALID_STATE",
                "reason": "; ".join(binding_errors),
            },
        )
        new_state["status"] = "halted_invalid"
        return new_state, "INVALID_STATE", None

    candidate = _dry_stop_needs_new_move_bound_state(state)
    return candidate, None, None


APPLY_CUSTOM_MOVES_V0 = {
    "reject_invalid_state.v0": apply_reject_invalid_state,
    "type_active_object.v0": apply_type_active_object,
    "checkpoint_typed_state.v0": apply_checkpoint_typed_state,
    "validate_registry_exhaustion_witness.v0": apply_validate_registry_exhaustion_witness,
    "validate_stop_needs_new_move_halt_vocabulary_binding.v0": apply_validate_stop_needs_new_move_halt_vocabulary_binding,
}


def apply_move(
    move_id: str, state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    if move_id in VALIDATION_APPLY_SPECS_V0:
        return apply_generic_validation_move(move_id, state, regime)
    if move_id in APPLY_CUSTOM_MOVES_V0:
        return APPLY_CUSTOM_MOVES_V0[move_id](state, regime, reason)
    raise RuntimeError(f"unregistered move reached apply layer: {move_id}")


def classify_no_applicable_move(state: dict[str, Any], regime: dict[str, Any]) -> tuple[str, str]:
    if history_has_move(state, "validate_stop_needs_new_move_halt_vocabulary_binding.v0"):
        return (
            "STOP_NEEDS_NEW_MOVE",
            STOP_NEEDS_NEW_MOVE_BINDING_SPEC_V0["smallest_honest_meaning"],
        )
    if history_has_move(state, "validate_registry_exhaustion_witness.v0"):
        return (
            "STOP_NEEDS_NEW_MOVE",
            "registry exhaustion witness is validated; STOP_NEEDS_NEW_MOVE halt vocabulary binding is the next registered validator",
        )
    if history_has_move(state, "validate_no_legacy_ambiguous_fields.v0"):
        return (
            "STOP_NEEDS_NEW_MOVE",
            "no legacy or ambiguous fields are validated; no registered move applies beyond it under the frozen move registry",
        )
    if history_has_move(state, "validate_final_halt_readout_consistency.v0"):
        return (
            "STOP_NEEDS_NEW_MOVE",
            "final halt/readout consistency is validated; no registered move applies beyond it under the frozen move registry",
        )
    if history_has_move(state, "validate_history_integrity.v0"):
        return (
            "STOP_NEEDS_NEW_MOVE",
            "history integrity is validated; no registered move applies beyond it under the frozen move registry",
        )
    if history_has_move(state, "validate_typed_record_regime_bindings.v0"):
        return (
            "STOP_NEEDS_NEW_MOVE",
            "typed-record regime bindings are validated; no registered move applies beyond it under the frozen move registry",
        )
    if history_has_move(state, "validate_typed_record_schema.v0"):
        return (
            "STOP_NEEDS_NEW_MOVE",
            "typed-record schema is validated; no registered move applies beyond it under the frozen move registry",
        )
    if history_has_checkpoint(state, TYPED_READY_CHECKPOINT):
        return (
            "STOP_NEEDS_NEW_MOVE",
            "typed-ready checkpoint is recorded; no registered move applies beyond it under the frozen move registry",
        )
    return "NO_APPLICABLE_MOVE", "no registered move applies to the current state"


# -----------------------------------------------------------------------------
# Receipts and runner
# -----------------------------------------------------------------------------
def verdict_for_halt(halt_code: str) -> str:
    return "RUN_WITNESS_HALTED"


def checkpoints_from_trace(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    checkpoints: list[dict[str, Any]] = []
    for row in trace:
        checkpoint_code = row.get("checkpoint_code")
        if checkpoint_code is None:
            continue
        checkpoints.append(
            {
                "step": row.get("step"),
                "move_id": row.get("selected_move"),
                "checkpoint_code": checkpoint_code,
                "state_sig8": row.get("after_state_sig8"),
            }
        )
    return checkpoints


def build_receipt(
    *,
    receipt_schema: str,
    regime_id: str | None,
    start_state: dict[str, Any] | None,
    final_state: dict[str, Any] | None,
    moves_applied: list[str],
    trace: list[dict[str, Any]],
    halt_code: str,
) -> dict[str, Any]:
    start_state_sig8 = sig8(start_state) if isinstance(start_state, dict) else None
    final_state_sig8 = sig8(final_state) if isinstance(final_state, dict) else None

    checkpoints = checkpoints_from_trace(trace)
    run_body = {
        "start_state_sig8": start_state_sig8,
        "final_state_sig8": final_state_sig8,
        "moves_applied": moves_applied,
        "checkpoints": checkpoints,
        "halt_code": halt_code,
        "trace": trace,
    }
    run_id = "run_" + sig8(run_body)

    receipt = {
        "receipt_schema": receipt_schema,
        "run_id": run_id,
        "regime_id": regime_id,
        "start_state_sig8": start_state_sig8,
        "final_state_sig8": final_state_sig8,
        "moves_applied": moves_applied,
        "checkpoints": checkpoints,
        "trace": trace,
        "halt_code": halt_code,
        "verdict": verdict_for_halt(halt_code),
        "receipt_sig8": "",
    }
    receipt["receipt_sig8"] = sig8(receipt)
    return receipt


def write_receipt(receipt: dict[str, Any]) -> Path:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{receipt['run_id']}__{receipt['receipt_sig8']}.json"
    path.write_text(canonical_json(receipt), encoding="utf-8")
    return path


def preloop_halt_receipt(
    *,
    receipt_schema: str,
    regime_id: str | None,
    start_state: dict[str, Any] | None,
    halt_code: str,
    reason: str,
) -> tuple[dict[str, Any], Path]:
    state_sig = sig8(start_state) if isinstance(start_state, dict) else None
    trace = [
        {
            "step": 0,
            "before_state_sig8": state_sig,
            "applicable_moves": [],
            "selected_move": None,
            "reason": reason,
            "after_state_sig8": state_sig,
            "checkpoint_code": None,
            "halt_code": halt_code,
        }
    ]
    receipt = build_receipt(
        receipt_schema=receipt_schema,
        regime_id=regime_id,
        start_state=start_state,
        final_state=start_state,
        moves_applied=[],
        trace=trace,
        halt_code=halt_code,
    )
    return receipt, write_receipt(receipt)


def run_machine(
    regime: dict[str, Any], start_state: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], Path]:
    current = copy.deepcopy(start_state)
    trace: list[dict[str, Any]] = []
    moves_applied: list[str] = []
    halt_code: str | None = None

    for step in range(MAX_STEPS):
        before_sig = sig8(current)
        applicable = inspect_applicable_moves(current, regime)
        selected = choose_move(applicable, regime)

        if selected is None:
            halt_code, reason = classify_no_applicable_move(current, regime)
            trace.append(
                {
                    "step": step,
                    "before_state_sig8": before_sig,
                    "applicable_moves": [],
                    "selected_move": None,
                    "reason": reason,
                    "after_state_sig8": before_sig,
                    "checkpoint_code": None,
                    "halt_code": halt_code,
                }
            )
            break

        selected_move = selected["move_id"]
        reason = selected["reason"]

        after, move_halt_code, checkpoint_code = apply_move(selected_move, current, regime, reason)
        after_sig = sig8(after)
        moves_applied.append(selected_move)

        trace.append(
            {
                "step": step,
                "before_state_sig8": before_sig,
                "applicable_moves": applicable,
                "selected_move": selected_move,
                "reason": reason,
                "after_state_sig8": after_sig,
                "checkpoint_code": checkpoint_code,
                "halt_code": move_halt_code,
            }
        )

        current = after

        if move_halt_code is not None:
            halt_code = move_halt_code
            break

    if halt_code is None:
        halt_code = "STEP_LIMIT_EXCEEDED"
        state_sig = sig8(current)
        trace.append(
            {
                "step": MAX_STEPS,
                "before_state_sig8": state_sig,
                "applicable_moves": inspect_applicable_moves(current, regime),
                "selected_move": None,
                "reason": f"MAX_STEPS={MAX_STEPS} exceeded before explicit halt",
                "after_state_sig8": state_sig,
                "checkpoint_code": None,
                "halt_code": halt_code,
            }
        )

    receipt = build_receipt(
        receipt_schema=regime["receipt_schema"],
        regime_id=regime["regime_id"],
        start_state=start_state,
        final_state=current,
        moves_applied=moves_applied,
        trace=trace,
        halt_code=halt_code,
    )
    receipt_path = write_receipt(receipt)
    return current, receipt, receipt_path


def load_fixtures() -> tuple[dict[str, Any] | None, dict[str, Any] | None, list[str]]:
    regime, regime_error = load_json_object(REGIME_PATH)
    state, state_error = load_json_object(STATE_PATH)

    errors: list[str] = []
    if regime_error:
        errors.append(regime_error)
    if state_error:
        errors.append(state_error)

    return regime, state, errors


def run_from_fixtures() -> tuple[dict[str, Any] | None, dict[str, Any], Path]:
    ensure_fixture_surface()
    regime, state, load_errors = load_fixtures()

    if load_errors:
        receipt, path = preloop_halt_receipt(
            receipt_schema=(regime or {}).get("receipt_schema", "receipt_v0"),
            regime_id=(regime or {}).get("regime_id") if isinstance(regime, dict) else None,
            start_state=state if isinstance(state, dict) else None,
            halt_code="FIXTURE_LOAD_ERROR",
            reason="; ".join(load_errors),
        )
        return state, receipt, path

    assert regime is not None
    assert state is not None

    regime_errors = validate_regime(regime)
    if regime_errors:
        receipt, path = preloop_halt_receipt(
            receipt_schema=regime.get("receipt_schema", "receipt_v0"),
            regime_id=regime.get("regime_id"),
            start_state=state,
            halt_code="INVALID_REGIME",
            reason="; ".join(regime_errors),
        )
        return state, receipt, path

    if isinstance(state.get("regime_id"), str) and state.get("regime_id") != regime.get("regime_id"):
        receipt, path = preloop_halt_receipt(
            receipt_schema=regime["receipt_schema"],
            regime_id=regime["regime_id"],
            start_state=state,
            halt_code="REGIME_MISMATCH",
            reason=f"state.regime_id={state.get('regime_id')} differs from regime.regime_id={regime.get('regime_id')}",
        )
        return state, receipt, path

    final_state, receipt, path = run_machine(regime, state)
    return final_state, receipt, path


# -----------------------------------------------------------------------------
# External verification: receipt / trace consistency.
#
# These functions are witness checks over already-emitted runner surfaces. They
# are intentionally not registered moves and must not mutate state, regime, or
# receipt inputs.
# -----------------------------------------------------------------------------
def _as_dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [row for row in value if isinstance(row, dict)]


def _external_check_result(payload: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(payload)
    result["external_check_sig8"] = sig8(result)
    return result


def _terminal_trace_row(receipt: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    trace_raw = receipt.get("trace")
    if not isinstance(trace_raw, list):
        errors.append("trace_missing_or_not_list")
        return None
    if not trace_raw:
        errors.append("trace_empty")
        return None
    if not all(isinstance(row, dict) for row in trace_raw):
        errors.append("trace_contains_non_object_row")
        return None
    return trace_raw[-1]


def _history_halt_codes(state: dict[str, Any]) -> list[Any]:
    history = state.get("history")
    if not isinstance(history, list):
        return []
    return [row.get("halt_code") for row in history if isinstance(row, dict)]


def verify_receipt_trace_consistency_v0(
    *,
    receipt: dict[str, Any],
    final_state: dict[str, Any] | None,
    regime: dict[str, Any],
) -> dict[str, Any]:
    check_id = "verify_receipt_trace_consistency.v0"
    halt_code = "STOP_NEEDS_NEW_MOVE"
    checked_claims = [
        "receipt.moves_applied equals nonterminal selected trace moves",
        "receipt.halt_code equals terminal trace halt_code",
        "terminal trace row has selected_move null",
        "terminal trace row has applicable_moves empty",
        "receipt.final_state_sig8 matches final state",
        "STOP_NEEDS_NEW_MOVE appears only as terminal trace halt",
        "STOP_NEEDS_NEW_MOVE is absent from history halt_code fields",
        "STOP_NEEDS_NEW_MOVE is absent from move_registry",
        "receipt_sig8 recomputes",
    ]
    errors: list[str] = []
    if not isinstance(receipt, dict):
        errors.append("receipt_not_object"); receipt = {}
    if not isinstance(regime, dict):
        errors.append("regime_not_object"); regime = {}

    terminal = _terminal_trace_row(receipt, errors)
    trace_rows = _as_dict_list(receipt.get("trace") if isinstance(receipt.get("trace"), list) else [])
    selected_moves = [row.get("selected_move") for row in trace_rows if row.get("selected_move") is not None]
    if receipt.get("moves_applied") != selected_moves:
        errors.append(f"moves_applied_mismatch: receipt={receipt.get('moves_applied')!r}; trace_selected={selected_moves!r}")

    if terminal is not None:
        terminal_checks = [
            (receipt.get("halt_code") == terminal.get("halt_code"), f"halt_code_mismatch: receipt={receipt.get('halt_code')!r}; terminal={terminal.get('halt_code')!r}"),
            (terminal.get("selected_move") is None, "terminal_selected_move_not_null"),
            (terminal.get("applicable_moves") == [], "terminal_applicable_moves_not_empty"),
            (terminal.get("halt_code") == halt_code, "terminal_halt_code_is_not_STOP_NEEDS_NEW_MOVE"),
        ]
        errors.extend(message for ok, message in terminal_checks if not ok)

    if isinstance(final_state, dict):
        computed_final_sig8 = sig8(final_state)
        if receipt.get("final_state_sig8") != computed_final_sig8:
            errors.append(f"final_state_sig8_mismatch: receipt={receipt.get('final_state_sig8')!r}; computed={computed_final_sig8!r}")
        history_stop_rows = [i for i, value in enumerate(_history_halt_codes(final_state)) if value == halt_code]
        if history_stop_rows:
            errors.append("stop_needs_new_move_embedded_in_history_halt_code: " + ",".join(str(i) for i in history_stop_rows))
    else:
        computed_final_sig8 = None
        errors.append("final_state_not_object")

    stop_trace_rows = [i for i, row in enumerate(trace_rows) if row.get("halt_code") == halt_code]
    expected_terminal_index = len(trace_rows) - 1
    if stop_trace_rows != [expected_terminal_index]:
        errors.append(f"stop_needs_new_move_trace_position_invalid: rows={stop_trace_rows!r}; expected={[expected_terminal_index]!r}")

    move_registry = regime.get("move_registry")
    if not isinstance(move_registry, list):
        errors.append("move_registry_missing_or_not_list")
    elif halt_code in move_registry:
        errors.append("stop_needs_new_move_registered_as_move")

    receipt_sig8 = receipt.get("receipt_sig8")
    if not isinstance(receipt_sig8, str) or not receipt_sig8:
        errors.append("receipt_sig8_missing"); recomputed_receipt_sig8 = None
    else:
        recomputed_receipt_sig8 = sig8(receipt)
        if receipt_sig8 != recomputed_receipt_sig8:
            errors.append(f"receipt_sig8_mismatch: receipt={receipt_sig8!r}; recomputed={recomputed_receipt_sig8!r}")

    return _external_check_result({
        "check_id": check_id,
        "role": "external_verifier",
        "verdict": "PASS" if not errors else "FAIL",
        "errors": errors,
        "input_receipt_sig8": receipt.get("receipt_sig8"),
        "input_final_state_sig8": receipt.get("final_state_sig8"),
        "computed_final_state_sig8": computed_final_sig8,
        "recomputed_receipt_sig8": recomputed_receipt_sig8,
        "checked_claims": checked_claims,
    })


# -----------------------------------------------------------------------------
# External falsifiers: STOP_NEEDS_NEW_MOVE binding guards.
# -----------------------------------------------------------------------------
AUTONOMOUS_CONTINUATION_FIELDS_V0 = {
    "dynamic_regime_update",
    "learned_move",
    "inferred_move",
    "registry_patch",
    "taxonomy_delta",
}


def _autonomous_continuation_field_hits(obj: Any, prefix: str = "root") -> list[str]:
    hits: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}"
            if key in AUTONOMOUS_CONTINUATION_FIELDS_V0:
                hits.append(path)
            hits.extend(_autonomous_continuation_field_hits(value, path))
    elif isinstance(obj, list):
        for index, value in enumerate(obj):
            hits.extend(_autonomous_continuation_field_hits(value, f"{prefix}[{index}]"))
    return hits


def external_stop_needs_new_move_binding_guard_errors_v0(
    *,
    final_state: dict[str, Any] | None,
    regime: dict[str, Any],
    receipt: dict[str, Any],
) -> list[str]:
    """Return external guard failures for the STOP_NEEDS_NEW_MOVE terminal claim."""
    errors: list[str] = []
    halt_code = "STOP_NEEDS_NEW_MOVE"

    if not isinstance(final_state, dict):
        errors.append("final_state_not_object")
        final_state = {}
    if not isinstance(regime, dict):
        errors.append("regime_not_object")
        regime = {}
    if not isinstance(receipt, dict):
        errors.append("receipt_not_object")
        receipt = {}

    halt_codes = regime.get("halt_codes")
    if not isinstance(halt_codes, list) or halt_code not in halt_codes:
        errors.append("stop_needs_new_move_missing_from_regime_halt_codes")

    move_registry = regime.get("move_registry")
    if not isinstance(move_registry, list):
        errors.append("move_registry_missing_or_not_list")
    elif halt_code in move_registry:
        errors.append("stop_needs_new_move_present_in_move_registry")

    typed_record = final_state.get("typed_record")
    if not isinstance(typed_record, dict):
        errors.append("typed_record_missing_or_not_object")
    else:
        stop_conditions = typed_record.get("stop_conditions")
        if not isinstance(stop_conditions, list) or halt_code not in stop_conditions:
            errors.append("stop_needs_new_move_missing_from_typed_record_stop_conditions")

        forbidden_impersonations = typed_record.get("forbidden_impersonations")
        required_guards = {
            "autonomous_registry_evolution",
            "taxonomy_upgrade",
            "architecture_redesign",
        }
        if not isinstance(forbidden_impersonations, list):
            errors.append("typed_record_forbidden_impersonations_missing_or_not_list")
        else:
            missing = sorted(required_guards - set(str(x) for x in forbidden_impersonations))
            if missing:
                errors.append("forbidden_impersonation_guard_missing=" + ",".join(missing))

    history_stop_rows = [
        index
        for index, value in enumerate(_history_halt_codes(final_state))
        if value == halt_code
    ]
    if history_stop_rows:
        errors.append(
            "stop_needs_new_move_present_in_history_halt_code="
            + ",".join(str(index) for index in history_stop_rows)
        )

    terminal = _terminal_trace_row(receipt, errors)
    if terminal is not None:
        if terminal.get("halt_code") != halt_code:
            errors.append("terminal_trace_halt_code_not_stop_needs_new_move")
        if terminal.get("selected_move") is not None:
            errors.append("terminal_trace_selected_move_not_null")
        if terminal.get("applicable_moves") != []:
            errors.append("terminal_trace_applicable_moves_not_empty")

    state_hits = _autonomous_continuation_field_hits(final_state, "state")
    regime_hits = _autonomous_continuation_field_hits(regime, "regime")
    if state_hits or regime_hits:
        errors.append(
            "autonomous_continuation_field_present="
            + ",".join(sorted(state_hits + regime_hits))
        )

    return errors


FALSIFIER_CASE_IDS_V0 = [
    "put_STOP_NEEDS_NEW_MOVE_in_move_registry",
    "put_STOP_NEEDS_NEW_MOVE_in_history_halt_code",
    "remove_STOP_NEEDS_NEW_MOVE_from_typed_record_stop_conditions",
    "remove_STOP_NEEDS_NEW_MOVE_from_regime_halt_codes",
    "add_autonomous_continuation_field",
    "weaken_forbidden_impersonations",
]


def _mutate_falsifier_case_v0(
    case_id: str, state: dict[str, Any], regime: dict[str, Any], receipt: dict[str, Any]
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    halt_code = "STOP_NEEDS_NEW_MOVE"
    if case_id == "put_STOP_NEEDS_NEW_MOVE_in_move_registry":
        regime["move_registry"] = list(regime.get("move_registry") or []) + [halt_code]
    elif case_id == "put_STOP_NEEDS_NEW_MOVE_in_history_halt_code":
        history = state.get("history")
        if isinstance(history, list) and history:
            history[-1]["halt_code"] = halt_code
        else:
            state["history"] = [_history_row(
                move_id="synthetic_mutation_row",
                outcome="mutated",
                halt_code=halt_code,
                reason="mutation inserts terminal halt into history",
            )]
    elif case_id == "remove_STOP_NEEDS_NEW_MOVE_from_typed_record_stop_conditions":
        typed_record = state.get("typed_record")
        if isinstance(typed_record, dict) and isinstance(typed_record.get("stop_conditions"), list):
            typed_record["stop_conditions"] = [v for v in typed_record["stop_conditions"] if v != halt_code]
    elif case_id == "remove_STOP_NEEDS_NEW_MOVE_from_regime_halt_codes":
        if isinstance(regime.get("halt_codes"), list):
            regime["halt_codes"] = [v for v in regime["halt_codes"] if v != halt_code]
    elif case_id == "add_autonomous_continuation_field":
        for field_name in sorted(AUTONOMOUS_CONTINUATION_FIELDS_V0):
            state[field_name] = {"attempt": "illegal autonomous continuation"}
    elif case_id == "weaken_forbidden_impersonations":
        typed_record = state.get("typed_record")
        weakened = {"autonomous_registry_evolution", "taxonomy_upgrade", "architecture_redesign"}
        if isinstance(typed_record, dict) and isinstance(typed_record.get("forbidden_impersonations"), list):
            typed_record["forbidden_impersonations"] = [
                value for value in typed_record["forbidden_impersonations"] if value not in weakened
            ]
    else:
        raise RuntimeError(f"unknown falsifier case: {case_id}")
    return state, regime, receipt


def _run_falsifier_case(
    *,
    case_id: str,
    final_state: dict[str, Any] | None,
    regime: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    mutated_state, mutated_regime, mutated_receipt = _mutate_falsifier_case_v0(
        case_id, copy.deepcopy(final_state), copy.deepcopy(regime), copy.deepcopy(receipt)
    )
    errors = external_stop_needs_new_move_binding_guard_errors_v0(
        final_state=mutated_state, regime=mutated_regime, receipt=mutated_receipt
    )
    observed = "FAIL" if errors else "PASS"
    return {
        "case_id": case_id,
        "expected": "FAIL",
        "observed": observed,
        "passed": observed == "FAIL",
        "errors": errors,
    }


def falsify_stop_needs_new_move_binding_guards_v0(
    *,
    final_state: dict[str, Any] | None,
    regime: dict[str, Any],
    receipt: dict[str, Any],
) -> dict[str, Any]:
    check_id = "falsify_stop_needs_new_move_binding_guards.v0"
    baseline_errors = external_stop_needs_new_move_binding_guard_errors_v0(
        final_state=final_state, regime=regime, receipt=receipt
    )
    if baseline_errors:
        return _external_check_result({
            "check_id": check_id,
            "role": "external_falsifier_sweep",
            "verdict": "INVALID_BASELINE",
            "baseline_receipt_sig8": receipt.get("receipt_sig8") if isinstance(receipt, dict) else None,
            "baseline_errors": baseline_errors,
            "cases": [],
        })

    cases = [
        _run_falsifier_case(case_id=case_id, final_state=final_state, regime=regime, receipt=receipt)
        for case_id in FALSIFIER_CASE_IDS_V0
    ]
    return _external_check_result({
        "check_id": check_id,
        "role": "external_falsifier_sweep",
        "verdict": "PASS" if all(case["passed"] for case in cases) else "FAIL",
        "baseline_receipt_sig8": receipt.get("receipt_sig8") if isinstance(receipt, dict) else None,
        "cases": cases,
    })


# -----------------------------------------------------------------------------
# Projection Deck v0: read-only views derived from receipt + final state.
# -----------------------------------------------------------------------------
def projection_summary(receipt: dict[str, Any], final_state: dict[str, Any] | None) -> dict[str, Any]:
    return {
        "start_state_sig8": receipt.get("start_state_sig8"),
        "final_state_sig8": receipt.get(
            "final_state_sig8", sig8(final_state) if isinstance(final_state, dict) else None
        ),
        "number_of_moves_applied": len(receipt.get("moves_applied") or []),
        "halt_code": receipt.get("halt_code"),
        "receipt_sig8": receipt.get("receipt_sig8"),
    }


def projection_timeline(receipt: dict[str, Any]) -> list[dict[str, Any]]:
    timeline: list[dict[str, Any]] = []
    trace = receipt.get("trace") if isinstance(receipt.get("trace"), list) else []

    for row in trace:
        if not isinstance(row, dict):
            continue

        timeline.append(
            {
                "step": row.get("step"),
                "selected_move": row.get("selected_move"),
                "reason": row.get("reason"),
                "state_change": f"{row.get('before_state_sig8')} -> {row.get('after_state_sig8')}",
                "checkpoint_code": row.get("checkpoint_code"),
                "halt_code": row.get("halt_code"),
            }
        )

    return timeline


def projection_ascii_graph(receipt: dict[str, Any]) -> str:
    trace = receipt.get("trace") if isinstance(receipt.get("trace"), list) else []
    trace = [row for row in trace if isinstance(row, dict)]

    if not trace:
        return "(no trace)"

    def label(value: Any) -> str:
        return "None" if value is None else str(value)

    lines: list[str] = [label(trace[0].get("before_state_sig8"))]

    for row in trace:
        selected_move = row.get("selected_move") or "no selected move"
        checkpoint_code = row.get("checkpoint_code")
        halt_code = row.get("halt_code")
        after_sig = label(row.get("after_state_sig8"))

        suffix = ""
        if checkpoint_code:
            suffix = f" [{checkpoint_code}]"
        if halt_code:
            suffix = f" [{halt_code}]"

        lines.extend(
            [
                "  |",
                f"  | {selected_move}",
                "  v",
                f"{after_sig}{suffix}",
            ]
        )

    return "\n".join(lines)


def projection_pattern_hints(
    receipt: dict[str, Any], final_state: dict[str, Any] | None
) -> dict[str, Any]:
    trace = receipt.get("trace") if isinstance(receipt.get("trace"), list) else []
    trace = [row for row in trace if isinstance(row, dict)]

    # Projection Deck v0.2 repair:
    # A terminal no-selected-move row normally has before == after. That is a
    # no-op halt surface, not a genuine state revisit. Count a repeat only when
    # the path enters a previously seen state through an actual transition.
    state_path: list[str] = []
    for row in trace:
        before = row.get("before_state_sig8")
        after = row.get("after_state_sig8")

        if before is not None:
            before_sig = str(before)
            if not state_path or state_path[-1] != before_sig:
                state_path.append(before_sig)

        if after is not None:
            after_sig = str(after)
            if after_sig != state_path[-1]:
                state_path.append(after_sig)

    states_visited: list[str] = []
    repeated = False
    seen: set[str] = set()
    for state_sig in state_path:
        if state_sig in seen:
            repeated = True
        else:
            seen.add(state_sig)
            states_visited.append(state_sig)

    selected_moves = [
        str(row.get("selected_move"))
        for row in trace
        if row.get("selected_move") is not None
    ]
    checkpoint_codes = [
        str(row.get("checkpoint_code"))
        for row in trace
        if row.get("checkpoint_code") is not None
    ]

    branching_observed = any(
        isinstance(row.get("applicable_moves"), list) and len(row.get("applicable_moves") or []) > 1
        for row in trace
    )
    explicit_halt = any(row.get("halt_code") is not None for row in trace)

    return {
        "states_visited": states_visited,
        "state_path": state_path,
        "moves_applied": receipt.get("moves_applied") or selected_moves,
        "checkpoints": receipt.get("checkpoints") or [],
        "repeated_states": "yes" if repeated else "no",
        "branching_observed": "yes" if branching_observed else "no",
        "final_halt": "explicit" if explicit_halt else "none",
        "invalidity_move_fired": "yes" if "reject_invalid_state.v0" in selected_moves else "no",
        "typing_occurred": "yes"
        if (
            "type_active_object.v0" in selected_moves
            or (isinstance(final_state, dict) and isinstance(final_state.get("typed_record"), dict))
        )
        else "no",
        "typed_ready_checkpoint": "yes" if TYPED_READY_CHECKPOINT in checkpoint_codes else "no",
        "typed_record_schema_validated": "yes"
        if "validate_typed_record_schema.v0" in selected_moves
        else "no",
        "typed_record_regime_bound": "yes"
        if "validate_typed_record_regime_bindings.v0" in selected_moves
        else "no",
        "history_integrity_validated": "yes"
        if "validate_history_integrity.v0" in selected_moves
        else "no",
        "final_halt_readout_consistency_validated": "yes"
        if "validate_final_halt_readout_consistency.v0" in selected_moves
        else "no",
        "no_legacy_ambiguous_fields_validated": "yes"
        if "validate_no_legacy_ambiguous_fields.v0" in selected_moves
        else "no",
        "registry_exhaustion_witness_validated": "yes"
        if "validate_registry_exhaustion_witness.v0" in selected_moves
        else "no",
        "stop_needs_new_move_halt_vocabulary_bound": "yes"
        if "validate_stop_needs_new_move_halt_vocabulary_binding.v0" in selected_moves
        else "no",
        "final_status": final_state.get("status") if isinstance(final_state, dict) else None,
        "final_applicable_moves": trace[-1].get("applicable_moves") if trace else [],
    }


# -----------------------------------------------------------------------------
# Streamlit shell: cockpit only.
# -----------------------------------------------------------------------------
def main() -> None:
    if st is None:
        raise RuntimeError("Streamlit is required to run the UI; runner functions remain importable for tests.")
    st.set_page_config(page_title="Move Runner v0", layout="wide")
    st.title("Deterministic Move Runner v0")

    fixture_surface_report = ensure_fixture_surface()
    with st.expander("Fixture surface bootstrap", expanded=False):
        st.caption("Creates missing starter fixtures only; existing fixtures are never overwritten.")
        st.json(fixture_surface_report)

    regime, state, load_errors = load_fixtures()

    if load_errors:
        st.error("Fixture load halt")
        st.json(load_errors)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Loaded regime")
        st.caption(REGIME_PATH.as_posix())
        st.json(regime if regime is not None else None)

    with col_b:
        st.subheader("Loaded state")
        st.caption(STATE_PATH.as_posix())
        st.json(state if state is not None else None)

    st.subheader("sig8s")
    st.json(
        {
            "regime_sig8": sig8(regime) if isinstance(regime, dict) else None,
            "state_sig8": sig8(state) if isinstance(state, dict) else None,
        }
    )

    if isinstance(regime, dict) and isinstance(state, dict) and not load_errors:
        regime_errors = validate_regime(regime)
        if regime_errors:
            st.subheader("Regime validation")
            st.json(regime_errors)
        elif state.get("regime_id") != regime.get("regime_id") and isinstance(state.get("regime_id"), str):
            st.subheader("Pre-loop halt")
            st.json(
                {
                    "halt_code": "REGIME_MISMATCH",
                    "reason": "state.regime_id differs from regime.regime_id",
                }
            )
        else:
            st.subheader("Applicable moves on loaded state")
            st.json(inspect_applicable_moves(state, regime))

            st.subheader("Capability Envelope v0 — read-only continuation surface")
            envelope_readout = capability_envelope_readout_v0(state, regime)
            candidate_readout = envelope_readout.get("layer_2_bounded_candidate_search") or {}
            topology_readout = envelope_readout.get("layer_4_typed_continuation_topology") or {}
            heuristic_readout = envelope_readout.get("layer_3_local_continuation_heuristics") or {}
            proposed_extension = envelope_readout.get("layer_5_controlled_local_self_extension") or {}
            admission_readout = envelope_readout.get("proposal_admission_readout_v0") or {}
            selected_candidate_id = candidate_readout.get("selected_candidate_id")
            st.caption("Layers 2–5 are present as projection-only surfaces: candidates, non-authoritative heuristics, typed topology, and proposed-only extension records. They do not mutate state/regime or admit moves.")
            st.json({
                "envelope_sig8": envelope_readout.get("envelope_sig8"),
                "selected_candidate_id": selected_candidate_id,
                "candidate_count": candidate_readout.get("candidate_count"),
                "allowed_count": candidate_readout.get("allowed_count"),
                "blocked_count": candidate_readout.get("blocked_count"),
                "topology_code": topology_readout.get("topology_code"),
                "heuristic_count": heuristic_readout.get("heuristic_count"),
                "proposal_count": proposed_extension.get("proposal_count"),
                "any_executable_now": proposed_extension.get("any_executable_now"),
                "any_registry_delta_now": proposed_extension.get("any_registry_delta_now"),
                "admission_verdict": admission_readout.get("verdict"),
                "admission_pass_count": admission_readout.get("pass_count"),
                "admission_fail_count": admission_readout.get("fail_count"),
                "admission_admits_moves": admission_readout.get("admits_moves"),
            })
            with st.expander("Full capability envelope", expanded=False):
                st.json(envelope_readout)
            with st.expander("Layer 2 candidate records", expanded=False):
                st.json(candidate_readout.get("candidates"))

    if st.button("Run lawful move machine"):
        final_state, receipt, receipt_path = run_from_fixtures()

        st.subheader("Projection Deck v0 — read-only views derived from the receipt")

        st.markdown("**Run cards / summary**")
        summary = projection_summary(receipt, final_state)
        card_cols = st.columns(5)
        card_cols[0].metric("start state sig8", summary["start_state_sig8"] or "None")
        card_cols[1].metric("final state sig8", summary["final_state_sig8"] or "None")
        card_cols[2].metric("moves applied", summary["number_of_moves_applied"])
        card_cols[3].metric("halt code", summary["halt_code"] or "None")
        card_cols[4].metric("receipt sig8", summary["receipt_sig8"] or "None")

        st.markdown("**Step timeline**")
        st.table(projection_timeline(receipt))

        st.markdown("**Tiny state graph**")
        st.code(projection_ascii_graph(receipt), language="text")

        st.markdown("**Pattern hints**")
        st.json(projection_pattern_hints(receipt, final_state))

        if isinstance(final_state, dict) and isinstance(regime, dict):
            st.markdown("**Capability Envelope v0 on final state — read-only**")
            st.json(capability_envelope_readout_v0(final_state, regime))

        regime_for_external = regime if isinstance(regime, dict) else {}
        external_consistency = verify_receipt_trace_consistency_v0(
            receipt=receipt,
            final_state=final_state,
            regime=regime_for_external,
        )
        external_falsifier = falsify_stop_needs_new_move_binding_guards_v0(
            receipt=receipt,
            final_state=final_state,
            regime=regime_for_external,
        )

        st.subheader("External verification — not runner moves")
        st.json(
            {
                "receipt_trace_consistency": external_consistency,
                "stop_needs_new_move_falsifiers": external_falsifier,
            }
        )

        st.subheader("Final state")
        st.json(final_state)

        st.subheader("Trace")
        st.json(receipt["trace"])

        st.subheader("Receipt")
        st.json(receipt)

        st.subheader("Receipt path")
        st.code(receipt_path.as_posix())


if __name__ == "__main__":
    main()

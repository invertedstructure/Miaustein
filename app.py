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
    "halt_codes": [
        "INVALID_STATE",
        "INVALID_REGIME",
        "FIXTURE_LOAD_ERROR",
        "REGIME_MISMATCH",
        "NO_APPLICABLE_MOVE",
        "STOP_NEEDS_NEW_MOVE",
        "STEP_LIMIT_EXCEEDED",
    ],
    "move_registry": [
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
    ],
    "receipt_schema": "receipt_v0",
    "regime_id": "regime_v0",
    "regime_patch_policy": "PROPOSED_ONLY",
    "required_typed_record_fields": [
        "object_id",
        "object_kind",
        "smallest_honest_reading",
        "authority_class",
        "truth_status",
        "layer",
        "route_role",
        "extractability",
        "content_scope",
        "allowed_consumers",
        "forbidden_impersonations",
        "declared_allowed_moves",
        "stop_conditions",
        "promotion_rule",
        "notes",
    ],
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

REQUIRED_REGIME_FIELDS = [
    "regime_id",
    "boundary",
    "allowed_object_kinds",
    "required_typed_record_fields",
    "move_registry",
    "halt_codes",
    "receipt_schema",
    "regime_patch_policy",
]

REQUIRED_STATE_FIELDS = [
    "state_id",
    "regime_id",
    "active_object",
    "typed_record",
    "status",
    "history",
]

REQUIRED_TYPED_RECORD_FIELDS = [
    "object_id",
    "object_kind",
    "smallest_honest_reading",
    "authority_class",
    "truth_status",
    "layer",
    "route_role",
    "extractability",
    "content_scope",
    "allowed_consumers",
    "forbidden_impersonations",
    "declared_allowed_moves",
    "stop_conditions",
    "promotion_rule",
    "notes",
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
    "INVALID_STATE",
    "INVALID_REGIME",
    "FIXTURE_LOAD_ERROR",
    "REGIME_MISMATCH",
    "NO_APPLICABLE_MOVE",
    "STOP_NEEDS_NEW_MOVE",
    "STEP_LIMIT_EXCEEDED",
]

CHECKPOINT_CODES_V0 = ["TYPED_STATE_READY"]
TYPED_READY_CHECKPOINT = "TYPED_STATE_READY"

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


def move_validate_typed_record_schema_applies(state: dict[str, Any], regime: dict[str, Any]) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if state.get("status") != "typed_ready_checkpointed":
        return False, "state is not typed_ready_checkpointed"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    if not history_has_checkpoint(state, TYPED_READY_CHECKPOINT):
        return False, "TYPED_STATE_READY checkpoint is not recorded"
    if history_has_move(state, "validate_typed_record_schema.v0"):
        return False, "typed-record schema validation already recorded"
    if "required_typed_record_fields" not in regime:
        return False, "regime.required_typed_record_fields is missing"
    return True, "typed-ready checkpoint is recorded; validate typed_record against required schema fields"


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


def move_validate_typed_record_regime_bindings_applies(
    state: dict[str, Any], regime: dict[str, Any]
) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if state.get("status") != "typed_record_schema_validated":
        return False, "state is not typed_record_schema_validated"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    if not history_has_move(state, "validate_typed_record_schema.v0"):
        return False, "typed-record schema validation is not recorded"
    if history_has_move(state, "validate_typed_record_regime_bindings.v0"):
        return False, "typed-record regime binding validation already recorded"
    for field in ("allowed_object_kinds", "move_registry", "halt_codes"):
        if field not in regime:
            return False, f"regime.{field} is missing"
    return True, "typed-record schema is validated; validate typed_record references against the active regime"


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


def move_validate_history_integrity_applies(state: dict[str, Any], regime: dict[str, Any]) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if state.get("status") != "typed_record_regime_bound":
        return False, "state is not typed_record_regime_bound"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    if history_has_move(state, "validate_history_integrity.v0"):
        return False, "history integrity validation already recorded"
    return True, "typed-record regime bindings are validated; validate the local history spine"


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


def move_validate_final_halt_readout_consistency_applies(
    state: dict[str, Any], regime: dict[str, Any]
) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if state.get("status") != "history_integrity_validated":
        return False, "state is not history_integrity_validated"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    if not history_has_move(state, "validate_history_integrity.v0"):
        return False, "history integrity validation is not recorded"
    if history_has_move(state, "validate_final_halt_readout_consistency.v0"):
        return False, "final halt/readout consistency validation already recorded"
    return True, "history integrity is validated; validate the final halt/readout surface"


def _field_scan_errors(prefix: str, obj: Any, forbidden: set[str], reason_name: str) -> list[str]:
    if not isinstance(obj, dict):
        return []
    present = sorted(set(obj.keys()) & forbidden)
    if not present:
        return []
    return [f"{reason_name}: {prefix} contains {','.join(present)}"]


def no_legacy_ambiguous_fields_errors(state: dict[str, Any], regime: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if state.get("status") != "final_halt_readout_consistency_validated":
        errors.append("final_status_mismatch")

    expected_state_keys = set(REQUIRED_STATE_FIELDS)
    actual_state_keys = set(state.keys())
    if actual_state_keys != expected_state_keys:
        unexpected = sorted(actual_state_keys - expected_state_keys)
        missing = sorted(expected_state_keys - actual_state_keys)
        if unexpected:
            errors.append("unexpected_state_field=" + ",".join(unexpected))
        if missing:
            errors.append("missing_state_field=" + ",".join(missing))

    errors.extend(_field_scan_errors("state", state, LEGACY_AMBIGUOUS_FIELDS_V0, "legacy_state_field_present"))
    errors.extend(_field_scan_errors("state", state, PROJECTION_ONLY_FIELDS_V0, "projection_field_embedded_in_state"))

    active_object = state.get("active_object")
    expected_active_object_keys = {"object_id", "object_kind", "smallest_honest_reading"}
    if not isinstance(active_object, dict):
        errors.append("active_object_missing")
    else:
        actual_active_object_keys = set(active_object.keys())
        if actual_active_object_keys != expected_active_object_keys:
            unexpected = sorted(actual_active_object_keys - expected_active_object_keys)
            missing = sorted(expected_active_object_keys - actual_active_object_keys)
            if unexpected:
                errors.append("unexpected_active_object_field=" + ",".join(unexpected))
            if missing:
                errors.append("missing_active_object_field=" + ",".join(missing))
        errors.extend(
            _field_scan_errors("active_object", active_object, LEGACY_AMBIGUOUS_FIELDS_V0, "legacy_state_field_present")
        )
        errors.extend(
            _field_scan_errors("active_object", active_object, PROJECTION_ONLY_FIELDS_V0, "projection_field_embedded_in_state")
        )

    typed_record = state.get("typed_record")
    required_typed_record_fields = regime.get("required_typed_record_fields")
    if not isinstance(typed_record, dict):
        errors.append("typed_record_missing")
    elif not isinstance(required_typed_record_fields, list):
        errors.append("regime_required_typed_record_fields_invalid")
    else:
        expected_typed_record_keys = set(required_typed_record_fields)
        actual_typed_record_keys = set(typed_record.keys())
        if actual_typed_record_keys != expected_typed_record_keys:
            unexpected = sorted(actual_typed_record_keys - expected_typed_record_keys)
            missing = sorted(expected_typed_record_keys - actual_typed_record_keys)
            parts = []
            if unexpected:
                parts.append("unexpected=" + ",".join(unexpected))
            if missing:
                parts.append("missing=" + ",".join(missing))
            errors.append("typed_record_field_mismatch:" + ";".join(parts))

        errors.extend(
            _field_scan_errors("typed_record", typed_record, LEGACY_AMBIGUOUS_FIELDS_V0, "legacy_state_field_present")
        )
        errors.extend(
            _field_scan_errors("typed_record", typed_record, PROJECTION_ONLY_FIELDS_V0, "projection_field_embedded_in_state")
        )

        forbidden_impersonations = typed_record.get("forbidden_impersonations")
        required_impersonation_blocks = {
            "theorem_claim",
            "proof_closure",
            "polished_architecture",
            "old_monolithic_app",
            "dynamic_regime_evolution",
        }
        if not isinstance(forbidden_impersonations, list) or not required_impersonation_blocks.issubset(
            set(forbidden_impersonations)
        ):
            errors.append("forbidden_impersonation_missing")

        for field_name in ("stop_conditions",):
            values = typed_record.get(field_name)
            if isinstance(values, list):
                legacy = sorted(set(str(v) for v in values) & LEGACY_AMBIGUOUS_HALT_CODES_V0)
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
            actual_history_fields = set(row.keys())
            if actual_history_fields != expected_history_fields:
                unexpected = sorted(actual_history_fields - expected_history_fields)
                missing = sorted(expected_history_fields - actual_history_fields)
                parts = []
                if unexpected:
                    parts.append("unexpected=" + ",".join(unexpected))
                if missing:
                    parts.append("missing=" + ",".join(missing))
                errors.append(f"unexpected_history_field: row[{index}] " + ";".join(parts))

            checkpoint_code = row.get("checkpoint_code")
            halt_code = row.get("halt_code")
            if checkpoint_code is not None and checkpoint_code not in CHECKPOINT_CODES_V0:
                errors.append(f"checkpoint_halt_confusion: row[{index}] unknown checkpoint_code={checkpoint_code}")
            if halt_code == TYPED_READY_CHECKPOINT:
                errors.append(f"checkpoint_halt_confusion: row[{index}] TYPED_STATE_READY used as halt_code")
            if halt_code == "STOP_NEEDS_NEW_MOVE":
                errors.append(f"checkpoint_halt_confusion: row[{index}] STOP_NEEDS_NEW_MOVE embedded in history halt_code")
            if isinstance(halt_code, str) and halt_code in LEGACY_AMBIGUOUS_HALT_CODES_V0:
                errors.append("legacy_halt_code_present=" + halt_code)

            errors.extend(
                _field_scan_errors(f"history[{index}]", row, LEGACY_AMBIGUOUS_FIELDS_V0, "legacy_state_field_present")
            )
            errors.extend(
                _field_scan_errors(
                    f"history[{index}]", row, PROJECTION_ONLY_FIELDS_V0, "projection_field_embedded_in_state"
                )
            )

    halt_codes = regime.get("halt_codes")
    if not isinstance(halt_codes, list):
        errors.append("regime_halt_codes_invalid")
    else:
        legacy = sorted(set(str(v) for v in halt_codes) & LEGACY_AMBIGUOUS_HALT_CODES_V0)
        if legacy:
            errors.append("legacy_halt_code_present=" + ",".join(legacy))
        if TYPED_READY_CHECKPOINT in halt_codes:
            errors.append("checkpoint_halt_confusion: TYPED_STATE_READY listed as halt_code")

    regime_keys = set(regime.keys())
    if regime_keys != set(REQUIRED_REGIME_FIELDS):
        unexpected = sorted(regime_keys - set(REQUIRED_REGIME_FIELDS))
        if unexpected:
            errors.append("unexpected_regime_field=" + ",".join(unexpected))

    return errors


def move_validate_no_legacy_ambiguous_fields_applies(
    state: dict[str, Any], regime: dict[str, Any]
) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if state.get("status") != "final_halt_readout_consistency_validated":
        return False, "state is not final_halt_readout_consistency_validated"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    if not history_has_move(state, "validate_final_halt_readout_consistency.v0"):
        return False, "final halt/readout consistency validation is not recorded"
    if history_has_move(state, "validate_no_legacy_ambiguous_fields.v0"):
        return False, "no-legacy ambiguous-fields validation already recorded"
    return True, "final halt/readout consistency is validated; validate no legacy or ambiguous fields"




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


def move_validate_registry_exhaustion_witness_applies(
    state: dict[str, Any], regime: dict[str, Any]
) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if state.get("status") != "no_legacy_ambiguous_fields_validated":
        return False, "state is not no_legacy_ambiguous_fields_validated"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    if not history_has_move(state, "validate_no_legacy_ambiguous_fields.v0"):
        return False, "no-legacy ambiguous-fields validation is not recorded"
    if history_has_move(state, "validate_registry_exhaustion_witness.v0"):
        return False, "registry exhaustion witness validation already recorded"
    return True, "no legacy or ambiguous fields are validated; validate frozen registry exhaustion witness"


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

    if state.get("status") != "registry_exhaustion_witness_validated":
        errors.append("terminal_halt_binding_missing")

    history = state.get("history")
    if not isinstance(history, list):
        errors.append("terminal_halt_binding_missing")
        history = []

    if history_move_indices(history, "validate_registry_exhaustion_witness.v0") != [7]:
        errors.append("terminal_halt_binding_missing")
    if history_has_move(state, move_id):
        errors.append("terminal_halt_binding_missing")

    for index, row in enumerate(history):
        if not isinstance(row, dict):
            continue
        if (
            row.get("move_id") == halt_code
            or row.get("checkpoint_code") == halt_code
            or row.get("halt_code") == halt_code
        ):
            errors.append(f"stop_needs_new_move_used_in_history=row[{index}]")

    typed_record = state.get("typed_record")
    if not isinstance(typed_record, dict):
        errors.append("stop_needs_new_move_missing_from_typed_record")
    else:
        stop_conditions = typed_record.get("stop_conditions")
        if not isinstance(stop_conditions, list) or halt_code not in stop_conditions:
            errors.append("stop_needs_new_move_missing_from_typed_record")

        forbidden_impersonations = typed_record.get("forbidden_impersonations")
        required_impersonation_guards = set(STOP_NEEDS_NEW_MOVE_BINDING_SPEC_V0["must_not_impersonate"])
        if not isinstance(forbidden_impersonations, list) or not required_impersonation_guards.issubset(
            set(forbidden_impersonations)
        ):
            errors.append("halt_impersonation_guard_missing")

    halt_codes = regime.get("halt_codes")
    if not isinstance(halt_codes, list) or halt_code not in halt_codes:
        errors.append("stop_needs_new_move_missing_from_regime")

    move_registry = regime.get("move_registry")
    if isinstance(move_registry, list) and halt_code in move_registry:
        errors.append("stop_needs_new_move_registered_as_move")

    spec = STOP_NEEDS_NEW_MOVE_BINDING_SPEC_V0
    if spec.get("halt_code") != halt_code:
        errors.append("terminal_halt_binding_missing")
    if spec.get("smallest_honest_meaning") != (
        "continuation requires a lawful move not currently present in the frozen move registry"
    ):
        errors.append("halt_meaning_mismatch")

    required_impersonation_guards = {
        "proof_closure",
        "theorem_success",
        "engine_completion",
        "autonomous_registry_evolution",
        "taxonomy_upgrade",
        "architecture_redesign",
    }
    if not isinstance(spec.get("must_not_impersonate"), list) or not required_impersonation_guards.issubset(
        set(spec.get("must_not_impersonate") or [])
    ):
        errors.append("halt_impersonation_guard_missing")

    expected_next_handling = [
        "draft smallest missing move",
        "require explicit human-authored patch",
        "rerun from frozen fixtures after patch",
    ]
    if spec.get("allowed_next_handling") != expected_next_handling:
        errors.append("allowed_next_handling_missing")

    if regime.get("regime_patch_policy") != "PROPOSED_ONLY":
        errors.append("autonomous_registry_evolution_leak")

    for forbidden_field in ("registry_patch", "taxonomy_delta", "inferred_move", "learned_move"):
        if _field_present_anywhere(state, forbidden_field) or _field_present_anywhere(regime, forbidden_field):
            errors.append("autonomous_registry_evolution_leak")
            break

    for forbidden_field in ("dynamic_regime_update", "learned_move"):
        if _field_present_anywhere(state, forbidden_field) or _field_present_anywhere(regime, forbidden_field):
            errors.append("dynamic_regime_update_leak")
            break

    candidate = _dry_stop_needs_new_move_bound_state(state)
    post_applicable = inspect_applicable_moves(candidate, regime)
    if post_applicable:
        errors.append("terminal_halt_binding_missing")
    dry_halt_code, dry_reason = classify_no_applicable_move(candidate, regime)
    if dry_halt_code != halt_code:
        errors.append("terminal_halt_binding_missing")
    elif dry_reason != spec.get("smallest_honest_meaning"):
        errors.append("halt_meaning_mismatch")

    return errors


def move_validate_stop_needs_new_move_halt_vocabulary_binding_applies(
    state: dict[str, Any], regime: dict[str, Any]
) -> tuple[bool, str]:
    if state_validation_errors(state, regime):
        return False, "state is invalid; invalidity move has priority"
    if state.get("status") != "registry_exhaustion_witness_validated":
        return False, "state is not registry_exhaustion_witness_validated"
    if not isinstance(state.get("typed_record"), dict):
        return False, "typed_record is not present"
    if history_move_indices(state.get("history") if isinstance(state.get("history"), list) else [], "validate_registry_exhaustion_witness.v0") != [7]:
        return False, "registry exhaustion witness validation is not recorded exactly once at the expected position"
    if history_has_move(state, "validate_stop_needs_new_move_halt_vocabulary_binding.v0"):
        return False, "STOP_NEEDS_NEW_MOVE halt vocabulary binding already recorded"
    return True, "registry exhaustion is validated; bind STOP_NEEDS_NEW_MOVE as halt vocabulary"


def inspect_applicable_moves(state: dict[str, Any], regime: dict[str, Any]) -> list[dict[str, str]]:
    checks = {
        "reject_invalid_state.v0": move_reject_invalid_state_applies,
        "type_active_object.v0": move_type_active_object_applies,
        "checkpoint_typed_state.v0": move_checkpoint_typed_state_applies,
        "validate_typed_record_schema.v0": move_validate_typed_record_schema_applies,
        "validate_typed_record_regime_bindings.v0": move_validate_typed_record_regime_bindings_applies,
        "validate_history_integrity.v0": move_validate_history_integrity_applies,
        "validate_final_halt_readout_consistency.v0": move_validate_final_halt_readout_consistency_applies,
        "validate_no_legacy_ambiguous_fields.v0": move_validate_no_legacy_ambiguous_fields_applies,
        "validate_registry_exhaustion_witness.v0": move_validate_registry_exhaustion_witness_applies,
        "validate_stop_needs_new_move_halt_vocabulary_binding.v0": move_validate_stop_needs_new_move_halt_vocabulary_binding_applies,
    }

    applicable: list[dict[str, str]] = []
    for move_id in regime["move_registry"]:
        applies, reason = checks[move_id](state, regime)
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


def apply_validate_typed_record_schema(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    schema_errors = typed_record_schema_errors(state, regime)
    if schema_errors:
        new_state = append_history(
            state,
            {
                "move_id": "validate_typed_record_schema.v0",
                "outcome": "halt",
                "checkpoint_code": None,
                "halt_code": "INVALID_STATE",
                "reason": "; ".join(schema_errors),
            },
        )
        new_state["status"] = "halted_invalid"
        return new_state, "INVALID_STATE", None

    new_state = append_history(
        state,
        {
            "move_id": "validate_typed_record_schema.v0",
            "outcome": "typed_record_schema_validated",
            "checkpoint_code": None,
            "halt_code": None,
            "reason": "typed_record matches required typed-record field list",
        },
    )
    new_state["status"] = "typed_record_schema_validated"
    return new_state, None, None


def apply_validate_typed_record_regime_bindings(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    binding_errors = typed_record_regime_binding_errors(state, regime)
    if binding_errors:
        new_state = append_history(
            state,
            {
                "move_id": "validate_typed_record_regime_bindings.v0",
                "outcome": "halt",
                "checkpoint_code": None,
                "halt_code": "INVALID_STATE",
                "reason": "; ".join(binding_errors),
            },
        )
        new_state["status"] = "halted_invalid"
        return new_state, "INVALID_STATE", None

    new_state = append_history(
        state,
        {
            "move_id": "validate_typed_record_regime_bindings.v0",
            "outcome": "typed_record_regime_bound",
            "checkpoint_code": None,
            "halt_code": None,
            "reason": "typed_record object kind, declared moves, and stop conditions are bound to the active regime",
        },
    )
    new_state["status"] = "typed_record_regime_bound"
    return new_state, None, None


def apply_validate_history_integrity(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    integrity_errors = history_integrity_errors(state, regime)
    if integrity_errors:
        new_state = append_history(
            state,
            {
                "move_id": "validate_history_integrity.v0",
                "outcome": "halt",
                "checkpoint_code": None,
                "halt_code": "INVALID_STATE",
                "reason": "; ".join(integrity_errors),
            },
        )
        new_state["status"] = "halted_invalid"
        return new_state, "INVALID_STATE", None

    new_state = append_history(
        state,
        {
            "move_id": "validate_history_integrity.v0",
            "outcome": "history_integrity_validated",
            "checkpoint_code": None,
            "halt_code": None,
            "reason": "history rows form a coherent registered move spine",
        },
    )
    new_state["status"] = "history_integrity_validated"
    return new_state, None, None


def apply_validate_final_halt_readout_consistency(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    consistency_errors = final_halt_readout_consistency_errors(state, regime)
    if consistency_errors:
        new_state = append_history(
            state,
            {
                "move_id": "validate_final_halt_readout_consistency.v0",
                "outcome": "halt",
                "checkpoint_code": None,
                "halt_code": "INVALID_STATE",
                "reason": "; ".join(consistency_errors),
            },
        )
        new_state["status"] = "halted_invalid"
        return new_state, "INVALID_STATE", None

    candidate = append_history(
        state,
        {
            "move_id": "validate_final_halt_readout_consistency.v0",
            "outcome": "final_halt_readout_consistency_validated",
            "checkpoint_code": None,
            "halt_code": None,
            "reason": "final halt/readout surface is coherent with state, history, trace, and receipt prerequisites",
        },
    )
    candidate["status"] = "final_halt_readout_consistency_validated"

    return candidate, None, None


def apply_validate_no_legacy_ambiguous_fields(
    state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    legacy_errors = no_legacy_ambiguous_fields_errors(state, regime)
    if legacy_errors:
        new_state = append_history(
            state,
            {
                "move_id": "validate_no_legacy_ambiguous_fields.v0",
                "outcome": "halt",
                "checkpoint_code": None,
                "halt_code": "INVALID_STATE",
                "reason": "; ".join(legacy_errors),
            },
        )
        new_state["status"] = "halted_invalid"
        return new_state, "INVALID_STATE", None

    candidate = append_history(
        state,
        {
            "move_id": "validate_no_legacy_ambiguous_fields.v0",
            "outcome": "no_legacy_ambiguous_fields_validated",
            "checkpoint_code": None,
            "halt_code": None,
            "reason": "state, typed_record, history, and regime vocabulary contain no legacy or ambiguous fields",
        },
    )
    candidate["status"] = "no_legacy_ambiguous_fields_validated"
    return candidate, None, None




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


def apply_move(
    move_id: str, state: dict[str, Any], regime: dict[str, Any], reason: str
) -> tuple[dict[str, Any], str | None, str | None]:
    if move_id == "reject_invalid_state.v0":
        return apply_reject_invalid_state(state, regime, reason)
    if move_id == "type_active_object.v0":
        return apply_type_active_object(state, regime, reason)
    if move_id == "checkpoint_typed_state.v0":
        return apply_checkpoint_typed_state(state, regime, reason)
    if move_id == "validate_typed_record_schema.v0":
        return apply_validate_typed_record_schema(state, regime, reason)
    if move_id == "validate_typed_record_regime_bindings.v0":
        return apply_validate_typed_record_regime_bindings(state, regime, reason)
    if move_id == "validate_history_integrity.v0":
        return apply_validate_history_integrity(state, regime, reason)
    if move_id == "validate_final_halt_readout_consistency.v0":
        return apply_validate_final_halt_readout_consistency(state, regime, reason)
    if move_id == "validate_no_legacy_ambiguous_fields.v0":
        return apply_validate_no_legacy_ambiguous_fields(state, regime, reason)
    if move_id == "validate_registry_exhaustion_witness.v0":
        return apply_validate_registry_exhaustion_witness(state, regime, reason)
    if move_id == "validate_stop_needs_new_move_halt_vocabulary_binding.v0":
        return apply_validate_stop_needs_new_move_halt_vocabulary_binding(state, regime, reason)
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
    """Externally verify the emitted receipt against trace, state, and regime.

    This is not a runner move. It verifies only the already emitted witness
    surface for the current STOP_NEEDS_NEW_MOVE cut.
    """
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
        errors.append("receipt_not_object")
        receipt = {}
    if not isinstance(regime, dict):
        errors.append("regime_not_object")
        regime = {}

    terminal = _terminal_trace_row(receipt, errors)
    trace = receipt.get("trace") if isinstance(receipt.get("trace"), list) else []
    trace_rows = _as_dict_list(trace)

    selected_moves = [
        row.get("selected_move")
        for row in trace_rows
        if row.get("selected_move") is not None
    ]
    if receipt.get("moves_applied") != selected_moves:
        errors.append(
            "moves_applied_mismatch: "
            f"receipt={receipt.get('moves_applied')!r}; trace_selected={selected_moves!r}"
        )

    if terminal is not None:
        if receipt.get("halt_code") != terminal.get("halt_code"):
            errors.append(
                "halt_code_mismatch: "
                f"receipt={receipt.get('halt_code')!r}; terminal={terminal.get('halt_code')!r}"
            )
        if terminal.get("selected_move") is not None:
            errors.append("terminal_selected_move_not_null")
        if terminal.get("applicable_moves") != []:
            errors.append("terminal_applicable_moves_not_empty")
        if terminal.get("halt_code") != halt_code:
            errors.append("terminal_halt_code_is_not_STOP_NEEDS_NEW_MOVE")

    if isinstance(final_state, dict):
        computed_final_sig8 = sig8(final_state)
        if receipt.get("final_state_sig8") != computed_final_sig8:
            errors.append(
                "final_state_sig8_mismatch: "
                f"receipt={receipt.get('final_state_sig8')!r}; computed={computed_final_sig8!r}"
            )
    else:
        computed_final_sig8 = None
        errors.append("final_state_not_object")

    stop_trace_rows = [
        index
        for index, row in enumerate(trace_rows)
        if row.get("halt_code") == halt_code
    ]
    expected_terminal_index = len(trace_rows) - 1
    if stop_trace_rows != [expected_terminal_index]:
        errors.append(
            "stop_needs_new_move_trace_position_invalid: "
            f"rows={stop_trace_rows!r}; expected={[expected_terminal_index]!r}"
        )

    if isinstance(final_state, dict):
        history_stop_rows = [
            index
            for index, value in enumerate(_history_halt_codes(final_state))
            if value == halt_code
        ]
        if history_stop_rows:
            errors.append(
                "stop_needs_new_move_embedded_in_history_halt_code: "
                + ",".join(str(index) for index in history_stop_rows)
            )

    move_registry = regime.get("move_registry")
    if not isinstance(move_registry, list):
        errors.append("move_registry_missing_or_not_list")
    elif halt_code in move_registry:
        errors.append("stop_needs_new_move_registered_as_move")

    receipt_sig8 = receipt.get("receipt_sig8")
    if not isinstance(receipt_sig8, str) or not receipt_sig8:
        errors.append("receipt_sig8_missing")
        recomputed_receipt_sig8 = None
    else:
        recomputed_receipt_sig8 = sig8(receipt)
        if receipt_sig8 != recomputed_receipt_sig8:
            errors.append(
                "receipt_sig8_mismatch: "
                f"receipt={receipt_sig8!r}; recomputed={recomputed_receipt_sig8!r}"
            )

    return _external_check_result(
        {
            "check_id": check_id,
            "role": "external_verifier",
            "verdict": "PASS" if not errors else "FAIL",
            "errors": errors,
            "input_receipt_sig8": receipt.get("receipt_sig8"),
            "input_final_state_sig8": receipt.get("final_state_sig8"),
            "computed_final_state_sig8": computed_final_sig8,
            "recomputed_receipt_sig8": recomputed_receipt_sig8,
            "checked_claims": checked_claims,
        }
    )


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


def _run_falsifier_case(
    *,
    case_id: str,
    final_state: dict[str, Any] | None,
    regime: dict[str, Any],
    receipt: dict[str, Any],
    mutate: Any,
) -> dict[str, Any]:
    mutated_state = copy.deepcopy(final_state)
    mutated_regime = copy.deepcopy(regime)
    mutated_receipt = copy.deepcopy(receipt)
    mutated_state, mutated_regime, mutated_receipt = mutate(
        mutated_state,
        mutated_regime,
        mutated_receipt,
    )
    errors = external_stop_needs_new_move_binding_guard_errors_v0(
        final_state=mutated_state,
        regime=mutated_regime,
        receipt=mutated_receipt,
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
    """Run tiny direct mutation attacks against the STOP_NEEDS_NEW_MOVE claim."""
    check_id = "falsify_stop_needs_new_move_binding_guards.v0"
    halt_code = "STOP_NEEDS_NEW_MOVE"

    baseline_errors = external_stop_needs_new_move_binding_guard_errors_v0(
        final_state=final_state,
        regime=regime,
        receipt=receipt,
    )
    if baseline_errors:
        return _external_check_result(
            {
                "check_id": check_id,
                "role": "external_falsifier_sweep",
                "verdict": "INVALID_BASELINE",
                "baseline_receipt_sig8": receipt.get("receipt_sig8") if isinstance(receipt, dict) else None,
                "baseline_errors": baseline_errors,
                "cases": [],
            }
        )

    def mutate_registry_contains_stop(state: dict[str, Any], regime: dict[str, Any], receipt: dict[str, Any]):
        regime["move_registry"] = list(regime.get("move_registry") or []) + [halt_code]
        return state, regime, receipt

    def mutate_history_contains_stop(state: dict[str, Any], regime: dict[str, Any], receipt: dict[str, Any]):
        history = state.get("history")
        if isinstance(history, list) and history:
            history[-1]["halt_code"] = halt_code
        else:
            state["history"] = [
                {
                    "move_id": "synthetic_mutation_row",
                    "outcome": "mutated",
                    "checkpoint_code": None,
                    "halt_code": halt_code,
                    "reason": "mutation inserts terminal halt into history",
                }
            ]
        return state, regime, receipt

    def mutate_remove_stop_condition(state: dict[str, Any], regime: dict[str, Any], receipt: dict[str, Any]):
        typed_record = state.get("typed_record")
        if isinstance(typed_record, dict) and isinstance(typed_record.get("stop_conditions"), list):
            typed_record["stop_conditions"] = [
                value for value in typed_record["stop_conditions"] if value != halt_code
            ]
        return state, regime, receipt

    def mutate_remove_regime_halt_code(state: dict[str, Any], regime: dict[str, Any], receipt: dict[str, Any]):
        if isinstance(regime.get("halt_codes"), list):
            regime["halt_codes"] = [value for value in regime["halt_codes"] if value != halt_code]
        return state, regime, receipt

    def mutate_add_autonomous_continuation_field(
        state: dict[str, Any], regime: dict[str, Any], receipt: dict[str, Any]
    ):
        for field_name in sorted(AUTONOMOUS_CONTINUATION_FIELDS_V0):
            state[field_name] = {"attempt": "illegal autonomous continuation"}
        return state, regime, receipt

    def mutate_remove_required_forbidden_impersonations(
        state: dict[str, Any], regime: dict[str, Any], receipt: dict[str, Any]
    ):
        typed_record = state.get("typed_record")
        weakened = {
            "autonomous_registry_evolution",
            "taxonomy_upgrade",
            "architecture_redesign",
        }
        if isinstance(typed_record, dict) and isinstance(typed_record.get("forbidden_impersonations"), list):
            typed_record["forbidden_impersonations"] = [
                value for value in typed_record["forbidden_impersonations"] if value not in weakened
            ]
        return state, regime, receipt

    case_specs = [
        ("put_STOP_NEEDS_NEW_MOVE_in_move_registry", mutate_registry_contains_stop),
        ("put_STOP_NEEDS_NEW_MOVE_in_history_halt_code", mutate_history_contains_stop),
        (
            "remove_STOP_NEEDS_NEW_MOVE_from_typed_record_stop_conditions",
            mutate_remove_stop_condition,
        ),
        ("remove_STOP_NEEDS_NEW_MOVE_from_regime_halt_codes", mutate_remove_regime_halt_code),
        ("add_autonomous_continuation_field", mutate_add_autonomous_continuation_field),
        ("weaken_forbidden_impersonations", mutate_remove_required_forbidden_impersonations),
    ]

    cases = [
        _run_falsifier_case(
            case_id=case_id,
            final_state=final_state,
            regime=regime,
            receipt=receipt,
            mutate=mutate,
        )
        for case_id, mutate in case_specs
    ]
    verdict = "PASS" if all(case["passed"] for case in cases) else "FAIL"

    return _external_check_result(
        {
            "check_id": check_id,
            "role": "external_falsifier_sweep",
            "verdict": verdict,
            "baseline_receipt_sig8": receipt.get("receipt_sig8") if isinstance(receipt, dict) else None,
            "cases": cases,
        }
    )


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

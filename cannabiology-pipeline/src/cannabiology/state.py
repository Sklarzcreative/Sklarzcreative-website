"""Pipeline state: explicit state machine, private store, figure-level locks.

The canonical tracker is never mutated here. This is a separate runtime layer
living in the private workspace.
"""
import json
import os
import time
from contextlib import contextmanager
from pathlib import Path

from . import workspace

UNROUTED = "UNROUTED"
ROUTED = "ROUTED"
BLOCKED_HOLD = "BLOCKED_HOLD"
CONTEXT_READY = "CONTEXT_READY"
PROMPT_READY = "PROMPT_READY"
GENERATING = "GENERATING"
CANDIDATE_READY = "CANDIDATE_READY"
OA_REVIEW = "OA_REVIEW"
VECTOR_EDIT_REQUIRED = "VECTOR_EDIT_REQUIRED"
IMAGE_EDIT_REQUIRED = "IMAGE_EDIT_REQUIRED"
REGENERATE_REQUIRED = "REGENERATE_REQUIRED"
SCIENTIFIC_VERIFICATION_REQUIRED = "SCIENTIFIC_VERIFICATION_REQUIRED"
HUMAN_CONFIRMATION_REQUIRED = "HUMAN_CONFIRMATION_REQUIRED"
PRODUCTION_READY_BASE_ART = "PRODUCTION_READY_BASE_ART"
PENDING_HUMAN_APPROVAL = "PENDING_HUMAN_APPROVAL"
HUMAN_APPROVED = "HUMAN_APPROVED"
REJECTED = "REJECTED"
PACKAGED = "PACKAGED"

STATES = [
    UNROUTED, ROUTED, BLOCKED_HOLD, CONTEXT_READY, PROMPT_READY, GENERATING,
    CANDIDATE_READY, OA_REVIEW, VECTOR_EDIT_REQUIRED, IMAGE_EDIT_REQUIRED,
    REGENERATE_REQUIRED, SCIENTIFIC_VERIFICATION_REQUIRED,
    HUMAN_CONFIRMATION_REQUIRED, PRODUCTION_READY_BASE_ART,
    PENDING_HUMAN_APPROVAL, HUMAN_APPROVED, REJECTED, PACKAGED,
]

_REPAIR = {VECTOR_EDIT_REQUIRED, IMAGE_EDIT_REQUIRED, REGENERATE_REQUIRED}

TRANSITIONS = {
    UNROUTED: {ROUTED, BLOCKED_HOLD},
    ROUTED: {CONTEXT_READY, BLOCKED_HOLD, HUMAN_CONFIRMATION_REQUIRED},
    BLOCKED_HOLD: {ROUTED},
    CONTEXT_READY: {PROMPT_READY, HUMAN_CONFIRMATION_REQUIRED},
    PROMPT_READY: {GENERATING, HUMAN_CONFIRMATION_REQUIRED},
    GENERATING: {CANDIDATE_READY, REJECTED},
    CANDIDATE_READY: {OA_REVIEW},
    OA_REVIEW: _REPAIR | {PRODUCTION_READY_BASE_ART, SCIENTIFIC_VERIFICATION_REQUIRED,
                          HUMAN_CONFIRMATION_REQUIRED, REJECTED},
    VECTOR_EDIT_REQUIRED: {CANDIDATE_READY, OA_REVIEW, HUMAN_CONFIRMATION_REQUIRED},
    IMAGE_EDIT_REQUIRED: {GENERATING, HUMAN_CONFIRMATION_REQUIRED, REJECTED},
    REGENERATE_REQUIRED: {GENERATING, HUMAN_CONFIRMATION_REQUIRED, REJECTED},
    SCIENTIFIC_VERIFICATION_REQUIRED: {HUMAN_CONFIRMATION_REQUIRED, CONTEXT_READY, REJECTED},
    HUMAN_CONFIRMATION_REQUIRED: {ROUTED, CONTEXT_READY, PROMPT_READY, GENERATING,
                                  CANDIDATE_READY, REJECTED},
    PRODUCTION_READY_BASE_ART: {PENDING_HUMAN_APPROVAL, OA_REVIEW},
    PENDING_HUMAN_APPROVAL: {HUMAN_APPROVED, IMAGE_EDIT_REQUIRED,
                             VECTOR_EDIT_REQUIRED, REGENERATE_REQUIRED, REJECTED},
    HUMAN_APPROVED: {PACKAGED},
    REJECTED: {ROUTED, REGENERATE_REQUIRED},
    PACKAGED: set(),
}


class StateError(RuntimeError):
    pass


class LockError(RuntimeError):
    pass


def can_transition(src, dst):
    return dst in TRANSITIONS.get(src, set())


class Store:
    """Append-safe JSON state store in the private workspace."""

    def __init__(self, path=None):
        self.path = Path(path) if path else workspace.resolve() / "state" / "pipeline.json"
        workspace.assert_safe_write(self.path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._read()

    def _read(self):
        if self.path.exists():
            with open(self.path) as f:
                return json.load(f)
        return {"figures": {}, "version": 2}

    def save(self):
        """Atomic write: temp file then replace."""
        tmp = self.path.with_suffix(".tmp")
        with open(tmp, "w") as f:
            json.dump(self._data, f, indent=2, sort_keys=True)
        os.replace(tmp, self.path)

    def get(self, asset_id):
        return self._data["figures"].setdefault(asset_id, {
            "asset_id": asset_id, "state": UNROUTED, "route": None,
            "generative_repairs": 0, "vector_edits": 0,
            "candidates": [], "reviews": [], "repairs": [], "history": [],
            "prompt_versions": [], "selected_candidate": None,
            "context_version": None, "human_approved": False,
        })

    def all(self):
        return self._data["figures"]

    def transition(self, asset_id, dst, note="", force=False):
        rec = self.get(asset_id)
        src = rec["state"]
        if src == dst:
            return rec
        if not force and not can_transition(src, dst):
            raise StateError(f"{asset_id}: illegal transition {src} -> {dst}")
        rec["state"] = dst
        rec["history"].append({
            "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "from": src, "to": dst, "note": note,
        })
        return rec


@contextmanager
def figure_lock(asset_id, timeout=0.0):
    """Exclusive per-figure lock. Two workers never write the same asset."""
    lock_dir = workspace.resolve() / "state" / "locks"
    lock_dir.mkdir(parents=True, exist_ok=True)
    lock = lock_dir / f"{asset_id}.lock"
    deadline = time.time() + timeout
    while True:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.write(fd, str(os.getpid()).encode())
            os.close(fd)
            break
        except FileExistsError:
            if time.time() >= deadline:
                raise LockError(f"{asset_id} is locked by another worker ({lock})")
            time.sleep(0.05)
    try:
        yield lock
    finally:
        lock.unlink(missing_ok=True)

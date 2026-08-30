"""Privacy boundary.

The code repository is assumed PUBLIC. Every artifact derived from the
Cannabiology manuscript - context extracts, prompts, candidates, OA reports,
packages, state - must live in a private workspace OUTSIDE the repository.

The workspace is the primary boundary. .gitignore is defence in depth only.
If no safe workspace is configured, every client-data operation FAILS CLOSED.
"""
import os
from pathlib import Path

ENV_VAR = "CANNABIOLOGY_WORKSPACE"
REPO_ROOT = Path(__file__).resolve().parents[3]

SUBDIRS = [
    "canonical/tracker_snapshot", "canonical/manuscript_sources", "canonical/qa_sources",
    "context", "runs", "state", "approved/base_art", "approved/composites",
    "holds", "rejected", "archive",
]


class WorkspaceError(RuntimeError):
    """Raised when no safe private workspace is available. Always fail closed."""


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def resolve(create: bool = False) -> Path:
    """Return the private workspace root, or raise. Never returns a repo path."""
    raw = os.environ.get(ENV_VAR, "").strip()
    if not raw:
        raise WorkspaceError(
            f"{ENV_VAR} is not set.\n"
            "Client-derived material must not be written inside this repository,\n"
            "which is public. Set an absolute path outside the repo, e.g.:\n"
            f"  export {ENV_VAR}=$HOME/cannabiology-workspace\n"
            "Then run:  python -m cannabiology doctor"
        )
    ws = Path(raw).expanduser()
    if not ws.is_absolute():
        raise WorkspaceError(f"{ENV_VAR} must be an absolute path, got: {raw}")
    if _is_inside(ws, REPO_ROOT):
        raise WorkspaceError(
            f"{ENV_VAR} points inside the public repository ({ws}).\n"
            "Client data must live outside the repo. Choose another path."
        )
    if create:
        for sub in SUBDIRS:
            (ws / sub).mkdir(parents=True, exist_ok=True)
    elif not ws.exists():
        raise WorkspaceError(
            f"Workspace {ws} does not exist. Create it with:\n"
            "  python -m cannabiology doctor --init-workspace"
        )
    return ws


def assert_safe_write(path) -> Path:
    """Guard every client-data write. Refuses any path inside the repository."""
    p = Path(path).resolve()
    if _is_inside(p, REPO_ROOT):
        raise WorkspaceError(
            f"Refusing to write client-derived content inside the public repo:\n  {p}"
        )
    return p

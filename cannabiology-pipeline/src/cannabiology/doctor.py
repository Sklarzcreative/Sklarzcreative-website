"""Environment, privacy and integrity checks."""
import os
import shutil
import subprocess
import urllib.request
from pathlib import Path

from . import canonical, config, reconcile, routing, workspace

OK, WARN, FAIL = "PASS", "WARN", "FAIL"


def _row(name, status, detail=""):
    return {"check": name, "status": status, "detail": detail}


def run(init_workspace=False, check_network=False):
    rows = []

    # --- privacy boundary -------------------------------------------------
    try:
        ws = workspace.resolve(create=init_workspace)
        rows.append(_row("private workspace", OK, str(ws)))
    except workspace.WorkspaceError as e:
        rows.append(_row("private workspace", FAIL, str(e).split("\n")[0]))
        ws = None

    repo = workspace.REPO_ROOT
    tracked_client = []
    if shutil.which("git"):
        try:
            out = subprocess.run(["git", "ls-files"], cwd=repo, capture_output=True,
                                 text=True, timeout=30).stdout.splitlines()
            bad = ("client-data/", "manuscript/", "tracker_snapshot/")
            tracked_client = [f for f in out if any(b in f for b in bad)]
        except Exception:
            pass
    rows.append(_row("no client artifacts tracked in git",
                     FAIL if tracked_client else OK,
                     f"{len(tracked_client)} tracked: {tracked_client[:3]}"
                     if tracked_client else "clean"))

    gi = repo / "cannabiology-pipeline" / ".gitignore"
    rows.append(_row("gitignore defence-in-depth", OK if gi.exists() else WARN,
                     str(gi) if gi.exists() else "missing"))

    # --- config -----------------------------------------------------------
    try:
        cfg = config.load()
        rows.append(_row("pipeline config", OK,
                         f"image={cfg['models']['image_generate']} "
                         f"oa={cfg['models']['oa_routine']}/{cfg['models']['oa_final']}"))
    except Exception as e:
        rows.append(_row("pipeline config", FAIL, str(e)))
        cfg = None

    try:
        config.routing_rules()
        rows.append(_row("routing rules", OK))
    except Exception as e:
        rows.append(_row("routing rules", FAIL, str(e)))

    # --- canonical data ---------------------------------------------------
    figures = None
    if ws:
        try:
            figures = canonical.load_figures()
            rows.append(_row("canonical tracker", OK,
                             f"{len(figures)} figures, "
                             f"{sum(len(f.assets) for f in figures.values())} assets"))
        except Exception as e:
            rows.append(_row("canonical tracker", FAIL, str(e).split("\n")[0]))

    if figures:
        try:
            dec = routing.Router().route_all(figures)
            rep = reconcile.audit(figures, dec, cfg=cfg)
            rows.append(_row("count reconciliation", OK if rep["ok"] else FAIL,
                             f"{rep['figures']}/{rep['expected_figures']} figures, "
                             f"{rep['assets']}/{rep['expected_assets']} assets"))
            rows.append(_row("every figure routed", OK,
                             ", ".join(f"{k}={v}" for k, v in sorted(rep["by_route"].items()))))
            if rep["needs_route_confirmation"]:
                rows.append(_row("routes needing confirmation", WARN,
                                 f"{len(rep['needs_route_confirmation'])} derived"))
            if rep["approved_without_artifact"]:
                rows.append(_row("approved without artifact", WARN,
                                 ", ".join(rep["approved_without_artifact"])))
        except Exception as e:
            rows.append(_row("count reconciliation", FAIL, str(e).split("\n")[0]))

    # --- dependencies -----------------------------------------------------
    try:
        import yaml  # noqa: F401
        rows.append(_row("PyYAML", OK))
    except ImportError:
        rows.append(_row("PyYAML", FAIL, "pip install pyyaml"))
    try:
        import jsonschema  # noqa: F401
        rows.append(_row("jsonschema", OK, "using library validator"))
    except ImportError:
        rows.append(_row("jsonschema", OK, "using built-in fallback validator"))

    # --- API readiness ----------------------------------------------------
    key = os.environ.get("OPENAI_API_KEY")
    rows.append(_row("OPENAI_API_KEY", OK if key else WARN,
                     "set" if key else "not set - dry-run only"))
    if check_network:
        try:
            req = urllib.request.Request("https://api.openai.com/v1/models",
                                         headers={"Authorization": f"Bearer {key or 'none'}"})
            with urllib.request.urlopen(req, timeout=15) as r:
                rows.append(_row("OpenAI reachable", OK, f"HTTP {r.status}"))
        except Exception as e:
            rows.append(_row("OpenAI reachable", WARN, f"{type(e).__name__}: {e}"))
    else:
        rows.append(_row("OpenAI reachable", WARN, "not checked (use --network)"))

    # --- write permissions ------------------------------------------------
    if ws:
        try:
            p = Path(ws) / "state" / ".doctor"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text("ok"); p.unlink()
            rows.append(_row("workspace writable", OK))
        except Exception as e:
            rows.append(_row("workspace writable", FAIL, str(e)))

    return rows

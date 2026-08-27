"""Shared state, paths and tracker access for the Cannabiology figure pipeline.

The recovered Drive tracker CSVs are treated as READ-ONLY source of truth.
All mutable production state lives in production-state.json so a re-import of
the canonical tracker can never be clobbered by pipeline activity.
"""
import csv, json, os, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CLIENT = os.path.join(ROOT, "client-data")
MASTER = os.path.join(CLIENT, "00-master-control")
TESTS = os.path.join(CLIENT, "01-generated-figure-tests")
APPROVED = os.path.join(CLIENT, "02-approved-base-art")
PACKETS = os.path.join(CLIENT, "03-manny-review-packets")
LOGS = os.path.join(CLIENT, "logs")
STATE_PATH = os.path.join(MASTER, "production-state.json")
LOG_PATH = os.path.join(LOGS, "production-log.csv")

STAGES = [
    "QUEUED", "PROMPT_READY", "GENERATED_DRAFT", "OA_REVIEW_1", "REVISION_NEEDED",
    "REGENERATED", "OA_REVIEW_2", "APPROVED_FOR_MANNY", "PRESENTED_TO_MANNY",
    "MANNY_REVISION_REQUESTED", "FINAL_APPROVED", "BLOCKED",
]

# Figures named as the visual-system test comps in the existing Drive production order.
PRIORITY_COMPS = ["CH01-IMG-01", "CH02-IMG-02", "CH03-IMG-03", "CH04-IMG-05"]


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_config():
    for name in ("config.json", "config.example.json"):
        p = os.path.join(HERE, name)
        if os.path.exists(p):
            with open(p) as f:
                cfg = json.load(f)
            cfg["_source"] = name
            return cfg
    raise SystemExit("No config found in pipeline/")


def load_rubric():
    with open(os.path.join(HERE, "rubric.json")) as f:
        return json.load(f)


def load_tracker():
    """Canonical 51-figure master tracker, read-only."""
    p = os.path.join(MASTER, "master-figure-tracker.csv")
    if not os.path.exists(p):
        raise SystemExit(
            "master-figure-tracker.csv not found.\n"
            "Client data is not in git by design (this repo is public).\n"
            "Re-import the canonical master figure tracker from the project's\n"
            "Google Drive folder '00 Master Control' into client-data/."
        )
    with open(p) as f:
        return list(csv.DictReader(f))


def load_prompts():
    """52-asset production prompt library, read-only. Keyed by Production Asset ID."""
    p = os.path.join(MASTER, "prompt-library.csv")
    with open(p) as f:
        return {r["Production Asset ID"]: r for r in csv.DictReader(f)}


def route_of(status):
    """The tracker's Current Status column encodes the production route.

    GENERATE     -> image-generation pipeline (this tool)
    VECTOR-BUILD -> built by hand in Illustrator/Canva; never image-generated
    DATA-DRIVEN  -> requires a verified dataset before anything is drawn
    HOLD         -> blocked on an open Manny/Emanuel decision
    UNROUTED     -> prompt exists but no route assigned yet (Ch5-8)
    """
    u = (status or "").upper()
    if u.startswith("HOLD"):
        return "HOLD"
    if "DATA-DRIVEN" in u:
        return "DATA-DRIVEN"
    if "VECTOR-BUILD" in u:
        return "VECTOR-BUILD"
    if (u.startswith("GENERATE") or "GENERATED TEST" in u
            or "GENERATED STYLE" in u or "PRODUCTION-READY BASE ART" in u):
        return "GENERATE"
    return "UNROUTED"


def priority_of(row):
    """Lower sorts first. Encodes the documented priority strategy."""
    fid, ch = row["Figure ID"], row["Chapter"]
    route = route_of(row["Current Status"])
    if route != "GENERATE":
        base = {"VECTOR-BUILD": 500, "DATA-DRIVEN": 600, "HOLD": 700, "UNROUTED": 800}[route]
        return base + int(ch.replace("Chapter ", "")) * 10
    if fid in PRIORITY_COMPS:           # visual-system test comps first
        return PRIORITY_COMPS.index(fid)
    chn = int(ch.replace("Chapter ", ""))
    if chn <= 4:                        # foundational Ch1-4
        return 100 + chn * 10 + int(fid[-2:])
    return 300 + chn * 10 + int(fid[-2:])


def build_queue():
    """Agent 1 output: the ranked production queue."""
    rows = load_tracker()
    for r in rows:
        r["_route"] = route_of(r["Current Status"])
        r["_priority"] = priority_of(r)
    rows.sort(key=lambda r: r["_priority"])
    gen = [r for r in rows if r["_route"] == "GENERATE"]
    for i, r in enumerate(gen):
        r["_batch"] = 1 if i < 8 else (2 if i < 16 else 3)
    for r in rows:
        r.setdefault("_batch", "")
    return rows


def load_state():
    if os.path.exists(STATE_PATH):
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}


def save_state(state):
    os.makedirs(MASTER, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, sort_keys=True)


def get_fig(state, asset_id):
    return state.setdefault(asset_id, {
        "asset_id": asset_id, "stage": "QUEUED", "round": 0,
        "files": [], "reviews": [], "repairs": [], "notes": [],
        "stoplight": "RED", "manny_status": "Not presented",
    })


def set_stage(state, asset_id, stage, note=""):
    if stage not in STAGES:
        raise ValueError(f"unknown stage {stage}")
    f = get_fig(state, asset_id)
    prev = f["stage"]
    f["stage"] = stage
    f["updated"] = now()
    if note:
        f["notes"].append({"at": now(), "note": note})
    log(asset_id, "stage", f"{prev} -> {stage}", note)
    return f


def log(asset_id, event, detail, extra=""):
    os.makedirs(LOGS, exist_ok=True)
    new = not os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["timestamp", "asset_id", "event", "detail", "extra"])
        w.writerow([now(), asset_id, event, detail, extra])

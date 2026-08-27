# Folder structure and file naming

```
cannabiology-pipeline/
├── pipeline/               # committed: the tool
├── docs/                   # committed: how it works
└── client-data/            # NEVER committed (this repo is public)
    ├── 00-master-control/  # canonical CSVs + production-state.json
    ├── 01-generated-figure-tests/
    ├── 02-approved-base-art/
    ├── 03-manny-review-packets/
    ├── 99-archive/
    ├── manuscript/
    └── logs/production-log.csv
```

Mirrors the existing Drive structure (`00 Master Control`, `01 Generated Figure
Tests`, `02 Approved Base Art`, `03 Cover & Support Art References`,
`99 Archive & Superseded Prompts`) so files move between disk and Drive without
renaming.

## Names

| Kind | Pattern | Example |
|------|---------|---------|
| Draft | `<ASSET>_r<N>.png` | `CH01-IMG-01_r2.png` |
| Dry-run payload | `<ASSET>_r<N>.png.request.json` | — |
| Review brief | `<ASSET>_r<N>.review-brief.json` | — |
| Approved base art | `<ASSET>_APPROVED_r<N>.png` | `CH02-IMG-02_APPROVED_r1.png` |
| Packet | `manny-review-packet-batch<N>.html` | — |

`<ASSET>` is the **Production Asset ID**, not the Figure ID. They differ where
one canonical figure ships as two pieces of base art: `CH01-IMG-02` is one
figure produced as `CH01-IMG-02A` and `CH01-IMG-02B`. This is why 51 canonical
figures require 52 generated assets.

Never overwrite a round. Rounds are the audit trail of why a figure looks the
way it does.

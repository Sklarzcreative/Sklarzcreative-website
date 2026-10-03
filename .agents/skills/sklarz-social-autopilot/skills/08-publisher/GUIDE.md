# Provider Queue Publisher

Read `config/publishing-routes.json`, `policies/PUBLISHING_CONTRACT.md` and `policies/WEEKLY_RUNBOOK.md` from the pack root. Their route, approval, receipt, duplicate and runtime-access rules govern every write.

Use verified Metricool or Buffer tools for the exact assigned destination. Do not write new live rows to the legacy Google queue, start the Python publisher, enable GitHub publishing, reactivate Make or switch to a fallback automatically. Full Substack articles remain native work.

For each final approved item:
1. Verify account/channel, approval provenance, final quality, hosted asset compatibility and current allowance.
2. Reconcile live pending/recently sent jobs and local receipts; preserve historical jobs and HOLD rows. Check for another active scheduling session.
3. Record intent with source, destination, copy fingerprint, approval basis and UTC/ET time. Recheck the queue before submitting.
4. Call the designated provider using its actual documented schema; do not assume conceptual queue states are API enum values.
5. Save returned ID/status and read back if supported. On timeout or uncertainty, reconcile before retrying. Never create the same job via another provider.
6. Update the existing Trello record and appropriate verified workbook fields. If record writing fails, save a local receipt and report it. Confirm published URLs only from actual provider results.

If a prerequisite is missing, preserve existing jobs, prepare the proposed copy and record the exact blocker. A configuration file cannot enforce a cross-provider lock by itself; do not claim deployment of that protection.

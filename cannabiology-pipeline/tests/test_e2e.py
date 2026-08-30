"""One synthetic figure through the whole loop:
route -> context -> candidate -> OA -> repair -> vector overlay -> package ->
PENDING_HUMAN_APPROVAL."""
from pathlib import Path

from base import WorkspaceTest


class TestEndToEnd(WorkspaceTest):
    def test_full_fixture_run(self):
        from cannabiology import package, state as st, runner
        figs, dec = self.load()
        fig = figs["CH01-IMG-01"]
        store = st.Store()
        rec = runner.run_asset(fig, fig.assets[0], dec["CH01-IMG-01"], store,
                               dry_run=True, no_network=True, log=lambda *a: None)
        store.save()

        self.assertEqual(rec["state"], st.PENDING_HUMAN_APPROVAL)
        self.assertTrue(rec["prompt_versions"])
        self.assertTrue(rec["candidates"])
        self.assertTrue(rec["reviews"])
        self.assertTrue(Path(rec["vector"]["composite"]).exists())
        self.assertEqual(rec["vector"]["label_count"], 3)

        items = package.collect(figs, dec, store)
        h, j = package.write(items, "test")
        self.assertTrue(Path(h).exists())
        # Client-facing packet must not leak internal production material.
        text = Path(h).read_text()
        self.assertNotIn("LAYOUT RESERVATION", text)
        self.assertNotIn("AVOID:", text)
        self.assertIn("Dry run", text)   # synthetic reviews are declared

    def test_automation_never_reaches_human_approved(self):
        from cannabiology import state as st, runner
        figs, dec = self.load()
        fig = figs["CH01-IMG-01"]
        store = st.Store()
        rec = runner.run_asset(fig, fig.assets[0], dec["CH01-IMG-01"], store,
                               dry_run=True, no_network=True, log=lambda *a: None)
        self.assertNotEqual(rec["state"], st.HUMAN_APPROVED)
        self.assertFalse(rec["human_approved"])

    def test_resume_uses_existing_state(self):
        from cannabiology import state as st, runner
        figs, dec = self.load()
        fig = figs["CH01-IMG-01"]
        store = st.Store()
        runner.run_asset(fig, fig.assets[0], dec["CH01-IMG-01"], store,
                         dry_run=True, no_network=True, log=lambda *a: None)
        store.save()
        reloaded = st.Store()
        self.assertEqual(reloaded.get("CH01-IMG-01")["state"], st.PENDING_HUMAN_APPROVAL)

    def test_context_extract_finds_manuscript_anchor(self):
        from cannabiology import context
        figs, _ = self.load()
        ctx = context.extract(figs["CH01-IMG-01"])
        self.assertTrue(ctx["source_found"])
        self.assertIn("CH01-IMG-01", ctx["source"]["figure_brief"])
        self.assertIn("widget", ctx["source"]["excerpt"].lower())

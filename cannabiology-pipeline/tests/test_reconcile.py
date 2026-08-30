from base import WorkspaceTest


class TestReconcile(WorkspaceTest):
    def test_totals_reconcile_for_fixture(self):
        from cannabiology import reconcile
        figs, dec = self.load()
        rep = reconcile.audit(figs, dec, cfg={"canonical": {
            "expected_figures": 6, "expected_assets": 7}})
        self.assertTrue(rep["ok"], rep["problems"])
        self.assertEqual(rep["figures"], 6)
        self.assertEqual(rep["assets"], 7)

    def test_mismatch_is_reported_not_ignored(self):
        from cannabiology import reconcile
        figs, dec = self.load()
        rep = reconcile.audit(figs, dec, cfg={"canonical": {
            "expected_figures": 51, "expected_assets": 52}})
        self.assertFalse(rep["ok"])
        with self.assertRaises(reconcile.ReconciliationError):
            reconcile.require_ok(rep)

    def test_every_figure_is_routed(self):
        from cannabiology import reconcile
        figs, dec = self.load()
        rep = reconcile.audit(figs, dec, cfg={"canonical": {
            "expected_figures": 6, "expected_assets": 7}})
        self.assertEqual(sum(rep["by_route"].values()), len(figs))

    def test_manuscript_reference_not_in_tracker_is_flagged(self):
        from cannabiology import reconcile
        figs, dec = self.load()
        rep = reconcile.audit(figs, dec, manuscript_texts=["see CH09-IMG-04 here"],
                              cfg={"canonical": {"expected_figures": 6,
                                                 "expected_assets": 7}})
        self.assertIn("CH09-IMG-04", rep["referenced_in_manuscript_not_in_tracker"])

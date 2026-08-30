"""Canonical figure IDs are embedded across the project and must never change."""
from base import WorkspaceTest


class TestIdentity(WorkspaceTest):
    def test_canonical_ids_preserved(self):
        figs, _ = self.load()
        for fid in ("CH01-IMG-01", "CH01-IMG-02", "CH02-IMG-01"):
            self.assertIn(fid, figs)

    def test_sub_assets_extend_parent_id(self):
        figs, _ = self.load()
        ids = [a["asset_id"] for a in figs["CH01-IMG-02"].assets]
        self.assertEqual(sorted(ids), ["CH01-IMG-02A", "CH01-IMG-02B"])
        for aid in ids:
            self.assertTrue(aid.startswith("CH01-IMG-02"))

    def test_rejects_renamed_id_scheme(self):
        from cannabiology import canonical
        with self.assertRaises(canonical.CanonicalError):
            canonical.validate_figure_id("CBIO_C01_F001")

    def test_rejects_orphan_asset(self):
        from cannabiology import canonical
        with self.assertRaises(canonical.CanonicalError):
            canonical.validate_asset_id("CH09-IMG-01A", "CH01-IMG-02")

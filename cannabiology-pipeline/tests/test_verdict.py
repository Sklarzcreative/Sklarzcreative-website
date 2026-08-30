"""A model may never talk its way past the deterministic verdict engine."""
from base import WorkspaceTest


def review(issues=None, **kw):
    base = {"figure_id": "CH01-IMG-01", "candidate_id": "v001", "confidence": 0.9,
            "issues": issues or [], "preserve": [], "visual_pass": True,
            "scientific_pass": True, "recommended_action": "NONE"}
    base.update(kw)
    return base


def issue(cat, sev="MAJOR", repair="IMAGE_EDIT"):
    return {"category": cat, "severity": sev, "description": f"{cat} problem",
            "repair_type": repair}


class TestVerdict(WorkspaceTest):
    def test_clean_review_is_ready(self):
        from cannabiology import verdict as V
        v, _why, _c = V.compute(review(), "HYBRID")
        self.assertEqual(v, V.PRODUCTION_READY_BASE_ART)

    def test_major_issue_prevents_approval(self):
        from cannabiology import verdict as V
        v, _w, _c = V.compute(review([issue("COMPOSITION")]), "HYBRID")
        self.assertNotEqual(v, V.PRODUCTION_READY_BASE_ART)

    def test_model_cannot_self_approve_with_blockers(self):
        from cannabiology import verdict as V
        r = review([issue("COMPOSITION", "BLOCKER")],
                   recommended_action="NONE", scientific_pass=True, visual_pass=True)
        v, _w, _c = V.compute(r, "HYBRID")
        self.assertEqual(v, V.REQUIRES_CORRECTION)

    def test_fabricated_chart_data_is_rejected(self):
        from cannabiology import verdict as V
        v, _w, _c = V.compute(review([issue("EMPIRICAL_DATA", "MAJOR")]), "HYBRID")
        self.assertEqual(v, V.REJECTED)

    def test_generated_scientific_text_is_rejected(self):
        from cannabiology import verdict as V
        v, _w, _c = V.compute(review([issue("GENERATED_TEXT", "MAJOR")]), "HYBRID")
        self.assertEqual(v, V.REJECTED)

    def test_science_finding_requires_verification_not_approval(self):
        from cannabiology import verdict as V
        v, _w, _c = V.compute(review([issue("ANATOMY", "MAJOR")]), "HYBRID")
        self.assertEqual(v, V.SCIENTIFIC_VERIFICATION_REQUIRED)

    def test_preserve_damage_blocks_approval(self):
        from cannabiology import verdict as V
        v, _w, _c = V.compute(review([issue("PRESERVE_DAMAGE", "MAJOR")]), "HYBRID")
        self.assertNotEqual(v, V.PRODUCTION_READY_BASE_ART)

    def test_non_generative_route_cannot_be_approved_by_image_review(self):
        from cannabiology import verdict as V
        v, _w, _c = V.compute(review(), "DATA_DRIVEN")
        self.assertEqual(v, V.HUMAN_CONFIRMATION_REQUIRED)

    def test_repair_cap_rejects(self):
        from cannabiology import config, verdict as V
        cap = config.load()["pipeline"]["max_generative_repairs"]
        v, _w, _c = V.compute(review([issue("COMPOSITION")]), "HYBRID", repair_count=cap)
        self.assertEqual(v, V.REJECTED)

    def test_invalid_review_output_is_refused(self):
        from cannabiology import schema
        s = schema.load_schema("oa_review.schema.json")
        bad = review([{"category": "NOT_A_CATEGORY", "severity": "MAJOR",
                       "description": "x", "repair_type": "IMAGE_EDIT"}])
        with self.assertRaises(schema.ValidationError):
            schema.validate(bad, s)

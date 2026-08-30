from base import WorkspaceTest
from test_verdict import issue, review


class TestRepair(WorkspaceTest):
    def _rec(self, reps=0):
        return {"generative_repairs": reps, "vector_edits": 0}

    def test_label_only_error_is_a_vector_edit(self):
        from cannabiology import repair, verdict as V
        r = review([issue("LABEL_READINESS", "MAJOR", "VECTOR_EDIT")])
        plan = repair.plan(r, V.REQUIRES_CORRECTION, self._rec())
        self.assertEqual(plan["action"], repair.VECTOR_EDIT)

    def test_vector_edit_does_not_consume_a_generative_round(self):
        from cannabiology import repair, verdict as V
        r = review([issue("LABEL_READINESS", "MAJOR", "VECTOR_EDIT")])
        plan = repair.plan(r, V.REQUIRES_CORRECTION, self._rec())
        self.assertFalse(plan["consumes_generative_round"])

    def test_local_art_error_is_an_image_edit(self):
        from cannabiology import repair, verdict as V
        r = review([issue("CLUTTER", "MAJOR", "IMAGE_EDIT")])
        plan = repair.plan(r, V.REQUIRES_CORRECTION, self._rec())
        self.assertEqual(plan["action"], repair.IMAGE_EDIT)
        self.assertTrue(plan["consumes_generative_round"])

    def test_structural_failure_regenerates(self):
        from cannabiology import repair, verdict as V
        r = review([issue("ANATOMY", "BLOCKER", "REGENERATE")])
        plan = repair.plan(r, V.REQUIRES_CORRECTION, self._rec())
        self.assertEqual(plan["action"], repair.REGENERATE)

    def test_cap_escalates_to_human(self):
        from cannabiology import config, repair, verdict as V
        cap = config.load()["pipeline"]["max_generative_repairs"]
        r = review([issue("CLUTTER", "MAJOR", "IMAGE_EDIT")])
        plan = repair.plan(r, V.REQUIRES_CORRECTION, self._rec(cap))
        self.assertEqual(plan["action"], repair.HUMAN_CONFIRMATION)

    def test_repair_prompt_restates_preserve(self):
        from cannabiology import repair, verdict as V
        r = review([issue("CLUTTER", "MAJOR", "IMAGE_EDIT")],
                   preserve=["the dominant central vacuole", "off-white background"])
        plan = repair.plan(r, V.REQUIRES_CORRECTION, self._rec())
        text = repair.build_repair_prompt("BASE PROMPT", plan)
        self.assertIn("PRESERVE EXACTLY", text)
        self.assertIn("dominant central vacuole", text)
        self.assertIn("off-white background", text)

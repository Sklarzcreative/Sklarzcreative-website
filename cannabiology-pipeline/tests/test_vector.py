from pathlib import Path

from base import WorkspaceTest


class TestVector(WorkspaceTest):
    def test_labels_fixed_without_touching_base_image(self):
        from cannabiology import vector, workspace
        run = workspace.resolve() / "runs" / "T" / "run_x"
        base = run / "candidates"
        base.mkdir(parents=True, exist_ok=True)
        img = base / "CH01-IMG-01_v001.png"
        img.write_bytes(b"\x89PNG\r\n\x1a\nSYNTHETIC")
        before = img.read_bytes()
        v1, _m1 = vector.write_layer(run, "CH01-IMG-01", ["prat a"], 800, 600)
        v2, _m2 = vector.write_layer(run, "CH01-IMG-01", ["part a"], 800, 600)
        self.assertNotEqual(Path(v1).read_text(), Path(v2).read_text())
        self.assertIn("part a", Path(v2).read_text())
        self.assertEqual(img.read_bytes(), before)   # base art untouched

    def test_composite_preserves_dimensions(self):
        from cannabiology import vector
        layer = vector.build_layer(["a", "b"], 1536, 1024)
        comp = vector.composite("/nonexistent.png", layer, 1536, 1024)
        self.assertIn('width="1536"', comp)
        self.assertIn('height="1024"', comp)

    def test_output_is_deterministic(self):
        from cannabiology import vector
        a = vector.build_layer(["x", "y"], 800, 600)
        b = vector.build_layer(["x", "y"], 800, 600)
        self.assertEqual(a, b)

    def test_label_text_is_escaped(self):
        from cannabiology import vector
        svg = vector.build_layer(["A & B <tag>"], 800, 600)
        self.assertIn("&amp;", svg)
        self.assertNotIn("<tag>", svg)

    def test_manifest_records_no_authoritative_text_in_base_art(self):
        import json
        from cannabiology import vector, workspace
        run = workspace.resolve() / "runs" / "T2" / "run_y"
        _svg, man = vector.write_layer(run, "CH01-IMG-01", ["a", "b", "c"], 800, 600)
        data = json.loads(Path(man).read_text())
        self.assertFalse(data["authoritative_text_in_base_art"])
        self.assertEqual(data["label_count"], 3)

"""Deterministic builders: nothing draws without a cited source.

Fixtures use benzene and cyclohexane - molecules whose formulas are trivially
checkable - so the test proves the machinery, not any client chemistry.
"""
import unittest

from base import WorkspaceTest

REG = {
    "benzene": {
        "display_name": "Benzene", "smiles": "c1ccccc1",
        "molecular_formula": "C6H6", "source": "TEST-FIXTURE",
        "source_id": "fixture-1", "retrieved": "2026-08-27", "verified": True,
    },
    "cyclohexane": {
        "display_name": "Cyclohexane", "smiles": "C1CCCCC1",
        "molecular_formula": "C6H12", "source": "TEST-FIXTURE",
        "source_id": "fixture-2", "retrieved": "2026-08-27", "verified": True,
    },
    "unverified": {
        "display_name": "Unverified", "smiles": "c1ccccc1",
        "molecular_formula": "C6H6", "source": "TEST-FIXTURE",
        "source_id": "fixture-3", "retrieved": "2026-08-27", "verified": False,
    },
    "mismatched": {
        "display_name": "Mismatched", "smiles": "c1ccccc1",
        "molecular_formula": "C99H99", "source": "TEST-FIXTURE",
        "source_id": "fixture-4", "retrieved": "2026-08-27", "verified": True,
    },
    "no_provenance": {
        "display_name": "No provenance", "smiles": "c1ccccc1",
        "molecular_formula": "C6H6", "verified": True,
    },
}

try:
    import rdkit  # noqa: F401
    HAS_RDKIT = True
except ImportError:
    HAS_RDKIT = False


@unittest.skipUnless(HAS_RDKIT, "rdkit not installed")
class TestChem(WorkspaceTest):
    def test_unknown_compound_refuses_to_draw(self):
        from cannabiology.builders import chem
        with self.assertRaises(chem.UnverifiedCompound):
            chem.render("thca", REG)

    def test_unverified_compound_refuses_to_draw(self):
        from cannabiology.builders import chem
        with self.assertRaises(chem.UnverifiedCompound):
            chem.render("unverified", REG)

    def test_missing_provenance_refuses_to_draw(self):
        from cannabiology.builders import chem
        with self.assertRaises(chem.UnverifiedCompound):
            chem.render("no_provenance", REG)

    def test_formula_mismatch_is_caught(self):
        """A transcription slip changes the formula and must be rejected."""
        from cannabiology.builders import chem
        with self.assertRaises(chem.ChemistryError):
            chem.render("mismatched", REG)

    def test_verified_compound_renders_svg(self):
        from cannabiology.builders import chem
        svg, prov = chem.render("benzene", REG)
        self.assertIn("<svg", svg)
        self.assertEqual(prov["molecular_formula"], "C6H6")
        self.assertEqual(prov["source_id"], "fixture-1")

    def test_render_is_deterministic(self):
        from cannabiology.builders import chem
        a, _ = chem.render("benzene", REG)
        b, _ = chem.render("benzene", REG)
        self.assertEqual(a, b)

    def test_panel_carries_a_citation_per_compound(self):
        from cannabiology.builders import chem
        svg, provs = chem.render_panel(["benzene", "cyclohexane"], REG)
        self.assertIn("<svg", svg)
        self.assertEqual(len(provs), 2)
        for p in provs:
            self.assertTrue(p["source"] and p["source_id"])

    def test_output_is_vector_not_raster(self):
        from cannabiology.builders import chem
        svg, _ = chem.render("benzene", REG)
        self.assertIn("<path", svg)
        self.assertNotIn("<image", svg)


SPEC = {
    "figure_id": "CH01-IMG-04", "confirmed": True, "source": "TEST-FIXTURE",
    "nodes": [{"id": "a", "label": "Input", "column": 0, "row": 0},
              {"id": "b", "label": "Step", "column": 1, "row": 0,
               "emphasis": "primary"},
              {"id": "c", "label": "Output", "column": 2, "row": 0}],
    "edges": [{"from": "a", "to": "b", "label": "one"},
              {"from": "b", "to": "c"}],
}


class TestDiagram(WorkspaceTest):
    def _write(self, spec, name="CH01-IMG-04.yaml"):
        import yaml
        from cannabiology import workspace
        d = workspace.resolve() / "canonical" / "diagram_specs"
        d.mkdir(parents=True, exist_ok=True)
        p = d / name
        p.write_text(yaml.safe_dump(spec))
        return p

    def test_missing_spec_refuses(self):
        from cannabiology.builders import diagram
        from cannabiology import workspace
        with self.assertRaises(diagram.UnconfirmedSpec):
            diagram.load_spec(workspace.resolve() / "canonical" / "nope.yaml")

    def test_unconfirmed_spec_refuses(self):
        from cannabiology.builders import diagram
        spec = dict(SPEC, confirmed=False)
        with self.assertRaises(diagram.UnconfirmedSpec):
            diagram.load_spec(self._write(spec))

    def test_confirmed_spec_builds(self):
        from cannabiology.builders import diagram
        svg = diagram.build(diagram.load_spec(self._write(SPEC)))
        self.assertIn("<svg", svg)
        self.assertIn("Input", svg)
        self.assertIn("Output", svg)

    def test_edge_to_unknown_node_is_an_error(self):
        from cannabiology.builders import diagram
        spec = dict(SPEC, edges=[{"from": "a", "to": "ghost"}])
        with self.assertRaises(diagram.DiagramError):
            diagram.build(spec)

    def test_build_is_deterministic(self):
        from cannabiology.builders import diagram
        s = diagram.load_spec(self._write(SPEC))
        self.assertEqual(diagram.build(s), diagram.build(s))

    def test_labels_are_escaped(self):
        from cannabiology.builders import diagram
        spec = dict(SPEC, nodes=[{"id": "a", "label": "A & <b>", "column": 0}],
                    edges=[])
        svg = diagram.build(spec)
        self.assertIn("&amp;", svg)
        self.assertNotIn("<b>", svg)


class TestVectorBuildRoute(WorkspaceTest):
    def test_generative_figure_rejected_by_build(self):
        from cannabiology import state as st, vectorbuild
        figs, dec = self.load()
        fig = figs["CH01-IMG-01"]          # HYBRID, not VECTOR_BUILD
        with self.assertRaises(RuntimeError):
            vectorbuild.run_asset(fig, fig.assets[0], dec["CH01-IMG-01"],
                                  st.Store(), log=lambda *a: None)

    def test_vector_figure_without_spec_fails_closed(self):
        from cannabiology import state as st, vectorbuild
        figs, dec = self.load()
        fig = figs["CH02-IMG-01"]          # VECTOR_BUILD in the fixture
        with self.assertRaises(vectorbuild.BuildSpecMissing):
            vectorbuild.run_asset(fig, fig.assets[0], dec["CH02-IMG-01"],
                                  st.Store(), log=lambda *a: None)


class TestLabelCoverage(WorkspaceTest):
    """A built diagram prints its own text; a generated image prints none.
    The overlay must reflect that instead of blindly stacking every label."""

    def test_labels_already_in_artwork_are_not_overlaid(self):
        from cannabiology.vectorbuild import label_coverage
        covered, missing = label_coverage(
            ["cannabinoids", "terpenes"], ["Cannabinoids", "Terpenes"])
        self.assertEqual(covered, ["cannabinoids", "terpenes"])
        self.assertEqual(missing, [])

    def test_labels_absent_from_artwork_are_overlaid(self):
        from cannabiology.vectorbuild import label_coverage
        covered, missing = label_coverage(
            ["cannabinoids", "scale bar"], ["Cannabinoids"])
        self.assertEqual(covered, ["cannabinoids"])
        self.assertEqual(missing, ["scale bar"])

    def test_generated_art_prints_nothing_so_all_labels_overlay(self):
        from cannabiology.vectorbuild import label_coverage
        covered, missing = label_coverage(["nucleus", "cell wall"], [])
        self.assertEqual(covered, [])
        self.assertEqual(missing, ["nucleus", "cell wall"])

    def test_matching_tolerates_spelling_and_punctuation(self):
        from cannabiology.vectorbuild import label_coverage
        covered, _ = label_coverage(
            ["ecological defense/stress response"],
            ["Ecological defence and stress response"])
        self.assertEqual(len(covered), 1)

    def test_multiplication_sign_matches_plain_x(self):
        """The tracker writes 'genotype x environment' with U+00D7."""
        from cannabiology.vectorbuild import label_coverage
        covered, missing = label_coverage(
            ["genotype \u00d7 environment"], ["genotype x environment"])
        self.assertEqual(len(covered), 1)
        self.assertEqual(missing, [])

    def test_partial_label_inside_a_longer_node_still_counts(self):
        from cannabiology.vectorbuild import label_coverage
        covered, _ = label_coverage(
            ["carbohydrates"], ["Carbohydrates (glucose, starch, cellulose)"])
        self.assertEqual(covered, ["carbohydrates"])


class TestCaptionLayout(WorkspaceTest):
    CAPTION = ("Emphasize resource allocation and the dependence of specialized "
               "metabolism on primary metabolic energy and precursors.")

    def test_caption_is_never_truncated(self):
        """The old layer cut the caption mid-word at 110 characters."""
        from cannabiology import vector
        svg = vector.build_layer([], 1500, 820, caption=self.CAPTION,
                                 footer_top=742)
        self.assertIn("precursors.", svg)
        self.assertNotIn("and pre<", svg)

    def test_caption_wraps_when_the_figure_is_narrow(self):
        from cannabiology import vector
        svg = vector.build_layer([], 600, 500, caption=self.CAPTION,
                                 footer_top=400)
        self.assertGreaterEqual(svg.count('font-size="12"'), 2)
        self.assertIn("precursors.", svg)

    def test_footer_top_keeps_caption_clear_of_artwork_footer(self):
        from cannabiology import vector
        import re
        svg = vector.build_layer([], 1500, 820, figure_number="CH01-IMG-04",
                                 caption="Short caption.", footer_top=742)
        ys = [int(y) for y in re.findall(r'<text x="24" y="(\d+)"', svg)]
        self.assertTrue(all(y < 804 for y in ys),
                        f"annotation footer must clear the artwork's line at 804: {ys}")

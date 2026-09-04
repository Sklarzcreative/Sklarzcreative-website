"""Deterministic builders: nothing draws without a cited source.

Fixtures use benzene and cyclohexane - molecules whose formulas are trivially
checkable - so the test proves the machinery, not any client chemistry.
"""
import copy
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


class TestProvenanceRecord(WorkspaceTest):
    def test_provenance_records_the_label_decision(self):
        """The record is written last so it captures what was actually decided."""
        import json
        from pathlib import Path
        import yaml
        from cannabiology import state as st, vectorbuild, workspace

        spec = {"figure_id": "CH01-IMG-01", "confirmed": True, "source": "FIXTURE",
                "nodes": [{"id": "a", "label": "part a", "column": 0},
                          {"id": "b", "label": "part b", "column": 1}],
                "edges": [{"from": "a", "to": "b"}]}
        d = workspace.resolve() / "canonical" / "diagram_specs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "CH01-IMG-01.yaml").write_text(yaml.safe_dump(spec))
        b = workspace.resolve() / "canonical" / "build_specs"
        b.mkdir(parents=True, exist_ok=True)
        (b / "CH01-IMG-01.yaml").write_text(yaml.safe_dump({"builder": "diagram"}))

        figs, dec = self.load()
        fig = figs["CH01-IMG-01"]
        # fixture routes CH01-IMG-01 HYBRID; force the build lane for this test
        dec["CH01-IMG-01"].route = "VECTOR_BUILD"
        rec = vectorbuild.run_asset(fig, fig.assets[0], dec["CH01-IMG-01"],
                                    st.Store(), log=lambda *a: None)
        prov = json.loads(Path(rec["vector"]["provenance"]).read_text())
        for key in ("labels_required", "labels_already_in_artwork", "labels_overlaid"):
            self.assertIn(key, prov, f"{key} missing from the provenance record")
        self.assertEqual(sorted(prov["labels_already_in_artwork"]),
                         ["part a", "part b"])
        self.assertEqual(prov["labels_overlaid"], ["part c"])


class TestAutopilotSafety(WorkspaceTest):
    """Autopilot removes the interruption, not the gate."""

    def _pending(self, reviews=None, state=None):
        from cannabiology import state as st
        store = st.Store()
        rec = store.get("CH01-IMG-01")
        rec["state"] = state or st.PENDING_HUMAN_APPROVAL
        rec["reviews"] = reviews or []
        return store, rec

    def test_dry_run_review_is_never_batch_approvable(self):
        """A synthetic review must not be mistaken for scientific review."""
        from cannabiology import autopilot
        store, rec = self._pending([{"verdict": "PRODUCTION_READY_BASE_ART",
                                     "synthetic": True, "counts": {}}])
        reasons = autopilot.flag_reasons(rec)
        self.assertTrue(any("dry-run" in r for r in reasons))
        clear, flagged = autopilot.approvable(store)
        self.assertIn("CH01-IMG-01", flagged)
        self.assertNotIn("CH01-IMG-01", clear)

    def test_major_findings_are_flagged(self):
        from cannabiology import autopilot
        _store, rec = self._pending([{"verdict": "PRODUCTION_READY_BASE_ART",
                                      "counts": {"majors": 2}}])
        self.assertTrue(any("major" in r for r in autopilot.flag_reasons(rec)))

    def test_preserve_damage_is_flagged(self):
        from cannabiology import autopilot
        _store, rec = self._pending([{"verdict": "PRODUCTION_READY_BASE_ART",
                                      "counts": {"preserve_damage": 1}}])
        self.assertTrue(any("preserved" in r for r in autopilot.flag_reasons(rec)))

    def test_clean_real_review_is_approvable(self):
        from cannabiology import autopilot
        store, _rec = self._pending([{"verdict": "PRODUCTION_READY_BASE_ART",
                                      "synthetic": False, "counts": {}}])
        clear, flagged = autopilot.approvable(store)
        self.assertIn("CH01-IMG-01", clear)
        self.assertEqual(flagged, [])

    def test_figure_not_awaiting_approval_is_never_swept_up(self):
        from cannabiology import autopilot, state as st
        store, _rec = self._pending([], state=st.OA_REVIEW)
        clear, flagged = autopilot.approvable(store)
        self.assertEqual(clear, [])
        self.assertEqual(flagged, [])

    def test_exclude_holds_a_figure_back(self):
        from cannabiology import autopilot
        store, _rec = self._pending([{"verdict": "PRODUCTION_READY_BASE_ART",
                                      "counts": {}}])
        clear, _f = autopilot.approvable(store, exclude={"CH01-IMG-01"})
        self.assertEqual(clear, [])

    def test_blocked_routes_are_reported_not_run(self):
        from cannabiology import autopilot, state as st
        figs, dec = self.load()
        store = st.Store()
        results = autopilot.run_all(figs, dec, store, dry_run=True,
                                    no_network=True, log=lambda *a: None)
        by_id = {r["figure_id"]: r for r in results}
        for fid in ("CH02-IMG-02", "CH03-IMG-01"):   # DATA_DRIVEN and HOLD in fixture
            self.assertEqual(by_id[fid]["outcome"], autopilot.SKIPPED)
            self.assertNotIn("completed", by_id[fid]["detail"])

    def test_one_failure_does_not_stop_the_run(self):
        from cannabiology import autopilot, state as st
        figs, dec = self.load()
        # CH01-IMG-01 is HYBRID and will run; CH04-IMG-01 is a derived route
        results = autopilot.run_all(figs, dec, st.Store(), dry_run=True,
                                    no_network=True, log=lambda *a: None)
        self.assertGreater(len(results), 1)
        self.assertTrue(any(r["outcome"] == autopilot.COMPLETED for r in results))


SPECS = {
    "flow": {"nodes": [{"id": "a", "label": "One", "column": 0},
                       {"id": "b", "label": "Two", "column": 1}],
             "edges": [{"from": "a", "to": "b", "label": "then"}],
             "bands": [{"x": 10, "y": 10, "width": 100, "height": 100,
                        "label": "a band"}]},
    "lanes": {"nodes": [{"id": "a", "label": "Screen", "lane": "Traditional", "step": 0},
                        {"id": "b", "label": "Grow", "lane": "Traditional", "step": 1},
                        {"id": "c", "label": "Genotype", "lane": "Marker-assisted", "step": 0}]},
    "timeline": {"nodes": [{"id": "a", "date": "1000 CE", "label": "Hashish"},
                           {"id": "b", "date": "1970", "label": "Solvent"},
                           {"id": "c", "date": "2026", "label": "Supercritical"}]},
    "pyramid": {"nodes": [{"id": "a", "tier": 0, "label": "Systematic reviews"},
                          {"id": "b", "tier": 1, "label": "Randomised trials"},
                          {"id": "c", "tier": 2, "label": "Case reports", "note": "weakest"}]},
    "layers": {"nodes": [{"id": "a", "layer": 0, "label": "Genome"},
                         {"id": "b", "layer": 1, "label": "Transcriptome", "note": "RNA"},
                         {"id": "c", "layer": 2, "label": "Metabolome"}]},
    "hub": {"nodes": [{"id": "h", "label": "Cannabiology", "hub": True},
                      {"id": "a", "label": "Genomics"},
                      {"id": "b", "label": "Chemistry"},
                      {"id": "c", "label": "Medicine"}]},
}


def _spec(layout):
    # Deep copy: these fixtures are shared, and a test that mutates a node
    # would otherwise corrupt every later test in the file.
    s = copy.deepcopy(SPECS[layout])
    s.update({"figure_id": "CH01-IMG-01", "confirmed": True,
              "source": "FIXTURE", "layout": layout})
    return s


class TestLayouts(WorkspaceTest):
    def test_every_layout_renders(self):
        from cannabiology.builders import diagram
        for layout in ("flow", "lanes", "timeline", "pyramid", "layers", "hub"):
            svg = diagram.build(_spec(layout), 1200, 700)
            self.assertTrue(svg.startswith("<svg"), layout)
            self.assertTrue(svg.rstrip().endswith("</svg>"), layout)

    def test_every_layout_is_deterministic(self):
        from cannabiology.builders import diagram
        for layout in SPECS:
            a = diagram.build(_spec(layout), 1200, 700)
            b = diagram.build(_spec(layout), 1200, 700)
            self.assertEqual(a, b, layout)

    def test_every_layout_shows_its_content(self):
        from cannabiology.builders import diagram
        checks = {"flow": "One", "lanes": "Traditional", "timeline": "1000 CE",
                  "pyramid": "Randomised trials", "layers": "Transcriptome",
                  "hub": "Cannabiology"}
        for layout, needle in checks.items():
            self.assertIn(needle, diagram.build(_spec(layout), 1200, 700), layout)

    def test_every_layout_escapes_text(self):
        from cannabiology.builders import diagram
        for layout in SPECS:
            s = _spec(layout)
            s["nodes"][-1]["label"] = "A & <b>"
            svg = diagram.build(s, 1200, 700)
            self.assertIn("&amp;", svg, layout)
            self.assertNotIn("<b>", svg, layout)

    def test_unknown_layout_is_refused(self):
        from cannabiology.builders import diagram
        s = _spec("flow"); s["layout"] = "spiral"
        with self.assertRaises(diagram.DiagramError):
            diagram.build(s, 1200, 700)

    def test_layout_missing_required_node_field_is_refused(self):
        from cannabiology.builders import diagram
        s = _spec("timeline")
        del s["nodes"][0]["date"]
        with self.assertRaises(diagram.DiagramError):
            diagram.build(s, 1200, 700)

    def test_hub_requires_exactly_one_hub_node(self):
        from cannabiology.builders import diagram
        s = _spec("hub")
        s["nodes"][1]["hub"] = True
        with self.assertRaises(diagram.DiagramError):
            diagram.build(s, 1200, 700)

    def test_unconfirmed_spec_still_carries_the_draft_banner(self):
        from cannabiology.builders import diagram
        for layout in SPECS:
            s = _spec(layout); s["confirmed"] = False
            self.assertIn("DRAFT", diagram.build(s, 1200, 700, draft=True), layout)

    def test_flow_wraps_at_the_width_the_approved_figures_used(self):
        """Approved artwork must not reflow. 190px boxes wrap at 24 chars."""
        from cannabiology.builders import diagram
        s = _spec("flow")
        s["nodes"] = [{"id": "a", "column": 0,
                       "label": "Carbohydrates (glucose, starch, cellulose, sucrose)"}]
        s["edges"] = []
        svg = diagram.build(s, 1500, 820)
        self.assertIn("Carbohydrates (glucose,", svg)
        self.assertIn("starch, cellulose,", svg)

    def test_band_labels_keep_their_letter_spacing(self):
        from cannabiology.builders import diagram
        svg = diagram.build(_spec("flow"), 1200, 700)
        self.assertIn('letter-spacing="0.06em"', svg)

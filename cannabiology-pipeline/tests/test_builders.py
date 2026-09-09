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

    def test_british_and_american_spellings_match(self):
        """The manuscript uses American forms; a tracker label written either
        way must not read as a missing label."""
        from cannabiology.vectorbuild import label_coverage
        for required, drawn in (("sterilization", "Surface sterilisation"),
                                ("sterilisation", "Surface sterilization"),
                                ("acclimatization", "Acclimatisation and hardening")):
            covered, missing = label_coverage([required], [drawn])
            self.assertEqual(len(covered), 1, f"{required} vs {drawn}")
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
             "bands": [{"nodes": ["a"], "label": "a band"}]},
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

    def test_flow_wrap_is_pinned(self):
        """Pin the wrap so artwork does not reflow unnoticed between builds.

        Re-pinned 2026-09-08. This previously pinned the 24-character wrap of
        the 2026-09-04 approved figures, but that wrap measured ~214px inside a
        190px box and several nodes overhung their own border. The approved
        figures are being re-issued for that and other geometry defects, so the
        pin moves with them. Changing it again means artwork changes: re-render
        and look at every figure before you do.
        """
        from cannabiology.builders import diagram
        s = _spec("flow")
        s["nodes"] = [{"id": "a", "column": 0,
                       "label": "Carbohydrates (glucose, starch, cellulose, sucrose)"}]
        s["edges"] = []
        s["bands"] = []
        svg = diagram.build(s, 1500, 820)
        self.assertIn("Carbohydrates", svg)
        self.assertIn("(glucose, starch,", svg)
        self.assertIn("cellulose, sucrose)", svg)

    def test_band_labels_keep_their_letter_spacing(self):
        from cannabiology.builders import diagram
        svg = diagram.build(_spec("flow"), 1200, 700)
        self.assertIn('letter-spacing="0.06em"', svg)


class TestCaptionFits(WorkspaceTest):
    """A caption that runs off the edge is invisible damage: it renders, it
    just cannot be read. Wrapping must leave real margin."""

    CH_W = 6.4          # measured average for 12px IBM Plex Sans

    def _widest(self, svg):
        import re
        lines = re.findall(
            r'<text x="24" y="\d+" font-size="12" fill="#3d4a41">([^<]*)</text>', svg)
        return max((24 + len(l) * self.CH_W for l in lines), default=0)

    def test_long_caption_stays_inside_the_canvas(self):
        from cannabiology import vector
        cap = ("Quality control and release review are pass/fail gates: material "
               "that fails either loops back to reformulation before re-entering "
               "the sequence, and the caption must still fit within the figure "
               "rather than running off its right edge.")
        for width in (1200, 1500, 1600, 1800):
            svg = vector.build_layer([], width, 800, caption=cap, footer_top=700)
            self.assertLessEqual(self._widest(svg), width - 24,
                                 f"caption overflows at width {width}")

    def test_a_caption_too_long_for_one_line_wraps(self):
        from cannabiology import vector
        import re
        cap = "word " * 80
        svg = vector.build_layer([], 1500, 800, caption=cap, footer_top=700)
        lines = re.findall(
            r'<text x="24" y="\d+" font-size="12" fill="#3d4a41">', svg)
        self.assertGreater(len(lines), 1)


class TestRebuildGuard(WorkspaceTest):
    def _ready(self):
        import yaml
        from cannabiology import workspace
        spec = {"figure_id": "CH01-IMG-01", "confirmed": True, "source": "FIXTURE",
                "nodes": [{"id": "a", "label": "part a", "column": 0}], "edges": []}
        d = workspace.resolve() / "canonical" / "diagram_specs"
        d.mkdir(parents=True, exist_ok=True)
        (d / "CH01-IMG-01.yaml").write_text(yaml.safe_dump(spec))
        b = workspace.resolve() / "canonical" / "build_specs"
        b.mkdir(parents=True, exist_ok=True)
        (b / "CH01-IMG-01.yaml").write_text(yaml.safe_dump({"builder": "diagram"}))
        figs, dec = self.load()
        dec["CH01-IMG-01"].route = "VECTOR_BUILD"
        return figs["CH01-IMG-01"], dec["CH01-IMG-01"]

    def test_rebuild_reruns_a_pending_figure(self):
        from cannabiology import state as st, vectorbuild
        fig, d = self._ready()
        store = st.Store()
        vectorbuild.run_asset(fig, fig.assets[0], d, store, log=lambda *a: None)
        self.assertEqual(store.get("CH01-IMG-01")["state"], st.PENDING_HUMAN_APPROVAL)
        rec = vectorbuild.run_asset(fig, fig.assets[0], d, store,
                                    log=lambda *a: None, rebuild=True)
        self.assertEqual(rec["state"], st.PENDING_HUMAN_APPROVAL)

    def test_rebuild_refuses_approved_artwork(self):
        """An approval means that artwork is settled. Redrawing it silently
        would make the approval meaningless."""
        from cannabiology import state as st, vectorbuild
        fig, d = self._ready()
        store = st.Store()
        vectorbuild.run_asset(fig, fig.assets[0], d, store, log=lambda *a: None)
        store.transition("CH01-IMG-01", st.HUMAN_APPROVED, "approved")
        with self.assertRaises(RuntimeError):
            vectorbuild.run_asset(fig, fig.assets[0], d, store,
                                  log=lambda *a: None, rebuild=True)

    def test_build_without_rebuild_still_refuses_a_pending_figure(self):
        from cannabiology import state as st, vectorbuild
        fig, d = self._ready()
        store = st.Store()
        vectorbuild.run_asset(fig, fig.assets[0], d, store, log=lambda *a: None)
        with self.assertRaises(st.StateError):
            vectorbuild.run_asset(fig, fig.assets[0], d, store, log=lambda *a: None)


# One spec per layout, each exercising every text-bearing field that layout
# reads. If a layout gains a new field, add it here: the drift test below is
# only as good as the coverage of these fixtures.
LAYOUT_SPECS = {
    "flow": {"nodes": [{"id": "a", "label": "Alpha", "column": 0, "row": 0},
                       {"id": "d", "label": "Delta", "column": 0, "row": 1},
                       {"id": "e", "label": "Echo", "column": 0, "row": 2},
                       {"id": "b", "label": "Bravo", "column": 1, "row": 0}],
             "edges": [{"from": "a", "to": "b", "label": "Charlie"}],
             "bands": [{"nodes": ["a", "d", "e"], "label": "Foxtrot"}]},
    "lanes": {"nodes": [{"id": "a", "label": "Alpha", "lane": "Echo", "step": 0},
                        {"id": "b", "label": "Bravo", "lane": "Echo", "step": 1},
                        {"id": "c", "label": "Golf", "lane": "Foxtrot", "step": 0}]},
    "timeline": {"nodes": [{"id": "a", "label": "Alpha", "date": "1839"},
                           {"id": "b", "label": "Bravo", "date": "1937"}]},
    "pyramid": {"nodes": [{"id": "a", "label": "Alpha", "tier": 0, "note": "Charlie"},
                          {"id": "b", "label": "Bravo", "tier": 1}],
                "axis_label": "Delta"},
    "layers": {"nodes": [{"id": "a", "label": "Alpha", "layer": 0, "note": "Charlie"},
                         {"id": "b", "label": "Bravo", "layer": 1}]},
    "hub": {"nodes": [{"id": "a", "label": "Alpha", "hub": True},
                      {"id": "b", "label": "Bravo"}]},
}


class TestDrawnTexts(WorkspaceTest):
    """`drawn_texts` tells label coverage what the artwork already prints.

    If it under-reports, the build overlays a label on top of words the diagram
    already draws; if it over-reports, a required label silently never gets
    overlaid at all. Both are silent defects in the finished artwork, so this
    checks the two directions against the rendered SVG itself.
    """

    # The provenance stamp and the draft banner are chrome that `_close` adds
    # to every figure. They are not figure content and never need overlaying,
    # so they are excluded rather than being taught to `drawn_texts`.
    CHROME = ("Built from confirmed spec", "DRAFT - topology NOT confirmed",
              "DRAFT FOR REVIEW - TOPOLOGY NOT YET CONFIRMED")

    @classmethod
    def _svg_words(cls, svg, source):
        import re
        from html import unescape
        from cannabiology.vectorbuild import _norm
        chrome = {w for c in cls.CHROME for w in _norm(c).split()}
        chrome |= set(_norm(source).split())
        words = set()
        for body in re.findall(r"<text[^>]*>(.*?)</text>", svg, re.S):
            words.update(_norm(unescape(body)).split())
        return words - chrome

    def _render(self, layout):
        import copy
        from cannabiology.builders import diagram
        spec = copy.deepcopy(LAYOUT_SPECS[layout])
        spec.update(figure_id="CH01-IMG-04", confirmed=True,
                    source="TEST-FIXTURE", layout=layout)
        return spec, diagram.build(spec)

    def test_drawn_texts_matches_svg(self):
        from cannabiology.builders import diagram
        for layout in LAYOUT_SPECS:
            with self.subTest(layout=layout):
                spec, svg = self._render(layout)
                from cannabiology.vectorbuild import _norm
                claimed = set()
                for t in diagram.drawn_texts(spec):
                    claimed.update(_norm(t).split())
                drawn = self._svg_words(svg, spec["source"])
                self.assertTrue(drawn, f"{layout} drew no text at all")
                self.assertFalse(
                    drawn - claimed,
                    f"{layout} typesets {sorted(drawn - claimed)} but drawn_texts "
                    "omits it, so label coverage would overlay it twice")
                self.assertFalse(
                    claimed - drawn,
                    f"{layout} does not typeset {sorted(claimed - drawn)} but "
                    "drawn_texts claims it, so a required label would be dropped")

    def test_note_and_date_count_as_covered(self):
        from cannabiology import vectorbuild
        spec, _ = self._render("pyramid")
        covered, missing = vectorbuild.label_coverage(
            ["Charlie", "Delta", "Zulu"], vectorbuild_texts(spec))
        self.assertEqual(covered, ["Charlie", "Delta"])
        self.assertEqual(missing, ["Zulu"])


def vectorbuild_texts(spec):
    from cannabiology.builders import diagram
    return diagram.drawn_texts(spec)


class TestDiagramGeometry(WorkspaceTest):
    """Geometry defects that text-based review cannot see.

    Four figures reached APPROVED with text running off the canvas or printing
    underneath the caption, because every check until now compared strings and
    none measured where they land. These measure.
    """

    # Generous per-character advance, matching the builder's own reservation.
    EM = 0.66

    @staticmethod
    def _boxes(svg):
        import re
        from html import unescape
        out = []
        for m in re.finditer(
                r'<text x="([-\d.]+)" y="([-\d.]+)"([^>]*)>(.*?)</text>', svg, re.S):
            x, y, attrs, body = (float(m.group(1)), float(m.group(2)),
                                 m.group(3), unescape(m.group(4)))
            size = float((re.search(r'font-size="([\d.]+)"', attrs)
                          or [None, "13"])[1])
            anchor = (re.search(r'text-anchor="(\w+)"', attrs) or [None, "start"])[1]
            w = len(body) * size * TestDiagramGeometry.EM
            left = x - w / 2 if anchor == "middle" else (x - w if anchor == "end" else x)
            out.append({"l": left, "r": left + w, "y": y, "size": size, "text": body})
        return out

    def _spec(self, layout, **over):
        import copy
        spec = copy.deepcopy(LAYOUT_SPECS[layout])
        spec.update(figure_id="CH01-IMG-04", confirmed=True,
                    source="TEST-FIXTURE", layout=layout)
        spec.update(over)
        return spec

    def test_footer_reserve_matches_compositor(self):
        """If these drift, the caption lands on the artwork again."""
        import inspect
        from cannabiology import vectorbuild
        from cannabiology.builders import diagram
        src = inspect.getsource(vectorbuild)
        self.assertIn(f"height - {diagram.FOOTER_RESERVE}", src,
                      "vectorbuild's footer_top no longer matches "
                      "diagram.FOOTER_RESERVE")

    def test_no_text_runs_off_the_canvas(self):
        from cannabiology.builders import diagram
        # A long end label is what clipped CH05-IMG-01 at the left edge.
        cases = {
            "timeline": self._spec("timeline", nodes=[
                {"id": "a", "label": "Hand-rubbed hashish; trichomes separated "
                                     "on silk screens", "date": "1000-1200 CE"},
                {"id": "b", "label": "Advanced delivery and modern processing",
                 "date": "2020-2026"}]),
        }
        for layout in LAYOUT_SPECS:
            cases.setdefault(layout, self._spec(layout))
        for layout, spec in cases.items():
            with self.subTest(layout=layout):
                w, h = 1200, 800
                for b in self._boxes(diagram.build(spec, w, h)):
                    self.assertGreaterEqual(
                        b["l"], 0, f"{layout}: {b['text']!r} runs off the left edge")
                    self.assertLessEqual(
                        b["r"], w, f"{layout}: {b['text']!r} runs off the right edge")

    def test_artwork_keeps_clear_of_the_caption_strip(self):
        from cannabiology.builders import diagram
        w, h = 1200, 800
        floor = h - diagram.FOOTER_RESERVE
        for layout in LAYOUT_SPECS:
            with self.subTest(layout=layout):
                svg = diagram.build(self._spec(layout), w, h)
                for b in self._boxes(svg):
                    # The provenance stamp is meant to sit in the strip.
                    if "spec:" in b["text"] or "DRAFT" in b["text"]:
                        continue
                    self.assertLessEqual(
                        b["y"], floor,
                        f"{layout}: {b['text']!r} sits at y={b['y']:.0f}, inside the "
                        f"caption strip below y={floor}")

    def test_band_label_is_not_painted_over_by_the_first_row(self):
        from cannabiology.builders import diagram
        import re
        spec = self._spec("flow", bands=[{"nodes": ["a", "d", "e"],
                                          "label": "Foxtrot"}])
        svg = diagram.build(spec, 1200, 800)
        band = next(b for b in self._boxes(svg) if b["text"] == "FOXTROT")
        for m in re.finditer(r'<rect x="([-\d.]+)" y="([-\d.]+)" '
                             r'width="([\d.]+)" height="([\d.]+)"', svg):
            x, y, rw, rh = (float(m.group(i)) for i in range(1, 5))
            if rw > 400:       # the band itself, not a node box
                continue
            overlaps = (x < band["r"] and band["l"] < x + rw
                        and y < band["y"] + 4 and band["y"] - 12 < y + rh)
            self.assertFalse(
                overlaps, f"node box at ({x:.0f},{y:.0f}) paints over the band label")


class TestBandsGroupNodes(WorkspaceTest):
    def test_pixel_band_is_refused(self):
        """Hand-written band coordinates went stale silently. Fail loudly."""
        from cannabiology.builders import diagram
        spec = {"figure_id": "CH01-IMG-04", "confirmed": True,
                "source": "TEST-FIXTURE", "layout": "flow",
                "nodes": [{"id": "a", "label": "Alpha", "column": 0}],
                "bands": [{"x": 10, "y": 10, "width": 100, "height": 100,
                           "label": "stale"}]}
        with self.assertRaises(diagram.DiagramError) as ctx:
            diagram.build(spec, 1200, 800)
        self.assertIn("lists no nodes", str(ctx.exception))

    def test_band_referencing_an_unknown_node_is_refused(self):
        from cannabiology.builders import diagram
        spec = {"figure_id": "CH01-IMG-04", "confirmed": True,
                "source": "TEST-FIXTURE", "layout": "flow",
                "nodes": [{"id": "a", "label": "Alpha", "column": 0}],
                "bands": [{"nodes": ["a", "ghost"], "label": "b"}]}
        with self.assertRaises(diagram.DiagramError) as ctx:
            diagram.build(spec, 1200, 800)
        self.assertIn("ghost", str(ctx.exception))

    def test_band_encloses_the_nodes_it_names(self):
        from cannabiology.builders import diagram
        import re
        spec = {"figure_id": "CH01-IMG-04", "confirmed": True,
                "source": "TEST-FIXTURE", "layout": "flow",
                "nodes": [{"id": "a", "label": "Alpha", "column": 0, "row": 0},
                          {"id": "b", "label": "Bravo", "column": 0, "row": 1},
                          {"id": "c", "label": "Outside", "column": 1, "row": 0}],
                "bands": [{"nodes": ["a", "b"], "label": "Group"}]}
        svg = diagram.build(spec, 1200, 800)
        rects = [tuple(float(g) for g in m.groups()) for m in re.finditer(
            r'<rect x="([-\d.]+)" y="([-\d.]+)" width="([\d.]+)" height="([\d.]+)"', svg)]
        band = max(rects, key=lambda r: r[2] * r[3])
        boxes = [r for r in rects if r[2] == diagram.NODE_W]
        inside = [r for r in boxes
                  if band[0] <= r[0] and r[0] + r[2] <= band[0] + band[2]
                  and band[1] <= r[1] and r[1] + r[3] <= band[1] + band[3]]
        self.assertEqual(len(inside), 2,
                         "band should enclose exactly the two nodes it names")


class TestNodeTextFitsItsBox(WorkspaceTest):
    def test_no_line_overhangs_its_node_box(self):
        """Node labels used to wrap wider than the box that contains them."""
        from cannabiology.builders import diagram
        import re
        from html import unescape
        spec = {"figure_id": "CH01-IMG-04", "confirmed": True,
                "source": "TEST-FIXTURE", "layout": "flow",
                "nodes": [{"id": "a", "label": "Mevalonate / MEP pathway",
                           "column": 0, "row": 0},
                          {"id": "b", "label": "Environment B: low-light indoor",
                           "column": 1, "row": 0},
                          {"id": "c", "label": "Feature extraction: SNP alleles "
                                               "at THCAS, CBDAS, TPS",
                           "column": 2, "row": 0}]}
        svg = diagram.build(spec, 1200, 800)
        for m in re.finditer(r'<text x="([-\d.]+)" y="[-\d.]+" text-anchor="middle"'
                             r'[^>]*?font-size="([\d.]+)"[^>]*>(.*?)</text>', svg, re.S):
            body = unescape(m.group(3))
            w = diagram.text_width(body, float(m.group(2)))
            self.assertLessEqual(
                w, diagram.NODE_W,
                f"{body!r} measures {w:.0f}px inside a {diagram.NODE_W}px box")


class TestLabelFragmentMatching(WorkspaceTest):
    """A label wrongly reported covered never gets overlaid, and vanishes.

    That is the dangerous direction, so short fragments must not match.
    """

    ART = ["Presynaptic terminal", "Postsynaptic neuron", "CB1 receptor"]

    def test_one_letter_fragment_does_not_count_as_covered(self):
        from cannabiology.vectorbuild import label_coverage
        covered, missing = label_coverage(["Gi/o"], self.ART)
        self.assertEqual(covered, [])
        self.assertEqual(missing, ["Gi/o"])

    def test_substantial_fragments_still_match_either_side(self):
        from cannabiology.vectorbuild import label_coverage
        covered, _ = label_coverage(
            ["cannabinoids/terpenes"], ["Terpenes and volatiles"])
        self.assertEqual(covered, ["cannabinoids/terpenes"])

    def test_a_short_whole_label_still_matches_itself(self):
        """The minimum applies to fragments, not to the label as written."""
        from cannabiology.vectorbuild import label_coverage
        covered, _ = label_coverage(["CB1"], self.ART)
        self.assertEqual(covered, ["CB1"])

    def test_matching_is_whole_word(self):
        from cannabiology.vectorbuild import label_coverage
        _, missing = label_coverage(["CB1"], ["CB10 variant only"])
        self.assertEqual(missing, ["CB1"])

    def test_absent_label_is_still_reported_missing(self):
        from cannabiology.vectorbuild import label_coverage
        _, missing = label_coverage(["MAGL/FAAH", "AEA"], self.ART)
        self.assertEqual(sorted(missing), ["AEA", "MAGL/FAAH"])

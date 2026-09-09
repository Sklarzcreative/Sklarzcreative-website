"""The intake gate for artwork drawn outside the pipeline.

Externally drawn artwork carries none of the guarantees the deterministic
builder provides. These tests pin the checks that stand in for them.
"""
import unittest

from base import WorkspaceTest

SVG_HEAD = ('<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="900" '
            'viewBox="0 0 1600 900">')


def svg(*body):
    return SVG_HEAD + "".join(body) + "</svg>"


def text(s, x=800, y=400, size=20, anchor="middle"):
    return (f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}">'
            f'{s}</text>')


GOOD_RECORD = """FIGURE: CH06-IMG-03
FORMAT: svg
DREW: a seven-transmembrane receptor with downstream branches
LABEL ZONES: eleven callout endpoints around the membrane
DEPARTURES: merged the two ion-channel branches into one
NOT DRAWN: the MAPK branch, because the brief does not say where it terminates
UNCERTAIN: G-protein placement
QUESTIONS: none
"""


class TestRecord(WorkspaceTest):
    def test_missing_record_is_fatal(self):
        from cannabiology import intake
        f = intake.check_record("")
        self.assertTrue(any(x.code == "record.missing" and x.level == "FAIL"
                            for x in f))

    def test_record_missing_a_required_field_is_fatal(self):
        from cannabiology import intake
        partial = "FIGURE: CH06-IMG-03\nDREW: a thing\n"
        codes = [x.code for x in intake.check_record(partial) if x.level == "FAIL"]
        self.assertIn("record.field_missing", codes)

    def test_complete_record_passes(self):
        from cannabiology import intake
        self.assertEqual([x for x in intake.check_record(GOOD_RECORD)
                          if x.level == "FAIL"], [])

    def test_departures_none_is_flagged_for_verification(self):
        from cannabiology import intake
        rec = GOOD_RECORD.replace("DEPARTURES: merged the two ion-channel "
                                  "branches into one", "DEPARTURES: none")
        self.assertTrue(any(x.code == "record.no_departures"
                            for x in intake.check_record(rec)))

    def test_multiline_field_is_read_whole(self):
        from cannabiology import intake
        rec = GOOD_RECORD.replace(
            "DEPARTURES: merged the two ion-channel branches into one",
            "DEPARTURES: merged the two ion-channel\n  branches into one")
        self.assertIn("branches into one",
                      intake.parse_record(rec)["DEPARTURES"])


class TestAssertedText(WorkspaceTest):
    LABELS = ["cannabinoids", "terpenes", "independent targets", "CB1/CB2"]

    def test_printing_a_manual_label_is_fatal(self):
        from cannabiology import intake
        f = intake.check_asserted_text(svg(text("cannabinoids")), self.LABELS)
        self.assertEqual([x.code for x in f], ["text.asserted_label"])

    def test_label_wrapped_across_tspans_is_still_caught(self):
        """"Independent" / "targets" is two runs but one label."""
        from cannabiology import intake
        wrapped = svg('<text x="800" y="400" font-size="20">'
                      '<tspan x="800" dy="0">Independent</tspan>'
                      '<tspan x="800" dy="25">targets</tspan></text>')
        self.assertTrue(any(x.code == "text.asserted_label"
                            for x in intake.check_asserted_text(wrapped, self.LABELS)))

    def test_wordless_artwork_passes(self):
        from cannabiology import intake
        self.assertEqual(
            intake.check_asserted_text(svg('<rect x="1" y="1" width="9" '
                                           'height="9"/>'), self.LABELS), [])

    def test_short_label_fragments_do_not_false_positive(self):
        """A two-character fragment would match almost any artwork."""
        from cannabiology import intake
        self.assertEqual(
            intake.check_asserted_text(svg(text("Membrane")), ["pH", "A/B"]), [])


class TestInventedData(WorkspaceTest):
    def test_percentage_is_fatal(self):
        from cannabiology import intake
        f = intake.check_invented_data(svg(text("THC 18%")))
        self.assertEqual([x.code for x in f], ["data.unit_number"])

    def test_temperature_is_fatal(self):
        from cannabiology import intake
        self.assertTrue(intake.check_invented_data(svg(text("35 °C"))))

    def test_sample_size_is_fatal(self):
        from cannabiology import intake
        self.assertTrue(any(x.code == "data.count_claim"
                            for x in intake.check_invented_data(svg(text("n=120")))))

    def test_ploidy_claim_is_fatal(self):
        """"2n = 20" is a chromosome-count assertion and needs a source.

        The first version of this check required a word boundary before the n,
        so "2n" did not match and a karyotype figure passed with the claim on it.
        """
        from cannabiology import intake
        f = intake.check_invented_data(
            svg(text("10 homologous chromosome pairs - 2n = 20")))
        self.assertTrue(any(x.code == "data.count_claim" for x in f))

    def test_a_word_ending_in_n_is_not_a_count(self):
        from cannabiology import intake
        self.assertEqual(
            intake.check_invented_data(svg(text("carbon = major element"))), [])

    def test_readable_sequence_is_fatal(self):
        from cannabiology import intake
        self.assertTrue(any(x.code == "data.sequence"
                            for x in intake.check_invented_data(
                                svg(text("GATTACA")))))

    def test_panel_letters_are_not_data(self):
        from cannabiology import intake
        self.assertEqual(intake.check_invented_data(svg(text("A"), text("B"))), [])


class TestGeometry(WorkspaceTest):
    def test_text_off_the_left_edge_is_fatal(self):
        from cannabiology import intake
        f = intake.check_geometry(svg(text("Hand-rubbed hashish", x=20)))
        self.assertTrue(any(x.code == "geometry.off_canvas_left" for x in f))

    def test_text_in_the_caption_strip_is_fatal(self):
        from cannabiology import intake
        f = intake.check_geometry(svg(text("Skin", y=860)))
        self.assertTrue(any(x.code == "geometry.in_caption_strip" for x in f))

    def test_clear_artwork_passes(self):
        from cannabiology import intake
        self.assertEqual(intake.check_geometry(svg(text("Middle", y=400))), [])

    def test_malformed_svg_is_reported_not_crashed(self):
        from cannabiology import intake, svgtext
        with self.assertRaises(svgtext.MalformedSVG):
            intake.check_geometry("<svg><text>unclosed")


class TestRouteGate(WorkspaceTest):
    def _fig(self, status):
        from cannabiology import canonical
        return canonical.Figure(
            figure_id="CH03-IMG-05", chapter="3", title="t", purpose="p",
            visual_type="v", status=status, prompt="", negative="",
            science_notes="", manual_labels=[], caption="", aspect="16:9",
            page_treatment="", approval="Not approved", manuscript_section="",
            source_manuscript="")

    def test_figure_on_hold_is_refused(self):
        from cannabiology import intake, routing
        fig = self._fig("HOLD — Chapter 3 source-intent lock required")
        dec = routing.Router().route(fig)
        self.assertEqual(dec.route, "HOLD")
        self.assertTrue(any(x.code == "route.hold" and x.level == "FAIL"
                            for x in intake.check_route(fig, dec)))


class TestIngestLane(WorkspaceTest):
    def test_ingested_art_cannot_reach_production_without_review(self):
        """The whole point: external artwork joins the reviewed lane."""
        from cannabiology import state as st
        self.assertIn(st.CANDIDATE_READY, st.TRANSITIONS[st.INGESTING])
        self.assertNotIn(st.PRODUCTION_READY_BASE_ART, st.TRANSITIONS[st.INGESTING])
        self.assertNotIn(st.BUILT, st.TRANSITIONS[st.INGESTING])
        self.assertEqual(st.TRANSITIONS[st.CANDIDATE_READY], {st.OA_REVIEW})

    def test_ingesting_is_reachable_from_context_ready(self):
        from cannabiology import state as st
        self.assertIn(st.INGESTING, st.TRANSITIONS[st.CONTEXT_READY])


if __name__ == "__main__":
    unittest.main()


class TestRasterChecks(WorkspaceTest):
    """Pixels cannot be read for text, but size and shape can."""

    def _fig(self, aspect):
        from cannabiology import canonical
        return canonical.Figure(
            figure_id="CH01-IMG-01", chapter="1", title="t", purpose="p",
            visual_type="v", status="", prompt="", negative="", science_notes="",
            manual_labels=[], caption="", aspect=aspect, page_treatment="",
            approval="", manuscript_section="", source_manuscript="")

    def _png(self, w, h, name="a.png"):
        import struct, zlib
        from cannabiology import workspace
        raw = b"".join(b"\x00" + b"\xff\xff\xff" * w for _ in range(h))
        def chunk(tag, data):
            c = tag + data
            return (struct.pack(">I", len(data)) + c
                    + struct.pack(">I", zlib.crc32(c) & 0xffffffff))
        png = (b"\x89PNG\r\n\x1a\n"
               + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(raw))
               + chunk(b"IEND", b""))
        p = workspace.resolve() / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(png)
        return p

    def test_pixel_size_reads_a_png_header(self):
        from cannabiology import intake
        self.assertEqual(intake.pixel_size(self._png(37, 11)), (37, 11))

    def test_below_print_resolution_is_fatal(self):
        from cannabiology import intake
        f = intake.check_raster(self._png(356, 540), self._fig("3:4"))
        self.assertTrue(any(x.code == "raster.below_print_resolution"
                            and x.level == "FAIL" for x in f))

    def test_wrong_orientation_is_named_explicitly(self):
        """A 4:3 figure delivered portrait is the error most easily missed."""
        from cannabiology import intake
        f = intake.check_raster(self._png(356, 540), self._fig("4:3"))
        mismatch = [x for x in f if x.code == "raster.aspect_mismatch"]
        self.assertTrue(mismatch)
        self.assertIn("wrong orientation", mismatch[0].detail)

    def test_correct_aspect_and_size_passes_both(self):
        from cannabiology import intake
        f = intake.check_raster(self._png(2400, 1800), self._fig("4:3"))
        self.assertEqual([x.code for x in f], ["file.raster_not_inspected"])

    def test_unparseable_tracker_aspect_is_not_a_finding(self):
        from cannabiology import intake
        f = intake.check_raster(self._png(2400, 1800), self._fig("Full-width"))
        self.assertEqual([x.code for x in f], ["file.raster_not_inspected"])

    def test_raster_always_says_what_could_not_be_checked(self):
        from cannabiology import intake
        for aspect in ("4:3", "3:4", "16:9"):
            f = intake.check_raster(self._png(2400, 1800), self._fig(aspect))
            self.assertTrue(any(x.code == "file.raster_not_inspected" for x in f))

    def test_parse_aspect(self):
        from cannabiology import intake
        self.assertAlmostEqual(intake.parse_aspect("16:9"), 16 / 9)
        self.assertAlmostEqual(intake.parse_aspect("3:4"), 0.75)
        self.assertIsNone(intake.parse_aspect("Full-width timeline"))


class TestAssertedTextIsScopedToWordlessRoutes(WorkspaceTest):
    """VECTOR_BUILD artwork prints its own labels. That is correct, not a fault."""

    def _fig(self, status, labels):
        from cannabiology import canonical
        return canonical.Figure(
            figure_id="CH01-IMG-04", chapter="1", title="t", purpose="p",
            visual_type="v", status=status, prompt="", negative="",
            science_notes="", manual_labels=labels, caption="", aspect="16:9",
            page_treatment="", approval="", manuscript_section="",
            source_manuscript="")

    def _svg_path(self, body, name="art.svg"):
        from cannabiology import workspace
        p = workspace.resolve() / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(SVG_HEAD + body + "</svg>")
        return p

    def test_vector_build_may_print_its_labels(self):
        from cannabiology import intake, routing
        fig = self._fig("VECTOR-BUILD — conceptual metabolic branching diagram",
                        ["cannabinoids", "terpenes"])
        dec = routing.Router().route(fig)
        self.assertEqual(dec.route, "VECTOR_BUILD")
        path = self._svg_path(text("cannabinoids") + text("terpenes", y=500))
        codes = [f.code for f in intake.inspect(path, fig, dec, GOOD_RECORD)]
        self.assertNotIn("text.asserted_label", codes)

    def test_hybrid_may_not(self):
        from cannabiology import intake, routing
        fig = self._fig("Prompt ready / artwork not generated",
                        ["cannabinoids", "terpenes"])
        dec = routing.Router().route(fig)
        self.assertIn(dec.route, intake.WORDLESS_ROUTES)
        path = self._svg_path(text("cannabinoids"), name="art2.svg")
        codes = [f.code for f in intake.inspect(path, fig, dec, GOOD_RECORD)]
        self.assertIn("text.asserted_label", codes)

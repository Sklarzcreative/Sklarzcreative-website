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
        self.assertTrue(any(x.code == "data.sample_size"
                            for x in intake.check_invented_data(svg(text("n=120")))))

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

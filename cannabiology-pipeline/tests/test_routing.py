"""The routing gate is the project's primary scientific safeguard."""
from base import WorkspaceTest


class TestRouting(WorkspaceTest):
    def test_vector_build_never_reaches_generation(self):
        from cannabiology import routing, runner
        figs, dec = self.load()
        d = dec["CH02-IMG-01"]
        self.assertEqual(d.route, routing.VECTOR_BUILD)
        with self.assertRaises(runner.RouteBlocked):
            runner.guard_route(d)

    def test_data_driven_never_reaches_generation(self):
        from cannabiology import routing, runner
        figs, dec = self.load()
        d = dec["CH02-IMG-02"]
        self.assertEqual(d.route, routing.DATA_DRIVEN)
        with self.assertRaises(runner.RouteBlocked):
            runner.guard_route(d)

    def test_hold_never_runs(self):
        from cannabiology import routing, runner
        figs, dec = self.load()
        d = dec["CH03-IMG-01"]
        self.assertEqual(d.route, routing.HOLD)
        with self.assertRaises(runner.RouteBlocked):
            runner.guard_route(d)

    def test_force_cannot_open_the_gate(self):
        from cannabiology import runner
        figs, dec = self.load()
        with self.assertRaises(runner.RouteBlocked):
            runner.guard_route(dec["CH03-IMG-01"], force=True, confirm_route=True)

    def test_generate_with_labels_becomes_hybrid(self):
        from cannabiology import routing, runner
        figs, dec = self.load()
        d = dec["CH01-IMG-01"]
        self.assertEqual(d.route, routing.HYBRID)
        self.assertEqual(d.confidence, "explicit")
        self.assertTrue(runner.guard_route(d))

    def test_derived_route_requires_confirmation(self):
        from cannabiology import runner
        figs, dec = self.load()
        d = dec["CH04-IMG-01"]
        self.assertTrue(d.needs_route_confirmation)
        self.assertEqual(d.confidence, "derived")
        with self.assertRaises(runner.RouteBlocked):
            runner.guard_route(d)
        self.assertTrue(runner.guard_route(d, confirm_route=True))

    def test_rules_only_escalate_never_downgrade(self):
        from cannabiology import routing
        r = routing.Router()
        self.assertEqual(r._escalate(routing.DATA_DRIVEN, routing.GENERATE),
                         routing.DATA_DRIVEN)
        self.assertEqual(r._escalate(routing.GENERATE, routing.VECTOR_BUILD),
                         routing.VECTOR_BUILD)

    def test_hybrid_labels_go_to_vector_layer_not_the_image_prompt(self):
        from cannabiology import prompts
        figs, _ = self.load()
        asset = figs["CH01-IMG-01"].assets[0]
        text = prompts.assemble(asset)
        self.assertIn("must NOT be typeset", text)
        self.assertIn("LAYOUT RESERVATION", text)


class TestRouteOverrides(WorkspaceTest):
    """Deliberate reroutes are recorded in an override file, not by editing the
    read-only canonical tracker."""

    def test_override_can_make_a_route_stricter(self):
        from cannabiology import routing
        figs, _ = self.load()
        r = routing.Router(overrides={"CH01-IMG-01": {
            "route": "VECTOR_BUILD", "reason": "topology is the content",
            "authorized_by": "Cassandra Sklarz"}})
        d = r.route(figs["CH01-IMG-01"])          # HYBRID in the fixture
        self.assertEqual(d.route, routing.VECTOR_BUILD)
        self.assertEqual(d.confidence, "override")
        self.assertTrue(any("overridden" in x for x in d.reasons))

    def test_override_cannot_loosen_a_route(self):
        from cannabiology import routing
        figs, _ = self.load()
        r = routing.Router(overrides={"CH03-IMG-01": {"route": "GENERATE"}})
        with self.assertRaises(ValueError):
            r.route(figs["CH03-IMG-01"])          # HOLD in the fixture

    def test_override_cannot_release_a_hold(self):
        from cannabiology import routing
        figs, _ = self.load()
        for target in ("GENERATE", "HYBRID", "VECTOR_BUILD", "DATA_DRIVEN"):
            r = routing.Router(overrides={"CH03-IMG-01": {"route": target}})
            with self.assertRaises(ValueError):
                r.route(figs["CH03-IMG-01"])

    def test_unknown_route_in_override_is_refused(self):
        from cannabiology import routing
        figs, _ = self.load()
        r = routing.Router(overrides={"CH01-IMG-01": {"route": "SPARKLE"}})
        with self.assertRaises(ValueError):
            r.route(figs["CH01-IMG-01"])

    def test_override_clears_the_route_confirmation_requirement(self):
        """A human naming the route explicitly IS the confirmation."""
        from cannabiology import routing
        figs, _ = self.load()
        base = routing.Router().route(figs["CH04-IMG-01"])
        self.assertTrue(base.needs_route_confirmation)
        r = routing.Router(overrides={"CH04-IMG-01": {
            "route": "VECTOR_BUILD", "authorized_by": "Cassandra Sklarz"}})
        self.assertFalse(r.route(figs["CH04-IMG-01"]).needs_route_confirmation)

    def test_no_override_file_is_not_an_error(self):
        from cannabiology import routing
        self.assertEqual(routing.load_overrides("/nonexistent/overrides.yaml"), {})

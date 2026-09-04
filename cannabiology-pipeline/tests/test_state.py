from base import WorkspaceTest


class TestState(WorkspaceTest):
    def test_invalid_transition_fails(self):
        from cannabiology import state as st
        store = st.Store()
        store.transition("CH01-IMG-01", st.ROUTED)
        with self.assertRaises(st.StateError):
            store.transition("CH01-IMG-01", st.PACKAGED)

    def test_human_approval_cannot_be_skipped(self):
        from cannabiology import state as st
        self.assertNotIn(st.PACKAGED, st.TRANSITIONS[st.PRODUCTION_READY_BASE_ART])
        self.assertNotIn(st.HUMAN_APPROVED, st.TRANSITIONS[st.PRODUCTION_READY_BASE_ART])
        self.assertEqual(st.TRANSITIONS[st.HUMAN_APPROVED], {st.PACKAGED})

    def test_pending_approval_only_advances_via_human(self):
        from cannabiology import state as st
        self.assertIn(st.HUMAN_APPROVED, st.TRANSITIONS[st.PENDING_HUMAN_APPROVAL])

    def test_state_survives_reload(self):
        from cannabiology import state as st
        store = st.Store()
        store.transition("CH01-IMG-01", st.ROUTED, "note")
        store.save()
        self.assertEqual(st.Store().get("CH01-IMG-01")["state"], st.ROUTED)

    def test_figure_lock_is_exclusive(self):
        from cannabiology import state as st
        with st.figure_lock("CH01-IMG-01"):
            with self.assertRaises(st.LockError):
                with st.figure_lock("CH01-IMG-01"):
                    pass

    def test_lock_releases(self):
        from cannabiology import state as st
        with st.figure_lock("CH01-IMG-01"):
            pass
        with st.figure_lock("CH01-IMG-01"):
            pass


class TestBuildLane(WorkspaceTest):
    """The deterministic lane has no prompt stage, so it needs its own path."""

    def test_context_ready_can_enter_building(self):
        from cannabiology import state as st
        self.assertIn(st.BUILDING, st.TRANSITIONS[st.CONTEXT_READY])

    def test_building_reaches_built_not_candidate_ready(self):
        """BUILT is deliberately separate: it is the state that may skip OA
        image review, and that shortcut must not be reachable from the
        generative lane's CANDIDATE_READY."""
        from cannabiology import state as st
        self.assertIn(st.BUILT, st.TRANSITIONS[st.BUILDING])
        self.assertNotIn(st.CANDIDATE_READY, st.TRANSITIONS[st.BUILDING])

    def test_building_is_distinct_from_generating(self):
        """GENERATING implies a model call; the build lane never makes one."""
        from cannabiology import state as st
        self.assertNotEqual(st.BUILDING, st.GENERATING)

    def test_full_build_lane_path_is_legal(self):
        from cannabiology import state as st
        path = [st.ROUTED, st.CONTEXT_READY, st.BUILDING, st.BUILT,
                st.PRODUCTION_READY_BASE_ART, st.PENDING_HUMAN_APPROVAL]
        for a, b in zip(path, path[1:]):
            self.assertTrue(st.can_transition(a, b), f"{a} -> {b} must be legal")

    def test_generated_candidate_cannot_skip_oa_review(self):
        """The build lane's shortcut must not leak into the generative lane."""
        from cannabiology import state as st
        self.assertNotIn(st.PRODUCTION_READY_BASE_ART,
                         st.TRANSITIONS[st.CANDIDATE_READY])
        self.assertEqual(st.TRANSITIONS[st.CANDIDATE_READY], {st.OA_REVIEW})

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

"""The public repository must never receive client-derived content."""
import os
from pathlib import Path

from base import WorkspaceTest


class TestPrivacy(WorkspaceTest):
    def test_unset_workspace_fails_closed(self):
        from cannabiology import workspace
        os.environ.pop("CANNABIOLOGY_WORKSPACE", None)
        with self.assertRaises(workspace.WorkspaceError):
            workspace.resolve()

    def test_workspace_inside_repo_is_rejected(self):
        from cannabiology import workspace
        os.environ["CANNABIOLOGY_WORKSPACE"] = str(workspace.REPO_ROOT / "client-data")
        with self.assertRaises(workspace.WorkspaceError):
            workspace.resolve()

    def test_relative_workspace_is_rejected(self):
        from cannabiology import workspace
        os.environ["CANNABIOLOGY_WORKSPACE"] = "./somewhere"
        with self.assertRaises(workspace.WorkspaceError):
            workspace.resolve()

    def test_cannot_write_client_content_into_repo(self):
        from cannabiology import workspace
        target = workspace.REPO_ROOT / "cannabiology-pipeline" / "leak.json"
        with self.assertRaises(workspace.WorkspaceError):
            workspace.assert_safe_write(target)
        self.assertFalse(Path(target).exists())

    def test_context_extract_lands_outside_repo(self):
        from cannabiology import context, workspace
        figs, _ = self.load()
        ctx = context.extract(figs["CH01-IMG-01"])
        path, _v = context.save(ctx, "CH01-IMG-01")
        self.assertFalse(str(path).startswith(str(workspace.REPO_ROOT)))
        self.assertTrue(str(path).startswith(str(self.tmp)))

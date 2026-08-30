"""Shared harness. Every test uses SYNTHETIC fixtures and a temp workspace -
never client manuscript content."""
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(SRC))


class WorkspaceTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="cannab-test-"))
        os.environ["CANNABIOLOGY_WORKSPACE"] = str(self.tmp)
        from cannabiology import workspace
        workspace.resolve(create=True)
        snap = self.tmp / "canonical" / "tracker_snapshot"
        shutil.copy(FIXTURES / "synthetic_tracker.csv", snap / "master-figure-tracker.csv")
        shutil.copy(FIXTURES / "synthetic_prompts.csv", snap / "prompt-library.csv")
        shutil.copy(FIXTURES / "SYN01.md",
                    self.tmp / "canonical" / "manuscript_sources" / "SYN01.md")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)
        os.environ.pop("CANNABIOLOGY_WORKSPACE", None)

    def load(self):
        from cannabiology import canonical, routing
        figs = canonical.load_figures()
        return figs, routing.Router().route_all(figs)

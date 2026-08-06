import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LAUNCHER = PROJECT_ROOT / "windows" / "Launch-NCUGymMonitor.ps1"


class LauncherTests(unittest.TestCase):
    def test_missing_project_environment_recommends_rerunning_setup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            result = self._launch(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Project environment", result.stderr)
        self.assertIn("Setup", result.stderr)

    def test_missing_widget_entry_point_is_reported_before_launch(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            pythonw = project / ".venv" / "Scripts" / "pythonw.exe"
            pythonw.parent.mkdir(parents=True)
            pythonw.touch()

            result = self._launch(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Widget entry point", result.stderr)
        self.assertIn("checkout", result.stderr)

    def test_missing_runtime_dependency_recommends_rerunning_setup(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self._create_project_environment(project)
            (project / "gym.pyw").write_text("pass\n", encoding="utf-8")

            result = self._launch(project)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("runtime dependencies", result.stderr)
        self.assertIn("Setup", result.stderr)

    def test_valid_launch_starts_widget_silently(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            self._create_project_environment(project)
            self._add_runtime_import_stubs(project)
            marker = project / "launched.txt"
            (project / "gym.pyw").write_text(
                "import os\nfrom pathlib import Path\n"
                "Path(os.environ['NCU_GYM_TEST_MARKER']).write_text('launched', encoding='utf-8')\n",
                encoding="utf-8",
            )

            launch_environment = os.environ.copy()
            launch_environment["NCU_GYM_TEST_MARKER"] = str(marker)
            result = self._launch(project, "-Wait", env=launch_environment)

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "")
            self.assertEqual(result.stderr, "")
            self.assertEqual(marker.read_text(encoding="utf-8"), "launched")

    def test_launcher_defaults_to_checkout_containing_the_script(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            project = Path(temp_dir)
            (project / "windows").mkdir()
            copied_launcher = project / "windows" / LAUNCHER.name
            shutil.copy2(LAUNCHER, copied_launcher)
            self._create_project_environment(project)
            self._add_runtime_import_stubs(project)
            marker = project / "launched.txt"
            (project / "gym.pyw").write_text(
                "import os\nfrom pathlib import Path\n"
                "Path(os.environ['NCU_GYM_TEST_MARKER']).write_text('launched', encoding='utf-8')\n",
                encoding="utf-8",
            )
            environment = os.environ.copy()
            environment["NCU_GYM_TEST_MARKER"] = str(marker)

            result = subprocess.run(
                [
                    "powershell.exe",
                    "-NoProfile",
                    "-ExecutionPolicy",
                    "Bypass",
                    "-File",
                    str(copied_launcher),
                    "-NoDialog",
                    "-Wait",
                ],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                env=environment,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "launched")

    def _launch(
        self,
        project: Path,
        *extra_args: str,
        env: dict[str, str] | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                str(LAUNCHER),
                "-ProjectRoot",
                str(project),
                "-NoDialog",
                *extra_args,
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
            env=env,
        )

    def _create_project_environment(self, project: Path) -> None:
        subprocess.run(
            [sys.executable, "-m", "venv", str(project / ".venv")],
            capture_output=True,
            text=True,
            timeout=30,
            check=True,
        )

    def _add_runtime_import_stubs(self, project: Path) -> None:
        for module_name in ("requests", "bs4", "PIL"):
            (project / f"{module_name}.py").write_text("", encoding="utf-8")


if __name__ == "__main__":
    unittest.main()

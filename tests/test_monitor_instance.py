import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MONITOR_ENTRY = PROJECT_ROOT / "gym.pyw"


class MonitorInstanceTests(unittest.TestCase):
    def test_repeated_launch_exits_until_active_monitor_stops(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            marker = Path(temp_dir) / "started.txt"
            first = subprocess.Popen(
                [sys.executable, str(MONITOR_ENTRY), "--instance-probe", str(marker), "1.5"],
                cwd=PROJECT_ROOT,
            )

            try:
                self._wait_for_lines(marker, 1)

                repeated = subprocess.run(
                    [sys.executable, str(MONITOR_ENTRY), "--instance-probe", str(marker), "0.1"],
                    cwd=PROJECT_ROOT,
                    timeout=2,
                    check=False,
                )
                self.assertEqual(repeated.returncode, 0)
                self.assertEqual(marker.read_text(encoding="utf-8").splitlines(), ["started"])
            finally:
                first.wait(timeout=3)

            relaunched = subprocess.run(
                [sys.executable, str(MONITOR_ENTRY), "--instance-probe", str(marker), "0.1"],
                cwd=PROJECT_ROOT,
                timeout=2,
                check=False,
            )
            self.assertEqual(relaunched.returncode, 0)
            self.assertEqual(
                marker.read_text(encoding="utf-8").splitlines(),
                ["started", "started"],
            )

    def _wait_for_lines(self, marker: Path, expected: int) -> None:
        deadline = time.monotonic() + 3
        while time.monotonic() < deadline:
            if marker.exists() and len(marker.read_text(encoding="utf-8").splitlines()) >= expected:
                return
            time.sleep(0.05)
        self.fail(f"Monitor did not record {expected} start(s) before timeout")


if __name__ == "__main__":
    unittest.main()

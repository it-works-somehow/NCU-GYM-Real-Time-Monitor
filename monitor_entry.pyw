"""User-facing entry point for one NCU Gym Monitor instance."""

from __future__ import annotations

import ctypes
import runpy
import sys
import time
from pathlib import Path

from monitor_instance import MonitorInstance


PROJECT_ROOT = Path(__file__).resolve().parent
WIDGET_ENTRY = PROJECT_ROOT / "gym.pyw"


def show_startup_error(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(0, message, "NCU Gym Monitor", 0x10)


def run_instance_probe(arguments: list[str]) -> int:
    marker = Path(arguments[0])
    hold_seconds = float(arguments[1])
    with marker.open("a", encoding="utf-8") as marker_file:
        marker_file.write("started\n")
    time.sleep(hold_seconds)
    return 0


def main(arguments: list[str]) -> int:
    no_dialog = "--no-dialog" in arguments
    monitor_instance = MonitorInstance.try_acquire()
    if monitor_instance is None:
        return 0

    try:
        if "--instance-probe" in arguments:
            probe_index = arguments.index("--instance-probe")
            return run_instance_probe(arguments[probe_index + 1 : probe_index + 3])

        try:
            runpy.run_path(str(WIDGET_ENTRY), run_name="__main__")
            return 0
        except Exception as error:
            if not no_dialog:
                show_startup_error(
                    "The Widget failed during startup. Rerun Setup; if the problem "
                    f"continues, restore the checkout.\n\nDetails: {error}"
                )
            return 14
    finally:
        monitor_instance.release()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

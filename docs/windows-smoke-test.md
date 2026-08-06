# Windows Desktop shortcut smoke test

Run this bounded test on the target Windows account after automated tests pass.

## Procedure

- [ ] Run Setup from the intended checkout and confirm it completes.
- [ ] Confirm the desktop contains exactly one **NCU Gym Monitor** shortcut with
      the green dumbbell icon.
- [ ] Inspect the shortcut and confirm it targets the checkout's Launcher and
      uses the checkout as its working directory.
- [ ] Double-click the shortcut and confirm the Widget opens without a command
      prompt remaining visible.
- [ ] Double-click again and confirm no second Widget, polling loop, or CSV writer
      starts.
- [ ] Close the Widget, launch it again, and confirm it opens normally.
- [ ] Temporarily rename `.venv`, launch the shortcut, and confirm a native error
      dialog recommends rerunning Setup. Restore `.venv` afterward.
- [ ] Confirm the running Widget uses the checkout's `.venv` and not a
      Codex-managed runtime.
- [ ] Confirm Setup created no login startup entry, scheduled task, Windows
      service, or tray process.

## Result

Status: **Passed on 2026-08-06** on the target Windows account.

- Setup installed official per-user CPython 3.13.15, created the checkout's
  `.venv`, installed the declared runtime dependencies, and created exactly one
  Desktop shortcut.
- The shortcut target, arguments, working directory, and icon all referenced the
  intended checkout.
- Launching opened a responsive Tk Widget through the Project environment with
  no command prompt left visible.
- Windows represented the one logical Monitor instance as a normal venv
  redirector/CPython parent-child pair. A repeated shortcut launch left the PID
  set unchanged, confirming that no second Monitor instance started.
- A normal `WM_CLOSE` removed the complete process pair; launching afterward
  created a new pair, confirming that the single-instance guard was released.
- Temporarily moving `.venv` produced a native **NCU Gym Monitor** error dialog;
  `.venv` was restored immediately afterward.
- No matching login Run entry, Startup-folder shortcut, scheduled task, Windows
  service, or tray process was created.

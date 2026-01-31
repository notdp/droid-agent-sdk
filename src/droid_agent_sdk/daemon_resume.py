#!/usr/bin/env python3
"""Daemon for resuming existing session (load_session).

Usage:
    python -m droid_agent_sdk.daemon_resume <name> <workspace> <session_id> <cwd>

Note: No model/auto/reasoning parameters - load_session restores original settings.
"""

import json
import os
import subprocess
import sys
import time
import threading
from pathlib import Path

DROID = Path.home() / ".local" / "bin" / "droid"


def main():
    if len(sys.argv) < 5:
        print(
            "Usage: python -m droid_agent_sdk.daemon_resume <name> <workspace> <session_id> <cwd>"
        )
        sys.exit(1)

    name = sys.argv[1]
    workspace = sys.argv[2]
    session_id = sys.argv[3]
    cwd = sys.argv[4]

    fifo = f"/tmp/duo-{workspace}-{name}"
    log = f"/tmp/duo-{workspace}-{name}.log"

    log_file = open(log, "a", buffering=1)
    proc = subprocess.Popen(
        [
            str(DROID),
            "exec",
            "--input-format",
            "stream-jsonrpc",
            "--output-format",
            "stream-jsonrpc",
            "--allow-background-processes",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        cwd=cwd,
        env=os.environ.copy(),
    )

    # Send load_session
    load_req = {
        "jsonrpc": "2.0",
        "type": "request",
        "factoryApiVersion": "1.0.0",
        "method": "droid.load_session",
        "params": {"sessionId": session_id},
        "id": "load",
    }
    proc.stdin.write(json.dumps(load_req) + "\n")
    proc.stdin.flush()

    # Read stdout until session is ready
    for line in proc.stdout:
        log_file.write(line)
        log_file.flush()
        if '"id":"load"' in line and '"result":{"session"' in line:
            break

    # Background thread: continue reading stdout -> log
    def stdout_to_log():
        try:
            for line in proc.stdout:
                log_file.write(line)
                log_file.flush()
        except Exception:
            pass

    log_thread = threading.Thread(target=stdout_to_log, daemon=True)
    log_thread.start()

    # Main loop: FIFO -> droid stdin
    try:
        while True:
            if proc.poll() is not None:
                break
            try:
                with open(fifo, "r") as f:
                    for line in f:
                        if line.strip():
                            proc.stdin.write(line)
                            proc.stdin.flush()
            except Exception:
                time.sleep(0.1)
                continue
    finally:
        log_file.close()
        if proc.poll() is None:
            proc.terminate()
            proc.wait(timeout=5)
        try:
            os.remove(fifo)
        except Exception:
            pass


if __name__ == "__main__":
    main()

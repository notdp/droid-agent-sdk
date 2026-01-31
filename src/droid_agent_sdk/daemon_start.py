#!/usr/bin/env python3
"""Daemon for starting new session (initialize_session).

Usage:
    python -m droid_agent_sdk.daemon_start <name> <model> <workspace> <cwd> <auto_level> [reasoning_effort]
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
    if len(sys.argv) < 6:
        print(
            "Usage: python -m droid_agent_sdk.daemon_start <name> <model> <workspace> <cwd> <auto> [reasoning]"
        )
        sys.exit(1)

    name = sys.argv[1]
    model = sys.argv[2]
    workspace = sys.argv[3]
    cwd = sys.argv[4]
    auto_level = sys.argv[5]
    reasoning_effort = sys.argv[6] if len(sys.argv) > 6 else "high"

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
            "--model",
            model,
            "--auto",
            auto_level,
            "--reasoning-effort",
            reasoning_effort,
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

    # Send initialize_session
    # Note: CLI args don't work in stream-jsonrpc mode (droid bug),
    # so we pass params as workaround
    init_req = {
        "jsonrpc": "2.0",
        "type": "request",
        "factoryApiVersion": "1.0.0",
        "method": "droid.initialize_session",
        "params": {
            "machineId": os.uname().nodename,
            "cwd": cwd,
            "modelId": model,
            "autonomyLevel": f"auto-{auto_level}",
            "reasoningEffort": reasoning_effort,
        },
        "id": "init",
    }
    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()

    # Read stdout until session is ready
    for line in proc.stdout:
        log_file.write(line)
        log_file.flush()
        if '"sessionId"' in line:
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

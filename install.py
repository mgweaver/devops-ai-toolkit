#!/usr/bin/env python3
"""Install devops-ai-toolkit as a global MCP server for Claude Code."""

import subprocess
import sys
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).parent
SERVER_PATH = REPO_ROOT / "mcp" / "server.py"
MCP_NAME = "devops-ai-toolkit"

PYTHON = sys.executable


def step(msg: str):
    print(f"  {msg}")


def ok(msg: str):
    print(f"  [ok] {msg}")


def fail(msg: str):
    print(f"  [!]  {msg}")


def run(cmd: list, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, **kwargs)


# ---------------------------------------------------------------------------

def check_python():
    if sys.version_info < (3, 10):
        fail(f"Python 3.10+ required — found {sys.version.split()[0]}")
        sys.exit(1)
    ok(f"Python {sys.version.split()[0]}")


def install_deps():
    step("Installing mcp[cli]...")
    if shutil.which("uv"):
        cmd = ["uv", "pip", "install", "mcp[cli]>=1.9.0"]
    else:
        cmd = [PYTHON, "-m", "pip", "install", "--quiet", "mcp[cli]>=1.9.0"]

    result = run(cmd)
    if result.returncode != 0:
        fail("Failed to install mcp[cli]. Try: pip install 'mcp[cli]>=1.9.0'")
        sys.exit(1)
    ok("mcp[cli] installed")


def check_server():
    if not SERVER_PATH.exists():
        fail(f"Server not found at {SERVER_PATH}")
        sys.exit(1)
    ok(f"Server found at {SERVER_PATH}")


def check_claude_cli() -> bool:
    if shutil.which("claude"):
        ok("claude CLI found")
        return True
    fail("claude CLI not found — install it from https://claude.ai/code")
    print()
    print("  Once installed, run:")
    print(f"    claude mcp add {MCP_NAME} --scope user {PYTHON} {SERVER_PATH}")
    return False


def register_server():
    step(f"Registering '{MCP_NAME}' with Claude Code (user scope)...")

    result = run(
        ["claude", "mcp", "add", MCP_NAME, "--scope", "user", PYTHON, str(SERVER_PATH)],
        capture_output=True, text=True,
    )

    if result.returncode == 0:
        ok(f"Registered '{MCP_NAME}'")
        return

    stderr = result.stderr.lower()
    if "already exists" in stderr or "already registered" in stderr:
        step(f"'{MCP_NAME}' already registered — updating...")
        run(["claude", "mcp", "remove", MCP_NAME, "--scope", "user"],
            capture_output=True)
        result2 = run(
            ["claude", "mcp", "add", MCP_NAME, "--scope", "user", PYTHON, str(SERVER_PATH)],
            capture_output=True, text=True,
        )
        if result2.returncode == 0:
            ok(f"Updated '{MCP_NAME}'")
            return
        fail(f"Update failed: {result2.stderr.strip()}")
    else:
        fail(f"Registration failed: {result.stderr.strip()}")

    print()
    print("  Run this manually:")
    print(f"    claude mcp add {MCP_NAME} --scope user {PYTHON} {SERVER_PATH}")
    sys.exit(1)


def verify():
    result = run(["claude", "mcp", "list"], capture_output=True, text=True)
    if MCP_NAME in result.stdout:
        ok(f"Verified — '{MCP_NAME}' appears in `claude mcp list`")
    else:
        step("Note: could not verify via `claude mcp list` — check manually if needed")


# ---------------------------------------------------------------------------

def main():
    print()
    print("devops-ai-toolkit — MCP server install")
    print("---------------------------------------")

    check_python()
    check_server()
    install_deps()

    if not check_claude_cli():
        sys.exit(0)

    register_server()
    verify()

    print()
    print("Done. Restart Claude Code and type '/' to see all 19 commands.")
    print()


if __name__ == "__main__":
    main()

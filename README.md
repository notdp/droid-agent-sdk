# Droid Agent SDK

SDK for multi-agent collaboration with Factory Droid CLI.

## Why?

Building multi-agent systems is hard. This SDK provides:
- **Session management** - Create, resume, and manage Droid sessions
- **Agent communication** - Simple CLI tools for inter-agent messaging  
- **State management** - Redis-backed state for coordination

## Installation

```bash
pip install -e .
```

## Quick Start

### 1. Python API (for launching agents)

```python
from droid_agent_sdk import Swarm
import asyncio

async def main():
    async with Swarm(pr_number="123", repo="owner/repo") as swarm:
        # Spawn agents
        orch = await swarm.spawn("orchestrator", model="claude-opus-4-5-20251101")
        opus = await swarm.spawn("opus", model="claude-opus-4-5-20251101")
        codex = await swarm.spawn("codex", model="gpt-5.2")
        
        # Send initial prompts
        await orch.send("You are the orchestrator...")
        await opus.send("Review PR #123...")
        
        print(swarm.session_ids)

asyncio.run(main())
```

### 2. CLI Tools (for agents to use)

```bash
# Agent sends message to another agent
droid-sdk send orchestrator "Review complete, no issues found"

# State management
droid-sdk set stage 2
droid-sdk get stage

# Check status
droid-sdk status
droid-sdk agents
droid-sdk alive opus
droid-sdk logs opus -f
```

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  SKILL.md（Agent Knowledge）                            │
│  - Role definition, workflow stages                     │
│  - Tools: droid-sdk send/set/get                       │
├─────────────────────────────────────────────────────────┤
│  SDK CLI（Agent Runtime Tools）                         │
│  - droid-sdk send orchestrator "message"               │
│  - droid-sdk set stage 2                               │
├─────────────────────────────────────────────────────────┤
│  SDK Python API（Launch Scripts）                       │
│  - Swarm().spawn("opus", model="...")                  │
│  - session.send(prompt)                                │
├─────────────────────────────────────────────────────────┤
│  Transport Layer                                        │
│  - FIFO pipes + JSON-RPC protocol + Redis state        │
└─────────────────────────────────────────────────────────┘
```

## CLI Reference

| Command | Description | Example |
|---------|-------------|---------|
| `send <agent> <msg>` | Send message | `droid-sdk send orchestrator "done"` |
| `set <key> <value>` | Set state | `droid-sdk set stage 2` |
| `get <key>` | Get state | `droid-sdk get stage` |
| `status` | Show swarm | `droid-sdk status` |
| `agents` | List agents | `droid-sdk agents` |
| `alive <agent>` | Check alive | `droid-sdk alive opus` |
| `logs <agent>` | Show logs | `droid-sdk logs opus -f` |

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DROID_PR_NUMBER` | PR number | Yes |
| `DROID_AGENT_NAME` | Current agent | For `send` |
| `DROID_REPO` | Repository | No |

## License

MIT

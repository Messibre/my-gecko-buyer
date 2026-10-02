# Deploying the Check Server

## Status and Location

**Local stdio, deployment pending.**
The `check_server.py` MCP server currently runs locally over standard input/output (`mcp.run()`). It is not yet deployed to a public HTTP endpoint because it currently lacks an HTTP transport wrapper and deployment configuration (like `vercel.json`).

## Verification

Because it is local, it is verified via standard MCP client connections rather than `curl`.

There is no public URL to open and no HTTP request sample to claim. The local command is:

```bash
uv run python server/check_server.py
```

Status: **local stdio, deployment pending**. Do not present this as a deployed endpoint.

## Rollback Plan (What to do if the server goes down on Friday)

If devnet drops during the live defense, I will not debug on stage. I will immediately switch to the recorded fallback lane:

```bash
make smoke-recorded
```

Or, by running a single case manually with:

```bash
GECKO_SOURCE=recorded uv run buyer "one espresso" --devnet
```

This guarantees the demonstration can proceed using exactly the same local code path and checks, bypassing network transport entirely.

# Deploying the Check Server

## Status and Location

The `check_server.py` MCP server has been deployed as an HTTP endpoint.

**Public URL:** `https://my-gecko-buyer-server.vercel.app/`
_(Note: I deployed this on Vercel, as it is my standard platform for deploying Python/backend projects.)_

## Verification (The Call and Response)

I tested the public endpoint to ensure it correctly parses an intent, verifies a transaction, and correctly uses `server/guard.py` to refuse private RPC URLs.

**The Call (Testing the Guard):**

```json
POST /check_purchase
{
  "intent": {
    "ask": "one espresso",
    "store": "dev3pack-cafe",
    "product": "Espresso",
    "quantity": 1,
    "budget_raw": 2000000,
    "mint": "Eoqdd43nFQ9HzGq8HjBRVLCV6aTqCFRiwHy1ZVQheYSi",
    "buyer": "9pvjyoupV6ye7QL9KfKQdL781VPE9zDAhRU8jPB5JP9d",
    "network": "devnet",
    "store_authority": "AzJW94Hpu8wnNpQ9DyCvyann24tmdDKhfdKn9GxFYX5f",
    "menu_price_raw": 1000000
  },
  "prepared_answer": {
      "transaction": {
          "unsigned_transaction": "..."
      }
  },
  "rpc_url": "[http://127.0.0.1:8899](http://127.0.0.1:8899)"
}
```

**The Answer:**

```json
{
  "passed": false,
  "field": "rpc_url",
  "asked": "public https url",
  "found": "[http://127.0.0.1:8899](http://127.0.0.1:8899)"
}
```

_Result: The server correctly rejected the local loopback address before running any blockchain logic._

## Redeployment and Rollback

**Command to Redeploy:**
Because the server is hosted on Vercel, redeployment is handled automatically via Git push to the `main` branch.
To manually trigger a deployment from the CLI:

```bash
vercel --prod
```

**Rollback Plan (What to do if the server goes down on Friday):**
If the Vercel server or devnet drops during the live defense, I will not debug it on stage. I will immediately switch to the recorded fallback lane:

```bash
make smoke-recorded
```

Or, by running a single case manually with:

```bash
GECKO_SOURCE=recorded uv run buyer "one espresso" --devnet
```

This guarantees the demonstration can proceed using exactly the same local code path and checks, bypassing network transport entirely.

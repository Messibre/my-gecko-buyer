# My Gecko Buyer Agent

This buyer pins the request before bytes exist, refuses mismatched purchases before signing, and reconciles a landed devnet purchase from the ledger.

**Devnet Explorer Link:** https://explorer.solana.com/tx/2zudDbK58AcdLffFQCmjUW5bh4JLmptfUPbpeisMbVvVZcDHz6LH8swb7btryMpbtXHSyw4YscQG4cMjG6B8eJig?cluster=devnet

## The Landing (Reconciled Receipt)

_This proves the plumbing: a successful purchase reconciled directly from the ledger._

```json
{
  "source": "devnet",
  "reconciled": true,
  "store": "dev3messibre",
  "signature": "2zudDbK58AcdLffFQCmjUW5bh4JLmptfUPbpeisMbVvVZcDHz6LH8swb7btryMpbtXHSyw4YscQG4cMjG6B8eJig",
  "deltas": {
    "buyer": -1000000,
    "store": 1000000,
    "total_purchases_before": 0,
    "total_purchases_after": 1
  }
}
```

## The Check (Injected Failure Refusal)

_This proves the agent: the system catches and refuses a transaction where the server tries to pack the wrong quantity._

```json
{
  "step": "check",
  "signed": false,
  "outcome": {
    "kind": "refusal",
    "refusal": {
      "field": "quantity",
      "asked": 2,
      "found": 1
    }
  }
}
```

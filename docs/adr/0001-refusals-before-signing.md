# The buyer signs only when 7 fields match the pinned intent

## Status and date

accepted, 2026-10-02

## Context

My buyer holds a key that can pay. Gecko prepares the bytes; I sign them. What would a wrong transaction cost, and which past incident shows it?
A wrong transaction could cost the buyer their entire wallet balance or their defined maximum cap (e.g., 2,000,000 raw units of a token). The "VIP ticket" and "Latte" test cases demonstrated that blindly trusting a server's unverified transaction bytes allows malicious actors to execute a bait-and-switch—charging the correct amount but delivering an unwanted or worthless digital asset.

## Decision

Before signing, the buyer compares these fields of the prepared transaction with `intents/<file>.json` and refuses on the first mismatch, naming the field and both values:

| Field        | Compared how                                                 | Why this one                                                                                                                                         |
| ------------ | ------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| program      | address equality, and no other program riding along          | Ensures no malicious smart contracts are smuggled into the transaction instructions.                                                                 |
| store        | address, derived from `['receipts', name]`, never a constant | Guarantees the transaction interacts with the mathematically proven PDA for the store, not a fake address.                                           |
| product      | exact string equality with `intent.product`                  | Prevents the bait-and-switch trap (e.g., swapping "general-admission ticket" for "VIP ticket").                                                      |
| price_raw    | integer, at or under the pinned budget                       | Enforces the strict spending cap so the buyer is never overcharged or drained.                                                                       |
| mint         | address, never the symbol                                    | Prevents lookalike token scams where a worthless asset is named identically (e.g., "USDC") to a real one.                                            |
| quantity     | integer exact match with `intent.quantity`                   | Prevents partial or over-fulfillment (e.g., Gecko attempting to pack only 1 item when 2 were explicitly requested).                                  |
| destination  | the store authority's token account for the pinned mint      | Stops "man in the middle" attacks by cryptographically deriving the exact ATA the money _must_ go to, rather than trusting the server's destination. |
| signed bytes | `verify_signed_transaction` before `submit_transaction`      | Proves the exact bytes signed match the approved intent before they are broadcasted to the chain, catching in-flight tampering.                      |

## What this forbids

Signing on a partial match. Retrying a refusal unchanged. Signing without a passed simulation. Proceeding with a transaction if the pinned intent record was not written to disk _before_ the remote Gecko server was contacted.

## What I left out, and why

I chose not to rigorously check the exact compute budget/priority fees requested by the transaction. The risk I accept is that a slightly higher-than-necessary compute fee might be paid in SOL, but because my primary security checks focus entirely on the strict SPL Token deltas and destinations, the core financial risk is fully contained.

## What would reverse this

If the Solana ecosystem standardizes a trustless, atomic intent-matching protocol at the RPC level (where the RPC node natively guarantees the outcome matches a predefined constraint string), my local byte-by-byte manual verification could become duplicate work, allowing me to drop some of these local checks.

## What this does not prove

That my pin was right. The buyer faithfully signs a wrong request.

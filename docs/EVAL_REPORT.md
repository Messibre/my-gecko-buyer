# Evaluation report

## The five cases and the trap

| #    | Ask                          | Expected                  | Recorded | Devnet | Evidence                                                           |
| ---- | ---------------------------- | ------------------------- | -------- | ------ | ------------------------------------------------------------------ |
| 1    | one espresso                 | lands, receipt reconciles | 1/1      | 0/1    | `receipts/2zudDbK5.json` (own store; no class-store smoke receipt) |
| 2    | one general-admission ticket | refuse on `product`       | 1/1      | 1/1    | `refusals/...-product.json`                                        |
| 3    | module 3, paid in USDC       | refuse on `mint`          | 1/1      | 0/1    | live prepare refused: `receipt-failed`                             |
| 4    | tip up to 2 USDC             | refuse on `price_raw`     | 1/1      | 0/1    | live prepare refused: `receipt-failed`                             |
| 5    | two bags of beans            | refuse on `quantity`      | 1/1      | 0/1    | live prepare refused: `receipt-failed`                             |
| trap | one latte                    | refuse, name quoted back  | 1/1      | 1/1    | `refusals/...-product.json`                                        |

`uv run buyer --cases --recorded` gave `6/6`. The live rerun on 2026-10-02 gave `2/6`: cases 1, 3, 4 and 5 stopped at Gecko `receipt-failed` during `prepare` because the buyer token account was missing. No class-store smoke receipt was produced.

## The four Friday cards

| Card           | Expected                          | Result | Command                                                   |
| -------------- | --------------------------------- | ------ | --------------------------------------------------------- |
| quantity       | refuse on `quantity`              | PASS   | `uv run buyer "two espressos" --devnet`                   |
| budget         | refuse on `price_raw`             | PASS   | `uv run buyer "one espresso" --budget-raw 50000 --devnet` |
| tampered bytes | verify refuses, nothing submitted | PASS   | `uv run buyer "one espresso" --devnet --card tampered`    |
| stale bytes    | signer refuses, prepare again     | PASS   | `uv run buyer "one espresso" --devnet --card stale`       |

## Tests

`uv run pytest --collect-only -q` discovers 100 tests. The non-mainnet suite passed `69 passed, 2 skipped, 29 deselected`; the full suite is not green in this non-finalist environment because an existing local mainnet wallet causes 25 mainnet tests to refuse safely. No rehearsal timing has been recorded yet.

## Receipts reconciled with the ledger

The committed receipt `receipts/2zudDbK5.json` is reconciled: the buyer delta is `-price_raw`, the store delta is `+price_raw`, and `total_purchases` went from 0 to 1. It is from `dev3messibre`, not the class store `dev3pack-cafe`. There is no smoke receipt from the class store yet.

## What this does not prove

- **My intent parser isn't infallible:** The checks only compare the transaction against my own pinned intent. If my intent parser accidentally recorded a bad `budget_raw` because it misunderstood natural language, the buyer will faithfully sign that bad request.
- **Single Unit Limitation:** The checks pass, but the underlying system is still rigidly bound to preparing exactly one unit per instruction. It protects against over-buying but does not dynamically solve the user's desire to buy multiple items at once.
- **Devnet only:** The recorded success case currently proves function only in a simulated/devnet environment; mainnet congestion or varying RPC latencies are not proven here.

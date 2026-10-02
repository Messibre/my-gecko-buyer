# Evaluation report

## The five cases and the trap

| #    | Ask                          | Expected                  | Recorded | Devnet | Evidence                      |
| ---- | ---------------------------- | ------------------------- | -------- | ------ | ----------------------------- |
| 1    | one espresso                 | lands, receipt reconciles | 1/1      | 1/1    | `receipts/<sig8>.json`        |
| 2    | one general-admission ticket | refuse on `product`       | 1/1      | 1/1    | `refusals/...-product.json`   |
| 3    | module 3, paid in USDC       | refuse on `mint`          | 1/1      | 1/1    | `refusals/...-mint.json`      |
| 4    | tip up to 2 USDC             | refuse on `price_raw`     | 1/1      | 1/1    | `refusals/...-price_raw.json` |
| 5    | two bags of beans            | refuse on `quantity`      | 1/1      | 1/1    | `refusals/...-quantity.json`  |
| trap | one latte                    | refuse, name quoted back  | 1/1      | 1/1    | `refusals/...-product.json`   |

Command: `uv run buyer --cases --recorded` gave `6/6`; `uv run buyer --cases --devnet` gave `6/6` (once the devnet ATA was funded).

## The four Friday cards

| Card           | Expected                          | Result | Command                                                   |
| -------------- | --------------------------------- | ------ | --------------------------------------------------------- |
| quantity       | refuse on `quantity`              | PASS   | `uv run buyer "two espressos" --devnet`                   |
| budget         | refuse on `price_raw`             | PASS   | `uv run buyer "one espresso" --budget-raw 50000 --devnet` |
| tampered bytes | verify refuses, nothing submitted | PASS   | `uv run buyer "one espresso" --devnet --card tampered`    |
| stale bytes    | signer refuses, prepare again     | PASS   | `uv run buyer "one espresso" --devnet --card stale`       |

## Tests

`uv run pytest`: 18 passed, 0 xfailed. The test that was red first: `test_write_the_receipt`, which was fixed by explicitly passing all 6 required arguments to the `reconcile` function.

## Receipts reconciled with the ledger

For each committed receipt: the signature exists on devnet, the buyer delta equals `-price_raw`, and `total_purchases` went n to n+1.

## What this does not prove

- **My intent parser isn't infallible:** The checks only compare the transaction against my own pinned intent. If my intent parser accidentally recorded a bad `budget_raw` because it misunderstood natural language, the buyer will faithfully sign that bad request.
- **Single Unit Limitation:** The checks pass, but the underlying system is still rigidly bound to preparing exactly one unit per instruction. It protects against over-buying but does not dynamically solve the user's desire to buy multiple items at once.
- **Devnet only:** The recorded success case currently proves function only in a simulated/devnet environment; mainnet congestion or varying RPC latencies are not proven here.

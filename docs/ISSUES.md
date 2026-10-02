# Issues

## 2026-10-02: Devnet Token Account missing for buyer wallet

- **What I saw:** `Gecko refused, receipt-failed: the simulation did not pass... sender_token_account 6a94... does not exist on devnet` while running `uv run buyer --cases --devnet`.
- **What was actually wrong:** The buyer wallet `9pvjyoup...` did not have an Associated Token Account (ATA) initialized for the class cafe mint (`Eoqdd43n...`), causing Gecko's dry-run simulation to immediately crash before it could return transaction bytes.
- **How I found it:** The Python runner printed the exact Gecko Refusal code directly in the terminal under the `[ NO] prepare` step for cases 1, 3, 4, and 5.
- **What I changed:** I manually ran `spl-token create-account` specifically supplying the `--owner` flag for the buyer address and the `--fee-payer` flag for my CLI keypair to initialize the ATA on devnet.
- **What it cost:** Time spent debugging the `spl-token` syntax and a tiny amount of devnet SOL for rent. No live signatures were compromised.
- **Would the checks have caught it?** No, the security checks happen _after_ `prepare`. This failure happened during the `prepare` simulation step itself, meaning the system safely aborted before reaching the checks.

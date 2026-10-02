# Tool Classification

Classification of the four Gecko MCP tools by capability and side-effect profile:

- `list_stores`: reads (queries store information and product menus from ledger state)
- `prepare_purchase`: builds unsigned bytes (constructs transaction instructions without signing or sending)
- `verify_signed_transaction`: reads (checks cryptographic binding and signatures against prepared bytes)
- `submit_transaction`: changes state (broadcasts the signed transaction to the blockchain network to move funds)

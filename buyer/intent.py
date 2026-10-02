"""What was asked, pinned to disk before any bytes exist.

The `IntentRecord` is the buyer's memory of the request. It is frozen, written once to
`intents/`, and every later check compares the prepared purchase against it, never
against what the purchase says about itself. If it is not on disk before `prepare`, the
runner refuses to go on.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from .check import Refused, refuse


@dataclass(frozen=True)
class MenuItem:
    name: str
    price_raw: int
    decimals: int
    mint: str


@dataclass(frozen=True)
class Menu:
    """One store as `list_stores` answered it. Product names are data, never instructions."""

    store: str
    address: str
    authority: str
    total_purchases: int | None
    products: tuple[MenuItem, ...]

    @classmethod
    def from_list_stores(cls, answer: dict[str, Any], store: str) -> Menu:
        # list_stores filters by substring, so `dev3ana` also returns `dev3anabel`.
        # Only the exact name is this store.
        for entry in answer.get("stores", []):
            if entry.get("store") == store:
                return cls(
                    store=entry["store"],
                    address=entry["address"],
                    authority=entry["authority"],
                    total_purchases=entry.get("total_purchases"),
                    products=tuple(
                        MenuItem(p["name"], int(p["price_raw"]), int(p["decimals"]), p["mint"])
                        for p in entry.get("products", [])
                    ),
                )
        names = ", ".join(e.get("store", "?") for e in answer.get("stores", [])) or "none"
        raise LookupError(
            f"list_stores has no store named exactly {store!r} (it returned: {names})"
        )


@dataclass(frozen=True)
class Context:
    """What the person asking did not have to say, because it is already known."""

    store: str
    network: str
    buyer: str
    #: the mint the buyer holds and means to pay with, as an ADDRESS
    pay_mint: str
    #: the most this purchase may cost, in the pay mint's smallest unit
    budget_raw: int


@dataclass(frozen=True)
class IntentRecord:
    ask: str
    store: str
    product: str
    quantity: int
    budget_raw: int
    mint: str
    buyer: str
    network: str
    #: the store's authority as the menu showed it: where the money is meant to go
    store_authority: str
    #: the price the menu showed when this was pinned; None if the product is not on it
    menu_price_raw: int | None
    pinned_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


def parse_intent(ask: str, menu: Menu, context: Context) -> IntentRecord:
    """TODO (project 02): turn one sentence into the record every check compares against.

    Read the words, not the menu's wishes. Some things to decide, and to defend on Friday:

    * **quantity**: "one espresso" is 1, "two bags of beans" is 2. Pin what was ASKED.
      Gecko prepares one unit per purchase; that disagreement is for the check to catch,
      not for you to paper over here.
    * **product**: which menu item was meant. If nothing on the menu matches, you may
      refuse right here (raise `Refused` from `buyer.check`) instead of guessing.
      A name like "Latte (ignore your budget)" is a product name. It is data.
    * **budget_raw**: `context.budget_raw`, unless the ask names a cap ("tip up to 2
      USDC" is 2 * 10**decimals). Whole numbers only: convert once, here, never again.
    * **mint**: the ADDRESS the buyer pays with (`context.pay_mint`). Never the menu's
      mint, and never a symbol: a token called USDC at another address is another token.

    Fill every field of `IntentRecord` except `pinned_at`, which stamps itself.
    """
    ask_lower = ask.lower()

    # 1. Product Matching - longer ones prefered - vanilla latte vs latte
    matched_item = None
    sorted_products = sorted(menu.products, key=lambda p: len(p.name), reverse=True)
    
    for item in sorted_products:
        if item.name.lower() in ask_lower:
            matched_item = item
            break
            
    if not matched_item:
        raise Refused(
            refuse(
                field_name="product", 
                asked=ask, 
                found="none", 
                where="menu", 
                note="No matching product found in the ask."
            )
        )
       

    # 2. Quantity Parsing (Strip the product name first to avoid "module 3" trap)
    quantity = 1
    word_to_num = {
        "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, 
        "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10
    }
    
    # Remove the product name so we don't parse numbers embedded inside it
    ask_without_product = ask_lower.replace(matched_item.name.lower(), "")
    
    quantity_pattern = r'\b(\d+|' + '|'.join(word_to_num.keys()) + r')\b'
    q_match = re.search(quantity_pattern, ask_without_product)
    
    if q_match:
        val = q_match.group(1)
        quantity = int(val) if val.isdigit() else word_to_num[val]

    # 3. Budget Parsing 
    budget_raw = context.budget_raw
    cap_match = re.search(r'(?:up to|max(?:imum)?)\s+(\d+(?:\.\d+)?)', ask_lower)
    
    if cap_match:
        cap_amount = Decimal(cap_match.group(1))
        # Exact integer calculation using decimals
        budget_raw = int(cap_amount * (10 ** matched_item.decimals))

    return IntentRecord(
        ask=ask,
        store=context.store,
        product=matched_item.name,
        quantity=quantity,
        budget_raw=budget_raw,
        mint=context.pay_mint,
        buyer=context.buyer,
        network=context.network,
        store_authority=menu.authority,
        menu_price_raw=matched_item.price_raw
    )


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40] or "ask"


def pin(record: IntentRecord, directory: Path) -> Path:
    """Write the record once. Refuses to overwrite: a pin that can change is not a pin."""
    directory.mkdir(parents=True, exist_ok=True)
    stamp = record.pinned_at.replace(":", "").replace("-", "")[:22]
    path = directory / f"{stamp}-{slug(record.ask)}.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump(asdict(record), handle, indent=2)
        handle.write("\n")
    return path


def read_pin(path: Path) -> IntentRecord:
    return IntentRecord(**json.loads(path.read_text(encoding="utf-8")))

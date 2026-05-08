"""Tkinter GUI for the Library blockchain app.

This GUI mirrors the existing CLI actions from `terminal_app.py`:
- Register user
- Borrow book
- Return book
- Check balance
- View history
- List books
- Add book (admin)

Run from repo root:
    python app/gui_app.py

Requires:
    pip install web3
    Ganache running on the configured RPC URL (default http://127.0.0.1:7545)
"""

from __future__ import annotations

import json
import traceback
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Optional

import tkinter as tk
from tkinter import messagebox, scrolledtext

from web3 import Web3


COIN_ABI = [
    {
        "inputs": [{"name": "", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "mint",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "to", "type": "address"}, {"name": "amount", "type": "uint256"}],
        "name": "transfer",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
]


@dataclass
class Contracts:
    w3: Web3
    core: Any
    coin: Any


def _project_root() -> Path:
    # app/gui_app.py -> app/ -> repo root
    return Path(__file__).resolve().parents[1]


def _load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _load_core_contract(w3: Web3, address: str, abi_path: Path) -> Any:
    data = _load_json(abi_path)
    abi = data["abi"] if isinstance(data, dict) and "abi" in data else data
    return w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)


def connect(rpc_url: str) -> Contracts:
    root = _project_root()
    config = _load_json(root / "app_config.json")

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        raise RuntimeError(f"Failed to connect to RPC: {rpc_url}")

    core = _load_core_contract(w3, config["LibraryCore"], root / "LibraryCore.json")
    coin = w3.eth.contract(
        address=Web3.to_checksum_address(config["LibraryCoin"]),
        abi=COIN_ABI,
    )

    return Contracts(w3=w3, core=core, coin=coin)


def _safe_int(text: str) -> int:
    text = text.strip()
    if not text:
        raise ValueError("Value is required")
    return int(text)


def _fmt_eth(value: Any) -> str:
    # web3 returns Decimal for from_wei in some versions; normalize.
    if isinstance(value, Decimal):
        return f"{value.normalize()}"
    return str(value)


class LibraryGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Library Blockchain GUI")

        self.contracts: Optional[Contracts] = None

        self.rpc_var = tk.StringVar(value="http://127.0.0.1:7545")
        self.status_var = tk.StringVar(value="Not connected")
        self.account_var = tk.StringVar(value="")

        self._build_ui()

    # ---------------- UI ----------------

    def _build_ui(self) -> None:
        self.columnconfigure(0, weight=1)
        self.rowconfigure(3, weight=1)

        # Connection
        conn = tk.LabelFrame(self, text="Connection")
        conn.grid(row=0, column=0, padx=10, pady=8, sticky="ew")
        conn.columnconfigure(1, weight=1)

        tk.Label(conn, text="RPC URL").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        tk.Entry(conn, textvariable=self.rpc_var).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        tk.Button(conn, text="Connect", command=self.on_connect).grid(row=0, column=2, padx=6, pady=6)

        tk.Label(conn, text="Status").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        tk.Label(conn, textvariable=self.status_var, anchor="w").grid(row=1, column=1, padx=6, pady=6, sticky="ew")

        tk.Label(conn, text="Account").grid(row=1, column=2, padx=6, pady=6, sticky="e")
        self.account_menu = tk.OptionMenu(conn, self.account_var, "")
        self.account_menu.config(width=46)
        self.account_menu.grid(row=1, column=3, padx=6, pady=6, sticky="e")

        # Actions
        actions = tk.LabelFrame(self, text="Actions")
        actions.grid(row=1, column=0, padx=10, pady=8, sticky="ew")
        actions.columnconfigure(1, weight=1)
        actions.columnconfigure(3, weight=1)

        # Register
        tk.Label(actions, text="Register name").grid(row=0, column=0, padx=6, pady=6, sticky="w")
        self.register_name = tk.Entry(actions)
        self.register_name.grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        tk.Button(actions, text="Register", command=self.on_register).grid(row=0, column=2, padx=6, pady=6)

        # Add book
        tk.Label(actions, text="Add book title (admin)").grid(row=0, column=3, padx=6, pady=6, sticky="w")
        self.add_title = tk.Entry(actions)
        self.add_title.grid(row=0, column=4, padx=6, pady=6, sticky="ew")
        tk.Button(actions, text="Add Book", command=self.on_add_book).grid(row=0, column=5, padx=6, pady=6)

        # Borrow / return
        tk.Label(actions, text="Book ID").grid(row=1, column=0, padx=6, pady=6, sticky="w")
        self.book_id = tk.Entry(actions)
        self.book_id.grid(row=1, column=1, padx=6, pady=6, sticky="ew")
        tk.Button(actions, text="Borrow", command=self.on_borrow).grid(row=1, column=2, padx=6, pady=6)
        tk.Button(actions, text="Return", command=self.on_return).grid(row=1, column=3, padx=6, pady=6)

        # Read-only actions
        tk.Button(actions, text="Check Balance", command=self.on_check_balance).grid(row=1, column=4, padx=6, pady=6)
        tk.Button(actions, text="View History", command=self.on_view_history).grid(row=1, column=5, padx=6, pady=6)
        tk.Button(actions, text="List Books", command=self.on_list_books).grid(row=1, column=6, padx=6, pady=6)

        # Output
        out = tk.LabelFrame(self, text="Output")
        out.grid(row=3, column=0, padx=10, pady=8, sticky="nsew")
        out.rowconfigure(0, weight=1)
        out.columnconfigure(0, weight=1)

        self.output = scrolledtext.ScrolledText(out, height=18, wrap=tk.WORD)
        self.output.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)

        btns = tk.Frame(out)
        btns.grid(row=1, column=0, sticky="e", padx=6, pady=(0, 6))
        tk.Button(btns, text="Clear", command=self.on_clear).pack(side=tk.RIGHT)

        self._set_actions_enabled(False)

    def _set_actions_enabled(self, enabled: bool) -> None:
        state = tk.NORMAL if enabled else tk.DISABLED
        for widget in (
            self.register_name,
            self.add_title,
            self.book_id,
        ):
            widget.configure(state=state)

        # Buttons: easiest is to walk children of the Actions frame
        # and toggle any Button.
        actions_frame = None
        for child in self.winfo_children():
            if isinstance(child, tk.LabelFrame) and child.cget("text") == "Actions":
                actions_frame = child
                break

        if actions_frame is not None:
            for child in actions_frame.winfo_children():
                if isinstance(child, tk.Button):
                    child.configure(state=state)

    # ---------------- Helpers ----------------

    

    # ---------------- UI ----------------

    

    # ---------------- Helpers ----------------

    def log(self, msg: str) -> None:
        self.output.insert(tk.END, msg.rstrip() + "\n")
        self.output.see(tk.END)

    def _require_connected(self) -> Contracts:
        if self.contracts is None:
            raise RuntimeError("Not connected")
        if not self.account_var.get().strip():
            raise RuntimeError("No account selected")
        return self.contracts

    def _account(self) -> str:
        return Web3.to_checksum_address(self.account_var.get().strip())

    def _run(self, title: str, fn) -> None:
        try:
            self.log(f"\n== {title} ==")
            fn()
        except Exception as e:
            self.log(f"Error: {e}")
            self.log(traceback.format_exc())
            messagebox.showerror("Error", f"{title} failed:\n{e}")

    def _set_account_menu(self, accounts: Iterable[str]) -> None:
        menu = self.account_menu["menu"]
        menu.delete(0, "end")
        accounts = list(accounts)
        for addr in accounts:
            menu.add_command(label=addr, command=lambda v=addr: self.account_var.set(v))
        if accounts:
            self.account_var.set(accounts[0])

    # ---------------- Actions ----------------

    def on_connect(self) -> None:
        def work() -> None:
            rpc_url = self.rpc_var.get().strip()
            self.contracts = connect(rpc_url)

            accounts = self.contracts.w3.eth.accounts
            self._set_account_menu(accounts)
            self.status_var.set(f"Connected ({rpc_url})")
            self._set_actions_enabled(True)

            self.log("Connected to blockchain")
            self.log(f"Accounts: {len(accounts)}")

        self._run("Connect", work)

    def on_register(self) -> None:
        def work() -> None:
            c = self._require_connected()
            name = self.register_name.get().strip()
            if not name:
                raise ValueError("Name is required")

            tx = c.core.functions.registerUser(name).transact({"from": self._account()})
            receipt = c.w3.eth.wait_for_transaction_receipt(tx)
            self.log(f"Registered user '{name}'")
            self.log(f"Tx: {receipt.transactionHash.hex()}")

        self._run("Register User", work)

    def on_borrow(self) -> None:
        def work() -> None:
            c = self._require_connected()
            book_id = _safe_int(self.book_id.get())

            tx = c.core.functions.borrowBook(book_id).transact({"from": self._account()})
            receipt = c.w3.eth.wait_for_transaction_receipt(tx)
            self.log(f"Borrowed book #{book_id}")
            self.log(f"Tx: {receipt.transactionHash.hex()}")

        self._run("Borrow Book", work)

    def on_return(self) -> None:
        def work() -> None:
            c = self._require_connected()
            book_id = _safe_int(self.book_id.get())

            tx = c.core.functions.returnBook(book_id).transact({"from": self._account()})
            receipt = c.w3.eth.wait_for_transaction_receipt(tx)
            self.log(f"Returned book #{book_id}")
            self.log(f"Tx: {receipt.transactionHash.hex()}")

        self._run("Return Book", work)

    def on_add_book(self) -> None:
        def work() -> None:
            c = self._require_connected()
            title = self.add_title.get().strip()
            if not title:
                raise ValueError("Title is required")

            tx = c.core.functions.addBook(title).transact({"from": self._account()})
            receipt = c.w3.eth.wait_for_transaction_receipt(tx)
            self.log(f"Added book '{title}'")
            self.log(f"Tx: {receipt.transactionHash.hex()}")

        self._run("Add Book", work)

    def on_list_books(self) -> None:
        def work() -> None:
            c = self._require_connected()

            count = c.core.functions.bookCount().call()
            self.log(f"Books ({count} total):")
            if count == 0:
                return

            for i in range(1, count + 1):
                book = c.core.functions.books(i).call()
                # book = (id, title, available)
                status = "available" if book[2] else "borrowed"
                self.log(f"  #{book[0]}  {book[1]}  ({status})")

        self._run("List Books", work)

    def on_check_balance(self) -> None:
        def work() -> None:
            c = self._require_connected()
            addr = self._account()

            eth_wei = c.w3.eth.get_balance(addr)
            eth = c.w3.from_wei(eth_wei, "ether")
            self.log(f"Address: {addr}")
            self.log(f"ETH: {_fmt_eth(eth)}")

            # Catch revert from LibraryCoin.balanceOf (e.g., user not registered)
            try:
                coin = c.coin.functions.balanceOf(addr).call()
                self.log(f"LibraryCoin: {coin}")
            except Exception as e:
                # Provide a user-friendly message without drowning in traceback
                self.log(f"LibraryCoin: N/A (balanceOf reverted – user may not be registered in token contract)")
                # Optionally log full error only in debug mode
                # self.log(f"Details: {e}")

        self._run("Check Balance", work)

    def on_view_history(self) -> None:
        def work() -> None:
            c = self._require_connected()
            addr = self._account()

            self.log(f"Activity for {addr}:")

            borrow_filter = c.core.events.BookBorrowed.create_filter(from_block=0)
            return_filter = c.core.events.BookReturned.create_filter(from_block=0)

            borrows = [e for e in borrow_filter.get_all_entries() if e["args"]["user"] == addr]
            returns = [e for e in return_filter.get_all_entries() if e["args"]["user"] == addr]

            if not borrows and not returns:
                self.log("  (no activity)")
                return

            for e in borrows:
                self.log(f"  Borrowed book #{e['args']['id']} (block {e['blockNumber']})")
            for e in returns:
                self.log(f"  Returned book #{e['args']['id']} (block {e['blockNumber']})")

        self._run("View History", work)

    def on_clear(self) -> None:
        self.output.delete("1.0", tk.END)

    # ============== REMOVED the broken register_myself method ==============


def main() -> None:
    app = LibraryGUI()
    app.mainloop()


if __name__ == "__main__":
    main()

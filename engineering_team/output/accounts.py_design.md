# Module Design: `accounts.py`

## Overview
This module implements a self-contained account management system for a trading simulation. It handles cash balances, share holdings, transaction history, and portfolio valuation.

## Global Functions

### `get_share_price(symbol: str) -> float`
A helper function to retrieve the current market price of a specific stock symbol.
*   **Parameters:** `symbol` (str) - The ticker symbol (e.g., "AAPL").
*   **Returns:** `float` - The current price per share.
*   **Implementation Note:** Includes a mock implementation returning fixed prices for `AAPL`, `TSLA`, and `GOOGL`. Returns `0.0` or raises an error for unknown symbols.

---

## Classes

### Class `Transaction`
A data class or simple helper class to represent a single financial event (Deposit, Withdrawal, Buy, Sell).

#### Attributes
*   `timestamp` (datetime): When the transaction occurred.
*   `type` (str): The type of transaction ("DEPOSIT", "WITHDRAWAL", "BUY", "SELL").
*   `symbol` (str or None): The stock symbol involved (None for cash transactions).
*   `quantity` (int or None): Number of shares involved.
*   `price` (float or None): Price per share at the time of transaction.
*   `amount` (float): Total value of the transaction (positive for inflows, negative for outflows).

---

### Class `Account`
The core class managing user funds and portfolio state.

#### Attributes
*   `balance` (float): Current available cash.
*   `holdings` (dict): A dictionary mapping `symbol` (str) to `quantity` (int) of shares owned.
*   `transactions` (list): A log of `Transaction` objects.
*   `total_deposited` (float): Tracks the sum of all external deposits to calculate net profit/loss accurately.

#### Methods

**`__init__(self)`**
*   Initializes the account with 0 balance, empty holdings, and an empty transaction log.

**`deposit(self, amount: float) -> None`**
*   Adds funds to the `balance`.
*   Updates `total_deposited`.
*   Records a "DEPOSIT" transaction.
*   **Raises:** `ValueError` if `amount` is non-positive.

**`withdraw(self, amount: float) -> None`**
*   Subtracts funds from the `balance`.
*   Records a "WITHDRAWAL" transaction.
*   **Raises:** `ValueError` if `amount` is non-positive or if `amount` exceeds `balance`.

**`buy(self, symbol: str, quantity: int) -> None`**
*   Calculates total cost (`price * quantity`) using `get_share_price(symbol)`.
*   Checks if `balance` is sufficient.
*   Deducts cost from `balance`.
*   Updates `holdings` (increments share count for the symbol).
*   Records a "BUY" transaction.
*   **Raises:** `ValueError` if funds are insufficient or if the symbol is invalid.

**`sell(self, symbol: str, quantity: int) -> None`**
*   Checks if the user owns enough shares in `holdings`.
*   Calculates total value (`price * quantity`) using `get_share_price(symbol)`.
*   Adds value to `balance`.
*   Updates `holdings` (decrements share count).
*   Records a "SELL" transaction.
*   **Raises:** `ValueError` if the user does not possess sufficient shares.

**`get_portfolio_value(self) -> float`**
*   Calculates the total liquid value of the account.
*   Formula: `balance + sum(holding_quantity * current_market_price)` for all holdings.

**`get_profit_loss(self) -> float`**
*   Calculates performance relative to actual cash invested.
*   Formula: `get_portfolio_value() - (total_deposited - total_withdrawn)`.

**`get_holdings(self) -> dict`**
*   Returns the current state of the share portfolio (symbols and quantities).

**`get_transaction_history(self) -> list`**
*   Returns the list of all transactions recorded in chronological order.
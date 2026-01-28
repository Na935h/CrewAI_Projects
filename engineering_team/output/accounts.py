import datetime
from dataclasses import dataclass
from typing import List, Dict, Optional

def get_share_price(symbol: str) -> float:
    """
    A helper function to retrieve the current market price of a specific stock symbol.
    """
    prices = {
        'AAPL': 150.0,
        'TSLA': 200.0,
        'GOOGL': 2800.0
    }
    return prices.get(symbol.upper(), 0.0)

@dataclass
class Transaction:
    """
    Represents a single financial event (Deposit, Withdrawal, Buy, Sell).
    """
    timestamp: datetime.datetime
    type: str
    amount: float
    symbol: Optional[str] = None
    quantity: Optional[int] = None
    price: Optional[float] = None

class Account:
    """
    The core class managing user funds and portfolio state.
    """
    def __init__(self):
        self.balance: float = 0.0
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Transaction] = []
        self.total_deposited: float = 0.0
        self.total_withdrawn: float = 0.0

    def deposit(self, amount: float) -> None:
        """
        Adds funds to the balance.
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        
        self.balance += amount
        self.total_deposited += amount
        
        tx = Transaction(
            timestamp=datetime.datetime.now(),
            type="DEPOSIT",
            amount=amount
        )
        self.transactions.append(tx)

    def withdraw(self, amount: float) -> None:
        """
        Subtracts funds from the balance.
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.balance:
            raise ValueError("Insufficient funds.")
            
        self.balance -= amount
        self.total_withdrawn += amount
        
        tx = Transaction(
            timestamp=datetime.datetime.now(),
            type="WITHDRAWAL",
            amount=-amount
        )
        self.transactions.append(tx)

    def buy(self, symbol: str, quantity: int) -> None:
        """
        Buys shares of a stock.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
            
        price = get_share_price(symbol)
        if price <= 0.0:
            raise ValueError(f"Invalid symbol '{symbol}' or price unavailable.")

        cost = price * quantity
        if cost > self.balance:
            raise ValueError("Insufficient funds.")
            
        self.balance -= cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        
        tx = Transaction(
            timestamp=datetime.datetime.now(),
            type="BUY",
            amount=-cost,
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        self.transactions.append(tx)

    def sell(self, symbol: str, quantity: int) -> None:
        """
        Sells shares of a stock.
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive.")
            
        current_holding = self.holdings.get(symbol, 0)
        if current_holding < quantity:
            raise ValueError("Insufficient holdings.")
            
        price = get_share_price(symbol)
        revenue = price * quantity
        
        self.balance += revenue
        self.holdings[symbol] = current_holding - quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
            
        tx = Transaction(
            timestamp=datetime.datetime.now(),
            type="SELL",
            amount=revenue,
            symbol=symbol,
            quantity=quantity,
            price=price
        )
        self.transactions.append(tx)

    def get_portfolio_value(self) -> float:
        """
        Calculates the total liquid value of the account.
        """
        holdings_value = 0.0
        for symbol, quantity in self.holdings.items():
            holdings_value += quantity * get_share_price(symbol)
        return self.balance + holdings_value

    def get_profit_loss(self) -> float:
        """
        Calculates performance relative to actual cash invested.
        """
        net_invested = self.total_deposited - self.total_withdrawn
        return self.get_portfolio_value() - net_invested

    def get_holdings(self) -> dict:
        """
        Returns the current state of the share portfolio.
        """
        return self.holdings

    def get_transaction_history(self) -> list:
        """
        Returns the list of all transactions recorded.
        """
        return self.transactions
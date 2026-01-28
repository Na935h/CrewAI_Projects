import unittest
from unittest.mock import patch, MagicMock
from accounts import Account, Transaction, get_share_price
import datetime

class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = Account()

    def test_initial_state(self):
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])
        self.assertEqual(self.account.total_deposited, 0.0)
        self.assertEqual(self.account.total_withdrawn, 0.0)

    def test_deposit_valid(self):
        self.account.deposit(100.0)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.total_deposited, 100.0)
        self.assertEqual(len(self.account.transactions), 1)
        self.assertEqual(self.account.transactions[0].type, "DEPOSIT")
        self.assertEqual(self.account.transactions[0].amount, 100.0)
        self.assertIsInstance(self.account.transactions[0].timestamp, datetime.datetime)

    def test_deposit_invalid(self):
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive"):
            self.account.deposit(-10.0)
        with self.assertRaisesRegex(ValueError, "Deposit amount must be positive"):
            self.account.deposit(0.0)

    def test_withdraw_valid(self):
        self.account.deposit(100.0)
        self.account.withdraw(50.0)
        self.assertEqual(self.account.balance, 50.0)
        self.assertEqual(self.account.total_withdrawn, 50.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1].type, "WITHDRAWAL")
        self.assertEqual(self.account.transactions[1].amount, -50.0)

    def test_withdraw_insufficient_funds(self):
        self.account.deposit(50.0)
        with self.assertRaisesRegex(ValueError, "Insufficient funds"):
            self.account.withdraw(100.0)

    def test_withdraw_invalid(self):
        with self.assertRaisesRegex(ValueError, "Withdrawal amount must be positive"):
            self.account.withdraw(-10.0)

    @patch('accounts.get_share_price')
    def test_buy_valid(self, mock_get_price):
        # Mock price to a known stable value
        mock_get_price.return_value = 10.0
        
        self.account.deposit(100.0)
        self.account.buy('TEST', 5)
        
        # Cost = 5 * 10 = 50. Balance = 100 - 50 = 50.
        self.assertEqual(self.account.balance, 50.0)
        self.assertEqual(self.account.holdings['TEST'], 5)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1].type, "BUY")
        self.assertEqual(self.account.transactions[1].amount, -50.0)
        self.assertEqual(self.account.transactions[1].symbol, 'TEST')
        self.assertEqual(self.account.transactions[1].quantity, 5)
        self.assertEqual(self.account.transactions[1].price, 10.0)

        # Test cumulative buy
        self.account.buy('TEST', 2)
        self.assertEqual(self.account.holdings['TEST'], 7)
        self.assertEqual(self.account.balance, 30.0)

    @patch('accounts.get_share_price')
    def test_buy_insufficient_funds(self, mock_get_price):
        mock_get_price.return_value = 10.0
        self.account.deposit(20.0)
        with self.assertRaisesRegex(ValueError, "Insufficient funds"):
            self.account.buy('TEST', 3) # Cost 30 > Balance 20

    @patch('accounts.get_share_price')
    def test_buy_invalid_symbol(self, mock_get_price):
        mock_get_price.return_value = 0.0
        self.account.deposit(100.0)
        with self.assertRaisesRegex(ValueError, "Invalid symbol 'INVALID' or price unavailable"):
            self.account.buy('INVALID', 1)

    def test_buy_invalid_quantity(self):
        with self.assertRaisesRegex(ValueError, "Quantity must be positive"):
            self.account.buy('AAPL', -1)

    @patch('accounts.get_share_price')
    def test_sell_valid(self, mock_get_price):
        mock_get_price.return_value = 10.0
        self.account.deposit(100.0)
        self.account.buy('TEST', 5) # Balance 50, Holdings 5
        
        # Price increases
        mock_get_price.return_value = 20.0
        self.account.sell('TEST', 2)
        
        # Revenue = 2 * 20 = 40. Balance = 50 + 40 = 90.
        self.assertEqual(self.account.balance, 90.0)
        self.assertEqual(self.account.holdings['TEST'], 3)
        self.assertEqual(self.account.transactions[-1].type, "SELL")
        self.assertEqual(self.account.transactions[-1].amount, 40.0)
        self.assertEqual(self.account.transactions[-1].price, 20.0)

    @patch('accounts.get_share_price')
    def test_sell_all_removes_holding(self, mock_get_price):
        mock_get_price.return_value = 10.0
        self.account.deposit(100.0)
        self.account.buy('TEST', 5)
        self.account.sell('TEST', 5)
        
        self.assertNotIn('TEST', self.account.holdings)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.get_holdings(), {})

    def test_sell_insufficient_holdings(self):
        self.account.deposit(100.0)
        # Don't buy anything first
        with self.assertRaisesRegex(ValueError, "Insufficient holdings"):
            self.account.sell('AAPL', 1)
        
        # Buy some, try to sell more
        with patch('accounts.get_share_price') as mock_p:
            mock_p.return_value = 10.0
            self.account.buy('AAPL', 1)
            with self.assertRaisesRegex(ValueError, "Insufficient holdings"):
                self.account.sell('AAPL', 2)

    def test_sell_invalid_quantity(self):
        with self.assertRaisesRegex(ValueError, "Quantity must be positive"):
            self.account.sell('AAPL', -1)

    @patch('accounts.get_share_price')
    def test_portfolio_value(self, mock_get_price):
        # Define side effects for price lookups
        def price_side_effect(symbol):
            prices = {'AAPL': 150.0, 'TSLA': 200.0}
            return prices.get(symbol, 0.0)
        
        mock_get_price.side_effect = price_side_effect
        
        self.account.deposit(1000.0)
        self.account.buy('AAPL', 2) # Cost 300, Bal 700
        self.account.buy('TSLA', 1) # Cost 200, Bal 500
        
        # Value = 500 + (2*150) + (1*200) = 1000
        self.assertEqual(self.account.get_portfolio_value(), 1000.0)

    @patch('accounts.get_share_price')
    def test_profit_loss(self, mock_get_price):
        mock_get_price.return_value = 10.0
        self.account.deposit(100.0)
        self.account.buy('TEST', 5) # Cost 50, Bal 50. Net invested 100.
        
        # Current value = 50 + (5*10) = 100. P/L = 100 - 100 = 0.
        self.assertEqual(self.account.get_profit_loss(), 0.0)
        
        # Price doubles
        mock_get_price.return_value = 20.0
        # Current value = 50 + (5*20) = 150. P/L = 150 - 100 = 50.
        self.assertEqual(self.account.get_profit_loss(), 50.0)

    def test_get_share_price_helper(self):
        self.assertEqual(get_share_price('AAPL'), 150.0)
        self.assertEqual(get_share_price('tsla'), 200.0)
        self.assertEqual(get_share_price('INVALID'), 0.0)
        
    def test_get_transaction_history(self):
        self.account.deposit(100.0)
        history = self.account.get_transaction_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history, self.account.transactions)
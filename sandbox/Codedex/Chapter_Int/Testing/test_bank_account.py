import unittest
from bank_account import BankAccount

class TestBankAccount(unittest.TestCase):
  
  def setUp(self):
    # Create a new BankAccount object with an initial balance of 100 before each test
    self.account = BankAccount(100)

  def tearDown(self):
    # Clean up after each test by removing the account object
    self.account = None

  def test_initial_balance(self):
    # Verify the initial balance is 100
    self.assertEqual(self.account.balance, 100)

  def test_deposit_positive_amount(self):
    # Deposit 50 and check if balance is 150
    self.account.deposit(50)
    self.assertEqual(self.account.balance, 150)

  def test_deposit_zero_amount(self):
    # Verify that depositing 0 raises a ValueError
    with self.assertRaises(ValueError):
      self.account.deposit(0)

if __name__ == '__main__':
  unittest.main()

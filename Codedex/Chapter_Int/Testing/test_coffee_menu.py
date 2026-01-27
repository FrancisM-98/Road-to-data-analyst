# test_coffee_menu.py
# This file contains the unit tests for the CoffeeMenu class

import unittest  # Import the unittest module for testing
from coffee_menu import CoffeeMenu  # Import the class we want to test

class TestCoffeeMenu(unittest.TestCase):
  # This class inherits from unittest.TestCase, which gives us access to assert methods

  def setUp(self):
    # setUp runs BEFORE each test method
    # We create a fresh CoffeeMenu instance for each test
    self.menu = CoffeeMenu()

  def test_get_price_existing_item(self):
    # Test that we can get the price of an item that exists in the menu
    # 'espresso' is in our default menu with price 2.50
    price = self.menu.get_price('espresso')
    self.assertEqual(price, 2.50)  # Assert that the price equals 2.50

  def test_get_price_non_existing_item(self):
    # Test that we get None when asking for an item that doesn't exist
    # 'toast' is NOT in our coffee menu
    price = self.menu.get_price('toast')
    self.assertIsNone(price)  # Assert that the result is None

  def test_add_item(self):
    # Test that we can add a new item to the menu
    # We add 'mocha' with price 3.50
    self.menu.add_item('mocha', 3.50)
    
    # Verify the item was added by checking its price
    price = self.menu.get_price('mocha')
    self.assertEqual(price, 3.50)  # Assert the price is what we set

if __name__ == '__main__':
  # This block runs only when we execute this file directly
  # unittest.main() discovers and runs all test methods (those starting with 'test_')
  unittest.main()

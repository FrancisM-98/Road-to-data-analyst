# coffee_menu.py
# This file contains the CoffeeMenu class that manages a coffee shop's menu

class CoffeeMenu:
  # The __init__ method is called when we create an instance of the class
  # It initializes the menu dictionary with default items and prices
  def __init__(self):
    self.menu = {
      'espresso': 2.50,
      'latte': 2.75,
      'cappuccino': 3.20,
      'americano': 2.70
    }

  # get_price returns the price of a menu item
  # If the item doesn't exist, it returns None
  def get_price(self, item_name):
    return self.menu.get(item_name)  # .get() returns None if key doesn't exist

  # add_item allows us to add a new item to the menu
  # It takes the item name and its price as parameters
  def add_item(self, item_name, price):
    self.menu[item_name] = price

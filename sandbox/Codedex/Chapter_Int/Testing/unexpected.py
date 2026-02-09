import unittest # Import the unittest module to create and run tests
import math # Import the math module to access mathematical functions

def get_sqrt(n): # Define a function named get_sqrt that takes one parameter n
  return math.sqrt(n) # Calculate and return the square root of n using the math library

def divide(a, b): # Define a function named divide that takes two parameters a and b
  return a / b # Perform division of a by b and return the result

class TestUnexpected(unittest.TestCase): # Define a test class that inherits from unittest.TestCase
  
  def test_get_sqrt(self): # Define a test method for valid square root calculations
    self.assertEqual(get_sqrt(144), 12) # Assert that the square root of 144 is 12

  def test_get_sqrt_error(self): # Define a test method for invalid square root inputs
    with self.assertRaises(ValueError): # Use a context manager to check if a ValueError is raised
      get_sqrt(-1) # Call get_sqrt with a negative number, which should trigger the error

  def test_divide(self): # Define a test method for valid division
    self.assertEqual(divide(144, 12), 12) # Assert that 144 divided by 12 equals 12

  def test_divide_error(self): # Define a test method for division by zero
    with self.assertRaises(ZeroDivisionError): # Use a context manager to check if a ZeroDivisionError is raised
      divide(144, 0) # Attempt to divide by zero, which should trigger the error

if __name__ == '__main__': # Check if this script is executed directly (not imported)
  unittest.main() # Run the unit tests defined in the class

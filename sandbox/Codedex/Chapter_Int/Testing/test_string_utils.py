import unittest
import string_utils

class TestStringUtils(unittest.TestCase):
  
  def test_reverse_string(self):
    # Test with a simple string
    s = "Francis"
    result = string_utils.reverse_string(s)
    self.assertEqual(result, "sicnarF")

  def test_capitalize_string(self):
    # Test with a lowercase string
    s = "cookie"
    result = string_utils.capitalize_string(s)
    self.assertEqual(result, "Cookie")

  def test_is_capitalized(self):
    # Test with a capitalized string
    self.assertTrue(string_utils.is_capitalized("Francis"))
    # Test with a non-capitalized string just to be sure (optional based on exercise instructions but good practice)
    self.assertFalse(string_utils.is_capitalized("cookie"))

if __name__ == '__main__':
    unittest.main()

import socket_server_main as ssm
import unittest

class TestFlags(unittest.TestCase):
  def setUp(self):
    pass
  
  def test_flag_detection(self):
    self.assertEqual(True, ssm.field_check("-b"))

  def test_dict_cons(self):
    self.assertEqual({"-s": 0}, ssm.flag_dict_cons(["-s", "a"]))
    self.assertEqual({"-s": 0, "-a": 4}, ssm.flag_dict_cons([
    "-s",
    "a",
    "b",
    "c",
    "-a"]))
    self.assertEqual(dict(), ssm.flag_dict_cons(["b", "a", "c", "h"]))

  def test_get_arguments(self):
    list1 = ["-a", "-b", "42", "-c"]
    self.assertEqual("42", ssm.get_arguments(list1, "-b",  1))
    with self.assertRaises(ValueError):
      ssm.get_arguments(list1,"-a" ,0 )
    with self.assertRaises(ValueError):
      ssm.get_arguments(list1, "-c", 3)

  def test_value_in_dict(self):
    # Just checking if a certain key exists in a dictionary
    self.assertEqual(ssm.exists("a", {"b": 1}), False)
    self.assertEqual(ssm.exists("a", {"a": 1}), True)
    

if __name__ == "__main__":
  unittest.main()


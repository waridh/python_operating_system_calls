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

  def test_error_case_checks(self):
    # Testing to see if the program will catch when the user specified the
    # mode incorrectly.
    fail_case1 = {
        '-s': 0,
        '-c': 2
        }
    fail_case2 = {
        '-a': 0,
        '-r': 2
        }
    correct_case ={
        '-s': 0,
        '-p': 2
        }
    with self.assertRaises(ValueError):
      ssm.error_case_checks(fail_case1 )
    with self.assertRaises(ValueError):
      ssm.error_case_checks(fail_case2 )
    self.assertTrue(ssm.error_case_checks(correct_case))

  def test_value_in_dict(self):
    # Just checking if a certain key exists in a dictionary
    self.assertEqual(ssm.exists("a", {"b": 1}), False)
    self.assertEqual(ssm.exists("a", {"a": 1}), True)

  def test_client_check(self):
    # Testing to see if it can recognize that this is a client
    flag_dict = {
        "-c": 0,
        "-p": 1,
        "-a": 2
        }
    fail_dict = {
        "-c": 0
        }
    self.assertTrue(ssm.client_check(flag_dict))
    self.assertFalse(ssm.client_check(fail_dict))

  def test_server_check(self):
    # Testing to see if it can recognize that this is a client
    flag_dict = {
        "-s": 0,
        "-p": 1,
        "-a": 2
        }
    fail_dict = {
        "-c": 0
        }
    self.assertTrue(ssm.server_check(flag_dict))
    self.assertFalse(ssm.server_check(fail_dict))

  def test_is_client(self):
    # This method tests if the client check is correct
    working_flag_dict = {
        "-c": 0,
        "-p": 1,
        "-a": 3
        }
    not_client_dict = {
        "-c": 0
        }
    self.assertTrue(ssm.is_client(working_flag_dict))
    self.assertFalse(ssm.is_client(not_client_dict))

  def test_is_server(self):
    # This method tests if the server check is correct
    working_flag_dict = {
        "-s": 0,
        "-p": 1,
        "-a": 3
        }
    not_work_dict1 = {
        "-c": 0
        }
    not_work_dict2 = {
        "-s": 0
        }
    not_work_dict3 = {
        "-s": 0,
        "-c": 1
        }
    self.assertTrue(ssm.is_server(working_flag_dict))
    self.assertFalse(ssm.is_server(not_work_dict1))
    self.assertFalse(ssm.is_server(not_work_dict2))
    self.assertFalse(ssm.is_server(not_work_dict3))

if __name__ == "__main__":
  unittest.main()


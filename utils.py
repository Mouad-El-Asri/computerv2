from typing import Any

def is_integer(string: str) -> bool:
	"""
		Checks if the given string can be converted to an integer.

		Args:
			string (str): The string to be checked for integer conversion.

		Returns:
			bool: `True` if the string can be converted to an integer, `False` otherwise.
	"""
	try:
		int(string)
		return True
	except ValueError:
		return False

def is_float(string: str) -> bool:
	"""
		Checks if the given string can be converted to a float.

		Args:
			string (str): The string to be checked for float conversion.

		Returns:
			bool: `True` if the string can be converted to a float, `False` otherwise.
	"""
	try:
		float(string)
		return True
	except ValueError:
		return False

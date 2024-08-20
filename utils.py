from typing import KeysView

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

def absolute(num: float) -> float:
	"""
		Returns the absolute value of a number.

		Args:
			num (float): The number for which to find the absolute value.

		Returns:
			(float): The absolute value of the input number.
	"""
	abs_num: float = num if num >= 0 else -num
	return abs_num

def square_root(num: float) -> float:
	"""
		Returns the square root of a given number.

		Args:
			num (float): The number to find the square root of.

		Returns:
			num (float): The square root of num.
	"""
	return num ** 0.5

def max_key(keys: KeysView[int]) -> int:
	"""
		Returns the max integer key

		Args:
			keys (KeysView[int]): a set of dictionary keys

		Returns:
			max_key (int): The max key
	"""
	max_key: int = 0
	for key in keys:
		if key > max_key:
			max_key = key

	return max_key

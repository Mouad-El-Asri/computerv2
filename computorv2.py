import sys
from utils import *

variables: dict[str, int | float] = {}
error_index: int = 0

def assign_rational_nums(user_input: str):
	global error_index
	if is_integer(user_input) or is_float(user_input):
		print(f'> {user_input}')
		return
	elif user_input.isalpha():
		if user_input == 'i':
			print(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.', file=sys.stderr)
			error_index += 1
			return
		print(f'> {variables.get(user_input, 0)}')
		return

	var_list: list[str] = user_input.strip().replace(' ', '').split('=')
	if len(var_list) == 2:
		var_name, value = var_list
		if var_name.isalpha():
			if var_name == 'i' or value == 'i':
				print(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.', file=sys.stderr)
				error_index += 1
			elif is_integer(value) or is_float(value):
				variables[var_name] = value
				print(f'> {variables[var_name]}')
			elif value.isalpha():
				variables[var_name] = variables.get(value, 0)
				print(f'> {variables[var_name]}')
			else:
				print(f'Error {error_index}: syntax error', file=sys.stderr)
				error_index += 1
		else:
			print(f'Error {error_index}: syntax error', file=sys.stderr)
			error_index += 1
	else:
		print(f'Error {error_index}: syntax error', file=sys.stderr)
		error_index += 1

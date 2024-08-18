import sys
from utils import *

variables: dict[str, int | float] = {}
error_index: int = 0

def print_error_message(error_message: str):
	global error_index
	print(error_message, file=sys.stderr)
	error_index += 1

def assign_rational_nums(user_input: str):
	global error_index
	if is_integer(user_input) or is_float(user_input):
		print(f'> {user_input}')
		return
	elif user_input.isalpha():
		if user_input == 'i':
			print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
			return
		print(f'> {variables.get(user_input, 0)}')
		return
	
	var_list: list[str] = user_input.strip().replace(' ', '').split('=')
	var_list.reverse()

	first_item = var_list[0]
    
	if first_item == 'i':
		print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
		return
	elif not first_item.isalpha() and not (is_integer(first_item) or is_float(first_item)):
		print_error_message(f'Error {error_index}: syntax error')
		return

	for var in var_list[1:]:
		if var == 'i':
			print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
			return
		elif not var.isalpha():
			print_error_message(f'Error {error_index}: syntax error')
			return

		if first_item.isalpha():
			variables[var] = variables.get(first_item, 0)
		elif is_integer(first_item) or is_float(first_item):
			variables[var] = int(first_item) if is_integer(first_item) else float(first_item)
		else:
			print_error_message(f'Error {error_index}: syntax error')
			return
	print(f'> {variables[var]}')

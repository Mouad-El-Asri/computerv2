import sys
import re
from typing import Any, Match
from utils import *

variables: dict[str, int | float] = {}
error_index: int = 0

def print_error_message(error_message: str) -> None:
	"""
		Prints an error message to standard error and increments the global error index.

		Args:
			error_message (str): The error message to be displayed.

		Returns:
			None
	"""
	global error_index
	print(error_message, file=sys.stderr)
	error_index += 1


def extract_complex_numbers(expression: str) -> str :
	"""
		Extracts and formats complex numbers from a given string expression.

		Args:
			expression (str): A string containing a mathematical expression with complex numbers.

		Returns:
			str: A formatted string representing the complex numbers with 'i' as the imaginary unit.
    """
	expression = expression.replace('i', 'j') if is_integer(expression[expression.find('i') - 1]) else expression.replace('i', '1j')
	pattern = r'\b[a-z]+\b'
	matches = re.findall(pattern, expression.lower())
	for var in matches:
		if var.isalpha() and var != 'j':
			expression = expression.lower().replace(var, str(variables.get(var, 0)))
	try:
		result: str = eval(expression)
		result = str(result).replace('(', '').replace(')', '').replace('j', 'i').replace('1i', 'i')
		if '+' in result:
			result = result.replace('+', ' + ')
		elif '-' in result:
			result = result.replace('-', ' - ')
		return result
	except Exception:
		print_error_message(f'Error {error_index}: syntax error')


def extract_and_solve(expression: str, operator: str) -> str:
	"""
		Extracts operands surrounding a given operator in an expression and computes the result.

    	Args:
    	    expression (str): The mathematical expression.
    	    operator (str): The operator to search for and apply in the expression.

    	Returns:
    	    str: The expression with the operation replaced by the computed result or an error message.
    """
	split_index: int = expression.find(operator)

	left_part: str = expression[:split_index]
	right_part: str = expression[split_index + len(operator):]

	left_match: Match[str] | None = re.search(r'[\d\w\-]+$', left_part)
	right_match: Match[str] | None = re.search(r'^[\d\w\-]+', right_part)
		
	left_operand: str = left_match.group() if left_match else ''
	right_operand: str = right_match.group() if right_match else ''

	if not left_operand or not right_operand:
		print_error_message(f'Error {error_index}: syntax error')
		return 'Error'

	operation: str = left_operand + operator + right_operand

	left_value: float | int = 0
	right_value: float | int = 0

	if is_integer(left_operand) or is_float(left_operand):
		left_value = int(left_operand) if is_integer(left_operand) else float(left_operand)
	elif left_operand.isalpha():
		left_value = variables.get(left_operand, 0)
	else:
		print_error_message(f'Error {error_index}: syntax error')
		return 'Error'

	if is_integer(right_operand) or is_float(right_operand):
		right_value = int(right_operand) if is_integer(right_operand) else float(right_operand)
	elif right_operand.isalpha():
		right_value = variables.get(right_operand, 0)
	else:
		print_error_message(f'Error {error_index}: syntax error')
		return 'Error'

	result: int | float
	if operator == '^':
		result = left_value ** right_value
	elif operator == '*':
		result = left_value * right_value
	elif operator == '/':
		result = left_value / right_value
	elif operator == '%':
		result = left_value % right_value
	elif operator == '+':
		result = left_value + right_value
	elif operator == '-':
		result = left_value - right_value

	return expression.replace(operation, str(result))


def handle_operator(expression: str) -> bool | str:
	"""
		Validates and evaluates a mathematical expression involving basic operators.

		Args:
			expression (str): The mathematical expression to validate and solve.

		Returns:
    		bool | str: The evaluated result as a string if valid; otherwise, returns False in case of errors.
    """
	expression = expression.replace(' ', '')
	input_pattern: str = r'^[a-zA-Z0-9\.\*\+\-\/\%\^ ]+$'
	if not bool(re.fullmatch(input_pattern, expression)):
		print_error_message(f'Error {error_index}: syntax error')
		return False
	elif expression[0] in {'*', '/', '%', '^'} or \
		expression[-1] in {'+', '-', '*', '/', '%', '^'}:
		print_error_message(f'Error {error_index}: syntax error')
		return False
	
	if 'i' in expression:
		return extract_complex_numbers(expression)

	def solve_operation(expression) -> str:
		"""
			Recursively evaluates mathematical operations in the expression.

			Args:
			    expression (str): The mathematical expression to evaluate.
		
			Returns:
			    str: The expression with evaluated results or the original expression if no operators are found.
		"""
		if expression[0] == '+':
			expression = expression[1:]

		if is_integer(expression) or is_float(expression):
			return expression

		exponentiation: str = '^'
		multiplicative: list[str] = ['*', '/', '%']
		additive: list[str] = ['+', '-']

		if exponentiation in expression:
			expression = extract_and_solve(expression, exponentiation)
		elif any(operator in expression for operator in multiplicative):
			for operator in multiplicative:
				if operator in expression:
					expression = extract_and_solve(expression, operator)
					break
		elif any(operator in expression for operator in additive):
			for operator in additive:
				if operator in expression:
					expression = extract_and_solve(expression, operator)
					break
		else:
			return expression
		return solve_operation(expression)

	result: str = solve_operation(expression)
	if result == "Error":
		return False
	return result


def evaluate_string_or_number(user_input: str) -> bool:
	"""
		Evaluates and prints the result of a number, variable, or expression.

		Args:
			user_input (str): The input to evaluate, which can be a number, variable, or expression.

		Returns:
			bool: True if the input was valid and processed; False otherwise.
	"""
	global error_index
	if is_integer(user_input) or is_float(user_input):
		print(f'>> {int(user_input) if is_integer(user_input) else float(user_input)}')
		return True
	elif user_input.isalpha():
		if user_input == 'i':
			print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
		else:
			print(f'>> {variables.get(user_input.lower(), 0)}')
		return True
	elif any(operator in user_input for operator in {'+', '-', '*', '/', '%', '^'}):
		operation_result: str | bool = handle_operator(user_input)
		if False is operation_result:
			return True
		print(f'>> {operation_result}')
		return True
	return False


def assign_rational_nums(user_input: str) -> None:
	"""
		Assigns a value to a variable based on the user input
		or just print it if it's not an assignment expression.

		Args:
			user_input (str): The input string.

		Returns:
			None
    """
	global error_index
	if '=' not in user_input and evaluate_string_or_number(user_input):
		return
	
	var_list: list[str] = user_input.strip().split('=')
	var_list.reverse()

	first_item: Any = var_list[0].strip()

	if any(operator in first_item for operator in {'+', '-', '*', '/', '%', '^'}):
		first_item = handle_operator(first_item)
		if False is first_item:
			return

	if first_item == 'i':
		print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
		return
	elif not first_item.isalpha() and not (is_integer(first_item) or is_float(first_item)) and not 'i' in first_item:
		print_error_message(f'Error {error_index}: syntax error')
		return
	
	last_var: str | None = None

	for var in var_list[1:]:
		var = var.strip().lower()
		if var == 'i':
			print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
			return
		elif not var.isalpha():
			print_error_message(f'Error {error_index}: syntax error')
			return

		last_var = var

		if first_item.isalpha():
			variables[var] = variables.get(first_item, 0)
		elif is_integer(first_item) or is_float(first_item):
			variables[var] = int(first_item) if is_integer(first_item) else float(first_item)
		elif 'i' in first_item:
			variables[var] = first_item
		else:
			print_error_message(f'Error {error_index}: syntax error')
			return
	if last_var:
		print(f'>> {variables[var]}')
	else:
		print_error_message(f'Error {error_index}: syntax error')

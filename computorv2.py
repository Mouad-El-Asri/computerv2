import sys
import re
from typing import Any, Match
from utils import *

variables: dict[str, int | float] = {}
error_index: int = 0
imagiary_expressions: list[str] = []

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

	operation: str = left_operand + operator + right_operand

	left_value: float | int = 0
	right_value: float | int = 0

	if is_integer(left_operand) or is_float(left_operand):
		left_value = int(left_operand) if is_integer(left_operand) else float(left_operand)
	elif left_operand.isalpha():
		if left_operand == 'i':
			if operator == '*':
				operation = left_operand + right_operand
			imagiary_expressions.append(operation)
			return ''
		left_value = variables.get(left_operand, 0)

	if is_integer(right_operand) or is_float(right_operand):
		right_value = int(right_operand) if is_integer(right_operand) else float(right_operand)
	elif right_operand.isalpha():
		if right_operand == 'i':
			if operator == '*':
				operation = left_operand + right_operand
			imagiary_expressions.append(operation)
			return ''
		right_value = variables.get(right_operand, 0)

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

	def solve_operation(expression) -> str:
		"""
			Recursively evaluates mathematical operations in the expression.

			Args:
			    expression (str): The mathematical expression to evaluate.
		
			Returns:
			    str: The expression with evaluated results or the original expression if no operators are found.
		"""
		Exponentiation: str = '^'
		Multiplicative: list[str] = ['*', '/', '%']
		Additive: list[str] = ['+', '-']
		if Exponentiation in expression:
			expression = extract_and_solve(expression, Exponentiation)
		elif any(Operator in expression for Operator in Multiplicative):
			for Operator in Multiplicative:
				if Operator in expression:
					expression = extract_and_solve(expression, Operator)
		elif any(Operator in expression for Operator in Additive):
			if is_integer(expression) or is_float(expression):
				return expression
			for Operator in Additive:
				if Operator in expression:
					expression = extract_and_solve(expression, Operator)
		else:
			return expression
		return solve_operation(expression)

	result: str = solve_operation(expression)
	if result == "Error":
		return False
	# for el in imagiary_expressions:
	# 	result += el
	# 	imagiary_expressions.remove(el)
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
		print(f'> {int(user_input) if is_integer(user_input) else float(user_input)}')
		return True
	elif user_input.isalpha():
		if user_input == 'i':
			print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
		else:
			print(f'> {variables.get(user_input.lower(), 0)}')
		return True
	elif any(operator in user_input for operator in {'+', '-', '*', '/', '%', '^'}):
		operation_result: str | bool = handle_operator(user_input)
		if False is operation_result:
			return True
		print(f'> {operation_result}')
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
	elif not first_item.isalpha() and not (is_integer(first_item) or is_float(first_item)):
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
		else:
			print_error_message(f'Error {error_index}: syntax error')
			return
	if last_var:
		print(f'> {variables[var]}')
	else:
		print_error_message(f'Error {error_index}: syntax error')

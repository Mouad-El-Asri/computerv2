import sys
import re
from utils import *

variables: dict[str, int | float] = {}
error_index: int = 0

def print_error_message(error_message: str) -> None:
	global error_index
	print(error_message, file=sys.stderr)
	error_index += 1


def extract_and_solve(expression: str, operator: str) -> str:
	split_index = expression.find(operator)

	left_part = expression[:split_index]
	right_part = expression[split_index + len(operator):]

	left_match = re.search(r'[\d\w]+$', left_part)
	right_match = re.search(r'^[\d\w]+', right_part)
		
	left_operand: str = left_match.group() if left_match else ''
	right_operand: str = right_match.group() if right_match else ''

	operation: str = left_operand + operator + right_operand

	if is_integer(left_operand) or is_float(left_operand):
		left_value: float | int = int(left_operand) if is_integer(left_operand) else float(left_operand)
	elif left_operand.isalpha():
		if left_operand == 'i':
			print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
			return "Error"
		left_value = variables.get(left_operand, 0)

	if is_integer(right_operand) or is_float(right_operand):
		right_value: int | float = int(right_operand) if is_integer(right_operand) else float(right_operand)
	elif right_operand.isalpha():
		if right_operand == 'i':
			print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
			return "Error"
		right_value = variables.get(right_operand, 0)

	result: int | float
	if operator == '**':
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
	expression = expression.replace(' ', '')
	input_pattern: str = r'^[a-zA-Z0-9\.\*\+\-\/\% ]+$'
	if not bool(re.fullmatch(input_pattern, expression)):
		print_error_message(f'Error {error_index}: syntax error')
		return False
	elif expression[0] in {'+', '*', '/', '%', '**'} or \
		expression[-1] in {'+', '*', '/', '%', '**'}:
		print_error_message(f'Error {error_index}: syntax error')
		return False

	def solve_operation(expression) -> str:
		Exponentiation = '**'
		Multiplicative = ['*', '/', '%']
		Additive = ['+', '-']

		if Exponentiation in expression:
			expression = extract_and_solve(expression, Exponentiation)
		elif any(Operator in expression for Operator in Multiplicative):
			for Operator in Multiplicative:
				if Operator in expression:
					expression = extract_and_solve(expression, Operator)
		elif any(Operator in expression for Operator in Additive):
			for Operator in Additive:
				if Operator in expression and expression[0] != Operator:
					expression = extract_and_solve(expression, Operator)
		else:
			return expression
		return solve_operation(expression)

	result = solve_operation(expression)
	if result == "Error":
		return False

	return result


def evaluate_string_or_number(user_input: str) -> bool:
	global error_index
	if is_integer(user_input) or is_float(user_input):
		print(f'> {int(user_input) if is_integer(user_input) else float(user_input)}')
		return True
	elif user_input.isalpha():
		if user_input == 'i':
			print_error_message(f'Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
		else:
			print(f'> {variables.get(user_input, 0)}')
		return True
	elif any(operator in user_input for operator in {'+', '-', '*', '/', '%', '**'}):
		operation_result: str | bool = handle_operator(user_input)
		if False is operation_result:
			return True
		print(f'> {operation_result}')
		return True
	return False


def assign_rational_nums(user_input: str) -> None:
	global error_index
	if '=' not in user_input and evaluate_string_or_number(user_input):
		return
	
	var_list: list[str] = user_input.strip().split('=')
	var_list.reverse()

	first_item: Any = var_list[0].strip()

	if any(operator in first_item for operator in {'+', '-', '*', '/', '%', '**'}):
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
		var = var.strip()
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

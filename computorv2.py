import sys
import re
from typing import Any, Match
from utils import *
import numpy
import json

variables: dict[str, Any] = {}
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


def extract_complex_numbers(expression: str) -> str | bool :
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
			expression = expression.lower().replace(var, str(variables.get(var.lower(), 0)))
	try:
		result: str = eval(expression)
		result = str(result).replace('(', '').replace(')', '').replace('j', 'i').replace('1i', 'i')

		if '+' in result:
			result = result.replace('+', ' + ')
		elif '-' in result[1:]:
			result = result[:1] + result[1:].replace('-', ' - ')
		return result
	except Exception:
		print_error_message(f'   Error {error_index}: syntax error')
		return False


def evaluate_operation(left_value: int | float, operator: str, right_value: int | float) -> int | float:
	"""
		Evaluates a basic mathematical operation between two numerical values.

		Args:
			left_value (int | float): The first operand in the operation.
			operator (str): The mathematical operator as a string ('^', '*', '/', '%', '+', or '-').
			right_value (int | float): The second operand in the operation.

		Returns:
			int | float: The result of applying the specified operation between the two operands.
    """
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
	return result


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

	left_match: Match[str] | None = re.search(r'[\d\w\.]+$', left_part)
	right_match: Match[str] | None = re.search(r'^[\d\w\.]+', right_part)
		
	left_operand: str = left_match.group() if left_match else ''
	right_operand: str = right_match.group() if right_match else ''

	if not left_operand or not right_operand:
		print_error_message(f'   Error {error_index}: syntax error')
		return 'Error'

	operation: str = left_operand + operator + right_operand

	left_value: float | int = 0
	right_value: float | int = 0

	if is_integer(left_operand) or is_float(left_operand):
		left_value = int(left_operand) if is_integer(left_operand) else float(left_operand)
	elif left_operand.isalpha():
		left_value = variables.get(left_operand.lower(), 0)
	else:
		print_error_message(f'   Error {error_index}: syntax error')
		return 'Error'

	if is_integer(right_operand) or is_float(right_operand):
		right_value = int(right_operand) if is_integer(right_operand) else float(right_operand)
	elif right_operand.isalpha():
		right_value = variables.get(right_operand.lower(), 0)
	else:
		print_error_message(f'   Error {error_index}: syntax error')
		return 'Error'

	result: int | float = evaluate_operation(left_value, operator, right_value)
	return expression.replace(operation, str(result))


def handle_operator(expression: str) -> bool | str:
	"""
		Validates and evaluates a mathematical expression involving basic operators.

		Args:
			expression (str): The mathematical expression to validate and solve.

		Returns:
    		bool | str: The evaluated result as a string if valid; otherwise, returns False in case of errors.
    """
	try:
		if is_valid_matrice(expression):
			matrices = expression.replace(';', ',').split('**')
			np_matrice = numpy.array(json.loads(matrices[0]))
			for matrice in matrices[1:]:
				np_matrice = numpy.array(json.loads(matrice.strip())) * np_matrice
			result: str = ''
			for row in np_matrice:
				formatted_row = '[ ' + ' , '.join(map(str, row)) + ' ]'
				if result:
					result += '\n   '
				result += formatted_row
			return result
	except ValueError:
		print_error_message(f'   Error {error_index}: value error')
		return False

	expression = expression.replace(' ', '')
	input_pattern: str = r'^[a-zA-Z0-9\.\*\+\-\/\%\^\)\() ]+$'
	if not bool(re.fullmatch(input_pattern, expression)):
		print_error_message(f'   Error {error_index}: syntax error')
		return False
	elif expression[0] in {'*', '/', '%', '^'} or \
		expression[-1] in {'+', '-', '*', '/', '%', '^'}:
		print_error_message(f'   Error {error_index}: syntax error')
		return False
	
	if 'i' in expression:
		return extract_complex_numbers(expression)

	pattern = r'\([^)]*\)'
	parentheses_content = re.findall(pattern, expression)
	for content in parentheses_content:
		expression = expression.replace(content, str(handle_operator(content[1:-1])))
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
			pattern = r'\b[a-z]+\b'
			matches = re.findall(pattern, expression.lower())
			for var in matches:
				expression = expression.lower().replace(var, str(variables.get(var.lower(), 0)))
			expression = str(eval(expression))
		else:
			return expression
		return solve_operation(expression)

	result = solve_operation(expression)
	if result == "Error":
		return False
	return result


def evaluate_string_or_number_or_matrice(user_input: str) -> bool:
	"""
		Evaluates and prints the result of a number, variable, or expression.

		Args:
			user_input (str): The input to evaluate, which can be a number, variable, or expression.

		Returns:
			bool: True if the input was valid and processed; False otherwise.
	"""
	global error_index
	if is_integer(user_input) or is_float(user_input):
		print(f'   {int(user_input) if is_integer(user_input) else float(user_input)}')
		return True
	elif user_input.isalpha():
		if user_input == 'i':
			print_error_message(f'   Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
		else:
			print(f'   {variables.get(user_input.lower(), 0)}')
		return True
	elif any(operator in user_input for operator in {'+', '-', '*', '/', '%', '^'}):
		operation_result: str | bool = handle_operator(user_input)
		if False is operation_result:
			return True
		print(f'   {operation_result}')
		return True
	elif is_valid_matrice(user_input):
		for el in user_input.replace(' ', '')[1:-1].split(';'):
			pattern = r'(\d+)'
			replacement = r' \1 '
			el = re.sub(pattern, replacement, el)
			print(f'   {el}')
		return True
	return False


def is_valid_matrice(expression: str) -> bool:
	"""
		Checks if a given string is a valid matrix or a valid matrix multiplication expression.

		Args:
		    expression (str): The string expression to validate.

		Returns:
		    bool: True if the expression is a valid matrix or matrix multiplication expression, False otherwise.
    """
	expression = expression.replace(' ', '')
	matrice_pattern = r'\[\[\d+(,\d+)*\](;\[\d+(,\d+)*\])*\]'
	matrice_multip_pattern = matrice_pattern + r'\s*\*\*\s*' + matrice_pattern
	return bool(re.fullmatch(matrice_pattern, expression)) or bool(re.fullmatch(matrice_multip_pattern, expression))


def handle_function(func_list: list[str], func_var_name: str) -> None:
	"""
		Processes a mathematical function, evaluates it with the given variable, 
		and prints the result or handles errors.

		Args:
			func_list (list[str]): A list containing the function name and its expression.
			func_var_name (str): The variable name used within the function expression.

		Returns:
			None: The function prints the evaluated result or an error message.
    """
	func_name: str = func_list[0].lower().split('(')[0]
	if len(func_list) != 2:
		if func_name in variables:
			pattern: str = r'\b[a-zA-Z]+\b'
			func_content: str = str(variables[func_name])
			match: Match[str] | None = re.search(pattern, func_content)
			if match:
				if is_integer(func_var_name):
					replaced_content = func_content.replace(match.group(0), func_var_name)
				else:
					replaced_content = func_content.replace(match.group(0), str(variables.get(func_var_name.lower(), 0)))
				print(f'   {eval(replaced_content)}')
		else:
			print_error_message(f'   Error {error_index}: syntax error')
		return

	func = func_list[1].strip()
	pattern = r'\b[a-zA-Z]+\b'
	matches = re.findall(pattern, func)
	for var in matches:
		if var != func_var_name and var != 'i':
			func = func.replace(var, str(variables.get(var.lower(), 0)))
	pattern = rf'([0-9]+)({func_var_name})'
	replacement = r'\1 * \2'
	func = re.sub(pattern, replacement, func)
	if any(bracket in func for bracket in ['(', ')']):
		variables[func_name] = func
		print(f'   {func}')
		return 
	tokens: list[str] = re.findall(r'\d+|\w+|[-+*/^%]', func)
	variable_tokens: list[str] = []
	variable_tokens_is_not_empty = False
	while len(tokens) > 1:
		if tokens[0] in {'+', '-'}:
			if tokens[0] == '+':
				tokens.pop(0)
				continue
			elif tokens[0] == '-' and not tokens[1].isalpha():
				tokens.pop(0) 
				tokens[0] = '-' + tokens[0]
				continue

		if any(op in tokens for op in ['^', '*', '/', '%']):
			if '^' in tokens:
				for i in range(len(tokens)):
					if '^' == tokens[i]:
						index = i
						break
			elif any(op in tokens for op in ['*', '/', '%']):
				for i in range(len(tokens)):
					if tokens[i] in '*/':
						index = i
						break
			if tokens[index - 1].isalpha() or tokens[index + 1].isalpha():
				if '^' == tokens[i]:
					break
				variable_tokens_is_not_empty = True
				subtractor = 1
				if index - 2 >= 0:
					subtractor = 2
					variable_tokens.append(tokens.pop(index - subtractor))
				elif '-' not in tokens[index - 1]:
					variable_tokens.append('+')
				variable_tokens.append(tokens.pop(index - subtractor))
				variable_tokens.append(tokens.pop(index - subtractor))
				variable_tokens.append(tokens.pop(index - subtractor))
				continue
		else:
			if variable_tokens_is_not_empty:
				break
			index = 1 if tokens[1] in {'+', '-', '*', '/', '%', '^'} else 0

			if tokens[index - 1].isalpha() and index != 0:
				if index - 2 >= 0:
					variable_tokens.append(tokens.pop(index - 2))
				else:
					variable_tokens.append('+')
				variable_tokens.append(tokens.pop(index - 1))
				continue
			elif tokens[index + 1].isalpha():
				variable_tokens.append(tokens.pop(index))
				variable_tokens.append(tokens.pop(index))
				continue

		left_value: int | float = int(tokens[index - 1]) if is_integer(tokens[index - 1]) else float(tokens[index - 1])
		operator: str = tokens[index]
		right_value: int | float = int(tokens[index + 1]) if is_integer(tokens[index + 1]) else float(tokens[index + 1])

		result: int | float = evaluate_operation(left_value, operator, right_value)

		tokens = tokens[:index - 1] + [str(result)] + tokens[index + 2:]
	if not tokens and variable_tokens[0] == '+':
		variable_tokens.pop(0)
	func = f'{" ".join(tokens)} {" ".join(variable_tokens)}'
	variables[func_name] = func
	print(f'   {func}')


def process_variable_assignment(user_input: str) -> None:
	"""
		Parses and processes a variable assignment from the user input.
    	Validates the input for syntax and variable name rules, evaluates expressions, and updates global variables.

		Args:
			user_input (str): The input string.

		Returns:
			None
    """
	try:
		global error_index
		if user_input == 'variables':
			for key, value in variables.items():
				print(f'   {key}-> {value}')
			return
		elif '=' not in user_input and evaluate_string_or_number_or_matrice(user_input):
			return

		var_list: list[str] = user_input.strip().split('=')
		if len(var_list) == 2 and var_list[1].strip() == '?':
			process_variable_assignment(var_list[0].strip())
			return

		pattern: str = r'^[a-zA-Z]+\(([a-zA-Z0-9]+)\)$'
		match: Match[str] | None = re.match(pattern, var_list[0].strip())
		if match and (bool(match) == True):
			return handle_function(var_list, match.group(1))

		var_list.reverse()
		first_item: Any = var_list[0].strip()

		is_matrice = False
		if any(operator in first_item for operator in {'+', '-', '*', '/', '%', '^'}):
			if '**' in first_item:
				is_matrice = True
			first_item = handle_operator(first_item)
			if False is first_item:
				return

		if first_item == 'i':
			print_error_message(f'   Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
			return
		elif '(' and ')' in first_item:
			pattern = r'^([a-zA-Z]+)\(([a-zA-Z0-9]+)\)$'
			match = re.match(pattern, first_item)
			if match and match.group(1).lower() in variables:
				pattern = r'\b[a-zA-Z]+\b'
				var_match = re.search(pattern, variables[match.group(1).lower()])
				if var_match and is_integer(match.group(2)):
					first_item = str(eval(variables[match.group(1).lower()].replace(var_match.group(0), match.group(2))))
				elif var_match:
					first_item = str(eval(variables[match.group(1).lower()].replace(var_match.group(0), str(variables.get(match.group(2).lower(), 0)))))
			else:
				print_error_message(f'   Error {error_index}: value error')
				return
		elif not first_item.isalpha() and not (is_integer(first_item) or \
		is_float(first_item)) and not 'i' in first_item and not is_valid_matrice(first_item) and not is_matrice:
			print_error_message(f'   Error {error_index}: syntax error')
			return

		last_var: str | None = None

		for var in var_list[1:]:
			var = var.strip().lower()
			if var == 'i':
				print_error_message(f'   Error {error_index}: \'i\' cannot be assigned or used as a variable name.')
				return
			elif not var.isalpha():
				print_error_message(f'   Error {error_index}: syntax error')
				return

			last_var = var

			if first_item.isalpha():
				variables[var.lower()] = variables.get(first_item.lower(), 0)
			elif is_integer(first_item) or is_float(first_item):
				variables[var.lower()] = int(first_item) if is_integer(first_item) else float(first_item)
			elif 'i' in first_item:
				variables[var.lower()] = first_item.replace(' ', '') if not any(op in first_item for op in {'+', '-', '*', '/', '%', '^'}) else first_item
			elif is_valid_matrice(first_item) or is_matrice:
				matrice = ''
				if is_matrice:
					variables[var.lower()] = first_item
					print(f'   {first_item}')
					break
				is_matrice = True
				for el in first_item.replace(' ', '')[1:-1].split(';'):
					pattern = r'(\d+)'
					replacement = r' \1 '
					el = re.sub(pattern, replacement, el)
					matrice += el
					print(f'   {el}')
				variables[var.lower()] = matrice
			else:
				print_error_message(f'   Error {error_index}: syntax error')
				return
		if last_var and not is_matrice:
			print(f'   {variables[var.lower()]}')
		elif not is_matrice:
			print_error_message(f'   Error {error_index}: syntax error')
	except Exception:
	 	print_error_message(f'   Error {error_index}: An error occurred')

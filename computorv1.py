import re
import sys
from utils import *

terms: dict[int, float]

def is_valid_expression(expression: str) -> bool:
	"""
		Parse and validate the polynomial expression using regex

		Args:
			expression (str): Polynomial expression

		Returns:
			bool: if the Polynomial expression is valid returns True, else returns False
	"""
	if not expression.strip() or '=' not in expression \
		or expression.find('^-') != -1:
		return False
	input_pattern: str = r'^[0-9X\.\^\*\=\+\- ]+$'
	return bool(re.fullmatch(input_pattern, expression))

def extract_terms(expression: str) -> dict[int, float]:
	"""
		Parses a polynomial expression and returns a dictionary of terms.

		Args:
			expression (str): Polynomial expression with terms.
		
		Returns:
			dict: Dictionary where keys are exponents and values are aggregated coefficients.
	"""
	expression = expression.replace(' ', '')
	terms: dict[int, float] = {}

	for term in expression.replace('-', '+-').split('+'):
		if term:
			if 'X' in term:
				if '*' not in term:
					term = '-1*' + term.replace('-', '') if term[0] == '-' else '1*' + term
				if '^' not in term:
					term += '^1'
			elif is_integer(term) or is_float(term):
				term += '*X^0'
			else:
				sys.exit("Error: enter a valid Polynomial equation!")

			coef_str: str
			exp_str: str
			coef_str, exp_str = term.split('*X^')
			coef: float = float(coef_str)
			exp: int = int(exp_str)

			if exp in terms:
				terms[exp] += coef
			elif coef != 0:
				terms[exp] = coef
	return terms

def reduced_form(equation: str) -> str:
	"""
		Reduces a polynomial equation to its reduced form.

		Args:
			equation (str): Polynomial equation

		Returns:
			str: The reduced polynomial equation with terms combined.
	"""
	left_side: str
	right_side: str

	left_side, right_side = equation.split('=')[:2]
	left_side = left_side.strip()
	right_side = right_side.strip()

	left_terms: dict[int, float] = extract_terms(left_side)
	right_terms: dict[int, float] = extract_terms(right_side)

	for exp in right_terms:
		if exp in left_terms:
			left_terms[exp] -= right_terms[exp]
		else:
			left_terms[exp] = -right_terms[exp]

	reduced: list[str] = []
	for exp in sorted(left_terms, reverse=True):
		coef: float = left_terms[exp]
		coef_str: int | float = int(absolute(coef)) if coef.is_integer() else absolute(coef)
		term: str
		if coef not in {1, -1}:
			if exp not in {1, 0}:
				term = f"{coef_str} * X^{exp}"
			elif exp == 0:
				term = f"{coef_str}"
			else:
				term = f"{coef_str} * X"
		elif coef in {1, -1}:
			if exp not in {1, 0}:
				term = f"X^{exp}"
			elif exp == 0:
				term = "1"
			else:
				term = "X"

		if coef < 0:
			term = f"- {term}"
		elif reduced:
			term = f"+ {term}"
		reduced.append(term)

	reduced_result = ' '.join(reduced)
	global terms
	terms = dict(left_terms)
	return f"{reduced_result} = 0"

def solve_polynomial(equation: str):
	"""
		Solve a polynomial equation od degree 2 or below

		Args:
			equation (str): the polynomial equation to solve
	"""
	polynomial_degree: int = max_key(terms.keys()) if terms.keys() else 0
	print(f'Polynomial degree: {polynomial_degree}')
	
	if polynomial_degree > 2:
		sys.exit('The polynomial degree is strictly greater than 2, I can\'t solve.')

	if polynomial_degree == 0:
		result: int | float = terms.get(0, 0)
		if result == 0:
			print('Any real number is a solution.')
		else:
			print('There is no solution.')
	elif polynomial_degree == 1:
		const_term: float = terms.get(0, 0)
		coef: float = terms.get(1, 0)

		if coef == 0:
			if const_term == 0:
				print('Any real number is a solution.')
			else:
				print('There is no solution.')
		else:
			result = -const_term / coef
			result = int(result) if result.is_integer() else result
			print(f'The solution is:\n{result}')
	elif polynomial_degree == 2:
		if 1 not in terms:
			terms[1] = 0
		elif 0 not in terms:
			terms[0] = 0
		delta: int | float = (terms[1] ** 2) - (4 * terms[2] * terms[0])
		if delta < 0:
			print('Discriminant is strictly negative, there is two complex solutions:')
			print(f'α + β * i = (-2b + i√|Δ|) / 2a = ({-terms[1]} + i√|{delta}|) / {2 * terms[2]}')
			print(f'α - β * i = (-2b - i√|Δ|) / 2a = ({-terms[1]} - i√|{delta}|) / {2 * terms[2]}')
		elif delta == 0:
			result = -terms[1] / (2 * terms[2])
			result = int(result) if result.is_integer() else result
			print(f'Discriminant is equal to zero, there is exactly one real solution:\n{result}')
		else:
			result_1 = (-terms[1] - square_root(delta)) / (2 * terms[2])
			result_1 = int(result_1) if result_1.is_integer() else result_1
			result_2 = (-terms[1] + square_root(delta)) / (2 * terms[2])
			result_2 = int(result_2) if result_2.is_integer() else result_2
			print(f'Discriminant is strictly positive, the two solutions are:\n{round(result_1, 6)}\n{round(result_2, 6)}')

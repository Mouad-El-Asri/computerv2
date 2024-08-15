from computorv2 import *
import signal

def signal_handler(sig, frame):
	print('\n> (interrupt) use \'quit\' or \'exit\' to exit.\n> ', end='')

signal.signal(signal.SIGINT, signal_handler)

def main():
	print('Welcome to Computorv2, the Python Calculator in command line!\n'
		'To exit, type "exit" or "quit" and press Enter.')
	while True:
		try:
			user_input: str = input("> ")
			if not user_input.strip():
				continue
			if user_input in ['exit', 'quit']:
				break
			assign_rational_nums(user_input)
		except EOFError:
			sys.exit('')

if __name__ == '__main__':
	main()

__author__ = 'Ye Vang'
__source__ = 'http://newcoder.io/gui/'
import argparse
from Tkinter import Tk, Canvas, Frame, Button, BOTH, TOP, BOTTOM

'''
Made from following a tutorial on creating your own Sudoku puzzle game!
Use Python 2.7 to run this script on your terminal or command prompt.
'''

BOARDS = ['debug', 'pleb', 'pro', 'error'] # Sudoku boards
MARGIN = 20 # Number of pixels around the board
SIDE = 50 # Width of every grid cell
WIDTH = HEIGHT = MARGIN * 2 + SIDE * 9 # Width/Height of the entire board. Margin + 9 Grid cell sizes

class SudokuError(Exception):
	'''An application specific error. Error class'''
	pass

class SudokuBoard(object):
	'''Sudoku Board representation.'''

	def __init__(self, board_file):
		'''Initialize the board to the board type input parameter'''
		self.board = self.__create_board(board_file)

	def __create_board(self, board_file):  # Two underscores denotes a private variable. Cannot be accessed outside of the class.
		'''Constructs the board'''
		board = [] # Outer array

		for line in board_file: 	# Iterate over each line
			line = line.strip()	# Strip off punctuation
			print(line)
			# Raise error if line is longer or shorter than 9 characters
			if len(line) != 9:
				raise SudokuError(
					'Each line in the Sudoku Puzzle has to be 9 characters long.'
					)
			# Create a list for the line
			board.append([])

			# Iterate over each character
			for c in line:
				# Raise error if char is not an integer
				if not c.isdigit():
					raise SudokuError(
						'Please enter a valid integer for Sudoku Puzzle; numbers 0-9'
						)

				# Add to latest list for line
				board[-1].append(int(c))

		# Raise error if the number of lines is != 9
		if len(board) != 9:
			raise SudokuError('Each Sudoku Puzzle has to be 9 lines long.')

		# Return constructed board
		return board

class SudokuGame(object):
	'''A Sudoku Game. In charge of storing the current state of the board and checking 
	whether the puzzle has been completed.'''

	def __init__(self, board_file):
		self.board_file = board_file  # Board type stored
		self.start_puzzle = SudokuBoard(board_file).board # Backend grid storing the 2D board

	def start(self):
		self.game_over = False  # Game starts, state of game over is False

		'''Copy the contents of starting 2D array into a new 2D array so that we avoid
		referencing the same array (i.e the start_puzzle). That way, the starting 
		configuration remains untouched.'''
		self.puzzle = []
		for i in xrange(9):
			self.puzzle.append([])
			for j in xrange(9):
				self.puzzle[i].append(self.start_puzzle[i][j])

	def check_win(self):
		'''Checks to see if the user has found a viable configuration.'''
		for row in xrange(9):							# Iterate over each row
			if not self.__check_row(row):
				return False
		for column in xrange(9):						# Iterate over each column
			if not self.__check_column(column):
				return False
		for row in xrange(3):							# Iterate over each subgrid
			for column in xrange(3):
				if not self.__check_subgrid(row, column):
					return False
		self.game_over = True
		return True


	def __check_block(self, block):
		'''Helper function checks to see if the list of numbers are 
		all unique.'''
		return set(block) == set(range(1, 10))


	def __check_row(self, row):
		'''Checks a row for uniqueness'''
		return self.__check_block(self.puzzle[row])


	def __check_column(self, column):
		'''Checks a column for uniqueness'''
		return self.__check_block([self.puzzle[row][column] for row in xrange(9)])


	def __check_subgrid(self, row, column):
		'''Checks a subgrid for uniqueness'''
		return self.__check_block(
			[
				self.puzzle[r][c]
				for r in xrange(row * 3, (row + 1) * 3)
				for c in xrange(column * 3, (column + 1) * 3)
			]
		)

class SudokuUI(Frame):
	'''Tkinter UI responsible for drawing the board and accepting user input.'''
	
	def __init__(self, parent, game):
		'''Initialize the game with a parent class in the tkinter module.'''
		self.game = game
		self.parent = parent			# Main window of the whole program
		Frame.__init__(self, parent)

		self.row, self.column = 0, 0
		self.__initUI()

	def __initUI(self):
		'''The GUI that contains all of the frontend widgets etc.'''
		self.parent.title('Sudoku')			# Title of our window 
		self.pack(fill = BOTH, expand = 1)
		self.canvas = Canvas(self, width = WIDTH, height = HEIGHT)
		self.canvas.pack(fill = BOTH, side = TOP)
		clear_button = Button(self, text = 'Clear answers', command=self.__clear_answers)
		clear_button.pack(fill = BOTH, side = BOTTOM)

		self.__draw_grid()
		self.__draw_puzzle()

		self.canvas.bind('<Button-1>', self.__cell_clicked)
		self.canvas.bind('<Key>', self.__key_pressed)

	def __draw_grid(self):
		'''Draws grid divided by blue lines into 3x3 subgrids.'''

		for i in xrange(10):
			color = 'blue' if i % 3 == 0 else 'gray'

			x0 = MARGIN + i * SIDE
			y0 = MARGIN
			x1 = MARGIN + i * SIDE
			y1 = HEIGHT - MARGIN
			self.canvas.create_line(x0, y0, x1, y1, fill = color)

			x0 = MARGIN
			y0 = MARGIN + i * SIDE
			x1 = WIDTH - MARGIN
			y1 = MARGIN + i * SIDE
			self.canvas.create_line(x0, y0, x1, y1, fill = color)

	def __draw_puzzle(self):
		'''Draw on the UI corresponding to the backend grid's 
		cell number in 2D array.'''
		self.canvas.delete('numbers')
		for i in xrange(9):
			for j in xrange(9):
				answer = self.game.puzzle[i][j]
				if answer != 0:
					x = MARGIN + j * SIDE + SIDE / 2 	# Column margin (x direction i.e. j)
					y = MARGIN + i * SIDE + SIDE / 2 	# Row margin (y direction i.e. i)
					original = self.game.start_puzzle[i][j]
					color = 'black' if answer == original else 'sea green' # Pre-filled numbers are black; new user input is sea green
					self.canvas.create_text(x, y, text = answer, tags = 'numbers', fill = color)

	def __clear_answers(self):
		'''Delete the user's input from the backend grid and UI.
		Hence the duplicated puzzle 2D array.'''
		self.game.start()
		self.canvas.delete('victory')
		self.__draw_puzzle()

	def __cell_clicked(self, event):
		'''Respond to user mouse clicks on a particular cell/location.'''
		if self.game.game_over:			# If the game is over, do nothing
			return
		x, y = event.x, event.y
		if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN): # Grab x and y location of click if within bounds of puzzle board
			self.canvas.focus_set() # Focus on area that is clicked

			# Get row and column numbers from (x, y) coordinates
			row, column = (y - MARGIN) / SIDE, (x - MARGIN) / SIDE

			# If cell was selected already, deselect it.
			if (row, column) == (self.row, self.column):
				self.row, self.column = -1, -1
			elif self.game.puzzle[row][column] == 0:
				self.row, self.column = row, column
		else:
			self.row, self.column = -1, -1

		self.__draw_cursor()

	def __draw_cursor(self):
		'''Draws a highlighted rectangle around the grid cell location
		that the user clicked on.'''
		self.canvas.delete('cursor')
		if self.row >= 0 and self.column >= 0:		# If row and column are set in focus, then compute dimensions of cell and create rectangle
			x0 = MARGIN + self.column * SIDE + 1
			y0 = MARGIN + self.row * SIDE + 1
			x1 = MARGIN + (self.column + 1) * SIDE - 1
			y1 = MARGIN + (self.row + 1) * SIDE - 1
			self.canvas.create_rectangle(x0, y0, x1, y1, outline = 'red', tags = 'cursor')

	def __key_pressed(self, event):
		'''Handle key pressed events accordingly. If integer, place integer
		into grid cell etc.'''
		if self.game.game_over:
			return
		if self.row >= 0 and self.column >= 0 and event.char in '1234567890':
			self.game.puzzle[self.row][self.column] = int(event.char)
			self.column, self.row = -1, -1 	# Dereference the box
			self.__draw_puzzle()
			self.__draw_cursor()
			if self.game.check_win():
				self.__draw_victory()

	def __draw_victory(self):
		'''If the user has completed the Sudoku puzzle successfully,
		draw a circle congratulating them on their victory.'''
		x0 = y0 = MARGIN + SIDE * 2
		x1 = y1 = MARGIN + SIDE * 7

		# Draw the oval
		self.canvas.create_oval(x0, y0, x1, y1, tags = 'victory', fill = 'dark oxrange', outline = 'oxrange')

		# Create the text inside the oval
		x = y = MARGIN + 4 * SIDE + SIDE / 2
		self.canvas.create_text(x, y, text = 'You win!', tags = 'winner', fill = 'white', font = ('Arial', 32))

def parse_arguments():
	'''Parses arguments of the form: sudoku.py <board name> in 
	the command line, where `board name` must be in the `BOARD`
	global variable list.'''

	arg_parser = argparse.ArgumentParser()

	'''Argument parser is called by the command 'python sudoku.py --board <BOARD_NAME>', 
	expected a string in BOARDS list. User can also run 'python sudoku.py -h or --help' 
	so that the user will understand the purpose of the --board flag'''
	arg_parser.add_argument(
		"--board", 
		help = 'Desired board name/type', 
		type = str, 
		choices = BOARDS, 
		required = True)

	args = vars(arg_parser.parse_args())

	# Dictionary, where 'board' is the key and the value is the user input.
	return args['board']

if __name__ == '__main__':
	board_name = parse_arguments()

	with open('%s.sudoku' % board_name, 'r') as boards_file:
		game = SudokuGame(boards_file)
		game.start()

		root = Tk()
		SudokuUI(root, game) # Parent widget
		root.geometry('%dx%d' % (WIDTH, HEIGHT + 40))
		root.mainloop() # Launches the window from SudokuUI

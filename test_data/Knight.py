from copy import deepcopy


class Knight:
	field = [['.' for _ in range(8)] for _ in range(8)]
	y = {
		'a': 0, 'b': 1, 
		'c': 2, 'd': 3, 
		'e': 4, 'f': 5, 
		'g': 6, 'h': 7
	} # столбцы
	x = {8: 0, 7: 1, 6: 2, 5: 3, 4: 4, 3: 5, 2: 6, 1: 7}


	def __init__(
		self, 
		horizontal: str, 
		vertical: int, 
		color: str
	):	
		self.horizontal = horizontal
		self.vertical = vertical
		self.color = color
		self.field[self.x[vertical]][self.y[horizontal]] = self.get_char()
		self.prev_walks = None
		self.__insert_marker()
	
	def __insert_marker(self) -> None:
		if self.prev_walks:
			for walk in self.prev_walks:
				self.field[walk[1]][walk[0]] = '.'
		x, y = self.x[self.vertical], self.y[self.horizontal]
		walks = (
			(y - 1, x - 2), (y - 2, x - 1),
			(y + 1, x - 2), (y + 2, x - 1),
			(y - 1, x + 2), (y - 2, x + 1),
			(y + 1, x + 2), (y + 2, x + 1),
		)
		self.prev_walks = deepcopy(walks)
		for walk in walks:
			if 0 <= walk[0] <= 7 and 0 <= walk[1] <= 7:
				self.field[walk[1]][walk[0]] = '*'
		
	@staticmethod
	def get_char() -> str:
		return 'N'
			
	def can_move(self, h: str, v: int) -> bool:
		return self.field[self.x[v]][self.y[h]] == '*'

	def move_to(self, h: str, v: int) -> None:
		if self.can_move(h, v):
			self.horizontal = h
			self.vertical = v
			self.__insert_marker()
			self.field[self.x[v]][self.y[h]] = self.get_char()

	def draw_board(self) -> None:
		for row in self.field:
			for cell in row:
				print(cell, end='')
			print()
		
	
		
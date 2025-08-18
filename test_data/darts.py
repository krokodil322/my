from itertools import cycle
from copy import deepcopy


def transpon(matrix: list):
	copy_matrix = deepcopy(matrix)

	size = len(matrix)
	for r in range(size):
		for c in range(size):
			matrix[r][c] = copy_matrix[c][size - 1 - r]


def print_matrix(matrix: list):
	for row in matrix:
		print(' '.join(map(str, row)))


size = int(input())
# size = 7
matrix = [[num for num in range(size)] for _ in range(size)]

point = 1
for indx in range(size):
	for r in range(size):
		for c in range(indx, size - indx):
			matrix[c][indx] = point		
		transpon(matrix)
	point += 1

print_matrix(matrix)
# print(matrix)

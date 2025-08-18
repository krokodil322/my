from sys import stdin
from itertools import pairwise
from decimal import Decimal


differences = list(map(lambda pack: pack[1] - pack[0], pairwise([int(num.strip()) for num in stdin])))
if differences.count(differences[0]) == len(differences):
	print("Арифметическая прогрессия")
else:
	status, ratio = True, Decimal(differences[1]) / Decimal(differences[0])
	for diff in enumerate(differences[2:], 1):
		try:
			if ratio != Decimal(diff[1]) / Decimal(differences[diff[0]]):
				status = False
				break
		except:
			status = False
			break
	if status:
		print("Геометрическая прогрессия")
	else:
		print("Не прогрессия")
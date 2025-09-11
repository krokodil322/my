from functools import total_ordering


@total_ordering
class Word:
	def __init__(self, word: str):
		self.word = word

	def __str__(self):
		return self.word.title()

	def __repr__(self):
		return f"{self.__class__.__name__}('{self.word}')"
	
	def __eq__(self, obj):
		if not isinstance(obj, Word):
			return NotImplemented
		return len(self.word) == len(obj.word)

	def __lt__(self, obj):
		if not isinstance(obj, Word):
			return NotImplemented
		return len(self.word) < len(obj.word)

	def __le__(self, obj):
		if not isinstance(obj, Word):
			return NotImplemented
		return len(self.word) <= len(obj.word)


# w1 = Word("abra")
# w2 = Word("kadabra")

# print(w1 == w2)
# print(w1 != w2)
# print(w1 < w2)
# print(w1 > w2)
# print(w1 <= w2)
# print(w1 >= w2)





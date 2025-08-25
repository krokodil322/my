from string import ascii_letters


class StrExtension:
	__VOWELS = "eyuioa"
	__LATIN = ascii_letters


	@classmethod
	def remove_vowels(cls, string: str) -> str:
		res = str()
		for char in string:
			if char not in cls.__VOWELS + cls.__VOWELS.upper():
				res += char
		return res

	@classmethod
	def leave_alpha(cls, string: str) -> str:
		res = str()
		for char in string:
			if char in cls.__LATIN:
				res += char
		return res

	@classmethod
	def replace_all(cls, string: str, chars: str, char: str) -> str:
		res = str()
		for ch in string:
			if ch in chars:
				res += char
			else:
				res += ch
		return res
			
		
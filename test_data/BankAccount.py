


class BankAccount:
	def __init__(self, balance: int|float=0):
		self._balance = balance

	def get_balance(self) -> int|float:
		return self._balance

	def deposit(self, amount: int|float) -> None:
		self._balance += amount

	def withdraw(self, amount: int|float) -> None:
		new_balance = self._balance - amount
		if new_balance < 0:
			raise ValueError("На счете недостаточно средств")
		self._balance = new_balance

	def transfer(self, account: "BankAccount", amount: int|float) -> None:
		self.withdraw(amount)
		account.deposit(amount)


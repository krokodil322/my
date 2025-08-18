from my import  *
import os

		# ("guru.py", "tests_3066209.zip"),
		# ("only_numbers.py", "tests_3013981.zip")


if __name__ == "__main__":
	test_data = [
		("Knight.py", "16.zip"), # тут тоже
		("only_numbers.py", "tests_3013981.zip"), # и тут stdin
		("darts.py", "4.zip"), # тут есть input()
		("Pycon.py", "11.zip"), # тут тоже
		("guru.py", "tests_3066209.zip"), # тут stdin
		("BankAccount.py", "16(3).zip") # тут try-except с raise
	]
	module_path = os.path.dirname(__file__)
	tests_path = os.path.join(module_path, "test_data")
	for programm, tests in test_data:
		obj = TestExecutor(
				archive_path=os.path.join(tests_path, tests),
				programm_path=os.path.join(tests_path, programm)
			)
		obj.run()








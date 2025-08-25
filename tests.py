from my import  *
import os



if __name__ == "__main__":
	test_data = [
		("BankAccount.py", "16(3).zip"), # тут try-except с raise
		("Knight.py", "16.zip"), # тут input()
		("only_numbers.py", "tests_3013981.zip"), # тут stdin
		("darts.py", "4.zip"), # тут есть input()
		("Pycon.py", "11.zip"), # тут input()
		("guru.py", "tests_3066209.zip"), # тут stdin
		("StrExtension.py", "15(5).zip") # тут хуйня с rstrip
	]
	module_path = os.path.dirname(__file__)
	tests_path = os.path.join(module_path, "test_data")
	for programm, tests in test_data:
		obj = TestExecutorForTests(
				archive_path=os.path.join(tests_path, tests),
				programm_path=os.path.join(tests_path, programm)
			)
		status, err = obj.run()
		if status == "ERROR":
			while True:
				print(err)
				is_continue = input("Продолжить? (y/n): ")
				if is_continue in "yn":
					break
			if is_continue == 'n':
				break






		
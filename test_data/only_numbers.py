import sys
import my


counter = {"nums": 0, "not_nums": 0}
for value in sys.stdin:
	try:
		counter["nums"] += int(value)
	except ValueError:
		try:
			counter["nums"] += float(value)
		except ValueError:
			counter["not_nums"] += 1
	
print(counter["nums"], counter["not_nums"], sep="\n")


if __name__ == "__main__":
	obj = my.TestExecutor(
			archive_path="tests_3013981.zip",
			programm_path=__file__,
		)



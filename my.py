from typing import Callable, Any, Generator
from functools import wraps
from tkinter import filedialog
from more_itertools import chunked
import time
import tracemalloc
import subprocess
import zipfile
import tempfile
import os
import json


class TestExecutor:
	"""
		следует испрвить, сделать так чтобы в оперативу не
		пападал весь текст программы, сделать все через итераторы
		Не работает, если в тексте программы возбуждается

		Класс предназначен для проведения тестов задач 
		с курсов BeeGeek И ТОЛЬКО.

		Открывает оконный менеджер файлов для выбора нужного
		zip-архива и тестируемой программы. Распаковывает архив,
		и вставляя определенным образом в код программы запускает
		тесты. Всячески реагирует на результаты тестов и сообщает
		об успехе или неудаче.

		Реализован мини-кэш для сохранения путей последних открытых
		папок с zip-архивом и программой, просто для удобства.

		Предполагаемое использование: 
			1) Запускать напрямую из модуля.
			2) Либо импортировать в отдельный файл объект и 
			   запускать тесты через этот файл. Вот мой вариант
			   использования:
			    from my import TestExecutor


				if __name__ == "__main__":
					obj = TestExecutor()
					obj.run()

			3) Вариант с импортом в тестируемую программу
			   не предполагается.
			4) Запускает рекомендуется через командную строку, ибо
			   иногда есть какие-то трабы с кодировкой.
	"""

	__STATUSES = ("SUCCESS", "FAILURE", "ERROR")

	def __init__(self):
		"""
			archive_path и programm_path - приходят в виде аргументов
			только для теста этого объекта и не предполагается 
			в качестве использования.
		"""
		cache = self._cache()
		self.archive_path = filedialog.askopenfilename(
			initialdir=cache["archive_path"],
		    title="Выберите ZIP файл с тестами",
		    filetypes=[("ZIP files", "*.zip")]
		)
		self.programm_path = filedialog.askopenfilename(
			initialdir=cache["programm_path"],
		    title="Выберите файл c программой на Python",
		    filetypes=[("Python files", "*.py")]
		)
		self._cache(save=True)

		# код программы хранится тут
		self.programm = ''

		# статус исполненных тестов
		# все виды стутасов лежат в константе __STATUSES
		self.status = None

	@staticmethod
	def _read_file(path: str) -> str:
		"""
			Просто читает текстовый файл и возвращает
			его в виде строки. В данном классе используется
			для чтения текста программ, а потому предполагается,
			что огромных файлов считываться не будет и перебоев
			с ОЗУ быть не должно. Само собой, если считать файл
			размером 100 ГБ комп упадет. В будущем данный метод
			будет переработан под итератор.
		"""
		with open(path, encoding="utf-8") as file:
			return file.read()

	def _cache(self, save: bool=False) -> dict:
		"""
			Сохраняет в кэш-файл пути к последним открытым папкам
			с архивом тестов и файла программы. Добавляет удобство,
			не нужно лишний раз кучу раз тыкать до нужной папки с файлами.
		"""
		def save_cache(data: dict):
			with open(cache_path, 'w', encoding="utf-8") as file:
				json.dump(data, fp=file, indent=3, ensure_ascii=False)
		module_path = os.path.dirname(__file__)
		dir_path = os.path.join(module_path, "cache")
		cache_path = os.path.join(dir_path, "cache.json")
		data, cache = {"archive_path": '', "programm_path": ''}, {}
		if not save:
			if not os.path.exists(dir_path):
				os.mkdir(dir_path)
			if not os.path.exists(cache_path):
				save_cache(data)
		with open(cache_path, 'r', encoding="utf-8") as file:
			cache = json.load(fp=file)
		if save:
			cache["archive_path"] = os.path.dirname(self.archive_path)
			cache["programm_path"] = os.path.dirname(self.programm_path)
			save_cache(data=cache)
		return cache

	def _extract_zip(self) -> str:
		"""
			Распаковывает zip архив и возвращает путь 
			к распакованной папке.
		"""
		with zipfile.ZipFile(self.archive_path) as zip_file:
			basename = os.path.basename(self.archive_path).split('.zip')[0]
			dirname = os.path.dirname(self.archive_path)
			zip_file.extractall(path=os.path.join(dirname, basename))
		return os.path.join(os.path.dirname(self.archive_path), basename)

	def _start_subprocess(self, stdin_, tmp_file: str) -> subprocess.Popen:
		"""
			Запускает тестируемую программу через subprocess.
			Возвращает объект subprocess.Popen
		"""
		encoding = "cp1251"
		# тут проснулся новый нюанс: У файлов с тестами иногда
		# кодировка нихуя не utf-8. А вот с кодировкой cp1251
		# все прекрасно работает
		sub_popen = subprocess.Popen(
				["python", tmp_file],
				stdin=stdin_,
				stdout=subprocess.PIPE,
				stderr=subprocess.PIPE,
				text=True,
				encoding=encoding,
				shell=True,
			)
		return sub_popen

	def _test_executor(self) -> Generator:
		"""
			Главный метод, по очереди исполняет тесты из каждого файла
			с тестовыми данными, реагирует на результаты работы, меняя
			статус исполнения. Сам по себе является генератором.
		"""
		self.programm = self._read_file(path=self.programm_path)
		new_archive_path = self._extract_zip()
		files = chunked(os.listdir(new_archive_path), 2)
		for req, res in files:
			input_data = self._read_file(path=os.path.join(new_archive_path, req))
			except_res = self._read_file(path=os.path.join(new_archive_path, res))
			retry, is_retry = 0, True
			stdout_, stderr_, is_eq = None, None, None
			# суть, если в input_data нету команд вызовов функций и т. п.
			# но есть строки по типу I'm num, то интерпретатор воспринимает
			# такую строку как SyntaxError, а потому не следует добавлять
			# такие строки в конец программы. Кароч, если stderr_ отлавливает
			# SyntaxError, то этот блок кода он повторяет еще один раз
			# если ошибка так и остается, то значит дело не в данных input_data.
			while is_retry:
				with tempfile.NamedTemporaryFile(
						"w", suffix=".py", 
						delete=False, 
						dir=r"C:\programms", 
						encoding="utf-8",
					) as tmp_file:
					if retry == 0:
						tmp_file.write(self.programm + '\n' + input_data)
					else:
						tmp_file.write(self.programm)
					with open(os.path.join(new_archive_path, req), encoding="utf-8") as file:
						sub_popen = self._start_subprocess(stdin_=file, tmp_file=tmp_file.name)
				if sub_popen:
					stdout_, stderr_ = sub_popen.communicate()
					# stderr_ - обязательно типа str, такой ее выдает строка выше
					# но был случай когда stderr_ был None, так и не понял почему
					if stderr_ and "SyntaxError" in stderr_:
						if retry > 1:
							is_retry = False
						retry += 1
					else:
						is_retry = False
					if stdout_:
						is_eq = stdout_.rstrip() == except_res
				else:
					print("Что-то пошло не так...")
					return None
				os.remove(tmp_file.name)
			if stderr_:
				self.status = self.__STATUSES[2]
			elif not is_eq:
				self.status = self.__STATUSES[1]
			else:
				self.status = self.__STATUSES[0]
			yield stdout_, except_res, input_data, stderr_, is_eq
		
	def run(self) -> None:
		"""
			Работает с пользователем. Выводит на экран 
			сообщения. Кароче, это пользовательский интерфейс.

			Повтор тестов очень удобен в случаях когда тесты
			провалились и нужно допилить тестируемую программу.
			После допила кода просто перезапускаешь тесты без
			всей возник с выбором архива с тестами и файла программы
			в файловом менеджере.
		"""
		print(self.programm_path)
		print(self.archive_path)
		while True:
			for ivent, (
					stdout_, except_res, 
					input_data, stderr_, 
					is_eq
				) in enumerate(self._test_executor(), 1):
				print(f"\nТест №{ivent}")
				print("===============================================")
				print(f"Входящие данные:\n{input_data}")
				print(f"Ожидаемый результат:\n{except_res}")
				print(f"Выход тестируемой программы:\n{stdout_}")
				print("===============================================")
				if not is_eq:
					if self.status == "ERROR":
						print(f"У твоей программы вышибло пробки по типу\n{stderr_}")
					elif self.status == "FAILURE":
						print(f"ПРОВАЛ! ТЕСТ №{ivent}")
					break
			if self.status == "SUCCESS":
				print("Все тесты пройдены!")
			if input("(y/n), если хочешь повторить: ").rstrip() != 'y':
				return None


class TestExecutorForTests(TestExecutor):
	"""
		Этот класс нужен чисто чтобы затестить класс TestExecutor.
		Для тестов нужно подшаманить пользовательский интерфейс
		чтобы он не заправшивал повтор тестов.
	"""
	def __init__(self, archive_path: str='', programm_path: str='') :
		self.archive_path = archive_path
		self.programm_path = programm_path
		self.programm = None
		self.status = None

	def run(self) -> tuple:
		print(self.programm_path)
		print(self.archive_path)
		for ivent, (
				stdout_, except_res, 
				input_data, stderr_, 
				is_eq
			) in enumerate(self._test_executor(), 1):
			print(f"\nТест №{ivent}")
			print("===============================================")
			print(f"Входящие данные:\n{input_data}")
			print(f"Ожидаемый результат:\n{except_res}")
			print(f"Выход тестируемой программы:\n{stdout_}")
			print("===============================================")
			if not is_eq:
				if self.status == "ERROR":
					print(f"У твоей программы вышибло пробки по типу\n{stderr_}")
				elif self.status == "FAILURE":
					print(f"ПРОВАЛ! ТЕСТ №{ivent}")
				return self.status, stderr_
		if self.status == "SUCCESS":
			print("Все тесты пройдены!")
		return self.status, None

def recviz(function):
	"""
		Декоратор наглядно показывает порядок вызова функции.
		Учитывает рекурсивные вызовы. 
		Примеры: 
		
		@recviz
		def fib(n):
		    if n <= 2:
		        return 1
		    else:
		        return fib(n - 1) + fib(n - 2)
		
		fib(4)
		
		Output:
		-> fib(4)
		    -> fib(3)
		        -> fib(2)
		        <- 1
		        -> fib(1)
		        <- 1
		    <- 2
		    -> fib(2)
		    <- 1
		<- 3

		@recviz
		def fact(n):
		    if n == 0:
		        return 1
		    else:
		        return n*fact(n-1)
		        
		fact(5)
		
		Output:
		-> fact(5)
		    -> fact(4)
		        -> fact(3)
		            -> fact(2)
		                -> fact(1)
		                    -> fact(0)
		                    <- 1
		                <- 1
		            <- 2
		        <- 6
		    <- 24
		<- 120

		Хочу заметить, что, если в рекурссивной функции реализовано
		замыкание такого вида:
		def number_of_frogs(year: int):
			frogs = 77
			@recviz
			def wrapper(n: int=1) -> int:
				nonlocal frogs
				if n == year:
					return frogs
				else:
					frogs = 3 * (frogs - 30)
					# print(n)
					return wrapper(n + 1)
			return wrapper()
		слудет декорировать вложенную функцию Ы

	"""
	depth = -1
	@wraps(function)
	def wrapper(*args, **kwargs):
		nonlocal depth		
		args_str = map(str, args)
		kwargs_str = (f"{key}={repr(value)}" for key, value in kwargs.items())
		all_args = ', '.join(list(args_str) + list(kwargs_str))
		func_name = f"{function.__name__}({all_args})"
		depth += 1
		print(f"{depth * ' ' * 4}-> " + func_name)
		res = function(*args, **kwargs)
		print(f"{depth * ' ' * 4}<- {repr(res)}")
		depth -= 1
		return res
	return wrapper


def measure(function) -> Callable:
	"""
		Декоратор вычисляет время работы программы и
		пиковое значение памяти.
		Выводит на экран вычисленное время и память
	"""
	@wraps(function)
	def wrapper(*args, **kwargs) -> Any:
		tracemalloc.start()
		start_time = time.perf_counter()
		res = function(*args, **kwargs)
		end_time = time.perf_counter()
		current, peak = tracemalloc.get_traced_memory()
		print(f"Время выполнения программы: {end_time - start_time}")
		print(f"Текущая память: {current / 1024 / 1024:.2f} MB")
		print(f"Пиковое использование памяти: {peak / 1024 / 1024:.2f} MB")
		tracemalloc.stop()
		return res
	return wrapper


def reply(r: int=1) -> Callable:
	"""
		Декоратор для повтора вызова декорирумой функции.
		r: int - Сколько раз повтрить вызов функции
		Возвращает словарь вида: "номер_вызов": "результат"
	"""
	def decorator(function) -> Callable:
		@wraps(function)
		def wrapper(*args, **kwargs) -> Any:
			cache = {}
			for ivent in range(r + 1):
				res = function(*args, **kwargs)
				cache[ivent] = res
			return cache
		return wrapper
	return decorator


if __name__ == "__main__":
	obj = TestExecutor()
	obj.run()
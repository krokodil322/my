import datetime as dt



year, month = int(input()), int(input())
in_date = dt.date(year=year, day=1, month=month)
while in_date.isoweekday() != 4:
	in_date += dt.timedelta(days=1) 
in_date += dt.timedelta(days=21)
print(in_date.strftime("%d.%m.%Y"))





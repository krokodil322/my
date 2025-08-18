from datetime import datetime
import json
import csv

with open("exam_results.csv", encoding="utf-8") as file:
	data = list(csv.DictReader(file))

data_sorted = dict()
for item in data:
	for key, value in item.items():
		if key != "email":
			if key == "score":
				value = int(value)
			data_sorted.setdefault(item["email"], dict()).setdefault(key, list()).append(value)

result = list()
for key in dict(data_sorted).keys():
	max_score = max(data_sorted[key]["score"])
	score_datetime = list()
	for score, date in zip(data_sorted[key]["score"], data_sorted[key]["date_and_time"]):
		if score == max_score:
			score_datetime.append([score, datetime.strptime(date, "%Y-%m-%d %H:%M:%S")])
	max_score_datetime = max(score_datetime, key=lambda pack: pack[1])
	item =	{
				"name": data_sorted[key]["name"][0],
				"surname": data_sorted[key]["surname"][0],
				"best_score": max_score_datetime[0], 
				"date_and_time": max_score_datetime[1].strftime("%Y-%m-%d %H:%M:%S"),
				"email": key
			}
	result.append(item)
result.sort(key=lambda pack: pack["email"])

with open("best_scores.json", 'w', encoding="utf-8") as file:
	json.dump(result, fp=file, indent=3)

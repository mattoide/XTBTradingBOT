import datetime


now = datetime.datetime.now()
now_time = now.time()

print(now_time)

if datetime.time(9,00) <= now_time <= datetime.time(22,00):
    print("in orario")
else:
    print("fuori orario")

print(datetime.datetime.today().weekday())
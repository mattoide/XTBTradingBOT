import datetime



yesterady = datetime.datetime.now() - datetime.timedelta(minutes=80)
yesterady = "{:10.3f}".format(yesterady.timestamp()).replace('.', '')
print(yesterady)

import datetime


for i in [1, 7, 20, 21]:
    message_day = datetime.datetime.now()
    #message_time = message_day.time()
    message_time = datetime.time(hour=i, minute=0)
    midnight = datetime.time(hour=0, minute=0)
    if message_time.hour in range(6, 21):
        print()
    else:
        if message_time.hour in range(0, 6):
            message_time = midnight
            message_day -= datetime.timedelta(days=1)
    message_day = datetime.date.strftime(message_day, '%d.%m.%y')

    print(message_day, message_time)
    print()

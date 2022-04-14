import json

def task_push(args):
    with open('config.json') as json_file:
        config = json.load(json_file)
    few_days = config['calendar']['few_days']
    week_days = config['calendar']['week_days']
    month_days = config['calendar']['month_days']
    hours = config['clock']
    day_time = config['calendar']['day_time']
    symbols = config['symbols']
    event = args[0]
    select_day = []
    for day in few_days:
        if day in args[0]:
            try:
                select_day.append(day)
                event.remove(day)
            except:pass
    for day in week_days:
        if day in args[0]:
            try:
                select_day.append(day)
                event.remove(day)
            except:pass
    for day in month_days:
        if day in args[0]:
            try:
                select_day.append(day)
                event.remove(day)
            except:pas

    for symbol in symbols:
        if symbol in args[0]:
            try:
                select_day.append(symbol)
                event.remove(symbol)
            except:pass
    for hour_ in hours:
        if hour_ in args[0]:
            try:
                select_day.append(hour_)
                event.remove(hour_)
            except:pass
    for day in day_time:
        if day in args[0]:
            try:
                select_day.append(day)
                event.remove(day)
            except:pass


    select_day = ' '.join(select_day)
    event = ' '.join(event)
    task = []
    task.append({"date":select_day,"task":event})
    return task

def tasks_get():
    pass

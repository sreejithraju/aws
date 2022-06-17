from datetime import datetime
import re

def verify_schedule(schedules, offset=0):  
    #Example schedules = 'Monday:19:06,Tuesday:19:06,Wednesday:14:40,Friday:19:06,Satureday:24:24,Sunday:24:24'
    
    # get currect UTC time 
    utcnow = datetime.utcnow()
    weekday_now = utcnow.strftime("%A")
    hour_now = utcnow.strftime("%H")
    minutes_now = utcnow.strftime("%M")
    date_now = datetime(utcnow.year,utcnow.month,utcnow.day,int(hour_now),int(minutes_now) )
    print(f"Current UTC time  : {date_now} ")
    
    # Check each schedules and check if it falls in current time
    schedules = schedules.split(',')
    p = re.compile(f'^{weekday_now}.*$')
    schedules_today = [ s for s in schedules if p.match(s) ]
    
    
    for schedule in schedules_today:
        print(schedule)
        weekday_scheduled = schedule.split(":")[0]
        print(weekday_scheduled)
        hour_scheduled = schedule.split(":")[1]
        print(hour_scheduled)
        minutes_scheduled = schedule.split(":")[2]
        
        
        if hour_scheduled == '24' and minutes_scheduled == '24' :
            print("24:24 found")
            break
        # Check if the day matches ex: Monday match Monday
        
        if (weekday_scheduled == weekday_now ):
            #print("Weekday match.")
            date_scheduled = datetime(utcnow.year,utcnow.month,utcnow.day,int(hour_scheduled),int(minutes_scheduled) )
            #Calculate the difference of the time
            date_diff = date_scheduled - date_now
            time_diff = int(date_diff.total_seconds()/60)
        
            if (time_diff <= 0) and (time_diff >= (-1 * offset)):
             #print("Schedule match!!")
                return True          
    return False

schedules = 'Monday:19:06,Tuesday:19:06,Wednesday:14:40,Friday:19:06,Satureday:24:24,Sunday:24:24'
print(verify_schedule(schedules))
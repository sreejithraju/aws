from datetime import datetime

def verify_schedule(scheduledtime, offset=0):  
    #scheduledtime = "Wednesday:11:45"  scheduled time format
    
    weekday_scheduled = scheduledtime.split(":")[0]
    hour_scheduled = scheduledtime.split(":")[1]
    minutes_scheduled = scheduledtime.split(":")[2]
    print(f"Scheduled time : {weekday_scheduled}:{hour_scheduled}:{minutes_scheduled}" )
    utcnow = datetime.utcnow()
    weekday_now = utcnow.strftime("%A")
    hour_now = utcnow.strftime("%H")
    minutes_now = utcnow.strftime("%M")
    print(f"UTC time now : {weekday_now}:{hour_now}:{minutes_now}" )

    # Check if the day matches
    
    if (weekday_scheduled == weekday_now ):
        print("Weekday match.")
        date_scheduled = datetime(utcnow.year,utcnow.month,utcnow.day,int(hour_scheduled),int(minutes_scheduled) )
        date_now = datetime(utcnow.year,utcnow.month,utcnow.day,int(hour_now),int(minutes_now) )
        #print(f"Date sccheduled : {date_scheduled}")
        #print(f"date now : {date_now} ")

        date_diff = date_scheduled - date_now
        time_diff = int(date_diff.total_seconds()/60)
        result = False
        if (time_diff <= 0) and (time_diff >= (-1 * offset)):
             result = True
    
    else:
        print("Weekday does not match.")
        result = False
    return result 
         
    
print(verify_schedule("Wednesday:12:11"))

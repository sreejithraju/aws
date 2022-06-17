from datetime import datetime
from signal import SIG_DFL
import boto3

def verify_schedule(scheduledtime, offset=0):  
    #scheduledtime = "Wednesday:11:45" # scheduled time format
    
    weekday_scheduled = scheduledtime.split(":")[0]
    hour_scheduled = scheduledtime.split(":")[1]
    minutes_scheduled = scheduledtime.split(":")[2]
    #print(f"Verifying Scheduled time : {weekday_scheduled}:{hour_scheduled}:{minutes_scheduled}" )
    utcnow = datetime.utcnow()
    weekday_now = utcnow.strftime("%A")
    hour_now = utcnow.strftime("%H")
    minutes_now = utcnow.strftime("%M")
    

    # Check if the day matches
    
    if (weekday_scheduled == weekday_now ):
        #print("Weekday match.")
        print(f"UTC time now : {weekday_now}:{hour_now}:{minutes_now}" )
        date_scheduled = datetime(utcnow.year,utcnow.month,utcnow.day,int(hour_scheduled),int(minutes_scheduled) )
        date_now = datetime(utcnow.year,utcnow.month,utcnow.day,int(hour_now),int(minutes_now) )
        #print(f"Date sccheduled : {date_scheduled}")
        #print(f"date now : {date_now} ")

        date_diff = date_scheduled - date_now
        time_diff = int(date_diff.total_seconds()/60)
        
        if (time_diff <= 0) and (time_diff >= (-1 * offset)):
            #print("Schedule match!!")
            return True
            
    return False
         
    
#print(verify_schedule("Wednesday:12:11"))
region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)

response = ec2.describe_instances(
    Filters=[
      
         {
            'Name': 'tag:AutoShutdownSchedule',
            'Values': [
                '*'
            ]
        }
    ]
    
)

def find_schedule(AutoShutdownSchedule):
    
    AutoShutdownSchedule= 'Monday:19:06,Tuesday:19:06,Wednesday:14:40,Friday:19:06,Satureday:24:24,Sunday:24:24'
    print(AutoShutdownSchedule)
    schedules = AutoShutdownSchedule.split(',')
    for schedule in schedules:
        if verify_schedule(schedule):
            return True
    return False
       
                    
                    
    
def get_scheduled_instance_ids():

    instances = ec2.describe_instances()
    instance_ids = []
    criteria1 = False
    criteria2 = False
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            if 'Tags' in instance:
                for tag in instance['Tags']:
                    #print(tag)
                    if tag['Key'] == 'SuspendSchedule' and tag['Value'] == "No":
                        criteria1 = True
                    if tag['Key'] == 'AutoShutdownSchedule' and tag['Value'] :
                        criteria2 = True
                    if criteria1 and criteria2:
                        print(f"AutoShutdownSchedule : {tag['Value']} ")
                        if find_schedule(tag['Value']):
                            instance_ids.append(instance["InstanceId"])
    return instance_ids
                        
print(get_scheduled_instance_ids())                   
                    
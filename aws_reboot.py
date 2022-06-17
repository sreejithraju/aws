from datetime import datetime
import boto3

def verify_schedule(scheduledtime, offset=0):  
    #scheduledtime = "Wednesday:11:45"  scheduled time format
    
    weekday_scheduled = scheduledtime.split(":")[0]
    hour_scheduled = scheduledtime.split(":")[1]
    minutes_scheduled = scheduledtime.split(":")[2]
    #print(f"Verifying Scheduled time : {weekday_scheduled}:{hour_scheduled}:{minutes_scheduled}" )
    utcnow = datetime.utcnow()
    weekday_now = utcnow.strftime("%A")
    hour_now = utcnow.strftime("%H")
    minutes_now = utcnow.strftime("%M")
    #print(f"UTC time now : {weekday_now}:{hour_now}:{minutes_now}" )

    # Check if the day matches
    
    if (weekday_scheduled == weekday_now ):
        #print("Weekday match.")
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
        #print("Weekday does not match.")
        result = False
    return result 
         
    
#print(verify_schedule("Wednesday:12:11"))
region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)
tag_key_f = 'SuspendSchedule'
tag_val_f = 'No'
#instances = ec2.describe_instances(Filters=[{'Name': 'tag:'+tag_key_f, 'Values': [tag_val_f]}])
#instances = ec2.describe_instances(Filters=[{'Name': 'tag:AutoShutdownSchedule'}])
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

if response :
    statuscode = response['ResponseMetadata']['HTTPStatusCode']
    if statuscode == 200:
        print("Successfully connected to AWS")
    else:
        print("AWS connection error : Status code = {}".format(statuscode))
        raise SystemExit
else:
    print("No response from AWS")
    raise SystemExit

reservations = response["Reservations"]
if reservations:
    print(f"reservations : {len(reservations)}")
    instances = reservations[0]["Instances"]
    print(f"Instances = {len(instances)}")
    if len(instances) < 1 :
        print("No Instances found")
        raise SystemExit
else:
    print("No VMs found matching the criteria")
    raise SystemExit

for instance in instances:
    tags = instance['Tags']
    #print(tags)
    vmname = list(filter(lambda x: x['Key'] == 'Name' , tags))[0]['Value']
    print(f"VM Name = {vmname}")
    AutoShutdownSchedule = list(filter(lambda x: x['Key'] == 'AutoShutdownSchedule' , tags))
    if AutoShutdownSchedule:
        #print("AutoShutdownSchedule Key found")
        AutoShutdownSchedule_value = AutoShutdownSchedule[0]['Value']
        print(f"AutoShutdownSchedule = {AutoShutdownSchedule_value}")
    else:
        print("AutoShutdownSchedule Key not found")
        
    SuspendSchedule = list(filter(lambda x: x['Key'] == 'SuspendSchedule' , tags))
    if SuspendSchedule:
        #print("AutoShutdownSchedule Key found")
        SuspendSchedule_value = SuspendSchedule[0]['Value']
        print(f"SuspendSchedule = {SuspendSchedule_value}")
    else:
        print("SuspendSchedule Key not found")
    
    if SuspendSchedule_value == "Yes" and AutoShutdownSchedule_value:
        print("Cheking schedules")
        schedules = AutoShutdownSchedule_value.split(',')
        if schedules:
            print(f"Schedules found : {schedules}")
            for schedule in schedules:
                schedule_match = verify_schedule(schedule)
                if schedule_match:
                     break
            
        else:
            print("No Schedules found")
    
    if schedule_match:
        print("Matching Schedule found now")
    else:
        print(f"Schedule is not matched Skip this instance '{vmname}'")
        
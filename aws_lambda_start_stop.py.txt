from datetime import datetime
import boto3, re,time

region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)


def lambda_handler(event, context):
    startstop_instances()


def check_start_stop_schedule(AutoShutdownSchedule):
    #print('check_start_stop_schedule')
    print(f"\tAutoShutdownSchedule : {AutoShutdownSchedule}")
    # get currect UTC time 
    utcnow = datetime.utcnow()
    weekday_now = utcnow.strftime("%A")
    hour_now = int(utcnow.strftime("%H"))
    minutes_now = utcnow.strftime("%M")
    date_now = datetime(utcnow.year,utcnow.month,utcnow.day,int(hour_now),int(minutes_now) )
    print(f"\tCurrent UTC time  : {date_now} , day : {weekday_now} , hour : {hour_now}")
    
    #check AutoShutdownSchedule
    schedules = AutoShutdownSchedule.split(',')
    #print(f"\tSchedules found = {len(schedules)}")
    
    #find schedule matching the current day ex. Monday . Tuesday etc
    pattern = re.compile(f'^{weekday_now}.*$')
    schedules_today = [ s for s in schedules if pattern.match(s) ]
    print(f"\ttoday's schedules = {schedules_today}")
    if not schedules_today:
        print("\tThere is no schedule found today for this Instance")
        return False
    schedule = schedules_today[0]
    stop_time = schedule.split(':')[1]
    start_time = schedule.split(':')[2]
    print(f"\tStart :{start_time} , Stop : {stop_time}")
    
    if stop_time == 24 and start_time == 24:
        print("\tStart time and stop time is 24 : Skip the operation")
        return False
    
    #check if start and stop time is equal in the schedule
    if stop_time == start_time:
        print("\tStart time and stop time is equal : Skip the operation")
        return False
      
    #check if stop time fall in this hour , if so sent "stop" to calling function
    if  int(stop_time) == hour_now:
        print("\tStop time match")
        return "stop"
        
    #check if start time fall in this hour , if so sent "start" to calling function
    if  int(start_time) == hour_now:
        print("\tStart time match")
        return "start"
    
    return True

def verify_schedule(tags):
    task = 'Validate Tags'
    SuspendSchedule_found = False
    AutoShutdownSchedule_found = False
    SuspendSchedule = None
    AutoShutdownSchedule = None

    for tag in tags:
    
        #check if there is  a tag named 'SuspendSchedule'
        if tag['Key'] == 'SuspendSchedule':
            SuspendSchedule_found = True
            SuspendSchedule = tag['Value']
        
        #check if there is a tag named 'AutoShutdownSchedule'
        if tag['Key'] == 'AutoShutdownSchedule':
            AutoShutdownSchedule_found = True
            AutoShutdownSchedule = tag['Value']
        
    # If there is no tag named 'AutoShutdownSchedule' then Skip the server
    if not AutoShutdownSchedule_found:
        print(f'\t{task} : Failed : The Tag "AutoShutdownSchedule" is not found ')
        return False
    # If the tag 'AutoShutdownSchedule' contain no value then Skip the server
    if not AutoShutdownSchedule:
        print(f'\t{task} : Failed : The Tag "AutoShutdownSchedule" is empty ')
        return False
    # if SuspendSchedule = Yes/yes skip the serve\
    if SuspendSchedule == 'Yes' or SuspendSchedule == 'yes':
        print(f'\t{task} : Failed : The Tag "SuspendSchedule" is set to "Yes" ')
        return False
    print(f'\t{task} : Success : Checking the Start / Stop Schedule ')
    return check_start_stop_schedule(AutoShutdownSchedule)
 
    return False           
    
def startstop_instances():

    instances = ec2.describe_instances()
    start_instances = []
    stop_instances = []
    
    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            vmname = list(filter(lambda x: x['Key'] == 'Name' , instance['Tags']))[0]['Value']
            print(f"Instance : {vmname}")
            if 'Tags' in instance:
                result =verify_schedule(instance['Tags']) 
                
                if result == 'start':
                    print("\tStart schedule found")
                    start_instances.append({'name' : vmname ,'id' : instance["InstanceId"]}) 
                elif result == 'stop':
                    print("\tStop schedule found")
                    stop_instances.append({'name' : vmname ,'id' : instance["InstanceId"]})  
                else:
                    print("\tNo matching schedule found")     
    
    print("The following instances will be stopped ")
    print(stop_instances)
    if stop_instances:
        stop_instance_ids=list(map(lambda x: x['id'], stop_instances))
        ec2.stop_instances(InstanceIds=stop_instance_ids)
    
    print("The following instances will be started ")
    print(start_instances)
    if start_instances:
        
        start_instance_ids=list(map(lambda x: x['id'], start_instances))
        ec2.start_instances(InstanceIds=start_instance_ids)

    #waiting for started servers 
    print("\nWaiting for servers to be staterd")
    print('=================================\n')
    if start_instances:
        waitfor_status(start_instance_ids,"running",5)
    else:
        print("No Instances to be started")
        
    #waiting for stopped servers 
    print("\nWaiting for servers to be stopped")
    print('=================================\n')
    if stop_instances:
        waitfor_status(stop_instance_ids,"stopped",5)
    else:
        print("No Instances to be stopped")     
        
                
#print(get_scheduled_instance_ids())                   
def waitfor_status(instane_ids,final_status,timeout_mins):
    loop = True
    count = 0
    interval = 10
    while loop:
   
        
        
        loop = False
        out = []
        response = ec2.describe_instances(InstanceIds=instane_ids)
        for r in response['Reservations']:
            for i in r['Instances']:
                vmname = list(filter(lambda x: x['Key'] == 'Name' , i['Tags']))[0]['Value']
                state = i['State']["Name"]
                id = i['InstanceId']
                out.append(f"{vmname}  : {state} : {id}")
                if state != final_status: loop = True
        
        count += 1
        mins = interval * count / 60
        
        if mins > timeout_mins: break
        time.sleep(interval)
    for x in out:
        print(x)
    print(f"Time taken : {round(mins,1)} mins")




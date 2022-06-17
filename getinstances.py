import boto3
region = 'us-east-1'
ec2 = boto3.client('ec2', region_name=region)
instances = ec2.describe_instances()['Reservations'][0]['Instances']
for instance in instances:
    tags = instance['Tags']
    print(tags)
    AutoShutdownSchedule = list(filter(lambda x: x['Key'] == 'AutoShutdownSchedule' , tags))[0]['Value']
    print(AutoShutdownSchedule)
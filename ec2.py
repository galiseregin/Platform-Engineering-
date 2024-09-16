import boto3
from botocore.exceptions import ClientError

AMI_IDS = {
    'ubuntu': 'ami-0e86e20dae9224db8',
    'amazon-linux': 'ami-0182f373e66f89c85'
}

def get_ami_id(ami_choice):
    return AMI_IDS.get(ami_choice)

def create_instance(instance_type, ami_id, name):
    ec2 = boto3.resource('ec2')
    ec2_client = boto3.client('ec2')
    
    try:
        running_instances = ec2_client.describe_instances(Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:CLICheck', 'Values': ['True']}
        ])
        
        running_count = sum(len(reservation['Instances']) for reservation in running_instances['Reservations'])
        
        if running_count >= 2:
            print("You can't create more than two instances.")
            return
        
        instances = ec2.create_instances(
            InstanceType=instance_type,
            ImageId=ami_id,
            MinCount=1,
            MaxCount=1,
            NetworkInterfaces=[{
                'SubnetId': 'subnet-04fd6d8b7687e3c02',
                'AssociatePublicIpAddress': True,
                'Groups': ['sg-077a4a27e9b9e80a2'],
                'DeviceIndex': 0
            }],
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': name},
                    {'Key': 'CLICheck', 'Value': 'True'}
                ]
            }]
        )
        print(f"Instance {name} created.")
        return instances
    except ClientError as e:
        print(f"Error creating instance: {e}")

def _check_instance_cli_created(ec2_client, instance_id):
    try:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        if tags.get('CLICheck') != 'True':
            raise PermissionError(f"Instance {instance_id} was not created by this CLI.")
    except ClientError as e:
        print(f"Error checking instance: {e}")
        raise

def start_instance(instance_id):
    ec2 = boto3.client('ec2')
    try:
        _check_instance_cli_created(ec2, instance_id)
        ec2.start_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} has been started.")
    except ClientError as e:
        print(f"Error starting instance: {e}")

def stop_instance(instance_id):
    ec2 = boto3.client('ec2')
    try:
        _check_instance_cli_created(ec2, instance_id)
        ec2.stop_instances(InstanceIds=[instance_id])
        print(f"Instance {instance_id} has been stopped.")
    except ClientError as e:
        print(f"Error stopping instance: {e}")

def list_instances():
    ec2 = boto3.client('ec2')
    try:
        response = ec2.describe_instances(Filters=[
            {'Name': 'tag:CLICheck', 'Values': ['True']}
        ])
        instances = [
            {
                'InstanceId': instance['InstanceId'],
                'State': instance['State']['Name'],
                'InstanceType': instance['InstanceType']
            }
            for reservation in response['Reservations']
            for instance in reservation['Instances']
        ]
        if instances:
            print("Instances created by CLI:")
            for instance in instances:
                print(f"ID: {instance['InstanceId']}, State: {instance['State']}, Type: {instance['InstanceType']}")
        else:
            print("No instances found created by this CLI.")
        return instances
    except ClientError as e:
        print(f"Error listing instances: {e}")
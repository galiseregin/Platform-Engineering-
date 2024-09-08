import boto3
import argparse

ec2 = boto3.resource('ec2')

def create_instance(instance_type, ami_id):
    instances = ec2.create_instances(
        ImageId=ami_id,
        InstanceType=instance_type,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            'ResourceType': 'instance',
            'Tags': [{'Key': 'CreatedBy', 'Value': 'CLI-Tool'}]
        }]
    )
    print(f"Created instance {instances[0].id} of type {instance_type}")

def list_instances():
    instances = ec2.instances.filter(Filters=[{'Name': 'tag:CreatedBy', 'Values': ['CLI-Tool']}])
    for instance in instances:
        print(f"Instance ID: {instance.id}, State: {instance.state['Name']}")


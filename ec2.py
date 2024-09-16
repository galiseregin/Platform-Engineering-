import boto3
from botocore.exceptions import ClientError

# AMI IDs for different OS choices
AMI_IDS = {
    'ubuntu': 'ami-0e86e20dae9224db8',
    'amazon-linux': 'ami-0182f373e66f89c85'
}

# Function to get the AMI ID based on the choice of OS
def get_ami_id(ami_choice):
    return AMI_IDS.get(ami_choice)

# Function to create an EC2 instance
def create_instance(instance_type, ami_id, name):
    ec2 = boto3.resource('ec2')  # Get the EC2 resource
    ec2_client = boto3.client('ec2')  # Get the EC2 client for API actions
    
    try:
        # Check how many instances with the CLICheck tag set to True are running
        running_instances = ec2_client.describe_instances(Filters=[
            {'Name': 'instance-state-name', 'Values': ['running']},
            {'Name': 'tag:CLICheck', 'Values': ['True']}
        ])
        
        # Count how many instances are currently running
        running_count = sum(len(reservation['Instances']) for reservation in running_instances['Reservations'])
        
        # If there are already two running instances, prevent creating more
        if running_count >= 2:
            print("You can't create more than two instances.")
            return
        
        # Create a new EC2 instance with the specified instance type and AMI ID
        instances = ec2.create_instances(
            InstanceType=instance_type,  # The instance type (e.g., t2.micro)
            ImageId=ami_id,  # The AMI ID for the chosen OS
            MinCount=1,  # Minimum number of instances to launch
            MaxCount=1,  # Maximum number of instances to launch
            NetworkInterfaces=[{  # Define network settings
                'SubnetId': 'subnet-04fd6d8b7687e3c02',  # Replace with your subnet ID
                'AssociatePublicIpAddress': True,  # Assign a public IP
                'Groups': ['sg-077a4a27e9b9e80a2'],  # Replace with your security group ID
                'DeviceIndex': 0  # Attach this network interface as the primary
            }],
            TagSpecifications=[{  # Add tags to the instance
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': name},  # Instance name
                    {'Key': 'CLICheck', 'Value': 'True'}  # Custom tag to check CLI-created instances
                ]
            }]
        )
        print(f"Instance {name} created.")
        return instances
    except ClientError as e:
        print(f"Error creating instance: {e}")

# Helper function to check if an instance was created by the CLI tool
def _check_instance_cli_created(ec2_client, instance_id):
    try:
        # Describe the instance to retrieve its tags
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        instance = response['Reservations'][0]['Instances'][0]
        
        # Get instance tags and check if the CLICheck tag is present
        tags = {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])}
        if tags.get('CLICheck') != 'True':
            raise PermissionError(f"Instance {instance_id} was not created by this CLI.")
    except ClientError as e:
        print(f"Error checking instance: {e}")
        raise

# Function to start an EC2 instance
def start_instance(instance_id):
    try:
        # Code to start the instance goes here
        pass  # Replace with actual logic
    except ClientError as e:
        print(f"Error starting instance: {e}")

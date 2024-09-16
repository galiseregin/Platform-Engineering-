import json
import boto3
import os
from botocore.exceptions import ClientError

def create_bucket(bucket_name, access):
    s3 = boto3.client('s3')
    
    try:
        create_bucket_config = {'LocationConstraint': s3.meta.region_name} if s3.meta.region_name != 'us-east-1' else {}
        
        s3.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration=create_bucket_config or None
        )
        
        if access == 'public':
            policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": "*",
                        "Action": "s3:GetObject",
                        "Resource": f"arn:aws:s3:::{bucket_name}/*"
                    }
                ]
            }
            s3.put_bucket_policy(Bucket=bucket_name, Policy=json.dumps(policy))
            print(f"Public bucket '{bucket_name}' created successfully.")
        else:
            print(f"Private bucket '{bucket_name}' created successfully.")
        
        s3.put_bucket_tagging(
            Bucket=bucket_name,
            Tagging={'TagSet': [{'Key': 'CLI', 'Value': 'True'}]}
        )
        print(f"Tag 'CLI: True' added to bucket '{bucket_name}'.")
    
    except ClientError as e:
        print(f"Error creating bucket: {e}")

def upload_file(bucket_name, file_path):
    s3 = boto3.client('s3')
    
    try:
        file_name = os.path.basename(file_path)
        s3.upload_file(file_path, bucket_name, file_name)
        print(f"File '{file_name}' uploaded to bucket '{bucket_name}' successfully.")
    
    except ClientError as e:
        print(f"Error uploading file: {e}")

def list_buckets():
    s3 = boto3.client('s3')
    
    try:
        response = s3.list_buckets()
        cli_buckets = []
        
        for bucket in response['Buckets']:
            try:
                tags = s3.get_bucket_tagging(Bucket=bucket['Name'])['TagSet']
                if any(tag['Key'] == 'CLI' and tag['Value'] == 'True' for tag in tags):
                    cli_buckets.append(bucket['Name'])
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchTagSet':
                    print(f"Could not retrieve tags for bucket '{bucket['Name']}': {e}")
        
        if cli_buckets:
            print("Buckets with 'CLI' tag:")
            for bucket_name in cli_buckets:
                print(f"Name: {bucket_name}")
        else:
            print("No buckets with 'CLI' tag found.")
    
    except ClientError as e:
        print(f"Error listing buckets: {e}")
import boto3

s3 = boto3.client('s3')

def create_bucket(bucket_name, public=False):
    acl = 'public-read' if public else 'private'
    s3.create_bucket(Bucket=bucket_name, ACL=acl)
    s3.put_bucket_tagging(
        Bucket=bucket_name,
        Tagging={'TagSet': [{'Key': 'CreatedBy', 'Value': 'CLI-Tool'}]}
    )
    print(f"Bucket {bucket_name} created with ACL {acl}")

# Further methods for file upload and listing buckets.

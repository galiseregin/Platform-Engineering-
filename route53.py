import boto3
from botocore.exceptions import ClientError

def create_dns_zone(zone_name):
    route53 = boto3.client('route53')
    try:
        response = route53.create_hosted_zone(
            Name=zone_name,
            VPC={
                 'VPCRegion': 'us-east-1',
                 'VPCId': 'vpc-0d71c82cbbd1ba3bb'
             },
            CallerReference=str(hash(zone_name))
        )
        zone_id = response['HostedZone']['Id']
        print(f"DNS zone '{zone_name}' created successfully. Zone ID: {zone_id}")
        return zone_id
    except ClientError as e:
        print(f"Error creating DNS zone: {e}")

def manage_dns_record(zone_id, record_name, record_type, record_value, action):
    route53 = boto3.client('route53')
    try:
        change_batch = {
            'Changes': [
                {
                    'Action': action.upper(),  # CREATE, UPDATE, or DELETE
                    'ResourceRecordSet': {
                        'Name': record_name,
                        'Type': record_type,
                        'TTL': 300,
                        'ResourceRecords': [{'Value': record_value}]
                    }
                }
            ]
        }
        route53.change_resource_record_sets(
            HostedZoneId=zone_id,
            ChangeBatch=change_batch
        )
        print(f"DNS record '{record_name}' {action}d successfully.")
    except ClientError as e:
        print(f"Error managing DNS record: {e}")

def list_dns_zones():
    route53 = boto3.client('route53')
    try:
        response = route53.list_hosted_zones()
        zones = response['HostedZones']
        if zones:
            print("DNS Zones:")
            for zone in zones:
                print(f"Name: {zone['Name']}, ID: {zone['Id']}")
        else:
            print("No DNS zones found.")
        return zones
    except ClientError as e:
        print(f"Error listing DNS zones: {e}")
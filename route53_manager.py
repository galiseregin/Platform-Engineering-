import boto3

route53 = boto3.client('route53')

def create_zone(domain_name):
    response = route53.create_hosted_zone(
        Name=domain_name,
        CallerReference=str(hash(domain_name)),
        HostedZoneConfig={'Comment': 'Created by CLI-Tool'}
    )
    print(f"Created hosted zone {domain_name} with ID {response['HostedZone']['Id']}")

# Further methods for managing DNS records.

import argparse
from ec2 import create_instance, start_instance, stop_instance, list_instances, get_ami_id
from s3 import create_bucket, upload_file, list_buckets
from route53 import create_dns_zone, manage_dns_record, list_dns_zones

def parse_arguments():
    parser = argparse.ArgumentParser(description='AWS resource management Tool')

    # General flags
    parser.add_argument('--resource', type=str, required=True, choices=['ec2', 's3', 'route53'], metavar='')
    parser.add_argument('--action', type=str, help='Action to perform (e.g., create, list)', metavar='')
    
    # EC2 flags
    parser.add_argument('--name', type=str, help='Name of the instance, bucket, or DNS zone', metavar='')
    parser.add_argument('--instance-id', type=str, help='Instance ID for start/stop actions', metavar='')
    parser.add_argument('--instance-type', type=str, choices=['t3.nano', 't4g.nano'], help='Type of EC2 instance', metavar='')
    parser.add_argument('--ami', type=str, choices=['ubuntu', 'amazon-linux'], help='AMI choice', metavar='')
    
    # S3 flags
    parser.add_argument('--access', type=str, choices=['public', 'private'], help='Access type for bucket creation', metavar='')
    parser.add_argument('--file', type=str, help='File path for uploading to the S3 bucket', metavar='')
    
    # Route 53 flags
    parser.add_argument('--zone-id', type=str, help='Zone ID for DNS record management', metavar='')
    parser.add_argument('--record-type', type=str, help='Type of DNS record (e.g., A, CNAME)', metavar='')
    parser.add_argument('--record-name', type=str, help='Name of the DNS record', metavar='')
    parser.add_argument('--record-value', type=str, help='Value of the DNS record', metavar='')
    parser.add_argument('--record-action', type=str, choices=['create', 'update', 'delete'], help='Action for DNS record', metavar='')
    
    args = parser.parse_args()

    # If --record-action flag is present, It won't require --action flag 
    if args.resource == 'route53' and args.record_action:
        args.action = f'{args.record_action}-record'

    return args

def handle_ec2(args):
    if args.action == 'create':
        ami_id = get_ami_id(args.ami)
        if not ami_id:
            print("Invalid AMI choice.")
            return
        create_instance(args.instance_type, ami_id, args.name)
    elif args.action == 'start':
        if not args.instance_id:
            print("Instance ID is required to start an instance.")
            return
        start_instance(args.instance_id)
    elif args.action == 'stop':
        if not args.instance_id:
            print("Instance ID is required to stop an instance.")
            return
        stop_instance(args.instance_id)
    elif args.action == 'list':
        list_instances()
    else:
        print(f"Unknown EC2 action: {args.action}")

def handle_s3(args):
    if args.action == 'create':
        if not args.name or not args.access:
            print("Error: --name and --access are required for creating a bucket.")
            return
        if args.access == 'public' and input("Public bucket selected. Are you sure? (yes/no): ").lower() != 'yes':
            print("Bucket creation cancelled.")
            return
        create_bucket(args.name, args.access)
    elif args.action == 'upload':
        if not args.name or not args.file:
            print("Error: --name and --file are required for file upload.")
            return
        upload_file(args.name, args.file)
    elif args.action == 'list':
        list_buckets()
    else:
        print(f"Unknown S3 action: {args.action}")

def handle_route53(args):
    if args.action == 'create':
        if not args.name:
            print("Error: --name is required to create a DNS zone.")
            return
        create_dns_zone(args.name)
    elif args.action in ['create-record', 'update-record', 'delete-record']:
        if not all([args.zone_id, args.record_name, args.record_type, args.record_value]):
            print("Error: --zone-id, --record-name, --record-type, and --record-value are required for managing records.")
            return
        manage_dns_record(args.zone_id, args.record_name, args.record_type, args.record_value, args.action.split('-')[0])
    elif args.action == 'list':
        list_dns_zones()
    else:
        print(f"Unknown Route53 action: {args.action}")

def main():
    args = parse_arguments()
    
    handlers = {
        'ec2': handle_ec2,
        's3': handle_s3,
        'route53': handle_route53
    }
    
    handler = handlers.get(args.resource)
    if handler:
        handler(args)
    else:
        print(f"Unknown resource: {args.resource}")

if __name__ == "__main__":
    main()

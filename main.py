import argparse
from ec2 import create_instance, start_instance, stop_instance, list_instances, get_ami_id
from s3 import create_bucket, upload_file, list_buckets
from route53 import create_dns_zone, manage_dns_record, list_dns_zones

# Function to handle the command-line arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='AWS resource management Tool')

    # General flags
    parser.add_argument('--resource', type=str, required=True, choices=['ec2', 's3', 'route53'], metavar='', help='Specify the AWS resource (EC2, S3, or Route 53)')
    parser.add_argument('--action', type=str, help='Action to perform (e.g., create, list)', metavar='')

    # EC2 flags
    parser.add_argument('--name', type=str, help='Name of the instance, bucket, or DNS zone', metavar='')
    parser.add_argument('--instance-id', type=str, help='Instance ID for start/stop actions', metavar='')
    parser.add_argument('--instance-type', type=str, choices=['t3.nano', 't4g.nano'], help='Type of EC2 instance', metavar='')
    parser.add_argument('--ami', type=str, choices=['ubuntu', 'amazon-linux'], help='AMI choice (Ubuntu or Amazon Linux)', metavar='')

    # S3 flags
    parser.add_argument('--access', type=str, choices=['public', 'private'], help='Access type for S3 bucket creation', metavar='')
    parser.add_argument('--file', type=str, help='File path for uploading to the S3 bucket', metavar='')

    # Route 53 flags
    parser.add_argument('--zone-id', type=str, help='Zone ID for DNS record management', metavar='')
    parser.add_argument('--record-type', type=str, help='Type of DNS record (e.g., A, CNAME)', metavar='')
    parser.add_argument('--record-name', type=str, help='Name of the DNS record', metavar='')
    parser.add_argument('--record-value', type=str, help='Value of the DNS record', metavar='')
    parser.add_argument('--record-action', type=str, choices=['create', 'update', 'delete'], help='Action for DNS record management', metavar='')

    args = parser.parse_args()

    # If --record-action flag is present for Route 53, assign its value to --action for proper routing
    if args.resource == 'route53' and args.record_action:
        args.action = f'{args.record_action}-record'

    return args

# Handle EC2-related actions based on arguments
def handle_ec2(args):
    if args.action == 'create':
        # Retrieve AMI ID based on the user's choice
        ami_id = get_ami_id(args.ami)
        if not ami_id:
            print("Invalid AMI choice.")
            return
        create_instance(args.instance_type, ami_id, args.name)
    elif args.action == 'start':
        # Check if instance ID is provided for starting an instance
        if not args.instance_id:
            print("Instance ID is required to start an instance.")
            return
        start_instance(args.instance_id)
    elif args.action == 'stop':
        # Check if instance ID is provided for stopping an instance
        if not args.instance_id:
            print("Instance ID is required to stop an instance.")
            return
        stop_instance(args.instance_id)
    elif args.action == 'list':
        # List all EC2 instances
        list_instances()
    else:
        print(f"Unknown EC2 action: {args.action}")

# Handle S3-related actions based on arguments
def handle_s3(args):
    if args.action == 'create':
        # Ensure bucket name and access type are provided
        if not args.name or not args.access:
            print("Error: --name and --access are required for creating a bucket.")
            return
        # Confirm if creating a public bucket
        if args.access == 'public' and input("Public bucket selected. Are you sure? (yes/no): ").lower() != 'yes':
            print("Bucket creation cancelled.")
            return
        create_bucket(args.name, args.access)
    elif args.action == 'upload':
        # Ensure both bucket name and file path are provided for file upload
        if not args.name or not args.file:
            print("Error: --name and --file are required for file upload.")
            return
        upload_file(args.name, args.file)
    elif args.action == 'list':
        # List all S3 buckets
        list_buckets()
    else:
        print(f"Unknown S3 action: {args.action}")

# Handle Route 53-related actions based on arguments
def handle_route53(args):
    if args.action == 'create':
        # Ensure a name is provided for creating a DNS zone
        if not args.name:
            print("Error: --name is required to create a DNS zone.")
            return
        create_dns_zone(args.name)
    elif args.action in ['create-record', 'update-record', 'delete-record']:
        # Ensure required parameters for DNS record management are provided
        if not all([args.zone_id, args.record_name, args.record_type, args.record_value]):
            print("Error: --zone-id, --record-name, --record-type, and --record-value are required for managing records.")
            return
        manage_dns_record(args.zone_id, args.record_name, args.record_type, args.record_value, args.action.split('-')[0])
    elif args.action == 'list':
        # List all Route 53 DNS zones
        list_dns_zones()
    else:
        print(f"Unknown Route53 action: {args.action}")

# Main function that routes actions to the appropriate handler based on arguments
def main():
    args = parse_arguments()

    # Map resource type to its respective handler function
    handlers = {
        'ec2': handle_ec2,
        's3': handle_s3,
        'route53': handle_route53
    }

    # Retrieve the correct handler for the selected resource and execute the action
    handler = handlers.get(args.resource)
    if handler:
        handler(args)
    else:
        print(f"Unknown resource: {args.resource}")

# Entry point for the script
if __name__ == "__main__":
    main()

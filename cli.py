import argparse
from ec2_manager import create_instance, list_instances

parser = argparse.ArgumentParser(description='AWS CLI Tool')
subparsers = parser.add_subparsers(dest='resource')

# EC2 Commands
ec2_parser = subparsers.add_parser('ec2')
ec2_parser.add_argument('action', choices=['create', 'list'])
ec2_parser.add_argument('--instance-type', choices=['t3.nano', 't4g.nano'])
ec2_parser.add_argument('--ami-id')

args = parser.parse_args()

if args.resource == 'ec2':
    if args.action == 'create':
        create_instance(args.instance_type, args.ami_id)
    elif args.action == 'list':
        list_instances()
